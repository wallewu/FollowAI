"""
Error handling utilities for the WebSearcher MCP server.

Provides standardized error responses and exception handling for JSON-RPC communication.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("websearcher.errors")


class MCPError(Exception):
    """Base exception for MCP-related errors."""
    
    def __init__(self, message: str, code: int = -32603):
        """
        Initialize MCP error.
        
        Args:
            message: Error message
            code: JSON-RPC error code (default: -32603 Internal error)
        """
        self.message = message
        self.code = code
        super().__init__(message)


class InvalidRequestError(MCPError):
    """Exception for invalid JSON-RPC requests."""
    
    def __init__(self, message: str):
        super().__init__(message, code=-32600)


class InvalidParamsError(MCPError):
    """Exception for invalid method parameters."""
    
    def __init__(self, message: str):
        super().__init__(message, code=-32602)


class ToolNotFoundError(MCPError):
    """Exception for unknown tool requests."""
    
    def __init__(self, tool_name: str):
        super().__init__(f"Tool not found: {tool_name}", code=-32601)


class SearchError(MCPError):
    """Exception for search-related errors."""
    
    def __init__(self, message: str):
        super().__init__(f"Search error: {message}", code=-32000)


class ConfigurationError(MCPError):
    """Exception for configuration-related errors."""
    
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}", code=-32001)


def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Format an exception into a JSON-RPC error response.
    
    Args:
        error: The exception to format
        
    Returns:
        Dictionary containing error code and message
    """
    if isinstance(error, MCPError):
        return {
            "code": error.code,
            "message": error.message
        }
    else:
        # Generic error for unexpected exceptions
        logger.error(f"Unexpected error: {error}", exc_info=True)
        return {
            "code": -32603,
            "message": "Internal server error"
        }


def validate_tool_arguments(tool_name: str, arguments: Any) -> None:
    """
    Validate tool arguments.
    
    Args:
        tool_name: Name of the tool being called
        arguments: Arguments provided to the tool
        
    Raises:
        InvalidParamsError: If arguments are invalid
    """
    if not isinstance(arguments, dict):
        raise InvalidParamsError(f"Tool arguments must be a dictionary, got {type(arguments)}")
    
    if tool_name == "web_search":
        # Validate web_search specific arguments
        if "query" not in arguments:
            raise InvalidParamsError("Missing required parameter: query")
        
        query = arguments.get("query")
        if not isinstance(query, str):
            raise InvalidParamsError(f"Parameter 'query' must be a string, got {type(query)}")
        
        if not query.strip():
            raise InvalidParamsError("Parameter 'query' cannot be empty")
        
        max_results = arguments.get("max_results")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise InvalidParamsError(
                    f"Parameter 'max_results' must be an integer, got {type(max_results)}"
                )
            if max_results < 1 or max_results > 20:
                raise InvalidParamsError(
                    f"Parameter 'max_results' must be between 1 and 20, got {max_results}"
                )


def safe_error_message(error: Exception, debug_mode: bool = False) -> str:
    """
    Generate a safe error message that doesn't expose sensitive information.
    
    Args:
        error: The exception to format
        debug_mode: Whether to include detailed error information
        
    Returns:
        Safe error message string
    """
    if debug_mode:
        return str(error)
    
    if isinstance(error, MCPError):
        return error.message
    
    # Don't expose internal error details in production
    return "An internal error occurred. Please check the server logs for details."
