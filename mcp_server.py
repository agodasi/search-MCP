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
            import json
            # Ensure data is strictly JSON serializable (fixes 500 error on bridge if results contain un-serializable types)
            safe_data = json.loads(json.dumps(data, default=str))
            payload = {"type": event_type, "data": safe_data}
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
        await notify_bridge("error", {"query": query, "error": error_msg, "source": "search"})
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
            
        await notify_bridge("content_extracted", {
            "url": url, 
            "length": len(text), 
            "content": text[:5000],  # UI用に冒頭5000文字を送信
            "status": "completed"
        })
        return text
    except Exception as e:
        error_msg = f"Content extraction failed: {str(e)}"
        await notify_bridge("error", {"url": url, "error": error_msg, "source": "fetch"})
        return error_msg

async def listen_to_bridge():
    """
    Listens for requests from the bridge (e.g., from the GUI) and acts on them.
    """
    import websockets
    import json
    ws_url = "ws://localhost:8002/ws"
    
    while True:
        try:
            async with websockets.connect(ws_url) as websocket:
                logger.info("MCP Server: Connected to Bridge WebSocket")
                async for message in websocket:
                    event = json.loads(message)
                    if event.get("type") == "fetch_url_request":
                        url = event.get("data", {}).get("url")
                        if url:
                            logger.info(f"MCP Server: Handling fetch request for {url}")
                            # 非同期でフェッチを実行
                            asyncio.create_task(fetch_content(url))
        except Exception as e:
            logger.error(f"MCP Server: Bridge connection error: {e}")
            await asyncio.sleep(5)  # Retry

if __name__ == "__main__":
    # ブリッジリスナーを別スレッドで開始（FastMCPのイベントループとの競合を避けるため）
    import threading
    
    def start_listener():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(listen_to_bridge())

    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()
    
    # FastMCPのrunを呼び出す（標準入出力を占有する）
    mcp.run()