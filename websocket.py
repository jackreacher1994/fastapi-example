from fastapi import WebSocket

class SocketManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.close()
            self.active_connections.pop(client_id, None)

    async def receive_text(self, websocket: WebSocket) -> str:
        return await websocket.receive_text()

    async def send(self, client_id: str, message: str):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for websocket in self.active_connections.values():
            await websocket.send_text(message)

socket_manager = SocketManager()
