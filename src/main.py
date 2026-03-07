import contextlib
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
import asyncio

from .models import ClientMessage, ServerInitMessage, PlayerStateMessage, ChatMessage, BlockUpdateMessage
from .server import server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rvgrt.main")

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the 60hz broadcast loop on startup
    task = asyncio.create_task(server.game_loop())
    yield
    # Cleanup on shutdown
    task.cancel()

app = FastAPI(title="RVGRT Multiplayer Server", lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok", "players": len(server.active_connections)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = await server.connect(websocket)
    
    if client_id is None:
        await websocket.close(code=1013, reason="Server full (Max 16 players)")
        return
        
    try:
        # Send init message
        init_msg = ServerInitMessage(client_id=client_id, max_players=16)
        await websocket.send_text(init_msg.model_dump_json())
        
        while True:
            # We expect JSON payloads containing a "type"
            data = await websocket.receive_text()
            
            try:
                # Use Pydantic to parse/validate JSON and discriminate by 'type'
                # Note Pydantic 2.x method:
                import json
                raw = json.loads(data)
                
                if raw.get('type') == 'state':
                    msg = PlayerStateMessage.model_validate(raw)
                    server.update_state(client_id, msg.data)
                    
                elif raw.get('type') == 'chat':
                    msg = ChatMessage.model_validate(raw)
                    # Broadcast chat to all other clients instantly
                    msg.client_id = client_id
                    await server.broadcast(msg.model_dump_json(), exclude=client_id)
                    
                elif raw.get('type') == 'block':
                    msg = BlockUpdateMessage.model_validate(raw)
                    # Broadcast block update directly
                    msg.client_id = client_id
                    await server.broadcast(msg.model_dump_json(), exclude=client_id)
                else:
                    logger.warning(f"Unknown message type received: {raw.get('type')}")
                    
            except ValidationError as e:
                logger.error(f"Schema validation error from client {client_id}: {e}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {client_id}")
                
    except WebSocketDisconnect:
        server.disconnect(client_id)
    except Exception as e:
        logger.error(f"Unexpected WS error for {client_id}: {e}")
        server.disconnect(client_id)
