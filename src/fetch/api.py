import logging
import requests
from typing import List, Dict, Any
from datetime import datetime
from exceptions import APIConnectionError, APIResponseError, APIRateLimitError

logger = logging.getLogger(__name__)

class NewsAPIClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
    def fetch_news(self, symbols: str = "TSLA,AMZN,MSFT", limit: int = 10) -> Dict[str, Any]:
        """
        Fetch news articles from the MarketAux API
        Returns API response containing news items
        """
        try:
            params = {
                "symbols": symbols,
                "filter_entities": "true",
                "language": "en",
                "limit": limit,
                "api_token": self.api_key
            }
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=10
            )

            if response.status_code == 429:
                raise APIRateLimitError("API rate limit exceeded")
                
            response.raise_for_status()
            
            data = response.json()
            
            # MarketAux specific validation
            if 'data' not in data:
                raise APIResponseError("Invalid API response format - 'data' field missing")
                
            news_items = data['data']
            logger.info(f"Successfully fetched {len(news_items)} news items")
            
            return data
            
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise APIConnectionError(f"Failed to connect to API: {str(e)}")
        
        except requests.Timeout as e:
            logger.error(f"Request timeout: {str(e)}")
            raise APIConnectionError(f"API request timed out: {str(e)}")
        
        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIResponseError(f"API request failed: {str(e)}")
