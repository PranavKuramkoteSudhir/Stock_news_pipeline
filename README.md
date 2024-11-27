# Stock News Pipeline

## Overview
This project is a data pipeline that fetches and processes stock market news using the MarketAux API. It's designed to be deployed on AWS, featuring modular components and scalable architecture.

## Project Structure

stock_news_pipeline/
├── src/
│   ├── fetch/
│   │   ├── api.py         # API client for MarketAux
│   │   └── exceptions.py  # Custom exceptions
│   └── database/          # Database interactions
├── tests/
│   └── test_api.py        # API tests
├── logs/                  # Log files
└── requirements.txt       # Project dependencies

## Coming soon
AWS Lambda deployment
Data storage in AWS RDS/DynamoDB
Real-time processing with AWS SQS
Data visualization dashboard
Automated deployment pipeline