"""Tests for PolyfillService — recommendations, aggregation, categorization, generation."""

import re
import pytest
from pathlib import Path

from src.polyfill.polyfill_service import (
    PolyfillService,
    PolyfillRecommendation,
    PolyfillPackage,
)
from src.polyfill.polyfill_generator import (
    generate_polyfills_file,
    generate_polyfills_content,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return PolyfillService()


@pytest.fixture
def npm_recs(service):
    """Recommendations with npm packages only."""
    return service.get_recommendations(
        unsupported_features={'fetch', 'promises'},
        partial_features=set(),
        browsers={'ie': '11'},
    )


@pytest.fixture
def fallback_recs(service):
    """Recommendations with CSS fallback only."""
    return service.get_recommendations(
        unsupported_features={'css-grid'},
        partial_features=set(),
        browsers={'ie': '11'},
    )


@pytest.fixture
def mixed_recs(service):
    """Both npm and fallback recommendations."""
    return service.get_recommendations(
        unsupported_features={'fetch', 'css-grid', 'dialog'},
        partial_features=set(),
        browsers={'ie': '11'},
    )


# ---------------------------------------------------------------------------
# Dataclass construction
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_package_required_fields_only(self):
        pkg = PolyfillPackage(name='test', npm_package='test-pkg', import_statement="import 'test';")
        assert pkg.cdn_url is None
        assert pkg.size_kb is None
        assert pkg.note is None

    def test_package_all_fields(self):
        pkg = PolyfillPackage(
            name='test', npm_package='test-pkg', import_statement="import 'test';",
            cdn_url='https://cdn.example.com/test.js', size_kb=1.5, note='A note',
        )
        assert pkg.cdn_url == 'https://cdn.example.com/test.js'
        assert pkg.size_kb == 1.5
        assert pkg.note == 'A note'

    def test_recommendation_npm_type(self):
        rec = PolyfillRecommendation(
            feature_id='fetch', feature_name='Fetch API', polyfill_type='npm',
            packages=[PolyfillPackage(name='whatwg-fetch', npm_package='whatwg-fetch',
                                     import_statement="import 'whatwg-fetch';", size_kb=3.2)],
            browsers_affected=['ie'],
        )
        assert rec.polyfill_type == 'npm'
        assert len(rec.packages) == 1
        assert rec.fallback_code is None

    def test_recommendation_fallback_type(self):
        rec = PolyfillRecommendation(
            feature_id='css-grid', feature_name='CSS Grid Layout', polyfill_type='fallback',
            packages=[], fallback_code='/* Flexbox fallback */',
            fallback_description='Use Flexbox as fallback', browsers_affected=['ie'],
        )
        assert rec.polyfill_type == 'fallback'
        assert len(rec.packages) == 0
        assert rec.fallback_code is not None

    def test_recommendation_default_empty_lists(self):
        rec = PolyfillRecommendation(feature_id='x', feature_name='X', polyfill_type='npm')
        assert rec.packages == []
        assert rec.browsers_affected == []


# ---------------------------------------------------------------------------
# get_recommendations — core behaviour
# ---------------------------------------------------------------------------

class TestGetRecommendations:
    def test_single_npm_feature(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        assert len(recs) == 1
        assert recs[0].feature_id == 'fetch'
        assert recs[0].polyfill_type == 'npm'

    def test_single_css_fallback(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        assert len(recs) == 1
        assert recs[0].polyfill_type == 'fallback'
        assert recs[0].fallback_code is not None

    def test_partial_features_produce_recommendations(self, service):
        recs = service.get_recommendations(
            unsupported_features=set(), partial_features={'fetch'}, browsers={'safari': '10'},
        )
        assert len(recs) == 1
        assert recs[0].feature_id == 'fetch'

    def test_mixed_unsupported_and_partial(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features={'css-grid'}, browsers={'ie': '11'},
        )
        ids = {r.feature_id for r in recs}
        assert 'fetch' in ids and 'css-grid' in ids

    def test_no_duplicates_when_in_both_sets(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features={'fetch'}, browsers={'ie': '11'},
        )
        assert len(recs) == 1

    def test_sorted_by_feature_id(self, service):
        recs = service.get_recommendations(
            unsupported_features={'promises', 'fetch', 'array-includes'},
            partial_features=set(), browsers={'ie': '11'},
        )
        ids = [r.feature_id for r in recs]
        assert ids == sorted(ids)

    def test_browsers_affected_matches_input(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(),
            browsers={'chrome': '40', 'firefox': '30'},
        )
        assert set(recs[0].browsers_affected) == {'chrome', 'firefox'}

    def test_empty_feature_sets(self, service):
        recs = service.get_recommendations(
            unsupported_features=set(), partial_features=set(), browsers={'chrome': '120'},
        )
        assert recs == []

    def test_nonexistent_features(self, service):
        recs = service.get_recommendations(
            unsupported_features={'totally-fake', 'another-fake'},
            partial_features=set(), browsers={'chrome': '120'},
        )
        assert recs == []

    def test_mix_of_real_and_fake(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'totally-fake'},
            partial_features=set(), browsers={'ie': '11'},
        )
        assert len(recs) == 1 and recs[0].feature_id == 'fetch'

    def test_empty_browsers_dict(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={},
        )
        assert len(recs) == 1 and recs[0].browsers_affected == []


# ---------------------------------------------------------------------------
# All features produce correct recommendations (batch tests, not per-feature)
# ---------------------------------------------------------------------------

class TestAllFeaturesRecommendations:
    ALL_JS = [
        'fetch', 'promises', 'async-functions', 'array-includes', 'array-flat',
        'object-entries', 'object-values', 'object-assign', 'object-fromentries',
        'pad-start-end', 'es6-string-includes', 'es6-number',
        'es6-map', 'es6-set', 'es6-weakmap', 'es6-weakset', 'es6-symbol', 'proxy',
        'intersectionobserver', 'resizeobserver', 'mutationobserver',
        'requestanimationframe', 'classlist', 'url', 'urlsearchparams',
        'customevent', 'abortcontroller', 'textencoder', 'matchmedia',
        'requestidlecallback', 'structuredclone', 'broadcastchannel', 'globalthis',
        'array-findindex', 'array-find', 'array-from', 'array-of', 'es6-array-fill',
        'pointer', 'focuswithin', 'focusvisible',
    ]
    CSS_NPM = ['css-variables', 'css-sticky', 'object-fit', 'css-scroll-snap', 'css-scroll-behavior']
    CSS_FALLBACK = ['css-grid', 'flexbox', 'css-backdrop-filter', 'css-filters']
    HTML = ['dialog', 'details', 'datalist', 'picture', 'template', 'input-color', 'input-date']

    def test_all_js_produce_npm_recommendations(self, service):
        """Every JS feature produces an npm recommendation with packages."""
        for fid in self.ALL_JS:
            recs = service.get_recommendations(
                unsupported_features={fid}, partial_features=set(), browsers={'ie': '11'},
            )
            assert len(recs) == 1, f"{fid} should produce 1 recommendation"
            assert recs[0].polyfill_type == 'npm', f"{fid} should be npm type"
            assert len(recs[0].packages) > 0, f"{fid} should have packages"

    def test_all_css_npm_produce_npm_recommendations(self, service):
        """Every CSS npm feature produces an npm recommendation."""
        for fid in self.CSS_NPM:
            recs = service.get_recommendations(
                unsupported_features={fid}, partial_features=set(), browsers={'ie': '11'},
            )
            assert len(recs) == 1 and recs[0].polyfill_type == 'npm', f"{fid} failed"

    def test_all_css_fallback_produce_fallback_recommendations(self, service):
        """Every CSS fallback feature produces a fallback recommendation with code."""
        for fid in self.CSS_FALLBACK:
            recs = service.get_recommendations(
                unsupported_features={fid}, partial_features=set(), browsers={'ie': '11'},
            )
            assert len(recs) == 1, f"{fid} should produce 1 recommendation"
            assert recs[0].polyfill_type == 'fallback', f"{fid} should be fallback type"
            assert recs[0].fallback_code and len(recs[0].fallback_code) > 0, f"{fid} missing fallback code"

    def test_all_html_produce_npm_recommendations(self, service):
        """Every HTML feature produces an npm recommendation with packages."""
        for fid in self.HTML:
            recs = service.get_recommendations(
                unsupported_features={fid}, partial_features=set(), browsers={'ie': '11'},
            )
            assert len(recs) == 1, f"{fid} should produce 1 recommendation"
            assert recs[0].polyfill_type == 'npm', f"{fid} should be npm type"
            assert len(recs[0].packages) > 0, f"{fid} should have packages"


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

class TestAggregation:
    def test_install_cmd_single_package(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        assert service.get_aggregate_install_command(recs) == 'npm install whatwg-fetch'

    def test_install_cmd_sorted_packages(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'requestidlecallback', 'abortcontroller'},
            partial_features=set(), browsers={'ie': '11'},
        )
        cmd = service.get_aggregate_install_command(recs)
        packages = cmd.replace('npm install ', '').split()
        assert packages == sorted(packages)

    def test_install_cmd_deduplication(self, service):
        recs = service.get_recommendations(
            unsupported_features={'array-includes', 'object-entries', 'globalthis'},
            partial_features=set(), browsers={'ie': '11'},
        )
        assert service.get_aggregate_install_command(recs).count('core-js') == 1

    def test_install_cmd_empty(self, service):
        assert service.get_aggregate_install_command([]) == ''

    def test_install_cmd_fallback_only(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        assert service.get_aggregate_install_command(recs) == ''

    def test_imports_single(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        imports = service.get_aggregate_imports(recs)
        assert len(imports) == 1 and "import 'whatwg-fetch';" in imports[0]

    def test_imports_multiple(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'abortcontroller'},
            partial_features=set(), browsers={'ie': '11'},
        )
        assert len(service.get_aggregate_imports(recs)) == 2

    def test_imports_fallback_only(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        assert service.get_aggregate_imports(recs) == []

    def test_imports_empty(self, service):
        assert service.get_aggregate_imports([]) == []


# ---------------------------------------------------------------------------
# Size calculation
# ---------------------------------------------------------------------------

class TestTotalSize:
    def test_single_package_size(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        assert service.get_total_size_kb(recs) == 3.2

    def test_multiple_packages_sum(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'intersectionobserver'},
            partial_features=set(), browsers={'ie': '11'},
        )
        assert service.get_total_size_kb(recs) == pytest.approx(3.2 + 4.8, rel=0.01)

    def test_fallback_zero_size(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        assert service.get_total_size_kb(recs) == 0.0

    def test_empty_zero_size(self, service):
        assert service.get_total_size_kb([]) == 0.0


# ---------------------------------------------------------------------------
# Categorization
# ---------------------------------------------------------------------------

class TestCategorize:
    def test_npm_only(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) == 1 and len(cat['fallback']) == 0

    def test_fallback_only(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) == 0 and len(cat['fallback']) == 1

    def test_mixed(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'css-grid', 'promises'},
            partial_features=set(), browsers={'ie': '11'},
        )
        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) == 2 and len(cat['fallback']) == 1

    def test_empty(self, service):
        assert service.categorize_recommendations([]) == {'npm': [], 'fallback': []}


# ---------------------------------------------------------------------------
# Large batch — all features at once
# ---------------------------------------------------------------------------

class TestLargeBatch:
    ALL_FEATURES = {
        'fetch', 'promises', 'async-functions', 'array-includes', 'array-flat',
        'object-entries', 'object-values', 'object-assign', 'object-fromentries',
        'pad-start-end', 'es6-string-includes', 'es6-number',
        'es6-map', 'es6-set', 'es6-weakmap', 'es6-weakset', 'es6-symbol', 'proxy',
        'intersectionobserver', 'resizeobserver', 'mutationobserver',
        'requestanimationframe', 'classlist', 'url', 'urlsearchparams',
        'customevent', 'abortcontroller', 'textencoder', 'matchmedia',
        'requestidlecallback', 'structuredclone', 'broadcastchannel', 'globalthis',
        'array-findindex', 'array-find', 'array-from', 'array-of', 'es6-array-fill',
        'pointer', 'focuswithin', 'focusvisible',
        'css-grid', 'flexbox', 'css-backdrop-filter', 'css-filters',
        'css-variables', 'css-sticky', 'object-fit', 'css-scroll-snap', 'css-scroll-behavior',
        'dialog', 'details', 'datalist', 'picture', 'template', 'input-color', 'input-date',
    }

    def test_all_produce_recommendations(self, service):
        recs = service.get_recommendations(
            unsupported_features=self.ALL_FEATURES, partial_features=set(), browsers={'ie': '11'},
        )
        assert len(recs) >= 53

    def test_all_ids_unique(self, service):
        recs = service.get_recommendations(
            unsupported_features=self.ALL_FEATURES, partial_features=set(), browsers={'ie': '11'},
        )
        ids = [r.feature_id for r in recs]
        assert len(ids) == len(set(ids))

    def test_install_command_not_empty(self, service):
        recs = service.get_recommendations(
            unsupported_features=self.ALL_FEATURES, partial_features=set(), browsers={'ie': '11'},
        )
        assert len(service.get_aggregate_install_command(recs)) > len('npm install ')

    def test_total_size_is_sum_of_first_packages(self, service):
        recs = service.get_recommendations(
            unsupported_features=self.ALL_FEATURES, partial_features=set(), browsers={'ie': '11'},
        )
        manual_sum = sum(
            rec.packages[0].size_kb
            for rec in recs
            if rec.polyfill_type == 'npm' and rec.packages and rec.packages[0].size_kb
        )
        assert service.get_total_size_kb(recs) == pytest.approx(manual_sum)


# ---------------------------------------------------------------------------
# Content generation (merged from test_polyfill_generator.py)
# ---------------------------------------------------------------------------

class TestGenerateContent:
    def test_header_and_imports(self, npm_recs):
        content = generate_polyfills_content(npm_recs)
        assert 'Auto-generated by Cross Guard' in content
        assert "import './polyfills';" in content
        assert "import 'whatwg-fetch';" in content

    def test_feature_names_as_comments(self, npm_recs):
        content = generate_polyfills_content(npm_recs)
        assert '// Fetch API' in content
        assert '// JavaScript Promises' in content

    def test_has_timestamp(self, npm_recs):
        content = generate_polyfills_content(npm_recs)
        assert re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', content)

    def test_fallback_only_no_imports(self, fallback_recs):
        content = generate_polyfills_content(fallback_recs)
        assert 'import' not in content or "import './polyfills'" in content

    def test_empty_recs_still_valid(self):
        content = generate_polyfills_content([])
        assert 'Auto-generated by Cross Guard' in content

    def test_correct_imports_in_content(self, service):
        """Verify specific import statements appear in generated content."""
        cases = [
            ('fetch', "import 'whatwg-fetch';"),
            ('intersectionobserver', "import 'intersection-observer';"),
            ('requestidlecallback', "import 'requestidlecallback-polyfill';"),
            ('abortcontroller', "import 'abortcontroller-polyfill/dist/polyfill-patch-fetch';"),
            ('globalthis', "import 'core-js/features/global-this';"),
            ('classlist', "import 'classlist-polyfill';"),
        ]
        for fid, expected_import in cases:
            recs = service.get_recommendations(
                unsupported_features={fid}, partial_features=set(), browsers={'ie': '11'},
            )
            assert expected_import in generate_polyfills_content(recs), f"{fid}: missing {expected_import}"


# ---------------------------------------------------------------------------
# File generation (merged from test_polyfill_generator.py)
# ---------------------------------------------------------------------------

class TestGenerateFile:
    def test_creates_file_and_returns_path(self, tmp_path, npm_recs):
        out = tmp_path / 'polyfills.js'
        result = generate_polyfills_file(npm_recs, str(out))
        assert result == str(out)
        assert Path(result).exists()

    def test_file_contains_imports_and_install(self, tmp_path, npm_recs):
        out = tmp_path / 'polyfills.js'
        generate_polyfills_file(npm_recs, str(out))
        content = out.read_text(encoding='utf-8')
        assert "import 'whatwg-fetch';" in content
        assert 'npm install' in content
        assert 'whatwg-fetch' in content

    def test_fallback_only_file(self, tmp_path, fallback_recs):
        out = tmp_path / 'polyfills.js'
        generate_polyfills_file(fallback_recs, str(out))
        assert 'No npm polyfills needed' in out.read_text(encoding='utf-8')

    def test_empty_recs_file(self, tmp_path):
        out = tmp_path / 'polyfills.js'
        generate_polyfills_file([], str(out))
        assert 'No npm polyfills needed' in out.read_text(encoding='utf-8')

    def test_overwrite_existing_file(self, tmp_path, npm_recs):
        out = tmp_path / 'polyfills.js'
        out.write_text('OLD CONTENT', encoding='utf-8')
        generate_polyfills_file(npm_recs, str(out))
        content = out.read_text(encoding='utf-8')
        assert 'OLD CONTENT' not in content
        assert 'Auto-generated' in content

    def test_nested_directory_path(self, tmp_path, npm_recs):
        out = tmp_path / 'deep' / 'nested' / 'polyfills.js'
        out.parent.mkdir(parents=True)
        assert Path(generate_polyfills_file(npm_recs, str(out))).exists()

    def test_npm_packages_in_generated_files(self, service, tmp_path):
        """Verify specific npm packages appear in generated files."""
        cases = [
            ('fetch', 'whatwg-fetch'),
            ('intersectionobserver', 'intersection-observer'),
            ('structuredclone', '@ungap/structured-clone'),
            ('broadcastchannel', 'broadcast-channel'),
            ('dialog', 'dialog-polyfill'),
        ]
        for fid, expected_npm in cases:
            recs = service.get_recommendations(
                unsupported_features={fid}, partial_features=set(), browsers={'ie': '11'},
            )
            out = tmp_path / f'polyfills_{fid}.js'
            generate_polyfills_file(recs, str(out))
            assert expected_npm in out.read_text(encoding='utf-8'), f"{fid}: missing {expected_npm}"

    def test_multiline_import_preserved(self, service):
        recs = service.get_recommendations(
            unsupported_features={'structuredclone'}, partial_features=set(), browsers={'ie': '11'},
        )
        import_stmt = recs[0].packages[0].import_statement
        assert '\n' in import_stmt or 'structuredClone' in import_stmt
