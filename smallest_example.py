import asyncio
import websockets
uri = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"
async def listen_to_websocket():
  async with websockets.connect(uri) as websocket:
    while True:
      try:
        message = await websocket.recv()
        print(message)
      except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")
        break
      except Exception as e:
        print(f"Error: {e}")

asyncio.get_event_loop().run_until_complete(listen_to_websocket())
