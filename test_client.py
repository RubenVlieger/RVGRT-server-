import asyncio
import json
import websockets
import time

async def mock_client(client_idx: int):
    # Connect to the local dev server
    try:
        async with websockets.connect('ws://127.0.0.1:8000/ws') as websocket:
            # Wait for init
            init_msg = await websocket.recv()
            print(f"Client {client_idx} initialized: {init_msg}")

            start_time = time.time()
            frame_count = 0
            
            # Send initial state
            state_payload = {
                "type": "state",
                "data": {
                    "transforms": [0.0] * 16 # Dummy data
                }
            }
            
            # Read and write tasks
            async def send_state():
                while True:
                    await websocket.send(json.dumps(state_payload))
                    await asyncio.sleep(1.0 / 60.0)
                    
            async def receive_broadcast():
                nonlocal frame_count
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    if data.get('type') == 'broadcast':
                        frame_count += 1
                        # Every 1 second, print stats just for client 0
                        if client_idx == 0 and time.time() - start_time >= 1.0:
                            print(f"[Client 0]: Receiving {frame_count} frames per second. Total players synced: {len(data['players'])}")
                            return # Exit after 1 second of successful ticks for test brevity
            
            sender = asyncio.create_task(send_state())
            receiver = asyncio.create_task(receive_broadcast())
            
            await asyncio.gather(sender, receiver)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_idx} disconnected.")

async def main():
    print("Spawning 16 clients...")
    await asyncio.gather(*(mock_client(i) for i in range(16)))
    print("Test complete.")

if __name__ == "__main__":
    asyncio.run(main())
