#!/usr/bin/env python3
"""CryptoGuard Desktop Application Launcher.

Launch directly from the repository root:
    python run_app.py
"""

import sys
from pathlib import Path

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.app import run

if __name__ == "__main__":
    run()
