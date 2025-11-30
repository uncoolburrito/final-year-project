# Text Expansion Engine

A system-wide text expansion engine for Windows, featuring a robust 3-process architecture and a modern Apple/Arc-inspired GUI.

## Architecture

The system is composed of three separate processes to ensure stability and isolation:

1.  **Hook Service (Process A)**:
    *   **Role**: Low-level keyboard interception.
    *   **Tech**: Python `ctypes` / Win32 API.
    *   **Responsibility**: Captures keystrokes, handles text injection (Backspace/SendInput), and communicates with the Backend.
    *   **Isolation**: If this crashes, it auto-restarts without losing user data.

2.  **Backend Engine (Process B)**:
    *   **Role**: The "Brain".
    *   **Tech**: Python.
    *   **Responsibility**: Buffers keystrokes, matches abbreviations against the database, resolves placeholders (date, cursor), and manages configuration.
    *   **IPC**: Receives `KEY_EVENT` from Hook; sends `REPLACE_TEXT` to Hook.

3.  **GUI (Process C)**:
    *   **Role**: User Interface.
    *   **Tech**: Flet (Flutter for Python).
    *   **Design**: Apple Human Interface Guidelines / Arc Browser aesthetic.
    *   **Responsibility**: Snippet management, settings, live preview.

## IPC Protocol

Communication happens via local TCP sockets (localhost).

*   **Hook -> Backend**: `{"type": "KEY_EVENT", "key_code": 65, "scan_code": 30, "is_up": false, ...}`
*   **Backend -> Hook**: `{"type": "REPLACE_TEXT", "backspaces": 3, "text": "expansion"}`

## Development

1.  Install dependencies: `pip install -r requirements.txt`
2.  Run the system: `python -m src.main`

idk why the fuck `python src/main.py` dont work 
