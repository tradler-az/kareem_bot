"""
Bosco Core - Web Search Capability
Search the web using Google or other search engines
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional


class WebSearch:
    """Web search provider"""
    
    def __init__(self, api_key: str = None, engine_id: str = None):
        self.api_key = api_key or os.environ.get("GOOGLE_SEARCH_API_KEY", "")
        self.engine_id = engine_id or os.environ.get("GOOGLE_SEARCH_ENGINE_ID", "")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                        self.api_key = config.get("google_search_api_key", "")
                        self.engine_id = config.get("google_search_engine_id", "")
                except:
                    pass
    
    def search(self, query: str, limit: int = 5) -> Dict:
        """Search the web"""
        if not self.api_key or not self.engine_id:
            return self._get_demo_search(query, limit)
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.engine_id,
                "q": query,
                "num": limit
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                results = []
                for item in data.get("items", [])[:limit]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", "")
                    })
                return {"success": True, "results": results, "query": query}
            else:
                return {"success": False, "error": data.get("error", {}).get("message", "Unknown")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_demo_search(self, query: str, limit: int) -> Dict:
        """Demo search results"""
        return {
            "success": True,
            "query": query,
            "results": [
                {"title": f"Result 1 for {query}", "snippet": "This is a demo search result.", "link": "https://example.com/1"},
                {"title": f"Result 2 for {query}", "snippet": "More information about the topic.", "link": "https://example.com/2"},
                {"title": f"Result 3 for {query}", "snippet": "Additional resources available.", "link": "https://example.com/3"}
            ][:limit],
            "demo": True
        }
    
    def format_results(self, data: Dict) -> str:
        """Format search results as speech"""
        if not data.get("success"):
            return f"I couldn't search. {data.get('error', '')}"
        
        results = data.get("results", [])
        if not results:
            return "No results found."
        
        response = f"Found {len(results)} results for '{data.get('query', 'your search')}'. "
        for i, result in enumerate(results, 1):
            response += f"{i}: {result.get('title', 'Untitled')}. "
        
        return response


_search = WebSearch()


def search(query: str, limit: int = 5) -> Dict:
    return _search.search(query, limit)


def format_results(data: Dict) -> str:
    return _search.format_results(data)


if __name__ == "__main__":
    print("Testing Web Search...")
    results = search("Python programming")
    print(format_results(results))

