"""Tests for error handling utilities."""

import pytest
from src.errors import (
    MCPError,
    InvalidRequestError,
    InvalidParamsError,
    ToolNotFoundError,
    SearchError,
    ConfigurationError,
    format_error_response,
    validate_tool_arguments,
    safe_error_message
)


class TestMCPErrors:
    """Test MCP error classes."""
    
    def test_mcp_error_default_code(self):
        """Test MCPError with default error code."""
        error = MCPError("Test error")
        assert error.message == "Test error"
        assert error.code == -32603
    
    def test_mcp_error_custom_code(self):
        """Test MCPError with custom error code."""
        error = MCPError("Test error", code=-32000)
        assert error.code == -32000
    
    def test_invalid_request_error(self):
        """Test InvalidRequestError."""
        error = InvalidRequestError("Invalid request")
        assert error.code == -32600
        assert "Invalid request" in error.message
    
    def test_invalid_params_error(self):
        """Test InvalidParamsError."""
        error = InvalidParamsError("Invalid params")
        assert error.code == -32602
    
    def test_tool_not_found_error(self):
        """Test ToolNotFoundError."""
        error = ToolNotFoundError("unknown_tool")
        assert error.code == -32601
        assert "unknown_tool" in error.message
    
    def test_search_error(self):
        """Test SearchError."""
        error = SearchError("Search failed")
        assert error.code == -32000
        assert "Search error" in error.message
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Config missing")
        assert error.code == -32001
        assert "Configuration error" in error.message


class TestFormatErrorResponse:
    """Test error response formatting."""
    
    def test_format_mcp_error(self):
        """Test formatting MCP error."""
        error = SearchError("Test search error")
        response = format_error_response(error)
        
        assert "code" in response
        assert "message" in response
        assert response["code"] == -32000
        assert "Search error" in response["message"]
    
    def test_format_generic_error(self):
        """Test formatting generic exception."""
        error = ValueError("Generic error")
        response = format_error_response(error)
        
        assert response["code"] == -32603
        assert response["message"] == "Internal server error"


class TestValidateToolArguments:
    """Test tool argument validation."""
    
    def test_validate_non_dict_arguments(self):
        """Test validation fails for non-dict arguments."""
        with pytest.raises(InvalidParamsError) as exc_info:
            validate_tool_arguments("web_search", "not a dict")
        
        assert "must be a dictionary" in str(exc_info.value)
    
    def test_validate_missing_query(self):
        """Test validation fails when query is missing."""
        with pytest.raises(InvalidParamsError) as exc_info:
            validate_tool_arguments("web_search", {})
        
        assert "Missing required parameter: query" in str(exc_info.value)
    
    def test_validate_non_string_query(self):
        """Test validation fails for non-string query."""
        with pytest.raises(InvalidParamsError) as exc_info:
            validate_tool_arguments("web_search", {"query": 123})
        
        assert "must be a string" in str(exc_info.value)
    
    def test_validate_empty_query(self):
        """Test validation fails for empty query."""
        with pytest.raises(InvalidParamsError) as exc_info:
            validate_tool_arguments("web_search", {"query": "   "})
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_validate_invalid_max_results_type(self):
        """Test validation fails for non-integer max_results."""
        with pytest.raises(InvalidParamsError) as exc_info:
            validate_tool_arguments("web_search", {
                "query": "test",
                "max_results": "10"
            })
        
        assert "must be an integer" in str(exc_info.value)
    
    def test_validate_max_results_out_of_range(self):
        """Test validation fails for out-of-range max_results."""
        with pytest.raises(InvalidParamsError) as exc_info:
            validate_tool_arguments("web_search", {
                "query": "test",
                "max_results": 25
            })
        
        assert "must be between 1 and 20" in str(exc_info.value)
    
    def test_validate_valid_arguments(self):
        """Test validation passes for valid arguments."""
        # Should not raise any exception
        validate_tool_arguments("web_search", {
            "query": "test query",
            "max_results": 10
        })


class TestSafeErrorMessage:
    """Test safe error message generation."""
    
    def test_safe_message_mcp_error(self):
        """Test safe message for MCP error."""
        error = SearchError("API failed")
        message = safe_error_message(error, debug_mode=False)
        
        assert "Search error: API failed" in message
    
    def test_safe_message_generic_error_production(self):
        """Test safe message for generic error in production."""
        error = ValueError("Internal details")
        message = safe_error_message(error, debug_mode=False)
        
        assert "internal error occurred" in message.lower()
        assert "Internal details" not in message
    
    def test_safe_message_generic_error_debug(self):
        """Test safe message for generic error in debug mode."""
        error = ValueError("Internal details")
        message = safe_error_message(error, debug_mode=True)
        
        assert "Internal details" in message
