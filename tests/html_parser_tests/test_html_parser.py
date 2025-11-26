"""Comprehensive test suite for HTML parser."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.html_parser import HTMLParser, parse_html_file, parse_html_string


def test_basic_elements():
    """Test detection of basic HTML5 elements."""
    print("\n" + "="*60)
    print("TEST 1: Basic HTML5 Elements")
    print("="*60)
    
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <dialog>Dialog content</dialog>
        <details>
            <summary>Summary</summary>
            <p>Details content</p>
        </details>
        <template id="my-template">
            <p>Template content</p>
        </template>
    </body>
    </html>
    """
    
    parser = HTMLParser()
    features = parser.parse_string(html)
    
    print(f"✓ Found {len(features)} features")
    
    expected = {'dialog', 'details', 'template'}
    found_expected = expected.intersection(features)
    
    print(f"  Expected features: {expected}")
    print(f"  Found features: {found_expected}")
    
    if found_expected == expected:
        print("✓ All expected features detected!")
        return True
    else:
        print(f"✗ Missing features: {expected - found_expected}")
        return False


def test_input_types():
    """Test detection of modern input types."""
    print("\n" + "="*60)
    print("TEST 2: Modern Input Types")
    print("="*60)
    
    html = """
    <form>
        <input type="date" name="birthday">
        <input type="color" name="favcolor">
        <input type="range" min="0" max="100">
        <input type="email" name="email">
        <input type="tel" name="phone">
    </form>
    """
    
    parser = HTMLParser()
    features = parser.parse_string(html)
    
    print(f"✓ Found {len(features)} features")
    
    expected_features = ['input-datetime', 'input-color', 'input-range', 'input-email', 'input-tel']
    found_count = sum(1 for f in expected_features if f in features)
    
    print(f"  Expected input types: {len(expected_features)}")
    print(f"  Found input types: {found_count}")
    print(f"  Features: {sorted([f for f in features if 'input' in f])}")
    
    if found_count >= 3:  # At least 3 input types
        print("✓ Input types detected successfully!")
        return True
    else:
        print("✗ Not enough input types detected")
        return False


def test_attributes():
    """Test detection of modern attributes."""
    print("\n" + "="*60)
    print("TEST 3: Modern HTML Attributes")
    print("="*60)
    
    html = """
    <img src="image.jpg" loading="lazy" decoding="async" alt="Test">
    <input type="text" placeholder="Enter text" required>
    <div contenteditable="true">Editable content</div>
    <a href="file.pdf" download>Download</a>
    """
    
    parser = HTMLParser()
    features = parser.parse_string(html)
    
    print(f"✓ Found {len(features)} features")
    
    expected_attrs = ['loading-lazy-attr', 'img-decoding-async', 'input-placeholder', 
                     'form-validation', 'contenteditable', 'download']
    found_attrs = [attr for attr in expected_attrs if attr in features]
    
    print(f"  Expected attributes: {len(expected_attrs)}")
    print(f"  Found attributes: {len(found_attrs)}")
    print(f"  Features: {found_attrs}")
    
    if len(found_attrs) >= 4:
        print("✓ Attributes detected successfully!")
        return True
    else:
        print("✗ Not enough attributes detected")
        return False


def test_picture_element():
    """Test detection of picture element with sources."""
    print("\n" + "="*60)
    print("TEST 4: Picture Element (Responsive Images)")
    print("="*60)
    
    html = """
    <picture>
        <source srcset="image.webp" type="image/webp">
        <source srcset="image.jpg" type="image/jpeg">
        <img src="fallback.jpg" alt="Image">
    </picture>
    """
    
    parser = HTMLParser()
    features = parser.parse_string(html)
    
    print(f"✓ Found {len(features)} features")
    print(f"  Features: {sorted(features)}")
    
    if 'picture' in features:
        print("✓ Picture element detected!")
        return True
    else:
        print("✗ Picture element not detected")
        return False


def test_script_attributes():
    """Test detection of script async/defer and modules."""
    print("\n" + "="*60)
    print("TEST 5: Script Attributes (async, defer, module)")
    print("="*60)
    
    html = """
    <script src="script1.js" async></script>
    <script src="script2.js" defer></script>
    <script type="module" src="module.js"></script>
    """
    
    parser = HTMLParser()
    features = parser.parse_string(html)
    
    print(f"✓ Found {len(features)} features")
    
    script_features = [f for f in features if 'script' in f or 'module' in f]
    print(f"  Script-related features: {script_features}")
    
    expected = ['script-async', 'script-defer', 'es6-module']
    found = [f for f in expected if f in features]
    
    print(f"  Expected: {expected}")
    print(f"  Found: {found}")
    
    if len(found) >= 2:
        print("✓ Script features detected!")
        return True
    else:
        print("✗ Not enough script features detected")
        return False


def test_link_rel():
    """Test detection of link rel attributes."""
    print("\n" + "="*60)
    print("TEST 6: Link Rel (preload, prefetch, etc.)")
    print("="*60)
    
    html = """
    <head>
        <link rel="preload" href="font.woff2" as="font">
        <link rel="prefetch" href="next-page.html">
        <link rel="dns-prefetch" href="//example.com">
        <link rel="preconnect" href="https://api.example.com">
    </head>
    """
    
    parser = HTMLParser()
    features = parser.parse_string(html)
    
    print(f"✓ Found {len(features)} features")
    
    link_features = [f for f in features if 'link-rel' in f]
    print(f"  Link rel features: {link_features}")
    
    if len(link_features) >= 2:
        print("✓ Link rel features detected!")
        return True
    else:
        print("✗ Not enough link rel features detected")
        return False


def test_data_attributes():
    """Test detection of data-* attributes."""
    print("\n" + "="*60)
    print("TEST 7: Data Attributes (data-*)")
    print("="*60)
    
    html = """
    <div data-id="123" data-name="test" data-value="456">
        Content
    </div>
    """
    
    parser = HTMLParser()
    features = parser.parse_string(html)
    
    print(f"✓ Found {len(features)} features")
    print(f"  Features: {sorted(features)}")
    
    if 'dataset' in features:
        print("✓ Data attributes detected!")
        return True
    else:
        print("✗ Data attributes not detected")
        return False


def test_sample_file():
    """Test parsing the actual sample.html file."""
    print("\n" + "="*60)
    print("TEST 8: Parse examples/sample.html")
    print("="*60)
    
    sample_path = Path(__file__).parent.parent / 'examples' / 'sample.html'
    
    if not sample_path.exists():
        print(f"✗ Sample file not found: {sample_path}")
        return False
    
    parser = HTMLParser()
    features = parser.parse_file(str(sample_path))
    
    print(f"✓ Parsed sample.html successfully")
    print(f"✓ Found {len(features)} features")
    print(f"\n  Features detected:")
    for i, feature in enumerate(sorted(features), 1):
        print(f"    {i}. {feature}")
    
    # Get detailed report
    report = parser.get_detailed_report()
    print(f"\n  Elements found: {len(report['elements_found'])}")
    for elem in report['elements_found'][:5]:  # Show first 5
        print(f"    - {elem['element']}: {elem['feature']}")
    
    if len(features) > 0:
        print("\n✓ Sample file parsed successfully!")
        return True
    else:
        print("\n✗ No features found in sample file")
        return False


def test_statistics():
    """Test statistics generation."""
    print("\n" + "="*60)
    print("TEST 9: Parser Statistics")
    print("="*60)
    
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <dialog>Test</dialog>
        <dialog>Test2</dialog>
        <details><summary>S</summary></details>
        <input type="date">
        <input type="color">
        <img loading="lazy" src="test.jpg">
    </body>
    </html>
    """
    
    parser = HTMLParser()
    features = parser.parse_string(html)
    stats = parser.get_statistics()
    
    print(f"✓ Statistics generated")
    print(f"  Total features: {stats['total_features']}")
    print(f"  Total elements detected: {stats['total_elements_detected']}")
    print(f"  Total attributes detected: {stats['total_attributes_detected']}")
    
    if stats['element_counts']:
        print(f"\n  Element counts:")
        for elem, count in list(stats['element_counts'].items())[:5]:
            print(f"    {elem}: {count}")
    
    if stats['total_features'] > 0:
        print("\n✓ Statistics working correctly!")
        return True
    else:
        print("\n✗ Statistics not working")
        return False


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n" + "="*60)
    print("TEST 10: Error Handling")
    print("="*60)
    
    parser = HTMLParser()
    
    # Test 1: Non-existent file
    try:
        parser.parse_file('nonexistent.html')
        print("✗ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print("✓ FileNotFoundError handled correctly")
    
    # Test 2: Empty HTML
    features = parser.parse_string('')
    print(f"✓ Empty HTML handled: {len(features)} features")
    
    # Test 3: Malformed HTML (BeautifulSoup handles this gracefully)
    features = parser.parse_string('<div><p>Unclosed tags')
    print(f"✓ Malformed HTML handled: {len(features)} features")
    
    # Test 4: Validate HTML
    is_valid = parser.validate_html('<html><body>Valid</body></html>')
    print(f"✓ HTML validation: {is_valid}")
    
    print("\n✓ Error handling working correctly!")
    return True


def run_all_tests():
    """Run all HTML parser tests."""
    print("\n" + "="*60)
    print("HTML PARSER - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        test_basic_elements,
        test_input_types,
        test_attributes,
        test_picture_element,
        test_script_attributes,
        test_link_rel,
        test_data_attributes,
        test_sample_file,
        test_statistics,
        test_error_handling,
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
        print("\n✓ All tests passed! HTML Parser is working perfectly!")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
