"""Whitebox tests for AnalyzerService internals.

Tests singleton behavior, lazy loading, mocked dependency wiring,
reload mechanics, database management, statistics, and baseline enrichment.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

import src.api.service as service_module
from src.api.service import AnalyzerService, get_analyzer_service
from src.api.schemas import AnalysisRequest, AnalysisResult, DatabaseInfo, DatabaseUpdateResult


# ═══════════════════════════════════════════════════════════════════════
# Singleton
# ═══════════════════════════════════════════════════════════════════════

class TestSingleton:

    @pytest.mark.whitebox
    def test_returns_analyzer_service(self, reset_singleton):
        service_module._service_instance = None
        svc = get_analyzer_service()
        assert isinstance(svc, AnalyzerService)

    @pytest.mark.whitebox
    def test_returns_same_instance(self, reset_singleton):
        service_module._service_instance = None
        a = get_analyzer_service()
        b = get_analyzer_service()
        assert a is b

    @pytest.mark.whitebox
    def test_fresh_state(self, reset_singleton):
        service_module._service_instance = None
        svc = get_analyzer_service()
        assert svc._analyzer is None
        assert svc._database_updater is None


# ═══════════════════════════════════════════════════════════════════════
# Lazy Loading
# ═══════════════════════════════════════════════════════════════════════

class TestLazyLoading:

    @pytest.mark.whitebox
    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_analyzer_not_created_until_analyze(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.run_analysis.return_value = sample_success_report

        assert service._analyzer is None
        service.analyze(AnalysisRequest(html_files=["index.html"]))
        assert service._analyzer is not None

    @pytest.mark.whitebox
    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_reuses_analyzer_on_second_call(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.run_analysis.return_value = sample_success_report

        service.analyze(AnalysisRequest(css_files=["a.css"]))
        service.analyze(AnalysisRequest(css_files=["b.css"]))

        assert MockAnalyzer.call_count == 1


# ═══════════════════════════════════════════════════════════════════════
# Database Management
# ═══════════════════════════════════════════════════════════════════════

class TestDatabaseManagement:

    @pytest.mark.whitebox
    @patch('src.analyzer.database_updater.DatabaseUpdater')
    def test_get_database_info_success(self, MockUpdater, service):
        mock_instance = MockUpdater.return_value
        mock_instance.get_database_info.return_value = {
            'features_count': 570,
            'last_updated': 'Unknown',
            'is_git_repo': True,
        }
        info = service.get_database_info()
        assert isinstance(info, DatabaseInfo)
        assert info.features_count == 570

    @pytest.mark.whitebox
    @patch('src.analyzer.database_updater.DatabaseUpdater')
    def test_get_database_info_error(self, MockUpdater, service):
        mock_instance = MockUpdater.return_value
        mock_instance.get_database_info.side_effect = Exception("disk error")
        info = service.get_database_info()
        assert info.features_count == 0
        assert "Error" in info.last_updated

    @pytest.mark.whitebox
    @patch('src.analyzer.database_updater.DatabaseUpdater')
    def test_update_database_success(self, MockUpdater, service):
        mock_instance = MockUpdater.return_value
        mock_instance.update_database.return_value = {
            'success': True,
            'message': 'Updated',
            'no_changes': False,
        }
        with patch.object(service, '_reload_database'):
            result = service.update_database()
        assert isinstance(result, DatabaseUpdateResult)
        assert result.success is True

    @pytest.mark.whitebox
    @patch('src.analyzer.database_updater.DatabaseUpdater')
    def test_update_database_failure(self, MockUpdater, service):
        mock_instance = MockUpdater.return_value
        mock_instance.update_database.return_value = {
            'success': False,
            'message': 'Git error',
            'error': 'Could not pull',
        }
        result = service.update_database()
        assert result.success is False
        assert result.error == 'Could not pull'

    @pytest.mark.whitebox
    def test_reload_database_resets_analyzer(self, service):
        service._analyzer = MagicMock()
        with patch('src.analyzer.database.reload_database'):
            service._reload_database()
        assert service._analyzer is None

    @pytest.mark.whitebox
    def test_reload_custom_rules_resets_analyzer(self, service):
        service._analyzer = MagicMock()
        with patch('src.parsers.custom_rules_loader.reload_custom_rules'):
            service.reload_custom_rules()
        assert service._analyzer is None


# ═══════════════════════════════════════════════════════════════════════
# Statistics
# ═══════════════════════════════════════════════════════════════════════

class TestStatistics:

    @pytest.mark.whitebox
    @patch('src.database.statistics.get_statistics_service')
    def test_get_statistics(self, mock_get_svc, service):
        mock_svc = MagicMock()
        mock_svc.get_summary_statistics.return_value = {'total_analyses': 10}
        mock_get_svc.return_value = mock_svc

        stats = service.get_statistics()
        assert stats['total_analyses'] == 10

    @pytest.mark.whitebox
    @patch('src.database.statistics.get_statistics_service')
    def test_get_statistics_error(self, mock_get_svc, service):
        mock_get_svc.side_effect = Exception("fail")
        stats = service.get_statistics()
        assert stats['total_analyses'] == 0
        assert 'error' in stats

    @pytest.mark.whitebox
    @patch('src.database.statistics.get_statistics_service')
    def test_get_score_trend(self, mock_get_svc, service):
        mock_svc = MagicMock()
        mock_svc.get_score_trend.return_value = [{'date': '2026-01-01', 'avg_score': 85.0}]
        mock_get_svc.return_value = mock_svc

        trend = service.get_score_trend(days=7)
        assert len(trend) == 1
        assert trend[0]['avg_score'] == 85.0

    @pytest.mark.whitebox
    @patch('src.database.statistics.get_statistics_service')
    def test_get_top_problematic_features(self, mock_get_svc, service):
        mock_svc = MagicMock()
        mock_svc.get_top_problematic_features.return_value = [{'feature': 'dialog', 'count': 5}]
        mock_get_svc.return_value = mock_svc

        features = service.get_top_problematic_features(limit=5)
        assert features[0]['feature'] == 'dialog'


# ═══════════════════════════════════════════════════════════════════════
# Baseline Enrichment
# ═══════════════════════════════════════════════════════════════════════

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
        assert result.baseline_summary.widely_available == 2
        assert result.baseline_summary.limited == 1

    @pytest.mark.whitebox
    @patch('src.api.service.AnalyzerService._get_analyzer')
    def test_baseline_none_when_no_data(self, mock_get_analyzer, service, mock_report):
        mock_analyzer = MagicMock()
        mock_analyzer.run_analysis.return_value = mock_report
        mock_get_analyzer.return_value = mock_analyzer

        mock_wf = MagicMock()
        mock_wf.has_data.return_value = False
        service._web_features = mock_wf

        request = AnalysisRequest(css_files=['test.css'])
        result = service.analyze(request)

        assert result.success is True
        assert result.baseline_summary is None


# ═══════════════════════════════════════════════════════════════════════
# Web Features APIs
# ═══════════════════════════════════════════════════════════════════════

class TestServiceWebFeaturesAPIs:

    @pytest.mark.whitebox
    def test_update_web_features(self, service):
        mock_wf = MagicMock()
        mock_wf.download.return_value = True
        service._web_features = mock_wf

        assert service.update_web_features() is True
        mock_wf.download.assert_called_once()

    @pytest.mark.whitebox
    def test_get_baseline_status(self, service):
        from src.analyzer.web_features import BaselineInfo as WFBaselineInfo
        mock_wf = MagicMock()
        mock_wf.get_baseline_status.return_value = WFBaselineInfo('high', '2020-01-01', '2022-06-01')
        service._web_features = mock_wf

        result = service.get_baseline_status('css-grid')
        assert result is not None
        assert result['status'] == 'high'

    @pytest.mark.whitebox
    def test_get_baseline_status_unknown(self, service):
        mock_wf = MagicMock()
        mock_wf.get_baseline_status.return_value = None
        service._web_features = mock_wf

        assert service.get_baseline_status('nonexistent') is None

    @pytest.mark.whitebox
    def test_has_web_features_data(self, service):
        mock_wf = MagicMock()
        mock_wf.has_data.return_value = True
        service._web_features = mock_wf
        assert service.has_web_features_data() is True


# ═══════════════════════════════════════════════════════════════════════
# Custom Rules (internal wiring)
# ═══════════════════════════════════════════════════════════════════════

class TestCustomRules:

    @pytest.mark.whitebox
    def test_get_custom_rules_returns_dict(self, service):
        rules = service.get_custom_rules()
        assert isinstance(rules, dict)

    @pytest.mark.whitebox
    def test_save_and_reload(self, service, tmp_path, monkeypatch):
        import src.parsers.custom_rules_loader as loader_mod
        original_path = loader_mod.CUSTOM_RULES_PATH
        test_path = tmp_path / "custom_rules.json"
        test_path.write_text('{"css": {}, "javascript": {}, "html": {"elements": {}, "attributes": {}, "input_types": {}, "attribute_values": {}}}')
        monkeypatch.setattr(loader_mod, 'CUSTOM_RULES_PATH', test_path)

        rules = {
            'css': {'test-feature': {'patterns': ['test-prop'], 'description': 'Test'}},
            'javascript': {},
            'html': {'elements': {}, 'attributes': {}, 'input_types': {}, 'attribute_values': {}},
        }
        result = service.save_custom_rules(rules)
        assert result is True

        with open(test_path) as f:
            saved = json.load(f)
        assert 'test-feature' in saved['css']

        monkeypatch.setattr(loader_mod, 'CUSTOM_RULES_PATH', original_path)
