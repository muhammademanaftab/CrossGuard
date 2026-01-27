"""Test suite for database loader and analyzer."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer.database import CanIUseDatabase, get_database
from src.analyzer.compatibility import CompatibilityAnalyzer, Severity
from src.analyzer.scorer import CompatibilityScorer


def test_database_loading():
    """Test database loading functionality."""
    db = CanIUseDatabase()
    success = db.load()

    assert success, "Failed to load database"

    stats = db.get_statistics()
    assert stats['total_features'] > 0, "No features loaded"
    assert stats['total_categories'] > 0, "No categories loaded"
    assert stats['index_size'] > 0, "Index is empty"


def test_feature_lookup():
    """Test feature lookup functionality."""
    db = get_database()

    # Test getting a feature
    feature = db.get_feature('flexbox')
    assert feature is not None, "Could not find 'flexbox' feature"
    assert 'title' in feature or 'description' in feature

    # Test feature info
    info = db.get_feature_info('css-grid')
    assert info is not None, "Could not get info for 'css-grid'"
    assert 'title' in info
    assert 'status' in info


def test_browser_support():
    """Test browser support checking."""
    db = get_database()

    # Test features - these should all be supported in modern browsers
    test_cases = [
        ('flexbox', 'chrome', '144'),
        ('css-grid', 'firefox', '146'),
        ('css-variables', 'safari', '18.4'),
        ('arrow-functions', 'edge', '141'),
    ]

    for feature_id, browser, version in test_cases:
        status = db.check_support(feature_id, browser, version)
        # Status should be one of: y (yes), a (partial), n (no), u (unknown), x (prefix), p (polyfill)
        assert status in ('y', 'a', 'n', 'u', 'x', 'p'), f"Invalid status '{status}' for {feature_id}"
        # Modern browsers should support these features
        assert status in ('y', 'a'), f"{feature_id} should be supported in {browser} {version}, got {status}"


def test_search():
    """Test feature search functionality."""
    db = get_database()

    # Search for grid-related features
    results = db.search_features('grid')
    assert len(results) > 0, "No results found for 'grid' search"

    # css-grid should be in results
    assert 'css-grid' in results, "'css-grid' not found in search results"


def test_compatibility_analyzer():
    """Test compatibility analyzer."""
    analyzer = CompatibilityAnalyzer()

    # Test features
    features = {'flexbox', 'css-grid', 'css-variables', 'arrow-functions'}

    # Target browsers
    target_browsers = {
        'chrome': '144',
        'firefox': '146',
        'safari': '18.4',
        'edge': '141'
    }

    report = analyzer.analyze(features, target_browsers)

    # Verify report structure
    assert report.overall_score >= 0, "Overall score should be non-negative"
    assert report.features_analyzed == len(features), "Features analyzed count mismatch"
    assert len(report.browser_scores) == len(target_browsers), "Browser scores count mismatch"

    # Get summary
    summary = analyzer.get_summary_statistics(report)
    assert 'grade' in summary, "Summary missing grade"
    assert 'best_browser' in summary, "Summary missing best_browser"
    assert 'worst_browser' in summary, "Summary missing worst_browser"


def test_scorer():
    """Test scoring algorithms."""
    scorer = CompatibilityScorer()

    # Test support status
    support_status = {
        'chrome': 'y',
        'firefox': 'y',
        'safari': 'a',
        'edge': 'y',
        'ie': 'n'
    }

    # Simple score
    simple_score = scorer.calculate_simple_score(support_status)
    assert 0 <= simple_score <= 100, "Simple score out of range"

    # Weighted score
    weighted = scorer.calculate_weighted_score(support_status)
    assert 0 <= weighted.weighted_score <= 100, "Weighted score out of range"
    assert len(weighted.breakdown) > 0, "Weighted breakdown is empty"

    # Compatibility index
    index = scorer.calculate_compatibility_index(support_status)
    assert 'grade' in index, "Index missing grade"
    assert 'risk_level' in index, "Index missing risk_level"
    assert 'support_percentage' in index, "Index missing support_percentage"


def test_categories():
    """Test category functionality."""
    db = get_database()
    categories = db.get_feature_categories()

    assert len(categories) > 0, "No categories found"

    # Each category should have at least one feature
    for category, features in categories.items():
        assert len(features) > 0, f"Category '{category}' has no features"


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("CROSS GUARD - DATABASE & ANALYZER TESTS")
    print("="*60)
    
    tests = [
        test_database_loading,
        test_feature_lookup,
        test_browser_support,
        test_search,
        test_compatibility_analyzer,
        test_scorer,
        test_categories
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
