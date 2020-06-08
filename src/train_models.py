import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
import argparse
import yaml
import helper
from sklearn.model_selection import TimeSeriesSplit
import logging.config
import boto3
import sys
import botocore.exceptions as botoexceptions
from datetime import datetime
import os
import unidecode
import pickle
from shutil import copyfile

#set-up logging
logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)

def read_data_from_db(model_type,engine_string=None):
    """
    Retrieve data from MySQL database locally or in RDS
    Args:
        model_type (str): can specify 'global' or 'country' so that the correct table is queried
        engine_string (str): sqlalchemy string for the connection.

    Returns:
        df (pandas DataFrame): DataFrame of covid19 data retrieved from MySQL database
    """

    # set table_name to be queried based on the model desired to be trained
    if (model_type =='global'):
        table_name = 'global_covid_daily_cases'

    elif (model_type =='country'):
        table_name = 'country_covid_daily_cases'

    else:
        logger.error("Not a valid model_type, options are: 'global' or 'country'")
        sys.exit(1)

    # get sqlalchemy engine
    engine = helper.get_engine(engine_string)

    # query the database
    query = """SELECT * FROM  {}""".format(table_name)
    df = helper.get_data_from_database(query,engine_string)

    return df

def reduce_and_reshape_data(model_type, df):
    """
    Perform simple manipulation to the DataFrame for modeling prep
    Args:
        model_type (str): can specify 'global' or 'country' so that the correct table is queried
        df (pandas DataFrame): DataFrame of covid19 data retrieved from MySQL database

    Returns:
        df (pandas DataFrame): DataFrame of covid19 data needed for modeling
    """
    # if global model, sort by Date and then take only the confirmed column
    if (model_type == 'global'):
        df = df.sort_values(by='Date',ascending = True)
        df = df[['Confirmed']]

    # if country models, take country, date, and confirmed fields
    elif (model_type =='country'):
        df = df[['Country','Date','Confirmed']]

    else:
        logger.error("Not a valid model_type, options are: 'global' or 'country'")
        sys.exit(1)

    return df

def train_global_model(df,model_params,optional_fit_args):
    """
    Train ARIMA model for forecasting global confirmed cases of COVID-19
    Args:
        df (pandas DataFrame): input data consisting of confirmed cases globally by day
        model_params (dict): ARIMA model required fit parameters
        optional_fit_args (dict): ARIMA model additional hyperparameters

    Returns:
        model_arima: ARIMA trained model object

    """
    # Define model
    arima_def = ARIMA(df, order=(model_params['p'], model_params['d'], model_params['q']))
    # Fit model
    model_arima = arima_def.fit(**optional_fit_args,disp=0)
    logger.info("Global daily forecasting model trained")
    return model_arima

def forward_chaining_eval_global_model(df,model_params,optional_fit_args,nbr_days_forecast):
    """
    Evaluate COVID19 global confirmed cases forecasting model using a walk forward validation approach
    Args:
        df (pandas DataFrame): input data used for training
        model_params (dict): ARIMA required fit parameters used in training
        optional_fit_args: ARIMA model additional hyperparameters used in trainig
        nbr_days_forecast: Number of days into the future to be forecasted

    Returns:
        avg_mape (float): Average Mean Average Percent Error across all folds of the walk forward approach
    """

    test_size = float(nbr_days_forecast) / len(df)
    n_splits = int((1 // test_size) - 1)
    tscv = TimeSeriesSplit(n_splits=n_splits)
    y_preds_arima = []
    mapes_arima = []
    counter = 1
    for train_index, test_index in tscv.split(df):
        y_train = df.iloc[train_index]
        y_test = df.iloc[test_index]
        arima_def = ARIMA(y_train, order=(model_params['p'], model_params['d'], model_params['q']))
        model_arima = arima_def.fit(**optional_fit_args,disp=0)
        y_pred = model_arima.forecast(len(y_test))[0]
        y_preds_arima.append(np.round(y_pred))
        mapes_arima.append(round((abs((y_pred - y_test.values) / y_test.values) * 100).mean()))
        counter+=1

    avg_mape = np.round(np.mean(mapes_arima),3)

    return avg_mape

def train_country_models(df,model_params,optional_fit_args):
    """
    Trains a ARIMA model for forecasting confirmed cases of COVID-19 for each country that has the necessary data
    Args:
        df (pandas DataFrame): input data consisting of confirmed cases globally by day
        model_params (dict): ARIMA model required fit parameters
        optional_fit_args (dict): ARIMA model additional hyperparameters

    Returns:
        country_models_df (pandas: ARIMA trained model object

    """
    # get list of each country in the dataset
    country_list = df.Country.unique()
    # initial lists to be appeneded to through training loop
    mapes_country_arima = []
    countries_w_models =[]
    country_models = []

    # for each country in the list, attempt to build an ARIMA model for forecasting
    for cntry in country_list:
        #subset dataframe to country of interest
        df_train = df.loc[df['Country'] == cntry]
        df_train.reset_index(inplace=True,drop=True)
        y = df_train['Confirmed']
        #only perform training if there are at least two weeks of data with at least 1 confirmed cases in that country
        enough_data_flag = len(df_train.loc[df_train['Confirmed']>0])
        if enough_data_flag > 13:
            # train on all the data
            arima_def = ARIMA(y, order=(model_params['p'], model_params['d'], model_params['q']))
            model_arima = arima_def.fit(**optional_fit_args, disp=0)
            # append model object reference to a list
            countries_w_models.append(cntry)
            country_models.append(model_arima)

            # for a rough evaluation of each model, train on all but last 7 days and evaluate on those 7
            y_train = y.iloc[0:len(y) - 7]
            y_test = y.iloc[-7:]
            arima_model_eval = ARIMA(y_train, order=(model_params['p'], model_params['d'], model_params['q']))
            model_eval_arima_fit = arima_model_eval.fit(**optional_fit_args, disp=0)
            y_pred = model_eval_arima_fit.forecast(len(y_test))[0]
            mapes_country_arima.append((abs((y_pred -y_test) / y_test) * 100).mean())
        else:
            pass
    # create a dataframe consisting of the countries for which a model could be built. In that dataframe have country name,
    # reference to trained model object, and its approximate MAPE
    country_models_df = pd.DataFrame({'Country': countries_w_models,'Model':country_models,'MAPE':mapes_country_arima})
    no_model_countries = len(country_list)-len(country_models_df)
    logger.info("Country models trained. Models could not be generated for {} countries due to lack of data.".format(no_model_countries))
    return country_models_df

def save_global_model_local(model,configfile,local_path,filename):
    """
    Save the global forecasting model to local
    Args:
        model (tmo): trained model object to save
        configfile(str): reference configuration file associated with this training run
        s3_flag (bool): Flag used to determine if the scripts will save to s3 or local
        s3_bucket_name (str): the name of S3 bucket to save model to (only needed if s3_flag is True)
        s3_output_path (str): s3 bucket file path (without filename) where output will be saved to (only needed if s3_flag is True)
        local_path (str): local path (without filename) where to save model
        filename(str): name of model file

    Returns:
        None -- saves trained model object to desired location
    """

    # save model and config to local
    try:
        model.save(os.path.join(local_path,filename))
    except FileNotFoundError:
        logger.error("Provided local path is not valid. Please correct this in the config file or create this path")
    except PermissionError:
        logger.error("You do not have permission to write to the path you've specified in the config file")
    except Exception as e:
        logger.error("Unexpected error in trying to write model to local path: {}:{}".format(type(e).__name__, e))
    try:
        copyfile(configfile,os.path.join(local_path,'config.yml'))
    ### DONT NEED FILENOTFOUND or PERMISSION EXCEPTION AS IT WOULD BE CAUGHT IN LINE 279. Just use a catch all
    except Exception as e:
        logger.error("Unexpected error in trying to copy config to new path: {}:{}".format(type(e).__name__, e))
    logger.info("Global model and config were successfully saved to local. They are located in the dir {}.".format(local_path))

def save_global_model_s3(model,configfile,s3_bucket_name,s3_output_path):
    """
    Save the global forecasting model to s3
    Args:
        model (tmo): trained model object to save
        configfile(str): reference configuration file associated with this training run
        s3_bucket_name (str): the name of S3 bucket to save model to (only needed if s3_flag is True)
        s3_output_path (str): s3 bucket file path (without filename) where output will be saved to (only needed if s3_flag is True)

    Returns:
        None -- saves trained model object to desired location
    """
    # generate filename for output written to s3 based on pull date
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = 'ARIMA_global_{}'.format(date_str)
    # local path here is arbitrary since its within the docker container not on the host system
    local_path = 'models/global'
    local_model_path= os.path.join(local_path,date_str)
    os.mkdir(local_model_path)
    # save model and config to local
    filename = 'ARIMA_global_model'
    local_file = os.path.join(local_path,filename)
    model.save(local_file)
    with open(os.path.join(local_path,"config.yml"), 'w') as file:
        yaml.dump(configfile, file)

    try:
        s3 = boto3.client("s3")
    except botoexceptions.NoCredentialsError:
        logger.error("Your AWS credentials were not found. Verify that they have been made available as detailed "
                     "in readme instructions")
        sys.exit(1)

    s3_model_file = os.path.join(s3_output_path,date_str,filename)
    s3_config_file = os.path.join(s3_output_path,date_str,"config_{}.yml".format(date_str))

    try:
        s3.upload_file(local_file, s3_bucket_name, s3_model_file)
        s3.upload_file(configfile,s3_bucket_name,s3_config_file)
    except Exception as e:
        logger.error("Unexpected error in trying to write data to s3: {}:{}".format(type(e).__name__, e))
        sys.exit(1)

    logger.info("Global model and config were successfully saved to s3 bucket. They are located in the dir {} in "
                "your s3 bucket".format(os.path.join(s3_output_path, date_str)))

def save_country_models_local(df,configfile,local_path):
    """
    Saves the country level forecasting models to local
    Args:
        df (pandas DataFrame): Country models DataFrame saved out from "train_country_models" function
        configfile(str): reference configuration file associated with this training run
        local_path (str): local path where to save models

    Returns:
        None -- saves trained model objects to local path
    """
    # Have to loop through each row in the DataFrame to save the model for each country
    countries = df['Country'].values
    models = df['Model'].values
    # go through each country in the dataset for which a model was trained
    for i in range(len(countries)):
        # generate file name for each country using the country name
        filename = 'ARIMA_{}'.format(unidecode.unidecode(countries[i]))
        model = models[i]
        # try to save model to local
        try:
            local_file = os.path.join(local_path, filename)
            model.save(local_file)
        except FileNotFoundError:
            logger.error("Specified local path for saving the model does not exist. Please create the directory or "
                         "modify configuration: 'save_country_models' in the yaml file for this script")
            sys.exit(1)
        except Exception as e:
            logger.error("Unexpected error in trying to write data to local: {}:{}".format(type(e).__name__, e))
            sys.exit(1)
    # try to save config file to path as well
    try:
        copyfile(configfile,os.path.join(local_path,'config.yml'))
    ### DONT NEED FILENOTFOUND or PERMISSION EXCEPTION AS IT WOULD BE CAUGHT IN LINE 279. Just use a catch all
    except Exception as e:
        logger.error("Unexpected error in trying to copy config to new path: {}:{}".format(type(e).__name__, e))
    # Dump out a list of the country names, which is needed for later processes in the pipeline
    try:
        countries_write = [unidecode.unidecode(x) for x in countries]
        with open(os.path.join(local_path, "countries.pkl"), 'wb') as f:
            pickle.dump(countries_write, f)
    except Exception as e:
        logger.error("Unexpected error in trying to write data to local: {}:{}".format(type(e).__name__, e))

    logger.info("Country models and config were successfully saved to local dir.They are located in the dir {}".format(local_path))

def save_country_models_s3(df,configfile,s3_bucket_name,s3_output_path):
    """
    Saves the country level forecasting models to s3
    Args:
        df (pandas DataFrame): Country models DataFrame saved out from "train_country_models" function
        configfile(str): reference configuration file associated with this training run
        s3_bucket_name (str): s3 bucket name to which the models should be saved
        s3_output_path (str): path within the s3 bucket to save the models to

    Returns:
        None -- saves trained model objects to s3
    """
    try:
        s3 = boto3.client("s3")
    except botoexceptions.NoCredentialsError:
        logger.error("Your AWS credentials were not found. Verify that they have been made available as detailed "
                     "in readme instructions")
        sys.exit(1)
    # Get list of countries
    countries = df['Country'].values
    # Get list of the models
    models = df['Model'].values
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Make a directory with the timestamp for the country models. The local path here is arbitrary as its only within
    # the docker container so didnt make it configurable
    local_path = "models/country"
    os.makedirs(os.path.join(local_path, date_str))
    for i in range(len(countries)):
        filename = 'ARIMA_{}_{}'.format(unidecode.unidecode(countries[i]), date_str)
        model = models[i]
        local_file = os.path.join(local_path, date_str, filename)
        model.save(local_file)
        s3_model_file = os.path.join(s3_output_path, date_str, filename)
        try:
            s3.upload_file(local_file, s3_bucket_name, s3_model_file)
        except Exception as e:
            logger.error("Unexpected error in trying to write data to s3: {}:{}".format(type(e).__name__, e))
            sys.exit(1)
    s3_config_file = os.path.join(s3_output_path, date_str, "config_{}.yml".format(date_str))
    countries_write = [unidecode.unidecode(x) for x in countries]
    with open(os.path.join(local_path, "countries.pkl"), 'wb') as f:
        pickle.dump(countries_write, f)
    s3_countries = os.path.join(s3_output_path, date_str, "countries_{}.pkl".format(date_str))

    try:
        s3.upload_file(configfile, s3_bucket_name, s3_config_file)
        s3.upload_file(os.path.join(local_path, "countries.pkl"), s3_bucket_name, s3_countries)
    except Exception as e:
        logger.error("Unexpected error in trying to write data to s3: {}:{}".format(type(e).__name__, e))
        sys.exit(1)
    logger.info("Country models and config were successfully saved to s3 bucket.They are located in the dir {}".format(
        os.path.join(s3_output_path, date_str)))

def run_train_models(args):
    """
    Wrapper function to run model traning and evaluation steps
    Args:
        args: From argparse:
           - config (str): Path to yaml file with load_data as a top level key containing relevant configurations
           - engine_string (str): sqlalchemy engine string argument can be entered
           - s3_flag (bool): the flag used to determine if the scripts will read/write via s3 or local

    Returns:
        None -- wrapper function
    """
    try:
        with open(args.config, "r") as f:
            config = yaml.load(f,Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")
        sys.exit(1)

    # get global data, trained global forecasting model, evaluate it, and save it
    global_data = read_data_from_db('global',args.engine_string)
    confirmed_series = reduce_and_reshape_data('global',global_data)
    arima_model = train_global_model(confirmed_series,config['train_models']['global_model_configs']['model_params'],config['train_models']['global_model_configs']['optional_fit_args'])
    eval_mape = forward_chaining_eval_global_model(confirmed_series,config['train_models']['global_model_configs']['model_params'],config['train_models']['global_model_configs']['optional_fit_args'],config['train_models']['global_model_configs']['nbr_days_forecast'])
    logger.info("Forward chaining MAPE for global forecasting model is: {}".format(str(eval_mape)))
   #save_global_model(arima_model,args.config,args.s3_flag,**config['train_models']['global_model_configs']['save_model'])

    if args.s3_flag == True:
        save_global_model_s3(arima_model,args.config,**config['train_models']['global_model_configs']['save_model_to_s3'])
    else:
        save_global_model_local(arima_model,args.config,**config['train_models']['global_model_configs']['save_model_to_local'])

    # get country level data, trained country forecasting models, evaluate it, and save it
    country_data = read_data_from_db('country',args.engine_string)
    country_data = reduce_and_reshape_data('country',country_data)
    logger.info("Training models for each country, this will take a few moments.")
    logger.warning("You may see some warnings issued from the ARIMA fit. Due to the nature of the data for some "
                   "countries, the fit/optimization algorithm encounters issues.")
    model_df = train_country_models(country_data,config['train_models']['country_model_configs']['model_params'],config['train_models']['country_model_configs']['optional_fit_args'])
    avg_country_model_mape = model_df.MAPE.mean()
    logger.info("Average MAPE across all country models: "+str(avg_country_model_mape))
    #save_country_models(model_df,args.config,args.s3_flag,**config['train_models']['country_model_configs']['save_model'])

    if args.s3_flag == True:
        save_country_models_s3(model_df,args.config,**config['train_models']['country_model_configs']['save_model_to_s3'])
    else:
        save_country_models_local(model_df,args.config,**config['train_models']['country_model_configs']['save_model_to_local'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train time-series forecasting model(s) for COVID-19 confirmed case numbers')
    parser.add_argument('--config', '-c', default='config.yml', help='path to yaml file with configurations')
    parser.add_argument("--engine_string", default=None, help="Optional engine string for db to add data to ")
    parser.add_argument("--s3", dest='s3_flag', action='store_true', help="Use arg if you want to save s3 rather than locally.")
    args = parser.parse_args()
    run_train_models(args)

    logger.info("train_models.py was run successfully.")