"""
Politics Data Pull for Culture Pulse Radar Chart
Fetches politics-related data to measure cultural engagement
"""

import requests
from datetime import datetime, timedelta
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()


class PoliticsDataPuller:
    """Pulls politics data to measure cultural pulse"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"
        
    def fetch_politics_news(self, days_back: int = 7, language: str = 'en') -> Dict:
        """Fetch politics news articles to gauge cultural engagement"""
        if not self.api_key:
            raise ValueError("API key required. Get one at https://newsapi.org/")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            'apiKey': self.api_key,
            'q': 'politics OR government OR election OR policy OR legislation',
            'language': language,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'sortBy': 'publishedAt',
            'pageSize': 100
        }
        
        response = requests.get(f"{self.base_url}/everything", params=params)
        response.raise_for_status()
        return response.json()
    
    def calculate_pulse_score(self, news_data: Dict) -> float:
        """Calculate pulse score (0-100) based on political engagement"""
        if not news_data or 'articles' not in news_data:
            return 0.0
        
        articles = news_data.get('articles', [])
        
        # Volume score (0-40 points)
        volume_score = min(40, (len(articles) / 100) * 40)
        
        # Source diversity score (0-30 points)
        unique_sources = len(set(article.get('source', {}).get('name') 
                                 for article in articles if article.get('source')))
        diversity_score = min(30, (unique_sources / 20) * 30)
        
        # Recency score (0-30 points)
        now = datetime.now()
        recent_articles = sum(1 for article in articles 
                            if self._is_recent(article.get('publishedAt'), now))
        recency_score = min(30, (recent_articles / 30) * 30)
        
        return round(volume_score + diversity_score + recency_score, 2)
    
    def _is_recent(self, published_at: str, now: datetime) -> bool:
        """Check if article was published in last 24 hours"""
        if not published_at:
            return False
        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            return (now - pub_date).days < 1
        except:
            return False
    
    def get_politics_pulse(self, days_back: int = 7) -> Dict:
        """Get complete politics pulse data for radar chart"""
        news_data = self.fetch_politics_news(days_back=days_back)
        pulse_score = self.calculate_pulse_score(news_data)
        
        return {
            'category': 'Politics',
            'pulse_score': pulse_score,
            'article_count': len(news_data.get('articles', [])),
            'total_results': news_data.get('totalResults', 0),
            'timestamp': datetime.now().isoformat(),
            'days_analyzed': days_back
        }


if __name__ == "__main__":
    try:
        puller = PoliticsDataPuller()
        pulse = puller.get_politics_pulse(days_back=7)
        
        print("=" * 50)
        print("POLITICS CULTURE PULSE")
        print("=" * 50)
        print(f"Pulse Score: {pulse['pulse_score']}/100")
        print(f"Articles Found: {pulse['article_count']}")
        print(f"Total Results: {pulse['total_results']}")
        print("=" * 50)
    except Exception as e:
        print(f"Error: {e}")
