"""Tests for search client functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.search_client import (
    SearchResult,
    SearchClient,
    GoogleSearchClient,
    BingSearchClient,
    SerpApiClient,
    create_search_client
)
from src.config import SearchEngineConfig
from src.errors import SearchError


class TestSearchResult:
    """Test SearchResult dataclass."""
    
    def test_create_search_result(self):
        """Test creating a search result."""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            position=1
        )
        
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"
        assert result.position == 1


class TestCreateSearchClient:
    """Test search client factory function."""
    
    def test_create_google_client(self):
        """Test creating Google search client."""
        config = SearchEngineConfig(engine="google", api_key="test_key")
        client = create_search_client(config)
        
        assert isinstance(client, GoogleSearchClient)
    
    def test_create_bing_client(self):
        """Test creating Bing search client."""
        config = SearchEngineConfig(engine="bing", api_key="test_key")
        client = create_search_client(config)
        
        assert isinstance(client, BingSearchClient)
    
    def test_create_serpapi_client(self):
        """Test creating SerpAPI client."""
        config = SearchEngineConfig(engine="serpapi", api_key="test_key")
        client = create_search_client(config)
        
        assert isinstance(client, SerpApiClient)
    
    def test_create_unsupported_client(self):
        """Test creating client with unsupported engine."""
        config = SearchEngineConfig(engine="unsupported", api_key="test_key")
        
        with pytest.raises(ValueError) as exc_info:
            create_search_client(config)
        
        assert "Unsupported search engine" in str(exc_info.value)


@pytest.mark.asyncio
class TestGoogleSearchClient:
    """Test Google search client."""
    
    async def test_search_no_api_key(self):
        """Test search fails without API key."""
        config = SearchEngineConfig(engine="google")
        client = GoogleSearchClient(config)
        
        with pytest.raises(SearchError) as exc_info:
            await client.search("test query")
        
        assert "API key not configured" in str(exc_info.value)
    
    async def test_search_no_engine_id(self):
        """Test search fails without search engine ID."""
        config = SearchEngineConfig(engine="google", api_key="test_key")
        client = GoogleSearchClient(config)
        
        with pytest.raises(SearchError) as exc_info:
            await client.search("test query")
        
        assert "Search Engine ID not configured" in str(exc_info.value)


@pytest.mark.asyncio
class TestBingSearchClient:
    """Test Bing search client."""
    
    async def test_search_no_api_key(self):
        """Test search fails without API key."""
        config = SearchEngineConfig(engine="bing")
        client = BingSearchClient(config)
        
        with pytest.raises(SearchError) as exc_info:
            await client.search("test query")
        
        assert "API key not configured" in str(exc_info.value)


@pytest.mark.asyncio
class TestSerpApiClient:
    """Test SerpAPI client."""
    
    async def test_search_no_api_key(self):
        """Test search fails without API key."""
        config = SearchEngineConfig(engine="serpapi")
        client = SerpApiClient(config)
        
        with pytest.raises(SearchError) as exc_info:
            await client.search("test query")
        
        assert "API key not configured" in str(exc_info.value)
    
    @patch('httpx.AsyncClient.get')
    async def test_search_success(self, mock_get):
        """Test successful search."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic_results": [
                {
                    "title": "Result 1",
                    "link": "https://example.com/1",
                    "snippet": "Snippet 1",
                    "position": 1
                },
                {
                    "title": "Result 2",
                    "link": "https://example.com/2",
                    "snippet": "Snippet 2",
                    "position": 2
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        config = SearchEngineConfig(engine="serpapi", api_key="test_key")
        client = SerpApiClient(config)
        
        results = await client.search("test query", max_results=2)
        
        assert len(results) == 2
        assert results[0].title == "Result 1"
        assert results[0].url == "https://example.com/1"
        assert results[1].title == "Result 2"
    
    @patch('httpx.AsyncClient.get')
    async def test_search_api_error(self, mock_get):
        """Test search with API error."""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": "API error message"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        config = SearchEngineConfig(engine="serpapi", api_key="test_key")
        client = SerpApiClient(config)
        
        with pytest.raises(SearchError) as exc_info:
            await client.search("test query")
        
        assert "API error message" in str(exc_info.value)
