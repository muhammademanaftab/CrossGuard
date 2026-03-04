"""Tests for baseline enrichment in AnalyzerService.analyze()."""

import json
from unittest.mock import patch, MagicMock

import pytest

from src.api.schemas import AnalysisRequest, AnalysisResult, BaselineSummary
from src.api.service import AnalyzerService


@pytest.fixture
def service():
    return AnalyzerService()


@pytest.fixture
def mock_report():
    """A minimal successful analysis report dict."""
    return {
        'success': True,
        'summary': {
            'total_features': 3,
            'html_features': 0,
            'css_features': 2,
            'js_features': 1,
            'critical_issues': 0,
        },
        'scores': {
            'grade': 'A',
            'risk_level': 'low',
            'simple_score': 95.0,
            'weighted_score': 93.0,
        },
        'browsers': {},
        'features': {
            'html': [],
            'css': ['css-grid', 'flexbox'],
            'js': ['promises'],
            'all': ['css-grid', 'flexbox', 'promises'],
        },
        'feature_details': {'css': [], 'js': [], 'html': []},
        'unrecognized': {'html': [], 'css': [], 'js': [], 'total': 0},
        'recommendations': [],
    }


class TestBaselineEnrichment:
    @patch('src.api.service.AnalyzerService._get_analyzer')
    def test_baseline_added_when_data_available(self, mock_get_analyzer, service, mock_report):
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_project.return_value = mock_report
        mock_get_analyzer.return_value = mock_analyzer

        mock_wf = MagicMock()
        mock_wf.has_data.return_value = True
        mock_wf.get_baseline_summary.return_value = {
            'widely_available': 2,
            'newly_available': 0,
            'limited': 1,
            'unknown': 0,
        }
        service._web_features = mock_wf

        request = AnalysisRequest(css_files=['test.css'])
        result = service.analyze(request)

        assert result.success is True
        assert result.baseline_summary is not None
        assert result.baseline_summary.widely_available == 2
        assert result.baseline_summary.limited == 1

    @patch('src.api.service.AnalyzerService._get_analyzer')
    def test_baseline_none_when_no_data(self, mock_get_analyzer, service, mock_report):
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_project.return_value = mock_report
        mock_get_analyzer.return_value = mock_analyzer

        mock_wf = MagicMock()
        mock_wf.has_data.return_value = False
        service._web_features = mock_wf

        request = AnalysisRequest(css_files=['test.css'])
        result = service.analyze(request)

        assert result.success is True
        assert result.baseline_summary is None

    @patch('src.api.service.AnalyzerService._get_analyzer')
    def test_baseline_none_on_failure(self, mock_get_analyzer, service):
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_project.return_value = {
            'success': False, 'error': 'Parse error'
        }
        mock_get_analyzer.return_value = mock_analyzer

        request = AnalysisRequest(css_files=['test.css'])
        result = service.analyze(request)

        assert result.success is False
        assert result.baseline_summary is None


class TestBaselineSummarySchema:
    def test_to_dict_includes_baseline(self):
        result = AnalysisResult(
            success=True,
            baseline_summary=BaselineSummary(
                widely_available=5,
                newly_available=2,
                limited=1,
                unknown=3,
            ),
        )
        d = result.to_dict()
        assert d['baseline_summary'] is not None
        assert d['baseline_summary']['widely_available'] == 5
        assert d['baseline_summary']['unknown'] == 3

    def test_to_dict_baseline_none(self):
        result = AnalysisResult(success=True)
        d = result.to_dict()
        assert d['baseline_summary'] is None

    def test_from_dict_with_baseline(self):
        data = {
            'success': True,
            'summary': {'total_features': 0, 'html_features': 0, 'css_features': 0, 'js_features': 0, 'critical_issues': 0},
            'scores': {'grade': 'A', 'risk_level': 'low', 'simple_score': 100, 'weighted_score': 100},
            'browsers': {},
            'features': {'html': [], 'css': [], 'js': [], 'all': []},
            'feature_details': {'css': [], 'js': [], 'html': []},
            'unrecognized': {'html': [], 'css': [], 'js': [], 'total': 0},
            'recommendations': [],
            'baseline_summary': {
                'widely_available': 10,
                'newly_available': 3,
                'limited': 2,
                'unknown': 1,
            },
        }
        result = AnalysisResult.from_dict(data)
        assert result.baseline_summary is not None
        assert result.baseline_summary.widely_available == 10

    def test_from_dict_without_baseline(self):
        data = {
            'success': True,
            'summary': {'total_features': 0, 'html_features': 0, 'css_features': 0, 'js_features': 0, 'critical_issues': 0},
            'scores': {'grade': 'A', 'risk_level': 'low', 'simple_score': 100, 'weighted_score': 100},
            'browsers': {},
            'features': {'html': [], 'css': [], 'js': [], 'all': []},
            'feature_details': {'css': [], 'js': [], 'html': []},
            'unrecognized': {'html': [], 'css': [], 'js': [], 'total': 0},
            'recommendations': [],
        }
        result = AnalysisResult.from_dict(data)
        assert result.baseline_summary is None


class TestServiceWebFeaturesAPIs:
    def test_update_web_features(self, service):
        mock_wf = MagicMock()
        mock_wf.download.return_value = True
        service._web_features = mock_wf

        assert service.update_web_features() is True
        mock_wf.download.assert_called_once()

    def test_get_baseline_status(self, service):
        from src.analyzer.web_features import BaselineInfo as WFBaselineInfo
        mock_wf = MagicMock()
        mock_wf.get_baseline_status.return_value = WFBaselineInfo('high', '2020-01-01', '2022-06-01')
        service._web_features = mock_wf

        result = service.get_baseline_status('css-grid')
        assert result is not None
        assert result['status'] == 'high'

    def test_get_baseline_status_unknown(self, service):
        mock_wf = MagicMock()
        mock_wf.get_baseline_status.return_value = None
        service._web_features = mock_wf

        result = service.get_baseline_status('nonexistent')
        assert result is None

    def test_has_web_features_data(self, service):
        mock_wf = MagicMock()
        mock_wf.has_data.return_value = True
        service._web_features = mock_wf
        assert service.has_web_features_data() is True
