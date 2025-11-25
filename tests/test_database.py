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
    print("\n" + "="*60)
    print("TEST 1: Database Loading")
    print("="*60)
    
    db = CanIUseDatabase()
    success = db.load()
    
    if success:
        print("✓ Database loaded successfully")
        stats = db.get_statistics()
        print(f"✓ Total features: {stats['total_features']}")
        print(f"✓ Total categories: {stats['total_categories']}")
        print(f"✓ Index size: {stats['index_size']}")
        return True
    else:
        print("✗ Failed to load database")
        return False


def test_feature_lookup():
    """Test feature lookup functionality."""
    print("\n" + "="*60)
    print("TEST 2: Feature Lookup")
    print("="*60)
    
    db = get_database()
    
    # Test getting a feature
    feature = db.get_feature('flexbox')
    if feature:
        print(f"✓ Found feature: {feature.get('title', 'Unknown')}")
        print(f"  Description: {feature.get('description', 'N/A')[:80]}...")
        print(f"  Categories: {feature.get('categories', [])}")
    else:
        print("✗ Could not find 'flexbox' feature")
        return False
    
    # Test feature info
    info = db.get_feature_info('css-grid')
    if info:
        print(f"✓ Feature info for CSS Grid:")
        print(f"  Title: {info['title']}")
        print(f"  Status: {info['status']}")
    
    return True


def test_browser_support():
    """Test browser support checking."""
    print("\n" + "="*60)
    print("TEST 3: Browser Support Checking")
    print("="*60)
    
    db = get_database()
    
    # Test features
    test_cases = [
        ('flexbox', 'chrome', '144'),
        ('css-grid', 'firefox', '146'),
        ('css-variables', 'safari', '18.4'),
        ('arrow-functions', 'edge', '141'),
    ]
    
    for feature_id, browser, version in test_cases:
        status = db.check_support(feature_id, browser, version)
        status_text = {
            'y': '✓ Fully Supported',
            'a': '⚠ Partially Supported',
            'n': '✗ Not Supported',
            'u': '? Unknown',
            'x': '⚠ Requires Prefix',
            'p': 'ℹ Polyfill Available'
        }.get(status, '? Unknown')
        
        print(f"{status_text}: {feature_id} in {browser} {version}")
    
    return True


def test_search():
    """Test feature search functionality."""
    print("\n" + "="*60)
    print("TEST 4: Feature Search")
    print("="*60)
    
    db = get_database()
    
    # Search for grid-related features
    results = db.search_features('grid')
    print(f"✓ Found {len(results)} features matching 'grid':")
    for i, feature_id in enumerate(results[:5], 1):
        info = db.get_feature_info(feature_id)
        if info:
            print(f"  {i}. {feature_id}: {info['title']}")
    
    if len(results) > 5:
        print(f"  ... and {len(results) - 5} more")
    
    return True


def test_compatibility_analyzer():
    """Test compatibility analyzer."""
    print("\n" + "="*60)
    print("TEST 5: Compatibility Analysis")
    print("="*60)
    
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
    
    print(f"Analyzing {len(features)} features across {len(target_browsers)} browsers...")
    
    report = analyzer.analyze(features, target_browsers)
    
    print(f"\n✓ Analysis complete!")
    print(f"  Overall Score: {report.overall_score:.2f}%")
    print(f"  Features Analyzed: {report.features_analyzed}")
    print(f"  Critical Issues: {report.critical_issues}")
    print(f"  High Issues: {report.high_issues}")
    print(f"  Medium Issues: {report.medium_issues}")
    print(f"  Low Issues: {report.low_issues}")
    
    print(f"\n  Browser Scores:")
    for browser, score in report.browser_scores.items():
        print(f"    {browser}: {score.score:.2f}% ({score.supported_count}/{score.total_features} supported)")
    
    # Get summary
    summary = analyzer.get_summary_statistics(report)
    print(f"\n  Grade: {summary['grade']}")
    print(f"  Best Browser: {summary['best_browser']}")
    print(f"  Worst Browser: {summary['worst_browser']}")
    
    return True


def test_scorer():
    """Test scoring algorithms."""
    print("\n" + "="*60)
    print("TEST 6: Scoring Algorithms")
    print("="*60)
    
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
    print(f"✓ Simple Score: {simple_score:.2f}%")
    
    # Weighted score
    weighted = scorer.calculate_weighted_score(support_status)
    print(f"✓ Weighted Score: {weighted.weighted_score:.2f}%")
    print(f"  Breakdown:")
    for browser, score in weighted.breakdown.items():
        weight = weighted.weights[browser]
        print(f"    {browser}: {score}% (weight: {weight})")
    
    # Compatibility index
    index = scorer.calculate_compatibility_index(support_status)
    print(f"\n✓ Compatibility Index:")
    print(f"  Grade: {index['grade']}")
    print(f"  Risk Level: {index['risk_level']}")
    print(f"  Support Percentage: {index['support_percentage']}%")
    print(f"  Supported: {index['supported_count']}/{index['total_browsers']}")
    
    return True


def test_categories():
    """Test category functionality."""
    print("\n" + "="*60)
    print("TEST 7: Feature Categories")
    print("="*60)
    
    db = get_database()
    categories = db.get_feature_categories()
    
    print(f"✓ Found {len(categories)} categories:")
    
    # Show top categories
    sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    for i, (category, features) in enumerate(sorted_cats[:10], 1):
        print(f"  {i}. {category}: {len(features)} features")
    
    return True


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
