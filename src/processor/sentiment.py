import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SentimentScore:
    compound: float
    positive: float
    negative: float
    neutral: float
    
class SentimentAnalyzer:
    def __init__(self):
        """Initialize the VADER sentiment analyzer"""
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            logger.info("Downloading VADER lexicon...")
            nltk.download('vader_lexicon')
        
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text: str) -> SentimentScore:
        """
        Analyze the sentiment of a given text
        
        Args:
            text: The text to analyze
            
        Returns:
            SentimentScore object containing sentiment scores
        """
        if not text or not isinstance(text, str):
            raise ValueError("Invalid input text")
            
        scores = self.analyzer.polarity_scores(text)
        return SentimentScore(
            compound=scores['compound'],
            positive=scores['pos'],
            negative=scores['neg'],
            neutral=scores['neu']
        )
    
    def analyze_news_item(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment for a news item
        
        Args:
            news_item: Dictionary containing news item data
            
        Returns:
            News item enriched with sentiment scores
        """
        try:
            # Combine title and description for analysis
            text = f"{news_item.get('title', '')} {news_item.get('description', '')}"
            sentiment = self.analyze_text(text)
            
            # Add sentiment scores to news item
            news_item['sentiment'] = {
                'compound': sentiment.compound,
                'positive': sentiment.positive,
                'negative': sentiment.negative,
                'neutral': sentiment.neutral
            }
            
            # Add sentiment label based on compound score
            if sentiment.compound >= 0.05:
                news_item['sentiment_label'] = 'positive'
            elif sentiment.compound <= -0.05:
                news_item['sentiment_label'] = 'negative'
            else:
                news_item['sentiment_label'] = 'neutral'
            
            return news_item
            
        except Exception as e:
            logger.error(f"Error analyzing news item: {str(e)}")
            raise

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for sentiment analysis
    
    Args:
        event: Lambda event containing news items
        context: Lambda context
        
    Returns:
        Dictionary containing processed news items with sentiment scores
    """
    try:
        logger.info("Processing news items for sentiment analysis")
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        
        # Get news items from event
        news_items = json.loads(event['Records'][0]['body'])
        
        if not isinstance(news_items, list):
            raise ValueError("Invalid input format - expected list of news items")
        
        # Process each news item
        processed_items = []
        for item in news_items:
            try:
                processed_item = analyzer.analyze_news_item(item)
                processed_items.append(processed_item)
            except Exception as e:
                logger.error(f"Error processing item: {str(e)}")
                # Continue processing other items
                continue
        
        logger.info(f"Successfully processed {len(processed_items)} news items")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Processed {len(processed_items)} news items',
                'timestamp': datetime.utcnow().isoformat(),
                'items': processed_items
            })
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }