#!/usr/bin/env bash

# Acquire new data from API
#python3 src/data_acquistion.py --config=config/config.yml --s3

# Create database (RDS or Local)
python3 src/create_database.py 

# data preparation
python3 src/data_preparation.py --config=config/config.yml --s3

#train models
python3 src/train_models.py --config=config/config.yml 