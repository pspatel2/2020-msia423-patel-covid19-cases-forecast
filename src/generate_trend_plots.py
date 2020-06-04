import pandas as pd
import botocore.exceptions as botoexceptions
import boto3
import sys
import helper
import logging.config
import yaml
import argparse
import plotly.express as px
import plotly
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

#set-up logging
logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)

def generate_global_line_plot(engine_string):
    """
    Creates a 'plotly' figure that shows the number of confirmed cases, deaths, and active cases of Covid-19 globally
    Args:
        engine_string (str): sqlalchemy string for the connection.

    Returns:
        None -- saves out plotly figure
    """
    # query the necessary data from database
    query = """SELECT * FROM global_covid_daily_cases"""
    global_df = helper.get_data_from_database(query,engine_string)

    # group data by date
    global_df_date = global_df.groupby('Date')['Recovered', 'Deaths', 'Confirmed'].sum().reset_index()

    # create figure using plotly express

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=global_df_date['Date'], y=global_df_date['Confirmed'], fill='tozeroy', name='Confirmed'))  # fill down to xaxis
    fig.add_trace(go.Scatter(x=global_df_date['Date'], y=global_df_date['Deaths'], fill='tozeroy', name='Deaths'))  # fill down to xaxis
    fig.add_trace(
        go.Scatter(x=global_df_date['Date'], y=global_df_date['Recovered'], fill='tozeroy', name='Recovered'))  # fill down to xaxis
    fig.update_layout(xaxis_rangeslider_visible=True)

    # convert figure to html and save it out to s3 or local depending on the option specified
    convToHtml = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    htmlout = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>' + "\n" + convToHtml

    return htmlout

def generate_world_time_lapse(engine_string):
    """
    Creates a 'plotly' figure that shows the number of confirmed cases across the globe (at the country level)
     over time with an animation
    Args:
        engine_string (str): sqlalchemy string for the connection.

    Returns:
        None -- saves out plotly figure
    """
    # query the necessary data from database
    query = """SELECT * FROM country_covid_daily_cases"""
    country_df = helper.get_data_from_database(query,engine_string)

    # manipulate the data to the desired form
    country_plot_df = country_df.groupby(['Date', 'Country'])['Confirmed', 'Deaths'].max().reset_index()
    country_plot_df["Date"] = pd.to_datetime(country_plot_df["Date"]).dt.strftime('%m/%d/%Y')
    # generate figure using plotly express
    fig = px.scatter_geo(country_plot_df, locations="Country", locationmode='country names',
                         color=np.power(country_plot_df["Confirmed"], 0.3) - 2,
                         size=np.power(country_plot_df["Confirmed"] + 1, 0.25) - 1, hover_name="Country",
                         hover_data=["Confirmed"],
                         range_color=[0, max(np.power(country_plot_df["Confirmed"], 0.25))],
                         projection="natural earth", animation_frame="Date",
                         color_continuous_scale=px.colors.sequential.Plasma,
                         title='COVID-19: Progression of spread'
                         )
    fig.update_coloraxes(colorscale="YlOrRd")
    fig.update(layout_coloraxis_showscale=False)

    # convert figure to html and save it out to s3 or local depending on the option specified
    convToHtml = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    # starts the animation as paused
    convToHtml = convToHtml.replace(", null", ', {"play-state":"paused"}')
    # add a link back to homepage
    link_to_home_page = '<h3><a href = "http://localhost:5000/">COVID-19 Forecasting Dashboard</a></h3>'
    htmlout = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>' + "\n" + link_to_home_page + "\n" + convToHtml
    return htmlout

def save_html_to_s3(file_content,filename,s3_bucket_name,s3_output_path):
    """
    Saves html representation of a plotly plot to s3
    Args:
        file_content (str): string representation of html for the plot of interest
        filename (str): desired name for the file
        s3_bucket_name (str): s3 bucket name for the file to be saved to
        s3_output_path (str): path within the s3 bucket where the file will be saved to

    Returns:
        None -- saves html file to s3
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

def save_html_to_local(file_content,filename,local_path):
    """
    Saves html representation of plotly plot to s3
    Args:
        file_content (str): string representation of html for the plot of interest
        filename (str): desired name for the file
        local_path (str): local path for where the file should be saved to

    Returns:
        None -- saves html file locally
    """
    # today_date = datetime.now().strftime("%Y-%m-%d")
    # local_file = os.path.join(local_path, "{}_{}.html".format(filename, today_date))
    try:
        local_file = os.path.join(local_path,"{}.html".format(filename))
        with open(local_file, 'w+') as f:
            f.write(file_content)
            f.close()
            logger.info("Html file was successfully saved to local machine. File is located at {}".format(local_file))
    except FileNotFoundError:
        logger.error("The local file path you've specified does not exist. Verify the path is correct in the config.yml")


def run_generate_trend_plots(args):
    """
    Wrapper function to run steps to generate trends plots for COVID-19 webapp
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

    global_trend_plot_html = generate_global_line_plot(args.engine_string)
    global_animation_plot_html = generate_world_time_lapse(args.engine_string)

    if args.s3_flag == True:
        save_html_to_s3(global_trend_plot_html,'global_cases',**config['generate_trend_plots']['save_html_to_s3'])
        save_html_to_s3(global_animation_plot_html,'global_animation',**config['generate_trend_plots']['save_html_to_s3'])
    else:
        save_html_to_local(global_trend_plot_html,'global_cases',**config['generate_trend_plots']['save_html_to_local'])
        save_html_to_local(global_animation_plot_html,'global_animation',**config['generate_trend_plots']['save_html_to_local'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate visualizations for global covid19 case numbers.')
    parser.add_argument('--config', '-c', default = 'config.yml', help='path to yaml file with configurations')
    parser.add_argument("--engine_string", default=None, help="Optional engine string for db to add data to ")
    parser.add_argument("--s3", dest='s3_flag', action='store_true', help="Use arg if you want to save s3 rather than locally.")

    args = parser.parse_args()

    run_generate_trend_plots(args)

    logger.info("generate_trend_plots.py was run successfully.")