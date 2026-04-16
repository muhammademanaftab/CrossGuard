"""Whitebox tests for AnalyzerService internals.

Tests singleton behavior, lazy loading, database management,
baseline enrichment, and reload mechanics.
"""

import pytest
from unittest.mock import patch, MagicMock

import src.api.service as service_module
from src.api.service import get_analyzer_service
from src.api.schemas import AnalysisRequest


# ===================================================================
# Singleton
# ===================================================================

class TestSingleton:

    @pytest.mark.whitebox
    def test_returns_same_instance(self, reset_singleton):
        service_module._service_instance = None
        a = get_analyzer_service()
        b = get_analyzer_service()
        assert a is b


# ===================================================================
# Lazy Loading
# ===================================================================

class TestLazyLoading:

    @pytest.mark.whitebox
    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_analyzer_not_created_until_analyze(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.run_analysis.return_value = sample_success_report

        assert service._analyzer is None
        service.analyze(AnalysisRequest(html_files=["index.html"]))
        assert service._analyzer is not None


# ===================================================================
# Baseline Enrichment
# ===================================================================

class TestBaselineEnrichment:

    @pytest.fixture
    def mock_report(self):
        return {
            'success': True,
            'summary': {
                'total_features': 3, 'html_features': 0,
                'css_features': 2, 'js_features': 1, 'critical_issues': 0,
            },
            'scores': {
                'grade': 'A', 'risk_level': 'low',
                'simple_score': 95.0, 'weighted_score': 93.0,
            },
            'browsers': {},
            'features': {
                'html': [], 'css': ['css-grid', 'flexbox'],
                'js': ['promises'], 'all': ['css-grid', 'flexbox', 'promises'],
            },
            'feature_details': {'css': [], 'js': [], 'html': []},
            'unrecognized': {'html': [], 'css': [], 'js': [], 'total': 0},
            'recommendations': [],
        }

    @pytest.mark.whitebox
    @patch('src.api.service.AnalyzerService._get_analyzer')
    def test_baseline_added_when_data_available(self, mock_get_analyzer, service, mock_report):
        mock_analyzer = MagicMock()
        mock_analyzer.run_analysis.return_value = mock_report
        mock_get_analyzer.return_value = mock_analyzer

        mock_wf = MagicMock()
        mock_wf.has_data.return_value = True
        mock_wf.get_baseline_summary.return_value = {
            'widely_available': 2, 'newly_available': 0,
            'limited': 1, 'unknown': 0,
        }
        service._web_features = mock_wf

        request = AnalysisRequest(css_files=['test.css'])
        result = service.analyze(request)

        assert result.success is True
        assert result.baseline_summary is not None
        assert result.baseline_summary['widely_available'] == 2
