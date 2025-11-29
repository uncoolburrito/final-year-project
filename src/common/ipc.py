import socket
import json
import struct
import threading
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# Protocol: 4 bytes length (big endian) + JSON body
MSG_KEY_EVENT = "key_event"
MSG_REPLACE_TEXT = "replace_text"
MSG_PING = "ping"
MSG_PONG = "pong"

def send_msg(sock: socket.socket, msg: dict):
    """Encodes and sends a JSON message."""
    try:
        body = json.dumps(msg).encode('utf-8')
        length = len(body)
        sock.sendall(struct.pack('>I', length) + body)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise

def recv_msg(sock: socket.socket) -> Optional[dict]:
    """Receives and decodes a JSON message."""
    try:
        # Read length
        raw_len = recvall(sock, 4)
        if not raw_len:
            return None
        length = struct.unpack('>I', raw_len)[0]
        
        # Read body
        body = recvall(sock, length)
        if not body:
            return None
        return json.loads(body.decode('utf-8'))
    except Exception as e:
        logger.error(f"Error receiving message: {e}")
        return None

def recvall(sock: socket.socket, n: int) -> Optional[bytes]:
    """Helper to receive exactly n bytes."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

class IPCServer:
    def __init__(self, port: int, handler: Callable[[dict, socket.socket], None]):
        self.port = port
        self.handler = handler
        self.running = False
        self.server_sock = None
        self.thread = None

    def start(self):
        self.running = True
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('127.0.0.1', self.port))
        self.server_sock.listen(5)
        self.thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.thread.start()
        logger.info(f"IPC Server started on port {self.port}")

    def _accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_sock.accept()
                logger.debug(f"Client connected: {addr}")
                client_thread = threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True)
                client_thread.start()
            except OSError:
                break

    def _handle_client(self, sock: socket.socket):
        try:
            while self.running:
                msg = recv_msg(sock)
                if msg is None:
                    break
                self.handler(msg, sock)
        finally:
            sock.close()

    def stop(self):
        self.running = False
        if self.server_sock:
            self.server_sock.close()

class IPCClient:
    def __init__(self, port: int):
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', self.port))
        logger.info(f"Connected to IPC Server on port {self.port}")

    def send(self, msg: dict):
        if self.sock:
            send_msg(self.sock, msg)

    def close(self):
        if self.sock:
            self.sock.close()
