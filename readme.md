# RVGRT Server

This is the multiplayer backend for RVGRT (RubenVlieger GPU Ray Tracer), a custom path-traced voxel engine. It handles up to 16 concurrent players connecting via WebSockets to stream their character state, broadcast chat messages, and sync block updates.

The server currently operates at a 60Hz tick rate, running entirely in an asynchronous Python loop (FastAPI + Websockets) to keep latency low.

## Features

- **60Hz Game Loop:** Consolidates and broadcasts player states 60 times a second.
- **Low Latency Comm:** Instant broadcasting for chat and block updates.
- **Admin Logger:** A built-in Django service accessible at `/admin/` to view recent logs and send server-wide announcements to players.
- **Containerized:** Managed seamlessly with Docker, Compose, and `uv` for blistering-fast dependency installation.

## Development Setup

1. Make sure you have Docker installed.
2. Clone this repo.
3. Bring it up:
   ```bash
   docker-compose up --build
   ```

The FastAPI game server will listen on port `8000` (WebSocket endpoint at `/ws`), while the Django logging/chat admin interface will be available on port `8001`.

## Production Deployment

This server is designed to be easily deployed to a VPS (e.g., Oracle Cloud) using Docker Compose. Security considerations for production have been mapped out to ensure internal endpoints remain protected and that WebSocket communication is robust. For step-by-step instructions on a complete Oracle deployment including domain setup and HTTPS, refer to [`deploy_oracle_example.txt`](deploy_oracle_example.txt).
