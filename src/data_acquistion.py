import requests
from datetime import datetime
import logging
import argparse
import yaml
import json
import boto3
import sys
import botocore.exceptions as botoexceptions
import logging.config

"""
Warning: Running data_acquistion.py may take several minutes to run as API pull is ~100MB. The API date parameters are not functioning at this time to filter down this data.
"""

#set-up logging
logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)

## try to connect to s3 prior to starting up any processing
try:
    s3 = boto3.client("s3")
except botoexceptions.NoCredentialsError:
    logger.error("Your AWS credentials were not found. Verify that they have been made available as detailed in readme instructions")
    sys.exit(1)

def get_latest_date(bucket_name,output_file_path):
    """
    Get date of the most recent pull from the API
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
    try:
        s3_objects = response['Contents']
    except KeyError as e:
        logger.error('There is no previous data from this acquisition pipeline in your s3 bucket. Please run again with an additional cmd line arg --start_date')
    most_recent_object = max(s3_objects, key=lambda x: x['LastModified'])
    latest_date_dt = most_recent_object['LastModified']
    #convert to string format needed for querying API
    latest_date = latest_date_dt.strftime("%Y-%m-%d")

    logger.debug("No user input start date. Latest date was fetched successfully based on files within s3 repo")
    return latest_date

def acquire_data(url, end_date,start_date=None,**kwargs):
    """

    Args:
        url (str): url for api to pull data from
        end_date (str): date which will be used as the date up to which data will be pulled.
        start_date (str or None): date which will be used as the date from which the data pull will begin from. If no argument is specified, arg is set to None and is updated with
         the date of the last api call using the get_latest_date() function
        **kwargs: Arbitrary keyword arguments
            -output_file_path (str): s3 bucket file path where data has historically been written to
            -bucket_name (str): s3 bucket name to which the data has been historically be saved to

    Returns:
        api_pull (dict): dict consisting of COVID-19 case information (number of confirmed cases, deaths, recovered) by country and date
    """
    # If no arg was start_date was specified, get date of latest api pull
    if start_date == None :
        output_file_path = kwargs.get('output_file_path', None)
        bucket_name= kwargs.get('bucket_name', None)
        start_date = get_latest_date(bucket_name,output_file_path)

    # Make call to the API with exception handling
    payload = {}
    headers = {}
    params = {'from': start_date, 'to': end_date}
    try:
        response = requests.request("GET", url, params=params, headers=headers, data=payload)
    except requests.exceptions.ConnectionError:
        logger.error("There was a connection error to the API. Please try again or verify the URL and API status.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        logger.error("Timeout error, please try again. If problem persists, wait to try again until later")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error("Unexpected error with the requested: {}".format(e))
        sys.exit(1)

    # Handle error in the case that deserialization fails
    try:
        api_pull = response.json()
    except ValueError:
        logger.error("No json returned from response.")
        sys.exit(1)

    logger.info("API call to COVID19-API was successful.")

    return  api_pull

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

    # generate filename for output written to s3 based on pull date
    filename = output_file_path + end_date +".json"
    # put data in form that the put_object function accepts
    serializedAPIdata = json.dumps(api_data)
    # try to write object to s3 directly
    try:
        s3.put_object(Bucket=bucket_name,Key=filename,Body=serializedAPIdata)
    except botoexceptions.ParamValidationError:
        logger.error("There is an error in the data format. Verify the input to this function is still json format")
    except Exception as e:
        logger.error("Unexpected error in trying to write data to s3: {}".format(e))

    logger.info("COVID-19 API Data was successfully saved to s3 bucket. File name is {}".format(filename))

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

    ## open configuration file
    try:
        with open(args.config, "r") as f:
            config = yaml.load(f,Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")

    ## assign variables based on configuration file
    url = config['data_acquisition']['url']
    s3_bucket =config['data_acquisition']['s3_bucket_name']
    output_path = config['data_acquisition']['output_file_path']

    # call the acquire_data function depending on if start_date is provided in the cmd line args
    if args.start_date is not None:
        api_data = acquire_data(url,args.end_date,args.start_date)
    else:
        api_data = acquire_data(url, args.end_date,args.start_date,bucket_name=s3_bucket,output_file_path=output_path)

    #call function to write data to s3
    write_data_to_s3(s3_bucket,api_data,output_path,args.end_date)

# call function if it is explicitly called rather than if it is imported (for whatever reason)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Acquire data from web')
    parser.add_argument('--config', '-c', default = 'config.yml', help='path to yaml file with configurations')
    parser.add_argument('--start_date', '-sd', help='optional start date for data pull')
    parser.add_argument('--end_date', '-ed',default=datetime.now().strftime("%Y-%m-%d"), help='optional end date for data pull')

    args = parser.parse_args()

    run_data_acquistion(args)

    logger.info("data_acquistion.py was run successfully.")

