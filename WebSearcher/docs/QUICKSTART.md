# WebSearcher Quick Start Guide

This guide will help you get the WebSearcher MCP server up and running in minutes.

## Step 1: Get an API Key

The easiest way to get started is with SerpAPI:

1. Go to [https://serpapi.com/](https://serpapi.com/)
2. Sign up for a free account
3. Copy your API key from the dashboard
4. Free tier includes 100 searches per month

**Alternative options:**
- **Google Custom Search**: [Get API key](https://developers.google.com/custom-search/v1/overview) (100 free searches/day)
- **Bing Web Search**: [Get API key](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api) (1000 free searches/month)

## Step 2: Install Dependencies

```bash
cd WebSearcher
pip install mcp httpx python-dotenv
```

Or use the project file:
```bash
pip install -e .
```

## Step 3: Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
SEARCH_ENGINE=serpapi
SERPAPI_KEY=your_actual_api_key_here
```

## Step 4: Test the Server

Test that the server starts correctly:

```bash
python -m src.server
```

You should see:
```
2024-01-07 10:00:00 - INFO - Configuration loaded successfully
2024-01-07 10:00:00 - INFO - WebSearcher MCP Server initialized
2024-01-07 10:00:00 - INFO - Starting WebSearcher MCP Server...
```

Press `Ctrl+C` to stop.

## Step 5: Configure Claude Desktop

### macOS

1. Open the config file:
   ```bash
   code ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Add the WebSearcher server:
   ```json
   {
     "mcpServers": {
       "websearcher": {
         "command": "python",
         "args": ["-m", "src.server"],
         "cwd": "/Users/YOUR_USERNAME/path/to/WebSearcher",
         "env": {
           "SEARCH_ENGINE": "serpapi",
           "SERPAPI_KEY": "your_actual_api_key_here"
         }
       }
     }
   }
   ```

3. Replace `/Users/YOUR_USERNAME/path/to/WebSearcher` with the actual path
4. Replace `your_actual_api_key_here` with your API key

### Windows

1. Open the config file:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. Add the WebSearcher server:
   ```json
   {
     "mcpServers": {
       "websearcher": {
         "command": "python",
         "args": ["-m", "src.server"],
         "cwd": "C:\\Users\\YOUR_USERNAME\\path\\to\\WebSearcher",
         "env": {
           "SEARCH_ENGINE": "serpapi",
           "SERPAPI_KEY": "your_actual_api_key_here"
         }
       }
     }
   }
   ```

## Step 6: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Start Claude Desktop again
3. Look for the 🔌 icon in the bottom right - it should show "websearcher" is connected

## Step 7: Try It Out!

In Claude Desktop, try these prompts:

```
Search the web for "latest Python features"
```

```
Find information about "Model Context Protocol"
```

```
What are the top news stories about AI today?
```

## Troubleshooting

### Server not showing in Claude Desktop

- Check the config file path is correct
- Verify the `cwd` path points to the WebSearcher directory
- Check Claude Desktop logs:
  - macOS: `~/Library/Logs/Claude/`
  - Windows: `%APPDATA%\Claude\logs\`

### "API key not configured" error

- Make sure your API key is set in the `env` section of the config
- Verify the API key is valid by testing at the provider's website

### "Search failed" errors

- Check your internet connection
- Verify you haven't exceeded your API quota
- Try enabling debug mode: `"DEBUG_MODE": "true"` in the env section

### Import errors

- Make sure you're in the WebSearcher directory
- Verify all dependencies are installed: `pip install mcp httpx python-dotenv`
- Try using absolute imports by installing the package: `pip install -e .`

## Next Steps

- Read the full [README.md](README.md) for more details
- Customize search settings in `.env`
- Add more search engines
- Check out the test suite: `pytest tests/`

## Getting Help

If you encounter issues:

1. Enable debug mode in your config
2. Check the logs for detailed error messages
3. Verify your API key and quota
4. Make sure all dependencies are installed

## Example Configuration (Complete)

Here's a complete working configuration for Claude Desktop:

```json
{
  "mcpServers": {
    "websearcher": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/WebSearcher",
      "env": {
        "SEARCH_ENGINE": "serpapi",
        "SERPAPI_KEY": "your_serpapi_key",
        "MAX_RESULTS": "10",
        "REQUEST_TIMEOUT": "30",
        "LOG_LEVEL": "INFO",
        "DEBUG_MODE": "false"
      }
    }
  }
}
```

Remember to:
- Use absolute paths
- Replace placeholder values with your actual API key
- Restart Claude Desktop after making changes
