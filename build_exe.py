import os
import subprocess
import sys

def build():
    print("Building Text Expander...")
    
    # Ensure requirements are installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Run PyInstaller
    subprocess.check_call(["pyinstaller", "text_expander.spec", "--clean", "--noconfirm"])
    
    print("Build complete! Check dist/TextExpander")

if __name__ == "__main__":
    build()
