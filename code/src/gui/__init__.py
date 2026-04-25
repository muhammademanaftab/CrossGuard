"""Cross Guard GUI -- all backend access goes through src.api, never directly to parsers or analyzer."""

from .main_window import MainWindow
from .app import main

__all__ = ['MainWindow', 'main']
