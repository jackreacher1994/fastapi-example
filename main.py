import asyncio
import logging

from alembic import command
from alembic.config import Config
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import files
from websocket import socket_manager

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def run_alembic():
    alembic_cfg = Config("alembic.ini")
    # command.revision(alembic_cfg, autogenerate=True, message="autogenerate")
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app_: FastAPI):
    # logger.info("Running Alembic migrations on startup...")
    # await asyncio.to_thread(run_alembic)
    # logger.info("Alembic migrations complete.")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(files.router)

@app.get("/")
async def root():
    return {"message": "Hello!"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await socket_manager.connect(client_id, websocket)
    try:
        while True:
            data = await socket_manager.receive_text(websocket)
            logger.info(f"Received message from client {client_id}: {data}")
    except WebSocketDisconnect:
        socket_manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")