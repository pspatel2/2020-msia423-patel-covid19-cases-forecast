import sys
import helper
import botocore.exceptions as botoexceptions
import boto3
import logging.config
import yaml
import argparse
import plotly
import plotly.graph_objects as go
from datetime import datetime
import os

#set-up logging
logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)

def get_global_forecasted_data(engine_string):
    """
    Get global forecast data from MySQL database
    Args:
        engine_string (str): sqlalchemy string for connection to desired database

    Returns:
        forecast_df (pandas DataFrame): DataFrame consisting of forecasted global confirmed case numbers for covid-19
    """

    query =  """SELECT * FROM global_covid_forecast"""
    forecast_df = helper.get_data_from_database(query,engine_string)
    logger.info("Retrieved global forecast data")
    return forecast_df

def get_country_forecasted_data(country,engine_string):
    """
    Get country forecast data from MySQL database
    Args:
        country (str): Country for which the data is to be retrieved
        engine_string (str): sqlalchemy string for connection to desired database

    Returns:
        forecast_df (pandas DataFrame): DataFrame consisting of forecasted confirmed case numbers for covid-19 for given country
    """

    query =  """SELECT * FROM  country_covid_forecast WHERE country = '{}'""".format(country)
    forecast_df = helper.get_data_from_database(query,engine_string)
    if len(forecast_df) == 0:
        logger.warning("Forecast not available for {}. No data retrieved".format(country))
    else:
        logger.info("Retrieved country forecast data for {}".format(country))
    return forecast_df

def get_recent_global_confirmed_data(engine_string):
    """
    Get global confirmed case numbers over the last two weeks
    Args:
        engine_string (str): sqlalchemy string for connection to desired database

    Returns:
        global_df_plot (pandas DataFrame): DataFrame of covid-19 case numbers globally over the last two weeks
    """
    query = """SELECT * FROM global_covid_daily_cases order by Date desc limit 14"""
    global_df_plot = helper.get_data_from_database(query,engine_string)
    global_df_plot = global_df_plot.sort_values(by='Date').reset_index(drop=True)
    logger.info("Retrieved recent global confirmed cases data")
    return global_df_plot

def get_recent_country_confirmed_data(country,engine_string):
    """
    Get country confirmed case numbers over the last two weeks
    Args:
        country (str): Country for which the data is to be retrieved
        engine_string (str): sqlalchemy string for connection to desired database

    Returns:
        country_df_plot (pandas DataFrame): DataFrame of covid-19 case numbers over the last two weeks for input country
    """

    query = """SELECT * FROM country_covid_daily_cases WHERE country = '{}'""".format(country)
    country_df = helper.get_data_from_database(query,engine_string)
    country_df_plot = country_df.groupby('Date').sum()[["Confirmed", "Recovered", "Active", "Deaths"]].reset_index()
    country_df_plot = country_df_plot.tail(14).sort_values(by='Date', ).reset_index(drop=True)
    logger.info("Retrieved recent confirmed cases data for {}".format(country))
    return country_df_plot


def generate_forecast_plot(forecast_df,cases_df_plot):
    """
    Generate a plotly plot of recent confirmed case numbers along with forecasted values for the future
    Args:
        forecast_df (pandas DataFrame): DataFrame containing forecasted values
        cases_df_plot (pandas DataFrame): DataFrame containing recent confirmed case values

    Returns:
        fig: plotly figure
    """

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=cases_df_plot['Date'], y=cases_df_plot['Confirmed'], marker_color='rgba(232, 17, 17, 0.8)',
                   name="Recent Confirmed Cases"))

    # sometimes the 'Date' column is capitilized in RDS and other times it isnt--not sure why, but solving via this code
    if 'date' in forecast_df.columns:
        forecast_df.rename(columns={'date':'Date'},inplace=True)

    fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['confirmed_cases_forecast'],
                             marker_color='rgba(241, 140, 39, 0.8)', name="Forecasted Confirmed Cases"))
    fig.update_xaxes(tickangle=315, tickfont=dict(family='Rockwell', size=14))
    fig.update_yaxes(tickfont=dict(family='Rockwell', size=14))
    logger.info("Successfully created plotly figure")
    return fig


def get_html_and_save(fig,s3_flag,filename,local_path,s3_bucket_name=None,s3_output_path=None):
    """
    Converts plotly figure into html and saves it out to file
    Args:
        fig: Plotly figure of interest
        s3_flag (bool): the flag used to determine if the file will be saved to s3 or local
        filename (str): name of file to be saved
        local_path (str): if saving locally, local path to where file should be saved
        s3_bucket_name (str): if saving to s3, name of s3 bucket (only needed if s3_flag is True)
        s3_output_path (str): if saving to s3, path in s3 bucket to save file to (only needed if s3_flag is True)

    Returns:
        None -- saves file to path
    """

    # convert plot to html
    convToHtml = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    # add plotly js plugin to output
    htmlout = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>' + "\n" + convToHtml

    # save to s3 or local
    if s3_flag == True:
        save_html_to_s3(s3_bucket_name,s3_output_path,htmlout,filename)
    else:
        #today_date = datetime.now().strftime("%Y-%m-%d")
        local_file = os.path.join(local_path,"{}.html".format(filename))
        with open(local_file, 'w+') as f:
            f.write(htmlout)
            f.close()
        logger.info("Html file saved to local. File is located at {}".format(local_file))


def save_html_to_s3(s3_bucket_name,s3_output_path,file_content,filename):
    """
    Saves plot html file to S3
    Args:
        s3_bucket_name (str): if saving to s3, name of s3 bucket
        s3_output_path (str): if saving to s3, path in s3 bucket to save file to
        file_content (str): html content of the plot to be saved
        filename (str): name of file to be saved

    Returns:
        None -- saves file to path
    """
    try:
        s3 = boto3.client("s3")
    except botoexceptions.NoCredentialsError:
        logger.error(
            "Your AWS credentials were not found. Verify that they have been made available as detailed in readme instructions")
        sys.exit(1)

    today_date = datetime.now().strftime("%Y-%m-%d")
    s3_filename = (s3_output_path+filename+"_{}"+".html").format(today_date)

    try:
        s3.put_object(Bucket=s3_bucket_name,Key=s3_filename,Body=file_content,ContentType="text/html")
    except botoexceptions.ParamValidationError:
        logger.error("There is an error in the data format. Verify the input to this function is html format")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error in trying to write data to s3: {}".format(e))
        sys.exit(1)

    logger.info("Html file was successfully saved to s3 bucket. File is located at {}".format(s3_filename))

def run_generate_forecast_plots(args):
    """
    Wrapper function for generating forecast plots
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

    global_forecast_df = get_global_forecasted_data(args.engine_string)
    global_plot_df = get_recent_global_confirmed_data(args.engine_string)
    fig = generate_forecast_plot(global_forecast_df,global_plot_df)
    get_html_and_save(fig,args.s3_flag,'global_cases_forecast',**config['generate_forecast_plots'])

    # country = 'Spain'
    #country_forecast_df = get_country_forecasted_data(country,args.RDS,args.engine_string)
    #country_plot_df = get_recent_country_confirmed_data(country,args.RDS, args.engine_string)
    #fig = generate_forecast_plot(country_forecast_df,country_plot_df)
    #get_html_and_save(fig,args.s3_flag,'country_cases_forecast',**config['generate_forecast_plots'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate trend plots with model forecast displayed')
    parser.add_argument('--config', '-c', default = 'config.yml', help='path to yaml file with configurations')
    parser.add_argument("--engine_string", default=None, help="Optional engine string for db to add data to ")
    parser.add_argument("--s3", dest='s3_flag', action='store_true', help="Use arg if you want to save s3 rather than locally.")

    args = parser.parse_args()

    run_generate_forecast_plots(args)