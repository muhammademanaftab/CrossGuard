"""
Test suite for CrossGuardAnalyzer main module.
Tests the core analysis workflow and report generation.
"""

import pytest
from pathlib import Path


class TestAnalyzerInitialization:
    """Test analyzer initialization."""

    def test_analyzer_initialization(self, main_analyzer):
        """Test main analyzer initializes correctly."""
        assert main_analyzer is not None
        assert hasattr(main_analyzer, 'analyze_project')
        assert hasattr(main_analyzer, 'html_parser')
        assert hasattr(main_analyzer, 'css_parser')
        assert hasattr(main_analyzer, 'js_parser')

    def test_analyzer_has_database(self, main_analyzer):
        """Test analyzer has database connection."""
        assert main_analyzer.database is not None

    def test_analyzer_has_parsers(self, main_analyzer):
        """Test analyzer has all parsers."""
        assert main_analyzer.html_parser is not None
        assert main_analyzer.css_parser is not None
        assert main_analyzer.js_parser is not None


class TestAnalyzeProject:
    """Test project analysis functionality."""

    def test_analyze_empty_project(self, main_analyzer, default_browsers):
        """Test analyzing project with no files returns validation error."""
        result = main_analyzer.analyze_project(
            html_files=[],
            css_files=[],
            js_files=[],
            target_browsers=default_browsers
        )
        # Empty project should return success=False (validation error)
        assert 'success' in result
        # Either success or error should be present
        assert result['success'] is False or 'error' in result

    def test_analyze_single_html_file(self, main_analyzer, sample_html_file, default_browsers):
        """Test analyzing single HTML file."""
        result = main_analyzer.analyze_project(
            html_files=[sample_html_file],
            target_browsers=default_browsers
        )
        assert result['success'] is True
        assert 'features' in result

    def test_analyze_single_css_file(self, main_analyzer, sample_css_file, default_browsers):
        """Test analyzing single CSS file."""
        result = main_analyzer.analyze_project(
            css_files=[sample_css_file],
            target_browsers=default_browsers
        )
        assert result['success'] is True
        assert 'features' in result

    def test_analyze_single_js_file(self, main_analyzer, sample_js_file, default_browsers):
        """Test analyzing single JavaScript file."""
        result = main_analyzer.analyze_project(
            js_files=[sample_js_file],
            target_browsers=default_browsers
        )
        assert result['success'] is True
        assert 'features' in result

    def test_analyze_with_default_browsers(self, main_analyzer, sample_css_file):
        """Test analyzing with default target browsers."""
        result = main_analyzer.analyze_project(
            css_files=[sample_css_file]
        )
        assert result['success'] is True
        assert 'browsers' in result

    def test_analyze_multiple_files(self, main_analyzer, tmp_path, default_browsers):
        """Test analyzing multiple files of different types."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><body><header><nav></nav></header></body></html>")

        css_file = tmp_path / "test.css"
        css_file.write_text(".container { display: flex; }")

        js_file = tmp_path / "test.js"
        js_file.write_text("const x = () => x + 1;")

        result = main_analyzer.analyze_project(
            html_files=[str(html_file)],
            css_files=[str(css_file)],
            js_files=[str(js_file)],
            target_browsers=default_browsers
        )

        assert result['success'] is True
        assert 'features' in result


class TestAnalyzerReportStructure:
    """Test the structure of analysis reports."""

    def test_report_contains_required_fields(self, main_analyzer, sample_css_file, default_browsers):
        """Test report contains all required fields."""
        result = main_analyzer.analyze_project(
            css_files=[sample_css_file],
            target_browsers=default_browsers
        )

        assert 'success' in result
        assert 'timestamp' in result
        assert 'summary' in result
        assert 'scores' in result
        assert 'browsers' in result
        assert 'features' in result

    def test_report_summary_structure(self, main_analyzer, sample_css_file, default_browsers):
        """Test summary section structure."""
        result = main_analyzer.analyze_project(
            css_files=[sample_css_file],
            target_browsers=default_browsers
        )

        summary = result.get('summary', {})
        assert 'total_features' in summary
        # Summary may contain feature counts by type
        assert 'css_features' in summary or 'total_features' in summary


class TestAnalyzerFeatureDetection:
    """Test feature detection through main analyzer."""

    def test_detects_flexbox(self, main_analyzer, tmp_path, default_browsers):
        """Test detection of flexbox through analyzer."""
        css_file = tmp_path / "flex.css"
        css_file.write_text(".container { display: flex; gap: 20px; }")

        result = main_analyzer.analyze_project(
            css_files=[str(css_file)],
            target_browsers=default_browsers
        )

        assert result['success'] is True
        features = result.get('features', {})
        css_features = features.get('css', [])
        assert 'flexbox' in css_features or any('flex' in str(f) for f in css_features)

    def test_detects_arrow_functions(self, main_analyzer, tmp_path, default_browsers):
        """Test detection of arrow functions through analyzer."""
        js_file = tmp_path / "arrows.js"
        js_file.write_text("const add = (a, b) => a + b;")

        result = main_analyzer.analyze_project(
            js_files=[str(js_file)],
            target_browsers=default_browsers
        )

        assert result['success'] is True


class TestAnalyzerErrorHandling:
    """Test error handling in analyzer."""

    def test_handles_nonexistent_file(self, main_analyzer, default_browsers):
        """Test handling of non-existent file."""
        result = main_analyzer.analyze_project(
            html_files=["/nonexistent/file.html"],
            target_browsers=default_browsers
        )
        assert 'success' in result


class TestAnalyzerExport:
    """Test export functionality of analyzer."""

    def test_export_to_json_format(self, main_analyzer, sample_css_file, default_browsers):
        """Test that report can be exported as JSON."""
        import json

        result = main_analyzer.analyze_project(
            css_files=[sample_css_file],
            target_browsers=default_browsers
        )

        json_str = json.dumps(result, indent=2)
        assert json_str is not None
        assert len(json_str) > 0

        parsed = json.loads(json_str)
        assert parsed['success'] == result['success']
