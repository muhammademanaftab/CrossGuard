"""Integration tests -- full pipeline from Can I Use through polyfill recommendations and file generation."""

import pytest
from pathlib import Path

from src.analyzer.database import get_database
from src.analyzer.compatibility import CompatibilityAnalyzer
from src.polyfill.polyfill_service import PolyfillService
from src.polyfill.polyfill_generator import generate_polyfills_file
from src.polyfill.polyfill_loader import get_polyfill_loader
from src.api.service import AnalyzerService
from src.utils.config import LATEST_VERSIONS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def db():
    return get_database()


@pytest.fixture(scope="module")
def analyzer():
    return CompatibilityAnalyzer()


@pytest.fixture
def service():
    return PolyfillService()


@pytest.fixture
def api_service():
    return AnalyzerService()


# ---------------------------------------------------------------------------
# Can I Use -- support status checks
# ---------------------------------------------------------------------------

class TestCanIUseSupportStatus:
    @pytest.mark.integration
    def test_fetch_supported_in_modern_unsupported_in_ie(self, db):
        assert db.check_support('fetch', 'chrome', '120') in ('y', 'a')
        assert db.check_support('fetch', 'ie', '11') in ('n', 'u')



# ---------------------------------------------------------------------------
# Compatibility analyzer integration
# ---------------------------------------------------------------------------

class TestCompatibilityAnalyzer:
    @pytest.mark.integration
    def test_ie11_marks_fetch_unsupported(self, analyzer):
        report = analyzer.analyze({'fetch'}, {'ie': '11'})
        assert report['browser_scores']['ie']['unsupported_count'] == 1



# ---------------------------------------------------------------------------
# Full pipeline: analyze -> polyfill -> generate
# ---------------------------------------------------------------------------

class TestFullPipeline:
    @pytest.mark.integration
    def test_ie11_fetch_pipeline(self, analyzer, service, tmp_path):
        features = {'fetch', 'promises'}
        report = analyzer.analyze(features, {'ie': '11'})
        ie = report['browser_scores']['ie']
        assert ie['unsupported_count'] + ie['partial_count'] == 2

        recs = service.get_recommendations(features, set(), {'ie': '11'})
        assert len(recs) == 2

        out = tmp_path / 'polyfills.js'
        generate_polyfills_file(recs, str(out))
        content = out.read_text(encoding='utf-8')
        assert "import 'whatwg-fetch';" in content

    @pytest.mark.integration
    def test_latest_browsers_no_polyfills_needed(self, analyzer):
        features = {'fetch', 'promises', 'array-includes', 'object-entries'}
        browsers = {b: LATEST_VERSIONS[b] for b in ('chrome', 'firefox', 'safari', 'edge')}
        report = analyzer.analyze(features, browsers)
        assert report['overall_score'] >= 95
        for browser, score in report['browser_scores'].items():
            assert score['unsupported_count'] == 0


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


# ---------------------------------------------------------------------------
# API service facade
# ---------------------------------------------------------------------------

class TestAPIServicePolyfills:
    @pytest.mark.integration
    def test_get_polyfill_suggestions(self, api_service):
        recs = api_service.get_polyfill_suggestions(
            unsupported_features=['fetch', 'promises'],
            partial_features=[], browsers={'ie': '11'},
        )
        assert len(recs) == 2
        assert {r['feature_id'] for r in recs} == {'fetch', 'promises'}

