from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.pipeline.local_pipeline import run_local_pipeline

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

run_local_pipeline_task = PythonOperator(
    task_id='run_local_pipeline',
    python_callable=run_local_pipeline,
    dag=dag,
)

# Define task dependencies
run_local_pipeline_task