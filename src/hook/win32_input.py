import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger(__name__)

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

# Virtual Key Codes
VK_BACK = 0x08
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_V = 0x56

# Structs
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]


# Callback type
HOOKPROC = ctypes.CFUNCTYPE(
    ctypes.c_longlong, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)


class Win32Input:
    def __init__(self):
        self.hook_id = None
        self.hook_proc = None  # Keep reference to prevent GC

    def install_hook(self, callback):
        """
        Installs the low-level keyboard hook.
        callback: function(vk_code, scan_code, is_down) -> bool (True to block, False to pass)
        """

        def low_level_handler(nCode, wParam, lParam):
            if nCode == 0:
                kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                is_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)

                # Log a bit to see events
                logger.info(
                    f"Hook key event: vk={kb_struct.vkCode} scan={kb_struct.scanCode} is_down={is_down}"
                )

                # Call user callback
                try:
                    should_block = callback(
                        kb_struct.vkCode, kb_struct.scanCode, is_down
                    )
                except Exception as e:
                    logger.error(f"Error in hook callback: {e}")
                    should_block = False

                if should_block:
                    return 1

            return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

        self.hook_proc = HOOKPROC(low_level_handler)

        # IMPORTANT CHANGE: for WH_KEYBOARD_LL we can safely pass hMod = 0 when threadId=0
        # This avoids some ERROR_MOD_NOT_FOUND (126) issues.
        hMod = 0
        thread_id = 0

        self.hook_id = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL, self.hook_proc, hMod, thread_id
        )

        if not self.hook_id:
            err = ctypes.GetLastError()
            logger.error(f"Failed to install hook: {err}")
            return False

        logger.info("Keyboard hook installed")
        return True

    def uninstall_hook(self):
        if self.hook_id:
            user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None
            logger.info("Keyboard hook uninstalled")

    def pump_messages(self):
        """
        Runs the message loop. Blocking.
        """
        msg = wintypes.MSG()
        # Standard GetMessage loop
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def send_backspace(self, count=1):
        """Sends N backspaces."""
        for _ in range(count):
            self._send_key(VK_BACK)

    def send_text(self, text):
        """
        Sends text using SendInput (Unicode), char by char.
        """
        for char in text:
            self._send_unicode_char(char)

    def send_ctrl_v(self):
        """Send Ctrl+V (paste)."""
        # Key down CTRL
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        # Key down V
        user32.keybd_event(VK_V, 0, 0, 0)
        # Key up V
        user32.keybd_event(VK_V, 0, 2, 0)
        # Key up CTRL
        user32.keybd_event(VK_CONTROL, 0, 2, 0)

    def _send_key(self, vk_code):
        # Down
        user32.keybd_event(vk_code, 0, 0, 0)
        # Up
        user32.keybd_event(vk_code, 0, 2, 0)

    def _send_unicode_char(self, char):
        INPUT_KEYBOARD = 1
        KEYEVENTF_UNICODE = 0x0004
        KEYEVENTF_KEYUP = 0x0002

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_ulonglong),
            ]

        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = [("ki", KEYBDINPUT)]

            _anonymous_ = ("_input",)
            _fields_ = [("type", wintypes.DWORD), ("_input", _INPUT)]

        # Key down
        x = INPUT(
            type=INPUT_KEYBOARD,
            ki=KEYBDINPUT(
                wVk=0,
                wScan=ord(char),
                dwFlags=KEYEVENTF_UNICODE,
                time=0,
                dwExtraInfo=0,
            ),
        )
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

        # Key up
        y = INPUT(
            type=INPUT_KEYBOARD,
            ki=KEYBDINPUT(
                wVk=0,
                wScan=ord(char),
                dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                time=0,
                dwExtraInfo=0,
            ),
        )
        user32.SendInput(1, ctypes.byref(y), ctypes.sizeof(y))

    def get_foreground_window_title(self):
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
