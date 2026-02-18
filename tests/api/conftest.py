"""Shared fixtures for API layer tests."""

import pytest

import src.api.service as service_module
from src.api.service import AnalyzerService
from src.api.schemas import (
    AnalysisRequest,
    AnalysisResult,
    FeatureSummary,
    CompatibilityScore,
    BrowserCompatibility,
    DetectedFeatures,
    FeatureDetails,
    UnrecognizedPatterns,
)


# ─── Service Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def service():
    """Fresh AnalyzerService instance (not singleton) for test isolation."""
    return AnalyzerService()


@pytest.fixture
def reset_singleton():
    """Save and restore the module-level singleton around the test."""
    original = service_module._service_instance
    yield
    service_module._service_instance = original


# ─── Request Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def empty_request():
    """AnalysisRequest with no files."""
    return AnalysisRequest()


# ─── Report / Result Fixtures ──────────────────────────────────────────

@pytest.fixture
def sample_success_report():
    """Realistic dict as returned by CrossGuardAnalyzer.analyze_project()."""
    return {
        'success': True,
        'summary': {
            'total_features': 5,
            'html_features': 1,
            'css_features': 2,
            'js_features': 2,
            'critical_issues': 1,
        },
        'scores': {
            'grade': 'B',
            'risk_level': 'medium',
            'simple_score': 82.5,
            'weighted_score': 80.0,
        },
        'browsers': {
            'chrome': {
                'version': '120',
                'supported': 4,
                'partial': 1,
                'unsupported': 0,
                'compatibility_percentage': 90.0,
                'unsupported_features': [],
                'partial_features': ['css-container-queries'],
            },
            'safari': {
                'version': '17',
                'supported': 3,
                'partial': 0,
                'unsupported': 2,
                'compatibility_percentage': 60.0,
                'unsupported_features': ['dialog', 'css-nesting'],
                'partial_features': [],
            },
        },
        'features': {
            'html': ['dialog'],
            'css': ['flexbox', 'css-grid'],
            'js': ['promises', 'arrow-functions'],
            'all': ['dialog', 'flexbox', 'css-grid', 'promises', 'arrow-functions'],
        },
        'feature_details': {
            'css': [{'feature': 'flexbox', 'description': 'Flexbox', 'matched_properties': ['display: flex']}],
            'js': [{'feature': 'promises', 'description': 'Promises', 'matched_properties': ['new Promise']}],
            'html': [{'feature': 'dialog', 'description': 'Dialog element', 'matched_properties': ['<dialog>']}],
        },
        'unrecognized': {
            'html': ['custom-element'],
            'css': [],
            'js': ['someApi()'],
            'total': 2,
        },
        'recommendations': ['Consider polyfills for dialog element'],
    }


@pytest.fixture
def sample_failure_report():
    """Failed analysis dict."""
    return {'success': False, 'error': 'File not found: missing.css'}


@pytest.fixture
def sample_success_result(sample_success_report):
    """Pre-built AnalysisResult from the success report."""
    return AnalysisResult.from_dict(sample_success_report)


@pytest.fixture
def sample_failed_result():
    """Pre-built failed AnalysisResult."""
    return AnalysisResult(success=False, error='Something went wrong')
