"""Tests for API schema dataclasses.

Pure unit tests — no mocks, no I/O. Validates field defaults,
enum values, serialisation round-trips, and helper methods.
"""

import pytest

from src.api.schemas import (
    AnalysisStatus,
    RiskLevel,
    BrowserTarget,
    AnalysisRequest,
    FeatureSummary,
    DetectedFeatures,
    FeatureDetails,
    UnrecognizedPatterns,
    CompatibilityScore,
    BrowserCompatibility,
    AnalysisResult,
    DatabaseInfo,
    DatabaseUpdateResult,
)


# ═══════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════

class TestAnalysisStatusEnum:
    """AnalysisStatus enum values."""

    def test_values(self):
        assert AnalysisStatus.SUCCESS.value == "success"
        assert AnalysisStatus.FAILED.value == "failed"
        assert AnalysisStatus.NO_FILES.value == "no_files"

    def test_member_count(self):
        assert len(AnalysisStatus) == 3


class TestRiskLevelEnum:
    """RiskLevel enum values."""

    def test_values(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_member_count(self):
        assert len(RiskLevel) == 4


# ═══════════════════════════════════════════════════════════════════════
# Simple Dataclasses
# ═══════════════════════════════════════════════════════════════════════

class TestBrowserTarget:
    """BrowserTarget stores name and version."""

    def test_fields(self):
        bt = BrowserTarget(name="chrome", version="120")
        assert bt.name == "chrome"
        assert bt.version == "120"


# ═══════════════════════════════════════════════════════════════════════
# AnalysisRequest
# ═══════════════════════════════════════════════════════════════════════

class TestAnalysisRequest:
    """AnalysisRequest — file lists, helpers."""

    def test_defaults_are_empty(self):
        req = AnalysisRequest()
        assert req.html_files == []
        assert req.css_files == []
        assert req.js_files == []
        assert req.target_browsers == {}

    def test_has_files_false_when_empty(self):
        req = AnalysisRequest()
        assert req.has_files() is False

    def test_has_files_true_with_html(self):
        req = AnalysisRequest(html_files=["index.html"])
        assert req.has_files() is True

    def test_has_files_true_with_css(self):
        req = AnalysisRequest(css_files=["style.css"])
        assert req.has_files() is True

    def test_has_files_true_with_js(self):
        req = AnalysisRequest(js_files=["app.js"])
        assert req.has_files() is True

    def test_total_files_empty(self):
        assert AnalysisRequest().total_files() == 0

    def test_total_files_counts_all_types(self):
        req = AnalysisRequest(
            html_files=["a.html", "b.html"],
            css_files=["c.css"],
            js_files=["d.js", "e.js", "f.js"],
        )
        assert req.total_files() == 6

    def test_default_factories_are_independent(self):
        """Each instance gets its own list objects."""
        a = AnalysisRequest()
        b = AnalysisRequest()
        a.html_files.append("x.html")
        assert b.html_files == []


# ═══════════════════════════════════════════════════════════════════════
# Dataclass Defaults
# ═══════════════════════════════════════════════════════════════════════

class TestDataclassDefaults:
    """Default field values for simple dataclasses."""

    def test_feature_summary_defaults(self):
        fs = FeatureSummary()
        assert fs.total_features == 0
        assert fs.html_features == 0
        assert fs.css_features == 0
        assert fs.js_features == 0
        assert fs.critical_issues == 0

    def test_detected_features_defaults(self):
        df = DetectedFeatures()
        assert df.html == []
        assert df.css == []
        assert df.js == []
        assert df.all == []

    def test_feature_details_defaults(self):
        fd = FeatureDetails()
        assert fd.css == []
        assert fd.js == []
        assert fd.html == []

    def test_unrecognized_patterns_defaults(self):
        up = UnrecognizedPatterns()
        assert up.html == []
        assert up.css == []
        assert up.js == []
        assert up.total == 0


# ═══════════════════════════════════════════════════════════════════════
# CompatibilityScore
# ═══════════════════════════════════════════════════════════════════════

class TestCompatibilityScore:
    """CompatibilityScore defaults and populated values."""

    def test_defaults(self):
        cs = CompatibilityScore()
        assert cs.grade == "N/A"
        assert cs.risk_level == "unknown"
        assert cs.simple_score == 0.0
        assert cs.weighted_score == 0.0

    def test_populated(self):
        cs = CompatibilityScore(grade="A", risk_level="low", simple_score=95.0, weighted_score=93.5)
        assert cs.grade == "A"
        assert cs.simple_score == 95.0


# ═══════════════════════════════════════════════════════════════════════
# BrowserCompatibility
# ═══════════════════════════════════════════════════════════════════════

class TestBrowserCompatibility:
    """BrowserCompatibility required + default fields."""

    def test_required_fields(self):
        bc = BrowserCompatibility(name="chrome", version="120")
        assert bc.name == "chrome"
        assert bc.version == "120"

    def test_default_counts(self):
        bc = BrowserCompatibility(name="firefox", version="121")
        assert bc.supported == 0
        assert bc.partial == 0
        assert bc.unsupported == 0
        assert bc.compatibility_percentage == 0.0
        assert bc.unsupported_features == []
        assert bc.partial_features == []


# ═══════════════════════════════════════════════════════════════════════
# AnalysisResult.from_dict
# ═══════════════════════════════════════════════════════════════════════

class TestAnalysisResultFromDict:
    """AnalysisResult.from_dict() — dict → dataclass."""

    def test_success_populates_all_fields(self, sample_success_report):
        result = AnalysisResult.from_dict(sample_success_report)
        assert result.success is True
        assert result.error is None
        assert result.summary.total_features == 5
        assert result.scores.grade == "B"
        assert "chrome" in result.browsers
        assert "safari" in result.browsers

    def test_failure_dict(self, sample_failure_report):
        result = AnalysisResult.from_dict(sample_failure_report)
        assert result.success is False
        assert "File not found" in result.error

    def test_empty_dict_is_failure(self):
        result = AnalysisResult.from_dict({})
        assert result.success is False
        assert result.error == "Unknown error"

    def test_minimal_success(self):
        """success=True with no other keys still parses cleanly."""
        result = AnalysisResult.from_dict({'success': True})
        assert result.success is True
        assert result.summary.total_features == 0
        assert result.browsers == {}
        assert result.detected_features.all == []

    def test_browser_features_populated(self, sample_success_report):
        result = AnalysisResult.from_dict(sample_success_report)
        safari = result.browsers['safari']
        assert safari.unsupported == 2
        assert 'dialog' in safari.unsupported_features

    def test_detected_features_parsed(self, sample_success_report):
        result = AnalysisResult.from_dict(sample_success_report)
        assert 'promises' in result.detected_features.js
        assert 'flexbox' in result.detected_features.css
        assert len(result.detected_features.all) == 5


# ═══════════════════════════════════════════════════════════════════════
# AnalysisResult.to_dict
# ═══════════════════════════════════════════════════════════════════════

class TestAnalysisResultToDict:
    """AnalysisResult.to_dict() — dataclass → dict."""

    def test_failed_result_minimal(self, sample_failed_result):
        d = sample_failed_result.to_dict()
        assert d['success'] is False
        assert 'error' in d
        # Failed results should NOT contain extra keys
        assert 'summary' not in d

    def test_success_contains_all_keys(self, sample_success_result):
        d = sample_success_result.to_dict()
        expected_keys = {'success', 'summary', 'scores', 'browsers',
                         'features', 'feature_details', 'unrecognized', 'recommendations'}
        assert expected_keys == set(d.keys())

    def test_roundtrip_preserves_data(self, sample_success_report):
        """from_dict → to_dict round-trip preserves key values."""
        result = AnalysisResult.from_dict(sample_success_report)
        d = result.to_dict()

        assert d['summary']['total_features'] == 5
        assert d['scores']['grade'] == 'B'
        assert d['browsers']['chrome']['compatibility_percentage'] == 90.0
        assert 'dialog' in d['features']['html']

    def test_success_result_has_browsers(self, sample_success_result):
        d = sample_success_result.to_dict()
        assert 'chrome' in d['browsers']
        assert d['browsers']['chrome']['version'] == '120'


# ═══════════════════════════════════════════════════════════════════════
# Database Schemas
# ═══════════════════════════════════════════════════════════════════════

class TestDatabaseSchemas:
    """DatabaseInfo and DatabaseUpdateResult."""

    def test_database_info_defaults(self):
        di = DatabaseInfo()
        assert di.features_count == 0
        assert di.last_updated == "Unknown"
        assert di.is_git_repo is False

    def test_database_update_result(self):
        dur = DatabaseUpdateResult(success=True, message="Updated!", no_changes=False)
        assert dur.success is True
        assert dur.message == "Updated!"
        assert dur.no_changes is False
        assert dur.error is None
