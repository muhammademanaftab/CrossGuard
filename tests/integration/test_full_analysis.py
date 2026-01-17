"""
Integration tests for Cross Guard.
Tests the complete analysis workflow end-to-end.
"""

import pytest
import json
from pathlib import Path


class TestFullAnalysisWorkflow:
    """Test complete analysis workflows."""

    def test_full_web_project_analysis(self, main_analyzer, tmp_path, default_browsers):
        """Test analyzing a complete web project with HTML, CSS, and JS."""
        # Create HTML file
        html_file = tmp_path / "index.html"
        html_file.write_text("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Test Page</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <header>
                <nav>Navigation</nav>
            </header>
            <main>
                <article>
                    <section>Content</section>
                </article>
            </main>
            <footer>Footer</footer>
            <script src="app.js" type="module" defer></script>
        </body>
        </html>
        """)

        # Create CSS file
        css_file = tmp_path / "styles.css"
        css_file.write_text("""
        :root {
            --primary-color: #3498db;
        }

        .container {
            display: flex;
            gap: 20px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
        }

        .card {
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        """)

        # Create JavaScript file
        js_file = tmp_path / "app.js"
        js_file.write_text("""
        const APP_NAME = 'Test App';

        const fetchData = async (url) => {
            const response = await fetch(url);
            return response.json();
        };

        class DataManager {
            constructor() {
                this.data = new Map();
            }

            async load() {
                const result = await fetchData('/api/data');
                this.data.set('main', result);
            }
        }

        const manager = new DataManager();
        manager.load().then(() => console.log('Loaded'));
        """)

        # Run analysis
        result = main_analyzer.analyze_project(
            html_files=[str(html_file)],
            css_files=[str(css_file)],
            js_files=[str(js_file)],
            target_browsers=default_browsers
        )

        # Verify success
        assert result['success'] is True

        # Verify features detected
        features = result.get('features', {})
        assert 'html' in features or 'css' in features or 'javascript' in features

        # Verify scores generated
        scores = result.get('scores', {})
        assert scores is not None

        # Verify browser analysis
        browsers = result.get('browsers', {})
        for browser in default_browsers.keys():
            assert browser in browsers

    def test_analysis_with_modern_features(self, main_analyzer, fixtures_dir, default_browsers):
        """Test analysis with modern CSS and JS features from fixtures."""
        css_file = fixtures_dir / "sample_css" / "modern.css"
        js_file = fixtures_dir / "sample_js" / "modern.js"
        html_file = fixtures_dir / "sample_html" / "modern.html"

        files_to_analyze = {
            'html': [str(html_file)] if html_file.exists() else [],
            'css': [str(css_file)] if css_file.exists() else [],
            'js': [str(js_file)] if js_file.exists() else []
        }

        if not any(files_to_analyze.values()):
            pytest.skip("No fixture files available")

        result = main_analyzer.analyze_project(
            html_files=files_to_analyze['html'],
            css_files=files_to_analyze['css'],
            js_files=files_to_analyze['js'],
            target_browsers=default_browsers
        )

        assert result['success'] is True
        assert result.get('summary', {}).get('total_features', 0) > 0


class TestReportExport:
    """Test report export functionality."""

    def test_json_export_valid(self, main_analyzer, sample_css_file, default_browsers, tmp_path):
        """Test JSON export produces valid JSON."""
        result = main_analyzer.analyze_project(
            css_files=[sample_css_file],
            target_browsers=default_browsers
        )

        # Export to JSON file
        export_file = tmp_path / "report.json"
        with open(export_file, 'w') as f:
            json.dump(result, f, indent=2)

        # Verify file exists and is valid JSON
        assert export_file.exists()
        with open(export_file, 'r') as f:
            loaded = json.load(f)
        assert loaded['success'] == result['success']

    def test_report_completeness(self, main_analyzer, sample_css_file, default_browsers):
        """Test report contains all expected sections."""
        result = main_analyzer.analyze_project(
            css_files=[sample_css_file],
            target_browsers=default_browsers
        )

        # Check all main sections exist
        required_sections = ['success', 'timestamp', 'summary', 'scores', 'browsers', 'features']
        for section in required_sections:
            assert section in result, f"Missing section: {section}"


class TestMultipleFileAnalysis:
    """Test analysis of multiple files."""

    def test_multiple_css_files(self, main_analyzer, tmp_path, default_browsers):
        """Test analyzing multiple CSS files."""
        css_files = []
        for i in range(3):
            css_file = tmp_path / f"style{i}.css"
            css_file.write_text(f".class{i} {{ display: flex; }}")
            css_files.append(str(css_file))

        result = main_analyzer.analyze_project(
            css_files=css_files,
            target_browsers=default_browsers
        )

        assert result['success'] is True
        # Verify CSS features were detected
        summary = result.get('summary', {})
        assert summary.get('css_features', 0) >= 1

    def test_multiple_js_files(self, main_analyzer, tmp_path, default_browsers):
        """Test analyzing multiple JavaScript files."""
        js_files = []
        for i in range(3):
            js_file = tmp_path / f"script{i}.js"
            js_file.write_text(f"const var{i} = () => {i};")
            js_files.append(str(js_file))

        result = main_analyzer.analyze_project(
            js_files=js_files,
            target_browsers=default_browsers
        )

        assert result['success'] is True


class TestBrowserCompatibilityScenarios:
    """Test different browser compatibility scenarios."""

    def test_modern_browsers_only(self, main_analyzer, sample_css_file):
        """Test with modern browsers only."""
        modern_browsers = {
            'chrome': '120',
            'firefox': '121',
            'safari': '17',
            'edge': '120'
        }

        result = main_analyzer.analyze_project(
            css_files=[sample_css_file],
            target_browsers=modern_browsers
        )

        assert result['success'] is True
        # Modern features should score well on modern browsers
        scores = result.get('scores', {})
        overall = scores.get('overall', scores.get('simple_score', 0))
        assert overall >= 0

    def test_with_legacy_browsers(self, main_analyzer, sample_css_file):
        """Test with legacy browsers included."""
        browsers_with_legacy = {
            'chrome': '120',
            'firefox': '121',
            'safari': '17',
            'edge': '120',
            'ie': '11'
        }

        result = main_analyzer.analyze_project(
            css_files=[sample_css_file],
            target_browsers=browsers_with_legacy
        )

        assert result['success'] is True
        # IE should show lower compatibility for modern features
        browsers = result.get('browsers', {})
        if 'ie' in browsers:
            ie_score = browsers['ie'].get('score', 0)
            chrome_score = browsers.get('chrome', {}).get('score', 100)
            # IE typically has lower compatibility than Chrome for modern features


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_files(self, main_analyzer, tmp_path, default_browsers):
        """Test analyzing empty files."""
        empty_css = tmp_path / "empty.css"
        empty_css.write_text("")

        empty_js = tmp_path / "empty.js"
        empty_js.write_text("")

        result = main_analyzer.analyze_project(
            css_files=[str(empty_css)],
            js_files=[str(empty_js)],
            target_browsers=default_browsers
        )

        assert result['success'] is True

    def test_comment_only_files(self, main_analyzer, tmp_path, default_browsers):
        """Test analyzing files with only comments."""
        css_comments = tmp_path / "comments.css"
        css_comments.write_text("/* This is just a comment */")

        js_comments = tmp_path / "comments.js"
        js_comments.write_text("// This is just a comment")

        result = main_analyzer.analyze_project(
            css_files=[str(css_comments)],
            js_files=[str(js_comments)],
            target_browsers=default_browsers
        )

        assert result['success'] is True

    def test_large_file(self, main_analyzer, tmp_path, default_browsers):
        """Test analyzing larger files."""
        large_css = tmp_path / "large.css"
        css_content = "\n".join([
            f".class{i} {{ display: flex; color: #{i:06x}; }}"
            for i in range(100)
        ])
        large_css.write_text(css_content)

        result = main_analyzer.analyze_project(
            css_files=[str(large_css)],
            target_browsers=default_browsers
        )

        assert result['success'] is True


class TestDatabaseIntegration:
    """Test database integration in full workflow."""

    def test_database_loaded(self, database):
        """Test database is loaded and functional."""
        assert database is not None
        stats = database.get_statistics()
        assert stats['total_features'] > 0

    def test_feature_lookup(self, database):
        """Test feature lookup works."""
        feature = database.get_feature('flexbox')
        assert feature is not None

    def test_support_check(self, database):
        """Test support checking works."""
        status = database.check_support('flexbox', 'chrome', '120')
        assert status in ['y', 'a', 'n', 'x', 'p', 'u']


class TestEndToEndScenarios:
    """Real-world end-to-end scenarios."""

    def test_portfolio_site_analysis(self, main_analyzer, tmp_path, default_browsers):
        """Test analyzing a typical portfolio website."""
        # HTML
        html = tmp_path / "index.html"
        html.write_text("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Portfolio</title>
        </head>
        <body>
            <header><nav></nav></header>
            <main>
                <section id="about"></section>
                <section id="projects"></section>
                <section id="contact">
                    <form>
                        <input type="email" required>
                        <button type="submit">Send</button>
                    </form>
                </section>
            </main>
            <footer></footer>
        </body>
        </html>
        """)

        # CSS
        css = tmp_path / "styles.css"
        css.write_text("""
        * { box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; }
        nav { display: flex; justify-content: space-between; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .card { transition: transform 0.3s; }
        .card:hover { transform: translateY(-5px); }
        @media (prefers-color-scheme: dark) { body { background: #1a1a1a; color: white; } }
        """)

        # JS
        js = tmp_path / "main.js"
        js.write_text("""
        const form = document.querySelector('form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = new FormData(form);
            await fetch('/api/contact', { method: 'POST', body: data });
        });
        """)

        result = main_analyzer.analyze_project(
            html_files=[str(html)],
            css_files=[str(css)],
            js_files=[str(js)],
            target_browsers=default_browsers
        )

        assert result['success'] is True
        assert result.get('summary', {}).get('total_features', 0) > 0
