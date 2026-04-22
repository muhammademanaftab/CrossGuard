"""
Cross Guard Frontend - CustomTkinter GUI Application.

This package contains the graphical user interface for Cross Guard.
It communicates with the backend ONLY through the API layer (src.api).

IMPORTANT: This package should NOT import directly from src.analyzer
or src.parsers. All backend communication should go through src.api.

Usage:
    from src.gui import main
    main()  # Launches the GUI application

    # Or directly use the MainWindow
    from src.gui import MainWindow
"""

from .main_window import MainWindow
from .app import main

__all__ = ['MainWindow', 'main']
