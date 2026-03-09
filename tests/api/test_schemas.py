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

class TestEnums:
    """Enum values and member counts."""

    @pytest.mark.parametrize("member,value", [
        (AnalysisStatus.SUCCESS, "success"),
        (AnalysisStatus.FAILED, "failed"),
        (AnalysisStatus.NO_FILES, "no_files"),
    ])
    def test_analysis_status_values(self, member, value):
        assert member.value == value

    def test_analysis_status_count(self):
        assert len(AnalysisStatus) == 3

    @pytest.mark.parametrize("member,value", [
        (RiskLevel.LOW, "low"),
        (RiskLevel.MEDIUM, "medium"),
        (RiskLevel.HIGH, "high"),
        (RiskLevel.CRITICAL, "critical"),
    ])
    def test_risk_level_values(self, member, value):
        assert member.value == value

    def test_risk_level_count(self):
        assert len(RiskLevel) == 4


# ═══════════════════════════════════════════════════════════════════════
# BrowserTarget
# ═══════════════════════════════════════════════════════════════════════

class TestBrowserTarget:
    def test_fields(self):
        bt = BrowserTarget(name="chrome", version="120")
        assert bt.name == "chrome"
        assert bt.version == "120"


# ═══════════════════════════════════════════════════════════════════════
# AnalysisRequest
# ═══════════════════════════════════════════════════════════════════════

class TestAnalysisRequest:

    def test_defaults_are_empty(self):
        req = AnalysisRequest()
        assert req.html_files == []
        assert req.css_files == []
        assert req.js_files == []
        assert req.target_browsers == {}

    @pytest.mark.parametrize("kwargs,expected", [
        ({}, False),
        ({"html_files": ["index.html"]}, True),
        ({"css_files": ["style.css"]}, True),
        ({"js_files": ["app.js"]}, True),
    ])
    def test_has_files(self, kwargs, expected):
        assert AnalysisRequest(**kwargs).has_files() is expected

    def test_total_files_counts_all_types(self):
        req = AnalysisRequest(
            html_files=["a.html", "b.html"],
            css_files=["c.css"],
            js_files=["d.js", "e.js", "f.js"],
        )
        assert req.total_files() == 6

    def test_default_factories_are_independent(self):
        a = AnalysisRequest()
        b = AnalysisRequest()
        a.html_files.append("x.html")
        assert b.html_files == []


# ═══════════════════════════════════════════════════════════════════════
# Dataclass Defaults (parametrized)
# ═══════════════════════════════════════════════════════════════════════

class TestDataclassDefaults:
    """Default field values for simple dataclasses."""

    @pytest.mark.parametrize("cls,field,expected", [
        (FeatureSummary, "total_features", 0),
        (FeatureSummary, "html_features", 0),
        (FeatureSummary, "css_features", 0),
        (FeatureSummary, "js_features", 0),
        (FeatureSummary, "critical_issues", 0),
        (DetectedFeatures, "html", []),
        (DetectedFeatures, "css", []),
        (DetectedFeatures, "js", []),
        (DetectedFeatures, "all", []),
        (FeatureDetails, "css", []),
        (FeatureDetails, "js", []),
        (FeatureDetails, "html", []),
        (UnrecognizedPatterns, "html", []),
        (UnrecognizedPatterns, "css", []),
        (UnrecognizedPatterns, "js", []),
        (UnrecognizedPatterns, "total", 0),
    ])
    def test_default_value(self, cls, field, expected):
        obj = cls()
        assert getattr(obj, field) == expected


# ═══════════════════════════════════════════════════════════════════════
# CompatibilityScore
# ═══════════════════════════════════════════════════════════════════════

class TestCompatibilityScore:

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

    def test_required_and_default_fields(self):
        bc = BrowserCompatibility(name="firefox", version="121")
        assert bc.name == "firefox"
        assert bc.version == "121"
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

    def test_failed_result_minimal(self, sample_failed_result):
        d = sample_failed_result.to_dict()
        assert d['success'] is False
        assert 'error' in d
        assert 'summary' not in d

    def test_success_contains_all_keys(self, sample_success_result):
        d = sample_success_result.to_dict()
        expected_keys = {'success', 'summary', 'scores', 'browsers',
                         'features', 'feature_details', 'unrecognized', 'recommendations',
                         'baseline_summary'}
        assert expected_keys == set(d.keys())

    def test_roundtrip_preserves_data(self, sample_success_report):
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
