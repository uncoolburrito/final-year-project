import logging
import sys
import time
import threading

from src.common.ipc import IPCClient, MSG_KEY_EVENT, MSG_REPLACE_TEXT, MSG_PING
from src.common.constants import IPC_PORT
from src.hook.win32_input import Win32Input

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("hook.log"),
    ],
)
logger = logging.getLogger("HookService")


class HookService:
    def __init__(self):
        self.client = IPCClient(IPC_PORT)
        self.win32 = Win32Input()
        self.connected = False
        self.lock = threading.Lock()

    def start(self):
        logger.info("Starting Hook Service...")

        # Connect to backend
        self._connect_to_backend()

        # Start reader thread to receive messages from backend
        if self.connected:
            read_thread = threading.Thread(target=self._read_loop, daemon=True)
            read_thread.start()

        # Install keyboard hook
        ok = self.win32.install_hook(self._on_key_event)
        if not ok:
            logger.error("Could not install keyboard hook, exiting hook service.")
            return

        # Pump Windows messages (blocking)
        try:
            self.win32.pump_messages()
        except KeyboardInterrupt:
            pass
        finally:
            self.win32.uninstall_hook()
            self.client.close()

    def _connect_to_backend(self):
        try:
            self.client.connect()
            self.connected = True
            logger.info("Connected to backend IPC server.")
        except Exception as e:
            logger.error(f"Could not connect to backend: {e}")
            self.connected = False

    def _read_loop(self):
        """Reads messages from the backend."""
        from src.common.ipc import recv_msg

        while self.connected:
            msg = recv_msg(self.client.sock)
            if msg:
                self._handle_backend_message(msg)
            else:
                logger.error("Connection to backend lost.")
                self.connected = False
                break

    def _handle_backend_message(self, msg):
        msg_type = msg.get("type")
        payload = msg.get("payload", {})

        if msg_type == MSG_REPLACE_TEXT:
            backspaces = payload.get("backspaces", 0)
            text = payload.get("text", "")
            cursor_offset = payload.get("cursor_offset", 0)

            logger.info(
                f"Replacing: backspaces={backspaces}, text='{text}', cursor_offset={cursor_offset}"
            )

            # 1) Delete abbreviation + trigger
            self.win32.send_backspace(backspaces)

            # 2) Clipboard-based insertion for reliability
            try:
                import pyperclip

                old_clip = None
                try:
                    old_clip = pyperclip.paste()
                except Exception:
                    old_clip = None

                pyperclip.copy(text)
                logger.info("Clipboard set; sending Ctrl+V")
                self.win32.send_ctrl_v()

                # Optional: restore clipboard
                if old_clip is not None:
                    try:
                        pyperclip.copy(old_clip)
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"Clipboard-based insertion failed: {e}")
                # Fallback to direct key injection
                self.win32.send_text(text)

            # 3) Cursor offset (move left if needed)
            if cursor_offset > 0:
                for _ in range(cursor_offset):
                    # VK_LEFT = 0x25
                    self.win32._send_key(0x25)

    def _on_key_event(self, vk_code, scan_code, is_down):
        """
        Callback from Win32 Hook.
        Returns True to block key, False to pass.
        """
        # Log at INFO so we can see keystrokes in the terminal
        logger.info(
            f"Hook key event: vk={vk_code} scan={scan_code} is_down={is_down}"
        )

        if not self.connected:
            return False

        # Only care about key-down events
        if not is_down:
            return False

        # Map VK to char (very basic) or mark as backspace
        char = self._vk_to_char(vk_code)
        is_backspace = (vk_code == 0x08)  # VK_BACK

        if char is not None or is_backspace:
            msg = {
                "type": MSG_KEY_EVENT,
                "payload": {
                    "char": char,
                    "is_backspace": is_backspace,
                    "vk_code": vk_code,
                },
            }
            try:
                self.client.send(msg)
            except Exception as e:
                logger.error(f"Failed to send key event to backend: {e}")

        # We never block keys in v1
        return False

    def _vk_to_char(self, vk):
        # Basic mapping for A-Z, 0-9, space, enter
        if 65 <= vk <= 90:  # A-Z
            return chr(vk + 32)  # assume lowercase
        if 48 <= vk <= 57:  # 0-9
            return chr(vk)
        if vk == 0x20:  # Space
            return " "
        if vk == 0x0D:  # Enter
            return "\n"
        return None


if __name__ == "__main__":
    service = HookService()
    service.start()
