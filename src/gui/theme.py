"""
Cross Guard Theme Configuration - Professional Charcoal + Cyan Design.

This module defines the modern dark theme with charcoal backgrounds
and cyan accents, inspired by VS Code and GitHub's dark mode.
"""

# =============================================================================
# Charcoal + Cyan Color Palette (GitHub-inspired)
# =============================================================================

COLORS = {
    # Backgrounds (charcoal gradient - darkest to lightest)
    'bg_darkest': '#0d1117',    # GitHub-style darkest (window bg)
    'bg_dark': '#161b22',       # Main background
    'bg_medium': '#21262d',     # Cards/panels
    'bg_light': '#30363d',      # Borders/hover states
    'bg_elevated': '#1c2128',   # Elevated surfaces (modals, dropdowns)

    # Accent colors (Cyan/Teal)
    'accent': '#58a6ff',        # Primary cyan accent
    'accent_bright': '#79c0ff', # Hover/highlight state
    'accent_dim': '#388bfd',    # Pressed/active state
    'accent_muted': '#1a3a5c',   # Muted accent (no alpha)
    'accent_glow': '#152d47',    # Glow effect (no alpha)

    # Legacy mappings for compatibility
    'primary': '#58a6ff',
    'primary_dark': '#388bfd',
    'primary_light': '#79c0ff',

    # Text colors
    'text_primary': '#f0f6fc',   # Bright white (main text)
    'text_secondary': '#c9d1d9', # Light gray (secondary text)
    'text_muted': '#8b949e',     # Gray (dimmed text)
    'text_disabled': '#6e7681',  # Dark gray (disabled)
    'text_link': '#58a6ff',      # Link color (cyan)

    # Status colors (semantic)
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

    # Border colors
    'border': '#30363d',         # Default border (subtle)
    'border_light': '#3d444d',   # Light border
    'border_focus': '#58a6ff',   # Focus border (accent)
    'border_muted': '#21262d',   # Very subtle border

    # Interactive states
    'input_bg': '#0d1117',       # Input background (darkest)
    'hover_bg': '#30363d',       # Hover state background
    'selected_bg': '#388bfd',    # Selected item background
    'active_bg': '#1f6feb',      # Active/pressed background

    # Drop zone states
    'drop_zone_normal': '#161b22',
    'drop_zone_hover': '#1c2128',
    'drop_zone_active': '#0d419d',
    'drop_zone_border': '#30363d',
    'drop_zone_border_active': '#58a6ff',

    # File type colors (semantic)
    'html_color': '#e34c26',     # HTML orange
    'css_color': '#264de4',      # CSS blue
    'js_color': '#f7df1e',       # JS yellow

    # Sidebar specific
    'sidebar_bg': '#0d1117',
    'sidebar_active': '#1a3a5c',       # Active item background (blended color, no alpha)
    'sidebar_hover': '#21262d',
    'sidebar_indicator': '#58a6ff',

    # Table specific
    'table_header_bg': '#161b22',
    'table_row_even': '#0d1117',
    'table_row_odd': '#161b22',
    'table_row_hover': '#21262d',
    'table_row_selected': '#1a3552',  # Selected row (no alpha)
}

# =============================================================================
# Font Settings
# =============================================================================

FONTS = {
    'family': 'SF Pro Display',  # macOS system font (falls back gracefully)
    'family_mono': 'SF Mono',    # Monospace font
    'size_xs': 10,
    'size_small': 11,
    'size_normal': 12,
    'size_medium': 13,
    'size_large': 14,
    'size_title': 18,
    'size_header': 22,
    'size_display': 28,
}

# =============================================================================
# Spacing System (8px base grid)
# =============================================================================

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
    'xxl': 32,
    '3xl': 48,
}

# =============================================================================
# Border Radius
# =============================================================================

RADIUS = {
    'xs': 2,
    'sm': 4,
    'md': 6,
    'lg': 8,
    'xl': 12,
    'xxl': 16,
    'full': 9999,
}

# =============================================================================
# Animation Durations (milliseconds)
# =============================================================================

ANIMATION = {
    'instant': 50,
    'fast': 150,
    'normal': 250,
    'slow': 400,
    'progress': 600,
}

# =============================================================================
# Window Settings
# =============================================================================

WINDOW = {
    'min_width': 1000,
    'min_height': 700,
    'default_width': 1200,
    'default_height': 800,
}

# =============================================================================
# Sidebar Settings
# =============================================================================

SIDEBAR = {
    'width_collapsed': 56,
    'width_expanded': 200,
    'icon_size': 20,
}

# =============================================================================
# Icon Definitions (Unicode symbols)
# =============================================================================

ICONS = {
    # Navigation (simple ASCII-compatible symbols that render everywhere)
    'files': '\u2630',           # ☰ Trigram - hamburger menu (3 lines)
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

    # Navigation arrows
    'arrow_left': '\u2190',      # Left arrow
    'arrow_right': '\u2192',     # Right arrow
    'arrow_up': '\u2191',        # Up arrow
    'arrow_down': '\u2193',      # Down arrow
    'chevron_right': '\u203A',   # Single right guillemet
    'chevron_down': '\u2304',    # Down arrowhead

    # Misc
    'folder': '\u2302',          # House
    'search': '\u2315',          # Telephone recorder
    'menu': '\u2630',            # Trigram for heaven
    'dot': '\u2022',             # Bullet
    'diamond': '\u25C6',         # Black diamond
}

# =============================================================================
# Logo (ASCII Art options)
# =============================================================================

LOGO_SIMPLE = "\u25C7 CROSS GUARD"  # Diamond + text
LOGO_COMPACT = "CG"

LOGO_ASCII = """
 \u2554\u2550\u2557\u252C\u2500\u252C\u250C\u2500\u2510\u250C\u2500\u2510\u250C\u2500\u2510  \u2554\u2550\u2557\u252C \u252C\u250C\u2500\u2510\u252C\u2500\u252C\u250C\u252C\u2510
 \u2551  \u251C\u252C\u2518\u2502 \u2502\u251C\u2500\u2524\u251C\u2500\u2524  \u2551 \u2551\u2502 \u2502\u251C\u2500\u2524\u251C\u252C\u2518 \u2502\u2502
 \u255A\u2550\u255D\u2534\u2514\u2500\u2514\u2500\u2518\u2514\u2500\u2518\u2514\u2500\u2518  \u255A\u2550\u255D\u2514\u2500\u2518\u2534 \u2534\u2534\u2514\u2500\u2500\u2534\u2518
"""

# =============================================================================
# Helper Functions
# =============================================================================

def get_color(name: str, fallback: str = '#ffffff') -> str:
    """Get a color value by name.

    Args:
        name: Color name from COLORS dict
        fallback: Default color if name not found

    Returns:
        Hex color string
    """
    return COLORS.get(name, fallback)


def get_score_color(score: float) -> str:
    """Get color based on compatibility score.

    Args:
        score: Score percentage (0-100)

    Returns:
        Hex color string
    """
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
    """Get color based on grade letter.

    Args:
        grade: Grade letter (A, B, C, D, F)

    Returns:
        Hex color string
    """
    grade_colors = {
        'A': COLORS['success'],
        'B': '#56d364',
        'C': COLORS['warning'],
        'D': '#f0883e',
        'F': COLORS['danger'],
    }
    return grade_colors.get(grade.upper(), COLORS['text_muted'])


def get_file_type_color(file_type: str) -> str:
    """Get color based on file type.

    Args:
        file_type: File type ('html', 'css', 'js', 'javascript')

    Returns:
        Hex color string
    """
    type_colors = {
        'html': COLORS['html_color'],
        'htm': COLORS['html_color'],
        'css': COLORS['css_color'],
        'js': COLORS['js_color'],
        'javascript': COLORS['js_color'],
    }
    return type_colors.get(file_type.lower(), COLORS['text_muted'])


def configure_ctk_theme():
    """Configure CustomTkinter appearance settings.

    Call this at application startup to set up the dark theme.
    """
    import customtkinter as ctk

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
