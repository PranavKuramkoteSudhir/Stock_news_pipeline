import json
import sys
import os
from datetime import datetime
from typing import Dict, Any
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from api import NewsAPIClient
from exceptions import FetcherException, APIConnectionError, APIResponseError, APIRateLimitError

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fetcher')

def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Simplified Lambda handler for fetching stock news data
    """
    try:
        # Get API credentials from environment
        api_key = os.getenv('API_KEY')
        base_url = "https://api.marketaux.com/v1/news/all"
        
        if not api_key:
            raise ValueError("API_KEY environment variable not set")
        
        # Initialize API client
        client = NewsAPIClient(
            api_key=api_key,
            base_url=base_url
        )
        
        # Get symbols from event or use defaults
        symbols = event.get('symbols', "TSLA,AMZN,MSFT")
        
        # Fetch news data
        logger.info(f"Fetching news for symbols: {symbols}")
        response = client.fetch_news(symbols=symbols)
        
        if not response or 'data' not in response:
            raise APIResponseError("Invalid response format from API")
            
        news_items = response['data']
        logger.info(f"Successfully fetched {len(news_items)} news items")
        
        # return the processed items
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully fetched {len(news_items)} news items',
                'timestamp': datetime.utcnow().isoformat(),
                'news_items': news_items  # Including the actual items for testing
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

if __name__ == '__main__':
    test_event = {
        'symbols': 'AAPL,GOOGL,MSFT'
    }
    result = handler(test_event)
    print(json.dumps(result, indent=2))