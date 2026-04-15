import asyncio
from mcp_server import search, fetch_content
from bridge import manager
import httpx

async def test_mcp_tools():
    # We need to mock the bridge notification since it uses httpx to call localhost:8002/event
    # But the bridge is already running! So we don't need to mock it.
    # We just need to make sure the bridge is reachable.
    
    print("Testing 'search' tool...")
    search_result = await search("OpenHands")
    print(f"Search Result: {search_result[:100]}...")

    print("\nTesting 'fetch_content' tool...")
    content_result = await fetch_content("https://www.google.com")
    print(f"Content Result (truncated): {content_result[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())