"""
Bosco Core - News Capability
Get latest news using NewsAPI or other sources
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional


class News:
    """News information provider"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("NEWS_API_KEY", "")
        self.base_url = "https://newsapi.org/v2"
        
        if not self.api_key:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                        self.api_key = config.get("news_api_key", "")
                except:
                    pass
    
    def get_top_headlines(self, category: str = None, country: str = "us", limit: int = 5) -> Dict:
        """Get top headlines"""
        if not self.api_key:
            return self._get_demo_news(limit)
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "country": country,
                "apiKey": self.api_key,
                "pageSize": limit
            }
            if category:
                params["category"] = category
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                articles = []
                for article in data.get("articles", [])[:limit]:
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "url": article.get("url", "")
                    })
                return {"success": True, "articles": articles}
            else:
                return {"success": False, "error": data.get("message", "Unknown")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_news(self, query: str, limit: int = 5) -> Dict:
        """Search for news"""
        if not self.api_key:
            return {"success": True, "articles": [{"title": f"Demo: {query}", "description": "Demo news article", "source": "Demo"}]}
        
        try:
            url = f"{self.base_url}/everything"
            params = {"q": query, "apiKey": self.api_key, "pageSize": limit, "sortBy": "publishedAt"}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                articles = []
                for article in data.get("articles", [])[:limit]:
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", "")
                    })
                return {"success": True, "articles": articles}
            else:
                return {"success": False, "error": data.get("message", "Unknown")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_demo_news(self, limit: int) -> Dict:
        """Demo news"""
        return {
            "success": True,
            "articles": [
                {"title": "Bosco Core Updates", "description": "New AI features released", "source": "Bosco News"},
                {"title": "Technology Advances", "description": "Latest in AI and automation", "source": "Tech Daily"},
                {"title": "Weather Alert", "description": "Changing weather patterns reported", "source": "Weather Channel"}
            ][:limit]
        }
    
    def format_headlines(self, data: Dict) -> str:
        """Format headlines as speech"""
        if not data.get("success"):
            return f"I couldn't retrieve news. {data.get('error', '')}"
        
        articles = data.get("articles", [])
        if not articles:
            return "No news articles found."
        
        response = "Here are the top headlines. "
        for i, article in enumerate(articles, 1):
            response += f"{i}: {article.get('title', 'Untitled')}. "
        
        return response


_news = News()


def get_top_headlines(category: str = None, limit: int = 5) -> Dict:
    return _news.get_top_headlines(category, limit)


def search_news(query: str, limit: int = 5) -> Dict:
    return _news.search_news(query, limit)


def format_headlines(data: Dict) -> str:
    return _news.format_headlines(data)


if __name__ == "__main__":
    print("Testing News...")
    headlines = get_top_headlines()
    print(format_headlines(headlines))

