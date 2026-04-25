"""Integration tests -- full pipeline from analyzer through polyfill recommendations and file generation."""

import pytest
from pathlib import Path

from src.analyzer.compatibility import CompatibilityAnalyzer
from src.polyfill.polyfill_service import PolyfillService
from src.polyfill.polyfill_generator import generate_polyfills_file


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def analyzer():
    return CompatibilityAnalyzer()


@pytest.fixture
def service():
    return PolyfillService()


# ---------------------------------------------------------------------------
# Full pipeline: analyze -> polyfill -> generate
# ---------------------------------------------------------------------------

class TestFullPipeline:
    @pytest.mark.integration
    def test_ie11_fetch_pipeline(self, analyzer, service, tmp_path):
        features = {'fetch', 'promises'}
        classification = analyzer.classify_features(features, {'ie': '11'})
        ie = classification['ie']
        # neither feature is natively supported in IE11 -- fetch='n' (unsupported), promises='p' (polyfill-only, unknown)
        assert 'fetch' not in ie['supported']
        assert 'promises' not in ie['supported']

        recs = service.get_recommendations(features, set(), {'ie': '11'})
        assert len(recs) == 2

        out = tmp_path / 'polyfills.js'
        generate_polyfills_file(recs, str(out))
        content = out.read_text(encoding='utf-8')
        assert "import 'whatwg-fetch';" in content


# ---------------------------------------------------------------------------
# File generation
# ---------------------------------------------------------------------------

class TestFileGeneration:
    @pytest.mark.integration
    def test_creates_file_with_correct_content(self, tmp_path):
        service = PolyfillService()
        recs = service.get_recommendations({'fetch', 'promises'}, set(), {'ie': '11'})
        out = tmp_path / 'polyfills.js'
        result = generate_polyfills_file(recs, str(out))
        assert Path(result).exists()
        content = out.read_text(encoding='utf-8')
        assert "import 'whatwg-fetch';" in content
