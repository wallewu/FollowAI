"""
WebSearcher MCP Server

A Model Context Protocol server that provides web search functionality to AI assistants.
"""

import asyncio
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import load_config, Config
from .errors import (
    MCPError,
    InvalidParamsError,
    ToolNotFoundError,
    SearchError,
    validate_tool_arguments,
    safe_error_message
)
from .logging_config import setup_logging, get_logger
from .search_client import create_search_client, SearchClient

# Logger will be configured in main()
logger = get_logger()


class WebSearcherServer:
    """MCP Server for web search functionality."""
    
    def __init__(self, config: Config):
        """
        Initialize the WebSearcher MCP server.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.server = Server("websearcher")
        self.search_client: Optional[SearchClient] = None
        self.setup_handlers()
        logger.info("WebSearcher MCP Server initialized")
    
    async def initialize(self):
        """Initialize async resources."""
        try:
            self.search_client = create_search_client(self.config.search)
            logger.info("Search client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize search client: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources."""
        if self.search_client:
            await self.search_client.close()
            logger.info("Search client closed")
    
    def setup_handlers(self):
        """Set up request handlers for the MCP server."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            logger.debug("Listing available tools")
            return [
                Tool(
                    name="web_search",
                    description="Search the web for information using a search engine API. "
                                "Returns a list of search results with titles, URLs, and snippets.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query string"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 10)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 20
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                # Validate tool name
                if name != "web_search":
                    raise ToolNotFoundError(name)
                
                # Validate arguments
                validate_tool_arguments(name, arguments)
                
                # Extract arguments
                query = arguments.get("query")
                max_results = arguments.get("max_results", self.config.search.max_results)
                
                # Check if search client is initialized
                if not self.search_client:
                    raise SearchError("Search client not initialized")
                
                # Perform search
                logger.info(f"Executing search: query='{query}', max_results={max_results}")
                results = await self.search_client.search(query, max_results)
                
                # Format results
                if not results:
                    result_text = f"No results found for query: {query}"
                else:
                    result_text = f"Found {len(results)} results for: {query}\n\n"
                    for result in results:
                        result_text += f"[{result.position}] {result.title}\n"
                        result_text += f"URL: {result.url}\n"
                        result_text += f"Snippet: {result.snippet}\n\n"
                
                logger.info(f"Search completed: {len(results)} results returned")
                
                return [
                    TextContent(
                        type="text",
                        text=result_text
                    )
                ]
                
            except MCPError as e:
                # Log and re-raise MCP errors
                logger.error(f"MCP error in tool call: {e.message}")
                error_text = safe_error_message(e, self.config.server.debug_mode)
                return [
                    TextContent(
                        type="text",
                        text=f"Error: {error_text}"
                    )
                ]
            except Exception as e:
                # Handle unexpected errors
                logger.error(f"Unexpected error in tool call: {e}", exc_info=True)
                error_text = safe_error_message(e, self.config.server.debug_mode)
                return [
                    TextContent(
                        type="text",
                        text=f"Error: {error_text}"
                    )
                ]
    
    async def run(self):
        """Run the MCP server using stdio transport."""
        logger.info("Starting WebSearcher MCP Server...")
        
        # Initialize async resources
        await self.initialize()
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("Server running on stdio transport")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        finally:
            await self.cleanup()


async def main():
    """Main entry point for the server."""
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return
    
    # Setup logging
    setup_logging(config.server.log_level, config.server.debug_mode)
    logger.info("Configuration loaded successfully")
    
    # Create and run server
    server = WebSearcherServer(config)
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        logger.info("WebSearcher MCP Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
