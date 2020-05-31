import traceback
from flask import render_template, request, redirect, url_for
import logging.config
from flask import Flask
import src.generate_forecast_plots as gfp
from flask_sqlalchemy import SQLAlchemy
import pickle
from src.create_database import User_App_Inputs
from datetime import datetime
import plotly
import os


# Initialize the Flask application
app = Flask("msia423-covid19-app", template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])

# Initialize the database
db = SQLAlchemy(app)


@app.route('/')
def index():
    """Main view that lists songs in the database.
    Create view into index page that uses data queried from Track database and
    inserts it into the msiapp/templates/index.html template.
    Returns: rendered html template
    """

    try:
        logger.debug("Index page accessed")
        return render_template('index.html')
    except:
        traceback.print_exc()
        logger.warning("Not able to display index page error page returned")
        return render_template('error.html')

def is_valid_country(country,country_list_file):
    """
    Checks to see if user input country is a valid country and if a forecast can be made for it
    Args:
        country (str): A country in the world

    Returns:
        valid (bool): Flag to determine if the a forecast plot can be generated for the input country
    """
    valid = False
    country_list = pickle.load(open(country_list_file, "rb"))
    if country.upper() in (name.upper() for name in country_list):
        valid = True

    return valid

@app.route('/add', methods=['POST'])
def add_entry():
    """
    """
    # get some user info
    name = str(request.form['name'])
    age = str(request.form['age'])
    residence = str(request.form['country_of_residence'])
    # get user input for country of interest
    country_input = str(request.form['country_input'])

    #check validity of input
    valid_input = is_valid_country(country_input,'countries.pkl')

    try:
        user_input = User_App_Inputs(date=datetime.now().date(),name=name, age=int(age), country_of_residence=residence,country_input=country_input)
        db.session.add(user_input)
        db.session.commit()
        logger.info("New user input added to database")
    except TypeError:
        logger.warning("There was an issue with these inputs. Please verify age was submitted as an integer value. Error page returned")
        return render_template('error.html')

    #if not valid, return error page.
    if valid_input == False:
        logger.error("A forecast cannot be made for the input country, please try to verify spelling or try another country")
        return render_template('error.html')
    else:
        logger.info("Valid country input, {}".format(country_input))
        country_forecast_df = gfp.get_country_forecasted_data(country_input,app.config["SQLALCHEMY_DATABASE_URI"])
        country_plot_df = gfp.get_recent_country_confirmed_data(country_input,app.config["SQLALCHEMY_DATABASE_URI"])
        fig = gfp.generate_forecast_plot(country_forecast_df,country_plot_df)
        fig.update_layout(title="Recent Confirmed Cases and Forecast for {}".format(country_input))
        convToHtml = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        htmlout = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>' + "\n" + convToHtml
        fname = "app/static/country_forecast.html"
        with open(fname, 'w+') as f:
            logger.info("Overwriting country plot")
            f.write(htmlout)
            f.close()
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])