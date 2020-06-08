#!/usr/bin/env bash

#genrate trend plots to display on webapp
python3 src/generate_trend_plots.py --config=config/config.yml

#get forecasts
python3 src/generate_forecasts.py --config=config/config.yml

#get forecast plots
python3 src/generate_forecast_plots.py --config=config/config.yml

#get news headlines
python3 src/get_news.py --config=config/config.yml