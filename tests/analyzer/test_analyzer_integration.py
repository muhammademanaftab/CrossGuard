"""Integration tests -- end-to-end pipeline from parsers through analyzer.

Validates that the full pipeline (parser -> feature set -> analyzer -> report)
works correctly with real Can I Use data.
"""

import pytest

from src.analyzer.compatibility import (
    CompatibilityAnalyzer,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
    SEVERITY_INFO,
)
from src.analyzer.scorer import CompatibilityScorer
from src.parsers.css_parser import CSSParser
from src.parsers.js_parser import JavaScriptParser
from src.parsers.html_parser import HTMLParser


# ============================================================================
# SECTION 1: Parser -> Analyzer Pipeline
# ============================================================================

class TestParserToAnalyzerPipeline:
    """Tests that parser output feeds correctly into the analyzer."""

    @pytest.mark.integration
    def test_css_flexbox_detected_and_scored(self, analyzer, modern_browsers, tmp_path):
        css_file = tmp_path / "test.css"
        css_file.write_text("div { display: flex; gap: 10px; }", encoding='utf-8')
        features = CSSParser().parse_file(str(css_file))
        assert 'flexbox' in features
        report = analyzer.analyze(features, modern_browsers)
        assert isinstance(report, dict)
        assert report['overall_score'] > 50

    @pytest.mark.integration
    def test_js_arrow_functions_detected_and_scored(self, analyzer, modern_browsers, tmp_path):
        js_file = tmp_path / "test.js"
        js_file.write_text("const add = (a, b) => a + b;", encoding='utf-8')
        features = JavaScriptParser().parse_file(str(js_file))
        assert 'arrow-functions' in features
        report = analyzer.analyze(features, modern_browsers)
        assert report['features_analyzed'] > 0

    @pytest.mark.integration
    def test_html_dialog_detected_and_scored(self, analyzer, modern_browsers, tmp_path):
        html_file = tmp_path / "test.html"
        html_file.write_text(
            "<html><body><dialog open>Hello</dialog></body></html>", encoding='utf-8')
        features = HTMLParser().parse_file(str(html_file))
        assert 'dialog' in features
        report = analyzer.analyze(features, modern_browsers)
        assert report['features_analyzed'] >= 1


# ============================================================================
# SECTION 2: Scoring End-to-End
# ============================================================================

class TestScoringEndToEnd:
    """Tests that scoring aligns with expectations for real features."""

    @pytest.mark.integration
    def test_modern_features_grade_high(self, analyzer, modern_browsers, well_supported_features):
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        assert summary['grade'] in ['A+', 'A', 'A-', 'B+', 'B']



# ============================================================================
# SECTION 3: Report Structure Validation
# ============================================================================

class TestReportStructure:
    """Tests that reports contain all required fields with valid values."""

    @pytest.mark.integration
    def test_report_fields_and_score_ranges(self, analyzer, modern_browsers):
        report = analyzer.analyze({'flexbox', 'css-grid'}, modern_browsers)
        for field in ('overall_score', 'browser_scores', 'issues', 'features_analyzed',
                      'critical_issues', 'high_issues', 'medium_issues', 'low_issues'):
            assert field in report
        assert 0 <= report['overall_score'] <= 100
        for bs in report['browser_scores'].values():
            assert 0 <= bs['score'] <= 100


# ============================================================================
# SECTION 4: Multi-File Analysis
# ============================================================================

class TestMultiFileAnalysis:
    """Tests combining features from multiple file types."""

    @pytest.mark.integration
    def test_css_and_js_features_union(self, analyzer, modern_browsers, tmp_path):
        css_file = tmp_path / "styles.css"
        css_file.write_text("div { display: grid; }", encoding='utf-8')
        js_file = tmp_path / "app.js"
        js_file.write_text("const x = new Promise((r) => r());", encoding='utf-8')
        combined = CSSParser().parse_file(str(css_file)) | JavaScriptParser().parse_file(str(js_file))
        report = analyzer.analyze(combined, modern_browsers)
        assert report['features_analyzed'] == len(combined)


# ============================================================================
# SECTION 5: Version Ranges + Database Consistency
# ============================================================================
