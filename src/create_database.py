from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
import logging
import argparse
import logging.config
import helper

#set-up logging
logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)

Base = declarative_base()

class Country_Covid_Daily_Cases(Base):
    """Create a data model for the database to be set up for COVID-19 visualizations and forecasting"""
    __tablename__ = 'country_covid_daily_cases'
    id = Column(Integer, primary_key=True)
    country = Column(String(100),unique=False, nullable=False)
    date = Column(Date,unique=False, nullable=False)
    confirmed = Column(Integer,unique=False, nullable = False)
    recovered = Column(Integer,unique=False, nullable = False)
    active = Column(Integer,unique=False, nullable = False)
    deaths = Column(Integer,unique=False, nullable = False)

class Global_Covid_Daily_Cases(Base):
    """Create a data model for the database to be set up for COVID-19 visualizations and forecasting"""
    __tablename__ = 'global_covid_daily_cases'
    id = Column(Integer, primary_key=True)
    date = Column(Date,unique=False, nullable=False)
    confirmed = Column(Integer,unique=False, nullable = False)
    recovered = Column(Integer,unique=False, nullable = False)
    active = Column(Integer,unique=False, nullable = False)
    deaths = Column(Integer,unique=False, nullable = False)

class Global_Covid_Forecast(Base):
    """Create a data model to store forecasting predictions for confirmed cases"""
    __tablename__ = 'global_covid_forecast'
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=False, nullable=False)
    confirmed_cases_forecast = Column(Integer,unique=False,nullable=False)

class Country_Covid_Forecast(Base):
    """Create a data model to store forecasting predictions for confirmed cases"""
    __tablename__ = 'country_covid_forecast'
    id = Column(Integer, primary_key=True)
    country = Column(String(100),unique=False, nullable=False)
    date = Column(Date, unique=False, nullable=False)
    confirmed_cases_forecast = Column(Integer,unique=False,nullable=False)

class User_App_Inputs(Base):
    __tablename__ = 'covid_app_user_inputs'
    id = Column(Integer,primary_key=True)
    date = Column(Date,unique=False,nullable=False)
    name = Column(String(70),unique=False)
    age = Column(Integer,unique=False)
    country_of_residence = Column(String(100),unique=False)
    country_input = Column(String(100),unique=False)


def create_db(args):
    """
    Creates a relational database with the data models inherited from Base
    Args:
        args: From argparse:
            - optional sql engine string argument can be entered
    Returns:
        None -- creates the database schema
    """
    engine = helper.get_engine(args.engine_string)
    try:
        Country_Covid_Forecast.__table__.drop(engine)
    except:
        pass
    Base.metadata.create_all(engine)
    logging.info("Database successfully created")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create tables in covid19 database")
    parser.add_argument("--engine_string", default=None, help="Optional engine string for sqlalchemy")
    args = parser.parse_args()

    engine = create_db(args)