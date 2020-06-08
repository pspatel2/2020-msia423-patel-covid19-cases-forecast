import os

# Getting the parent directory of this file. That will function as the project home.
PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

### API ###
# NewsAPI KEY
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

### DATABASES ###
# FOR RDS
conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
DATABASE_NAME = os.environ.get("MYSQL_DATABASE")
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

if SQLALCHEMY_DATABASE_URI is not None:
    pass
elif host is None:
    # FOR LOCAL
    DATABASE_PATH = os.path.join(PROJECT_HOME, 'data/msia423_covid19_db.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:////{}'.format(DATABASE_PATH)
else:
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, DATABASE_NAME)