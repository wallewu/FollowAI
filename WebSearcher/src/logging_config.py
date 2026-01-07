"""
Logging configuration for the WebSearcher MCP server.

Provides centralized logging setup with configurable levels and formats.
"""

import logging
import sys
from typing import Optional


class SensitiveDataFilter(logging.Filter):
    """Filter to prevent sensitive data from being logged."""
    
    SENSITIVE_KEYS = ["api_key", "token", "password", "secret"]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records to remove sensitive information.
        
        Args:
            record: Log record to filter
            
        Returns:
            True to allow the record, False to suppress it
        """
        # Check if message contains sensitive keywords
        message = record.getMessage().lower()
        for key in self.SENSITIVE_KEYS:
            if key in message:
                # Mask the sensitive data
                record.msg = self._mask_sensitive_data(str(record.msg))
        return True
    
    def _mask_sensitive_data(self, message: str) -> str:
        """
        Mask sensitive data in log messages.
        
        Args:
            message: Original message
            
        Returns:
            Message with sensitive data masked
        """
        for key in self.SENSITIVE_KEYS:
            if key in message.lower():
                # Simple masking - in production, use more sophisticated approach
                parts = message.split("=")
                if len(parts) > 1:
                    return f"{parts[0]}=***REDACTED***"
        return message


def setup_logging(level: str = "INFO", debug_mode: bool = False) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug_mode: Enable debug mode with verbose output
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Override with DEBUG if debug_mode is enabled
    if debug_mode:
        numeric_level = logging.DEBUG
    
    # Create logger
    logger = logging.getLogger("websearcher")
    logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    if debug_mode:
        # Verbose format for debugging
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # Concise format for production
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    
    # Add sensitive data filter in production
    if not debug_mode:
        console_handler.addFilter(SensitiveDataFilter())
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info(f"Logging configured: level={level}, debug_mode={debug_mode}")
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (will be prefixed with 'websearcher.')
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"websearcher.{name}")
    return logging.getLogger("websearcher")


class LogContext:
    """Context manager for temporary log level changes."""
    
    def __init__(self, logger: logging.Logger, level: int):
        """
        Initialize log context.
        
        Args:
            logger: Logger to modify
            level: Temporary log level
        """
        self.logger = logger
        self.new_level = level
        self.old_level = logger.level
    
    def __enter__(self):
        """Enter context and set new log level."""
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original log level."""
        self.logger.setLevel(self.old_level)
