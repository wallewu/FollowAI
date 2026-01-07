"""
HTTP/SSE transport for remote MCP server.

Provides HTTP server with Server-Sent Events (SSE) for remote MCP communication.
"""

import asyncio
import json
from typing import Optional
from urllib.parse import parse_qs

from mcp.server import Server
from mcp.types import JSONRPCMessage

from .config import Config
from .logging_config import get_logger
from .search_client import create_search_client, SearchClient

logger = get_logger("http_server")


class HTTPTransport:
    """HTTP/SSE transport for MCP server."""
    
    def __init__(self, server: Server, config: Config):
        """
        Initialize HTTP transport.
        
        Args:
            server: MCP server instance
            config: Server configuration
        """
        self.server = server
        self.config = config
        self.search_client: Optional[SearchClient] = None
    
    async def initialize(self):
        """Initialize async resources."""
        try:
            self.search_client = create_search_client(self.config.search)
            logger.info("Search client initialized for HTTP transport")
        except Exception as e:
            logger.error(f"Failed to initialize search client: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources."""
        if self.search_client:
            await self.search_client.close()
            logger.info("Search client closed")
    
    async def handle_message(self, message: str) -> str:
        """
        Handle incoming JSON-RPC message.
        
        Args:
            message: JSON-RPC message string
            
        Returns:
            JSON-RPC response string
        """
        try:
            # Parse incoming message
            request = json.loads(message)
            logger.debug(f"Received request: {request}")
            
            # Process through MCP server
            # Note: This is a simplified implementation
            # Full implementation would use proper MCP message handling
            
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "tools/list":
                # Return available tools
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "web_search",
                                "description": "Search the web for information",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Search query"
                                        },
                                        "max_results": {
                                            "type": "integer",
                                            "description": "Maximum results",
                                            "default": 10
                                        }
                                    },
                                    "required": ["query"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                # Execute tool
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "web_search" and self.search_client:
                    query = arguments.get("query")
                    max_results = arguments.get("max_results", 10)
                    
                    results = await self.search_client.search(query, max_results)
                    
                    # Format results
                    result_text = f"Found {len(results)} results for: {query}\n\n"
                    for result in results:
                        result_text += f"[{result.position}] {result.title}\n"
                        result_text += f"URL: {result.url}\n"
                        result_text += f"Snippet: {result.snippet}\n\n"
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result_text
                                }
                            ]
                        }
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
            
            return json.dumps(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            return json.dumps(error_response)
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error"
                }
            }
            return json.dumps(error_response)


async def run_http_server(config: Config, host: str = "0.0.0.0", port: int = 8000):
    """
    Run HTTP server with SSE support.
    
    Args:
        config: Server configuration
        host: Host to bind to
        port: Port to listen on
    """
    try:
        # Import aiohttp here to make it optional
        import aiohttp
        from aiohttp import web
    except ImportError:
        logger.error("aiohttp is required for HTTP transport. Install with: pip install aiohttp")
        raise
    
    # Create MCP server
    mcp_server = Server("websearcher")
    transport = HTTPTransport(mcp_server, config)
    await transport.initialize()
    
    # Define HTTP handlers
    async def handle_health(request):
        """Health check endpoint."""
        return web.json_response({"status": "healthy", "service": "websearcher-mcp"})
    
    async def handle_sse(request):
        """Server-Sent Events endpoint for MCP communication."""
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        response.headers['Access-Control-Allow-Origin'] = '*'
        
        await response.prepare(request)
        
        logger.info(f"SSE connection established from {request.remote}")
        
        try:
            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                # Send keep-alive ping
                await response.write(b': ping\n\n')
        except Exception as e:
            logger.info(f"SSE connection closed: {e}")
        finally:
            await response.write_eof()
        
        return response
    
    async def handle_message(request):
        """Handle JSON-RPC messages."""
        try:
            data = await request.json()
            message = json.dumps(data)
            
            # Process message
            response_message = await transport.handle_message(message)
            
            return web.json_response(json.loads(response_message))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error"
                }
            }, status=500)
    
    async def handle_cors_preflight(request):
        """Handle CORS preflight requests."""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
    
    # Create web application
    app = web.Application()
    app.router.add_get('/health', handle_health)
    app.router.add_get('/sse', handle_sse)
    app.router.add_post('/message', handle_message)
    app.router.add_options('/message', handle_cors_preflight)
    
    # Cleanup on shutdown
    async def cleanup_on_shutdown(app):
        await transport.cleanup()
    
    app.on_cleanup.append(cleanup_on_shutdown)
    
    # Run server
    logger.info(f"Starting HTTP server on {host}:{port}")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"HTTP server running at http://{host}:{port}")
    logger.info(f"Health check: http://{host}:{port}/health")
    logger.info(f"SSE endpoint: http://{host}:{port}/sse")
    logger.info(f"Message endpoint: http://{host}:{port}/message")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down HTTP server...")
    finally:
        await runner.cleanup()
