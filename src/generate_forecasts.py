import pandas as pd
import argparse
import yaml
import helper
from statsmodels.tsa.arima_model import ARIMAResults
import logging.config
import boto3
import sys
import botocore.exceptions as botoexceptions
import datetime
import os
import numpy as np
import pickle

#set-up logging
logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)


def get_model(s3_flag,local_model_path,input_filename,s3_bucket_name=None,bucket_dir_path=None):
    """
    Retrieve ARIMA trained model object from s3 or local location
    Args:
        s3_flag (bool): Flag used to determine if the scripts will save to s3 or local
        local_model_path (str): path to directory in local machine where trained model object is located
        input_filename (str): name of the model object file
        s3_bucket_name (str): the name of S3 bucket where models are saved (only needed if s3_flag is True)
        bucket_dir_path (str): s3 bucket file path (without filename) where the objects are located (only needed if s3_flag is True)

    Returns:
        model: ARIMA trained model object
    """

    if s3_flag == True:
        try:
            s3 = boto3.client("s3")
        except botoexceptions.NoCredentialsError:
            logger.error(
                "Your AWS credentials were not found. Verify that they have been made available as detailed in readme instructions")
            sys.exit(1)

        s3_file_path = os.path.join(bucket_dir_path, input_filename)
        s3.download_file(s3_bucket_name, s3_file_path, 'model_file')
        model = ARIMAResults.load('model_file')
        logger.info("Model loaded from s3")
    else:
        model = ARIMAResults.load(os.path.join(local_model_path,input_filename))

    return model

def get_global_forecast(model,n_days):
    """
    Make forecasts for the number of confirmed covid19 cases globally
    Args:
        model: ARIMA trained model object for forecasting global covid-19 cases
        n_days: number of days to forecast

    Returns:
        global_forecast_df (pandas DataFrame): DataFrame consisting of Date and Forecasted Value pairs
    """
    #Make forecast
    global_forecast=np.round(model.forecast(n_days)[0])
    #Get date list from today through the next n_days
    today_date = datetime.datetime.now()
    date_list = [today_date + datetime.timedelta(days=x) for x in range(n_days)]
    date_list = [x.date() for x in date_list]
    # generate dataframe of Date, Forecast pairs
    global_forecast_df = pd.DataFrame({'Date': date_list, 'confirmed_cases_forecast': global_forecast})
    logger.info("Global forecasts made for {} days.".format(str(n_days)))
    return global_forecast_df

def get_country_list(s3_flag,local_model_path,input_filename,s3_bucket_name=None,bucket_dir_path=None):
    """
    Retrieves list of countries for which a trained model exists
    Args:
        s3_flag (bool): Flag used to determine if the scripts will save to s3 or local
        local_model_path (str): path to directory in local machine where the object is located
        input_filename (str): name of the object file
        s3_bucket_name (str): the name of S3 bucket where the object is saved (only needed if s3_flag is True)
        bucket_dir_path (str): s3 bucket file path (without filename) where the object is located (only needed if s3_flag is True)

    Returns:
        countries (list): list of countries for which a trained model exists
    """
    # If retrieving from s3
    if s3_flag == True:
        try:
            s3 = boto3.client("s3")
        except botoexceptions.NoCredentialsError:
            logger.error(
                "Your AWS credentials were not found. Verify that they have been made available as detailed in readme instructions")
            sys.exit(1)

        s3_file_path = os.path.join(bucket_dir_path,input_filename)
        s3.download_file(s3_bucket_name, s3_file_path, 'countries.pkl')
        with open("countries.pkl", 'rb') as f:
            countries = pickle.load(f)

    # else retrieving locally
    else:
        with open(os.path.join(local_model_path,input_filename), 'rb') as f:
            countries = pickle.load(f)
    return countries


def get_country_forecast(s3_flag,country,local_model_path,n_days,s3_bucket_name=None,bucket_dir_path=None):
    """
    Make forecasts for the number of confirmed covid19 cases for a given country
    Args:
        s3_flag (bool): Flag used to determine if the scripts will save to s3 or local
        country (str): Country to make the forecast for
        local_model_path (str): path to directory in local machine where trained model object is located
        n_days: number of days to forecast
        s3_bucket_name (str): the name of S3 bucket where models are saved (only needed if s3_flag is True)
        bucket_dir_path (str): s3 bucket file path (without filename) where the objects are located (only needed if s3_flag is True)\


    Returns:
        country_forecast_df (pandas DataFrame): DataFrame consisting of Date and Forecasted Value pairs
    """
    # If retrieving from s3
    if s3_flag == True:
        timestr_use = bucket_dir_path[-15:]
        input_filename = "ARIMA_{}_{}".format(country, timestr_use)
        model = get_model(s3_flag,s3_bucket_name,bucket_dir_path,input_filename)
        logger.debug("Model retrieved for {} from s3".format(country))

    # else retrieving local
    else:
        input_filename = "ARIMA_{}".format(country)
        model = get_model(s3_flag, local_model_path,input_filename,s3_bucket_name, bucket_dir_path)
        logger.debug("Model retrieved for {} from local".format(country))

    # Make forecast
    country_forecast = np.round(model.forecast(n_days)[0])
    # create dates from today to the next n_days
    today_date = datetime.datetime.now()
    date_list = [today_date + datetime.timedelta(days=x) for x in range(n_days)]
    date_list = [x.date() for x in date_list]
    # generate dataframe with Date, Forecast pairs
    country_forecast_df = pd.DataFrame({'country': country, 'Date': date_list, 'confirmed_cases_forecast': country_forecast})
    logger.debug("Forecasts made for {} days for {}".format(str(n_days), country))

    return country_forecast_df

def run_generate_forecasts(args):
    """
    Wrapper function to run steps for making covid19 confirmed cases forecasts
    Args:
        args: from argparse
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

    model = get_model(args.s3_flag,**config['generate_forecasts']['get_model'])
    global_forecast_df = get_global_forecast(model,**config['generate_forecasts']['get_global_forecast'])
    helper.add_to_database(global_forecast_df, "global_covid_forecast",'replace', args.engine_string)

    country_list = get_country_list(args.s3_flag,**config['generate_forecasts']['get_country_list'])
    logger.info("Making forecasts for each country in the dataset. This will take some time if you are using RDS.")

    for country in country_list:
        country_forecast_df = get_country_forecast(args.s3_flag,country,**config['generate_forecasts']['get_country_forecast'])
        helper.add_to_database(country_forecast_df, "country_covid_forecast",'append', args.engine_string)
        logger.debug("Forecasts for {} added to database".format(country))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get covid data from s3 and prep for modeling')
    parser.add_argument('--config', '-c', default='config.yml', help='path to yaml file with configurations')
    parser.add_argument("--engine_string", default=None, help="Optional engine string for db to add data to ")
    parser.add_argument("--s3", dest='s3_flag', action='store_true', help="Use arg if you want to save s3 rather than locally.")
    args = parser.parse_args()
    run_generate_forecasts(args)