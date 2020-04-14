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
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)
  * [Workaround for potential Docker problem for Windows.](#workaround-for-potential-docker-problem-for-windows)

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
7.	Initiative1.Epic3.Story2: Holt Winters Model (2pts) -- Sprint 2 (April 11 - April 25)
8.	Initiative1.Epic3.Story3: ARIMA Modeling (4pts) -- Sprint 2 (April 11 - April 25)
8.	Initiative1.Epic3.Story4: Prophet Modeling (2pts) -- Sprint 2 (April 11 - April 25)
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
6.	Initiative2.Epic4.Story6: Update UI Based on Feedback(4pts)

## Directory structure 

```
├── README.md                         <- You are here
├── api
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
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app
### 1. Initialize the database 

#### Create the database with a single song 
To create the database in the location configured in `config.py` with one initial song, run: 

`python run.py create_db --engine_string=<engine_string> --artist=<ARTIST> --title=<TITLE> --album=<ALBUM>`

By default, `python run.py create_db` creates a database at `sqlite:///data/tracks.db` with the initial song *Radar* by Britney spears. 
#### Adding additional songs 
To add an additional song:

`python run.py ingest --engine_string=<engine_string> --artist=<ARTIST> --title=<TITLE> --album=<ALBUM>`

By default, `python run.py ingest` adds *Minor Cause* by Emancipator to the SQLite database located in `sqlite:///data/tracks.db`.

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/tracks.db'

```

The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2020-MSIA423-template-repository/data/tracks.db'
```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

To run the Flask app, run: 

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

## Running the app in Docker 

### 1. Build the image 

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f app/Dockerfile -t pennylane .
```

This command builds the Docker image, with the tag `pennylane`, based on the instructions in `app/Dockerfile` and the files existing in this directory.
 
### 2. Run the container 

To run the app, run from this directory: 

```bash
docker run -p 5000:5000 --name test pennylane
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

This command runs the `pennylane` image as a container named `test` and forwards the port 5000 from container to your laptop so that you can access the flask app exposed through that port. 

If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `app/Dockerfile`)

### 3. Kill the container 

Once finished with the app, you will need to kill the container. To do so: 

```bash
docker kill test 
```

where `test` is the name given in the `docker run` command.

### Workaround for potential Docker problem for Windows.

It is possible that Docker will have a problem with the bash script `app/boot.sh` that is used when running on a Windows machine. Windows can encode the script wrongly so that when it copies over to the Docker image, it is corrupted. If this happens to you, try using the alternate Dockerfile, `app/Dockerfile_windows`, i.e.:

```bash
 docker build -f app/Dockerfile_windows -t pennylane .
```

then run the same `docker run` command: 

```bash
docker run -p 5000:5000 --name test pennylane
```

The new image defines the entry command as `python3 app.py` instead of `./boot.sh`. Building the sample PennyLane image this way will require initializing the database prior to building the image so that it is copied over, rather than created when the container is run. Therefore, please **do the step [Create the database with a single song](#create-the-database-with-a-single-song) above before building the image**.