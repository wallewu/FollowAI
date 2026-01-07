"""
Search engine API clients for the WebSearcher MCP server.

Provides unified interface for different search engine APIs.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import httpx

from .config import SearchEngineConfig
from .errors import SearchError
from .logging_config import get_logger

logger = get_logger("search")


@dataclass
class SearchResult:
    """Represents a single search result."""
    
    title: str
    url: str
    snippet: str
    position: Optional[int] = None


class SearchClient(ABC):
    """Abstract base class for search engine clients."""
    
    def __init__(self, config: SearchEngineConfig):
        """
        Initialize search client.
        
        Args:
            config: Search engine configuration
        """
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
    
    @abstractmethod
    async def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """
        Perform a search query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
            
        Raises:
            SearchError: If search fails
        """
        pass
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class GoogleSearchClient(SearchClient):
    """Google Custom Search API client."""
    
    BASE_URL = "https://www.googleapis.com/customsearch/v1"
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """Perform Google Custom Search."""
        if not self.config.api_key:
            raise SearchError("Google API key not configured")
        
        if not self.config.search_engine_id:
            raise SearchError("Google Search Engine ID not configured")
        
        max_results = max_results or self.config.max_results
        
        try:
            logger.info(f"Performing Google search: {query}")
            
            params = {
                "key": self.config.api_key,
                "cx": self.config.search_engine_id,
                "q": query,
                "num": min(max_results, 10)  # Google API max is 10 per request
            }
            
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            results = []
            for idx, item in enumerate(items[:max_results], 1):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    position=idx
                ))
            
            logger.info(f"Google search returned {len(results)} results")
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Google API HTTP error: {e.response.status_code}")
            raise SearchError(f"Google API error: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("Google API request timed out")
            raise SearchError("Search request timed out")
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            raise SearchError(f"Search failed: {str(e)}")


class BingSearchClient(SearchClient):
    """Bing Web Search API client."""
    
    BASE_URL = "https://api.bing.microsoft.com/v7.0/search"
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """Perform Bing Web Search."""
        if not self.config.api_key:
            raise SearchError("Bing API key not configured")
        
        max_results = max_results or self.config.max_results
        
        try:
            logger.info(f"Performing Bing search: {query}")
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.config.api_key
            }
            
            params = {
                "q": query,
                "count": max_results,
                "textDecorations": False,
                "textFormat": "Raw"
            }
            
            response = await self.client.get(self.BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            web_pages = data.get("webPages", {})
            items = web_pages.get("value", [])
            
            results = []
            for idx, item in enumerate(items[:max_results], 1):
                results.append(SearchResult(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", ""),
                    position=idx
                ))
            
            logger.info(f"Bing search returned {len(results)} results")
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Bing API HTTP error: {e.response.status_code}")
            raise SearchError(f"Bing API error: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("Bing API request timed out")
            raise SearchError("Search request timed out")
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            raise SearchError(f"Search failed: {str(e)}")


class SerpApiClient(SearchClient):
    """SerpAPI client (supports multiple search engines)."""
    
    BASE_URL = "https://serpapi.com/search"
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """Perform search using SerpAPI."""
        if not self.config.api_key:
            raise SearchError("SerpAPI key not configured")
        
        max_results = max_results or self.config.max_results
        
        try:
            logger.info(f"Performing SerpAPI search: {query}")
            
            params = {
                "api_key": self.config.api_key,
                "q": query,
                "num": max_results,
                "engine": "google"  # Default to Google
            }
            
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "error" in data:
                raise SearchError(f"SerpAPI error: {data['error']}")
            
            items = data.get("organic_results", [])
            
            results = []
            for idx, item in enumerate(items[:max_results], 1):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    position=item.get("position", idx)
                ))
            
            logger.info(f"SerpAPI search returned {len(results)} results")
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error(f"SerpAPI HTTP error: {e.response.status_code}")
            raise SearchError(f"SerpAPI error: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("SerpAPI request timed out")
            raise SearchError("Search request timed out")
        except Exception as e:
            logger.error(f"SerpAPI search failed: {e}")
            raise SearchError(f"Search failed: {str(e)}")


def create_search_client(config: SearchEngineConfig) -> SearchClient:
    """
    Factory function to create appropriate search client.
    
    Args:
        config: Search engine configuration
        
    Returns:
        Configured search client instance
        
    Raises:
        ValueError: If search engine is not supported
    """
    clients = {
        "google": GoogleSearchClient,
        "bing": BingSearchClient,
        "serpapi": SerpApiClient
    }
    
    client_class = clients.get(config.engine.lower())
    if not client_class:
        raise ValueError(f"Unsupported search engine: {config.engine}")
    
    logger.info(f"Creating search client: {config.engine}")
    return client_class(config)
