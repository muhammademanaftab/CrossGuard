"""Dark theme config -- charcoal + cyan, GitHub-inspired."""

COLORS = {
    'bg_darkest': '#0d1117',
    'bg_dark': '#161b22',
    'bg_medium': '#21262d',
    'bg_light': '#30363d',
    'bg_elevated': '#1c2128',

    'accent': '#58a6ff',
    'accent_bright': '#79c0ff',
    'accent_dim': '#388bfd',
    'accent_muted': '#1a3a5c',
    'accent_glow': '#152d47',

    'primary': '#58a6ff',
    'primary_dark': '#388bfd',
    'primary_light': '#79c0ff',

    'text_primary': '#f0f6fc',
    'text_secondary': '#c9d1d9',
    'text_muted': '#8b949e',
    'text_disabled': '#6e7681',
    'text_link': '#58a6ff',

    'success': '#3fb950',
    'success_dark': '#238636',
    'success_muted': '#1a3d24',

    'warning': '#d29922',
    'warning_dark': '#9e6a03',
    'warning_muted': '#3d3314',

    'danger': '#f85149',
    'danger_dark': '#da3633',
    'danger_muted': '#4a1e1c',

    'info': '#58a6ff',
    'info_dark': '#388bfd',

    'border': '#30363d',
    'border_light': '#3d444d',
    'border_focus': '#58a6ff',
    'border_muted': '#21262d',

    'input_bg': '#0d1117',
    'hover_bg': '#30363d',
    'selected_bg': '#388bfd',
    'active_bg': '#1f6feb',

    'drop_zone_normal': '#161b22',
    'drop_zone_hover': '#1c2128',
    'drop_zone_active': '#0d419d',
    'drop_zone_border': '#30363d',
    'drop_zone_border_active': '#58a6ff',

    'html_color': '#e34c26',
    'css_color': '#264de4',
    'js_color': '#f7df1e',

    'sidebar_bg': '#0d1117',
    'sidebar_active': '#1a3a5c',
    'sidebar_hover': '#21262d',
    'sidebar_indicator': '#58a6ff',

    'table_header_bg': '#161b22',
    'table_row_even': '#0d1117',
    'table_row_odd': '#161b22',
    'table_row_hover': '#21262d',
    'table_row_selected': '#1a3552',

    'card_bg': '#21262d',
    'surface': '#30363d',
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
    'files': '\u2630',
    'project': '\u25A3',
    'results': '\u25CF',
    'settings': '\u2699',
    'help': '?',

    'html': '\u25B6',
    'css': '\u25C6',
    'js': '\u2605',
    'file': '\u25A0',

    'add': '\u002B',
    'remove': '\u2212',
    'delete': '\u2715',
    'check': '\u2713',
    'close': '\u2715',
    'refresh': '\u21BB',
    'export': '\u2913',
    'upload': '\u2912',

    'success': '\u2713',
    'warning': '\u26A0',
    'error': '\u2715',
    'info': '\u2139',

    'arrow_left': '\u2190',
    'arrow_right': '\u2192',
    'arrow_up': '\u2191',
    'arrow_down': '\u2193',
    'chevron_right': '\u203A',
    'chevron_down': '\u2304',

    'folder': '\U0001F4C1',
    'folder_open': '\U0001F4C2',
    'search': '\u2315',
    'menu': '\u2630',
    'dot': '\u2022',
    'diamond': '\u25C6',
    'scan': '\U0001F50D',
    'tree': '\u251C',
    'project': '\U0001F4C1',

    'history': '\u25D4',
    'statistics': '\u2261',
    'clock': '\u25F4',
    'trash': '\u2716',
    'clear': '\u2718',

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
    return COLORS.get(name, fallback)


def get_score_color(score: float) -> str:
    if score >= 90:
        return COLORS['success']
    elif score >= 75:
        return '#56d364'
    elif score >= 60:
        return COLORS['warning']
    elif score >= 40:
        return '#f0883e'
    else:
        return COLORS['danger']


def get_grade_color(grade: str) -> str:
    grade_colors = {
        'A': COLORS['success'],
        'B': '#56d364',
        'C': COLORS['warning'],
        'D': '#f0883e',
        'F': COLORS['danger'],
    }
    return grade_colors.get(grade.upper(), COLORS['text_muted'])


def get_file_type_color(file_type: str) -> str:
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
        # Linux uses Button-4/5 instead of MouseWheel
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

    def _bind_to_widget(widget):
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

    if platform.system() == 'Linux':
        canvas.bind('<Button-4>', _on_linux_scroll, add='+')
        canvas.bind('<Button-5>', _on_linux_scroll, add='+')
    else:
        canvas.bind('<MouseWheel>', _on_mousewheel, add='+')

    scrollable_frame.bind('<Configure>', _bind_all_children, add='+')
