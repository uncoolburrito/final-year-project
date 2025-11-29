import logging
import sys
import time
from src.common.ipc import IPCServer, MSG_KEY_EVENT, MSG_REPLACE_TEXT, MSG_PING, MSG_PONG
from src.common.constants import BACKEND_PORT
from src.engine.store import Store
from src.engine.core import ExpansionEngine

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("backend.log")
    ]
)
logger = logging.getLogger("Backend")

class BackendService:
    def __init__(self):
        self.store = Store()
        self.engine = ExpansionEngine(self.store)
        self.server = IPCServer(BACKEND_PORT, self.handle_message)

    def start(self):
        logger.info("Starting Backend Service...")
        self.server.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        logger.info("Stopping Backend Service...")
        self.server.stop()

    def handle_message(self, msg: dict, sock):
        msg_type = msg.get("type")
        
        if msg_type == MSG_PING:
            logger.debug("Received PING")
            # Respond with PONG if needed, or just ack
            
        elif msg_type == MSG_KEY_EVENT:
            payload = msg.get("payload", {})
            char = payload.get("char")
            is_backspace = payload.get("is_backspace", False)
            
            if char or is_backspace:
                result = self.engine.process_key(char, is_backspace)
                
                if result:
                    backspaces, text, cursor_offset = result
                    response = {
                        "type": MSG_REPLACE_TEXT,
                        "payload": {
                            "backspaces": backspaces,
                            "text": text,
                            "cursor_offset": cursor_offset
                        }
                    }
                    # Send back to the Hook Service (which is the client here)
                    # Wait, the Hook Service is the CLIENT connecting to US (Server).
                    # So we send on the same socket.
                    from src.common.ipc import send_msg
                    send_msg(sock, response)

if __name__ == "__main__":
    service = BackendService()
    service.start()
