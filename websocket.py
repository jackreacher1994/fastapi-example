from fastapi import WebSocket

class SocketManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    def get(self, client_id: str) -> WebSocket | None:
        return self.active_connections.get(client_id)

    async def receive_text(self, websocket: WebSocket) -> str:
        return await websocket.receive_text()

    async def send(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for websocket in self.active_connections.values():
            await websocket.send_text(message)

socket_manager = SocketManager()
