"""
Cross Guard Application Entry Point
Main application launcher for the GUI using CustomTkinter with drag-and-drop support.
"""

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from pathlib import Path
from PIL import Image, ImageTk

from .theme import configure_ctk_theme, COLORS, WINDOW
from .main_window import MainWindow

# Icon path
ICON_PATH = Path(__file__).parent / "assets" / "icon.png"
ICON_ICO_PATH = Path(__file__).parent / "assets" / "icon.ico"


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
    app.configure(fg_color=COLORS['bg_darkest'])

    # Set application icon
    try:
        if ICON_PATH.exists():
            # Load icon for window (all platforms)
            icon_image = Image.open(ICON_PATH)
            icon_photo = ImageTk.PhotoImage(icon_image)
            app.iconphoto(True, icon_photo)
            app._icon_photo = icon_photo  # Keep reference to prevent garbage collection

            # macOS dock icon (requires PyObjC)
            try:
                import platform
                if platform.system() == 'Darwin':
                    from AppKit import NSApplication, NSImage
                    ns_app = NSApplication.sharedApplication()
                    ns_image = NSImage.alloc().initWithContentsOfFile_(str(ICON_PATH))
                    if ns_image:
                        ns_app.setApplicationIconImage_(ns_image)
            except ImportError:
                pass  # PyObjC not installed, dock icon won't change
            except Exception:
                pass  # Silently fail for dock icon

        # Windows-specific icon (.ico)
        if ICON_ICO_PATH.exists():
            try:
                app.iconbitmap(str(ICON_ICO_PATH))
            except Exception:
                pass  # iconbitmap may not work on all platforms
    except Exception as e:
        print(f"Could not load icon: {e}")

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
