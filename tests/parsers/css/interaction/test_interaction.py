"""Tests for CSS Interaction features.

Tests features: css-resize, pointer-events, user-select-none, css-appearance,
                css-caret-color, css-touch-action, css-scroll-behavior,
                css3-cursors, css3-cursors-grab, css3-cursors-newer,
                css-overscroll-behavior, css-scrollbar, css-snappoints

Note: css-snappoints patterns include: scroll-snap-type, scroll-snap-align
scroll-snap-stop is not in the parser patterns.
"""

import pytest


class TestResize:
    """Tests for resize property detection."""

    def test_resize_both(self, parse_and_check):
        """Test resize: both detection."""
        css = "textarea { resize: both; }"
        assert parse_and_check(css, 'css-resize')

    def test_resize_horizontal(self, parse_and_check):
        """Test resize: horizontal detection."""
        css = ".element { resize: horizontal; }"
        assert parse_and_check(css, 'css-resize')

    def test_resize_vertical(self, parse_and_check):
        """Test resize: vertical detection."""
        css = ".element { resize: vertical; }"
        assert parse_and_check(css, 'css-resize')

    def test_resize_none(self, parse_and_check):
        """Test resize: none detection."""
        css = "textarea { resize: none; }"
        assert parse_and_check(css, 'css-resize')


class TestPointerEvents:
    """Tests for pointer-events detection."""

    def test_pointer_events_none(self, parse_and_check):
        """Test pointer-events: none detection."""
        css = ".disabled { pointer-events: none; }"
        assert parse_and_check(css, 'pointer-events')

    def test_pointer_events_auto(self, parse_and_check):
        """Test pointer-events: auto detection."""
        css = ".element { pointer-events: auto; }"
        assert parse_and_check(css, 'pointer-events')


class TestUserSelect:
    """Tests for user-select detection."""

    def test_user_select_none(self, parse_and_check):
        """Test user-select: none detection."""
        css = ".no-select { user-select: none; }"
        assert parse_and_check(css, 'user-select-none')

    def test_webkit_user_select(self, parse_and_check):
        """Test -webkit-user-select detection."""
        css = ".no-select { -webkit-user-select: none; }"
        assert parse_and_check(css, 'user-select-none')


class TestAppearance:
    """Tests for appearance property detection."""

    def test_appearance_none(self, parse_and_check):
        """Test appearance: none detection."""
        css = "button { appearance: none; }"
        assert parse_and_check(css, 'css-appearance')

    def test_webkit_appearance(self, parse_and_check):
        """Test -webkit-appearance detection."""
        css = "input { -webkit-appearance: none; }"
        assert parse_and_check(css, 'css-appearance')


class TestCaretColor:
    """Tests for caret-color detection."""

    def test_caret_color(self, parse_and_check):
        """Test caret-color detection."""
        css = "input { caret-color: red; }"
        assert parse_and_check(css, 'css-caret-color')

    def test_caret_color_transparent(self, parse_and_check):
        """Test caret-color: transparent detection."""
        css = "input { caret-color: transparent; }"
        assert parse_and_check(css, 'css-caret-color')


class TestTouchAction:
    """Tests for touch-action detection."""

    def test_touch_action_none(self, parse_and_check):
        """Test touch-action: none detection."""
        css = ".no-touch { touch-action: none; }"
        assert parse_and_check(css, 'css-touch-action')

    def test_touch_action_pan_x(self, parse_and_check):
        """Test touch-action: pan-x detection."""
        css = ".horizontal-scroll { touch-action: pan-x; }"
        assert parse_and_check(css, 'css-touch-action')

    def test_touch_action_manipulation(self, parse_and_check):
        """Test touch-action: manipulation detection."""
        css = ".element { touch-action: manipulation; }"
        assert parse_and_check(css, 'css-touch-action')


class TestScrollBehavior:
    """Tests for scroll-behavior detection."""

    def test_scroll_behavior_smooth(self, parse_and_check):
        """Test scroll-behavior: smooth detection."""
        css = "html { scroll-behavior: smooth; }"
        assert parse_and_check(css, 'css-scroll-behavior')

    def test_scroll_behavior_auto(self, parse_and_check):
        """Test scroll-behavior: auto detection."""
        css = ".element { scroll-behavior: auto; }"
        assert parse_and_check(css, 'css-scroll-behavior')


class TestCursors:
    """Tests for cursor property detection."""

    def test_cursor_pointer(self, parse_and_check):
        """Test cursor: pointer detection."""
        css = ".clickable { cursor: pointer; }"
        assert parse_and_check(css, 'css3-cursors')

    def test_cursor_default(self, parse_and_check):
        """Test cursor: default detection."""
        css = ".element { cursor: default; }"
        assert parse_and_check(css, 'css3-cursors')


class TestCursorsGrab:
    """Tests for grab/grabbing cursors detection."""

    def test_cursor_grab(self, parse_and_check):
        """Test cursor: grab detection."""
        css = ".draggable { cursor: grab; }"
        assert parse_and_check(css, 'css3-cursors-grab')

    def test_cursor_grabbing(self, parse_and_check):
        """Test cursor: grabbing detection."""
        css = ".dragging { cursor: grabbing; }"
        assert parse_and_check(css, 'css3-cursors-grab')


class TestCursorsNewer:
    """Tests for zoom-in/zoom-out cursors detection."""

    def test_cursor_zoom_in(self, parse_and_check):
        """Test cursor: zoom-in detection."""
        css = ".zoomable { cursor: zoom-in; }"
        assert parse_and_check(css, 'css3-cursors-newer')

    def test_cursor_zoom_out(self, parse_and_check):
        """Test cursor: zoom-out detection."""
        css = ".zoomable { cursor: zoom-out; }"
        assert parse_and_check(css, 'css3-cursors-newer')


class TestOverscrollBehavior:
    """Tests for overscroll-behavior detection."""

    def test_overscroll_behavior(self, parse_and_check):
        """Test overscroll-behavior detection."""
        css = ".modal { overscroll-behavior: contain; }"
        assert parse_and_check(css, 'css-overscroll-behavior')

    def test_overscroll_behavior_none(self, parse_and_check):
        """Test overscroll-behavior: none detection."""
        css = ".element { overscroll-behavior: none; }"
        assert parse_and_check(css, 'css-overscroll-behavior')


class TestScrollbar:
    """Tests for scrollbar styling detection."""

    def test_scrollbar_width(self, parse_and_check):
        """Test scrollbar-width detection."""
        css = ".element { scrollbar-width: thin; }"
        assert parse_and_check(css, 'css-scrollbar')

    def test_scrollbar_color(self, parse_and_check):
        """Test scrollbar-color detection."""
        css = ".element { scrollbar-color: gray lightgray; }"
        assert parse_and_check(css, 'css-scrollbar')


class TestScrollSnap:
    """Tests for scroll snap detection."""

    def test_scroll_snap_type(self, parse_and_check):
        """Test scroll-snap-type detection."""
        css = ".container { scroll-snap-type: x mandatory; }"
        assert parse_and_check(css, 'css-snappoints')

    def test_scroll_snap_align(self, parse_and_check):
        """Test scroll-snap-align detection."""
        css = ".item { scroll-snap-align: start; }"
        assert parse_and_check(css, 'css-snappoints')
