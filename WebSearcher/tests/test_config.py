"""Tests for configuration management."""

import os
import pytest
from pathlib import Path
from src.config import (
    SearchEngineConfig,
    ServerConfig,
    Config,
    ConfigLoader,
    load_config
)
from src.errors import ConfigurationError


class TestSearchEngineConfig:
    """Test SearchEngineConfig dataclass."""
    
    def test_create_config(self):
        """Test creating search engine config."""
        config = SearchEngineConfig(
            engine="google",
            api_key="test_key",
            search_engine_id="test_id",
            max_results=5,
            timeout=20
        )
        
        assert config.engine == "google"
        assert config.api_key == "test_key"
        assert config.search_engine_id == "test_id"
        assert config.max_results == 5
        assert config.timeout == 20


class TestServerConfig:
    """Test ServerConfig dataclass."""
    
    def test_create_config(self):
        """Test creating server config."""
        config = ServerConfig(log_level="DEBUG", debug_mode=True)
        
        assert config.log_level == "DEBUG"
        assert config.debug_mode is True
    
    def test_default_values(self):
        """Test default config values."""
        config = ServerConfig()
        
        assert config.log_level == "INFO"
        assert config.debug_mode is False


class TestConfigLoader:
    """Test ConfigLoader class."""
    
    def test_load_search_config_serpapi(self, monkeypatch):
        """Test loading SerpAPI configuration."""
        monkeypatch.setenv("SEARCH_ENGINE", "serpapi")
        monkeypatch.setenv("SERPAPI_KEY", "test_serpapi_key")
        
        loader = ConfigLoader()
        config = loader._load_search_config()
        
        assert config.engine == "serpapi"
        assert config.api_key == "test_serpapi_key"
    
    def test_load_search_config_google(self, monkeypatch):
        """Test loading Google configuration."""
        monkeypatch.setenv("SEARCH_ENGINE", "google")
        monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key")
        monkeypatch.setenv("GOOGLE_SEARCH_ENGINE_ID", "test_engine_id")
        
        loader = ConfigLoader()
        config = loader._load_search_config()
        
        assert config.engine == "google"
        assert config.api_key == "test_google_key"
        assert config.search_engine_id == "test_engine_id"
    
    def test_load_search_config_bing(self, monkeypatch):
        """Test loading Bing configuration."""
        monkeypatch.setenv("SEARCH_ENGINE", "bing")
        monkeypatch.setenv("BING_API_KEY", "test_bing_key")
        
        loader = ConfigLoader()
        config = loader._load_search_config()
        
        assert config.engine == "bing"
        assert config.api_key == "test_bing_key"
    
    def test_load_search_config_invalid_engine(self, monkeypatch):
        """Test loading with invalid search engine."""
        monkeypatch.setenv("SEARCH_ENGINE", "invalid_engine")
        
        loader = ConfigLoader()
        
        with pytest.raises(ConfigurationError) as exc_info:
            loader._load_search_config()
        
        assert "Invalid search engine" in str(exc_info.value)
    
    def test_load_search_config_defaults(self, monkeypatch):
        """Test default search configuration values."""
        monkeypatch.setenv("SEARCH_ENGINE", "serpapi")
        monkeypatch.delenv("MAX_RESULTS", raising=False)
        monkeypatch.delenv("REQUEST_TIMEOUT", raising=False)
        
        loader = ConfigLoader()
        config = loader._load_search_config()
        
        assert config.max_results == 10
        assert config.timeout == 30
    
    def test_load_search_config_custom_values(self, monkeypatch):
        """Test custom search configuration values."""
        monkeypatch.setenv("SEARCH_ENGINE", "serpapi")
        monkeypatch.setenv("MAX_RESULTS", "15")
        monkeypatch.setenv("REQUEST_TIMEOUT", "45")
        
        loader = ConfigLoader()
        config = loader._load_search_config()
        
        assert config.max_results == 15
        assert config.timeout == 45
    
    def test_load_server_config(self, monkeypatch):
        """Test loading server configuration."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("DEBUG_MODE", "true")
        
        loader = ConfigLoader()
        config = loader._load_server_config()
        
        assert config.log_level == "DEBUG"
        assert config.debug_mode is True
    
    def test_load_server_config_defaults(self, monkeypatch):
        """Test default server configuration."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        monkeypatch.delenv("DEBUG_MODE", raising=False)
        
        loader = ConfigLoader()
        config = loader._load_server_config()
        
        assert config.log_level == "INFO"
        assert config.debug_mode is False
    
    def test_load_full_config(self, monkeypatch):
        """Test loading full configuration."""
        monkeypatch.setenv("SEARCH_ENGINE", "serpapi")
        monkeypatch.setenv("SERPAPI_KEY", "test_key")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        
        loader = ConfigLoader()
        config = loader.load()
        
        assert isinstance(config, Config)
        assert isinstance(config.search, SearchEngineConfig)
        assert isinstance(config.server, ServerConfig)
        assert config.search.engine == "serpapi"
        assert config.server.log_level == "INFO"


class TestLoadConfig:
    """Test load_config convenience function."""
    
    def test_load_config_function(self, monkeypatch):
        """Test load_config function."""
        monkeypatch.setenv("SEARCH_ENGINE", "serpapi")
        monkeypatch.setenv("SERPAPI_KEY", "test_key")
        
        config = load_config()
        
        assert isinstance(config, Config)
        assert config.search.engine == "serpapi"
