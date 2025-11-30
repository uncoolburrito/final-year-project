import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger(__name__)

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# ----- Win32 constants -----
WH_KEYBOARD_LL = 13

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

VK_BACK = 0x08
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt

# ----- Structs -----
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]


# ----- Win32 API signatures -----
# LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam);
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)

user32.SetWindowsHookExW.argtypes = (
    ctypes.c_int,           # idHook
    LowLevelKeyboardProc,   # lpfn
    wintypes.HINSTANCE,     # hMod
    wintypes.DWORD,         # dwThreadId
)
user32.SetWindowsHookExW.restype = wintypes.HHOOK

user32.CallNextHookEx.argtypes = (
    wintypes.HHOOK,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM,
)
user32.CallNextHookEx.restype = ctypes.c_long

user32.UnhookWindowsHookEx.argtypes = (wintypes.HHOOK,)
user32.UnhookWindowsHookEx.restype = wintypes.BOOL

user32.GetMessageW.argtypes = (
    ctypes.POINTER(wintypes.MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT,
)
user32.GetMessageW.restype = wintypes.BOOL

user32.TranslateMessage.argtypes = (ctypes.POINTER(wintypes.MSG),)
user32.DispatchMessageW.argtypes = (ctypes.POINTER(wintypes.MSG),)

user32.SendInput.argtypes = (wintypes.UINT, ctypes.c_void_p, ctypes.c_int)
user32.SendInput.restype = wintypes.UINT


class Win32Input:
    def __init__(self):
        self.hook_id = None
        self.hook_proc = None  # keep reference to avoid GC

    def install_hook(self, callback):
        """
        Installs the low-level keyboard hook.
        callback: function(vk_code, scan_code, is_down) -> bool (True to block, False to pass)
        """

        @LowLevelKeyboardProc
        def low_level_handler(nCode, wParam, lParam):
            if nCode == 0:
                kb_struct = ctypes.cast(
                    lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)
                ).contents
                is_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)

                try:
                    should_block = callback(
                        kb_struct.vkCode, kb_struct.scanCode, is_down
                    )
                except Exception as e:
                    logger.exception("Error in keyboard callback: %s", e)
                    should_block = False

                if should_block:
                    # non-zero return means "eat the event"
                    return 1

            # pass to next hook
            return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

        self.hook_proc = low_level_handler

        # IMPORTANT:
        # For WH_KEYBOARD_LL, we can safely pass hMod=0 and threadId=0
        # to install a global low-level hook in this process.
        self.hook_id = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self.hook_proc,
            0,   # hMod = 0 avoids ERROR_MOD_NOT_FOUND (126) on some setups
            0,   # system-wide low-level hook
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
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def send_backspace(self, count=1):
        """Sends N backspaces."""
        for _ in range(count):
            self._send_vk_key(VK_BACK)

    def send_text(self, text: str):
        """
        Sends text using SendInput (Unicode) char by char.
        """
        for char in text:
            self._send_unicode_char(char)

    def _send_vk_key(self, vk_code: int):
        # fallback using keybd_event (deprecated but simple)
        user32.keybd_event(vk_code, 0, 0, 0)
        user32.keybd_event(vk_code, 0, 2, 0)  # KEYEVENTF_KEYUP = 0x0002

    def _send_unicode_char(self, char: str):
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

        down = INPUT(
            type=INPUT_KEYBOARD,
            ki=KEYBDINPUT(
                wVk=0,
                wScan=ord(char),
                dwFlags=KEYEVENTF_UNICODE,
                time=0,
                dwExtraInfo=0,
            ),
        )

        up = INPUT(
            type=INPUT_KEYBOARD,
            ki=KEYBDINPUT(
                wVk=0,
                wScan=ord(char),
                dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                time=0,
                dwExtraInfo=0,
            ),
        )

        user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(down))
        user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(up))

    def get_foreground_window_title(self) -> str:
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
