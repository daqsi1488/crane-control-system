"""Build script for creating Windows executable"""

import os
import sys
import subprocess
from pathlib import Path


def build_exe():
    """Build executable using PyInstaller"""
    
    print("Building Crane Simulator Pro executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "CraneSimulatorPro",
        "--icon", "src/resources/icons/app.ico",
        "--add-data", "src/resources;src/resources",
        "--add-data", "config.yaml;.",
        "--hidden-import", "PySide6",
        "--hidden-import", "pymunk",
        "--hidden-import", "numpy",
        "--hidden-import", "scipy",
        "--hidden-import", "SQLAlchemy",
        "--hidden-import", "loguru",
        "--hidden-import", "yaml",
        "--hidden-import", "websockets",
        "--hidden-import", "pyqtgraph",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        print("Executable located in: dist/CraneSimulatorPro.exe")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_exe()