"""Tests for new AnalyzerService methods added during refactoring.

Covers: export, feature utilities, custom rules, config, and classify_file.
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from src.api.service import AnalyzerService
from src.api.schemas import ExportRequest, AnalysisResult


# ─── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def service():
    return AnalyzerService()


@pytest.fixture
def sample_report():
    return {
        'success': True,
        'summary': {'total_features': 3, 'html_features': 1,
                     'css_features': 1, 'js_features': 1, 'critical_issues': 0},
        'scores': {'grade': 'A', 'simple_score': 95.0, 'weighted_score': 93.0,
                   'risk_level': 'low'},
        'browsers': {'chrome': {'version': '120', 'supported': 3,
                                 'partial': 0, 'unsupported': 0,
                                 'compatibility_percentage': 100.0,
                                 'unsupported_features': [], 'partial_features': []}},
        'features': {'html': [], 'css': [], 'js': [], 'all': []},
        'feature_details': {'css': [], 'js': [], 'html': []},
        'unrecognized': {'html': [], 'css': [], 'js': [], 'total': 0},
        'recommendations': [],
    }


@pytest.fixture
def sample_result(sample_report):
    return AnalysisResult.from_dict(sample_report)


# ═══════════════════════════════════════════════════════════════════════
# ExportRequest schema
# ═══════════════════════════════════════════════════════════════════════

class TestExportRequest:
    def test_valid_json_format(self, sample_result):
        req = ExportRequest(format='json', result=sample_result)
        assert req.format == 'json'

    def test_valid_pdf_format(self):
        req = ExportRequest(format='pdf', analysis_id=1)
        assert req.format == 'pdf'

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported export format"):
            ExportRequest(format='xml', analysis_id=1)

    def test_no_source_raises(self):
        with pytest.raises(ValueError, match="Either analysis_id or result"):
            ExportRequest(format='json')


# ═══════════════════════════════════════════════════════════════════════
# Export methods
# ═══════════════════════════════════════════════════════════════════════

class TestExportToJson:
    def test_returns_dict_without_path(self, service, sample_report):
        result = service.export_to_json(sample_report)
        assert isinstance(result, dict)
        assert result['generated_by'] == 'Cross Guard'

    def test_writes_file_with_path(self, service, sample_report, tmp_path):
        out = str(tmp_path / "test.json")
        result = service.export_to_json(sample_report, output_path=out)
        assert result == out
        assert os.path.isfile(out)

    def test_accepts_analysis_result(self, service, sample_result):
        result = service.export_to_json(sample_result)
        assert isinstance(result, dict)
        assert result['success'] is True

    @patch('src.api.service.AnalyzerService.get_analysis_by_id')
    def test_accepts_analysis_id(self, mock_get, service, sample_report):
        mock_get.return_value = sample_report
        result = service.export_to_json(42)
        assert isinstance(result, dict)
        mock_get.assert_called_once_with(42)

    @patch('src.api.service.AnalyzerService.get_analysis_by_id')
    def test_raises_for_missing_id(self, mock_get, service):
        mock_get.return_value = None
        with pytest.raises(ValueError, match="not found"):
            service.export_to_json(999)

    def test_raises_for_bad_type(self, service):
        with pytest.raises(TypeError):
            service.export_to_json("bad input")


class TestExportToPdf:
    def test_creates_pdf(self, service, sample_report, tmp_path):
        out = str(tmp_path / "test.pdf")
        result = service.export_to_pdf(sample_report, output_path=out)
        assert result == out
        assert os.path.isfile(out)


# ═══════════════════════════════════════════════════════════════════════
# Feature utility methods
# ═══════════════════════════════════════════════════════════════════════

class TestFeatureUtilities:
    def test_get_feature_display_name_known(self, service):
        name = service.get_feature_display_name('css-grid')
        assert name == 'CSS Grid Layout'

    def test_get_feature_display_name_unknown(self, service):
        name = service.get_feature_display_name('some-unknown-feature')
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_fix_suggestion_known(self, service):
        suggestion = service.get_fix_suggestion('css-grid')
        assert suggestion is not None
        assert 'fallback' in suggestion.lower() or 'support' in suggestion.lower()

    def test_get_fix_suggestion_unknown(self, service):
        result = service.get_fix_suggestion('nonexistent-feature')
        assert result is None

    def test_is_ml_enabled(self, service):
        result = service.is_ml_enabled()
        assert isinstance(result, bool)


class TestClassifyFile:
    def test_html(self, service):
        assert service.classify_file('index.html') == 'html'
        assert service.classify_file('page.htm') == 'html'

    def test_css(self, service):
        assert service.classify_file('style.css') == 'css'

    def test_js(self, service):
        assert service.classify_file('app.js') == 'js'
        assert service.classify_file('module.mjs') == 'js'
        assert service.classify_file('component.jsx') == 'js'
        assert service.classify_file('main.ts') == 'js'
        assert service.classify_file('app.tsx') == 'js'

    def test_unknown(self, service):
        assert service.classify_file('readme.md') is None
        assert service.classify_file('image.png') is None

    def test_path_with_dirs(self, service):
        assert service.classify_file('/some/path/to/style.css') == 'css'


# ═══════════════════════════════════════════════════════════════════════
# Custom rules methods
# ═══════════════════════════════════════════════════════════════════════

class TestCustomRulesMethods:
    def test_get_custom_rules_returns_dict(self, service):
        rules = service.get_custom_rules()
        assert isinstance(rules, dict)
        # Should have top-level keys
        assert 'css' in rules or 'javascript' in rules or 'html' in rules

    def test_is_user_rule_false_for_builtin(self, service):
        # A feature from built-in maps should not be a user rule
        assert service.is_user_rule('css', 'css-grid') is False

    def test_save_and_reload(self, service, tmp_path, monkeypatch):
        """save_custom_rules() writes and reloads."""
        # Patch the custom rules path to tmp
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

        # Verify file was written
        with open(test_path) as f:
            saved = json.load(f)
        assert 'test-feature' in saved['css']

        # Restore
        monkeypatch.setattr(loader_mod, 'CUSTOM_RULES_PATH', original_path)


# ═══════════════════════════════════════════════════════════════════════
# Config method
# ═══════════════════════════════════════════════════════════════════════

class TestLoadConfig:
    def test_load_config_returns_dict(self, service):
        config = service.load_config()
        assert isinstance(config, dict)
        assert 'browsers' in config

    def test_load_config_from_file(self, service, tmp_path):
        config_data = {'browsers': {'chrome': '100'}, 'output': 'json'}
        config_file = tmp_path / 'crossguard.config.json'
        config_file.write_text(json.dumps(config_data))

        config = service.load_config(config_path=str(config_file))
        assert config['browsers']['chrome'] == '100'
