"""CSS parser integration tests.

File I/O, real-world multi-feature scenarios, and full pipeline tests
through statistics and reports.
"""

import pytest


@pytest.fixture
def tmp_css_file(tmp_path):
    def _create(content, filename="test.css"):
        filepath = tmp_path / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
    return _create


# =====================================================================
# File Operations
# =====================================================================

@pytest.mark.integration
class TestParseFile:
    def test_parse_valid_file(self, css_parser, tmp_css_file):
        assert "flexbox" in css_parser.parse_file(tmp_css_file("div { display: flex; }"))

    def test_file_not_found_raises(self, css_parser):
        with pytest.raises(FileNotFoundError):
            css_parser.parse_file("/nonexistent/path/file.css")


@pytest.mark.integration
class TestParseMultipleFiles:
    def test_multiple_files_combined(self, css_parser, tmp_css_file):
        f1 = tmp_css_file("div { display: flex; }", "a.css")
        f2 = tmp_css_file("div { display: grid; }", "b.css")
        features = css_parser.parse_multiple_files([f1, f2])
        assert "flexbox" in features
        assert "css-grid" in features

    def test_one_bad_file_doesnt_break_others(self, css_parser, tmp_css_file):
        good = tmp_css_file("div { display: flex; }", "good.css")
        assert "flexbox" in css_parser.parse_multiple_files([good, "/nonexistent.css"])


# =====================================================================
# Statistics & Reports
# =====================================================================

@pytest.mark.integration
class TestGetStatistics:
    def test_stats_structure(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        stats = css_parser.get_statistics()
        for key in ["total_features", "layout_features", "features_list", "categories"]:
            assert key in stats


@pytest.mark.integration
class TestDetailedReport:
    def test_report_structure(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        report = css_parser.get_detailed_report()
        for key in ["total_features", "features", "feature_details", "unrecognized"]:
            assert key in report


# =====================================================================
# Real-World Scenarios
# =====================================================================

@pytest.mark.integration
class TestRealWorldScenarios:
    def test_modern_css_reset(self, parse_features):
        css = """
        *, *::before, *::after { box-sizing: border-box; }
        * { margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body { min-height: 100vh; line-height: 1.5; }
        """
        features = parse_features(css)
        assert "css3-boxsizing" in features
        assert "css-gencontent" in features
        assert "css-scroll-behavior" in features
        assert "viewport-units" in features

    def test_flexbox_card_layout(self, parse_features):
        css = """
        .cards { display: flex; flex-wrap: wrap; gap: 20px; }
        .card { border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s ease; }
        .card:hover { transform: translateY(-4px); }
        """
        features = parse_features(css)
        assert "flexbox" in features
        assert "flexbox-gap" in features
        assert "border-radius" in features
        assert "css-transitions" in features

    def test_dark_mode_support(self, parse_features):
        css = """
        :root { --bg: #fff; --fg: #1a1a1a; }
        @media (prefers-color-scheme: dark) { :root { --bg: #1a1a1a; --fg: #fff; } }
        body { background-color: var(--bg); color: var(--fg); }
        """
        features = parse_features(css)
        assert "css-variables" in features
        assert "prefers-color-scheme" in features


