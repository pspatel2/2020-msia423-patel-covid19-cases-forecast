# COVID-19 Confirmed Cases Forecasting 

***
__Developor__: [Parth Patel](https://github.com/pspatel2)  <br/> 
__QA__: [Greesham Simon](https://github.com/greeshamsimon)  
***

<!-- toc -->
- [Project Charter](#project-charter)
    * [Vision](#vision)
    * [Mission](#mission)
    * [Success Criteria](#success-criteria) 
- [Planned Work](#planned-work)
    * [Backlog](#backlog)
    * [Icebox](#icebox)
- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Run Data Acquisition via Docker](#1-initialize-the-database)
    + [Configuration Modifications](#configuration-modifications)
    + [Docker Commands](#docker-commands)
  * [2. Create the database](#2-create-database-locally-sqlite-or-on-amazon-rds)
    + [Create Locally for SQLite](#local-database)
    + [Create on RDS](#rds-database)

<!-- tocstop -->

## Project Charter

### Mission:
Coronavirus is a family of viruses that can cause illness, which can vary from the common cold to more severe illnesses such as the current pandemic known as COVID-19. As the COVID-19 pandemic accelerates at a frightening pace, most of world’s governments have issued orders for their citizens to stay at home to minimize the spread of the virus. There is a lot of uncertainty around the virus and its spread which adds to the fear and panic around the situation. The primary focus of this app is to provide forecasting of COVID-19 cases in attempts to reduce this level of uncertainty by some degree. Such a forecast could prove helpful not only to general public but also to politcal leaders and healthcare workers on the front lines. The second "MVP" of the app is the goal to serve as a "home-base" for users to get the forecasting information along with other statistics of the pandemic and headlines/links for the top trending news.

### Vision:
Utilize historical time series data of COVID-19 cases to forecast the number of expected COVID-19 cases for each day through the next week. This forecast will be computed at both the global level and the country level. Data is updated daily and is pulled via a free [API](https://covid19api.com/#details). This data is originally sourced by Johns Hopkins CSSE. Utilize one of the many free news APIs on the web or develop a custom scraper for achieving MVP 2 vision. 

### Success Criteria
__Machine Learning Performance Metric__: Forecasting model achieves forward-chaining averaged MAPE of 15% or less.

__Business Metrics__: Inbound traffic of 100 unique users and 50% retention thereafter.

## Planned Work
### Initiative 1: Forecasting model to predict number of COVID-19 cases in the future
**_Epic 1: Data acquisition_**
- Story 1: Write Python script to pull data using the API 
- Story 2: Explore other sources of data that could be joined with the API data for additional features

**_Epic 2: Data preparation_**
- Story 1: Exploratory data analysis and data quality checks
- Story 2: Design new features 
- Story 3: Create final cleaned dataset to be used for modeling

**_Epic 3: Model development_**
- Story 1: Build and evaluate a linear regression model for forecasting as a baseline approach
- Story 2: Build a Holt Linear model
- Story 3: Research on ARIMA modeling and build an ARIMA model
- Story 4: Research and build a Prophet model
- Story 5: Research RNN modeling
- Story 6: Build RNN Model
- Story 7: Compare model performances and select final model
- Story 8: Repeat modeling process at the USA state level

**_Epic 4: Ensemble models_**
- Story 1: Ensemble predictions from models built in Epic 3
- Story 2: Research other efforts to perform similar predictions online
- Story 3: If similar open source models are found online by other users, ensemble them into the prediction

### Initiative 2: Web Application Development and User Experience Design
**_Epic 1: Configure deployment pipeline_**
- Story 1: Create requirements.txt file so that the appropriate packages and their respective versions can be installed/loaded in any environment/container
- Story 2: Set-up a S3 bucket/instance and store raw data here
- Story 3: Create script to pull daily data from the API and append to data in S3
- Story 4: Initialize RDS database with model results

**_Epic 2: Front end interface for model results_**
- Story 1: Global trend plot with forecasted values shown
- Story 2: Country level trend plot with forecasted values shown and user UI to selection country of interest
- Story 3: USA state-wise trend plot with forecasted values
- Story 4: Write the script to deploy the Flask app 

**_Epic 3: Descriptive analyses_**
- Story 1: Global geospatial map to show time lapse and current state of COVID-19 cases
- Story 2: Racing bar chart (as alt viz) to show the spread of the virus
- Story 3: Top trending COVID-19 news API or scraper code
- Story 4: Viz/link UI for top news results

**_Epic 4: Product tests and refinement_**
- Story 1: Create tests to confirm model functionality
- Story 2: Create test(s) for UI exception handling
- Story 3: Adjust product based on test results and roll out closed prototype of the app
- Story 4: Send link to prototype to beta users for feedback
- Story 5: Improve UI based on beta user feedback
- Story 6: As data accumulates explore forecasting accuracy beyond 7 days

**_Epic 5: Release and Demo_**
- Story 1: Verify git repo is up to date, clean, and confirm all deliverables are met per requirements
- Story 2: Create presentation deck for final demo
- Story 3: Collect feedback on final presentation deck/demo
- Story 4: Incorporate feedback by making final adjustments to app and presentation

### Backlog

__Sprint Sizing Legend:__
- 0 points - quick chore
- 1 point ~ 1 hour (small)
- 2 points ~ 1/2 day (medium)
- 4 points ~ 1 day (large)
- 8 points - big and needs to be broken down more when it comes to execution (placeholder for future work)

1.  Initiative1.Epic1.Story1: Pull Data from API (1pts) -- Sprint 1 (April 11 - April 25)
2.  Initiative1.Epic1.Story2: Research for Additional Data (2pts) -- Sprint 1 (April 11 - April 25)
3.	Initiative1.Epic2.Story1: EDA & QA (4pts) -- Sprint 1 (April 11 - April 25)
4.	Initiative1.Epic2.Story2: Design New Features (2pts) -- Sprint 1 (April 11 - April 25)
5.	Initiative1.Epic2.Story3: Create finalized dataset (1pts) -- Sprint 1 (April 11 - April 25)
6.	Initiative1.Epic3.Story1: Linear Regression & Eval (4pts) -- Sprint 1 (April 11 - April 25)
7.	Initiative1.Epic3.Story2: Holt Winters Model (2pts) -- Sprint 2 (April 25 - May 9)
8.	Initiative1.Epic3.Story3: ARIMA Modeling (4pts) -- Sprint 2 (April 25 - May 9)
8.	Initiative1.Epic3.Story4: Prophet Modeling (2pts) -- Sprint 2 (April 25 - May 9)
9.	Initiative1.Epic3.Story5: Research LSTM (2pts) -- Sprint 2 (April 25 - May 9)
10.	Initiative1.Epic3.Story6: Build LSTM (4pts) -- Sprint 2 (April 25 - May 9)
11. Initiative1.Epic3.Story7: Compare models and select final (1pts) -- Sprint 2 (April 25 - May 9)
12.	Initiative2.Epic1.Story1: requirements.txt file (1pts) – Sprint 3 (May 9 – May 23)
13.	Initiative2.Epic1.Story2: Set up S3 instance (2pts) – Sprint 3 (May 9 – May 23)
14.	Initiative2.Epic1.Story3: Daily data append to S3 (4pts) – Sprint 3 (May 9 – May 23)
15.	Initiative2.Epic1.Story4: Initialize RDS database (4pts) – Sprint 3 (May 9 – May 23)
16.	Initiative2.Epic2.Story1: Global trend plot w/forecast (2pts) – Sprint 3 (May 9 – May 23)
17.	Initiative2.Epic2.Story2: Country trend plot w/forecast (4pts) – Sprint 3 (May 9 – May 23)
18.	Initiative2.Epic2.Story4: Web app construction (8pts) – Sprint 3 (May 9 – May 23)
19.	Initiative2.Epic4.Story1: Unit Tests for Model (2pts) – Sprint 4 (May 23 – June 6)
20.	Initiative2.Epic4.Story2: Unit Tests for UI (2pts) – Sprint 4 (May 23 – June 6)
21.	Initiative2.Epic4.Story3: Beta roll-out (4pts) – Sprint 4 (May 23 – June 6)
22.	Initiative2.Epic5.Story1: Git Housekeeping and reqs check (2pts) – Sprint 4 (May 23 – June 6)
23.	Initiative2.Epic5.Story2: Final Presentation & Demo Dev (4pts) – Sprint 4 (May 23 – June 6)
24.	Initiative2.Epic5.Story3: Collect Presentation Feedback (2pts) – Sprint 4 (May 23 – June 6)
25.	Initiative2.Epic5.Story4: Final modifications and roll-out (4pts) – Sprint 4 (May 23 – June 6)

### Icebox
1.	Initiative1.Epic3.Story7: Forecasting at the USA State Level
2.	Initiative1.Epic4: Ensemble Models
3.	Initiative2.Epic2.Story3: USA State Level Plots
4.	Initiative2.Epic3: Descriptive Analyses
5.	Initiative2.Epic4.Story4: Send link to beta testers (1pts)
6.	Initiative2.Epic4.Story5: Update UI Based on Feedback(8pts)
7.	Initiative2.Epic4.Story6: Update UI Based on Feedback(4pts)

## Directory structure 

```
├── README.md                         <- You are here
├── app
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│       │
│       ├──pull_and_save_cases_data.ipynb/                   <- Notebook used to test pulling COVID19 cases data
│       ├──pull_news_headlines.ipynb/                        <- Notebook used to test pulling news headlines for covid19
│       ├──covid19_eda.ipynb/                                <- Notebook used to explore and plot covid19 data
│       ├──covid19_forecasting_model_development.ipynb/      <- Notebook used for time series model development (global)
│       ├──covid19_forecasting_model_development_country_level.ipynb/      <- Notebook used for time series model development (country)
│       ├──covid19_forecasting_model_development.ipynb/      <- Notebook used for time series model development (global)
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│       ├──data_acquistion.ipynb/                            <- Script for pulling covid case data from API and writing to s3
│       ├──create_database.ipynb/                            <- Script for creating either a SQLlite db or a RDS db
│       ├──get_news.ipynb/                                   <- Script for getting BBC news headliens for covid-19
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app (WIP)

### 1. Run Data Acquisition via Docker

#### Configuration Modifications
First navigate to config.yml located in the config directory. Update the following two options:
* s3_bucket_name &rarr; to the name of a s3 bucket that you own and would like the data to be written to
* output_file_path &rarr; path in your s3 bucket that you want to save to (you can leave it as "" to save to s3 home)

Next open the aws_creds file in a text editor of your choice. Update both fields to correspond with your AWS account.
 
#### Docker commands
Next, verify that you are in the 2020-msia423-patel-covid19-cases-forecast root directory. Issue the following command in order
to build the docker image.
    
```
docker build -t covid19cases .
```
Last to execute the process, issue the following commmand:
```
docker run --env-file=aws_creds covid19cases src/data_acquistion.py --config=config/config.yml
```

### 2. Create database locally (SQLite) or on Amazon RDS
The file create_database.py creates the database schema. Before continuing, if you do not have the docker container running
from part 1 (Run Data Acquisition via Docker), please issue the following command from the 2020-msia423-patel-covid19-cases-forecast root directory
```
docker build -t covid19cases .
```

#### Local Database: 
To create the database locally,  run the command:
```
docker run --mount type=bind,source="$(pwd)"/data,target=/src/data covid19cases src/create_database.py
```
To confirm the creation of the database (aside from reviewing the logfile), you can navigate to the data directory and find it
there named as "msia423_covid19_db".

#### RDS Database:
To create the database in RDS, if you have not previously set-up some environment variables related to 
your RDS account, you will need to do so now. To do so, fill out the rdsconfig file  (located in the config/ dir ) in
its entirety. An explanation of the fields is as follows:
* MYSQL_USER: the master username associated with your RDS DB instance (try using admin if you do not recall altering this)
* MYSQL_PASSWORD: the password associated with the aforementioned master username 
* MYSQL_HOST: RDS endpoint associated with your database
* MYSQL_PORT: port associated with the RDS instance -- generally 3306

Once you have done so, issue the commands: 
```
echo 'source config/rdsconfig' >> ~/.bashrc
source ~/.bashrc
```
This will source the environment variables for use by your bash tool. Verify you are in the project root directory, 
then execute the following command to create the database schema in RDS.
```
docker run --env MYSQL_HOST --env MYSQL_PORT --env MYSQL_USER --env MYSQL_PASSWORD covid19cases src/create_database.py --RDS=True
```
The database should now be set-up in your RDS instance. You can connect to your RDS database to verify the schema.
Once you're connected, type:
```
use msia423_covid19_db;
```
Followed by:
```
show tables;
```
You should see:

![image](../../rds_schema.PNG)

Similarly you can review the schema of each table by issuing the command below, replacing "<table_name>"
with the table of interest.
```
show columns from <table_name>;
```
A example result for the country_covid_daily_cases is shown below.

![image](../../sample_table_schema.PNG)