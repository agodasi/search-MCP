import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post('http://localhost:8002/event', json={'type': 'test', 'data': {'msg': 'hello'}})
            print(f"Response: {resp.status_code}, {resp.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())