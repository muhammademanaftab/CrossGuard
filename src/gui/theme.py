"""
Dark Blue Theme Configuration for Cross Guard GUI.

This module defines the dark blue color scheme and theme settings
for the CustomTkinter-based GUI.
"""

# =============================================================================
# Dark Blue Color Palette
# =============================================================================

COLORS = {
    # Background colors (dark to light)
    'bg_dark': '#1a1a2e',       # Darkest background (main window)
    'bg_medium': '#2b2b40',     # Medium background (cards, panels)
    'bg_light': '#3d3d5c',      # Lighter background (borders, hover)

    # Primary accent (blue)
    'primary': '#2196F3',       # Main blue accent
    'primary_dark': '#1976D2',  # Blue hover/pressed
    'primary_light': '#64B5F6', # Light blue highlights

    # Text colors
    'text_primary': '#ffffff',  # Main text (white)
    'text_secondary': '#e0e0e0', # Secondary text
    'text_muted': '#888888',    # Muted/placeholder text

    # Status colors
    'success': '#4CAF50',       # Green (supported)
    'success_dark': '#388E3C',  # Dark green
    'warning': '#FF9800',       # Orange (partial)
    'warning_dark': '#F57C00',  # Dark orange
    'danger': '#F44336',        # Red (unsupported)
    'danger_dark': '#D32F2F',   # Dark red

    # Border colors
    'border': '#3d3d5c',        # Default border
    'border_light': '#4a4a6a',  # Light border
    'border_focus': '#2196F3',  # Focus border (blue)

    # Special backgrounds
    'input_bg': '#252538',      # Input/entry background
    'hover_bg': '#363650',      # Hover state background
    'selected_bg': '#1976D2',   # Selected item background

    # Drop zone states
    'drop_zone_normal': '#252538',
    'drop_zone_hover': '#2b3d4f',
    'drop_zone_active': '#1e3a5f',
}

# =============================================================================
# Font Settings
# =============================================================================

FONTS = {
    'family': 'Segoe UI',       # Primary font (falls back to system)
    'size_small': 11,
    'size_normal': 12,
    'size_medium': 13,
    'size_large': 14,
    'size_title': 18,
    'size_header': 22,
}

# =============================================================================
# Spacing
# =============================================================================

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
    'xxl': 32,
}

# =============================================================================
# Border Radius
# =============================================================================

RADIUS = {
    'sm': 4,
    'md': 6,
    'lg': 8,
    'xl': 12,
}

# =============================================================================
# Animation Durations (milliseconds)
# =============================================================================

ANIMATION = {
    'fast': 150,
    'normal': 300,
    'slow': 500,
    'progress': 800,
}

# =============================================================================
# Window Settings
# =============================================================================

WINDOW = {
    'min_width': 1000,
    'min_height': 850,
    'default_width': 1100,
    'default_height': 900,
}

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
    elif score >= 70:
        return '#8BC34A'  # Light green
    elif score >= 50:
        return COLORS['warning']
    elif score >= 30:
        return '#FF5722'  # Deep orange
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
        'B': '#8BC34A',
        'C': COLORS['warning'],
        'D': '#FF5722',
        'F': COLORS['danger'],
    }
    return grade_colors.get(grade.upper(), COLORS['text_muted'])


def configure_ctk_theme():
    """Configure CustomTkinter appearance settings.

    Call this at application startup to set up the dark blue theme.
    """
    import customtkinter as ctk

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
