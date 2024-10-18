from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.etl.etl import fetch_stock_news, transform_news_data, load_to_postgres, clear_cache
import pandas as pd
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom JSON encoder to handle Pandas Timestamp
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return super().default(obj)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'local_operations',
    default_args=default_args,
    description='A DAG to perform local ETL operations',
    schedule_interval=timedelta(days=1),
    catchup=False,
    max_active_runs=1,
)

def validate_and_transform_data(**kwargs):
    ti = kwargs['ti']
    news_data = ti.xcom_pull(task_ids='fetch_data')
    
    logger.info(f"Received data from fetch_data task: {json.dumps(news_data)[:50]}...")  # Log first 500 characters
    
    if not news_data:
        logger.warning("No data received from fetch_data task")
        return None
    
    if isinstance(news_data, str):
        try:
            news_data = json.loads(news_data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON data received from fetch_data task")
            return None
    
    if not isinstance(news_data, dict) or 'data' not in news_data:
        logger.error(f"Unexpected data format received from fetch_data task: {type(news_data)}")
        return None
    
    transformed_data = transform_news_data(news_data)
    
    # Use custom JSON encoder to handle Pandas Timestamp objects
    logger.info(f"Transformed data: {json.dumps(transformed_data[:2], cls=CustomJSONEncoder)}...")  # Log first 2 items
    
    return transformed_data

def save_to_csv(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform_data')
    if not data:
        logger.warning("No data to save to CSV")
        return None
    
    df = pd.DataFrame(data)
    csv_file_path = os.path.join('/tmp', f'stock_news_{datetime.now().strftime("%Y%m%d")}.csv')
    df.to_csv(csv_file_path, index=False)
    logger.info(f"Saved data to CSV: {csv_file_path}")
    return csv_file_path

fetch_data_task = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_stock_news,
    dag=dag,
)

transform_data_task = PythonOperator(
    task_id='transform_data',
    python_callable=validate_and_transform_data,
    provide_context=True,
    dag=dag,
)

load_to_postgres_task = PythonOperator(
    task_id='load_to_postgres',
    python_callable=load_to_postgres,
    provide_context=True,
    dag=dag,
)

save_to_csv_task = PythonOperator(
    task_id='save_to_csv',
    python_callable=save_to_csv,
    provide_context=True,
    dag=dag,
)

clear_cache_task = PythonOperator(
    task_id='clear_cache',
    python_callable=clear_cache,
    dag=dag,
)

# Define task dependencies
fetch_data_task >> transform_data_task >> [load_to_postgres_task, save_to_csv_task] >> clear_cache_task