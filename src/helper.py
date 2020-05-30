import boto3
import sys
import botocore.exceptions as botoexceptions
import logging.config
import logging
import os
import sqlalchemy as sql
from sqlalchemy import exc
import pandas as pd

logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger()

def get_latest_s3_data(bucket_name,s3_file_path):
    '''
    Retrieves the latest object saved to the specified path s3 bucket path.
    Args:
        bucket_name (str): the name of S3 bucket of interest
        s3_file_path (str): s3 bucket file path of interest

    Returns:
        most_recent_object: the most recently modified object in the s3 file path specified
    '''
    ## try to connect to s3 prior to starting up any processing
    try:
        s3 = boto3.client("s3")
    except botoexceptions.NoCredentialsError:
        logger.error("Your AWS credentials were not found. Verify that they have been made available as detailed in readme instructions")
        sys.exit(1)
    ## try to access s3 file path of interest
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_file_path)
        logger.debug("Successfully reached s3 bucket")
    except botoexceptions.ParamValidationError as error:
        logger.error('The parameters you provided are incorrect: {}'.format(error))
        sys.exit(1)
    except botoexceptions.ClientError as error:
        logger.error('Unexpected error with reaching the s3 bucket: {}'.format(error))
        sys.exit(1)
    except Exception as error:
        logger.error('Unexpected error: {}'.format(error))
        sys.exit(1)
    ## try to pull objects from the s3 file path
    try:
        s3_objects = response['Contents']
        logger.debug("Successfully retrieved s3 objects")
    except KeyError as e:
        logger.error('There is no previous data from this acquisition pipeline in your s3 bucket. Please run again with an additional cmd line arg --start_date')
        sys.exit(1)
    ## get most recent object
    most_recent_object = max(s3_objects, key=lambda x: x['LastModified'])
    return most_recent_object

def get_engine_string(RDS = False):
    """
    Get the engine string for the database connection.
    Args:
    RDS(boolean): Flag for using  RDS vs local.
        If True: creates the database schema in RDS
        If False: creates the database schema locally in sqlite.

    Return:
    engine_string (str): sqlalchemy string for the connection. String is dependent on:
        If RDS = False -- returns the local path to sqlite location
        If RDS = True -- returns engine string for RDS
    """
    # for RDS
    if RDS==True:
        # the engine_string format
        # engine_string = "{conn_type}://{user}:{password}@{host}:{port}/{database}"
        conn_type = "mysql+pymysql"
        user = os.environ.get("MYSQL_USER")
        password = os.environ.get("MYSQL_PASSWORD")
        host = os.environ.get("MYSQL_HOST")
        port = os.environ.get("MYSQL_PORT")
        DATABASE_NAME = os.environ.get("MYSQL_DATABASE")
        engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, DATABASE_NAME)
        logging.debug("engine string: %s"%engine_string)
        return  engine_string
    # for local
    else:
        engine_string = 'sqlite:///data/msia423_covid19_db.db'
        return engine_string

def get_engine(RDS=False,engine_string=None):
    """
    Creates sqlalchemy engine
    Args:
        RDS (boolean): Flag for using RDS vs local
        engine_string (str): sqlalchemy string for the connection

    Returns:
        engine (sqlalchemy.engine.base.Engine): sqlalchemy engine for database of interest
    """
    if engine_string is None:
        logger.info("RDS:%s"%RDS)
        engine_string = get_engine_string(RDS = RDS)
        engine = sql.create_engine(engine_string)

    else:
        engine = sql.create_engine(engine_string)

    return engine

def add_to_database(df,table_name,if_exists_condition,RDS=False,engine_string=None):
    """
    Adds data from a pandas DataFrame to a local or RDS MySQL database
    Args:
        df (pandas DataFrame): DataFrame containing data to be added into the database of interest
        table_name (str): Name of the table the data should be added to
        if_exists_condition (str): Argument to determine what should be done if data already exists in the table
        RDS (boolean): Flag for executing on RDS vs local.
        engine_string (str): sqlalchemy string for connection to desired database

    Returns:
        None -- adds data to a MySQL database

    """
    engine = get_engine(RDS,engine_string)
    try:
        df.to_sql(table_name,engine,if_exists=if_exists_condition,index=False)
        logger.debug("Data inserted into {}".format(table_name))
    except exc.IntegrityError:
        logger.error("There is an issue with duplication from your request. Try using 'append' as the argument for the if_exists_condition")
        sys.exit(1)
    except exc.OperationalError:
        logger.error("Unable to connect to the database. Verify the connection info provided (in rds_config file) is accurate."
                     "Also verify you had write access to this database")
        sys.exit(1)
    except exc.TimeoutError:
        logger.error("Timeout issue with trying to read from the database. Please try again later")
        sys.exit(1)
    except exc.SQLAlchemyError as error:
        logger.error("Unexpected error with the SQLAlchemy: {}:{}".format(type(error).__name__, error))
        sys.exit(1)

def get_data_from_database(query,RDS=False,engine_string=None):
    """
    Retrieve data from a MySQL database on local machine or RDS
    Args:
        query (str): single string representing the query of interest
        RDS (boolean): Flag for executing on RDS vs local.
        engine_string (str): sqlalchemy string for connection to desired database

    Returns:
        df (pandas DataFrame): DataFrame containing results from input query
    """

    if engine_string is None:
        logger.info("RDS:%s"%RDS)
        engine_string = get_engine_string(RDS = RDS)
        engine = sql.create_engine(engine_string)
    else:
        engine = sql.create_engine(engine_string)
    try:
        df= pd.read_sql(query,con=engine)
        logger.debug("Data successfully retrieved")
    except exc.OperationalError:
        logger.error("Unable to connect to the database. Verify the connection info provided (in rds_config file) is accurate. "
                     "Also verify you had read access to this database")
        sys.exit(1)
    except exc.TimeoutError:
        logger.error("Timeout issue with trying to read from the database. Please try again later")
        sys.exit(1)
    except exc.SQLAlchemyError as error:
        logger.error("Unexpected error with the SQLAlchemy: {}:{}".format(type(error).__name__, error))
        sys.exit(1)

    return df
