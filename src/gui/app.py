"""
Cross Guard Application Entry Point
Main application launcher for the GUI using CustomTkinter with drag-and-drop support.
"""

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

from .theme import configure_ctk_theme, COLORS, WINDOW
from .main_window import MainWindow


class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    """CustomTkinter root window with TkinterDnD drag-and-drop support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


def main():
    """Launch the Cross Guard application."""
    # Configure theme
    configure_ctk_theme()

    # Create window
    app = CTkDnD()
    app.title("Cross Guard - Browser Compatibility Checker")
    app.geometry(f"{WINDOW['default_width']}x{WINDOW['default_height']}")
    app.minsize(WINDOW['min_width'], WINDOW['min_height'])
    app.configure(fg_color=COLORS['bg_dark'])

    # Center on screen
    x = (app.winfo_screenwidth() // 2) - (WINDOW['default_width'] // 2)
    y = (app.winfo_screenheight() // 2) - (WINDOW['default_height'] // 2)
    app.geometry(f"+{x}+{y}")

    # Create and pack main window content
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Run
    app.mainloop()


if __name__ == '__main__':
    main()
