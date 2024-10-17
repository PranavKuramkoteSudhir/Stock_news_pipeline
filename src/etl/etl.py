import requests
import json
import pandas as pd
from sqlalchemy import create_engine, String, Text, DateTime, Float
from ..utils import API_KEY, API_URL, get_database_url, get_aws_session
from celery import Celery
from datetime import datetime
import redis
import logging
import os
from sqlalchemy.dialects.postgresql import JSON

# Setup Celery
app = Celery('etl_tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# Setup Redis client
redis_client = redis.Redis(host='redis', port=6379, db=1)  # Use a different DB than Celery

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task
def fetch_stock_news():
    params = {
        "symbols": "TSLA,AMZN,MSFT",
        "filter_entities": "true",
        "language": "en",
        "limit": 10,  
        "api_token": API_KEY
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

@app.task
def transform_news_data(news_data):
    transformed_data = []
    for article in news_data['data']:
        # Check if article is already in cache
        if redis_client.get(article['uuid']):
            logger.info(f"Skipping article {article['uuid']} - already processed")
            continue
        
        transformed_article = {
            "uuid": article['uuid'],
            "title": article['title'],
            "description": article['description'],
            "snippet": article['snippet'],
            "url": article['url'],
            "image_url": article['image_url'],
            "language": article['language'],
            "published_at": article['published_at'],
            "source": article['source'],
            "relevance_score": article['relevance_score'],
            "entities": []
        }
        
        for entity in article['entities']:
            transformed_entity = {
                "symbol": entity['symbol'],
                "name": entity['name'],
                "industry": entity['industry'],
                "match_score": entity['match_score'],
                "sentiment_score": entity['sentiment_score']
            }
            transformed_article['entities'].append(transformed_entity)
        
        transformed_data.append(transformed_article)
        
        # Add article UUID to cache with expiration of 24 hours
        redis_client.setex(article['uuid'], 86400, "1")
    
    # Convert to DataFrame
    df = pd.DataFrame(transformed_data)
    df['date'] = pd.to_datetime(df['published_at'])
    
    return df.to_dict('records')

@app.task
def load_to_postgres(data):
    if not data:
        logger.warning("No data to load into Postgres")
        return

    try:
        if not isinstance(data, list):
            raise ValueError(f"Expected list of dictionaries, got {type(data)}")

        # Convert entities to JSON string
        for item in data:
            item['entities'] = json.dumps(item['entities'])

        df = pd.DataFrame(data)
        logger.info(f"DataFrame created with shape: {df.shape}")
        logger.info(f"DataFrame columns: {df.columns.tolist()}")

        engine = create_engine(get_database_url())
        
        # Define the data types for the columns
        dtype = {
            'uuid': String(255),
            'title': Text,
            'description': Text,
            'snippet': Text,
            'url': Text,
            'image_url': Text,
            'language': String(10),
            'published_at': DateTime,
            'source': String(255),
            'relevance_score': Float,
            'entities': JSON,
            'date': DateTime
        }

        df.to_sql('stock_news', engine, if_exists='append', index=False, dtype=dtype)
        logger.info(f"Successfully loaded {len(df)} rows to Postgres")
    except Exception as e:
        logger.error(f"Error loading data to Postgres: {str(e)}")
        raise

@app.task
def save_to_csv(data):
    if not data:
        logger.warning("No data to save to CSV")
        return None
    
    df = pd.DataFrame(data)
    csv_file_path = os.path.join('/tmp', f'stock_news_{datetime.now().strftime("%Y%m%d")}.csv')
    df.to_csv(csv_file_path, index=False)
    logger.info(f"Saved data to CSV: {csv_file_path}")
    return csv_file_path

@app.task
def load_to_s3(data, bucket_name, file_name):
    s3 = get_aws_session().client('s3')
    s3.put_object(Body=json.dumps(data), Bucket=bucket_name, Key=file_name)

@app.task
def trigger_glue_job(job_name):
    glue = get_aws_session().client('glue')
    response = glue.start_job_run(JobName=job_name)
    return response['JobRunId']

@app.task
def check_glue_job_status(job_name, run_id):
    glue = get_aws_session().client('glue')
    response = glue.get_job_run(JobName=job_name, RunId=run_id)
    return response['JobRun']['JobRunState']

@app.task
def clear_cache():
    redis_client.flushdb()
    logger.info("Cache cleared")

if __name__ == '__main__':
    print(fetch_stock_news())