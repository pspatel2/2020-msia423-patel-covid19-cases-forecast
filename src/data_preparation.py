import pandas as pd
import botocore.exceptions as botoexceptions
import os
import sys
import helper
import json
import logging.config
import boto3
import yaml
import argparse
import glob

#set-up logging
logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)

def get_s3_data(s3_bucket_name,bucket_dir_path,input_filename = None):
    '''
    Read covud 19 cases data from s3 bucket
    Args:
        s3_bucket_name: the name of S3 bucket containing data of interest
        bucket_dir_path: s3 bucket file path where data is located
        input_filename: optional argument for filename containing data of interest

    Returns:
        covid_df (pandas DataFrame): DataFrame representation of the covid-19 data pulled from API
    '''
    ## try to connect to s3 prior to starting up any processing
    try:
        s3 = boto3.client("s3")
    except botoexceptions.NoCredentialsError:
        logger.error(
            "Your AWS credentials were not found. Verify that they have been made available as detailed in readme instructions")
        sys.exit(1)
    ## if no filename is provided, get the latest file in the specified bucket path
    if input_filename is not None:
        try:
            s3_file = os.path.join(bucket_dir_path,input_filename)
            logger.debug("user inputted file path:{}".format(s3_file))
            s3_obj = s3.get_object(s3_bucket_name, s3_file)
        except botoexceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                logger.error("The object does not exist. Verify pathing and filename.")
            else:
                logger.error("Unexpected error trying to retrieve s3 object. {}".format(e.response['Error']))
            sys.exit(1)
    # if filename is specified, retrieve the s3 object directly
    else:
        logger.info("No user inputted file for raw. Automatically fetching latest data from s3 bucket specified in configs."
                    "This may take a minute.")
        s3_obj_key = helper.get_latest_s3_data(s3_bucket_name, bucket_dir_path)['Key']
        s3_obj = s3.get_object(Bucket=s3_bucket_name,Key=s3_obj_key)

    # the raw data should be in a json form, thus try to parse the s3 object accordingly otherwise throw exception
    try:
        file_content = s3_obj['Body'].read().decode('utf-8')
        covid_data = json.loads(file_content)
        logger.info("Successfully retrieved data from s3")
    except TypeError:
        logger.error("")
    except ValueError:
        logger.error("Latest file in s3 directory is not in json form. This file should not be in the directory")
        sys.exit(1)
    except Exception as error:
        logger.error("Unexpected error in parsing s3 data: {}:{}".format(type(error).__name__, error))
        sys.exit(1)

    # convert data to a DataFrame
    covid_df = pd.DataFrame(covid_data)
    # Active cases data is just 0 throughout dataframe, thus replace with manual computation
    covid_df['Active'] = covid_df['Confirmed'] - covid_df['Deaths'] - covid_df['Recovered']
    # Convert date from string representation to datetime
    covid_df['Date'] = pd.to_datetime(covid_df['Date'])
    return covid_df

def get_local_data(input_file_path):
    """
    Read covid 19 cases data from local machine
    Args:
        input_file_path (str): file path (including file name) to covid-19 raw data on local machine

    Returns:
        covid_df (pandas DataFrame): DataFrame representation of the covid-19 data pulled from API
    """
    try:
        with open(input_file_path) as f:
            covid_data = json.load(f)
    except FileNotFoundError:
        logger.error("The file path you've specified does not exist. Verify the path is correct in the config.yml")
        sys.exit(1)
    except ValueError as e:
        logger.error("The file specified does not seem to be of appropriate json form: {}".format(e))
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error with trying to read in raw data locally: {}:{}".format(type(e).__name__, e))
        sys.exit(1)

    # convert data to a DataFrame
    covid_df = pd.DataFrame(covid_data)
    # Active cases data is just 0 throughout dataframe, thus replace with manual computation
    covid_df['Active'] = covid_df['Confirmed'] - covid_df['Deaths'] - covid_df['Recovered']
    # Convert date from string representation to datetime
    covid_df['Date'] = pd.to_datetime(covid_df['Date'])

    logger.info("Successfully retrieved data from local")

    return covid_df

def get_country_daily(df):
    '''
    Filters raw data to columns of interest to the country_covid_daily_cases database table
    Args:
        df (pandas DataFrame): DataFrame consisting of the raw data acquired from covid19 API

    Returns:
        df (pandas DataFrame): Reduced columns version of the input DataFrame
    '''
    try:
        # china has to be processed differently than all other countries
        china_df = df.loc[df['Country'] == 'China']
        china_df = china_df.drop(columns=["Province","City","CityCode","Lat","Lon"])
        china_df = china_df.groupby(['Country','Date']).sum().reset_index()
        # rest of the world
        rest_of_the_world_df = df.loc[df['Province'] == '']
        rest_of_the_world_df = rest_of_the_world_df.drop(columns=["Province","City","CityCode","Lat","Lon"])
        rest_of_the_world_df = rest_of_the_world_df.groupby(['Country','Date']).sum().reset_index()
        country_df = pd.concat([rest_of_the_world_df,china_df])
    except AttributeError:
        logger.error("Your input to the function 'get_country_daily' was not a DataFrame and thus the function could not run")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error in the function 'get_country_daily': {}:{}".format(type(e).__name__, e))
        sys.exit(1)

    return country_df

def get_global_daily(df):
    """
    Aggregates the raw data from a city/state/country by day level to global by day level. E.g. to the form for the
    global_covid_daily_cases table
    Args:
        df (pandas DataFrame): DataFrame consisting of the raw data acquired from covid19 API

    Returns:
        global_df (pandas DataFrame): Input DataFrame aggregated to the global daily level.

    """
    try:
        ### STILL REQUIRE PROCESSING AT THE COUNTRY LEVEL FIRST TO GET RID OF DUPLICATE COUNTING
        china_df = df.loc[df['Country'] == 'China']
        china_df = china_df.drop(columns=["Province","City","CityCode","Lat","Lon"])
        china_df = china_df.groupby(['Country','Date']).sum().reset_index()
        # rest of the world
        rest_of_the_world_df = df.loc[df['Province'] == '']
        rest_of_the_world_df = rest_of_the_world_df.drop(columns=["Province","City","CityCode","Lat","Lon"])
        rest_of_the_world_df = rest_of_the_world_df.groupby(['Country','Date']).sum().reset_index()
        country_df = pd.concat([rest_of_the_world_df,china_df])
        # now sum up to global
        global_df = country_df.groupby('Date').sum()[["Confirmed", "Recovered", "Active", "Deaths"]].reset_index()
    except TypeError:
        logger.error("Your input to the function 'get_global_daily' was not a DataFrame and thus the function could not run")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error in the function 'get_global_daily': {}:{}".format(type(e).__name__, e))
        sys.exit(1)

    return global_df

def run_data_preparation(args):
    """
    Wrapper function that prepares the raw data for upload to databases and for next steps of plotting and modeling
    Args:
        args: From argparse:
           - config (str): Path to yaml file with load_data as a top level key containing relevant configurations
           - engine_string (str): sqlalchemy engine string argument can be entered
           - s3_flag (bool): the flag used to determine if the scripts will read/write via s3 or local

    Returns:
        None -- this a wrapper function for the data preparation steps
    """
    try:
        with open(args.config, "r") as f:
            config = yaml.load(f,Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")
        sys.exit(1)

    if args.s3_flag == True:
        df = get_s3_data(**config['data_preparation']['get_s3_data'])
    else:
        df = get_local_data(**config['data_preparation']['get_local_data'])
    country_df = get_country_daily(df)
    global_df = get_global_daily(df)
    helper.add_to_database(country_df,"country_covid_daily_cases",'replace',args.engine_string)
    helper.add_to_database(global_df, "global_covid_daily_cases",'replace', args.engine_string)
    country_df.to_csv('data/country_data.csv')
    global_df.to_csv('data/global_data.csv')

    logger.info("data_preparation.py was run successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get covid data from s3 and prep for modeling')
    parser.add_argument('--config', '-c', default='config.yml', help='path to yaml file with configurations')
    parser.add_argument("--engine_string", default=None, help="Optional engine string for db to add data to ")
    parser.add_argument("--s3", dest='s3_flag', action='store_true', help="Use arg if you want to save s3 rather than locally.")
    args = parser.parse_args()
    run_data_preparation(args)

    # TO RUN IN DOCKER: docker run --mount type=bind,source="$(pwd)"/data,target=/src/data --env-file=aws_creds --env-file=rds_config covid19cases src/data_preparation.py --config=config/config.yml --RDS