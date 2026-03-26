"""Blackbox tests for AnalyzerService public API.

Tests analyze, CRUD operations, export, schemas, and utility methods
through the public interface with mocked backend dependencies.
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from src.api.service import AnalyzerService
from src.api.schemas import (
    AnalysisRequest,
    AnalysisResult,
    BaselineSummary,
    ExportRequest,
)


# ═══════════════════════════════════════════════════════════════════════
# AnalysisRequest schema
# ═══════════════════════════════════════════════════════════════════════

class TestAnalysisRequest:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("kwargs,expected", [
        ({}, False),
        ({"html_files": ["index.html"]}, True),
        ({"css_files": ["style.css"]}, True),
        ({"js_files": ["app.js"]}, True),
    ])
    def test_has_files(self, kwargs, expected):
        assert AnalysisRequest(**kwargs).has_files() is expected

    @pytest.mark.blackbox
    def test_total_files_counts_all_types(self):
        req = AnalysisRequest(
            html_files=["a.html", "b.html"],
            css_files=["c.css"],
            js_files=["d.js", "e.js", "f.js"],
        )
        assert req.total_files() == 6

    @pytest.mark.blackbox
    def test_default_factories_are_independent(self):
        a = AnalysisRequest()
        b = AnalysisRequest()
        a.html_files.append("x.html")
        assert b.html_files == []


# ═══════════════════════════════════════════════════════════════════════
# AnalysisResult serialisation
# ═══════════════════════════════════════════════════════════════════════

class TestAnalysisResultFromDict:

    @pytest.mark.blackbox
    def test_success_populates_all_fields(self, sample_success_report):
        result = AnalysisResult.from_dict(sample_success_report)
        assert result.success is True
        assert result.error is None
        assert result.summary.total_features == 5
        assert result.scores.grade == "B"
        assert "chrome" in result.browsers
        assert "safari" in result.browsers

    @pytest.mark.blackbox
    def test_failure_dict(self, sample_failure_report):
        result = AnalysisResult.from_dict(sample_failure_report)
        assert result.success is False
        assert "File not found" in result.error

    @pytest.mark.blackbox
    def test_empty_dict_is_failure(self):
        result = AnalysisResult.from_dict({})
        assert result.success is False

    @pytest.mark.blackbox
    def test_roundtrip_preserves_data(self, sample_success_report):
        result = AnalysisResult.from_dict(sample_success_report)
        d = result.to_dict()
        assert d['summary']['total_features'] == 5
        assert d['scores']['grade'] == 'B'
        assert d['browsers']['chrome']['compatibility_percentage'] == 90.0
        assert 'dialog' in d['features']['html']

    @pytest.mark.blackbox
    def test_failed_result_to_dict_minimal(self, sample_failed_result):
        d = sample_failed_result.to_dict()
        assert d['success'] is False
        assert 'error' in d
        assert 'summary' not in d

    @pytest.mark.blackbox
    def test_baseline_roundtrip(self):
        """from_dict -> to_dict preserves baseline data."""
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
                'widely_available': 10, 'newly_available': 3, 'limited': 2, 'unknown': 1,
            },
        }
        result = AnalysisResult.from_dict(data)
        assert result.baseline_summary.widely_available == 10
        d = result.to_dict()
        assert d['baseline_summary']['widely_available'] == 10

    @pytest.mark.blackbox
    def test_baseline_none_when_absent(self):
        result = AnalysisResult(success=True)
        assert result.baseline_summary is None
        assert result.to_dict()['baseline_summary'] is None


# ═══════════════════════════════════════════════════════════════════════
# analyze()
# ═══════════════════════════════════════════════════════════════════════

class TestAnalyze:

    @pytest.mark.blackbox
    def test_no_files_returns_failure(self, service, empty_request):
        result = service.analyze(empty_request)
        assert result.success is False
        assert "No files" in result.error

    @pytest.mark.blackbox
    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_success_delegates_to_analyzer(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.run_analysis.return_value = sample_success_report

        request = AnalysisRequest(css_files=["style.css"])
        result = service.analyze(request)

        assert result.success is True
        assert result.summary.total_features == 5
        mock_instance.run_analysis.assert_called_once()

    @pytest.mark.blackbox
    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_uses_custom_browsers(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.run_analysis.return_value = sample_success_report

        custom_browsers = {'chrome': '100'}
        request = AnalysisRequest(js_files=["app.js"], target_browsers=custom_browsers)
        service.analyze(request)

        call_kwargs = mock_instance.run_analysis.call_args[1]
        assert call_kwargs['target_browsers'] == custom_browsers

    @pytest.mark.blackbox
    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_exception_returns_failure(self, MockAnalyzer, service):
        mock_instance = MockAnalyzer.return_value
        mock_instance.run_analysis.side_effect = RuntimeError("boom")

        request = AnalysisRequest(css_files=["style.css"])
        result = service.analyze(request)

        assert result.success is False
        assert "boom" in result.error


# ═══════════════════════════════════════════════════════════════════════
# History CRUD
# ═══════════════════════════════════════════════════════════════════════

class TestHistory:

    @pytest.mark.blackbox
    @patch('src.database.repositories.save_analysis_from_result')
    def test_save_success(self, mock_save, service, sample_success_result):
        mock_save.return_value = 42
        aid = service.save_analysis_to_history(sample_success_result, file_name='test.css')
        assert aid == 42

    @pytest.mark.blackbox
    def test_save_failed_result_returns_none(self, service, sample_failed_result):
        aid = service.save_analysis_to_history(sample_failed_result)
        assert aid is None

    @pytest.mark.blackbox
    @patch('src.database.repositories.AnalysisRepository')
    def test_get_history(self, MockRepo, service):
        mock_analysis = MagicMock()
        mock_analysis.to_dict.return_value = {'id': 1, 'file_name': 'test.css'}
        MockRepo.return_value.get_all_analyses.return_value = [mock_analysis]

        history = service.get_analysis_history(limit=10)
        assert len(history) == 1
        assert history[0]['id'] == 1

    @pytest.mark.blackbox
    @patch('src.database.repositories.AnalysisRepository')
    def test_delete(self, MockRepo, service):
        MockRepo.return_value.delete_analysis.return_value = True
        assert service.delete_from_history(1) is True

    @pytest.mark.blackbox
    @patch('src.database.repositories.AnalysisRepository')
    def test_clear_history(self, MockRepo, service):
        MockRepo.return_value.clear_all.return_value = 10
        assert service.clear_history() is True


# ═══════════════════════════════════════════════════════════════════════
# Settings CRUD
# ═══════════════════════════════════════════════════════════════════════

class TestSettings:

    @pytest.mark.blackbox
    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting(self, MockRepo, service):
        MockRepo.return_value.get.return_value = 'dark'
        assert service.get_setting('theme', 'light') == 'dark'

    @pytest.mark.blackbox
    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting_error_returns_default(self, MockRepo, service):
        MockRepo.return_value.get.side_effect = Exception("fail")
        assert service.get_setting('theme', 'light') == 'light'

    @pytest.mark.blackbox
    @patch('src.database.repositories.SettingsRepository')
    def test_set_setting(self, MockRepo, service):
        assert service.set_setting('theme', 'dark') is True
        MockRepo.return_value.set.assert_called_once_with('theme', 'dark')


# ═══════════════════════════════════════════════════════════════════════
# Bookmarks CRUD
# ═══════════════════════════════════════════════════════════════════════

class TestBookmarks:

    @pytest.mark.blackbox
    @patch('src.database.repositories.BookmarksRepository')
    def test_add_bookmark(self, MockRepo, service):
        assert service.add_bookmark(1, note='important') is True
        MockRepo.return_value.add_bookmark.assert_called_once_with(1, 'important')

    @pytest.mark.blackbox
    @patch('src.database.repositories.BookmarksRepository')
    def test_toggle_bookmark_adds_when_not_bookmarked(self, MockRepo, service):
        repo_instance = MockRepo.return_value
        repo_instance.is_bookmarked.return_value = False
        result = service.toggle_bookmark(1, note='test')
        assert result is True
        repo_instance.add_bookmark.assert_called_once_with(1, 'test')

    @pytest.mark.blackbox
    @patch('src.database.repositories.BookmarksRepository')
    def test_toggle_bookmark_removes_when_bookmarked(self, MockRepo, service):
        repo_instance = MockRepo.return_value
        repo_instance.is_bookmarked.return_value = True
        result = service.toggle_bookmark(1)
        assert result is False
        repo_instance.remove_bookmark.assert_called_once_with(1)


# ═══════════════════════════════════════════════════════════════════════
# Tags CRUD
# ═══════════════════════════════════════════════════════════════════════

class TestTags:

    @pytest.mark.blackbox
    @patch('src.database.repositories.TagsRepository')
    def test_create_tag(self, MockRepo, service):
        MockRepo.return_value.create_tag.return_value = 7
        assert service.create_tag('bugfix', '#ff0000') == 7

    @pytest.mark.blackbox
    @patch('src.database.repositories.TagsRepository')
    def test_delete_tag(self, MockRepo, service):
        MockRepo.return_value.delete_tag.return_value = True
        assert service.delete_tag(1) is True

    @pytest.mark.blackbox
    @patch('src.database.repositories.TagsRepository')
    def test_add_tag_to_analysis(self, MockRepo, service):
        MockRepo.return_value.add_tag_to_analysis.return_value = True
        assert service.add_tag_to_analysis(1, 2) is True

    @pytest.mark.blackbox
    @patch('src.database.repositories.TagsRepository')
    def test_get_tags_for_analysis(self, MockRepo, service):
        MockRepo.return_value.get_tags_for_analysis.return_value = [{'id': 1}]
        tags = service.get_tags_for_analysis(10)
        assert len(tags) == 1


# ═══════════════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════════════

class TestExportRequest:

    @pytest.mark.blackbox
    def test_valid_json_format(self, sample_success_result):
        req = ExportRequest(format='json', result=sample_success_result)
        assert req.format == 'json'

    @pytest.mark.blackbox
    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported export format"):
            ExportRequest(format='xml', analysis_id=1)

    @pytest.mark.blackbox
    def test_no_source_raises(self):
        with pytest.raises(ValueError, match="Either analysis_id or result"):
            ExportRequest(format='json')


class TestExportToJson:

    @pytest.mark.blackbox
    def test_returns_dict_without_path(self, service, sample_success_report):
        result = service.export_to_json(sample_success_report)
        assert isinstance(result, dict)
        assert result['generated_by'] == 'Cross Guard'

    @pytest.mark.blackbox
    def test_writes_file_with_path(self, service, sample_success_report, tmp_path):
        out = str(tmp_path / "test.json")
        result = service.export_to_json(sample_success_report, output_path=out)
        assert result == out
        assert os.path.isfile(out)

    @pytest.mark.blackbox
    def test_raises_for_bad_type(self, service):
        with pytest.raises(TypeError):
            service.export_to_json("bad input")


class TestExportToPdf:

    @pytest.mark.blackbox
    def test_creates_pdf(self, service, sample_success_report, tmp_path):
        out = str(tmp_path / "test.pdf")
        result = service.export_to_pdf(sample_success_report, output_path=out)
        assert result == out
        assert os.path.isfile(out)


# ═══════════════════════════════════════════════════════════════════════
# Utility methods
# ═══════════════════════════════════════════════════════════════════════

class TestFeatureUtilities:

    @pytest.mark.blackbox
    def test_get_feature_display_name_known(self, service):
        name = service.get_feature_display_name('css-grid')
        assert name == 'CSS Grid Layout'

    @pytest.mark.blackbox
    def test_get_fix_suggestion_known(self, service):
        suggestion = service.get_fix_suggestion('css-grid')
        assert suggestion is not None

    @pytest.mark.blackbox
    def test_get_fix_suggestion_unknown(self, service):
        assert service.get_fix_suggestion('nonexistent-feature') is None


class TestClassifyFile:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("filename,expected", [
        ('index.html', 'html'),
        ('style.css', 'css'),
        ('app.js', 'js'),
        ('module.mjs', 'js'),
        ('component.jsx', 'js'),
        ('main.ts', 'js'),
        ('readme.md', None),
        ('image.png', None),
    ])
    def test_classify_file(self, service, filename, expected):
        assert service.classify_file(filename) == expected


# ═══════════════════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════════════════

class TestLoadConfig:

    @pytest.mark.blackbox
    def test_load_config_returns_dict(self, service):
        config = service.load_config()
        assert isinstance(config, dict)
        assert 'browsers' in config

    @pytest.mark.blackbox
    def test_load_config_from_file(self, service, tmp_path):
        config_data = {'browsers': {'chrome': '100'}, 'output': 'json'}
        config_file = tmp_path / 'crossguard.config.json'
        config_file.write_text(json.dumps(config_data))

        config = service.load_config(config_path=str(config_file))
        assert config['browsers']['chrome'] == '100'
