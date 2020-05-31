import requests
from datetime import datetime
import argparse
import yaml
import json
import boto3
import sys
import botocore.exceptions as botoexceptions
import logging.config
import os
import ast
import config

logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)


def acquire_data(url,params):
    '''
    Make GET request to API (newsAPI) to retrieve raw data
    Args:
        url (str): url for api to pull data from
        params (dict): params to be applied for api call

    Returns:
        api_pull (dict):  raw data (in dict) consisting of news information pulled from the aPI
    '''

    ##Make API request
    # convert string rep of dict to dict for params
    params = ast.literal_eval(params)
    # get apiKey from environment variable
    params['apiKey'] = config.NEWS_API_KEY
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.ConnectionError:
        logger.error("There was a connection error to the news API. Please try again or verify the URL and API status. "
                     "Pipeline will continue but the app will not display updated news headlines")
    except requests.exceptions.Timeout:
        logger.error("Timeout error to the news API, please try again. If problem persists, wait to try again until later. "
                     "Pipeline will continue but the app will not display updated news headlines")
    except requests.exceptions.RequestException as e:
        logger.error("Unexpected error with the request to the news API: {}:{}. Pipeline will continue but the app will "
                     "not display updated news headlines".format(type(e).__name__, e))

    # Handle error in the case that deserialization fails
    try:
        api_response = response.json()
        logger.info("Request to newsAPI was successful.")
    except ValueError:
        logger.error("Call to the newsAPI was okay, but did not return a json parsable response. There may be some issue"
                     "with the API itself.")

    # get just the article headlines from the response
    try:
        api_pull = api_response['articles']
    except KeyError:
        logger.error("It is likely you have not set your API key--please see the readme for instructions on this")

    return api_pull

def write_data_to_s3(api_data,s3_bucket_name,s3_output_path):
    """
    Save newsAPI data to s3 bucket
    Args:
        api_data (dict): raw data pull from newsAPI
        s3_bucket_name (str): name of the desired s3 bucket to write to
        s3_output_path (str): s3 bucket file path for desired write location
    Returns:
        None - data to be saved to s3 bucket
    """
    # generate filename for output written to s3 based on pull date
    filename = os.path.join(s3_output_path, "news_headlines_{}".format(datetime.now().strftime("%Y-%m-%d")) + ".json")
    # put data in form that the put_object function accepts
    serializedAPIdata = json.dumps(api_data)
    # try to write object to s3 directly
    ## try to connect to s3 prior to starting up any processing
    try:
        s3 = boto3.client("s3")
        s3.put_object(Bucket=s3_bucket_name,Key=filename,Body=serializedAPIdata)
        logger.info("News API Data was successfully saved to s3 bucket. File name is {}".format(filename))
    except botoexceptions.NoCredentialsError:
        logger.error(
            "Your AWS credentials were not found. Verify that they have been made available as detailed "
            "in readme instructions.")
        logger.warning("new newsAPI data could not be saved thus the app will not displayed an updated feed")
    except botoexceptions.ParamValidationError:
        logger.error("There is an error in the data format. Verify the input to this function is still json format")
        logger.warning("new newsAPI data could not be saved thus the app will not displayed an updated feed")
    except Exception as e:
        logger.error("Unexpected error in trying to write data to s3: {}:{}".format(type(e).__name__, e))
        logger.warning("new newsAPI data could not be saved thus the app will not displayed an updated feed")

def write_data_to_local(api_data,local_filename):
    """
    Save newsAPI data to local
    Args:
        api_data (dict): raw data pull from newsAPI
        local_filename (str): path to local (including file name) of where to save data locally

    Returns:

    """
    #filename = os.path.join(local_path,"bbc_headlines_{}".format(datetime.now().strftime("%Y-%m-%d")) +".json")
    try:
        with open(local_filename, 'w') as f:
            json.dump(api_data, f)
        logger.info("News API Data was successfully saved to local. File is located at {}".format(local_filename))
    except FileNotFoundError:
        logger.error("It seems that the path you've provided does not exist. Please create the path or update the path in the config.yml file")
    except Exception as e:
        logger.error("Unexpected error in trying to write data to s3: {}:{}".format(type(e).__name__, e))
        logger.warning("new newsAPI data could not be saved thus the app will not displayed an updated feed")

def run_get_news(args):
    """
    Wrapper function, retrieves data via API call and saves to s3 bucket

    Args:
        args: From argparse, should contain args.config and optionally, args.start_date, args.end_date
            args.config (str): Path to yaml file with load_data as a top level key containing relevant configurations
            args.s3_flag (bool): Boolean flag that decides whether data is written to s3 or local
    Returns:
        None -- wrapper function to handle acquiring BBC and Reuters news headlines pertaining to covid19
    """
    ## open configuration file
    try:
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")

    # call function to get data
    api_data = acquire_data(**config['get_news']['acquire_data'])

    # call function to write data to s3
    if args.s3_flag == True:
        write_data_to_s3(api_data, **config['get_news']['write_data_to_s3'])
    else:
        write_data_to_local(api_data,**config['get_news']['write_data_to_local'])

# call function if it is explicitly called rather than if it is imported (for whatever reason)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Acquire data from news headlines from newsAPI')
    parser.add_argument('--config', '-c', default='config.yml', help='path to yaml file with configurations')
    parser.add_argument("--s3", dest='s3_flag', action='store_true', help="Use arg if you want to save s3 rather than locally.")
    args = parser.parse_args()

    run_get_news(args)

    logger.info("get_news.py was run successfully.")