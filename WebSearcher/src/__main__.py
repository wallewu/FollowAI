"""
Main entry point for WebSearcher MCP server.

Supports both stdio (local) and HTTP (remote) transport modes.
"""

import asyncio
import argparse
import sys

from .config import load_config
from .logging_config import setup_logging, get_logger
from .server import WebSearcherServer


async def main_stdio():
    """Run server in stdio mode (local)."""
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Failed to load configuration: {e}", file=sys.stderr)
        return 1
    
    # Setup logging
    setup_logging(config.server.log_level, config.server.debug_mode)
    logger = get_logger()
    logger.info("Configuration loaded successfully")
    
    # Create and run server
    server = WebSearcherServer(config)
    try:
        await server.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
    finally:
        logger.info("WebSearcher MCP Server stopped")


async def main_http(host: str, port: int):
    """Run server in HTTP mode (remote)."""
    from .http_server import run_http_server
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Failed to load configuration: {e}", file=sys.stderr)
        return 1
    
    # Setup logging
    setup_logging(config.server.log_level, config.server.debug_mode)
    logger = get_logger()
    logger.info("Configuration loaded successfully")
    logger.info(f"Starting in HTTP mode on {host}:{port}")
    
    try:
        await run_http_server(config, host, port)
        return 0
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="WebSearcher MCP Server - Web search tool for AI assistants"
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode: stdio (local) or http (remote). Default: stdio"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to in HTTP mode. Default: 0.0.0.0"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on in HTTP mode. Default: 8000"
    )
    
    args = parser.parse_args()
    
    if args.mode == "stdio":
        exit_code = asyncio.run(main_stdio())
    else:  # http
        exit_code = asyncio.run(main_http(args.host, args.port))
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
