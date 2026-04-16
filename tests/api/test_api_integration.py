"""Integration tests for AnalyzerService with real backend.

Uses real parsers and Can I Use database (read-only JSON files).
No database (SQLite) interaction -- only the analyze() pipeline.
"""

import pytest

from src.api.service import AnalyzerService


# --- Fixtures ---

@pytest.fixture
def service():
    """Fresh service wired to real backend."""
    return AnalyzerService()


@pytest.fixture
def create_temp_file(tmp_path):
    """Factory for creating temp files with given content."""
    def _create(filename: str, content: str) -> str:
        filepath = tmp_path / filename
        filepath.write_text(content, encoding='utf-8')
        return str(filepath)
    return _create


# ===================================================================
# Mixed File Analysis
# ===================================================================

class TestMixedFileAnalysis:

    @pytest.mark.integration
    def test_html_css_js_combined(self, service, create_temp_file):
        html_path = create_temp_file("index.html", "<html><body><dialog>Hi</dialog></body></html>")
        css_path = create_temp_file("style.css", ".x { display: flex; }")
        js_path = create_temp_file("app.js", "const fn = () => 1;")

        result = service.analyze_files(
            html_files=[html_path],
            css_files=[css_path],
            js_files=[js_path],
        )

        assert result.success is True
        assert result.summary['total_features'] > 0


# ===================================================================
# Result Structure Validation
# ===================================================================

class TestResultStructure:

    @pytest.mark.integration
    def test_all_fields_present(self, service, create_temp_file):
        path = create_temp_file("style.css", ".x { display: flex; gap: 10px; }")
        result = service.analyze_files(css_files=[path])

        assert result.success is True
        assert result.summary is not None
        assert result.scores is not None
        assert isinstance(result.browsers, dict)
        assert result.detected_features is not None
        assert result.feature_details is not None
        assert result.unrecognized_patterns is not None
        assert isinstance(result.recommendations, list)
