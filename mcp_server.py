import asyncio
import logging
import httpx
from mcp.server.fastmcp import FastMCP
from search_engine import SearchEngine
from content_extractor import ContentExtractor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Initialize FastMCP
mcp = FastMCP("Search-MCP")

# Initialize core components
search_engine = SearchEngine()
content_extractor = ContentExtractor()

# Bridge URL for notifications
BRIDGE_URL = "http://localhost:8002/event"

async def notify_bridge(event_type: str, data: dict):
    """
    Sends an event to the FastAPI bridge via HTTP POST.
    """
    async with httpx.AsyncClient() as client:
        try:
            payload = {"type": event_type, "data": data}
            await client.post(BRIDGE_URL, json=payload)
        except Exception as e:
            logger.error(f"Failed to notify bridge: {e}")

@mcp.tool()
async def search(query: str) -> str:
    """
    Search DuckDuckGo for the given query.
    """
    logger.info(f"Tool 'search' called with query: {query}")
    await notify_bridge("search_query", {"query": query, "status": "running"})
    
    try:
        results = search_engine.search(query)
        await notify_bridge("search_results", {"query": query, "results": results, "status": "completed"})
        
        if not results:
            return "No results found."
        
        # Format results for the LLM
        formatted_results = []
        for res in results:
            formatted_results.append(f"Title: {res['title']}\nURL: {res['href']}\nSnippet: {res['body']}\n")
        
        return "\n".join(formatted_results)
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        await notify_bridge("error", {"query": query, "error": error_msg})
        return error_msg

@mcp.tool()
async def fetch_content(url: str) -> str:
    """
    Extract text content from a URL.
    """
    logger.info(f"Tool 'fetch_content' called with url: {url}")
    await notify_bridge("fetch_url", {"url": url, "status": "running"})
    
    try:
        text = content_extractor.extract_text(url)
        # Truncate text for the LLM if it's too long
        if len(text) > 10000:
            text = text[:10000] + "... [truncated]"
            
        await notify_bridge("content_extracted", {"url": url, "length": len(text), "status": "completed"})
        return text
    except Exception as e:
        error_msg = f"Content extraction failed: {str(e)}"
        await notify_bridge("error", {"url": url, "error": error_msg})
        return error_msg

if __name__ == "__main__":
    mcp.run()