"""
Cross Guard - Browser Compatibility Checker.

A desktop application for checking cross-browser compatibility of web code.

Architecture:
============

This project is organized into separate frontend and backend layers:

    src/
    ├── api/          # API Layer - Interface between frontend and backend
    │   ├── service.py      # Service class for frontend to use
    │   └── schemas.py      # Data contracts/schemas
    │
    ├── gui/          # Frontend - PyQt6 GUI (depends ONLY on api/)
    │   ├── main_window.py  # Main application window
    │   ├── widgets/        # Custom UI widgets
    │   └── config.py       # GUI-specific configuration
    │
    ├── analyzer/     # Backend - Analysis engine
    │   ├── main.py         # Main analyzer coordinator
    │   ├── compatibility.py
    │   ├── scorer.py
    │   └── database.py
    │
    ├── parsers/      # Backend - Code parsers
    │   ├── html_parser.py
    │   ├── css_parser.py
    │   └── js_parser.py
    │
    └── utils/        # Shared utilities
        ├── config.py       # Shared configuration & logging
        └── exceptions.py   # Custom exceptions

Communication Flow:
    Frontend (gui/) --> API (api/) --> Backend (analyzer/, parsers/)

Multiple agents can work on frontend and backend independently:
    - Frontend developers: Only modify gui/ and use api/ interfaces
    - Backend developers: Only modify analyzer/, parsers/, and ensure api/ contracts are maintained
"""

__version__ = "1.0.0"
__author__ = "Cross Guard Team"
