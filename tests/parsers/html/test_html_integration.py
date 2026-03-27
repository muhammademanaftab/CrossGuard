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

    def test_file_not_found(self, html_parser):
        with pytest.raises(FileNotFoundError):
            html_parser.parse_file("/nonexistent/path/to/file.html")


@pytest.mark.integration
class TestParseMultipleFiles:
    def test_combines_features(self, html_parser, create_temp_file):
        f1 = create_temp_file("f1.html", "<video src='v.mp4'></video>")
        f2 = create_temp_file("f2.html", "<audio src='a.mp3'></audio>")
        f3 = create_temp_file("f3.html", "<canvas></canvas>")
        result = html_parser.parse_multiple_files([str(f1), str(f2), str(f3)])
        assert "video" in result
        assert "audio" in result
        assert "canvas" in result

    def test_continues_after_missing_file(self, html_parser, create_html_file):
        valid = create_html_file("<main>Valid</main>")
        result = html_parser.parse_multiple_files([str(valid), "/nonexistent/file.html"])
        assert "html5semantic" in result


# =====================================================================
# Reports & Statistics
# =====================================================================

@pytest.mark.integration
class TestDetailedReport:
    def test_has_required_keys(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        report = html_parser.get_detailed_report()
        for key in ("total_features", "features", "elements_found", "attributes_found", "unrecognized"):
            assert key in report

    def test_feature_count(self, html_parser):
        html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        assert html_parser.get_detailed_report()["total_features"] == 2


@pytest.mark.integration
class TestStatistics:
    def test_has_required_keys(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        stats = html_parser.get_statistics()
        for key in ("total_features", "total_elements_detected", "features_list"):
            assert key in stats


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

    def test_checkout_form(self, parse_features):
        html = """
        <form id="checkout">
            <input type="email" required autocomplete="email" inputmode="email" placeholder="you@ex.com">
            <input type="tel" pattern="[0-9]{10}">
            <input type="text" required minlength="16" maxlength="16">
            <input type="month" required>
            <button type="submit">Pay</button>
        </form>
        """
        features = parse_features(html)
        assert "input-email-tel-url" in features
        assert "form-validation" in features
        assert "input-pattern" in features
        assert "input-placeholder" in features
        assert "input-minlength" in features
        assert "maxlength" in features
        assert "input-datetime" in features

