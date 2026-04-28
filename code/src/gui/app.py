"""GUI application launcher."""

import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk

from .theme import configure_ctk_theme, COLORS, WINDOW
from .main_window import MainWindow

# tkdnd binaries are absent on some platforms (notably Apple Silicon + macOS Tahoe).
# We import lazily and fall back to plain CTk so the GUI launches without drag-and-drop
# instead of crashing the user out at startup.
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
        """A CustomTkinter root window that also supports tkdnd drag-and-drop."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
else:
    CTkDnD = ctk.CTk


def _create_app():
    if not _TKDND_IMPORT_OK:
        print("Warning: tkinterdnd2 unavailable — drag-and-drop disabled. Use the file picker instead.")
        return ctk.CTk()
    try:
        return CTkDnD()
    except Exception as e:
        print(f"Warning: tkdnd library failed to load ({e}); drag-and-drop disabled. Use the file picker instead.")
        return ctk.CTk()


def main():
    configure_ctk_theme()

    app = _create_app()
    app.title("Cross Guard - Browser Compatibility Checker")
    app.geometry(f"{WINDOW['default_width']}x{WINDOW['default_height']}")
    app.minsize(WINDOW['min_width'], WINDOW['min_height'])
    app.configure(fg_color=COLORS['bg_darkest'])

    try:
        if ICON_PATH.exists():
            icon_image = Image.open(ICON_PATH)
            icon_photo = ImageTk.PhotoImage(icon_image)
            app.iconphoto(True, icon_photo)
            app._icon_photo = icon_photo  # Tk will GC the photo object if we don't hold a reference

            # macOS dock icon -- needs PyObjC
            try:
                import platform
                if platform.system() == 'Darwin':
                    from AppKit import NSApplication, NSImage
                    ns_app = NSApplication.sharedApplication()
                    ns_image = NSImage.alloc().initWithContentsOfFile_(str(ICON_PATH))
                    if ns_image:
                        ns_app.setApplicationIconImage_(ns_image)
            except ImportError:
                pass
            except Exception:
                pass

        # Windows icon
        if ICON_ICO_PATH.exists():
            try:
                app.iconbitmap(str(ICON_ICO_PATH))
            except Exception:
                pass
    except Exception as e:
        print(f"Could not load icon: {e}")

    x = (app.winfo_screenwidth() // 2) - (WINDOW['default_width'] // 2)
    y = (app.winfo_screenheight() // 2) - (WINDOW['default_height'] // 2)
    app.geometry(f"+{x}+{y}")

    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    app.mainloop()


if __name__ == '__main__':
    main()
