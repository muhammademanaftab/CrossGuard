#!/usr/bin/env python3
"""
Cross Guard GUI Launcher
Run this file to start the Cross Guard application.
"""

import sys
from pathlib import Path

# Add project root to path so we can import src as a package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.app import main

if __name__ == '__main__':
    main()
