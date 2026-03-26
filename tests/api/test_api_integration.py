"""Integration tests for AnalyzerService with real backend.

Uses real parsers and Can I Use database (read-only JSON files).
No database (SQLite) interaction -- only the analyze() pipeline.
"""

import pytest
from pathlib import Path

from src.api.service import AnalyzerService
from src.api.schemas import AnalysisRequest, AnalysisResult, BrowserCompatibility


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


# ═══════════════════════════════════════════════════════════════════════
# CSS Integration
# ═══════════════════════════════════════════════════════════════════════

class TestAnalyzeCSS:

    @pytest.mark.integration
    def test_flexbox_detected_and_scored(self, service, create_temp_file):
        path = create_temp_file("style.css", ".container { display: flex; }")
        result = service.analyze_files(css_files=[path])

        assert result.success is True
        assert result.summary.total_features > 0
        assert result.scores.simple_score > 0

    @pytest.mark.integration
    def test_grid_detected(self, service, create_temp_file):
        path = create_temp_file("grid.css", ".layout { display: grid; grid-template-columns: 1fr 1fr; }")
        result = service.analyze_files(css_files=[path])

        assert result.success is True
        assert any('grid' in f for f in result.detected_features.css)

    @pytest.mark.integration
    def test_empty_file(self, service, create_temp_file):
        path = create_temp_file("empty.css", "")
        result = service.analyze_files(css_files=[path])

        assert result.success is True
        assert result.summary.total_features == 0

    @pytest.mark.integration
    def test_multiple_features(self, service, create_temp_file):
        css = """
        .a { display: flex; gap: 10px; }
        .b { position: sticky; }
        .c { display: grid; }
        """
        path = create_temp_file("multi.css", css)
        result = service.analyze_files(css_files=[path])

        assert result.success is True
        assert result.summary.css_features >= 3


# ═══════════════════════════════════════════════════════════════════════
# JavaScript Integration
# ═══════════════════════════════════════════════════════════════════════

class TestAnalyzeJS:

    @pytest.mark.integration
    def test_arrow_functions(self, service, create_temp_file):
        path = create_temp_file("app.js", "const fn = () => 42;")
        result = service.analyze_files(js_files=[path])

        assert result.success is True
        assert result.summary.js_features > 0

    @pytest.mark.integration
    def test_promises(self, service, create_temp_file):
        path = create_temp_file("async.js", "const p = new Promise((resolve) => resolve(1));")
        result = service.analyze_files(js_files=[path])

        assert result.success is True
        assert any('promise' in f for f in result.detected_features.js)


# ═══════════════════════════════════════════════════════════════════════
# HTML Integration
# ═══════════════════════════════════════════════════════════════════════

class TestAnalyzeHTML:

    @pytest.mark.integration
    def test_dialog_element(self, service, create_temp_file):
        html = "<html><body><dialog open>Hello</dialog></body></html>"
        path = create_temp_file("page.html", html)
        result = service.analyze_files(html_files=[path])

        assert result.success is True
        assert result.summary.html_features > 0

    @pytest.mark.integration
    def test_details_element(self, service, create_temp_file):
        html = "<html><body><details><summary>Info</summary>Content</details></body></html>"
        path = create_temp_file("page.html", html)
        result = service.analyze_files(html_files=[path])

        assert result.success is True
        assert result.summary.html_features > 0


# ═══════════════════════════════════════════════════════════════════════
# Mixed File Analysis
# ═══════════════════════════════════════════════════════════════════════

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
        assert result.summary.total_features > 0

    @pytest.mark.integration
    def test_multiple_css_files(self, service, create_temp_file):
        css1 = create_temp_file("a.css", ".a { display: flex; }")
        css2 = create_temp_file("b.css", ".b { display: grid; }")

        result = service.analyze_files(css_files=[css1, css2])
        assert result.success is True
        assert result.summary.css_features >= 2


# ═══════════════════════════════════════════════════════════════════════
# Error Handling
# ═══════════════════════════════════════════════════════════════════════

class TestIntegrationErrors:

    @pytest.mark.integration
    def test_nonexistent_file(self, service):
        result = service.analyze_files(css_files=["/nonexistent/path/missing.css"])
        assert isinstance(result, AnalysisResult)

    @pytest.mark.integration
    def test_garbage_content_no_crash(self, service, create_temp_file):
        path = create_temp_file("garbage.css", "\x00\xff\xfe binary garbage @#$%")
        result = service.analyze_files(css_files=[path])
        assert isinstance(result, AnalysisResult)


# ═══════════════════════════════════════════════════════════════════════
# Result Structure Validation
# ═══════════════════════════════════════════════════════════════════════

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

    @pytest.mark.integration
    def test_browser_compatibility_valid(self, service, create_temp_file):
        path = create_temp_file("style.css", ".x { display: flex; }")
        result = service.analyze_files(css_files=[path])

        assert result.success is True
        for name, browser in result.browsers.items():
            assert isinstance(browser, BrowserCompatibility)
            assert browser.name == name
            assert 0 <= browser.compatibility_percentage <= 100
            assert browser.supported >= 0
            assert browser.partial >= 0
            assert browser.unsupported >= 0
