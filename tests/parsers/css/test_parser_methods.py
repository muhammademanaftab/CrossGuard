"""Tests for CSS parser methods: parse_file, parse_multiple_files,
get_statistics, validate_css, convenience functions, unrecognized patterns,
and detailed report accuracy.

These tests target the methods and code paths that had NO test coverage.
"""

import os
import pytest
import tempfile
from unittest.mock import patch

from src.parsers.css_parser import CSSParser, parse_css_file, parse_css_string


# ─── Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def css_parser():
    return CSSParser()


@pytest.fixture
def tmp_css_file(tmp_path):
    """Create a temporary CSS file with given content."""
    def _create(content, filename="test.css"):
        filepath = tmp_path / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
    return _create


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: parse_file() — File Operations
# ═══════════════════════════════════════════════════════════════════════════

class TestParseFile:
    """Tests for CSSParser.parse_file()."""

    def test_parse_valid_file(self, css_parser, tmp_css_file):
        path = tmp_css_file("div { display: flex; }")
        features = css_parser.parse_file(path)
        assert 'flexbox' in features

    def test_parse_file_returns_set(self, css_parser, tmp_css_file):
        path = tmp_css_file("body { margin: 0; }")
        result = css_parser.parse_file(path)
        assert isinstance(result, set)

    def test_file_not_found_raises(self, css_parser):
        with pytest.raises(FileNotFoundError):
            css_parser.parse_file("/nonexistent/path/file.css")

    def test_non_utf8_file_raises(self, css_parser, tmp_path):
        filepath = tmp_path / "bad.css"
        filepath.write_bytes(b'\xff\xfe\x00\x00' + b'\x80\x81\x82')
        with pytest.raises(ValueError, match="not valid UTF-8"):
            css_parser.parse_file(str(filepath))

    def test_empty_file(self, css_parser, tmp_css_file):
        path = tmp_css_file("")
        features = css_parser.parse_file(path)
        assert len(features) == 0

    def test_file_with_multiple_features(self, css_parser, tmp_css_file):
        css = """
        .container { display: grid; }
        .item { opacity: 0.5; }
        @keyframes slide { from { transform: translateX(0); } }
        """
        path = tmp_css_file(css)
        features = css_parser.parse_file(path)
        assert 'css-grid' in features
        assert 'css-animation' in features

    def test_file_path_as_string(self, css_parser, tmp_css_file):
        path = tmp_css_file(".a { position: sticky; }")
        features = css_parser.parse_file(path)
        assert 'css-sticky' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: parse_multiple_files()
# ═══════════════════════════════════════════════════════════════════════════

class TestParseMultipleFiles:
    """Tests for CSSParser.parse_multiple_files()."""

    def test_multiple_files_combined(self, css_parser, tmp_css_file):
        f1 = tmp_css_file("div { display: flex; }", "a.css")
        f2 = tmp_css_file("div { display: grid; }", "b.css")
        features = css_parser.parse_multiple_files([f1, f2])
        assert 'flexbox' in features
        assert 'css-grid' in features

    def test_empty_file_list(self, css_parser):
        features = css_parser.parse_multiple_files([])
        assert len(features) == 0

    def test_one_bad_file_doesnt_break_others(self, css_parser, tmp_css_file):
        good = tmp_css_file("div { display: flex; }", "good.css")
        features = css_parser.parse_multiple_files([good, "/nonexistent.css"])
        assert 'flexbox' in features

    def test_returns_union_of_features(self, css_parser, tmp_css_file):
        f1 = tmp_css_file("div { position: sticky; }", "x.css")
        f2 = tmp_css_file("div { position: sticky; }", "y.css")
        features = css_parser.parse_multiple_files([f1, f2])
        assert 'css-sticky' in features

    def test_single_file_in_list(self, css_parser, tmp_css_file):
        f = tmp_css_file("div { display: grid; }", "single.css")
        features = css_parser.parse_multiple_files([f])
        assert 'css-grid' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: get_statistics()
# ═══════════════════════════════════════════════════════════════════════════

class TestGetStatistics:
    """Tests for CSSParser.get_statistics()."""

    def test_stats_structure(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        stats = css_parser.get_statistics()
        assert 'total_features' in stats
        assert 'layout_features' in stats
        assert 'transform_animation' in stats
        assert 'color_background' in stats
        assert 'typography' in stats
        assert 'selectors' in stats
        assert 'media_queries' in stats
        assert 'other_features' in stats
        assert 'features_list' in stats
        assert 'categories' in stats

    def test_stats_layout_category(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        stats = css_parser.get_statistics()
        assert stats['layout_features'] >= 1
        assert 'flexbox' in stats['categories']['layout']

    def test_stats_transform_category(self, css_parser):
        css_parser.parse_string("div { transform: rotate(45deg); }")
        stats = css_parser.get_statistics()
        assert stats['transform_animation'] >= 1
        assert 'transforms2d' in stats['categories']['transform_animation']

    def test_stats_empty_input(self, css_parser):
        css_parser.parse_string("")
        stats = css_parser.get_statistics()
        assert stats['total_features'] == 0
        assert stats['features_list'] == []

    def test_stats_features_list_sorted(self, css_parser):
        css_parser.parse_string("""
            div { display: flex; opacity: 0.5; }
            @keyframes x { from { transform: rotate(0); } }
        """)
        stats = css_parser.get_statistics()
        assert stats['features_list'] == sorted(stats['features_list'])

    def test_stats_total_matches_sum(self, css_parser):
        css_parser.parse_string("""
            div { display: flex; opacity: 0.5; transform: rotate(0); }
            @media (prefers-color-scheme: dark) { body { color: white; } }
        """)
        stats = css_parser.get_statistics()
        category_sum = (
            stats['layout_features'] +
            stats['transform_animation'] +
            stats['color_background'] +
            stats['typography'] +
            stats['selectors'] +
            stats['media_queries'] +
            stats['other_features']
        )
        assert stats['total_features'] == category_sum

    def test_stats_media_query_category(self, css_parser):
        css_parser.parse_string("@media (prefers-color-scheme: dark) { body { color: white; } }")
        stats = css_parser.get_statistics()
        assert stats['media_queries'] >= 1

    def test_stats_selectors_category(self, css_parser):
        css_parser.parse_string("div:nth-child(2) { color: red; }")
        stats = css_parser.get_statistics()
        assert stats['selectors'] >= 1
        assert 'css-sel3' in stats['categories']['selectors']

    def test_stats_has_selector_correctly_categorized(self, css_parser):
        """css-has is a selector and get_statistics() correctly categorizes it."""
        css_parser.parse_string("div:has(.child) { color: red; }")
        stats = css_parser.get_statistics()
        assert 'css-has' in stats['categories']['selectors']


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: validate_css()
# ═══════════════════════════════════════════════════════════════════════════

class TestValidateCSS:
    """Tests for CSSParser.validate_css()."""

    def test_valid_basic_css(self, css_parser):
        assert css_parser.validate_css("body { margin: 0; }") is True

    def test_valid_with_class(self, css_parser):
        assert css_parser.validate_css(".container { display: flex; }") is True

    def test_valid_with_id(self, css_parser):
        assert css_parser.validate_css("#main { padding: 10px; }") is True

    def test_valid_media_query(self, css_parser):
        assert css_parser.validate_css("@media screen { }") is True

    def test_valid_keyframes(self, css_parser):
        assert css_parser.validate_css("@keyframes fade { }") is True

    def test_invalid_plain_text(self, css_parser):
        assert css_parser.validate_css("hello world") is False

    def test_invalid_empty_string(self, css_parser):
        assert css_parser.validate_css("") is False

    def test_valid_just_braces(self, css_parser):
        assert css_parser.validate_css("{ }") is True

    def test_valid_just_colon(self, css_parser):
        assert css_parser.validate_css("color:") is True

    def test_valid_just_semicolon(self, css_parser):
        assert css_parser.validate_css("margin: 0;") is True


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: Convenience Functions
# ═══════════════════════════════════════════════════════════════════════════

class TestConvenienceFunctions:
    """Tests for module-level parse_css_file() and parse_css_string()."""

    def test_parse_css_string_basic(self):
        features = parse_css_string("div { display: grid; }")
        assert 'css-grid' in features

    def test_parse_css_string_empty(self):
        features = parse_css_string("")
        assert len(features) == 0

    def test_parse_css_file_basic(self, tmp_css_file):
        path = tmp_css_file("div { display: grid; }")
        features = parse_css_file(path)
        assert 'css-grid' in features

    def test_parse_css_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_css_file("/nonexistent.css")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: get_detailed_report()
# ═══════════════════════════════════════════════════════════════════════════

class TestDetailedReport:
    """Tests for report structure and accuracy."""

    def test_report_structure(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        report = css_parser.get_detailed_report()
        assert 'total_features' in report
        assert 'features' in report
        assert 'feature_details' in report
        assert 'unrecognized' in report

    def test_report_total_matches_features_list(self, css_parser):
        css_parser.parse_string("div { display: flex; opacity: 0.5; }")
        report = css_parser.get_detailed_report()
        assert report['total_features'] == len(report['features'])

    def test_report_features_sorted(self, css_parser):
        css_parser.parse_string("div { display: flex; opacity: 0.5; }")
        report = css_parser.get_detailed_report()
        assert report['features'] == sorted(report['features'])

    def test_report_feature_details_has_description(self, css_parser):
        css_parser.parse_string("div { display: grid; }")
        report = css_parser.get_detailed_report()
        for detail in report['feature_details']:
            assert 'description' in detail
            assert 'feature' in detail
            assert 'matched_properties' in detail

    def test_report_unrecognized_sorted(self, css_parser):
        css_parser.parse_string("div { some-unknown-prop: value; }")
        report = css_parser.get_detailed_report()
        assert report['unrecognized'] == sorted(report['unrecognized'])

    def test_report_empty_input(self, css_parser):
        css_parser.parse_string("")
        report = css_parser.get_detailed_report()
        assert report['total_features'] == 0
        assert report['features'] == []
        assert report['feature_details'] == []


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: Unrecognized Patterns Detection
# ═══════════════════════════════════════════════════════════════════════════

class TestUnrecognizedPatterns:
    """Tests for _find_unrecognized_patterns_structured()."""

    def test_basic_property_not_flagged(self, css_parser):
        css_parser.parse_string("div { color: red; margin: 10px; }")
        assert len(css_parser.unrecognized_patterns) == 0

    def test_unknown_property_flagged(self, css_parser):
        css_parser.parse_string("div { some-unknown-property: value; }")
        assert any('some-unknown-property' in p for p in css_parser.unrecognized_patterns)

    def test_custom_property_not_flagged(self, css_parser):
        css_parser.parse_string(":root { --my-color: red; }")
        # Custom properties (--var) should be ignored
        assert not any('--my-color' in p for p in css_parser.unrecognized_patterns)

    def test_known_feature_property_not_flagged(self, css_parser):
        css_parser.parse_string("div { clip-path: circle(); }")
        assert not any('clip-path' in p for p in css_parser.unrecognized_patterns)

    def test_basic_at_rule_not_flagged(self, css_parser):
        css_parser.parse_string("@media screen { div { color: red; } }")
        assert not any('@media' in p for p in css_parser.unrecognized_patterns)

    def test_unknown_at_rule_flagged(self, css_parser):
        css_parser.parse_string("@some-unknown-rule { div { color: red; } }")
        assert any('some-unknown-rule' in p for p in css_parser.unrecognized_patterns)

    def test_font_face_at_rule_not_flagged(self, css_parser):
        css_parser.parse_string("@font-face { font-family: 'Test'; }")
        assert not any('@font-face' in p for p in css_parser.unrecognized_patterns)

    def test_import_not_flagged(self, css_parser):
        css_parser.parse_string("@import url('style.css');")
        assert not any('@import' in p for p in css_parser.unrecognized_patterns)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: State Reset Between Parses
# ═══════════════════════════════════════════════════════════════════════════

class TestStateReset:
    """Verify that parse_string resets state between calls."""

    def test_features_reset(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        assert 'flexbox' in css_parser.features_found
        css_parser.parse_string("div { color: red; }")
        assert 'flexbox' not in css_parser.features_found

    def test_feature_details_reset(self, css_parser):
        css_parser.parse_string("div { display: grid; }")
        count1 = len(css_parser.feature_details)
        assert count1 > 0
        css_parser.parse_string("")
        assert len(css_parser.feature_details) == 0

    def test_unrecognized_reset(self, css_parser):
        css_parser.parse_string("div { weird-prop: val; }")
        assert len(css_parser.unrecognized_patterns) > 0
        css_parser.parse_string("div { color: red; }")
        assert len(css_parser.unrecognized_patterns) == 0

    def test_block_counter_reset(self, css_parser):
        css_parser.parse_string("div { color: red; } span { color: blue; }")
        assert css_parser._block_counter > 0
        css_parser.parse_string("")
        assert css_parser._block_counter == 0
