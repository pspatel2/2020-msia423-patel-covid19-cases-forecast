import requests
from datetime import datetime
import logging
import argparse
import yaml
import json
import boto3
import sys
import botocore.exceptions as botoexceptions

"""
Warning: Running data_acquistion.py may take several minutes to run as API pull is 50+ MB. The API data parameters are not functioning at this time.
"""

s3 = boto3.client("s3")
logging.basicConfig(filename='logfile.log', filemode='a', level=logging.DEBUG, format="%(asctime)-15s %(levelname)-8s %(message)s")
logger = logging.getLogger(__name__)

def get_latest_date(bucket_name,output_file_path):
    """
    Get date of the latest pull from the API
    Args:
        bucket_name (str): the name of S3 bucket containing the latest data
        output_file_path (str): s3 bucket file path where data has historically been written to

    Returns:
        latest_date (str): The date of the latest case in the existing date in string format
    """
    # Get list of objects in the s3 bucket directory where the data is generally saved
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=output_file_path)
    except botoexceptions.ParamValidationError as error:
        logger.error('The parameters you provided are incorrect: {}'.format(error))
        sys.exit(1)
    except botoexceptions.NoCredentialsError:
        logger.error('Your AWS credentials could not be located. Please verify you have followed the appropriate steps outlined in the directions for this set-up')
        sys.exit(1)
    except botoexceptions.ClientError as error:
        logger.error('Unexpected error with reaching the s3 bucket: {}'.format(error))
        sys.exit(1)

    # Get the most recent date modified from all files (will correspond to last API pull)
    s3_objects = response['Contents']
    most_recent_object = max(s3_objects, key=lambda x: x['LastModified'])
    latest_date_dt = most_recent_object['LastModified']
    #convert to string format needed for querying API
    latest_date = latest_date_dt.strftime("%Y-%m-%d")

    logger.debug("No user input start date. Latest date was fetched successfully")
    return latest_date

def acquire_data(url,bucket_name, start_date=None,end_date=datetime.now().strftime("%Y-%m-%d")):
    """
    Args:
        url (str): url for api to pull data from
        bucket_name (str): s3 bucket name to which the data should be saved to
        start_date (str): date which will be used as the date from which the data pull will begin from. If no argument is specified, the date of the last api call will be used.
        end_date (str): date which will be used as the date up to which data will be pulled. If no argument is specified then today's date will be used.

    Returns:
        api_pull (dict): dict consisting of COVID-19 case information (number of confirmed cases, deaths, recovered) by country and date
        end_date (str): max date in the data pulled
    """
    # If no arg was start_date was specified, get date of latest api pull
    if start_date == None :
        latest_date = get_latest_date(bucket_name)

    # Make call to the API with exception handling
    payload = {}
    headers = {}
    params = {'from': start_date, 'to': end_date}
    try:
        response = requests.request("GET", url, params=params, headers=headers, data=payload)
    except requests.exceptions.ConnectionError:
        logger.error("There was a connection error to the API. Please try again or verify the URL and API status.")
    except requests.exceptions.Timeout:
        logger.error("Timeout error, please try again. If problem persists, wait to try again until later")
    except requests.exceptions.RequestException as e:
        logger.error("Unexpected error with the requested: {}".format(e))

    # Handle error in the case that deserialization fails
    try:
        api_pull = response.json()
        logger.info("Successfully made request to the API.")
    except ValueError:
        logger.error("No json returned from response.")

    logger.info("API call to COVID19-API was successful.")

    return  api_pull, end_date

def write_data_to_s3(bucket_name, api_data, output_file_path,end_date):
    """
    Write data to s3 bucket

    Args:
        bucket_name (str): name of the desired s3 bucket to write to
        api_data (dict): raw data pull from COVID-19 API detailing numbers on cases, deaths, etc per day by country
        output_file_path (str): s3 bucket file path for desired write location
        end_date (str): date which will be used as the date up to which data will be pulled--fed in by previous function in chain

    Returns:
        None - data to be saved to s3 bucket
    """
    #to-do: exception handling here
    filename = output_file_path + end_date +".json"
    serializedAPIdata = json.dumps(api_data)
    s3.put_object(Bucket=bucket_name,Key=filename,Body=serializedAPIdata)
    logger.info("COVID-19 API Data was successfully saved to s3 bucket.")

def run_data_acquistion(args):
    """
    Retrieves data via API call and saves to s3 bucket

    Args:
        args: From argparse, should contain args.config and optionally, args.start_date, args.end_date
            args.config (str): Path to yaml file with load_data as a top level key containing relevant configurations
            args.start_date (str): If given, resulting API call will be given this as a param to filter from this date on
            args.end_date (str): If given, resulting API call will be given this as a param to filter out data past this date

    Returns:
        None
    """
    try:
        with open(args.config, "r") as f:
            config = yaml.load(f,Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")

    url = config['data_acquisition']['url']
    s3_bucket =config['data_acquisition']['s3_bucket_name']
    output_path = config['data_acquisition']['output_file_path']

    if args.start_date is not None and args.end_date is not None:
        df, write_date = acquire_data(url,s3_bucket,args.start_date,args.end_date)
    elif args.start_date is not None:
        df, write_date = acquire_data(url,s3_bucket,args.start_date,)
    elif args.end_date is not None:
        df, write_date = acquire_data(url,s3_bucket,None,args.end_date)
    else:
        df, write_date = acquire_data(url,s3_bucket)

    write_data_to_s3(s3_bucket,df,output_path,write_date)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Acquire data from web')
    parser.add_argument('--config', '-c', default = 'config.yml', help='path to yaml file with configurations')
    parser.add_argument('--start_date', '-sd', help='optional start date for data pull')
    parser.add_argument('--end_date', '-ed', default='config.yml', help='optional end date for data pull')

    args = parser.parse_args()

    run_data_acquistion(args)

    logger.info("data_acquistion.py was run successfully.")

