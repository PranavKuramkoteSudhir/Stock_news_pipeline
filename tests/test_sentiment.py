import pytest
import json
from src.processor.sentiment import SentimentAnalyzer, handler

@pytest.fixture
def analyzer():
    return SentimentAnalyzer()

def test_analyze_text(analyzer):
    # Test positive sentiment
    text = "This is excellent news for the company!"
    result = analyzer.analyze_text(text)
    assert result.compound > 0
    assert result.positive > 0
    
    # Test negative sentiment
    text = "The company reported devastating losses"
    result = analyzer.analyze_text(text)
    assert result.compound < 0
    assert result.negative > 0
    
    # Test neutral sentiment
    text = "The company released their quarterly report"
    result = analyzer.analyze_text(text)
    assert -0.05 <= result.compound <= 0.05

def test_analyze_news_item(analyzer):
    news_item = {
        "title": "Tech Company Reports Strong Growth",
        "description": "Quarterly earnings exceeded expectations.",
        "published_at": "2024-03-15T10:00:00Z"
    }
    
    result = analyzer.analyze_news_item(news_item)
    
    assert 'sentiment' in result
    assert 'sentiment_label' in result
    assert all(k in result['sentiment'] for k in ['compound', 'positive', 'negative', 'neutral'])

def test_handler():
    # Test event with single news item
    test_event = {
        "Records": [{
            "body": json.dumps([{
                "title": "Company Stock Surges 20%",
                "description": "Investors celebrate positive earnings report",
                "published_at": "2024-03-15T10:00:00Z"
            }])
        }]
    }
    
    result = handler(test_event, None)
    
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert 'items' in body
    assert len(body['items']) == 1
    assert 'sentiment' in body['items'][0]

def test_handler_invalid_input():
    # Test with invalid event structure
    test_event = {
        "Records": [{
            "body": "invalid json"
        }]
    }
    
    result = handler(test_event, None)
    assert result['statusCode'] == 500