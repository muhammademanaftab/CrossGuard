"""CSS parser integration tests.

File I/O, real-world multi-feature scenarios, and full pipeline tests
through statistics and reports.
"""

import pytest
from src.parsers.css_parser import parse_css_file


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

    def test_empty_file(self, css_parser, tmp_css_file):
        assert len(css_parser.parse_file(tmp_css_file(""))) == 0

    def test_file_with_multiple_features(self, css_parser, tmp_css_file):
        css = ".container { display: grid; } .item { opacity: 0.5; }"
        css += " @keyframes slide { from { transform: translateX(0); } }"
        features = css_parser.parse_file(tmp_css_file(css))
        assert "css-grid" in features
        assert "css-animation" in features


@pytest.mark.integration
class TestParseMultipleFiles:
    def test_multiple_files_combined(self, css_parser, tmp_css_file):
        f1 = tmp_css_file("div { display: flex; }", "a.css")
        f2 = tmp_css_file("div { display: grid; }", "b.css")
        features = css_parser.parse_multiple_files([f1, f2])
        assert "flexbox" in features
        assert "css-grid" in features

    def test_empty_file_list(self, css_parser):
        assert len(css_parser.parse_multiple_files([])) == 0

    def test_one_bad_file_doesnt_break_others(self, css_parser, tmp_css_file):
        good = tmp_css_file("div { display: flex; }", "good.css")
        assert "flexbox" in css_parser.parse_multiple_files([good, "/nonexistent.css"])


@pytest.mark.integration
class TestConvenienceFileFunction:
    def test_parse_css_file(self, tmp_css_file):
        assert "css-grid" in parse_css_file(tmp_css_file("div { display: grid; }"))


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

    def test_stats_total_matches_sum(self, css_parser):
        css_parser.parse_string("""
            div { display: flex; opacity: 0.5; transform: rotate(0); }
            @media (prefers-color-scheme: dark) { body { color: white; } }
        """)
        stats = css_parser.get_statistics()
        category_sum = (
            stats["layout_features"] + stats["transform_animation"] +
            stats["color_background"] + stats["typography"] +
            stats["selectors"] + stats["media_queries"] + stats["other_features"]
        )
        assert stats["total_features"] == category_sum

    def test_stats_selectors_category(self, css_parser):
        css_parser.parse_string("div:nth-child(2) { color: red; }")
        stats = css_parser.get_statistics()
        assert "css-sel3" in stats["categories"]["selectors"]


@pytest.mark.integration
class TestDetailedReport:
    def test_report_structure(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        report = css_parser.get_detailed_report()
        for key in ["total_features", "features", "feature_details", "unrecognized"]:
            assert key in report

    def test_report_total_matches_features_list(self, css_parser):
        css_parser.parse_string("div { display: flex; opacity: 0.5; }")
        report = css_parser.get_detailed_report()
        assert report["total_features"] == len(report["features"])

    def test_report_feature_details_has_description(self, css_parser):
        css_parser.parse_string("div { display: grid; }")
        report = css_parser.get_detailed_report()
        for detail in report["feature_details"]:
            assert "description" in detail
            assert "feature" in detail


# =====================================================================
# Pipeline Scenarios
# =====================================================================

@pytest.mark.integration
class TestFontFaceHandling:
    def test_font_face_basic(self, parse_features):
        features = parse_features(
            "@font-face { font-family: 'F'; src: url('f.woff2') format('woff2'); }"
        )
        assert "fontface" in features
        assert "woff2" in features

    def test_font_face_multiple_sources(self, parse_features):
        css = """@font-face {
            font-family: 'F';
            src: url('f.woff2') format('woff2'), url('f.woff') format('woff');
        }"""
        features = parse_features(css)
        assert "woff2" in features
        assert "woff" in features


@pytest.mark.integration
class TestKeyframesHandling:
    def test_keyframes_with_transforms(self, parse_features):
        css = "@keyframes s { from { transform: translateX(0); } to { transform: translateX(100px); } }"
        features = parse_features(css)
        assert "css-animation" in features
        assert "transforms2d" in features

    def test_keyframes_with_modern_features(self, parse_features):
        css = "@keyframes e { from { clip-path: circle(0%); } to { clip-path: circle(100%); } }"
        features = parse_features(css)
        assert "css-animation" in features
        assert "css-clip-path" in features


@pytest.mark.integration
class TestNestedAtRules:
    def test_media_wrapping_rules(self, parse_features):
        features = parse_features("@media (max-width: 768px) { .c { display: flex; } }")
        assert "css-mediaqueries" in features
        assert "flexbox" in features

    def test_three_levels_deep(self, parse_features):
        css = "@media (min-width: 768px) { @supports (display: grid) {"
        css += " @layer layout { .g { display: grid; } } } }"
        features = parse_features(css)
        assert "css-mediaqueries" in features
        assert "css-featurequeries" in features
        assert "css-cascade-layers" in features
        assert "css-grid" in features


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

    def test_css_grid_layout(self, parse_features):
        css = """
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem; }
        @media (max-width: 768px) { .item { grid-column: span 1; } }
        """
        features = parse_features(css)
        assert "css-grid" in features
        assert "rem" in features
        assert "css-mediaqueries" in features

    def test_dark_mode_support(self, parse_features):
        css = """
        :root { --bg: #fff; --fg: #1a1a1a; }
        @media (prefers-color-scheme: dark) { :root { --bg: #1a1a1a; --fg: #fff; } }
        body { background-color: var(--bg); color: var(--fg); }
        """
        features = parse_features(css)
        assert "css-variables" in features
        assert "prefers-color-scheme" in features

    def test_modern_button_styles(self, parse_features):
        css = """
        .button {
            appearance: none; border-radius: 0.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            cursor: pointer; transition: all 0.2s ease; user-select: none;
        }
        .button:focus-visible { outline: 2px solid #667eea; }
        """
        features = parse_features(css)
        assert "css-appearance" in features
        assert "css-gradients" in features
        assert "css-transitions" in features
        assert "css-focus-visible" in features

    def test_container_queries_pattern(self, parse_features):
        css = """
        .container { container-type: inline-size; container-name: card; }
        @container card (min-width: 400px) {
            .card { display: flex; gap: 20px; }
            .card-image { width: 40cqi; }
        }
        """
        features = parse_features(css)
        assert "css-container-queries" in features
        assert "flexbox" in features
        assert "css-container-query-units" in features

    def test_scroll_snap_gallery(self, parse_features):
        css = """
        .gallery { display: flex; overflow-x: auto; scroll-snap-type: x mandatory;
                   scroll-behavior: smooth; overscroll-behavior-x: contain; }
        .gallery-item { scroll-snap-align: start; }
        """
        features = parse_features(css)
        assert "flexbox" in features
        assert "css-snappoints" in features
        assert "css-overscroll-behavior" in features

    def test_animation_with_reduced_motion(self, parse_features):
        css = """
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-in { animation: fadeInUp 0.5s ease-out forwards; }
        @media (prefers-reduced-motion: reduce) { .animate-in { animation: none; } }
        """
        features = parse_features(css)
        assert "css-animation" in features
        assert "transforms2d" in features
        assert "prefers-reduced-motion" in features
