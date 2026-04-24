"""HTML parser integration tests.

File I/O, real-world multi-feature scenarios, reports, statistics,
and complex parsing scenarios.
"""

import pytest


# =====================================================================
# File Operations
# =====================================================================

@pytest.mark.integration
class TestParseFile:
    def test_finds_features(self, html_parser, create_html_file):
        filepath = create_html_file("<main><video src='v.mp4'></video></main>")
        features = html_parser.parse_file(str(filepath))
        assert "html5semantic" in features
        assert "video" in features


# =====================================================================
# Real-World Scenarios
# =====================================================================

@pytest.mark.integration
class TestRealWorldScenarios:
    def test_landing_page(self, parse_features):
        html = """
        <!DOCTYPE html><html lang="en"><head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="theme-color" content="#4285f4">
            <link rel="icon" type="image/svg+xml" href="favicon.svg">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preload" href="hero.jpg" as="image">
        </head><body>
            <header><nav aria-label="Main"><a href="/">Home</a></nav></header>
            <main>
                <picture>
                    <source srcset="hero.avif" type="image/avif">
                    <source srcset="hero.webp" type="image/webp">
                    <img src="hero.jpg" alt="Hero" loading="lazy">
                </picture>
                <video controls><source src="i.mp4" type="video/mp4">
                    <track kind="captions" src="c.vtt" srclang="en">
                </video>
            </main>
            <footer><a href="/privacy" rel="noopener">Privacy</a></footer>
        </body></html>
        """
        features = parse_features(html)
        assert "viewport-units" in features
        assert "meta-theme-color" in features
        assert "link-icon-svg" in features
        assert "html5semantic" in features
        assert "wai-aria" in features
        assert "picture" in features
        assert "avif" in features
        assert "webp" in features
        assert "loading-lazy-attr" in features
        assert "video" in features
        assert "webvtt" in features
        assert "rel-noopener" in features
