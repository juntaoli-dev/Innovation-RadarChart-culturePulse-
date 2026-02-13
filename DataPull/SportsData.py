"""
Sports Data Pull for Culture Pulse Radar Chart
Fetches sports-related data to measure cultural engagement
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SportsDataPuller:
    """Pulls sports data to measure cultural pulse"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Sports Data Puller
        
        Args:
            api_key: NewsAPI key for fetching sports news
                    Get free key at: https://newsapi.org/
        """
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"
        
    def fetch_sports_news(self, days_back: int = 7, language: str = 'en', start_date: str = None, end_date: str = None) -> Dict:
        """
        Fetch sports news articles to gauge cultural engagement
        
        Args:
            days_back: Number of days to look back (ignored if start_date/end_date provided)
            language: Language code (default: 'en')
            start_date: Start date in 'YYYY-MM-DD' format (optional)
            end_date: End date in 'YYYY-MM-DD' format (optional)
            
        Returns:
            Dictionary with sports news data
        """
        if not self.api_key:
            raise ValueError("API key required. Get one at https://newsapi.org/")
        
        # Use custom dates if provided
        if start_date and end_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=days_back)
        
        params = {
            'apiKey': self.api_key,
            'q': 'sports OR football OR basketball OR baseball OR soccer',
            'language': language,
            'from': start_date_obj.strftime('%Y-%m-%d'),
            'to': end_date_obj.strftime('%Y-%m-%d'),
            'sortBy': 'publishedAt',
            'pageSize': 100
        }
        
        response = requests.get(f"{self.base_url}/everything", params=params)
        response.raise_for_status()
        
        return response.json()
    
    def calculate_pulse_score(self, news_data: Dict) -> float:
        """
        Calculate a pulse score (0-100) based on sports engagement
        
        Metrics considered:
        - Article volume (more aggressive scaling)
        - Source diversity
        - Recent activity (HEAVILY weighted for breaking events)
        - Keyword intensity (sports-specific terms boost score)
        
        Args:
            news_data: Raw news data from API
            
        Returns:
            Pulse score between 0-100
        """
        if not news_data or 'articles' not in news_data:
            return 0.0
        
        articles = news_data.get('articles', [])
        total_results = news_data.get('totalResults', 0)
        
        # Volume score (0-35 points) - exponential scaling for dramatic effect
        article_ratio = len(articles) / 100
        volume_score = min(35, (article_ratio ** 0.7) * 35)
        
        # Source diversity score (0-25 points)
        unique_sources = len(set(article.get('source', {}).get('name') 
                                 for article in articles if article.get('source')))
        diversity_score = min(25, (unique_sources / 20) * 25)
        
        # Recency score (0-40 points) - HEAVILY weighted!
        # Recent events should SPIKE the score
        now = datetime.now()
        recent_articles = sum(1 for article in articles 
                            if self._is_recent(article.get('publishedAt'), now))
        # More aggressive: if lots of recent articles, this dominates
        recency_score = min(40, (recent_articles / 20) * 40)
        
        # Keyword intensity bonus (0-15 points)
        # Count sports-specific keywords in titles
        sports_keywords = ['super bowl', 'championship', 'playoffs', 'finals', 
                          'world cup', 'olympics', 'game', 'victory', 'win', 'score']
        keyword_count = 0
        for article in articles:
            title = (article.get('title') or '').lower()
            keyword_count += sum(1 for kw in sports_keywords if kw in title)
        
        keyword_intensity = min(15, (keyword_count / 30) * 15)
        
        total_score = volume_score + diversity_score + recency_score + keyword_intensity
        return round(min(100, total_score), 2)
    
    def _is_recent(self, published_at: str, now: datetime) -> bool:
        """Check if article was published in last 24 hours"""
        if not published_at:
            return False
        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            return (now - pub_date).days < 1
        except:
            return False
    
    def get_sports_pulse(self, days_back: int = 7, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get complete sports pulse data for radar chart
        
        Args:
            days_back: Days of data to analyze
            start_date: Start date in 'YYYY-MM-DD' format (optional)
            end_date: End date in 'YYYY-MM-DD' format (optional)
            
        Returns:
            Dictionary with pulse score and metadata
        """
        news_data = self.fetch_sports_news(days_back=days_back, start_date=start_date, end_date=end_date)
        pulse_score = self.calculate_pulse_score(news_data)
        
        return {
            'category': 'Sports',
            'pulse_score': pulse_score,
            'article_count': len(news_data.get('articles', [])),
            'total_results': news_data.get('totalResults', 0),
            'timestamp': datetime.now().isoformat(),
            'days_analyzed': days_back
        }


# Example usage
if __name__ == "__main__":
    # API key will be loaded automatically from .env file
    
    try:
        puller = SportsDataPuller()  # Automatically loads from .env
        sports_pulse = puller.get_sports_pulse(days_back=7)
        
        print("=" * 50)
        print("SPORTS CULTURE PULSE")
        print("=" * 50)
        print(f"Pulse Score: {sports_pulse['pulse_score']}/100")
        print(f"Articles Found: {sports_pulse['article_count']}")
        print(f"Total Results: {sports_pulse['total_results']}")
        print(f"Period: Last {sports_pulse['days_analyzed']} days")
        print(f"Timestamp: {sports_pulse['timestamp']}")
        print("=" * 50)
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo use this script:")
        print("1. Get a free API key from https://newsapi.org/")
        print("2. Set it as environment variable: export NEWS_API_KEY='your-key'")
        print("3. Or replace 'YOUR_API_KEY_HERE' in the script")
    except Exception as e:
        print(f"Error fetching data: {e}")
