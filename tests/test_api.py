import pytest
import os
import sys
from src.fetch.api import NewsAPIClient
from src.fetch.exceptions import APIConnectionError, APIResponseError, APIRateLimitError

class TestNewsAPIClient:
    @pytest.fixture
    def api_client(self):
        """Create API client with environment variables"""
        api_key = os.getenv('API_KEY')
        base_url = "https://api.marketaux.com/v1/news/all"
        
        if not api_key:
            pytest.skip("API_KEY environment variable not set")
            
        return NewsAPIClient(api_key=api_key, base_url=base_url)

    def test_api_connection(self, api_client):
        """Test real API connection"""
        try:
            response = api_client.fetch_news()
            assert isinstance(response, dict)
            assert 'data' in response
            assert isinstance(response['data'], list)
            assert len(response['data']) > 0
            
            # Test first news item structure
            first_item = response['data'][0]
            required_fields = ['title', 'published_at', 'source', 
                             'description', 'keywords', 'url', 'entities']
            
            for field in required_fields:
                assert field in first_item, f"Missing required field: {field}"
                
            # Test entities structure
            assert isinstance(first_item['entities'], list)
            if first_item['entities']:
                assert 'name' in first_item['entities'][0]
                
        except Exception as e:
            pytest.fail(f"API test failed: {str(e)}")

    def test_invalid_api_key(self):
        """Test behavior with invalid API key"""
        client = NewsAPIClient(
            api_key="invalid_key",
            base_url="https://api.marketaux.com/v1/news/all"
        )
        
        with pytest.raises(APIResponseError):
            client.fetch_news()

    def test_custom_parameters(self, api_client):
        """Test API with custom parameters"""
        try:
            response = api_client.fetch_news(
                symbols="AAPL,GOOGL",
                limit=5
            )
            
            assert isinstance(response, dict)
            assert 'data' in response
            assert len(response['data']) <= 5  # Should respect limit
            
        except Exception as e:
            pytest.fail(f"Custom parameters test failed: {str(e)}")

# conftest.py
def pytest_configure(config):
    """Pytest configuration"""
    # Add marker for real API tests
    config.addinivalue_line(
        "markers", "real_api: mark test as requiring real API access"
    )