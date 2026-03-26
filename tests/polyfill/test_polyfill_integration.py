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
# Can I Use database -- browser version validation
# ---------------------------------------------------------------------------

class TestCanIUseVersions:
    @pytest.mark.integration
    def test_key_versions_exist_in_database(self, db):
        """Representative old and new versions all exist in Can I Use."""
        cases = [
            ('chrome', '40'), ('chrome', '120'),
            ('firefox', '30'), ('firefox', '120'),
            ('safari', '9'), ('safari', '17.2'),
            ('edge', '14'), ('edge', '120'),
            ('ie', '11'),
        ]
        for browser, version in cases:
            all_versions = db.get_browser_versions(browser)
            assert version in all_versions, f"{browser} {version} not in database"

    @pytest.mark.integration
    def test_latest_versions_exist_and_browsers_have_many(self, db):
        for browser in ('chrome', 'firefox', 'safari', 'edge'):
            versions = db.get_browser_versions(browser)
            assert LATEST_VERSIONS[browser] in versions, f"{browser} latest missing"
            assert len(versions) > 20, f"{browser} too few versions"


# ---------------------------------------------------------------------------
# Can I Use -- support status checks
# ---------------------------------------------------------------------------

class TestCanIUseSupportStatus:
    @pytest.mark.integration
    def test_fetch_supported_in_modern_unsupported_in_ie(self, db):
        assert db.check_support('fetch', 'chrome', '120') in ('y', 'a')
        assert db.check_support('fetch', 'ie', '11') in ('n', 'u')

    @pytest.mark.integration
    def test_dialog_unsupported_in_old_safari(self, db):
        assert db.check_support('dialog', 'safari', '9') in ('n', 'u')

    @pytest.mark.integration
    def test_common_features_supported_in_latest_chrome(self, db):
        for fid in ('fetch', 'promises', 'intersectionobserver'):
            status = db.check_support(fid, 'chrome', LATEST_VERSIONS['chrome'])
            assert status in ('y', 'a'), f"{fid} not supported in latest Chrome"


# ---------------------------------------------------------------------------
# Browser version boundaries
# ---------------------------------------------------------------------------

class TestBrowserVersionBoundaries:
    @pytest.mark.integration
    def test_feature_boundaries_across_versions(self, db):
        """Features transition from unsupported to supported at known version boundaries."""
        boundaries = [
            ('fetch', 'chrome', '39', '42'),
            ('intersectionobserver', 'chrome', '50', '58'),
        ]
        for feature, browser, old, new in boundaries:
            assert db.check_support(feature, browser, old) in ('n', 'u'), f"{feature} should be unsupported in {browser} {old}"
            assert db.check_support(feature, browser, new) in ('y', 'a'), f"{feature} should be supported in {browser} {new}"

    @pytest.mark.integration
    def test_css_grid_firefox_boundary(self, db):
        assert db.check_support('css-grid', 'firefox', '40') in ('n', 'u', 'p', 'x')
        assert db.check_support('css-grid', 'firefox', '52') in ('y', 'a')


# ---------------------------------------------------------------------------
# Compatibility analyzer integration
# ---------------------------------------------------------------------------

class TestCompatibilityAnalyzer:
    @pytest.mark.integration
    def test_ie11_marks_fetch_unsupported(self, analyzer):
        report = analyzer.analyze({'fetch'}, {'ie': '11'})
        assert report.browser_scores['ie'].unsupported_count == 1

    @pytest.mark.integration
    def test_modern_chrome_all_supported(self, analyzer):
        features = {'fetch', 'promises', 'array-includes', 'object-entries'}
        report = analyzer.analyze(features, {'chrome': LATEST_VERSIONS['chrome']})
        assert report.browser_scores['chrome'].supported_count == len(features)
        assert report.browser_scores['chrome'].unsupported_count == 0

    @pytest.mark.integration
    def test_score_lower_for_old_browsers(self, analyzer):
        features = {'fetch', 'promises', 'intersectionobserver', 'css-grid'}
        old = analyzer.analyze(features, {'ie': '11'})
        new = analyzer.analyze(features, {'chrome': LATEST_VERSIONS['chrome']})
        assert old.overall_score < new.overall_score


# ---------------------------------------------------------------------------
# Full pipeline: analyze -> polyfill -> generate
# ---------------------------------------------------------------------------

class TestFullPipeline:
    @pytest.mark.integration
    def test_ie11_fetch_pipeline(self, analyzer, service, tmp_path):
        features = {'fetch', 'promises'}
        report = analyzer.analyze(features, {'ie': '11'})
        ie = report.browser_scores['ie']
        assert ie.unsupported_count + ie.partial_count == 2

        recs = service.get_recommendations(features, set(), {'ie': '11'})
        assert len(recs) == 2

        out = tmp_path / 'polyfills.js'
        generate_polyfills_file(recs, str(out))
        content = out.read_text(encoding='utf-8')
        assert "import 'whatwg-fetch';" in content
        assert 'npm install' in content

    @pytest.mark.integration
    def test_mixed_features_pipeline(self, analyzer, service):
        features = {'fetch', 'css-grid', 'promises', 'flexbox'}
        recs = service.get_recommendations(features, set(), {'ie': '11'})
        assert len(recs) == 4
        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) >= 2
        assert len(cat['fallback']) >= 1

    @pytest.mark.integration
    def test_latest_browsers_no_polyfills_needed(self, analyzer):
        features = {'fetch', 'promises', 'array-includes', 'object-entries'}
        browsers = {b: LATEST_VERSIONS[b] for b in ('chrome', 'firefox', 'safari', 'edge')}
        report = analyzer.analyze(features, browsers)
        assert report.overall_score >= 95
        for browser, score in report.browser_scores.items():
            assert score.unsupported_count == 0


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
        assert 'npm install' in content

    @pytest.mark.integration
    def test_fallback_only_and_empty(self, tmp_path):
        service = PolyfillService()
        fb_recs = service.get_recommendations({'css-grid'}, set(), {'ie': '11'})
        out1 = tmp_path / 'fb.js'
        generate_polyfills_file(fb_recs, str(out1))
        assert 'No npm polyfills needed' in out1.read_text(encoding='utf-8')

        out2 = tmp_path / 'empty.js'
        generate_polyfills_file([], str(out2))
        assert 'No npm polyfills needed' in out2.read_text(encoding='utf-8')

    @pytest.mark.integration
    def test_overwrite_existing_file(self, tmp_path):
        service = PolyfillService()
        recs = service.get_recommendations({'fetch'}, set(), {'ie': '11'})
        out = tmp_path / 'polyfills.js'
        out.write_text('OLD CONTENT', encoding='utf-8')
        generate_polyfills_file(recs, str(out))
        content = out.read_text(encoding='utf-8')
        assert 'OLD CONTENT' not in content
        assert 'Auto-generated' in content


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
        assert {r.feature_id for r in recs} == {'fetch', 'promises'}

    @pytest.mark.integration
    def test_generate_polyfills_file_via_api(self, api_service, tmp_path):
        recs = api_service.get_polyfill_suggestions(
            unsupported_features=['fetch'], browsers={'ie': '11'},
        )
        out = tmp_path / 'polyfills.js'
        result = api_service.generate_polyfills_file(recs, str(out))
        assert Path(result).exists()
        assert "import 'whatwg-fetch';" in Path(result).read_text(encoding='utf-8')


# ---------------------------------------------------------------------------
# Polyfill map alignment with Can I Use
# ---------------------------------------------------------------------------

class TestPolyfillsAlignWithCanIUse:
    @pytest.mark.integration
    def test_most_feature_ids_exist_in_caniuse(self, db):
        loader = get_polyfill_loader()
        all_caniuse = set(db.get_all_features())
        known_exceptions = {
            'object-assign', 'object-fromentries', 'es6-map', 'es6-set',
            'es6-weakmap', 'es6-weakset', 'es6-symbol', 'structuredclone',
            'globalthis', 'array-findindex', 'array-from', 'array-of',
            'es6-array-fill', 'focuswithin', 'focusvisible',
            'css-scroll-snap', 'input-date', 'array-find',
        }
        unexpected = []
        for getter in (loader.get_all_javascript_polyfills,
                       loader.get_all_css_polyfills,
                       loader.get_all_html_polyfills):
            for fid in getter():
                if fid not in all_caniuse and fid not in known_exceptions:
                    unexpected.append(fid)
        assert unexpected == []

    @pytest.mark.integration
    def test_polyfill_features_not_fully_supported_in_ie11(self, db):
        """Each polyfilled feature should be at least partially unsupported in IE 11."""
        for fid in ('fetch', 'promises', 'intersectionobserver', 'css-grid', 'dialog'):
            status = db.check_support(fid, 'ie', '11')
            assert status != 'y', f"{fid} fully supported in IE 11 -- polyfill unnecessary"


# ---------------------------------------------------------------------------
# API service -- additional edge cases
# ---------------------------------------------------------------------------

class TestAPIServiceEdgeCases:
    @pytest.mark.integration
    def test_nonexistent_feature_returns_empty(self, api_service):
        recs = api_service.get_polyfill_suggestions(
            unsupported_features=['totally-nonexistent'],
        )
        assert recs == []

    @pytest.mark.integration
    def test_default_browsers_used_when_omitted(self, api_service):
        recs = api_service.get_polyfill_suggestions(
            unsupported_features=['fetch'],
        )
        assert len(recs) == 1
        assert len(recs[0].browsers_affected) > 0
