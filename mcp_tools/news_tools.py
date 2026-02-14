"""
MCP-2: News Tools
-----------------
Tools for searching news articles and analyzing sentiment.

Functions:
- search_news(company_name, date_range): Search for news articles
- analyze_sentiment(article_text): Analyze sentiment (positive/negative/neutral)

Data Sources: NewsAPI (free tier), RSS feeds, GDELT
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_news(
    company_name: str, 
    date_range: str = "last_30_days",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search for news articles about a company.
    
    This function searches for news articles using NewsAPI (free tier).
    It returns articles with headlines, descriptions, URLs, and publication dates.
    
    Args:
        company_name (str): Company name to search for
        date_range (str): Time period to search. Options:
                         - "last_7_days"
                         - "last_30_days" (default)
                         - "last_90_days"
                         - "last_year"
        max_results (int): Maximum number of articles to return (default: 10)
        
    Returns:
        Dict containing:
        - 'success' (bool): Whether search was successful
        - 'articles' (List[Dict]): List of articles with title, description, url, date, source
        - 'article_count' (int): Number of articles found
        - 'company_name' (str): The searched company name
        - 'error' (str, optional): Error message if failed
        
    Example:
        >>> result = search_news("TechTextiles Ltd", date_range="last_30_days")
        >>> print(f"Found {result['article_count']} articles")
        >>> for article in result['articles']:
        >>>     print(f"- {article['title']} ({article['published_at']})")
    """
    try:
        logger.info(f"Searching news for: {company_name} ({date_range})")
        
        # Calculate date range
        today = datetime.now()
        if date_range == "last_7_days":
            from_date = today - timedelta(days=7)
        elif date_range == "last_30_days":
            from_date = today - timedelta(days=30)
        elif date_range == "last_90_days":
            from_date = today - timedelta(days=90)
        elif date_range == "last_year":
            from_date = today - timedelta(days=365)
        else:
            from_date = today - timedelta(days=30)  # Default
        
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = today.strftime("%Y-%m-%d")
        
        # Get NewsAPI key from environment
        api_key = os.getenv("NEWSAPI_KEY")
        
        if not api_key:
            logger.warning("NewsAPI key not found. Using mock data for demonstration.")
            # Return mock data for demo purposes
            return _get_mock_news_data(company_name)
        
        # NewsAPI endpoint
        url = "https://newsapi.org/v2/everything"
        
        params = {
            'q': company_name,
            'from': from_date_str,
            'to': to_date_str,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': min(max_results, 100),  # NewsAPI max is 100
            'apiKey': api_key
        }
        
        # Make API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'ok':
            logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return {
                'success': False,
                'error': data.get('message', 'Unknown error'),
                'articles': [],
                'article_count': 0,
                'company_name': company_name
            }
        
        # Parse articles
        articles = []
        for article in data.get('articles', [])[:max_results]:
            articles.append({
                'title': article.get('title', 'No title'),
                'description': article.get('description', 'No description'),
                'url': article.get('url', ''),
                'published_at': article.get('publishedAt', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'author': article.get('author', 'Unknown')
            })
        
        logger.info(f"Found {len(articles)} articles for {company_name}")
        
        return {
            'success': True,
            'articles': articles,
            'article_count': len(articles),
            'company_name': company_name,
            'date_range': f"{from_date_str} to {to_date_str}"
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while searching news: {e}")
        return {
            'success': False,
            'error': f"Network error: {str(e)}",
            'articles': [],
            'article_count': 0,
            'company_name': company_name
        }
    except Exception as e:
        logger.error(f"Failed to search news for {company_name}: {e}")
        return {
            'success': False,
            'error': str(e),
            'articles': [],
            'article_count': 0,
            'company_name': company_name
        }


def analyze_sentiment(article_text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of a news article.
    
    This function uses simple keyword-based sentiment analysis.
    For production, you can integrate OpenAI API for more accurate sentiment.
    
    Args:
        article_text (str): Text to analyze (headline + description)
        
    Returns:
        Dict containing:
        - 'sentiment' (str): 'positive', 'negative', or 'neutral'
        - 'confidence' (float): Confidence score (0.0 to 1.0)
        - 'reasoning' (str): Brief explanation
        
    Example:
        >>> text = "Company wins sustainability award and reports record profits"
        >>> result = analyze_sentiment(text)
        >>> print(result['sentiment'])
        'positive'
    """
    try:
        # Convert to lowercase for matching
        text_lower = article_text.lower()
        
        # Define keyword sets
        positive_keywords = [
            'award', 'win', 'success', 'growth', 'profit', 'expansion', 
            'innovation', 'achievement', 'excellence', 'breakthrough', 
            'record', 'leading', 'pioneer', 'sustainable', 'approved',
            'partnership', 'collaboration', 'contract', 'milestone'
        ]
        
        negative_keywords = [
            'fraud', 'scandal', 'lawsuit', 'fine', 'penalty', 'investigation',
            'violation', 'bankrupt', 'loss', 'decline', 'failure', 'breach',
            'controversy', 'criticized', 'accused', 'suspended', 'illegal',
            'complaint', 'dispute', 'problem', 'issue', 'concern', 'risk'
        ]
        
        # Count keyword matches
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        # Determine sentiment
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.6 + (positive_count - negative_count) * 0.1, 0.95)
            reasoning = f"Contains {positive_count} positive keywords, {negative_count} negative keywords"
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.6 + (negative_count - positive_count) * 0.1, 0.95)
            reasoning = f"Contains {negative_count} negative keywords, {positive_count} positive keywords"
        else:
            sentiment = 'neutral'
            confidence = 0.5
            reasoning = f"Balanced sentiment: {positive_count} positive, {negative_count} negative keywords"
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'reasoning': reasoning,
            'positive_signals': positive_count,
            'negative_signals': negative_count
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        return {
            'sentiment': 'neutral',
            'confidence': 0.0,
            'reasoning': f"Analysis failed: {str(e)}",
            'positive_signals': 0,
            'negative_signals': 0
        }


def _get_mock_news_data(company_name: str) -> Dict[str, Any]:
    """
    Generate mock news data for demonstration purposes.
    Used when NewsAPI key is not available.
    """
    mock_articles = [
        {
            'title': f'{company_name} Wins Sustainability Award',
            'description': f'{company_name} has been recognized for its eco-friendly practices and commitment to sustainable manufacturing.',
            'url': 'https://example.com/article1',
            'published_at': '2025-11-20T10:00:00Z',
            'source': 'Industry Today',
            'author': 'John Smith'
        },
        {
            'title': f'Q4 Growth Report: {company_name} Exceeds Expectations',
            'description': f'{company_name} reports strong Q4 performance with 15% year-over-year growth in textile exports.',
            'url': 'https://example.com/article2',
            'published_at': '2025-12-10T14:30:00Z',
            'source': 'Trade Journal',
            'author': 'Sarah Johnson'
        },
        {
            'title': f'{company_name} Partners with Major Retailer',
            'description': f'New partnership announced between {company_name} and leading retail chain for sustainable clothing line.',
            'url': 'https://example.com/article3',
            'published_at': '2026-01-15T09:00:00Z',
            'source': 'Business News',
            'author': 'Mike Williams'
        }
    ]
    
    logger.info(f"Returning {len(mock_articles)} mock articles (NewsAPI key not configured)")
    
    return {
        'success': True,
        'articles': mock_articles,
        'article_count': len(mock_articles),
        'company_name': company_name,
        'note': 'Using mock data - Configure NEWSAPI_KEY in .env for real data'
    }


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print("TESTING MCP-2: NEWS TOOLS")
    print("=" * 80)
    
    # Test 1: Search news
    print("\n[TEST 1] Searching news for 'TechTextiles Ltd'...")
    result = search_news("TechTextiles Ltd", date_range="last_30_days", max_results=5)
    
    if result['success']:
        print(f"✅ Success!")
        print(f"   Company: {result['company_name']}")
        print(f"   Articles found: {result['article_count']}")
        
        if 'note' in result:
            print(f"   ⚠️  {result['note']}")
        
        print(f"\n   Articles:")
        for i, article in enumerate(result['articles'], 1):
            print(f"\n   {i}. {article['title']}")
            print(f"      Source: {article['source']}")
            print(f"      Date: {article['published_at']}")
            print(f"      {article['description'][:100]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 2: Analyze sentiment
    print("\n[TEST 2] Analyzing sentiment...")
    test_texts = [
        "Company wins sustainability award and reports record profits",
        "Fraud investigation launched against company officials",
        "Company announces new product line"
    ]
    
    for text in test_texts:
        sentiment_result = analyze_sentiment(text)
        print(f"\n   Text: '{text}'")
        print(f"   Sentiment: {sentiment_result['sentiment']} (confidence: {sentiment_result['confidence']:.2f})")
        print(f"   Reasoning: {sentiment_result['reasoning']}")
    
    print("\n" + "=" * 80)
    print("NEWS TOOLS TEST COMPLETE")
    print("=" * 80)