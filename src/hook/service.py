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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("hook.log")
    ]
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
        
        # Start IPC listener thread (to receive commands from backend)
        # Wait, IPCClient is designed for sending. We need bidirectional.
        # The current IPCClient implementation is simple. 
        # We need to listen on the socket we connected with.
        
        # Let's modify the flow:
        # 1. Connect to Backend.
        # 2. Start a thread to read from that socket (Backend -> Hook).
        # 3. Main thread runs the Windows Message Loop (Hook -> Backend).
        
        if self.connected:
            read_thread = threading.Thread(target=self._read_loop, daemon=True)
            read_thread.start()
        
        # Install hook
        self.win32.install_hook(self._on_key_event)
        
        # Pump messages (Blocking)
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
        except Exception as e:
            logger.error(f"Could not connect to backend: {e}")
            # Retry logic could go here
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
            
            logger.info(f"Replacing: backspaces={backspaces}, text='{text}'")
            
            # Execute replacement
            # We need to be careful not to trigger our own hook recursively?
            # The hook callback checks for injected keys? 
            # Win32 LL hooks usually see injected keys with a flag, but we might just ignore them in logic.
            # Or we temporarily disable hook?
            
            # Simple approach: Just do it.
            self.win32.send_backspace(backspaces)
            self.win32.send_text(text)
            
            # Handle cursor offset (move left)
            if cursor_offset > 0:
                for _ in range(cursor_offset):
                    self.win32._send_key(0x25) # VK_LEFT

    def _on_key_event(self, vk_code, scan_code, is_down):
        """
        Callback from Win32 Hook.
        Returns True to block key, False to pass.
        """
        if not self.connected:
            return False

        # We only care about KeyDown for typing
        # But we might need Up for modifiers?
        # For simple expansion, Down is enough.
        
        if not is_down:
            return False

        # Map VK to char (simplified)
        # In a real app, we need `ToUnicode` or `MapVirtualKey`.
        # For now, let's assume standard US layout or pass raw VK to backend.
        # Passing raw VK is safer, let backend decide.
        # But our backend expects chars.
        
        # Let's do a basic mapping for A-Z, 0-9, Space, Enter, Backspace
        char = self._vk_to_char(vk_code)
        is_backspace = (vk_code == 0x08)
        
        if char or is_backspace:
            msg = {
                "type": MSG_KEY_EVENT,
                "payload": {
                    "char": char,
                    "is_backspace": is_backspace,
                    "vk_code": vk_code
                }
            }
            self.client.send(msg)
            
        return False # Never block for now, unless we are in "Expansion Mode" (advanced)

    def _vk_to_char(self, vk):
        # Very basic mapping
        if 65 <= vk <= 90: # A-Z
            # Check shift? Too complex for this snippet. Assume lowercase for now.
            return chr(vk + 32) 
        if 48 <= vk <= 57: # 0-9
            return chr(vk)
        if vk == 0x20: return " "
        if vk == 0x0D: return "\n"
        return None

if __name__ == "__main__":
    service = HookService()
    service.start()
