"""News API integration module."""
import requests
import time
from config import Config

# Mock data fallback for when API fails
MOCK_ARTICLES = [
    {
        "title": "AI Breakthrough: New Model Can Summarize News with 99% Accuracy",
        "description": "Researchers have developed a revolutionary AI system that can understand and summarize news articles better than humans.",
        "content": "The new model, trained on millions of articles, shows remarkable understanding of context and nuance. It can generate concise summaries while preserving key information.",
        "url": "https://example.com/ai-news-1",
        "source": "Tech Daily",
        "published_at": "2026-02-12"
    },
    {
        "title": "Major Tech Company Announces Quantum Computing Milestone",
        "description": "A breakthrough in quantum computing promises to revolutionize how we process information.",
        "content": "The company's new quantum processor achieved what experts call 'quantum supremacy' in specific computational tasks, opening new possibilities for drug discovery and cryptography.",
        "url": "https://example.com/quantum-news",
        "source": "Future Tech",
        "published_at": "2026-02-12"
    },
    {
        "title": "Tech Giants Announce New AI Safety Standards",
        "description": "Leading technology companies have agreed on voluntary AI safety guidelines to ensure responsible development.",
        "content": "The new framework includes transparency requirements, regular audits, and public disclosure of AI capabilities and limitations.",
        "url": "https://example.com/ai-safety",
        "source": "Tech Weekly",
        "published_at": "2026-02-12"
    }
]

class NewsAPI:
    """Fetch news articles from NewsAPI."""
    
    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.last_call_time = 0
        self.min_interval = 60.0 / Config.NEWS_API_RPM  # Rate limiting
    
    def _wait_if_needed(self):
        """Wait if we need to rate limit."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"Rate limiting News API: waiting {wait_time:.2f}s...")
            time.sleep(wait_time)
        self.last_call_time = time.time()
    
    def fetch_top_headlines(self, category="technology", country="us", max_articles=5):
        """
        Fetch top headlines.
        
        Args:
            category: News category (business, technology, etc.)
            country: Country code (us, gb, etc.)
            max_articles: Maximum number of articles to return
        
        Returns:
            List of article dictionaries
        """
        self._wait_if_needed()
        
        url = f"{self.base_url}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "category": category,
            "country": country,
            "pageSize": max_articles
        }
        
        # Always try API first, but have mock data ready
        try:
            print(f"Fetching news from API...")
            response = requests.get(url, params=params, timeout=Config.REQUEST_TIMEOUT)
            
            # Handle 401 Unauthorized specifically
            if response.status_code == 401:
                print(f"✗ News API key is invalid or unauthorized")
                print("⚠️ Using mock data instead")
                return MOCK_ARTICLES[:max_articles]
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                print(f"✗ News API error: {data.get('message', 'Unknown error')}")
                print("⚠️ Using mock data instead")
                return MOCK_ARTICLES[:max_articles]
            
            articles = data.get("articles", [])
            
            # If no articles returned, use mock data
            if not articles:
                print("✗ No articles returned from API")
                print("⚠️ Using mock data instead")
                return MOCK_ARTICLES[:max_articles]
            
            # Extract relevant fields
            processed_articles = []
            for article in articles:
                processed_articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", "")
                })
            
            print(f"✓ Fetched {len(processed_articles)} articles from News API")
            return processed_articles
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching news: {e}")
            print("⚠️ Using mock data instead")
            return MOCK_ARTICLES[:max_articles]
        
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            print("⚠️ Using mock data instead")
            return MOCK_ARTICLES[:max_articles]

# Test the module
if __name__ == "__main__":
    api = NewsAPI()
    articles = api.fetch_top_headlines(category="technology", max_articles=3)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['url']}")