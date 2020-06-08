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
- [Running the Program for MSiA 423 Grading Purposes](#running-the-program-for-msia-423-grading-purposes)
- [Running the Program End to End](#running-the-program-end-to-end)
  * [1. Configuration and Environment Variable Set-up for Main Pipeline](#1-configuration-and-environment-variable-set-up-for-main-pipeline)
    + [1a. Set-up for Running Program Completely Locally](#1a-set-up-for-running-the-complete-program-fully-local) 
        + [Environment Variables](#environment-variables) 
        + [Configuration Options](#configuration-options)
    + [1b. Set-up for Running Program Completely Locally Aside from Data Acquisition in s3](#1b-set-up-for-running-program-completely-locally-aside-from-data-acquisition-in-s3) 
        + [Environment Variables](#environment-variables) 
        + [Configuration Options](#configuration-options)
    + [1c. Set-up for Running Program With Data Acq in s3, Database in RDS, All Else Local (DEFAULT)](#1c-default-set-up-for-running-program-with-data-acq-in-s3-database-in-rds-all-else-local) 
        + [Environment Variables](#environment-variables) 
        + [Configuration Options](#configuration-options)
    + [1d. Set-up for Running Program Fully in S3 and RDS](#1d-set-up-for-running-program-fully-in-s3-and-rds) 
        + [Environment Variables](#environment-variables) 
        + [Configuration Options](#configuration-options)
  * [2. Run the Data Acquisition and Modeling Pipeline](#2-run-the-data-acquisition-and-modeling-pipeline)
    + [Building the Docker Image](#build-the-docker-image) 
    + [Run-time Options](#run-time-options)
    + [Running the Pipeline](#running-the-pipeline)
    + [Verifying a Sucessful Run](#verifying-a-successful-run)
  * [3. Run the Web Application](#3-run-the-web-application)
  * [4. Code Unit Testing](#4-code-unit-testing)
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
├── requirements.txt                  <- Python package dependencies 
```

## Running the Program for MSiA 423 Grading Purposes
Note, in this section, instructions are written primarily for grading purposes for the MSiA423 course. Please realize these
instructions will not run the pipeline in its entirety (because of the requested fields in the submission form). 
It runs on old data for the training pipeline and the items displayed on the webpage will be outdated as well. 
This approach will not run many of the scripts that pertain to creating new elements for the webpage and making new forecasts. 
 __If you want the full pipeline__ you can still follow these directions but you will need to run an additional docker run
 statement that will be detailed. OR you can follow the end-to-end instructions in the section following this one.

Instructions in the next section detail all the configurations that can be changed and the optionality of running the model
pipeline and the app. This section focuses on running with all defaults and use the shortest path to have the app running 
on your local instance. In particular, the quick start uses s3 for data acquisition but runs everything else locally
including the database.

##### Environment Variables: 
You will __need__ to set environment variables for accessing s3. They will be called using the -e command and the variable names
that will be searched for are: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.

The newsAPI is not a part of the modeling pipeline; rather it  pulls in news headlines for the webpage, thus it can be 
skipped at the cost of this secondary functionality (e.g. not needed for grading). If you want to sign up for a newsAPI key, 
please go to the following page and follow the instructions: https://newsapi.org/register. You will be able to access 
the API key at the end of the registration process. Next, open the __news_api_env__ file in the  project root directory 
and enter your key where indicated. Do not add a space after the "=".

##### Docker Image: 
Build the docker image with the following command (place a name of your choosing that replaces "<image_name>")
```
docker build -f="DockerfileBash" -t <image_name> .
```
Run the model training pipeline with the command below, again replacing "<image_name>":
```
docker run --mount type=bind,source="$(pwd)"/data,target=/src/data --mount type=bind,source="$(pwd)"/models/global,target=/src/models/global --mount type=bind,source="$(pwd)"/models/country,target=/src/models/country  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY <image_name> run_model_pipeline.sh
```

To run the app, first build the docker image using the command below, replacing "<image_name>":
```angular2
docker build -f="DockerfileApp" -t <image_name> .
```
Next issue the command, replacing "<image_name>":
```angular2
docker run --env-file=rds_config -p 5000:5000 <image_name>
```
To view the app in browser and/or for more details on configurations, view section 3 of this report that contains more details.


__THESE ARE THE STEPS TO GENERATE NEW DATA, FORECASTS, AND ARTIFACTS FOR THE WEBPAGE__:

First open the run_model_pipeline.sh file and uncomment line 4. Then re-build the docker image and re-run the training pipeline
command. No API key is needed to pull new data.

Then run the model execution (forecasting) and file generation (for webapp) pipeline using the command below, again replacing "<image_name>".
If you have a newsAPI key and added it to the environment file, add the argument --env-file=news_api_env to command as well.
```angular2
docker run --mount type=bind,source="$(pwd)"/data,target=/src/data --mount type=bind,source="$(pwd)"/app/static,target=/src/app/static <image_name> run_forecast_appfiles_pipeline.sh
```
To run the app, first build the docker image using the command below, replacing "<image_name>":
```angular2
docker build -f="DockerfileApp" -t <image_name> .
```
Next issue the command, replacing "<image_name>":
```angular2
docker run -p 5000:5000 <image_name>
```
To view the app in browser and/or for more details on configurations, view section 3 of this report that contains more details.

## Running the Program End to End
In this section, the steps to run the program from end to end are discussed. These means from the initial API call for data
all the way through having everything ready to launch the webapp

### 1. Configuration and Environment Variable Set-up for Main Pipeline
Depending on how you decide to run the pipeline there can be quite a few different environment variables that need to be
set and passed to the Docker container. In this section, the necessary configurations for each approach will be specified.

#### 1a. Set-up for Running the Complete Program Fully Local 
In this scenario, the execution pipeline along with the app will run completely on your local machine. 

##### Environment Variables: 
In this case there is only one 'required' environment variable, which is an API key for the newsAPI. 
However, the newsAPI is not a part of the modeling pipeline, it just pulls in news headlines for the webpage, thus it can
also be skipped at the cost of this secondary functionality. To sign up for a newsAPI key, please go to the following page
and follow the instructions: https://newsapi.org/register. You will be able to access the API key at the end of the 
registration process. Next, open the __news_api_env__ file in the project root directory and enter your key where indicated.
Do not add a space after the "=".

##### Configuration Options:
In this scenario, there are no configurations that must be changed for a successful run, however there are many options
you can adjust. The configurations that are the most common to change are discussed below.
__config.py__: Navigate to the src folder and open the config.py file. 
* In here you can change the "DATABASE_PATH" configuration to choose
the name of the local database. Caution, if you change the path from "data/", you will need to adjust the docker mounts
downstream to make sure the database saves out locally.
* You can also adjust line 8 in this file if you have decided to source your newsAPI key under some other variable name.
__config.yml__: Navigate to the config folder from the project root directory and open the config.yml file. The file is 
laid out such that each script has its own configuration blocks and within that block each function in the script has its 
own block. So you can intuitively locate the configurations you might want to change. With this layout, it is important 
to recognize the output of one script is potentially the input of another, thus if you change output pathing, please look
downstream to adjust the same path being taken in as an input downstream. An example is:  
* Under "data_acquisition", you can adjust the "local_filepath_out" to choose where to save the raw covid-19 data locally.
Note that if you choose to do this, you must also change the "input_file_path" config under "data_preparation-get_local_data".

This is all in terms of environmental variables and configurations for a full local run. You can jump onto the section
"Run the Data Acquisition and Modeling Pipeline" for next steps if you are choosing to run completely locally.

#### 1b. Set-up for Running Program Completely Locally Aside from Data Acquisition in s3
In this scenario, the execution pipeline along with the app will run completely on your local machine other than the covid-19
input data, which will be pulled from the API and saved to s3. It will then be accessed from s3 for subsequent steps.

##### Environment Variables: 
You will __need__ to set environment variables for accessing s3. If you already are aware of the process to set these
please do so in the manner of your choosing. Otherwise, in the root directory of the repo, there is a file called __aws_creds__. 
Please open this file and enter the information within the file that is associated with your s3 account. Do not use 
quotation marks or include any spaces in the file. Save this file and close it. How to use this file will be discussed 
in a later section of this readMe. 

In addition, for secondary functionality of the webapp, you will need to get a newsAPI key. Please refer to the environment
variable section in part 1a of this readMe for instructions on how to get a key and its relative importance in this pipeline.

##### Configuration Options:
In this case, there is one particular configuration that must be changed for a successful run of the pipeline. Other configs
such as local file pathing can be altered as explained in Configuration Options section in part 1a. 

The configuration that __must__ modified is the name of the s3 bucket. Navigate to the config folder and open config.yml. 
In this file change the value of the instances associated with the key '__s3_bucket_name__' in lines 3 and 9 of the file to 
correspond to your s3 bucket name. You may change the bucket directory paths (lines 4 and 10) if you wish to as well. 
If you do not, the default paths will be generated in your bucket.

Please see the __config.py__ section in part 1a if you wish to configure the name of the local database data is written to.
Otherwise a defaulted value will be used.

#### 1c. DEFAULT: Set-up for Running Program With Data Acq in s3, Database in RDS, All Else Local
This is the default method set in this repo. It is fairly similar to 1b aside from changing from a local SQLite database 
to using an RDS instance.

##### Environment Variables: 
As discussed in part 1b of the the readMe, you will __need__ to set environment variables for accessing s3. Instructions
on how to do so is localed in part 1b in the Environment Variables section. Other configs such as local file pathing can 
again be altered as explained in Configuration Options section in part 1a.  

In addition to this, you will also __need__ to 
set your RDS configurations as environment variables. To do so, please open the file __rds_config__ in the repo root directory.
file. The variables in this file should be adjusted according to your RDS instance--do not use quotation marks or spaces within the file
A brief explanation of these variables are below:
* MYSQL_USER: the master username associated with your RDS instance (try using admin if you do not recall altering this)
* MYSQL_PASSWORD: the password associated with the aforementioned master username 
* MYSQL_HOST: RDS endpoint associated with your instance
* MYSQL_PORT: port associated with the RDS instance -- generally 3306
* DATABASE_NAME: Name of the database to work with

Finally, for secondary functionality of the webapp, you will need to get a newsAPI key. Please refer to the environment
variable section in part 1a of this readMe for instructions on how to get a key and its relative importance in this pipeline.

##### Configuration Options:
Please go to the Configuration Options section in part 1b. The same discussion applies here aside from the final sentence
pertaining to the local database configuration in the config.py

In addition, you will need to change some of the filename/pathing as the code expects certain things for finding files 
in s3 and organizing outputs. Namely there are some potential changes to be made under the generate_forecasts part of the config.yml
* If you have not made any s3 pathing changes to the "train_models" part of the config.yml since cloning the repo then simply do the following:
    * For configs: get_model->bucket_dir_path, et_country_list->bucket_dir_path, get_country_list-> input_filename, and 
    get_country_forecast->bucket_dir_path, update the date you say in the path to today's date. 
* If you've altered s3 pathing to the "train_models" part of the config.yml, then you need do a little more.
   * The config, get_model->bucket_dir_path, must have a path that matches the path under train_models->global_model_configs->save_model_to_s3
   ->s3_output_path. Copy this path and add "/yyyy-mm-dd" to it, filled in with today's date as the value for the bucket_dir_path config
   * Repeat this with the config, get_country_list->bucket_dir_path. Verify the path matches that under train_models->country_model_configs->
   save_model_to_s3->s3_output_path. Add a "/yyyy-mm-dd" to the path, filled in with today's date.
   * Follow the same exact steps as in the second bullet, but fore the config, get_country_forecast->bucket_dir_path
   * Also in the config, get_country_list-> input_filename, add a "_yyyy-mm-dd" to the path, filled in with today's date

#### 1d. Set-up for Running Program Fully in S3 and RDS

##### Environment Variables: 
Please go to the Environment Variables section of part 1c. These directions apply equivalently here.
##### Configuration Options:
This scenario is almost identical to part 1c. The only difference is that you will need to update the config.yml file a little more.
Namely, you __must__ change the value associated with all instances (lines 3,9,16,26,47,66,75,82,87,92) of the key __s3_bucket_name__ to correspond to your s3 bucket.
Similarly you can change (you don't have to though) any bucket directory path reference (lines 4,10,17,27,48,67,76,83,88,93) in the config.yml file--be careful to verify consistency. E.g.
if you change an output path, it might be the input path for a downstream function. For any other configuration choices you
can refer to the applicable section in part 1c.


### 2. Run the Data Acquisition and Modeling Pipeline
This section will discuss the building of the Docker image and the subsequent Docker run command to execute the pipeline for 
modeling and retrieving all things needed for the webapp.

#### Build the Docker Image
For all of various choices of running the pipeline (with or without s3, with or without RDS, etc) the Docker image command
remains tme same. From the root directory of the project repo, please issue the command below to build the image. You __must__
replace "<image_name>" with a name of your choice.
```angular2
docker build -f="DockerfileBash" -t <image_name> .
```

#### Run-time Options
Depending on which path you've chosen in part 1a-1d (full local, RDS or no RDS, etc) there will be a couple of modifications
you may need to make. Particularly, since this code repo gives you the option of different levels of s3 usage, a command line arg
is necessary where and when to use s3. Aside from this there a few command line args to be aware that apply to all choices 1a-1d.

Storage approach dependent run-time options:
* For option 1a (full local), please open the run_main_pipeline.sh in a text editor. Remove the --s3 from lines 4 and 10.
* For options 1b and 1c, no changes are needed in the run_main_pipeline.sh. If you happened to have changed this and want
to get back to the default, make sure there is a --s3 at the end of lines 4 and 10.
* For option 1d (full s3), please open the run_main_pipeline.sh in a text editor. Add --s3 to lines 10,13,16,19,22, and 25

General run-time options:
The __data_acquisition.py__ script has a few command line args to be aware of. NOTE, the start_date and end_date API params 
discussed below have been slated to be incorporated in the API but as of 6/1/2020, they are not yet functional.
* --start_date: This is the date which will be used as the date from which the data pull will begin from. The rationale is 
to prevent the app from having to go get 100 MB+ data each day and instead just getting the new data for previous day. If you use s3
the code will automatically find the date of the last pull and use that as the start_date. It is key to note that this arg is set to
'01-01-2020' in the default 'run_main_pipeline.sh' because the first time you use this script, you will not have a data file in your s3,
which will not allow the code to find what it should use as the start date. For local, if no arg is specified, it defaults to '01-01-2020'.
* --end_date: This is the date for which the date will be pulled until. This is default to the current date for obvious reasons.
The primary reason this arg is available (but not limited to) is in-case there is a correction in the data, then you can run the pipeline with 
the correction window specified using start_date and end_date args.

#### Running the Pipeline
To run the pipeline, a docker run command is issued. This command does look slightly different depending on the choice of run approach.
E.g. which option 1a-1d. Regardless of the command used below, verify that you are in the project root directory before issuing it.

__NOTE__: The first  time you run the pipeline, the data acquisition step will pull 100+ MBs of data. Also as this is a relatively 
newer API, there is no specified data update times listed in the documentation/website. It does say the data is updated several
times a day. For most accurate near term forecasts, I would wait until later in the evening to run the pipeline. 

* For 1a (full local) issue the command below. You __must__ replace "<image_name>" with the docker image name you set previously.
```angular2
docker run --mount type=bind,source="$(pwd)"/data,target=/src/data --mount type=bind,source="$(pwd)"/models/global,target=/src/models/global --mount type=bind,source="$(pwd)"/models/country,target=/src/models/country --mount type=bind,source="$(pwd)"/app/static,target=/src/app/static  --env-file=news_api_env <image_name> run_main_pipeline.sh
```
* For 1b (s3 data acq, all other local) issue the command below. You __must__ replace "<image_name>" with the docker image name you set previously.
```angular2
docker run --mount type=bind,source="$(pwd)"/data,target=/src/data --mount type=bind,source="$(pwd)"/models/global,target=/src/models/global --mount type=bind,source="$(pwd)"/models/country,target=/src/models/country --mount type=bind,source="$(pwd)"/app/static,target=/src/app/static --env-file=aws_creds --env-file=news_api_env <image_name> run_main_pipeline.sh
```
* For 1c (1b and use RDS) issue the command below. You __must__ replace "<image_name>" with the docker image name you set previously.
```angular2
docker run --mount type=bind,source="$(pwd)"/models/global,target=/src/models/global --mount type=bind,source="$(pwd)"/models/country,target=/src/models/country --mount type=bind,source="$(pwd)"/app/static,target=/src/app/static --env-file=aws_creds --env-file=rds_config --env-file=news_api_env <image_name> run_main_pipeline.sh
```
* For 1d (Full s3 and use RDS) issue the command below. You __must__ replace "<image_name>" with the docker image name you set previously.
```angular2
docker run --mount type=bind,source="$(pwd)"/app/static,target=/src/app/static --env-file=aws_creds --env-file=rds_config --env-file=news_api_env <image_name> run_main_pipeline.sh
```

#### Verifying a Successful Run:
This section details how to verify a successful run if you chose to run paths 1b or 1c. E.g. if you used s3 only for data acquisition.
Look for the following artifacts in your local directory (if you left the default local pathing in the config.yml)
* Directory: data/
    * If you ran with a local database, you should find that object here
* Directory: models/global
    * ARIMA_global_model: Trained model object
    * config.yml: The yml configuration used for this modeling run config.yml 
* Directory: models/country
    * ARIMA_{}: Models for many countries 
    * config.yml: The yml configuration used for this modeling run 
    * countries.pkl: Pickle file containing list of all countries for which a model was built 
* Directory: app/static:
    * global_cases: html file used by the webapp for ploting COVID-19 cases trends over time
    * global_animation: html file used by the webapp to show time-lapse of COVID-19 spread across the global
    * global_cases_forecast: html file for plot showing recent global case numbers and the near future forecasted numbers

### 3. Run the Web Application
Now that the modeling pipeline is complete and the necessary artifacts are acquired, the webapp can be run.

A configuration change must be made if you choose to create a local database with a database name different than the default.
If this is the case, navigate to the config folder and open up flaskconfig.py in an editor of your choice. Change line 20 to match
the name you gave the local database. An optional change is to adjust the APP_NAME field in line 5 of the flaskconfig.py.

Issue the following command from the project repo root directory to the build the Docker image for the web application. Replace
"<image_name>" with a name of your choosing.
```angular2
docker build -f="DockerfileApp" -t <image_name> .
```
To boot the app, run the command below if you are working with a local database. You _need_ to replace "<image_name" with
the image name you chose in the command above. You can set your own SQLALCHEMY_DATABASE_URI and the flaskconfig.py
file will locate it based on an os.get. If you choose to do this, note that you need to re-run the model exeuction pipeline
and before you do change the SQLALCHEMY_DATABASE_URI in the config.py file to match.

```angular2
docker run -p 5000:5000 <image_name>
```
If you are working with an RDS database then issue:
```angular2
docker run --env-file=rds_config -p 5000:5000 <image_name>
```

To access the application:
* MAC/Linux users go to: http://0.0.0.0:5000/
* Windows users go to: http://localhost:5000/

### 4. Code Unit Testing
If you would like to run the unit testing script, first verify that you have built a docker image with bash as an entrypoint.
The command to run for this is located at the beginning of section 2. Once you have done this, simply the run command below. Note
you must change "<image_name>" to correspond with whatever you have named the docker image.
```
docker run <image_name> unit_tests.sh
```
Note, there are two csv files located in the data/sample directory in the git repo. These need to be present for some of the
unit tests. If you happen to have .gitignore settings that were told to ignore .csvs or if you removed the .csvs, then
you may encounter an error being thrown when running the unit tests.