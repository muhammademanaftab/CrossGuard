"""Dark theme config -- charcoal + cyan, GitHub-inspired."""

COLORS = {
    # Backgrounds (darkest to lightest)
    'bg_darkest': '#0d1117',    # GitHub-style darkest (window bg)
    'bg_dark': '#161b22',       # Main background
    'bg_medium': '#21262d',     # Cards/panels
    'bg_light': '#30363d',      # Borders/hover states
    'bg_elevated': '#1c2128',   # Elevated surfaces (modals, dropdowns)

    # Accent (cyan/teal)
    'accent': '#58a6ff',        # Primary cyan accent
    'accent_bright': '#79c0ff', # Hover/highlight state
    'accent_dim': '#388bfd',    # Pressed/active state
    'accent_muted': '#1a3a5c',   # Muted accent (no alpha)
    'accent_glow': '#152d47',    # Glow effect (no alpha)

    # Legacy aliases
    'primary': '#58a6ff',
    'primary_dark': '#388bfd',
    'primary_light': '#79c0ff',

    # Text
    'text_primary': '#f0f6fc',   # Bright white (main text)
    'text_secondary': '#c9d1d9', # Light gray (secondary text)
    'text_muted': '#8b949e',     # Gray (dimmed text)
    'text_disabled': '#6e7681',  # Dark gray (disabled)
    'text_link': '#58a6ff',      # Link color (cyan)

    # Status
    'success': '#3fb950',        # Green - supported/success
    'success_dark': '#238636',   # Dark green (hover)
    'success_muted': '#1a3d24',   # Muted green (no alpha)

    'warning': '#d29922',        # Amber - partial/warning
    'warning_dark': '#9e6a03',   # Dark amber (hover)
    'warning_muted': '#3d3314',   # Muted amber (no alpha)

    'danger': '#f85149',         # Red - unsupported/error
    'danger_dark': '#da3633',    # Dark red (hover)
    'danger_muted': '#4a1e1c',    # Muted red (no alpha)

    'info': '#58a6ff',           # Cyan - info
    'info_dark': '#388bfd',      # Dark cyan

    # Borders
    'border': '#30363d',         # Default border (subtle)
    'border_light': '#3d444d',   # Light border
    'border_focus': '#58a6ff',   # Focus border (accent)
    'border_muted': '#21262d',   # Very subtle border

    # Interactive
    'input_bg': '#0d1117',       # Input background (darkest)
    'hover_bg': '#30363d',       # Hover state background
    'selected_bg': '#388bfd',    # Selected item background
    'active_bg': '#1f6feb',      # Active/pressed background

    # Drop zone
    'drop_zone_normal': '#161b22',
    'drop_zone_hover': '#1c2128',
    'drop_zone_active': '#0d419d',
    'drop_zone_border': '#30363d',
    'drop_zone_border_active': '#58a6ff',

    # File type badges
    'html_color': '#e34c26',     # HTML orange
    'css_color': '#264de4',      # CSS blue
    'js_color': '#f7df1e',       # JS yellow

    # Sidebar
    'sidebar_bg': '#0d1117',
    'sidebar_active': '#1a3a5c',       # Active item background (blended color, no alpha)
    'sidebar_hover': '#21262d',
    'sidebar_indicator': '#58a6ff',

    # Table
    'table_header_bg': '#161b22',
    'table_row_even': '#0d1117',
    'table_row_odd': '#161b22',
    'table_row_hover': '#21262d',
    'table_row_selected': '#1a3552',  # Selected row (no alpha)

    # Card surfaces
    'card_bg': '#21262d',            # Card background (same as bg_medium)
    'surface': '#30363d',            # Surface elements inside cards (same as bg_light)
}

FONTS = {
    'family': 'SF Pro Display',  # falls back gracefully on non-macOS
    'family_mono': 'SF Mono',
    'size_xs': 10,
    'size_small': 11,
    'size_normal': 12,
    'size_medium': 13,
    'size_large': 14,
    'size_title': 18,
    'size_header': 22,
    'size_display': 28,
}

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
    'xxl': 32,
    '3xl': 48,
}

RADIUS = {
    'xs': 2,
    'sm': 4,
    'md': 6,
    'lg': 8,
    'xl': 12,
    'xxl': 16,
    'full': 9999,
}

ANIMATION = {  # milliseconds
    'instant': 50,
    'fast': 150,
    'normal': 250,
    'slow': 400,
    'progress': 600,
}

WINDOW = {
    'min_width': 1000,
    'min_height': 700,
    'default_width': 1200,
    'default_height': 800,
}

SIDEBAR = {
    'width_collapsed': 56,
    'width_expanded': 200,
    'icon_size': 20,
}

ICONS = {
    # Navigation
    'files': '\u2630',           # ☰ Trigram - hamburger menu (3 lines)
    'project': '\u25A3',         # ▣ Square with inner square (project/folder)
    'results': '\u25CF',         # ● Black circle (simple, distinct)
    'settings': '\u2699',        # ⚙ Gear
    'help': '?',                 # Simple question mark

    # File types
    'html': '\u25B6',            # ▶ Play triangle
    'css': '\u25C6',             # ◆ Black diamond
    'js': '\u2605',              # ★ Black star
    'file': '\u25A0',            # ■ Black square

    # Actions
    'add': '\u002B',             # Plus
    'remove': '\u2212',          # Minus
    'delete': '\u2715',          # Multiplication X
    'check': '\u2713',           # Check mark
    'close': '\u2715',           # X
    'refresh': '\u21BB',         # Clockwise arrow
    'export': '\u2913',          # Downwards arrow
    'upload': '\u2912',          # Upwards arrow

    # Status
    'success': '\u2713',         # Check mark
    'warning': '\u26A0',         # Warning sign
    'error': '\u2715',           # X
    'info': '\u2139',            # Information source

    # Arrows
    'arrow_left': '\u2190',      # Left arrow
    'arrow_right': '\u2192',     # Right arrow
    'arrow_up': '\u2191',        # Up arrow
    'arrow_down': '\u2193',      # Down arrow
    'chevron_right': '\u203A',   # Single right guillemet
    'chevron_down': '\u2304',    # Down arrowhead

    # Misc
    'folder': '\U0001F4C1',
    'folder_open': '\U0001F4C2',
    'search': '\u2315',
    'menu': '\u2630',
    'dot': '\u2022',
    'diamond': '\u25C6',
    'scan': '\U0001F50D',
    'tree': '\u251C',
    'project': '\U0001F4C1',

    # History / Stats
    'history': '\u25D4',
    'statistics': '\u2261',
    'clock': '\u25F4',
    'trash': '\u2716',
    'clear': '\u2718',

    # Bookmarks / Tags
    'bookmark': '\u2606',
    'bookmark_filled': '\u2605',
    'tag': '\u2302',
    'tag_add': '\u271A',
    'edit': '\u270E',
    'note': '\u2261',
}

LOGO_SIMPLE = "\u25C7 CROSS GUARD"
LOGO_COMPACT = "CG"

LOGO_ASCII = """
 \u2554\u2550\u2557\u252C\u2500\u252C\u250C\u2500\u2510\u250C\u2500\u2510\u250C\u2500\u2510  \u2554\u2550\u2557\u252C \u252C\u250C\u2500\u2510\u252C\u2500\u252C\u250C\u252C\u2510
 \u2551  \u251C\u252C\u2518\u2502 \u2502\u251C\u2500\u2524\u251C\u2500\u2524  \u2551 \u2551\u2502 \u2502\u251C\u2500\u2524\u251C\u252C\u2518 \u2502\u2502
 \u255A\u2550\u255D\u2534\u2514\u2500\u2514\u2500\u2518\u2514\u2500\u2518\u2514\u2500\u2518  \u255A\u2550\u255D\u2514\u2500\u2518\u2534 \u2534\u2534\u2514\u2500\u2500\u2534\u2518
"""

def get_color(name: str, fallback: str = '#ffffff') -> str:
    """Look up a color by name, with fallback."""
    return COLORS.get(name, fallback)


def get_score_color(score: float) -> str:
    """Map a 0-100 score to a green/yellow/red color."""
    if score >= 90:
        return COLORS['success']
    elif score >= 75:
        return '#56d364'  # Light green
    elif score >= 60:
        return COLORS['warning']
    elif score >= 40:
        return '#f0883e'  # Orange
    else:
        return COLORS['danger']


def get_grade_color(grade: str) -> str:
    """Map a letter grade (A-F) to a color."""
    grade_colors = {
        'A': COLORS['success'],
        'B': '#56d364',
        'C': COLORS['warning'],
        'D': '#f0883e',
        'F': COLORS['danger'],
    }
    return grade_colors.get(grade.upper(), COLORS['text_muted'])


def get_file_type_color(file_type: str) -> str:
    """Get the brand color for a file type (HTML orange, CSS blue, JS yellow)."""
    type_colors = {
        'html': COLORS['html_color'],
        'htm': COLORS['html_color'],
        'css': COLORS['css_color'],
        'js': COLORS['js_color'],
        'jsx': COLORS['js_color'],
        'ts': COLORS['js_color'],
        'tsx': COLORS['js_color'],
        'mjs': COLORS['js_color'],
        'javascript': COLORS['js_color'],
    }
    return type_colors.get(file_type.lower(), COLORS['text_muted'])


def configure_ctk_theme():
    """Set up CTk dark mode. Call once at startup."""
    import customtkinter as ctk

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def enable_smooth_scrolling(scrollable_frame, scroll_speed: float = 1.0):
    """Fix CTkScrollableFrame's broken trackpad/mousewheel scrolling."""
    import platform

    try:
        canvas = scrollable_frame._parent_canvas
    except AttributeError:
        # Fallback: dig through children for the canvas
        for child in scrollable_frame.winfo_children():
            if child.winfo_class() == 'Canvas':
                canvas = child
                break
        else:
            return

    def _on_mousewheel(event):
        # macOS and Windows both use event.delta but in different scales
        if platform.system() == 'Darwin':
            delta = -event.delta / 120 * scroll_speed
        elif platform.system() == 'Windows':
            delta = -event.delta / 120 * scroll_speed
        else:
            delta = -1 if event.num == 4 else 1
        canvas.yview_scroll(int(delta), "units")

    def _on_linux_scroll(event):
        """Linux uses Button-4/5 instead of MouseWheel."""
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

    def _bind_to_widget(widget):
        """Recursively bind scroll events to a widget tree."""
        if platform.system() == 'Linux':
            widget.bind('<Button-4>', _on_linux_scroll, add='+')
            widget.bind('<Button-5>', _on_linux_scroll, add='+')
        else:
            widget.bind('<MouseWheel>', _on_mousewheel, add='+')

        for child in widget.winfo_children():
            _bind_to_widget(child)

    def _bind_all_children(event=None):
        _bind_to_widget(scrollable_frame)

    _bind_to_widget(scrollable_frame)

    # Canvas itself also needs bindings
    if platform.system() == 'Linux':
        canvas.bind('<Button-4>', _on_linux_scroll, add='+')
        canvas.bind('<Button-5>', _on_linux_scroll, add='+')
    else:
        canvas.bind('<MouseWheel>', _on_mousewheel, add='+')

    # Re-bind when new children appear
    scrollable_frame.bind('<Configure>', _bind_all_children, add='+')
