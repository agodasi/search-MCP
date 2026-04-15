import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8002/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            # Send an HTTP POST to trigger a broadcast
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post('http://localhost:8002/event', json={'type': 'test', 'data': {'msg': 'hello'}})
                print("Sent POST request")

            # Wait for the broadcasted message
            message = await websocket.recv()
            print(f"Received message: {message}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())