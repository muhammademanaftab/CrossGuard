"""Integration tests for CSS parser.

Tests real-world CSS scenarios and complete stylesheets.
"""

import pytest


class TestRealWorldCSS:
    """Tests for real-world CSS patterns."""

    def test_modern_css_reset(self, parse_css):
        """Test modern CSS reset."""
        css = """
        *, *::before, *::after {
            box-sizing: border-box;
        }
        * {
            margin: 0;
            padding: 0;
        }
        html {
            scroll-behavior: smooth;
        }
        body {
            min-height: 100vh;
            line-height: 1.5;
        }
        img, picture, video, canvas, svg {
            display: block;
            max-width: 100%;
        }
        """
        features = parse_css(css)
        assert 'css3-boxsizing' in features
        assert 'css-gencontent' in features
        assert 'css-scroll-behavior' in features
        assert 'viewport-units' in features

    def test_flexbox_card_layout(self, parse_css):
        """Test flexbox card layout pattern."""
        css = """
        .cards {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .card {
            flex: 1 1 300px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        .card:hover {
            transform: translateY(-4px);
        }
        """
        features = parse_css(css)
        assert 'flexbox' in features
        assert 'flexbox-gap' in features
        assert 'border-radius' in features
        assert 'css-boxshadow' in features
        assert 'css-transitions' in features
        assert 'transforms2d' in features

    def test_css_grid_layout(self, parse_css):
        """Test CSS Grid layout pattern."""
        css = """
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }
        .grid-item {
            grid-column: span 2;
        }
        @media (max-width: 768px) {
            .grid-item {
                grid-column: span 1;
            }
        }
        """
        features = parse_css(css)
        assert 'css-grid' in features
        assert 'flexbox-gap' in features
        assert 'rem' in features
        assert 'css-mediaqueries' in features

    def test_dark_mode_support(self, parse_css):
        """Test dark mode support pattern."""
        css = """
        :root {
            --bg-color: #ffffff;
            --text-color: #1a1a1a;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #1a1a1a;
                --text-color: #ffffff;
            }
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        """
        features = parse_css(css)
        assert 'css-variables' in features
        assert 'prefers-color-scheme' in features

    def test_modern_button_styles(self, parse_css):
        """Test modern button styles."""
        css = """
        .button {
            appearance: none;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .button:focus-visible {
            outline: 2px solid #667eea;
            outline-offset: 2px;
        }
        """
        features = parse_css(css)
        assert 'css-appearance' in features
        assert 'rem' in features
        assert 'border-radius' in features
        assert 'css-gradients' in features
        assert 'css3-cursors' in features
        assert 'css-transitions' in features
        assert 'user-select-none' in features
        assert 'transforms2d' in features
        assert 'css-boxshadow' in features
        assert 'css-focus-visible' in features

    def test_responsive_typography(self, parse_css):
        """Test responsive typography with clamp."""
        css = """
        html {
            font-size: clamp(1rem, 0.5rem + 1vw, 1.25rem);
        }
        h1 {
            font-size: clamp(2rem, 5vw, 4rem);
            line-height: 1.1;
        }
        .readable {
            max-width: 65ch;
            margin-inline: auto;
        }
        """
        features = parse_css(css)
        assert 'css-math-functions' in features
        assert 'rem' in features
        assert 'viewport-units' in features
        assert 'ch-unit' in features
        assert 'css-logical-props' in features

    def test_container_queries_pattern(self, parse_css):
        """Test container queries pattern."""
        css = """
        .card-container {
            container-type: inline-size;
            container-name: card;
        }
        @container card (min-width: 400px) {
            .card {
                display: flex;
                gap: 20px;
            }
            .card-image {
                width: 40cqi;
            }
        }
        """
        features = parse_css(css)
        assert 'css-container-queries' in features
        assert 'flexbox' in features
        assert 'flexbox-gap' in features
        assert 'css-container-query-units' in features

    def test_scroll_snap_gallery(self, parse_css):
        """Test scroll snap gallery pattern."""
        css = """
        .gallery {
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            scroll-behavior: smooth;
            overscroll-behavior-x: contain;
        }
        .gallery-item {
            flex: 0 0 100%;
            scroll-snap-align: start;
        }
        """
        features = parse_css(css)
        assert 'flexbox' in features
        assert 'css-snappoints' in features
        assert 'css-scroll-behavior' in features
        assert 'css-overscroll-behavior' in features

    def test_animation_keyframes(self, parse_css):
        """Test animation with keyframes."""
        css = """
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .animate-in {
            animation: fadeInUp 0.5s ease-out forwards;
        }
        @media (prefers-reduced-motion: reduce) {
            .animate-in {
                animation: none;
            }
        }
        """
        features = parse_css(css)
        assert 'css-animation' in features
        assert 'css-opacity' in features
        assert 'transforms2d' in features
        assert 'prefers-reduced-motion' in features

    def test_glassmorphism_effect(self, parse_css):
        """Test glassmorphism effect pattern."""
        css = """
        .glass {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
        }
        """
        features = parse_css(css)
        assert 'css3-colors' in features
        assert 'css-backdrop-filter' in features
        assert 'border-radius' in features

    def test_css_layers_pattern(self, parse_css):
        """Test CSS Cascade Layers pattern."""
        css = """
        @layer reset, base, components, utilities;

        @layer reset {
            *, *::before, *::after {
                box-sizing: border-box;
                margin: 0;
            }
        }

        @layer base {
            body {
                font-family: system-ui, sans-serif;
            }
        }
        """
        features = parse_css(css)
        assert 'css-cascade-layers' in features
        assert 'css3-boxsizing' in features
        assert 'css-gencontent' in features
        assert 'font-family-system-ui' in features
