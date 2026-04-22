"""Blackbox tests for AnalyzerService public API.

Tests analyze, CRUD operations, export, and utility methods
through the public interface with mocked backend dependencies.
"""

import os
import pytest
from unittest.mock import patch

from src.api.service import AnalyzerService
from src.api.schemas import AnalysisRequest


# ===================================================================
# analyze()
# ===================================================================

class TestAnalyze:

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


# ===================================================================
# History CRUD
# ===================================================================

class TestHistory:

    @pytest.mark.blackbox
    @patch('src.api.service.save_analysis_from_result')
    def test_save_success(self, mock_save, service, sample_success_result):
        mock_save.return_value = 42
        aid = service.save_analysis_to_history(sample_success_result, file_name='test.css')
        assert aid == 42


# ===================================================================
# Settings / Bookmarks (essential)
# ===================================================================

class TestSettings:

    @pytest.mark.blackbox
    @patch('src.api.service.SettingsRepository')
    def test_set_setting(self, MockRepo, service):
        assert service.set_setting('theme', 'dark') is True
        MockRepo.return_value.set.assert_called_once_with('theme', 'dark')


class TestBookmarks:

    @pytest.mark.blackbox
    @patch('src.api.service.BookmarksRepository')
    def test_toggle_bookmark_adds_when_not_bookmarked(self, MockRepo, service):
        repo_instance = MockRepo.return_value
        repo_instance.is_bookmarked.return_value = False
        result = service.toggle_bookmark(1, note='test')
        assert result is True
        repo_instance.add_bookmark.assert_called_once_with(1, 'test')


# ===================================================================
# Export
# ===================================================================

class TestExportToJson:

    @pytest.mark.blackbox
    def test_writes_file_with_path(self, service, sample_success_report, tmp_path):
        out = str(tmp_path / "test.json")
        result = service.export_to_json(sample_success_report, output_path=out)
        assert result == out
        assert os.path.isfile(out)
