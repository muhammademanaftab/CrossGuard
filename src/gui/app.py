"""GUI application launcher."""

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from pathlib import Path
from PIL import Image, ImageTk

from .theme import configure_ctk_theme, COLORS, WINDOW
from .main_window import MainWindow

ICON_PATH = Path(__file__).parent / "assets" / "icon.png"
ICON_ICO_PATH = Path(__file__).parent / "assets" / "icon.ico"


class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    """CTk root window with drag-and-drop mixed in."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


def main():
    """Launch the Cross Guard application."""
    configure_ctk_theme()

    app = CTkDnD()
    app.title("Cross Guard - Browser Compatibility Checker")
    app.geometry(f"{WINDOW['default_width']}x{WINDOW['default_height']}")
    app.minsize(WINDOW['min_width'], WINDOW['min_height'])
    app.configure(fg_color=COLORS['bg_darkest'])

    try:
        if ICON_PATH.exists():
            icon_image = Image.open(ICON_PATH)
            icon_photo = ImageTk.PhotoImage(icon_image)
            app.iconphoto(True, icon_photo)
            app._icon_photo = icon_photo  # prevent GC from killing the photo

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

        # .ico for Windows
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
