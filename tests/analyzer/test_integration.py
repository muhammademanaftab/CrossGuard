"""Integration tests — end-to-end pipeline from parsers through analyzer.

Validates that the full pipeline (parser -> feature set -> analyzer -> report)
works correctly with real Can I Use data.
"""

import pytest

from src.analyzer.compatibility import CompatibilityAnalyzer, CompatibilityReport, Severity
from src.analyzer.scorer import CompatibilityScorer
from src.analyzer.database import CanIUseDatabase
from src.analyzer.version_ranges import get_version_ranges, get_support_summary
from src.parsers.css_parser import CSSParser
from src.parsers.js_parser import JavaScriptParser
from src.parsers.html_parser import HTMLParser


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: Parser -> Analyzer Pipeline
# ═══════════════════════════════════════════════════════════════════════════

class TestParserToAnalyzerPipeline:
    """Tests that parser output feeds correctly into the analyzer."""

    def test_css_flexbox_detected_and_scored(self, analyzer, modern_browsers, tmp_path):
        """CSS file with flexbox -> parser detects 'flexbox' -> analyzer scores highly."""
        css_file = tmp_path / "test.css"
        css_file.write_text("div { display: flex; gap: 10px; }", encoding='utf-8')

        features = CSSParser().parse_file(str(css_file))
        assert 'flexbox' in features

        report = analyzer.analyze(features, modern_browsers)
        assert isinstance(report, CompatibilityReport)
        assert report.features_analyzed > 0
        assert report.overall_score > 50

    def test_js_arrow_functions_detected_and_scored(self, analyzer, modern_browsers, tmp_path):
        """JS file with arrow function -> parser detects it -> analyzer scores."""
        js_file = tmp_path / "test.js"
        js_file.write_text("const add = (a, b) => a + b;", encoding='utf-8')

        features = JavaScriptParser().parse_file(str(js_file))
        assert 'arrow-functions' in features

        report = analyzer.analyze(features, modern_browsers)
        assert report.features_analyzed > 0
        assert report.overall_score > 0

    def test_html_dialog_detected_and_scored(self, analyzer, modern_browsers, tmp_path):
        """HTML file with <dialog> -> parser detects 'dialog' -> analyzer scores."""
        html_file = tmp_path / "test.html"
        html_file.write_text(
            "<html><body><dialog open>Hello</dialog></body></html>",
            encoding='utf-8',
        )

        features = HTMLParser().parse_file(str(html_file))
        assert 'dialog' in features

        report = analyzer.analyze(features, modern_browsers)
        assert report.features_analyzed >= 1

    def test_empty_file_perfect_score(self, analyzer, modern_browsers, tmp_path):
        """Empty CSS file -> no features -> perfect score."""
        css_file = tmp_path / "empty.css"
        css_file.write_text("", encoding='utf-8')

        features = CSSParser().parse_file(str(css_file))
        assert len(features) == 0

        report = analyzer.analyze(features, modern_browsers)
        assert report.overall_score == 100.0
        assert report.features_analyzed == 0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: Scoring End-to-End
# ═══════════════════════════════════════════════════════════════════════════

class TestScoringEndToEnd:
    """Tests that scoring aligns with expectations for real features."""

    def test_modern_features_grade_high(self, analyzer, modern_browsers, well_supported_features):
        """Well-supported features in modern browsers get grade A or B."""
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        assert summary['grade'] in ['A+', 'A', 'A-', 'B+', 'B']

    def test_adding_ie_strictly_lowers_score(self, analyzer, well_supported_features):
        """Adding IE 11 strictly reduces overall score for modern-only features."""
        modern = {'chrome': '120', 'firefox': '121', 'safari': '17'}
        with_ie = {'chrome': '120', 'firefox': '121', 'safari': '17', 'ie': '11'}

        score_modern = analyzer.analyze(well_supported_features, modern).overall_score
        score_ie = analyzer.analyze(well_supported_features, with_ie).overall_score

        assert score_ie < score_modern

    def test_scorer_weighted_vs_simple_diverge(self):
        """Weighted and simple scores differ with non-uniform browser weights.

        Simple: (100+0+100)/3 = 66.67
        Weighted: ie(0.5) and opera(0.7) change the calculation.
        """
        scorer = CompatibilityScorer()
        status = {'chrome': 'y', 'ie': 'n', 'opera': 'y'}
        simple = scorer.calculate_simple_score(status)
        weighted = scorer.calculate_weighted_score(status)

        assert abs(simple - 66.67) < 0.1
        assert weighted.weighted_score != simple


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Report Structure Validation
# ═══════════════════════════════════════════════════════════════════════════

class TestReportStructure:
    """Tests that reports contain all required fields with valid values."""

    def test_all_dataclass_fields_present(self, analyzer, modern_browsers):
        """Report has all 8 CompatibilityReport fields."""
        report = analyzer.analyze({'flexbox', 'css-grid'}, modern_browsers)
        assert hasattr(report, 'overall_score')
        assert hasattr(report, 'browser_scores')
        assert hasattr(report, 'issues')
        assert hasattr(report, 'features_analyzed')
        assert hasattr(report, 'critical_issues')
        assert hasattr(report, 'high_issues')
        assert hasattr(report, 'medium_issues')
        assert hasattr(report, 'low_issues')

    def test_browser_scores_valid_range(self, analyzer, modern_browsers):
        """Each browser score is a float in [0, 100] with non-negative counts."""
        report = analyzer.analyze({'flexbox'}, modern_browsers)
        for browser, bs in report.browser_scores.items():
            assert 0 <= bs.score <= 100
            assert bs.supported_count >= 0
            assert bs.partial_count >= 0
            assert bs.unsupported_count >= 0

    def test_overall_score_in_range(self, analyzer, modern_browsers):
        """Overall score is between 0 and 100."""
        report = analyzer.analyze({'flexbox', 'arrow-functions'}, modern_browsers)
        assert 0 <= report.overall_score <= 100


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Multi-File Analysis
# ═══════════════════════════════════════════════════════════════════════════

class TestMultiFileAnalysis:
    """Tests combining features from multiple file types."""

    def test_css_and_js_features_union(self, analyzer, modern_browsers, tmp_path):
        """CSS + JS features are unioned; report covers all."""
        css_file = tmp_path / "styles.css"
        css_file.write_text("div { display: grid; }", encoding='utf-8')
        js_file = tmp_path / "app.js"
        js_file.write_text("const x = new Promise((r) => r());", encoding='utf-8')

        css_features = CSSParser().parse_file(str(css_file))
        js_features = JavaScriptParser().parse_file(str(js_file))

        combined = css_features | js_features
        assert len(combined) >= 2

        report = analyzer.analyze(combined, modern_browsers)
        assert report.features_analyzed == len(combined)

    def test_html_and_css_combined(self, analyzer, modern_browsers, tmp_path):
        """HTML + CSS features analyzed together."""
        html_file = tmp_path / "page.html"
        html_file.write_text(
            '<html><body><details><summary>Info</summary>Content</details></body></html>',
            encoding='utf-8',
        )
        css_file = tmp_path / "style.css"
        css_file.write_text("body { display: flex; }", encoding='utf-8')

        html_features = HTMLParser().parse_file(str(html_file))
        css_features = CSSParser().parse_file(str(css_file))

        combined = html_features | css_features
        report = analyzer.analyze(combined, modern_browsers)
        assert report.features_analyzed == len(combined)
        assert report.overall_score > 0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: Version Ranges + Database Consistency
# ═══════════════════════════════════════════════════════════════════════════

class TestDatabaseConsistency:
    """Tests that version_ranges and database agree on support data."""

    def test_flexbox_range_ends_supported(self):
        """Flexbox's last range in Chrome is 'y' (supported)."""
        ranges = get_version_ranges('flexbox', 'chrome')
        assert ranges[-1]['status'] == 'y'

    def test_summary_current_status_matches_last_range(self):
        """Support summary current_status matches the last range status for all browsers."""
        summary = get_support_summary('flexbox')
        for browser, data in summary.items():
            last_range_status = data['ranges'][-1]['status']
            assert data['current_status'] == last_range_status, \
                f"{browser}: summary says '{data['current_status']}' but last range is '{last_range_status}'"

    def test_database_and_ranges_agree(self, caniuse_db):
        """CanIUseDatabase.check_support() agrees with version_ranges for latest Chrome."""
        ranges = get_version_ranges('flexbox', 'chrome')
        last_range = ranges[-1]
        db_status = caniuse_db.check_support('flexbox', 'chrome', last_range['end'])
        assert db_status == last_range['status']

    def test_multiple_features_consistent(self, caniuse_db):
        """Database and ranges agree for multiple features."""
        for feature_id in ['css-grid', 'promises', 'arrow-functions']:
            ranges = get_version_ranges(feature_id, 'chrome')
            if ranges:
                last = ranges[-1]
                db_status = caniuse_db.check_support(feature_id, 'chrome', last['end'])
                assert db_status == last['status'], \
                    f"{feature_id}: DB says '{db_status}' but range says '{last['status']}'"
