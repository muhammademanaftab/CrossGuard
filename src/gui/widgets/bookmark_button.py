"""
Bookmark button widget for toggling bookmark status on analyses.

Provides visual feedback and toggle functionality for bookmarking.
"""

from typing import Callable, Optional
import customtkinter as ctk

from ..theme import COLORS, ICONS


class BookmarkButton(ctk.CTkButton):
    """Button widget for toggling bookmark status.

    Shows a star icon that toggles between filled (bookmarked)
    and outline (not bookmarked) states.
    """

    def __init__(
        self,
        master,
        is_bookmarked: bool = False,
        on_toggle: Optional[Callable[[bool], None]] = None,
        size: int = 28,
        **kwargs
    ):
        """Initialize the bookmark button.

        Args:
            master: Parent widget
            is_bookmarked: Initial bookmark state
            on_toggle: Callback when bookmark is toggled (receives new state)
            size: Button size in pixels
        """
        self._is_bookmarked = is_bookmarked
        self._on_toggle = on_toggle

        icon = ICONS.get('bookmark_filled' if is_bookmarked else 'bookmark', '\u2606')

        super().__init__(
            master,
            text=icon,
            font=ctk.CTkFont(size=14),
            width=size,
            height=size,
            fg_color="transparent",
            hover_color=COLORS['bg_light'],
            text_color=COLORS['warning'] if is_bookmarked else COLORS['text_muted'],
            command=self._handle_click,
            **kwargs
        )

        self._update_tooltip()

    @property
    def is_bookmarked(self) -> bool:
        """Get current bookmark state."""
        return self._is_bookmarked

    @is_bookmarked.setter
    def is_bookmarked(self, value: bool):
        """Set bookmark state and update appearance."""
        self._is_bookmarked = value
        self._update_appearance()

    def _handle_click(self):
        """Handle button click - toggle state."""
        self._is_bookmarked = not self._is_bookmarked
        self._update_appearance()

        if self._on_toggle:
            self._on_toggle(self._is_bookmarked)

    def _update_appearance(self):
        """Update button appearance based on state."""
        if self._is_bookmarked:
            self.configure(
                text=ICONS.get('bookmark_filled', '\u2605'),
                text_color=COLORS['warning'],
            )
        else:
            self.configure(
                text=ICONS.get('bookmark', '\u2606'),
                text_color=COLORS['text_muted'],
            )
        self._update_tooltip()

    def _update_tooltip(self):
        """Update tooltip text based on state."""
        # Note: CustomTkinter doesn't have built-in tooltips,
        # so this is a placeholder for potential tooltip implementation
        pass

    def set_state(self, is_bookmarked: bool):
        """Set bookmark state without triggering callback.

        Args:
            is_bookmarked: New bookmark state
        """
        self._is_bookmarked = is_bookmarked
        self._update_appearance()


class BookmarkIndicator(ctk.CTkLabel):
    """Small indicator showing bookmark status (read-only).

    Used in cards/lists where clicking the whole card is the action.
    """

    def __init__(
        self,
        master,
        is_bookmarked: bool = False,
        size: int = 12,
        **kwargs
    ):
        """Initialize the bookmark indicator.

        Args:
            master: Parent widget
            is_bookmarked: Whether item is bookmarked
            size: Font size
        """
        icon = ICONS.get('bookmark_filled', '\u2605') if is_bookmarked else ''
        color = COLORS['warning'] if is_bookmarked else COLORS['text_muted']

        super().__init__(
            master,
            text=icon,
            font=ctk.CTkFont(size=size),
            text_color=color,
            **kwargs
        )

        self._is_bookmarked = is_bookmarked

    def set_bookmarked(self, is_bookmarked: bool):
        """Update bookmark state."""
        self._is_bookmarked = is_bookmarked
        if is_bookmarked:
            self.configure(
                text=ICONS.get('bookmark_filled', '\u2605'),
                text_color=COLORS['warning'],
            )
        else:
            self.configure(text='')
