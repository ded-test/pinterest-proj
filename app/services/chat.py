from fastapi import WebSocket
from typing import List


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

"""
__init__
- active_connections - это список всех активных подключений WebSocket.
- Каждый элемент — объект WebSocket, через который мы можем посылать и получать сообщения.

connect
- accept() — мы говорим браузеру/клиенту: «Ок, теперь ты подключён, можем обмениваться сообщениями».
- append() — добавляем этого нового клиента в наш список active_connections, чтобы потом отправлять ему сообщения вместе с другими.

disconnect
- Когда клиент уходит (закрыл вкладку, ушёл из сети), мы убираем его из списка.
- Иначе сервер будет пытаться слать ему сообщения, и будет ошибка.

broadcast
- «broadcast» = рассылаем сообщение всем, кто сейчас подключен.
- Берём каждый WebSocket из active_connections и отправляем текст (send_text).
"""
