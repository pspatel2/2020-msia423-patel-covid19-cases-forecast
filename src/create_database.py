from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
import sqlalchemy as sql
import logging
import argparse
import os
import logging.config

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

class Global_Covid_Forecast(Base):
    """Create a data model to store forecasting predictions for confirmed cases"""
    __tablename__ = 'global_covid_forecast'
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=False, nullable=False)
    confirmed_cases_forecast = Column(Date,unique=False,nullable=False)

class Country_Covid_Forecast(Base):
    """Create a data model to store forecasting predictions for confirmed cases"""
    __tablename__ = 'country_covid_forecast'
    id = Column(Integer, primary_key=True)
    country = Column(String(100),unique=False, nullable=False)
    date = Column(Date, unique=False, nullable=False)
    confirmed_cases_forecast = Column(Date,unique=False,nullable=False)


def get_engine_string(RDS = False):
    """
    Get the engine string for the database connection.
    Args:
    RDS(boolean): Flag for executing for RDS vs local.
        If True, creates the database schema in RDS
        If False: creates the database schema locally in sqlite.

    Return:
        engine_string (str):
            If RDS = False -- returns the local path to sqlite location
            If RDS = True -- returns engine string for RDS
    """
    if RDS:
        # the engine_string format
        # engine_string = "{conn_type}://{user}:{password}@{host}:{port}/{database}"
        conn_type = "mysql+pymysql"
        user = os.environ.get("MYSQL_USER")
        password = os.environ.get("MYSQL_PASSWORD")
        host = os.environ.get("MYSQL_HOST")
        port = os.environ.get("MYSQL_PORT")
        DATABASE_NAME = 'msia423_covid19_db'
        engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, DATABASE_NAME)
        logging.debug("engine string: %s"%engine_string)
        return  engine_string

    else:
        engine_string = 'sqlite:///data/msia423_covid19_db.db'
        return engine_string

def create_db(args,SQL_URI=None):
    """
    Creates a relational database with the data models inherited from Base
    Args:
        args: From argparse, contains the RDS flag used to determine where the database schema will be created
        SQL_URI: Engine string for where to create connection. If None, engine string will be created by get_engine_string function

    Returns:
        None -- creates the database schema
    """
    if SQL_URI is None:
        RDS = eval(args.RDS)
        logger.info("RDS:%s"%RDS)
        SQL_URI = sql.create_engine(get_engine_string(RDS = RDS))
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(SQL_URI)
    logging.info("Database successfully created")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create tables in covid19 database")
    parser.add_argument("--RDS", default="False",help="True if you want to create in RDS else None.")
    args = parser.parse_args()

    engine = create_db(args)