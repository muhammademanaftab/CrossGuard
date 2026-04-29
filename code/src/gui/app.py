"""GUI application launcher."""

import sys
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk

from .theme import configure_ctk_theme, COLORS, WINDOW
from .main_window import MainWindow

# Drag-and-drop needs a C library called tkdnd. On some Macs it can't load —
# in that case we just turn off drag-and-drop and the file picker still works.
try:
    from tkinterdnd2 import TkinterDnD
    _TKDND_IMPORT_OK = True
except Exception:
    TkinterDnD = None
    _TKDND_IMPORT_OK = False

ICON_PATH = Path(__file__).parent / "assets" / "icon.png"
ICON_ICO_PATH = Path(__file__).parent / "assets" / "icon.ico"


if _TKDND_IMPORT_OK:
    class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
        """CTk window with drag-and-drop. Falls back to a normal CTk if tkdnd fails."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except Exception as e:
                # Don't destroy the window and try again — that segfaults on Mac.
                # Just disable drag-and-drop on this window and keep going.
                self.TkdndVersion = None
                print(
                    f"Warning: tkdnd library failed to load ({e}); "
                    "drag-and-drop disabled. Use the file picker instead.",
                    file=sys.stderr,
                )
else:
    CTkDnD = ctk.CTk


def _create_app():
    if not _TKDND_IMPORT_OK:
        print(
            "Warning: tkinterdnd2 unavailable — drag-and-drop disabled. "
            "Use the file picker instead.",
            file=sys.stderr,
        )
        return ctk.CTk()
    return CTkDnD()


def main():
    configure_ctk_theme()

    app = _create_app()
    app.title("Cross Guard - Browser Compatibility Checker")
    app.geometry(f"{WINDOW['default_width']}x{WINDOW['default_height']}")
    app.minsize(WINDOW['min_width'], WINDOW['min_height'])
    app.configure(fg_color=COLORS['bg_darkest'])

    import platform
    _IS_MAC = platform.system() == 'Darwin'

    if ICON_PATH.exists():
        # Mac dock icon — the only icon a Mac user actually sees. Set first,
        # since it works even if the Tk icon code below has issues.
        if _IS_MAC:
            try:
                from AppKit import NSApplication, NSImage
                ns_app = NSApplication.sharedApplication()
                ns_image = NSImage.alloc().initWithContentsOfFile_(str(ICON_PATH))
                if ns_image:
                    ns_app.setApplicationIconImage_(ns_image)
            except ImportError:
                pass
            except Exception:
                pass

        # Title-bar icon for Linux/Windows. Skip on Mac — macOS doesn't show
        # title-bar icons, and newer Pillow+Tk combos crash on iconphoto().
        if not _IS_MAC:
            try:
                import tkinter as tk
                photo = tk.PhotoImage(file=str(ICON_PATH))
                app.iconphoto(True, photo)
                app._icon_photo = photo  # keep a reference so Tk doesn't GC it
            except Exception:
                # Fallback via Pillow if tk.PhotoImage couldn't read the file.
                try:
                    icon_image = Image.open(ICON_PATH)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    app.iconphoto(True, icon_photo)
                    app._icon_photo = icon_photo
                except Exception:
                    pass

    # Windows-style icon (ignored on Mac/Linux).
    if not _IS_MAC and ICON_ICO_PATH.exists():
        try:
            app.iconbitmap(str(ICON_ICO_PATH))
        except Exception:
            pass

    x = (app.winfo_screenwidth() // 2) - (WINDOW['default_width'] // 2)
    y = (app.winfo_screenheight() // 2) - (WINDOW['default_height'] // 2)
    app.geometry(f"+{x}+{y}")

    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    app.mainloop()


if __name__ == '__main__':
    main()
