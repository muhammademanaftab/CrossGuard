"""CSS parser integration tests.

Real-world multi-feature scenario through the full pipeline.
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
