from src.etl.etl import (
    fetch_stock_news,
    transform_news_data,
    load_to_postgres,
    save_to_csv,
    upload_csv_files_to_s3,
    trigger_glue_job,
    check_glue_job_status,
    clear_cache
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_aws_pipeline(bucket_name, glue_job_name):
    try:
        # Step 1: Fetch data
        logger.info("Fetching stock news data...")
        news_data = fetch_stock_news()

        # Step 2: Transform data
        logger.info("Transforming news data...")
        transformed_data = transform_news_data(news_data)

        # Step 3: Load data to Postgres
        logger.info("Loading data to Postgres...")
        load_to_postgres(transformed_data)

        # Step 4: Save data to CSV
        logger.info("Saving data to CSV...")
        csv_file_path = save_to_csv(transformed_data)
        logger.info(f"Data saved to CSV: {csv_file_path}")

        # Step 5: Upload CSV files to S3
        logger.info("Uploading CSV files to S3...")
        upload_csv_files_to_s3(bucket_name)

        # Step 6: Trigger Glue job
        logger.info("Triggering Glue job...")
        job_run_id = trigger_glue_job(glue_job_name)
        logger.info(f"Glue job triggered: {job_run_id}")

        # Step 7: Check Glue job status
        job_status = check_glue_job_status(glue_job_name, job_run_id)
        logger.info(f"Glue job status: {job_status}")

        # Step 8: Clear cache
        logger.info("Clearing cache...")
        clear_cache()

        logger.info("AWS pipeline completed successfully!")
    except Exception as e:
        logger.error(f"Error in AWS pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    run_aws_pipeline('your-s3-bucket-name', 'your-glue-job-name')