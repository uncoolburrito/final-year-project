import multiprocessing
import time
import sys
import os
import subprocess

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_backend():
    from src.engine.service import BackendService
    service = BackendService()
    service.start()

def run_hook():
    # Hook needs to be in a separate process, but ideally a separate executable or script
    # to avoid GIL issues and for stability.
    # For now, we run it as a function in a Process.
    from src.hook.service import HookService
    service = HookService()
    service.start()

def run_gui():
    # Flet needs to be main thread usually, or at least blocking.
    import flet as ft
    from src.gui.app import main
    ft.app(target=main)

if __name__ == "__main__":
    # Start Backend
    backend_process = multiprocessing.Process(target=run_backend, daemon=True)
    backend_process.start()
    
    # Wait for backend to init
    time.sleep(1)
    
    # Start Hook
    hook_process = multiprocessing.Process(target=run_hook, daemon=True)
    hook_process.start()
    
    # Start GUI (Blocking)
    try:
        run_gui()
    except KeyboardInterrupt:
        pass
    finally:
        backend_process.terminate()
        hook_process.terminate()
