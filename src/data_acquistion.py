import requests
from datetime import datetime
import argparse
import yaml
import json
import boto3
import sys
import botocore.exceptions as botoexceptions
import logging.config
import helper
import os
"""
Warning: Running data_acquistion.py may take several minutes to run as API pull is ~100MB. The API date parameters are not functioning at this time to filter down this data.
"""

#set-up logging
logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)

def get_latest_date_s3(s3_bucket_name,s3_output_path):
    """
    Get date of the most recent pull from the API based on data within s3
    Args:
        bucket_name (str): the name of S3 bucket containing the latest data
        s3_output_path (str): s3 bucket file path where data has historically been written to

    Returns:
        latest_date (str): The date of the latest case in the existing date in string format
    """

    #call helper function to get most recent s3 object
    most_recent_object = helper.get_latest_s3_data(s3_bucket_name,s3_output_path)
    #get date of most recent file
    latest_date_dt = most_recent_object['LastModified']
    #convert to string format needed for querying API
    latest_date = latest_date_dt.strftime("%Y-%m-%d")
    logger.debug("No user input start date. Latest date was fetched successfully based on files within s3 repo. "
                 "Latest date {}".format(latest_date))
    return latest_date

# def get_latest_date_local(local_path):
#     """
#     Get date of the most recent pull from the API based on data on local system
#     Args:
#         local_path (str): local path where raw data from API has historically been stored
#
#     Returns:
#         latest_date (str): The date of the latest case in the existing date in string format
#     """
#
#     # get list of files within the local path directory
#     list_of_files = glob.glob(local_path + "*")
#     # get the name of the most recently modified file
#     latest_file = max(list_of_files, key=os.path.getctime)
#     # Extract just the date string from full filename
#     latest_date = latest_file[-15:-5]
#     logger.info("No user input start date. Date of last file retrieved from local data folder. "
#                 "Latest date: {}".format(latest_date))
#     return latest_date

def acquire_data(url,s3_flag,end_date,start_date=None,**kwargs):
    """
    Make GET request to API (COVID19API) to retrieve raw data
    Args:
        url (str): url for api to pull data from
        end_date (str): date which will be used as the date up to which data will be pulled.
        start_date (str or None): date which will be used as the date from which the data pull will begin from.
        If no argument is specified, arg is set to None and date is automatically retrieved based on latest data in s3 or local
        **kwargs: Arbitrary keyword arguments
            -s3_output_path (str): s3 bucket file path where data has historically been written to. Only used if running pipeline in s3.
            -bucket_name (str): s3 bucket name to which the data has been historically be saved to. Only used if running pipeline in s3.

    Returns:
        api_pull (dict): dict consisting of COVID-19 case information (number of confirmed cases, deaths, recovered) by country and date
    """

    logger.info("Making GET request to COVID19 API")
    logger.warning("This request response will contain over 100 MB of data--abort now if you have concerns on "
                   "storage limitations either on s3 or local depending on where you have chosen to store the data")
    # If no arg was start_date was specified, get date of latest api pull
    if start_date == None :
        # If running pipeline in s3, search s3 for latest data
        if s3_flag == True:
            try:
                s3 = boto3.client("s3")
            except botoexceptions.NoCredentialsError:
                logger.error("Your AWS credentials were not found. Verify that they have been made available as "
                             "detailed in readme instructions")
                sys.exit(1)

            s3_output_path = kwargs.get('s3_output_path', None)
            bucket_name= kwargs.get('bucket_name', None)
            start_date = get_latest_date_s3(bucket_name,s3_output_path)
        # Otherwise running locally. In local flow, just keeping one copy of any given type of file. Set start_date as
        # beginning of the year
        else:
            #start_date = get_latest_date_local(kwargs.get('local_path', None))
            start_date = "2020-01-01"

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
        logger.error("Unexpected error with the requested: {}:{}".format(type(e).__name__, e))
        sys.exit(1)

    # Handle error in the case that deserialization fails
    try:
        api_pull = response.json()
        logger.info("API call to COVID19-API was successful.")
    except ValueError:
        logger.error("No json returned from response.")
        sys.exit(1)

    return  api_pull

def write_data_to_s3(s3_bucket_name, api_data, s3_output_path,end_date):
    """
    Write raw data retrieved from API GET request to s3 bucket
    Args:
        bucket_name (str): name of the desired s3 bucket to write to
        api_data (dict): raw data pull from COVID-19 API detailing numbers on cases, deaths, etc per day by country
        s3_output_path (str): s3 bucket file path for desired write location
        end_date (str): date which will be used as the date up to which data will be pulled--fed in by previous function in chain

    Returns:
        None - data to be saved to s3 bucket
    """

    ## try to connect to s3 prior to starting up any processing
    try:
        s3 = boto3.client("s3")
    except botoexceptions.NoCredentialsError:
        logger.error("Your AWS credentials were not found. Verify that they have been made available "
                     "as detailed in readme instructions")
        sys.exit(1)

    # generate filename for output written to s3 based on pull date
    filename = os.path.join(s3_output_path, "covid19_time_series_{}".format(end_date) + ".json")
    # put data in form that the put_object function accepts
    serializedAPIdata = json.dumps(api_data)
    # try to write object to s3 directly
    try:
        s3.put_object(Bucket=s3_bucket_name,Key=filename,Body=serializedAPIdata)
    except botoexceptions.ParamValidationError:
        logger.error("There is an error in the data format. Verify the input to this function is still json format")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error in trying to write data to s3: {}:{}".format(type(e).__name__, e))
        sys.exit(1)

    logger.info("COVID-19 API Data was successfully saved to s3 bucket. File name is {}".format(filename))

def write_data_to_local(api_data,local_filepath_out):
    """
    Write raw data retrieved from API GET request to local machine
    Args:
        api_data (dict): raw data pull from COVID-19 API detailing numbers on cases, deaths, etc per day by country
        local_filepath_out (str): local path (including filename) of where to save the raw data from the API GET request

    Returns:

    """

    #filename = os.path.join(local_path, "covid19_time_series_{}".format(end_date) + ".json")
    try:
        with open(local_filepath_out, 'w') as f:
            json.dump(api_data, f)
    except FileNotFoundError:
        logger.error("It seems that the path you've provided does not exist. Please create the path or update the path in the config.yml file")
        sys.exit(1)
    except TypeError as e:
        logger.error("The data you are trying to write as a json has an invalid structure. {}".format(e))
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error in trying to write data to local: {}:{}".format(type(e).__name__, e))
        sys.exit(1)

    logger.info("COVID-19 API Data was successfully saved to local. File is located at {}".format(local_filepath_out))

def run_data_acquistion(args):
    """
    Wrapper function that retrieves data via API call and saves to s3 bucket

    Args:
        args: From argparse, should contain args.config and optionally, args.start_date, args.end_date
            args.config (str): Path to yaml file with load_data as a top level key containing relevant configurations
            args.start_date (str): If given, resulting API call will be given this as a param to filter from this date on
            args.end_date (str): If given, resulting API call will be given this as a param to filter out data past this date

    Returns:
        None -- wrapper function that runs the acquisition steps for covid19 confirmed cases
    """
    ## open configuration file
    try:
        with open(args.config, "r") as f:
            config = yaml.load(f,Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")

    ## assign variables based on configuration file
    url = config['data_acquisition']['url']
    s3_bucket_name =config['data_acquisition']['s3_bucket_name']
    output_path = config['data_acquisition']['s3_output_path']
    local_filepath_out = config['data_acquisition']['local_filepath_out']

    # call the acquire_data function depending on if start_date is provided in the cmd line args
    if args.start_date is not None:
        api_data = acquire_data(url,args.end_date,args.start_date)
    else:
        api_data = acquire_data(url, args.end_date,args.start_date,bucket_name=s3_bucket_name,s3_output_path=output_path)

    #call function to write data either to s3 or local based on --s3 arg from cmd line
    if args.s3_flag == True: 
        write_data_to_s3(s3_bucket_name,api_data,output_path,args.end_date)
    else:
        write_data_to_local(api_data, local_filepath_out)

# call function if it is explicitly called rather than if it is imported (for whatever reason)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Acquire covid19 cases data from web')
    parser.add_argument('--config', '-c', default = 'config.yml', help='path to yaml file with configurations')
    parser.add_argument('--start_date', '-sd', help='optional start date for data pull')
    parser.add_argument('--end_date', '-ed',default=datetime.now().strftime("%Y-%m-%d"), help='optional end date for data pull')
    parser.add_argument("--s3", dest='s3_flag', action='store_true', help="Use arg if you want to save s3 rather than locally.")

    args = parser.parse_args()

    run_data_acquistion(args)

    logger.info("data_acquistion.py was run successfully.")

