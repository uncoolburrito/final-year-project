import logging
import sys
import time
from src.common.ipc import IPCServer, MSG_KEY_EVENT, MSG_REPLACE_TEXT, MSG_PING, MSG_PONG
from src.common.constants import IPC_PORT
from src.engine.store import Store
from src.engine.core import ExpansionEngine

# Configure Logging (more verbose: DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("backend.log"),
    ],
)
logger = logging.getLogger("Backend")


class BackendService:
    def __init__(self):
        self.store = Store()
        self.engine = ExpansionEngine(self.store)
        self.server = IPCServer(IPC_PORT, self.handle_message)

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
        payload = msg.get("payload", {})

        logger.debug(f"Backend received IPC message: type={msg_type}, payload={payload}")

        if msg_type == MSG_PING:
            logger.debug("Received PING")

        elif msg_type == MSG_KEY_EVENT:
            char = payload.get("char")
            is_backspace = payload.get("is_backspace", False)

            logger.info(f"Backend received key event: char={repr(char)}, backspace={is_backspace}")

            # Only process keys that matter
            if char or is_backspace:
                result = self.engine.process_key(char if char else "", is_backspace)

                logger.info(f"Engine.process_key result: {result}")

                if result:
                    backspaces, text, cursor_offset = result
                    response = {
                        "type": MSG_REPLACE_TEXT,
                        "payload": {
                            "backspaces": backspaces,
                            "text": text,
                            "cursor_offset": cursor_offset,
                        },
                    }

                    from src.common.ipc import send_msg

                    logger.info(f"Sending MSG_REPLACE_TEXT to hook: {response}")
                    send_msg(sock, response)


if __name__ == "__main__":
    service = BackendService()
    service.start()
