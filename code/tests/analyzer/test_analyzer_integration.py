"""Integration tests -- end-to-end pipeline from parsers through analyzer.

Validates that the full pipeline (parser -> feature set -> analyzer -> report)
works correctly with real Can I Use data.
"""

import pytest

from src.analyzer.scorer import CompatibilityScorer
from src.parsers.css_parser import CSSParser
from src.parsers.js_parser import JavaScriptParser


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
        classification = analyzer.classify_features(features, modern_browsers)
        scorer = CompatibilityScorer()
        pcts = {b: scorer.score_statuses(r['statuses']) for b, r in classification.items()}
        assert scorer.overall_score(pcts) > 50


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
        classification = analyzer.classify_features(combined, modern_browsers)
        # every feature should land in exactly one bucket per browser
        bucket_keys = ('supported', 'partial', 'unsupported', 'unknown')
        for bucket in classification.values():
            total_in_buckets = sum(len(bucket[k]) for k in bucket_keys)
            assert total_in_buckets == len(combined)
            assert len(bucket['statuses']) == len(combined)
