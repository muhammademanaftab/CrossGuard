"""Toggleable bookmark button widget."""

from typing import Callable, Optional
import customtkinter as ctk

from ..theme import COLORS, ICONS


class BookmarkButton(ctk.CTkButton):
    """Star icon button that toggles between bookmarked/unbookmarked states."""

    def __init__(
        self,
        master,
        is_bookmarked: bool = False,
        on_toggle: Optional[Callable[[bool], None]] = None,
        size: int = 28,
        **kwargs
    ):
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
        return self._is_bookmarked

    @is_bookmarked.setter
    def is_bookmarked(self, value: bool):
        self._is_bookmarked = value
        self._update_appearance()

    def _handle_click(self):
        self._is_bookmarked = not self._is_bookmarked
        self._update_appearance()

        if self._on_toggle:
            self._on_toggle(self._is_bookmarked)

    def _update_appearance(self):
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
        # CustomTkinter has no built-in tooltips, placeholder for future
        pass

    def set_state(self, is_bookmarked: bool):
        """Update state without triggering the callback."""
        self._is_bookmarked = is_bookmarked
        self._update_appearance()


class BookmarkIndicator(ctk.CTkLabel):
    """Read-only bookmark icon for use in cards/lists."""

    def __init__(
        self,
        master,
        is_bookmarked: bool = False,
        size: int = 12,
        **kwargs
    ):
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
        self._is_bookmarked = is_bookmarked
        if is_bookmarked:
            self.configure(
                text=ICONS.get('bookmark_filled', '\u2605'),
                text_color=COLORS['warning'],
            )
        else:
            self.configure(text='')
