import asyncio
import json
import websockets
import time


async def mock_client(client_idx: int):
    # Connect to the local dev server
    try:
        async with websockets.connect("ws://127.0.0.1:8000/ws") as websocket:
            # Wait for init
            init_msg = await websocket.recv()
            print(f"Client {client_idx} initialized: {init_msg}")

            # Wait for block_sync (may or may not arrive)
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(msg)
                if data.get("type") == "block_sync":
                    print(
                        f"Client {client_idx} received block_sync with {len(data.get('changes', []))} changes"
                    )
            except asyncio.TimeoutError:
                print(f"Client {client_idx}: no block_sync received (empty world)")

            start_time = time.time()
            frame_count = 0

            # Send initial state
            state_payload = {"type": "state", "data": {"transforms": [0.0] * 16}}

            # Send a block edit after 0.5 seconds (client 0 only)
            if client_idx == 0:
                await asyncio.sleep(0.5)
                block_payload = {
                    "type": "block",
                    "x": 100,
                    "y": 50,
                    "z": 200,
                    "mat_id": 2,
                }
                await websocket.send(json.dumps(block_payload))
                print(
                    f"Client {client_idx} sent block edit: place grass at (100, 50, 200)"
                )

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
                    msg_type = data.get("type")
                    if msg_type == "broadcast":
                        frame_count += 1
                        if client_idx == 0 and time.time() - start_time >= 1.0:
                            print(
                                f"[Client 0]: Receiving {frame_count} frames per second. Total players synced: {len(data['players'])}"
                            )
                            return
                    elif msg_type == "block":
                        print(
                            f"Client {client_idx} received block edit: ({data['x']}, {data['y']}, {data['z']}) mat_id={data['mat_id']}"
                        )
                    elif msg_type == "block_reset":
                        print(f"Client {client_idx} received block_reset notification")

            sender = asyncio.create_task(send_state())
            receiver = asyncio.create_task(receive_broadcast())

            await asyncio.gather(sender, receiver)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_idx} disconnected.")


async def main():
    print("Spawning 2 clients to test block sync...")
    await asyncio.gather(*(mock_client(i) for i in range(2)))
    print("Test complete.")


if __name__ == "__main__":
    asyncio.run(main())
