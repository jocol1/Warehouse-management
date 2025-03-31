import asyncio
import websockets
from PyQt5.QtCore import QThread, pyqtSignal

class WebSocketClient(QThread):
    # Gửi dữ liệu hình ảnh về cho PyQt
    image_received = pyqtSignal(bytes)

    def __init__(self, uri):
        super().__init__()
        self.uri = uri

    async def connect_to_websocket(self):
        async with websockets.connect(self.uri) as websocket:
            while True:
                data = await websocket.recv()
                self.image_received.emit(data)

    def run(self):
        asyncio.run(self.connect_to_websocket())
