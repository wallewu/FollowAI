"""
Configuration management for the WebSearcher MCP server.

Handles loading and validation of configuration from environment variables and files.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .errors import ConfigurationError
from .logging_config import get_logger

logger = get_logger("config")


@dataclass
class SearchEngineConfig:
    """Configuration for search engine API."""
    
    engine: str
    api_key: Optional[str] = None
    search_engine_id: Optional[str] = None  # For Google Custom Search
    max_results: int = 10
    timeout: int = 30


@dataclass
class ServerConfig:
    """Configuration for the MCP server."""
    
    log_level: str = "INFO"
    debug_mode: bool = False


@dataclass
class Config:
    """Main configuration container."""
    
    search: SearchEngineConfig
    server: ServerConfig


class ConfigLoader:
    """Loads and validates configuration from environment variables."""
    
    def __init__(self, env_file: Optional[Path] = None):
        """
        Initialize configuration loader.
        
        Args:
            env_file: Path to .env file (optional)
        """
        self.env_file = env_file
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        if self.env_file and self.env_file.exists():
            logger.info(f"Loading environment from {self.env_file}")
            load_dotenv(self.env_file)
        else:
            # Try to load from default location
            default_env = Path.cwd() / ".env"
            if default_env.exists():
                logger.info(f"Loading environment from {default_env}")
                load_dotenv(default_env)
            else:
                logger.info("No .env file found, using environment variables only")
    
    def load(self) -> Config:
        """
        Load and validate configuration.
        
        Returns:
            Validated configuration object
            
        Raises:
            ConfigurationError: If configuration is invalid or incomplete
        """
        # Load search engine configuration
        search_config = self._load_search_config()
        
        # Load server configuration
        server_config = self._load_server_config()
        
        return Config(search=search_config, server=server_config)
    
    def _load_search_config(self) -> SearchEngineConfig:
        """
        Load search engine configuration.
        
        Returns:
            Search engine configuration
            
        Raises:
            ConfigurationError: If search engine configuration is invalid
        """
        engine = os.getenv("SEARCH_ENGINE", "serpapi").lower()
        
        # Validate engine selection
        valid_engines = ["google", "bing", "serpapi"]
        if engine not in valid_engines:
            raise ConfigurationError(
                f"Invalid search engine: {engine}. Must be one of: {', '.join(valid_engines)}"
            )
        
        # Load API key based on engine
        api_key = None
        search_engine_id = None
        
        if engine == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            if not api_key:
                logger.warning(
                    "GOOGLE_API_KEY not set. Search functionality will be limited. "
                    "Get your API key from: https://developers.google.com/custom-search/v1/overview"
                )
            if not search_engine_id:
                logger.warning(
                    "GOOGLE_SEARCH_ENGINE_ID not set. Please configure your custom search engine."
                )
        
        elif engine == "bing":
            api_key = os.getenv("BING_API_KEY")
            
            if not api_key:
                logger.warning(
                    "BING_API_KEY not set. Search functionality will be limited. "
                    "Get your API key from: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api"
                )
        
        elif engine == "serpapi":
            api_key = os.getenv("SERPAPI_KEY")
            
            if not api_key:
                logger.warning(
                    "SERPAPI_KEY not set. Search functionality will be limited. "
                    "Get your API key from: https://serpapi.com/"
                )
        
        # Load other search settings
        max_results = int(os.getenv("MAX_RESULTS", "10"))
        timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        # Validate max_results
        if max_results < 1 or max_results > 20:
            logger.warning(f"MAX_RESULTS={max_results} is out of range, using default: 10")
            max_results = 10
        
        logger.info(f"Search engine configured: {engine}")
        
        return SearchEngineConfig(
            engine=engine,
            api_key=api_key,
            search_engine_id=search_engine_id,
            max_results=max_results,
            timeout=timeout
        )
    
    def _load_server_config(self) -> ServerConfig:
        """
        Load server configuration.
        
        Returns:
            Server configuration
        """
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        debug_mode = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")
        
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            logger.warning(f"Invalid LOG_LEVEL={log_level}, using INFO")
            log_level = "INFO"
        
        return ServerConfig(
            log_level=log_level,
            debug_mode=debug_mode
        )


def load_config(env_file: Optional[Path] = None) -> Config:
    """
    Convenience function to load configuration.
    
    Args:
        env_file: Path to .env file (optional)
        
    Returns:
        Loaded configuration
    """
    loader = ConfigLoader(env_file)
    return loader.load()
