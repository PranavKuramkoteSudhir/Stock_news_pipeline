from src.etl.etl import (
    fetch_stock_news,
    transform_news_data,
    load_to_postgres,
    save_to_csv,
    clear_cache
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_local_pipeline():
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

        # Step 5: Clear cache
        logger.info("Clearing cache...")
        clear_cache()

        logger.info("Local pipeline completed successfully!")
    except Exception as e:
        logger.error(f"Error in local pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    run_local_pipeline()
