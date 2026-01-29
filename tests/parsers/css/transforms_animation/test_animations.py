"""Tests for CSS Animation features.

Tests features: css-animation, css-transitions, will-change

Note: Animation patterns only include: @keyframes, animation:, animation-name, animation-duration
Other animation properties (timing-function, delay, iteration-count, direction, fill-mode, play-state)
are not in the parser patterns.

Transition patterns only include: transition:, transition-property, transition-duration
Other transition properties (timing-function, delay) are not in the parser patterns.
"""

import pytest


class TestCSSAnimation:
    """Tests for CSS Animation detection."""

    def test_keyframes_at_rule(self, parse_and_check):
        """Test @keyframes detection."""
        css = """
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        """
        assert parse_and_check(css, 'css-animation')

    def test_keyframes_percentage(self, parse_and_check):
        """Test @keyframes with percentages."""
        css = """
        @keyframes slide {
            0% { transform: translateX(0); }
            50% { transform: translateX(50px); }
            100% { transform: translateX(100px); }
        }
        """
        assert parse_and_check(css, 'css-animation')

    def test_animation_shorthand(self, parse_and_check):
        """Test animation shorthand property."""
        css = ".element { animation: fadeIn 1s ease-in-out; }"
        assert parse_and_check(css, 'css-animation')

    def test_animation_name(self, parse_and_check):
        """Test animation-name property."""
        css = ".element { animation-name: fadeIn; }"
        assert parse_and_check(css, 'css-animation')

    def test_animation_duration(self, parse_and_check):
        """Test animation-duration property."""
        css = ".element { animation-duration: 2s; }"
        assert parse_and_check(css, 'css-animation')

    def test_multiple_animations(self, parse_and_check):
        """Test multiple animations."""
        css = ".element { animation: fadeIn 1s, slideIn 0.5s 0.5s; }"
        assert parse_and_check(css, 'css-animation')

    def test_complete_animation(self, parse_and_check):
        """Test complete animation setup with supported patterns."""
        css = """
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-30px); }
        }
        .bounce {
            animation-name: bounce;
            animation-duration: 1s;
        }
        """
        assert parse_and_check(css, 'css-animation')


class TestCSSTransitions:
    """Tests for CSS Transitions detection."""

    def test_transition_shorthand(self, parse_and_check):
        """Test transition shorthand property."""
        css = ".element { transition: all 0.3s ease; }"
        assert parse_and_check(css, 'css-transitions')

    def test_transition_property(self, parse_and_check):
        """Test transition-property property."""
        css = ".element { transition-property: opacity, transform; }"
        assert parse_and_check(css, 'css-transitions')

    def test_transition_duration(self, parse_and_check):
        """Test transition-duration property."""
        css = ".element { transition-duration: 0.3s; }"
        assert parse_and_check(css, 'css-transitions')

    def test_multiple_transitions(self, parse_and_check):
        """Test multiple transitions."""
        css = ".element { transition: opacity 0.3s, transform 0.5s ease-out; }"
        assert parse_and_check(css, 'css-transitions')

    def test_transition_none(self, parse_and_check):
        """Test transition: none."""
        css = ".element { transition: none; }"
        assert parse_and_check(css, 'css-transitions')

    def test_hover_transition(self, parse_and_check):
        """Test transition on hover."""
        css = """
        .button {
            transition: background-color 0.2s ease;
        }
        .button:hover { background-color: blue; }
        """
        assert parse_and_check(css, 'css-transitions')


class TestWillChange:
    """Tests for will-change property detection."""

    def test_will_change_transform(self, parse_and_check):
        """Test will-change: transform detection."""
        css = ".animated { will-change: transform; }"
        assert parse_and_check(css, 'will-change')

    def test_will_change_opacity(self, parse_and_check):
        """Test will-change: opacity detection."""
        css = ".fading { will-change: opacity; }"
        assert parse_and_check(css, 'will-change')

    def test_will_change_multiple(self, parse_and_check):
        """Test will-change with multiple properties."""
        css = ".element { will-change: transform, opacity; }"
        assert parse_and_check(css, 'will-change')

    def test_will_change_auto(self, parse_and_check):
        """Test will-change: auto detection."""
        css = ".element { will-change: auto; }"
        assert parse_and_check(css, 'will-change')

    def test_will_change_scroll_position(self, parse_and_check):
        """Test will-change: scroll-position detection."""
        css = ".scrollable { will-change: scroll-position; }"
        assert parse_and_check(css, 'will-change')

    def test_will_change_contents(self, parse_and_check):
        """Test will-change: contents detection."""
        css = ".dynamic { will-change: contents; }"
        assert parse_and_check(css, 'will-change')
