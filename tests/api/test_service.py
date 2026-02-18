"""Unit tests for AnalyzerService with mocked dependencies.

Every backend dependency (analyzer, database repos, statistics, settings,
bookmarks, tags) is mocked so tests run fast and in isolation.
"""

import pytest
from unittest.mock import patch, MagicMock

import src.api.service as service_module
from src.api.service import AnalyzerService, get_analyzer_service
from src.api.schemas import (
    AnalysisRequest,
    AnalysisResult,
    DatabaseInfo,
    DatabaseUpdateResult,
)


# ═══════════════════════════════════════════════════════════════════════
# Singleton
# ═══════════════════════════════════════════════════════════════════════

class TestSingleton:
    """get_analyzer_service() returns and reuses a singleton."""

    def test_returns_analyzer_service(self, reset_singleton):
        service_module._service_instance = None
        svc = get_analyzer_service()
        assert isinstance(svc, AnalyzerService)

    def test_returns_same_instance(self, reset_singleton):
        service_module._service_instance = None
        a = get_analyzer_service()
        b = get_analyzer_service()
        assert a is b

    def test_fresh_state(self, reset_singleton):
        service_module._service_instance = None
        svc = get_analyzer_service()
        assert svc._analyzer is None
        assert svc._database_updater is None


# ═══════════════════════════════════════════════════════════════════════
# analyze()
# ═══════════════════════════════════════════════════════════════════════

class TestAnalyze:
    """service.analyze() delegates to CrossGuardAnalyzer."""

    def test_no_files_returns_failure(self, service, empty_request):
        result = service.analyze(empty_request)
        assert result.success is False
        assert "No files" in result.error

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_success_delegates_to_analyzer(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.return_value = sample_success_report

        request = AnalysisRequest(css_files=["style.css"])
        result = service.analyze(request)

        assert result.success is True
        assert result.summary.total_features == 5
        mock_instance.analyze_project.assert_called_once()

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_uses_default_browsers_when_not_specified(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.return_value = sample_success_report

        request = AnalysisRequest(html_files=["index.html"])
        service.analyze(request)

        call_kwargs = mock_instance.analyze_project.call_args[1]
        assert call_kwargs['target_browsers'] == service.DEFAULT_BROWSERS

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_uses_custom_browsers_when_specified(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.return_value = sample_success_report

        custom_browsers = {'chrome': '100'}
        request = AnalysisRequest(js_files=["app.js"], target_browsers=custom_browsers)
        service.analyze(request)

        call_kwargs = mock_instance.analyze_project.call_args[1]
        assert call_kwargs['target_browsers'] == custom_browsers

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_exception_returns_failure(self, MockAnalyzer, service):
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.side_effect = RuntimeError("boom")

        request = AnalysisRequest(css_files=["style.css"])
        result = service.analyze(request)

        assert result.success is False
        assert "boom" in result.error

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_lazy_loads_analyzer(self, MockAnalyzer, service, sample_success_report):
        """Analyzer is not created until analyze() is called."""
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.return_value = sample_success_report

        assert service._analyzer is None
        service.analyze(AnalysisRequest(html_files=["index.html"]))
        assert service._analyzer is not None

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_reuses_analyzer_on_second_call(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.return_value = sample_success_report

        service.analyze(AnalysisRequest(css_files=["a.css"]))
        service.analyze(AnalysisRequest(css_files=["b.css"]))

        # CrossGuardAnalyzer() should only be instantiated once
        assert MockAnalyzer.call_count == 1

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_failure_report_from_analyzer(self, MockAnalyzer, service, sample_failure_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.return_value = sample_failure_report

        result = service.analyze(AnalysisRequest(js_files=["app.js"]))
        assert result.success is False


# ═══════════════════════════════════════════════════════════════════════
# analyze_files()
# ═══════════════════════════════════════════════════════════════════════

class TestAnalyzeFiles:
    """analyze_files() convenience wrapper."""

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_wraps_analyze(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.return_value = sample_success_report

        result = service.analyze_files(css_files=["style.css"])
        assert result.success is True

    def test_none_args_become_empty_lists(self, service):
        """Passing None for file lists should not crash."""
        result = service.analyze_files()
        assert result.success is False
        assert "No files" in result.error

    @patch('src.analyzer.main.CrossGuardAnalyzer')
    def test_passes_target_browsers(self, MockAnalyzer, service, sample_success_report):
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_project.return_value = sample_success_report

        browsers = {'firefox': '100'}
        service.analyze_files(html_files=["a.html"], target_browsers=browsers)
        call_kwargs = mock_instance.analyze_project.call_args[1]
        assert call_kwargs['target_browsers'] == browsers


# ═══════════════════════════════════════════════════════════════════════
# Browser Config
# ═══════════════════════════════════════════════════════════════════════

class TestBrowserConfig:
    """get_default_browsers() and get_available_browsers()."""

    def test_get_default_browsers_returns_copy(self, service):
        a = service.get_default_browsers()
        b = service.get_default_browsers()
        assert a == b
        assert a is not b  # Must be a copy

    def test_default_browsers_has_expected_keys(self, service):
        browsers = service.get_default_browsers()
        for key in ('chrome', 'firefox', 'safari', 'edge'):
            assert key in browsers

    def test_get_available_browsers(self, service):
        available = service.get_available_browsers()
        assert isinstance(available, list)
        assert 'chrome' in available
        assert 'edge' in available


# ═══════════════════════════════════════════════════════════════════════
# _score_to_grade()
# ═══════════════════════════════════════════════════════════════════════

class TestScoreToGrade:
    """_score_to_grade() boundary conditions."""

    @pytest.mark.parametrize("score,grade", [
        (100.0, 'A'),
        (90.0, 'A'),
        (89.9, 'B'),
        (80.0, 'B'),
        (79.9, 'C'),
        (70.0, 'C'),
        (69.9, 'D'),
        (60.0, 'D'),
        (59.9, 'F'),
        (0.0, 'F'),
    ])
    def test_grade_boundaries(self, service, score, grade):
        assert service._score_to_grade(score) == grade


# ═══════════════════════════════════════════════════════════════════════
# Database Management
# ═══════════════════════════════════════════════════════════════════════

class TestDatabaseManagement:
    """get_database_info(), update_database(), _reload_database(), reload_custom_rules()."""

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

    @patch('src.analyzer.database_updater.DatabaseUpdater')
    def test_get_database_info_error(self, MockUpdater, service):
        mock_instance = MockUpdater.return_value
        mock_instance.get_database_info.side_effect = Exception("disk error")
        info = service.get_database_info()
        assert info.features_count == 0
        assert "Error" in info.last_updated

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

    @patch('src.analyzer.database_updater.DatabaseUpdater')
    def test_update_database_no_changes(self, MockUpdater, service):
        mock_instance = MockUpdater.return_value
        mock_instance.update_database.return_value = {
            'success': True,
            'message': 'Already up to date',
            'no_changes': True,
        }
        result = service.update_database()
        assert result.success is True
        assert result.no_changes is True

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

    def test_reload_database_resets_analyzer(self, service):
        """_reload_database() sets self._analyzer = None."""
        service._analyzer = MagicMock()
        with patch('src.analyzer.database.reload_database'):
            service._reload_database()
        assert service._analyzer is None

    def test_reload_custom_rules_resets_analyzer(self, service):
        """reload_custom_rules() sets self._analyzer = None."""
        service._analyzer = MagicMock()
        with patch('src.parsers.custom_rules_loader.reload_custom_rules'):
            service.reload_custom_rules()
        assert service._analyzer is None


# ═══════════════════════════════════════════════════════════════════════
# History
# ═══════════════════════════════════════════════════════════════════════

class TestHistory:
    """History CRUD via mocked AnalysisRepository."""

    @patch('src.database.repositories.save_analysis_from_result')
    def test_save_success(self, mock_save, service, sample_success_result):
        mock_save.return_value = 42
        aid = service.save_analysis_to_history(sample_success_result, file_name='test.css')
        assert aid == 42
        mock_save.assert_called_once()

    def test_save_failed_result_returns_none(self, service, sample_failed_result):
        """Cannot save a failed analysis."""
        aid = service.save_analysis_to_history(sample_failed_result)
        assert aid is None

    @patch('src.database.repositories.save_analysis_from_result')
    def test_save_exception_returns_none(self, mock_save, service, sample_success_result):
        mock_save.side_effect = Exception("db locked")
        aid = service.save_analysis_to_history(sample_success_result)
        assert aid is None

    @patch('src.database.repositories.AnalysisRepository')
    def test_get_history(self, MockRepo, service):
        mock_analysis = MagicMock()
        mock_analysis.to_dict.return_value = {'id': 1, 'file_name': 'test.css'}
        MockRepo.return_value.get_all_analyses.return_value = [mock_analysis]

        history = service.get_analysis_history(limit=10)
        assert len(history) == 1
        assert history[0]['id'] == 1

    @patch('src.database.repositories.AnalysisRepository')
    def test_get_history_error(self, MockRepo, service):
        MockRepo.return_value.get_all_analyses.side_effect = Exception("fail")
        history = service.get_analysis_history()
        assert history == []

    @patch('src.database.repositories.AnalysisRepository')
    def test_get_by_id(self, MockRepo, service):
        mock_analysis = MagicMock()
        mock_analysis.to_dict.return_value = {'id': 5}
        MockRepo.return_value.get_analysis_by_id.return_value = mock_analysis

        record = service.get_analysis_by_id(5)
        assert record['id'] == 5

    @patch('src.database.repositories.AnalysisRepository')
    def test_get_by_id_not_found(self, MockRepo, service):
        MockRepo.return_value.get_analysis_by_id.return_value = None
        record = service.get_analysis_by_id(999)
        assert record is None

    @patch('src.database.repositories.AnalysisRepository')
    def test_delete(self, MockRepo, service):
        MockRepo.return_value.delete_analysis.return_value = True
        assert service.delete_from_history(1) is True

    @patch('src.database.repositories.AnalysisRepository')
    def test_delete_error(self, MockRepo, service):
        MockRepo.return_value.delete_analysis.side_effect = Exception("fail")
        assert service.delete_from_history(1) is False

    @patch('src.database.repositories.AnalysisRepository')
    def test_clear_history(self, MockRepo, service):
        MockRepo.return_value.clear_all.return_value = 10
        assert service.clear_history() is True

    @patch('src.database.repositories.AnalysisRepository')
    def test_clear_history_error(self, MockRepo, service):
        MockRepo.return_value.clear_all.side_effect = Exception("fail")
        assert service.clear_history() is False

    @patch('src.database.repositories.AnalysisRepository')
    def test_history_count(self, MockRepo, service):
        MockRepo.return_value.get_count.return_value = 25
        assert service.get_history_count() == 25

    @patch('src.database.repositories.AnalysisRepository')
    def test_history_count_error(self, MockRepo, service):
        MockRepo.return_value.get_count.side_effect = Exception("fail")
        assert service.get_history_count() == 0


# ═══════════════════════════════════════════════════════════════════════
# Statistics
# ═══════════════════════════════════════════════════════════════════════

class TestStatistics:
    """Statistics via mocked get_statistics_service."""

    @patch('src.database.statistics.get_statistics_service')
    def test_get_statistics(self, mock_get_svc, service):
        mock_svc = MagicMock()
        mock_svc.get_summary_statistics.return_value = {'total_analyses': 10}
        mock_get_svc.return_value = mock_svc

        stats = service.get_statistics()
        assert stats['total_analyses'] == 10

    @patch('src.database.statistics.get_statistics_service')
    def test_get_statistics_error(self, mock_get_svc, service):
        mock_get_svc.side_effect = Exception("fail")
        stats = service.get_statistics()
        assert stats['total_analyses'] == 0
        assert 'error' in stats

    @patch('src.database.statistics.get_statistics_service')
    def test_get_score_trend(self, mock_get_svc, service):
        mock_svc = MagicMock()
        mock_svc.get_score_trend.return_value = [{'date': '2026-01-01', 'avg_score': 85.0}]
        mock_get_svc.return_value = mock_svc

        trend = service.get_score_trend(days=7)
        assert len(trend) == 1
        assert trend[0]['avg_score'] == 85.0

    @patch('src.database.statistics.get_statistics_service')
    def test_get_score_trend_error(self, mock_get_svc, service):
        mock_get_svc.side_effect = Exception("fail")
        assert service.get_score_trend() == []

    @patch('src.database.statistics.get_statistics_service')
    def test_get_top_problematic_features(self, mock_get_svc, service):
        mock_svc = MagicMock()
        mock_svc.get_top_problematic_features.return_value = [{'feature': 'dialog', 'count': 5}]
        mock_get_svc.return_value = mock_svc

        features = service.get_top_problematic_features(limit=5)
        assert features[0]['feature'] == 'dialog'

    @patch('src.database.statistics.get_statistics_service')
    def test_get_top_problematic_features_error(self, mock_get_svc, service):
        mock_get_svc.side_effect = Exception("fail")
        assert service.get_top_problematic_features() == []


# ═══════════════════════════════════════════════════════════════════════
# Settings
# ═══════════════════════════════════════════════════════════════════════

class TestSettings:
    """Settings CRUD via mocked SettingsRepository."""

    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting(self, MockRepo, service):
        MockRepo.return_value.get.return_value = 'dark'
        assert service.get_setting('theme', 'light') == 'dark'

    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting_error_returns_default(self, MockRepo, service):
        MockRepo.return_value.get.side_effect = Exception("fail")
        assert service.get_setting('theme', 'light') == 'light'

    @patch('src.database.repositories.SettingsRepository')
    def test_set_setting(self, MockRepo, service):
        assert service.set_setting('theme', 'dark') is True
        MockRepo.return_value.set.assert_called_once_with('theme', 'dark')

    @patch('src.database.repositories.SettingsRepository')
    def test_set_setting_error(self, MockRepo, service):
        MockRepo.return_value.set.side_effect = Exception("fail")
        assert service.set_setting('theme', 'dark') is False

    @patch('src.database.repositories.SettingsRepository')
    def test_get_all_settings(self, MockRepo, service):
        MockRepo.return_value.get_all.return_value = {'theme': 'dark', 'lang': 'en'}
        settings = service.get_all_settings()
        assert settings == {'theme': 'dark', 'lang': 'en'}

    @patch('src.database.repositories.SettingsRepository')
    def test_get_all_settings_error(self, MockRepo, service):
        MockRepo.return_value.get_all.side_effect = Exception("fail")
        assert service.get_all_settings() == {}

    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting_as_bool(self, MockRepo, service):
        MockRepo.return_value.get_as_bool.return_value = True
        assert service.get_setting_as_bool('auto_save', False) is True

    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting_as_bool_error(self, MockRepo, service):
        MockRepo.return_value.get_as_bool.side_effect = Exception("fail")
        assert service.get_setting_as_bool('auto_save', False) is False

    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting_as_list(self, MockRepo, service):
        MockRepo.return_value.get_as_list.return_value = ['chrome', 'firefox']
        assert service.get_setting_as_list('browsers') == ['chrome', 'firefox']

    @patch('src.database.repositories.SettingsRepository')
    def test_get_setting_as_list_error(self, MockRepo, service):
        MockRepo.return_value.get_as_list.side_effect = Exception("fail")
        assert service.get_setting_as_list('browsers', ['chrome']) == ['chrome']


# ═══════════════════════════════════════════════════════════════════════
# Bookmarks
# ═══════════════════════════════════════════════════════════════════════

class TestBookmarks:
    """Bookmark CRUD via mocked BookmarksRepository."""

    @patch('src.database.repositories.BookmarksRepository')
    def test_add_bookmark(self, MockRepo, service):
        assert service.add_bookmark(1, note='important') is True
        MockRepo.return_value.add_bookmark.assert_called_once_with(1, 'important')

    @patch('src.database.repositories.BookmarksRepository')
    def test_add_bookmark_error(self, MockRepo, service):
        MockRepo.return_value.add_bookmark.side_effect = Exception("fail")
        assert service.add_bookmark(1) is False

    @patch('src.database.repositories.BookmarksRepository')
    def test_remove_bookmark(self, MockRepo, service):
        MockRepo.return_value.remove_bookmark.return_value = True
        assert service.remove_bookmark(1) is True

    @patch('src.database.repositories.BookmarksRepository')
    def test_remove_bookmark_error(self, MockRepo, service):
        MockRepo.return_value.remove_bookmark.side_effect = Exception("fail")
        assert service.remove_bookmark(1) is False

    @patch('src.database.repositories.BookmarksRepository')
    def test_is_bookmarked(self, MockRepo, service):
        MockRepo.return_value.is_bookmarked.return_value = True
        assert service.is_bookmarked(1) is True

    @patch('src.database.repositories.BookmarksRepository')
    def test_toggle_bookmark_adds_when_not_bookmarked(self, MockRepo, service):
        repo_instance = MockRepo.return_value
        repo_instance.is_bookmarked.return_value = False
        result = service.toggle_bookmark(1, note='test')
        assert result is True
        repo_instance.add_bookmark.assert_called_once_with(1, 'test')

    @patch('src.database.repositories.BookmarksRepository')
    def test_toggle_bookmark_removes_when_bookmarked(self, MockRepo, service):
        repo_instance = MockRepo.return_value
        repo_instance.is_bookmarked.return_value = True
        result = service.toggle_bookmark(1)
        assert result is False
        repo_instance.remove_bookmark.assert_called_once_with(1)

    @patch('src.database.repositories.BookmarksRepository')
    def test_get_all_bookmarks(self, MockRepo, service):
        MockRepo.return_value.get_all_bookmarks.return_value = [{'id': 1}]
        bookmarks = service.get_all_bookmarks(limit=10)
        assert len(bookmarks) == 1

    @patch('src.database.repositories.BookmarksRepository')
    def test_get_all_bookmarks_error(self, MockRepo, service):
        MockRepo.return_value.get_all_bookmarks.side_effect = Exception("fail")
        assert service.get_all_bookmarks() == []

    @patch('src.database.repositories.BookmarksRepository')
    def test_update_bookmark_note(self, MockRepo, service):
        MockRepo.return_value.update_note.return_value = True
        assert service.update_bookmark_note(1, 'new note') is True

    @patch('src.database.repositories.BookmarksRepository')
    def test_update_bookmark_note_error(self, MockRepo, service):
        MockRepo.return_value.update_note.side_effect = Exception("fail")
        assert service.update_bookmark_note(1, 'note') is False

    @patch('src.database.repositories.BookmarksRepository')
    def test_get_bookmarks_count(self, MockRepo, service):
        MockRepo.return_value.get_count.return_value = 3
        assert service.get_bookmarks_count() == 3

    @patch('src.database.repositories.BookmarksRepository')
    def test_get_bookmarks_count_error(self, MockRepo, service):
        MockRepo.return_value.get_count.side_effect = Exception("fail")
        assert service.get_bookmarks_count() == 0


# ═══════════════════════════════════════════════════════════════════════
# Tags
# ═══════════════════════════════════════════════════════════════════════

class TestTags:
    """Tag CRUD via mocked TagsRepository."""

    @patch('src.database.repositories.TagsRepository')
    def test_create_tag(self, MockRepo, service):
        MockRepo.return_value.create_tag.return_value = 7
        assert service.create_tag('bugfix', '#ff0000') == 7

    @patch('src.database.repositories.TagsRepository')
    def test_create_tag_error(self, MockRepo, service):
        MockRepo.return_value.create_tag.side_effect = Exception("fail")
        assert service.create_tag('bugfix') is None

    @patch('src.database.repositories.TagsRepository')
    def test_get_all_tags(self, MockRepo, service):
        MockRepo.return_value.get_all_tags.return_value = [{'id': 1, 'name': 'urgent'}]
        tags = service.get_all_tags()
        assert len(tags) == 1
        assert tags[0]['name'] == 'urgent'

    @patch('src.database.repositories.TagsRepository')
    def test_get_all_tags_error(self, MockRepo, service):
        MockRepo.return_value.get_all_tags.side_effect = Exception("fail")
        assert service.get_all_tags() == []

    @patch('src.database.repositories.TagsRepository')
    def test_delete_tag(self, MockRepo, service):
        MockRepo.return_value.delete_tag.return_value = True
        assert service.delete_tag(1) is True

    @patch('src.database.repositories.TagsRepository')
    def test_delete_tag_error(self, MockRepo, service):
        MockRepo.return_value.delete_tag.side_effect = Exception("fail")
        assert service.delete_tag(1) is False

    @patch('src.database.repositories.TagsRepository')
    def test_update_tag(self, MockRepo, service):
        MockRepo.return_value.update_tag.return_value = True
        assert service.update_tag(1, name='critical', color='#ff0000') is True

    @patch('src.database.repositories.TagsRepository')
    def test_update_tag_error(self, MockRepo, service):
        MockRepo.return_value.update_tag.side_effect = Exception("fail")
        assert service.update_tag(1, name='x') is False

    @patch('src.database.repositories.TagsRepository')
    def test_add_tag_to_analysis(self, MockRepo, service):
        MockRepo.return_value.add_tag_to_analysis.return_value = True
        assert service.add_tag_to_analysis(1, 2) is True

    @patch('src.database.repositories.TagsRepository')
    def test_add_tag_to_analysis_error(self, MockRepo, service):
        MockRepo.return_value.add_tag_to_analysis.side_effect = Exception("fail")
        assert service.add_tag_to_analysis(1, 2) is False

    @patch('src.database.repositories.TagsRepository')
    def test_remove_tag_from_analysis(self, MockRepo, service):
        MockRepo.return_value.remove_tag_from_analysis.return_value = True
        assert service.remove_tag_from_analysis(1, 2) is True

    @patch('src.database.repositories.TagsRepository')
    def test_remove_tag_from_analysis_error(self, MockRepo, service):
        MockRepo.return_value.remove_tag_from_analysis.side_effect = Exception("fail")
        assert service.remove_tag_from_analysis(1, 2) is False

    @patch('src.database.repositories.TagsRepository')
    def test_get_tags_for_analysis(self, MockRepo, service):
        MockRepo.return_value.get_tags_for_analysis.return_value = [{'id': 1}]
        tags = service.get_tags_for_analysis(10)
        assert len(tags) == 1

    @patch('src.database.repositories.TagsRepository')
    def test_get_tags_for_analysis_error(self, MockRepo, service):
        MockRepo.return_value.get_tags_for_analysis.side_effect = Exception("fail")
        assert service.get_tags_for_analysis(10) == []

    @patch('src.database.repositories.TagsRepository')
    def test_get_analyses_by_tag(self, MockRepo, service):
        MockRepo.return_value.get_analyses_by_tag.return_value = [{'id': 1}]
        analyses = service.get_analyses_by_tag(5)
        assert len(analyses) == 1

    @patch('src.database.repositories.TagsRepository')
    def test_get_analyses_by_tag_error(self, MockRepo, service):
        MockRepo.return_value.get_analyses_by_tag.side_effect = Exception("fail")
        assert service.get_analyses_by_tag(5) == []

    @patch('src.database.repositories.TagsRepository')
    def test_get_tag_counts(self, MockRepo, service):
        MockRepo.return_value.get_tag_counts.return_value = {'urgent': 3, 'bugfix': 1}
        counts = service.get_tag_counts()
        assert counts['urgent'] == 3

    @patch('src.database.repositories.TagsRepository')
    def test_get_tag_counts_error(self, MockRepo, service):
        MockRepo.return_value.get_tag_counts.side_effect = Exception("fail")
        assert service.get_tag_counts() == {}
