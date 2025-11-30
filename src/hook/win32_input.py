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
VK_SPACE = 0x20
VK_RETURN = 0x0D

VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28

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
                kb_struct = ctypes.cast(
                    lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)
                ).contents
                is_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)

                # This logging used to work for you — keep it
                logger.info(
                    f"Hook key event: vk={kb_struct.vkCode} "
                    f"scan={kb_struct.scanCode} is_down={is_down}"
                )

                # Call user callback
                should_block = callback(
                    kb_struct.vkCode, kb_struct.scanCode, is_down
                )

                if should_block:
                    return 1

            return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

        self.hook_proc = HOOKPROC(low_level_handler)
        self.hook_id = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL, self.hook_proc, kernel32.GetModuleHandleW(None), 0
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

    # -------------------------
    # OUTPUT / INJECTION HELPERS
    # -------------------------

    def send_backspace(self, count=1):
        """Sends N backspaces."""
        logger.debug(f"Sending {count} backspaces via keybd_event")
        for _ in range(count):
            self._send_key(VK_BACK)

    def send_text(self, text):
        """
        Sends text by synthesizing simple keyboard events with keybd_event.
        Supports:
          - a–z / A–Z
          - 0–9
          - space
          - newline
          - underscore
        This is enough for your current snippets and avoids the flaky Unicode path.
        """
        logger.info(f"Sending text: {repr(text)}")

        for ch in text:
            vk, use_shift = self._char_to_vk(ch)
            if vk is None:
                logger.warning(f"Skipping unsupported char in send_text: {repr(ch)}")
                continue

            if use_shift:
                user32.keybd_event(VK_SHIFT, 0, 0, 0)

            # Down + up
            user32.keybd_event(vk, 0, 0, 0)
            user32.keybd_event(vk, 0, 2, 0)  # KEYEVENTF_KEYUP = 0x0002

            if use_shift:
                user32.keybd_event(VK_SHIFT, 0, 2, 0)

    def _send_key(self, vk_code):
        # Down
        user32.keybd_event(vk_code, 0, 0, 0)
        # Up
        user32.keybd_event(vk_code, 0, 2, 0)

    def _char_to_vk(self, ch):
        """
        Very simple char -> (vk_code, use_shift) mapper.
        Assumes US layout, enough for demo.
        """
        # Newline
        if ch == "\n" or ch == "\r":
            return VK_RETURN, False

        # Space
        if ch == " ":
            return VK_SPACE, False

        # Digits
        if "0" <= ch <= "9":
            return ord(ch), False  # VK_0..VK_9

        # Lowercase letters
        if "a" <= ch <= "z":
            return ord(ch.upper()), False  # VK_A..VK_Z

        # Uppercase letters
        if "A" <= ch <= "Z":
            return ord(ch), True  # same VK, but Shift

        # Underscore -> Shift + '-'
        if ch == "_":
            VK_OEM_MINUS = 0xBD
            return VK_OEM_MINUS, True

        return None, False

    def get_foreground_window_title(self):
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
