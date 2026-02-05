"""
Tests for the polyfill recommendation module.
"""

import pytest
from pathlib import Path

from src.polyfill import (
    PolyfillLoader,
    get_polyfill_loader,
    PolyfillService,
    PolyfillRecommendation,
    generate_polyfills_file,
)
from src.polyfill.polyfill_generator import generate_polyfills_content


class TestPolyfillLoader:
    """Tests for PolyfillLoader."""

    def test_singleton_instance(self):
        """Test that loader is a singleton."""
        loader1 = get_polyfill_loader()
        loader2 = get_polyfill_loader()
        assert loader1 is loader2

    def test_get_javascript_polyfill(self):
        """Test getting a JavaScript polyfill."""
        loader = get_polyfill_loader()
        polyfill = loader.get_polyfill('fetch')
        assert polyfill is not None
        assert polyfill['name'] == 'Fetch API'
        assert polyfill['polyfillable'] is True
        assert len(polyfill['packages']) > 0

    def test_get_css_polyfill(self):
        """Test getting a CSS polyfill/fallback."""
        loader = get_polyfill_loader()
        polyfill = loader.get_polyfill('css-grid')
        assert polyfill is not None
        assert polyfill['name'] == 'CSS Grid Layout'
        assert polyfill['polyfillable'] is False
        assert 'fallback' in polyfill

    def test_get_html_polyfill(self):
        """Test getting an HTML polyfill."""
        loader = get_polyfill_loader()
        polyfill = loader.get_polyfill('dialog')
        assert polyfill is not None
        assert polyfill['name'] == 'HTML <dialog> Element'
        assert polyfill['polyfillable'] is True

    def test_get_nonexistent_polyfill(self):
        """Test getting a polyfill that doesn't exist."""
        loader = get_polyfill_loader()
        polyfill = loader.get_polyfill('nonexistent-feature')
        assert polyfill is None

    def test_has_polyfill(self):
        """Test has_polyfill method."""
        loader = get_polyfill_loader()
        assert loader.has_polyfill('fetch') is True
        assert loader.has_polyfill('css-grid') is True  # Has fallback
        assert loader.has_polyfill('nonexistent') is False

    def test_is_polyfillable(self):
        """Test is_polyfillable method."""
        loader = get_polyfill_loader()
        assert loader.is_polyfillable('fetch') is True
        assert loader.is_polyfillable('css-grid') is False  # Only fallback
        assert loader.is_polyfillable('nonexistent') is False

    def test_get_metadata(self):
        """Test getting metadata."""
        loader = get_polyfill_loader()
        metadata = loader.get_metadata()
        assert 'version' in metadata
        assert 'description' in metadata


class TestPolyfillService:
    """Tests for PolyfillService."""

    def test_get_recommendations_npm(self):
        """Test getting npm polyfill recommendations."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'promises'},
            partial_features=set(),
            browsers={'ie': '11'}
        )
        assert len(recs) == 2

        feature_names = {rec.feature_name for rec in recs}
        assert 'Fetch API' in feature_names
        assert 'JavaScript Promises' in feature_names

        for rec in recs:
            assert rec.polyfill_type == 'npm'
            assert len(rec.packages) > 0

    def test_get_recommendations_css_fallback(self):
        """Test getting CSS fallback recommendations."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'css-grid'},
            partial_features=set(),
            browsers={'ie': '11'}
        )
        assert len(recs) == 1
        assert recs[0].polyfill_type == 'fallback'
        assert recs[0].fallback_code is not None
        assert recs[0].fallback_description is not None

    def test_get_recommendations_partial_features(self):
        """Test that partial features also get recommendations."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features=set(),
            partial_features={'fetch'},
            browsers={'safari': '14'}
        )
        assert len(recs) == 1
        assert recs[0].feature_name == 'Fetch API'

    def test_get_recommendations_empty(self):
        """Test with no matching features."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'nonexistent-feature'},
            partial_features=set(),
            browsers={'chrome': '90'}
        )
        assert len(recs) == 0

    def test_get_aggregate_install_command(self):
        """Test aggregate npm install command generation."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'promises'},
            partial_features=set(),
            browsers={'ie': '11'}
        )
        cmd = service.get_aggregate_install_command(recs)
        assert cmd.startswith('npm install')
        assert 'whatwg-fetch' in cmd
        assert 'core-js' in cmd

    def test_get_aggregate_imports(self):
        """Test aggregate import statements generation."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'fetch'},
            partial_features=set(),
            browsers={'ie': '11'}
        )
        imports = service.get_aggregate_imports(recs)
        assert len(imports) == 1
        assert "import 'whatwg-fetch';" in imports[0]

    def test_get_total_size(self):
        """Test total size calculation."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'promises'},
            partial_features=set(),
            browsers={'ie': '11'}
        )
        total_size = service.get_total_size_kb(recs)
        assert total_size > 0

    def test_categorize_recommendations(self):
        """Test categorizing recommendations by type."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'css-grid'},
            partial_features=set(),
            browsers={'ie': '11'}
        )
        categorized = service.categorize_recommendations(recs)
        assert 'npm' in categorized
        assert 'fallback' in categorized
        assert len(categorized['npm']) == 1
        assert len(categorized['fallback']) == 1


class TestPolyfillGenerator:
    """Tests for polyfill file generation."""

    def test_generate_polyfills_content(self):
        """Test generating polyfills.js content."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'promises'},
            partial_features=set(),
            browsers={'ie': '11'}
        )
        content = generate_polyfills_content(recs)

        assert 'Auto-generated by Cross Guard' in content
        assert "import './polyfills';" in content
        assert "import 'whatwg-fetch';" in content

    def test_generate_polyfills_file(self, tmp_path):
        """Test generating polyfills.js file."""
        service = PolyfillService()
        recs = service.get_recommendations(
            unsupported_features={'fetch'},
            partial_features=set(),
            browsers={'ie': '11'}
        )

        output_path = tmp_path / 'polyfills.js'
        result = generate_polyfills_file(recs, str(output_path))

        assert Path(result).exists()
        content = Path(result).read_text()
        assert "import 'whatwg-fetch';" in content


class TestPolyfillMapIntegrity:
    """Tests for polyfill_map.json integrity."""

    def test_all_polyfillable_have_packages(self):
        """Test that all polyfillable entries have at least one package."""
        loader = get_polyfill_loader()

        for feature_id, info in loader.get_all_javascript_polyfills().items():
            if info.get('polyfillable'):
                assert 'packages' in info, f"{feature_id} is polyfillable but has no packages"
                assert len(info['packages']) > 0, f"{feature_id} has empty packages list"

        for feature_id, info in loader.get_all_html_polyfills().items():
            if info.get('polyfillable'):
                assert 'packages' in info, f"{feature_id} is polyfillable but has no packages"

    def test_all_fallbacks_have_code(self):
        """Test that all CSS fallbacks have code."""
        loader = get_polyfill_loader()

        for feature_id, info in loader.get_all_css_polyfills().items():
            if 'fallback' in info:
                fallback = info['fallback']
                assert 'code' in fallback, f"{feature_id} fallback has no code"
                assert 'description' in fallback, f"{feature_id} fallback has no description"

    def test_packages_have_required_fields(self):
        """Test that all packages have required fields."""
        loader = get_polyfill_loader()

        for feature_id, info in loader.get_all_javascript_polyfills().items():
            for pkg in info.get('packages', []):
                assert 'name' in pkg, f"{feature_id} package missing name"
                assert 'npm' in pkg, f"{feature_id} package missing npm"
                assert 'import' in pkg, f"{feature_id} package missing import"
