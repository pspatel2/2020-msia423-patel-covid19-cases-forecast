#!/usr/bin/env bash

#get forecasts
python3 src/generate_forecasts.py --config=config/config.yml

#get forecast plots
python3 src/generate_forecast_plots.py --config=config/config.yml

#get news headlines
python3 src/get_news.py --config=config/config.yml