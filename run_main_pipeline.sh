#!/usr/bin/env bash

# Acquire data from URL
python3 src/data_acquistion.py --config=config/config.yml --s3 --start_date='01-01-2020'

# Create database
python3 src/create_database.py 

# data preparation
python3 src/data_preparation.py --config=config/config.yml --s3

#genrate trend plots
python3 src/generate_trend_plots.py --config=config/config.yml

#train models
python3 src/train_models.py --config=config/config.yml

#get forecasts
python3 src/generate_forecasts.py --config=config/config.yml

#get forecast plots
python3 src/generate_forecast_plots.py --config=config/config.yml

#get news headlines
python3 src/get_news.py --config=config/config.yml

