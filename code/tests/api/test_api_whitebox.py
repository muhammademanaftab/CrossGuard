"""Whitebox tests for AnalyzerService internals.

Tests baseline enrichment logic for analysis results.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.api.schemas import AnalysisRequest


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
