"""CSS parser integration tests.

File I/O, real-world multi-feature scenarios, and full pipeline tests
through statistics and reports.
"""

import pytest


@pytest.fixture
def tmp_css_file(tmp_path):
    def _create(content, filename="test.css"):
        filepath = tmp_path / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
    return _create


# =====================================================================
# File Operations
# =====================================================================

@pytest.mark.integration
class TestParseFile:
    def test_parse_valid_file(self, css_parser, tmp_css_file):
        assert "flexbox" in css_parser.parse_file(tmp_css_file("div { display: flex; }"))


# =====================================================================
# Real-World Scenarios
# =====================================================================

@pytest.mark.integration
class TestRealWorldScenarios:
    def test_modern_css_reset(self, parse_features):
        css = """
        *, *::before, *::after { box-sizing: border-box; }
        * { margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body { min-height: 100vh; line-height: 1.5; }
        """
        features = parse_features(css)
        assert "css3-boxsizing" in features
        assert "css-gencontent" in features
        assert "css-scroll-behavior" in features
        assert "viewport-units" in features

    def test_flexbox_card_layout(self, parse_features):
        css = """
        .cards { display: flex; flex-wrap: wrap; gap: 20px; }
        .card { border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s ease; }
        .card:hover { transform: translateY(-4px); }
        """
        features = parse_features(css)
        assert "flexbox" in features
        assert "flexbox-gap" in features
        assert "border-radius" in features
        assert "css-transitions" in features
