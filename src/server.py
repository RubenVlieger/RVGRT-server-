import asyncio
import logging
import time
from typing import Dict

from fastapi import WebSocket
from .models import PlayerStateData, ServerStateBroadcast

logger = logging.getLogger("rvgrt.server")
logger.setLevel(logging.INFO)

MAX_PLAYERS = 16
TIMEOUT_SECONDS = 2.0


class GameServer:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.player_states: Dict[int, PlayerStateData] = {}
        self.player_names: Dict[int, str] = {}
        self.last_seen: Dict[int, float] = {}
        self._next_id = 1

    async def connect(self, websocket: WebSocket) -> int | None:
        if len(self.active_connections) >= MAX_PLAYERS:
            return None

        await websocket.accept()
        client_id = self._next_id
        self._next_id += 1

        self.active_connections[client_id] = websocket
        self.last_seen[client_id] = time.time()
        logger.info(
            f"Client {client_id} connected. Total: {len(self.active_connections)}"
        )
        return client_id

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.player_states:
            del self.player_states[client_id]
        if client_id in self.last_seen:
            del self.last_seen[client_id]
        logger.info(f"Client {client_id} disconnected.")

    def update_state(self, client_id: int, state: PlayerStateData):
        self.player_states[client_id] = state
        self.last_seen[client_id] = time.time()

    async def broadcast(self, message: str, exclude: int | None = None):
        for cid, ws in list(self.active_connections.items()):
            if exclude and cid == exclude:
                continue
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {cid}: {e}")

    async def game_loop(self):
        logger.info("Starting 60Hz game loop")
        while True:
            await asyncio.sleep(1.0 / 60.0)

            now = time.time()
            to_remove = []

            # 1. Cull timed out players
            for cid, last in self.last_seen.items():
                if now - last > TIMEOUT_SECONDS:
                    logger.warning(f"Client {cid} timed out.")
                    to_remove.append(cid)

            for cid in to_remove:
                self.disconnect(cid)

            # 2. Broadcast state
            if self.player_states:
                # We dump directly to string for fast broadcasting
                broadcast_msg = ServerStateBroadcast(players=self.player_states)
                await self.broadcast(broadcast_msg.model_dump_json())


server = GameServer()
