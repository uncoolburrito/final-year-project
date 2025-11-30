# Ports
# Ports
IPC_PORT = 5055
GUI_PORT = 5001 # If needed for reverse comms, though usually GUI -> Backend is enough

# Message Types
MSG_KEY_EVENT = "KEY_EVENT"
MSG_REPLACE_TEXT = "REPLACE_TEXT"
MSG_PASTE_TEXT = "PASTE_TEXT"
MSG_RELOAD_CONFIG = "RELOAD_CONFIG"
MSG_PING = "PING"
MSG_PONG = "PONG"

# Paths
import os
APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(APP_DIR, "assets")
DATA_DIR = os.path.join(APP_DIR, "data")
