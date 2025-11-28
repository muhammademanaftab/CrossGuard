#!/usr/bin/env python3
"""
Cross Guard GUI Launcher
Run this file to start the Cross Guard application.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from gui.app import main

if __name__ == '__main__':
    main()
