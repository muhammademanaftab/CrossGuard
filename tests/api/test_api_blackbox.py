"""Blackbox tests for AnalyzerService public API.

Tests analyze, CRUD operations, export, and utility methods
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
    ExportRequest,
)


# ===================================================================
# AnalysisRequest schema
# ===================================================================

class TestAnalysisRequest:

    @pytest.mark.blackbox
    def test_total_files_counts_all_types(self):
        req = AnalysisRequest(
            html_files=["a.html", "b.html"],
            css_files=["c.css"],
            js_files=["d.js", "e.js", "f.js"],
        )
        assert req.total_files() == 6


# ===================================================================
# analyze()
# ===================================================================

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
        assert result.summary['total_features'] == 5
        mock_instance.run_analysis.assert_called_once()

    @pytest.mark.blackbox
    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_exception_returns_failure(self, MockAnalyzer, service):
        mock_instance = MockAnalyzer.return_value
        mock_instance.run_analysis.side_effect = RuntimeError("boom")

        request = AnalysisRequest(css_files=["style.css"])
        result = service.analyze(request)

        assert result.success is False
        assert "boom" in result.error


# ===================================================================
# History CRUD
# ===================================================================

class TestHistory:

    @pytest.mark.blackbox
    @patch('src.database.repositories.save_analysis_from_result')
    def test_save_success(self, mock_save, service, sample_success_result):
        mock_save.return_value = 42
        aid = service.save_analysis_to_history(sample_success_result, file_name='test.css')
        assert aid == 42

    @pytest.mark.blackbox
    @patch('src.database.repositories.AnalysisRepository')
    def test_get_history(self, MockRepo, service):
        mock_analysis = MagicMock()
        mock_analysis.to_dict.return_value = {'id': 1, 'file_name': 'test.css'}
        MockRepo.return_value.get_all_analyses.return_value = [mock_analysis]

        history = service.get_analysis_history(limit=10)
        assert len(history) == 1
        assert history[0]['id'] == 1



# ===================================================================
# Settings / Bookmarks / Tags CRUD (essential)
# ===================================================================

class TestSettings:

    @pytest.mark.blackbox
    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting(self, MockRepo, service):
        MockRepo.return_value.get.return_value = 'dark'
        assert service.get_setting('theme', 'light') == 'dark'

    @pytest.mark.blackbox
    @patch('src.database.repositories.SettingsRepository')
    def test_set_setting(self, MockRepo, service):
        assert service.set_setting('theme', 'dark') is True
        MockRepo.return_value.set.assert_called_once_with('theme', 'dark')


class TestBookmarks:

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


class TestTags:

    @pytest.mark.blackbox
    @patch('src.database.repositories.TagsRepository')
    def test_create_tag(self, MockRepo, service):
        MockRepo.return_value.create_tag.return_value = 7
        assert service.create_tag('bugfix', '#ff0000') == 7

    @pytest.mark.blackbox
    @patch('src.database.repositories.TagsRepository')
    def test_add_tag_to_analysis(self, MockRepo, service):
        MockRepo.return_value.add_tag_to_analysis.return_value = True
        assert service.add_tag_to_analysis(1, 2) is True


# ===================================================================
# Export
# ===================================================================

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
