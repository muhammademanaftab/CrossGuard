"""
Integration tests — full pipeline from Can I Use database through to polyfill recommendations.

These tests verify that:
1. Can I Use browser versions are real and queryable
2. Old browser versions correctly mark features as unsupported
3. Unsupported features produce the right polyfill recommendations
4. The API service facade calls work end-to-end
"""

import pytest
from pathlib import Path

from src.analyzer.database import get_database
from src.analyzer.compatibility import CompatibilityAnalyzer
from src.polyfill.polyfill_service import PolyfillService
from src.polyfill.polyfill_generator import generate_polyfills_file, generate_polyfills_content
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
# Can I Use database — browser versions are real
# ---------------------------------------------------------------------------

class TestCanIUseBrowserVersions:
    """Verify that browser versions used in polyfill testing actually exist in Can I Use."""

    @pytest.mark.parametrize("browser,version", [
        ('chrome', '40'), ('chrome', '60'), ('chrome', '80'), ('chrome', '100'), ('chrome', '120'),
        ('firefox', '30'), ('firefox', '50'), ('firefox', '70'), ('firefox', '100'), ('firefox', '120'),
        ('safari', '9'), ('safari', '10'), ('safari', '12'), ('safari', '14'), ('safari', '17.2'),
        ('edge', '12'), ('edge', '14'), ('edge', '18'), ('edge', '80'), ('edge', '120'),
        ('ie', '11'),
    ])
    def test_version_exists_in_database(self, db, browser, version):
        """Every version we use for testing must actually exist in Can I Use."""
        all_versions = db.get_browser_versions(browser)
        assert version in all_versions, (
            f"{browser} {version} not in Can I Use database. Available: {all_versions[:10]}..."
        )

    @pytest.mark.parametrize("browser", ['chrome', 'firefox', 'safari', 'edge'])
    def test_latest_version_exists(self, db, browser):
        latest = LATEST_VERSIONS[browser]
        all_versions = db.get_browser_versions(browser)
        assert latest in all_versions, (
            f"LATEST_VERSIONS['{browser}'] = {latest} not in Can I Use"
        )

    @pytest.mark.parametrize("browser", ['chrome', 'firefox', 'safari', 'edge'])
    def test_has_many_versions(self, db, browser):
        versions = db.get_browser_versions(browser)
        assert len(versions) > 20, f"{browser} should have many versions, got {len(versions)}"


# ---------------------------------------------------------------------------
# Can I Use — support status checks
# ---------------------------------------------------------------------------

class TestCanIUseSupportStatus:
    """Verify that Can I Use correctly reports support status for features we polyfill."""

    def test_fetch_supported_in_modern_chrome(self, db):
        status = db.check_support('fetch', 'chrome', '120')
        assert status in ('y', 'a'), f"fetch should be supported in Chrome 120, got '{status}'"

    def test_fetch_unsupported_in_ie11(self, db):
        status = db.check_support('fetch', 'ie', '11')
        assert status in ('n', 'u'), f"fetch should be unsupported in IE 11, got '{status}'"

    def test_promises_partial_in_ie11(self, db):
        """IE 11 has partial promise support (no unhandledrejection events)."""
        status = db.check_support('promises', 'ie', '11')
        assert status in ('p', 'n', 'u'), f"promises should be partial/unsupported in IE 11, got '{status}'"

    def test_css_grid_partial_in_ie11(self, db):
        """IE 11 has partial/old-spec CSS Grid (a or p)."""
        status = db.check_support('css-grid', 'ie', '11')
        assert status in ('a', 'p', 'x', 'n', 'u'), f"css-grid in IE 11 got '{status}'"

    def test_dialog_unsupported_in_old_safari(self, db):
        status = db.check_support('dialog', 'safari', '9')
        assert status in ('n', 'u'), f"dialog should be unsupported in Safari 9, got '{status}'"

    @pytest.mark.parametrize("feature_id", [
        'fetch', 'promises', 'intersectionobserver', 'resizeobserver',
    ])
    def test_features_supported_in_latest_chrome(self, db, feature_id):
        status = db.check_support(feature_id, 'chrome', LATEST_VERSIONS['chrome'])
        assert status in ('y', 'a'), (
            f"{feature_id} should be supported in Chrome {LATEST_VERSIONS['chrome']}, got '{status}'"
        )


# ---------------------------------------------------------------------------
# Compatibility Analyzer → unsupported features
# ---------------------------------------------------------------------------

class TestCompatibilityAnalyzerIntegration:
    """Verify that the analyzer correctly identifies unsupported features."""

    def test_ie11_marks_fetch_unsupported(self, analyzer):
        report = analyzer.analyze({'fetch'}, {'ie': '11'})
        ie_score = report.browser_scores['ie']
        assert ie_score.unsupported_count == 1
        assert ie_score.supported_count == 0

    def test_ie11_many_unsupported(self, analyzer):
        features = {'fetch', 'promises', 'intersectionobserver', 'resizeobserver'}
        report = analyzer.analyze(features, {'ie': '11'})
        ie_score = report.browser_scores['ie']
        assert ie_score.unsupported_count >= 3

    def test_modern_chrome_all_supported(self, analyzer):
        features = {'fetch', 'promises', 'array-includes', 'object-entries'}
        report = analyzer.analyze(features, {'chrome': LATEST_VERSIONS['chrome']})
        chrome_score = report.browser_scores['chrome']
        assert chrome_score.supported_count == len(features)
        assert chrome_score.unsupported_count == 0

    def test_old_safari_partial_or_unsupported(self, analyzer):
        features = {'css-grid', 'fetch', 'dialog'}
        report = analyzer.analyze(features, {'safari': '9'})
        safari_score = report.browser_scores['safari']
        # At least some should be unsupported/partial in Safari 9
        assert safari_score.unsupported_count + safari_score.partial_count > 0

    def test_score_is_lower_for_old_browsers(self, analyzer):
        features = {'fetch', 'promises', 'intersectionobserver', 'css-grid'}
        old_report = analyzer.analyze(features, {'ie': '11'})
        new_report = analyzer.analyze(features, {'chrome': LATEST_VERSIONS['chrome']})
        assert old_report.overall_score < new_report.overall_score


# ---------------------------------------------------------------------------
# Full pipeline: parse features → check compatibility → get polyfills
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """End-to-end: detected features → analyzer → polyfill service → file generation."""

    def test_ie11_fetch_pipeline(self, analyzer, service, tmp_path):
        # Step 1: Analyze features against IE 11
        features = {'fetch', 'promises'}
        report = analyzer.analyze(features, {'ie': '11'})

        # Step 2: Collect unsupported + partial features
        ie_score = report.browser_scores['ie']
        # fetch is unsupported, promises is partial in IE 11
        assert ie_score.unsupported_count + ie_score.partial_count == 2

        # Step 3: Get polyfill recommendations
        recs = service.get_recommendations(
            unsupported_features=features,
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) == 2

        # Step 4: Generate polyfills.js
        out = tmp_path / 'polyfills.js'
        generate_polyfills_file(recs, str(out))
        content = out.read_text(encoding='utf-8')
        assert "import 'whatwg-fetch';" in content
        assert 'npm install' in content

    def test_mixed_features_pipeline(self, analyzer, service, tmp_path):
        """Features: some supported, some not, some have polyfills, some don't."""
        features = {'fetch', 'css-grid', 'promises', 'flexbox'}
        report = analyzer.analyze(features, {'ie': '11'})

        # Gather unsupported and partial
        unsupported = set()
        partial = set()
        for issue in report.issues:
            if issue.severity.value in ('critical', 'high'):
                unsupported.add(issue.feature_id)
            elif issue.severity.value in ('medium', 'low'):
                partial.add(issue.feature_id)

        # Get polyfills for whatever is problematic
        all_problem = unsupported | partial | features  # worst case: all
        recs = service.get_recommendations(
            unsupported_features=all_problem,
            partial_features=set(),
            browsers={'ie': '11'},
        )
        # All 4 features are in polyfill_map
        assert len(recs) == 4

        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) >= 2  # fetch, promises
        assert len(cat['fallback']) >= 1  # css-grid and/or flexbox

    def test_old_safari_html_polyfills(self, analyzer, service):
        """Safari 9 doesn't support <dialog> — polyfill should be suggested."""
        features = {'dialog'}
        report = analyzer.analyze(features, {'safari': '9'})
        safari_score = report.browser_scores['safari']
        assert safari_score.unsupported_count == 1

        recs = service.get_recommendations(
            unsupported_features={'dialog'},
            partial_features=set(),
            browsers={'safari': '9'},
        )
        assert len(recs) == 1
        assert recs[0].packages[0].npm_package == 'dialog-polyfill'

    def test_latest_browsers_no_polyfills_needed(self, analyzer, service):
        """With latest browsers, common features should all be supported."""
        features = {'fetch', 'promises', 'array-includes', 'object-entries'}
        browsers = {
            'chrome': LATEST_VERSIONS['chrome'],
            'firefox': LATEST_VERSIONS['firefox'],
            'safari': LATEST_VERSIONS['safari'],
            'edge': LATEST_VERSIONS['edge'],
        }
        report = analyzer.analyze(features, browsers)
        assert report.overall_score >= 95

        # Even with full support, the service CAN still return recommendations
        # if you explicitly pass features as "unsupported" — but the point is
        # the analyzer shouldn't mark them as unsupported.
        for browser, score in report.browser_scores.items():
            assert score.unsupported_count == 0, (
                f"{browser} {score.version} has {score.unsupported_count} unsupported"
            )


# ---------------------------------------------------------------------------
# API Service facade — get_polyfill_suggestions
# ---------------------------------------------------------------------------

class TestAPIServicePolyfills:
    def test_get_polyfill_suggestions(self, api_service):
        recs = api_service.get_polyfill_suggestions(
            unsupported_features=['fetch', 'promises'],
            partial_features=[],
            browsers={'ie': '11'},
        )
        assert len(recs) == 2
        feature_ids = {r.feature_id for r in recs}
        assert 'fetch' in feature_ids
        assert 'promises' in feature_ids

    def test_get_polyfill_suggestions_empty(self, api_service):
        recs = api_service.get_polyfill_suggestions(
            unsupported_features=['totally-nonexistent'],
        )
        assert recs == []

    def test_get_polyfill_suggestions_uses_default_browsers(self, api_service):
        recs = api_service.get_polyfill_suggestions(
            unsupported_features=['fetch'],
        )
        assert len(recs) == 1
        # Should use DEFAULT_BROWSERS
        assert len(recs[0].browsers_affected) > 0

    def test_generate_polyfills_file_via_api(self, api_service, tmp_path):
        recs = api_service.get_polyfill_suggestions(
            unsupported_features=['fetch'],
            browsers={'ie': '11'},
        )
        out = tmp_path / 'polyfills.js'
        result = api_service.generate_polyfills_file(recs, str(out))
        assert Path(result).exists()
        content = Path(result).read_text(encoding='utf-8')
        assert "import 'whatwg-fetch';" in content


# ---------------------------------------------------------------------------
# Browser version ranges — polyfills should appear for old versions, disappear for new
# ---------------------------------------------------------------------------

class TestBrowserVersionBoundaries:
    """Test that features transition from unsupported to supported across versions."""

    def test_fetch_unsupported_in_chrome_39(self, db):
        """Chrome 39 didn't have fetch."""
        status = db.check_support('fetch', 'chrome', '39')
        assert status in ('n', 'u')

    def test_fetch_supported_in_chrome_42(self, db):
        """Chrome 42+ supports fetch."""
        status = db.check_support('fetch', 'chrome', '42')
        assert status in ('y', 'a')

    def test_intersectionobserver_unsupported_in_chrome_50(self, db):
        status = db.check_support('intersectionobserver', 'chrome', '50')
        assert status in ('n', 'u')

    def test_intersectionobserver_supported_in_chrome_58(self, db):
        status = db.check_support('intersectionobserver', 'chrome', '58')
        assert status in ('y', 'a')

    def test_css_grid_unsupported_in_firefox_40(self, db):
        status = db.check_support('css-grid', 'firefox', '40')
        assert status in ('n', 'u', 'p', 'x')

    def test_css_grid_supported_in_firefox_52(self, db):
        status = db.check_support('css-grid', 'firefox', '52')
        assert status in ('y', 'a')

    def test_promises_not_fully_supported_in_safari_7(self, db):
        """Safari 7 has at most partial promise support."""
        status = db.check_support('promises', 'safari', '7')
        assert status in ('n', 'u', 'p'), f"promises should not be fully supported in Safari 7, got '{status}'"

    def test_promises_supported_in_safari_10(self, db):
        status = db.check_support('promises', 'safari', '10')
        assert status in ('y', 'a')


# ---------------------------------------------------------------------------
# Polyfill recommendations align with Can I Use data
# ---------------------------------------------------------------------------

class TestPolyfillsAlignWithCanIUse:
    """The polyfill map feature IDs must correspond to real Can I Use features."""

    def test_most_polyfill_feature_ids_exist_in_caniuse(self, db):
        """Most feature IDs in polyfill_map.json should be real Can I Use features.

        Some polyfill features (e.g. array-find, object-assign) are sub-features
        that don't have their own Can I Use entry — they're covered under parent
        features. We allow a known set of exceptions.
        """
        loader = get_polyfill_loader()
        all_caniuse_features = set(db.get_all_features())

        # Sub-features that don't have direct Can I Use entries
        known_exceptions = {
            'object-assign', 'object-fromentries', 'es6-map', 'es6-set',
            'es6-weakmap', 'es6-weakset', 'es6-symbol', 'structuredclone',
            'globalthis', 'array-findindex', 'array-from', 'array-of',
            'es6-array-fill', 'focuswithin', 'focusvisible',
            'css-scroll-snap', 'input-date', 'array-find',
        }

        unexpected_missing = []
        for fid in loader.get_all_javascript_polyfills():
            if fid not in all_caniuse_features and fid not in known_exceptions:
                unexpected_missing.append(f"javascript/{fid}")
        for fid in loader.get_all_css_polyfills():
            if fid not in all_caniuse_features and fid not in known_exceptions:
                unexpected_missing.append(f"css/{fid}")
        for fid in loader.get_all_html_polyfills():
            if fid not in all_caniuse_features and fid not in known_exceptions:
                unexpected_missing.append(f"html/{fid}")

        assert unexpected_missing == [], (
            f"Polyfill map feature IDs not found in Can I Use (and not in known exceptions): "
            f"{unexpected_missing}"
        )

    def test_polyfills_target_features_that_are_sometimes_unsupported(self, db):
        """Each polyfill feature should have at least some version where it's not fully supported."""
        loader = get_polyfill_loader()

        # Test a sample of features — they should NOT be fully supported in IE 11
        sample_features = ['fetch', 'promises', 'intersectionobserver', 'css-grid', 'dialog']
        for fid in sample_features:
            assert loader.has_polyfill(fid), f"{fid} should be in polyfill map"
            status = db.check_support(fid, 'ie', '11')
            # 'y' = fully supported — polyfill would be unnecessary
            # 'a' (partial with prefix), 'p' (partial), 'n'/'u' (unsupported) are all valid
            assert status != 'y', (
                f"{fid} is fully supported in IE 11 (got '{status}'), "
                "which means the polyfill is unnecessary"
            )
