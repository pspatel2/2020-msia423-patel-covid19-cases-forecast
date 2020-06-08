import yaml
import json
import logging.config
import data_acquistion as data_acq
import data_preparation as data_prep
import generate_trend_plots as gtp
import generate_forecast_plots as gfp
import generate_forecasts as gf
import train_models as tm
import get_news as gn
import pytest
import pandas as pd
import plotly
import _plotly_utils
import statsmodels
import numpy
import os
from statsmodels.tsa.arima_model import ARIMAResults
from datetime import datetime


logging.config.fileConfig(fname="local.conf")
logger = logging.getLogger(__name__)

############ TESTS FOR data_acquisition.py functions ############
# ALL BUT ONE FUNCTION IN THIS SCRIPT INTERACT WITH AN API or s3.
def test_write_to_local():
    """
    Test the write_to_local function in the data_acquisition.py script
    """
    #happy path
    # create some data to write out using the function
    test_raw_data = [ {'Country': 'Armenia','CountryCode': 'AM','Province': '','City': '','CityCode': '','Lat': '40.07',
                       'Lon': '45.04','Confirmed': 1013,'Deaths': 13,'Recovered': 197,'Active': 803,
                       'Date': '2020-04-12T00:00:00Z'}]
    fname = 'raw_test_data.json'
    data_acq.write_data_to_local(test_raw_data,fname)

    #read the written data back in from the same path and verify it is the same as the created data above
    with open(fname) as f:
        data_from_file = json.load(f)
    assert(test_raw_data==data_from_file)
    logger.info("data_acquistion function write_to_local happy path unit test is successful")

    #unhappy path -- provide data of improper format. This triggers an except clause that calls sys.exit(), assert this
    dict1 = {('addresss', 'street'): 'Brigade road', }
    with pytest.raises(SystemExit):
        data_acq.write_data_to_local(dict1,"unhappy_test.json")
    logger.info("data_acquistion function write_to_local unhappy path unit test is successful")

############ TESTS FOR data_preparation.py functions ############
def test_get_local_data():
    """
    Test the get_local_data function in the data_preparation.py function
    """
    #happy path
    # generate data like before
    test_raw_data = [ {'Country': 'Armenia','CountryCode': 'AM','Province': '','City': '','CityCode': '','Lat': '40.07',
                       'Lon': '45.04','Confirmed': 1013,'Deaths': 13,'Recovered': 197,'Active': 803,
                       'Date': '2020-04-12T00:00:00Z'}]
    fname = 'raw_test_data.json'
    #write it out
    data_acq.write_data_to_local(test_raw_data,fname)
    # read the data using the function being tested
    data = data_prep.get_local_data(fname)

    # create the expected output
    test = pd.DataFrame(test_raw_data)
    test['Active'] = test['Confirmed'] - test['Deaths'] - test['Recovered']
    test['Date'] = pd.to_datetime(test['Date'])
    # assert the two are equal
    assert(data.equals(test))
    logger.info("data_preparation function get_local_data happy path unit test is successful")

    #unhappy path -- give it a path to a non-existent file. Will trigger and exception that causes a sys.exit(), assert
    fake_path = "this/is/afake/path.json"
    with pytest.raises(SystemExit):
        data_prep.get_local_data(fake_path)
    logger.info("data_preparation function get_local_data unhappy path unit test is successful")

def test_get_country_daily():
    """
    Test the get_country_daily function in the data_preparation.py function
    """
    #happy path
    # generate data like before
    test_raw_data = [ {'Country': 'Armenia','CountryCode': 'AM','Province': '','City': '','CityCode': '','Lat': '40.07',
                       'Lon': '45.04','Confirmed': 1013,'Deaths': 13,'Recovered': 197,'Active': 803,
                       'Date': '2020-04-12T00:00:00Z'},{'Country': 'China','CountryCode': 'CN','Province':
                        'Inner Mongolia','City': '','CityCode': '','Lat': '44.09','Lon': '113.94','Confirmed': 190,
                        'Deaths': 1,'Recovered': 83,'Active': 106,'Date': '2020-04-13T00:00:00Z'}]

    fname = 'raw_test_data.json'

    # run the function steps prior to this one
    data_acq.write_data_to_local(test_raw_data, fname)
    data = data_prep.get_local_data(fname)
    #call function being tested
    country_df = data_prep.get_country_daily(data)

    #generate what the output should be
    test = pd.DataFrame(test_raw_data)
    test['Active'] = test['Confirmed'] - test['Deaths'] - test['Recovered']
    test['Date'] = pd.to_datetime(test['Date'])
    china_df = test.loc[test['Country'] == 'China']
    china_df = china_df.drop(columns=["Province", "City", "CityCode", "Lat", "Lon"])
    china_df = china_df.groupby(['Country', 'Date']).sum().reset_index()
    rest_of_the_world_df = test.loc[test['Province'] == '']
    rest_of_the_world_df = rest_of_the_world_df.drop(columns=["Province", "City", "CityCode", "Lat", "Lon"])
    rest_of_the_world_df = rest_of_the_world_df.groupby(['Country', 'Date']).sum().reset_index()
    test_country_df = pd.concat([rest_of_the_world_df, china_df])

    #assert expected output equals function output
    assert(country_df.equals(test_country_df))
    logger.info("data_preparation function get_country_daily happy path unit test is successful")

    #unhappy path -- provide input of wrong type -- hits except block which calls sys.exit(), assert this
    with pytest.raises(SystemExit):
        data_prep.get_country_daily(test_raw_data)
    logger.info("data_preparation function get_country_daily unhappy path unit test is successful")

def test_get_global_daily():
    """
    Test the get_global_daily function in the data_preparation.py function
    """
    # happy path: generate data, call the function being tested, compare it to expected output
    test_raw_data = [ {'Country': 'Armenia','CountryCode': 'AM','Province': '','City': '','CityCode': '','Lat': '40.07',
                       'Lon': '45.04','Confirmed': 1013,'Deaths': 13,'Recovered': 197,'Active': 803,
                       'Date': '2020-04-12T00:00:00Z'}, {'Country': 'Belgium','CountryCode': 'BE','Province': '','City': '',
                        'CityCode': '','Lat': '50.5','Lon': '4.47','Confirmed': 29647,'Deaths': 3600,'Recovered': 6463,
                                                         'Active': 19584,'Date': '2020-04-12T00:00:00Z'}]

    fname = 'raw_test_data.json'
    data_acq.write_data_to_local(test_raw_data, fname)
    data = data_prep.get_local_data(fname)
    # call the function in question
    global_df = data_prep.get_global_daily(data)

    test = pd.DataFrame(test_raw_data)
    test['Active'] = test['Confirmed'] - test['Deaths'] - test['Recovered']
    test['Date'] = pd.to_datetime(test['Date'])
    test_global_df = test.groupby('Date').sum()[["Confirmed", "Recovered", "Active", "Deaths"]].reset_index()
    assert(global_df.equals(test_global_df))
    logger.info("data_preparation function get_global_daily happy path unit test is successful")

    #unhappy path: feed in json instead of dataframe, should trigger exception which calls sys.exit(), assert.
    with pytest.raises(SystemExit):
        data_prep.get_global_daily(test_raw_data)
    logger.info("data_preparation function get_global_daily unhappy path unit test is successful")

############ TESTS FOR generate_trend_plots.py function ############
# ONLY 1 FUNCTION DOES NOT INTERACT WITH s3, API or a database
def test_save_html_to_local():
    """
    Test the save_html_to_local function in the generate_trend_plots.py function
    """
    #happy path: generate some random html string and save it out. Assert that reading it back in equals the original
    random_html =  "div { background-color: green; : 0.3;}"
    fname = 'rand'
    gtp.save_html_to_local(random_html,fname,'src/')
    f = open('src/rand.html', "r")
    assert f.read() == random_html
    logger.info("generate_trend_plots function save_html_to_local happy path unit test is successful")

    #unhappy path: feed function an argument that is of the wrong type, should raise TypeError
    with pytest.raises(TypeError) as execinfo:
        gtp.save_html_to_local(random_html,fname,22)
    assert str(execinfo.value)=="expected str, bytes or os.PathLike object, not int"
    logger.info("generate_trend_plots function save_html_to_local unhappy path unit test is successful")


############ TESTS FOR train_models.py function ############
def test_reduce_and_reshape_data():
    """
    Test the reduce_and_reshape_data function in the train_models.py function
    """
    #happy path: make some fake data, run the function, compare it to the expected output
    test_raw_data = [ {'Country': 'Armenia','CountryCode': 'AM','Province': '','City': '','CityCode': '','Lat': '40.07',
                       'Lon': '45.04','Confirmed': 1013,'Deaths': 13,'Recovered': 197,'Active': 803,
                       'Date': '2020-04-12T00:00:00Z'}]

    fname = 'raw_test_data.json'
    data_acq.write_data_to_local(test_raw_data, fname)
    data = data_prep.get_local_data(fname)
    country_df = data_prep.get_country_daily(data)
    test_df = country_df[['Country', 'Date', 'Confirmed']]
    out_df = tm.reduce_and_reshape_data('country',country_df)
    assert (out_df.equals(test_df))
    logger.info("train_models function reduce_and_reshape_data happy path unit test is successful")

    #unhappy path: feed in empty dataframe to the function, should raise KeyError.
    country_df =pd.DataFrame()
    with pytest.raises(KeyError):
        tm.reduce_and_reshape_data('country', country_df)
    logger.info("train_models function reduce_and_reshape_data unhappy path unit test is successful")

def test_train_global_model():
    """
    Test the train_global_model function in the train_models.py function
    """
    #happy path: read in some sample data from the repo, run the function and assert the returned model is of the correct type
    global_df = pd.read_csv('sample_global_daily_data.csv')
    global_df_series = tm.reduce_and_reshape_data('global', global_df)
    model_params = {'p':1,'d':1,'q':0}
    model = tm.train_global_model(global_df_series,model_params,{'solver':'lbfgs'})
    assert type(model)==statsmodels.tsa.arima_model.ARIMAResultsWrapper
    logger.info("train_models function train_global_model happy path unit test is successful")

    #unhappy path: give a wrong type for an arg which should trip a ValueError
    with pytest.raises(ValueError):
        tm.train_global_model(2, model_params,{'solver':'lbfgs'})
    logger.info("train_models function train_global_model unhappy path unit test is successful")

def test_forward_chaining_eval_global_model():
    """
    Test the forward_chaining_eval_global_model function in the train_models.py function
    """
    #happy path: read in some sample data from the repo, run the function and assert the return value (MAPE) is of float type
    global_df = pd.read_csv('sample_global_daily_data.csv')
    global_df_series = tm.reduce_and_reshape_data('global', global_df)
    model_params = {'p':1,'d':1,'q':0}
    optional_fit_args = {'solver':'lbfgs'}
    nbr_days_forecast = 7
    val = tm.forward_chaining_eval_global_model(global_df_series, model_params, optional_fit_args, nbr_days_forecast)
    assert type(val)==numpy.float64
    logger.info("train_models function forward_chaining_eval_global_model happy path unit test is successful")
    #unhappy path: give a wrong type for an arg which should trip a TypeError
    with pytest.raises(TypeError):
        tm.forward_chaining_eval_global_model(2, model_params, optional_fit_args, nbr_days_forecast)
    logger.info("train_models function forward_chaining_eval_global_model unhappy path unit test is successful")

def test_save_global_model_local():
    """
    Test the save_global_model_local function in the train_models.py function
    """
    #happy path: read in some sample data from the repo, run the function and assert the returned model is of the correct type
    global_df = pd.read_csv('sample_global_daily_data.csv')
    global_df_series = tm.reduce_and_reshape_data('global', global_df)
    model_params = {'p':1,'d':1,'q':0}
    model = tm.train_global_model(global_df_series,model_params,{'solver':'lbfgs'})
    fake_config = [{'Empty': ['yaml']}]
    tm.save_global_model_local(model,fake_config,'','testmodel')
    model_read = ARIMAResults.load('testmodel')
    logger.info(model_read)
    assert type(model_read)==statsmodels.tsa.arima_model.ARIMAResultsWrapper
    logger.info("train_models function test_save_global_model_local happy path unit test is successful")
    #unhappy path: give a wrong type for an arg which should trip a TypeError
    with pytest.raises(TypeError):
        tm.save_global_model_local(model,fake_config,1234)
    logger.info("train_models function test_save_global_model_local unhappy path unit test is successful")

def test_train_country_models():
    """
    Test the train_country_models function in the train_models.py function
    """
    #happy path: read in sample data from repo, run the function, assert length of output (dataframe) is 1 as there
    # is only one country in the sample data
    country_df = pd.read_csv('sample_country_daily_data.csv')
    model_params = {'p': 1, 'd': 1, 'q': 0}
    models_df = tm.train_country_models(country_df, model_params, {'solver': 'lbfgs'})
    assert(len(models_df)==1)
    logger.info("train_models function train_country_models happy path unit test is successful")

    #unhappy path: feed in the wrong (global instead of country) data to the function; should raise an AttributeError
    global_df = pd.read_csv('sample_global_daily_data.csv')
    model_params = {'p': 1, 'd': 1, 'q': 0}
    with pytest.raises(AttributeError):
        models_df = tm.train_country_models(global_df, model_params, {'solver': 'lbfgs'})
    logger.info("train_models function train_country_models unhappy path unit test is successful")
############ TESTS FOR generate_forecasts.py function ############
def test_get_model():
    """
    Test the get_model function in the generate_forecasts.py function
    """
    #only test local path (not s3)
    #happy path: read sample data, train model, save it, run get_model and assert the object it gets is of the right type
    global_df = pd.read_csv('sample_global_daily_data.csv')
    global_df_series = tm.reduce_and_reshape_data('global', global_df)
    model_params = {'p': 1, 'd': 1, 'q': 0}
    model = tm.train_global_model(global_df_series, model_params, {'solver': 'lbfgs'})
    fake_config = [{'Empty': ['yaml']}]
    tm.save_global_model_local(model, fake_config, '', 'testmodel')
    model_read = gf.get_model(False,'','testmodel')
    assert type(model_read)==statsmodels.tsa.arima_model.ARIMAResultsWrapper
    logger.info("generate_forecasts function get_model happy path unit test is successful")

    #unhappy path: provide wrong filename, should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        model_read = gf.get_model(False,'','nomodelhere')
    logger.info("generate_forecasts function get_model unhappy path unit test is successful")

def test_get_global_forecast():
    """
    Test the get_global_forecast function in the generate_forecasts.py function
    """
    # happy path: read sample data, train a model, call the forecast function and assert the output is the same length
    # as the number of days to forecast arg input
    global_df = pd.read_csv('sample_global_daily_data.csv')
    global_df_series = tm.reduce_and_reshape_data('global', global_df)
    model_params = {'p': 1, 'd': 1, 'q': 0}
    model = tm.train_global_model(global_df_series, model_params, {'solver': 'lbfgs'})
    days = 7
    forecast_df = gf.get_global_forecast(model,days)
    assert len(forecast_df==days)
    logger.info("generate_forecasts function get_global_forecast happy path unit test is successful")

    #unhappy path: provide string instead of numeric as number of days to forecast, should raise TypeError
    with pytest.raises(TypeError):
        forecast_df = gf.get_global_forecast(model,'ten')
    logger.info("generate_forecasts function get_global_forecast unhappy path unit test is successful")

def test_get_country_forecast():
    """
    Test the get_country_forecast function in the generate_forecasts.py function
    """
    # happy path: read sample data, train a model, call the forecast function and assert the output is the same length
    # as the number of days to forecast arg input
    country_df = pd.read_csv('sample_country_daily_data.csv')
    country = country_df.Country.unique()[0]
    model_params = {'p': 1, 'd': 1, 'q': 0}
    models_df = tm.train_country_models(country_df, model_params, {'solver': 'lbfgs'})
    models = models_df['Model'].values
    models[0].save("ARIMA_Spain")
    days =7
    forecast_df = gf.get_country_forecast(False,country,'',days)
    assert len(forecast_df==days)
    logger.info("generate_forecasts function get_country_forecast happy path unit test is successful")

    #unhappy path: provide string instead of numeric as number of days to forecast, should raise TypeError
    with pytest.raises(TypeError):
        forecast_df = gf.get_country_forecast(False,country,'','ten')
    logger.info("generate_forecasts function get_country_forecast unhappy path unit test is successful")

############ TESTS FOR generate_forecast_plots.py function ############
def test_generate_forecast_plot():
    """
    Test the generate_forecast_plot function in the generate_forecast_plots.py function
    """
    #happy path: create some fake data, feed it into the function, assert the figure type generated is as expected
    forecast_df = pd.DataFrame({'Date': pd.date_range(start="2020-01-01",end="2020-01-05"), 'confirmed_cases_forecast': [2,3,4,5,6]})
    cases_df_plot = pd.DataFrame({'Date': pd.date_range(start="2020-01-01",end="2020-01-05"), 'Confirmed': [0,0,1,2,2]})
    # no way to test if the figure generated is the correct one, just assert its type and thats good enough
    fig1 = gfp.generate_forecast_plot(forecast_df,cases_df_plot)
    assert type(fig1) == plotly.graph_objs._figure.Figure
    logger.info("generate_forecast_plots function generate_forecast_plot happy path unit test is successful")

    #unhappy path: feed in empty dataframe which should raise a KeyError
    cases_df_plot = pd.DataFrame()
    with pytest.raises(KeyError):
        gfp.generate_forecast_plot(forecast_df,cases_df_plot)
    logger.info("generate_forecast_plots function generate_forecast_plot unhappy path unit test is successful")

def test_get_html_and_save():
    """
    Test the get_html_and_save function in the generate_forecast_plots.py function
    """
    #happy path:  create some fake data, feed it into the function, read the html in and verify its length is the same as
    # is expected
    forecast_df = pd.DataFrame({'Date': pd.date_range(start="2020-01-01",end="2020-01-05"), 'confirmed_cases_forecast': [2,3,4,5,6]})
    cases_df_plot = pd.DataFrame({'Date': pd.date_range(start="2020-01-01",end="2020-01-05"), 'Confirmed': [0,0,1,2,2]})
    # no way to test if the figure generated is the correct one, just assert its type and thats good enough
    fig1 = gfp.generate_forecast_plot(forecast_df,cases_df_plot)

    convToHtml = plotly.offline.plot(fig1, include_plotlyjs=False, output_type='div')
    htmlout = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>' + "\n" + convToHtml

    gfp.get_html_and_save(fig1,False,'figtest','src')
    with open("src/figtest.html", 'r') as f:
        read_html = f.read()
        f.close()
    #Div ID is different b/c rng so check length instead
    assert len(read_html) == len(htmlout)
    logger.info("get_html_and_save function get_html_and_save happy path unit test is successful")

    #unhappy path: provide a numeric instead of the plotly figure which should raise a PlotlyError
    with pytest.raises(_plotly_utils.exceptions.PlotlyError):
        gfp.get_html_and_save(22,False,'figtest','src')
    logger.info("generate_trend_plots function get_html_and_save unhappy path unit test is successful")

############ TESTS FOR get_news.py functions ############
# ALL BUT ONE FUNCTION IN THIS SCRIPT INTERACT WITH AN API or s3.
def test_write_data_to_local():
    """
    Test the write_data_to_local function in the get_news.py script
    """

    #happy path: generate some data, call the function to write it out. Read it back in and assert it is the same as the
    # original data
    test_raw_data = [{'source': {'id': 'reuters', 'name': 'Reuters'},
      'author': 'John Whitesides',
      'title': 'Confusion, long lines at some poll sites as eight U.S. states vote during coronavirus pandemic',
      'description': 'Confusion, complaints of missing mail-in ballots and long lines at some polling centers marred primary elections on Tuesday in eight states and the District of Columbia, the biggest test yet of voting during the coronavirus outbreak.',
      'url': 'http://feeds.reuters.com/~r/reuters/topNews/~3/QbkrfPfEuh8/confusion-long-lines-at-some-poll-sites-as-eight-u-s-states-vote-during-coronavirus-pandemic-idUSKBN2391B5',
      'urlToImage': 'https://s4.reutersmedia.net/resources/r/?m=02&d=20200603&t=2&i=1520862281&w=1200&r=LYNXMPEG5128W',
      'publishedAt': '2020-06-03T21:25:52Z',
      'content': 'WASHINGTON (Reuters) - Confusion, complaints of missing mail-in ballots and long lines at some polling centers marred primary elections on Tuesday in eight states and the District of Columbia, the bi… [+4224 chars]'}]
    fname = 'raw_test_data.json'
    gn.write_data_to_local(test_raw_data,fname)
    with open(fname) as f:
        data_from_file = json.load(f)
    assert(test_raw_data==data_from_file)
    logger.info("get_news function write_data_to_local happy path unit test is successful")

    #unhappy path: hard to test because there is a catch exception as this is not a critical piece of the primary
    #objective of the app so it can fail and the pipeline is unimpacted. Just some loss on the webpage.
    # even running with data of poor form an exception should be caught in except block and move on
    dict1 = {('addresss', 'street'): 'Brigade road', }
    gn.write_data_to_local(dict1,"unhappy_test.json")
    logger.info("get_news function write_data_to_local unhappy path unit test is successful")

def run_unit_tests():
    """
    Wrapper function that executes all unit tests when called
    """

    # run unit tests for data_acquistion.py (other functions interact with API or s3)
    test_write_to_local()
    # run unit tests for data_preparation.py (other functions interact with s3 or database)
    test_get_local_data()
    test_get_country_daily()
    test_get_global_daily()
    # run unit tests for generate_trend_plots.py (other functions interact with s3 or database)
    test_save_html_to_local()
    # run unit tests for train_models.py (other functions interact with s3)
    test_reduce_and_reshape_data()
    test_train_global_model()
    test_train_country_models()
    test_forward_chaining_eval_global_model()
    test_save_global_model_local()
    # run unit tests for generate_forecasts.py (other functions interact with s3)
    test_get_model()
    test_get_global_forecast()
    test_get_country_forecast()
    test_write_data_to_local()
    # run unit tests for generate_forecast_plots.py (other functions interact with s3)
    test_generate_forecast_plot()
    test_get_html_and_save()
    # run unit tests for get_news.py
    test_write_data_to_local()


if __name__ == '__main__':
    run_unit_tests()
    logger.info("All tests were run successfully.")