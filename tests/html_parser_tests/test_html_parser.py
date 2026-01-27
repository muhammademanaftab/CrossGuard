"""Comprehensive test suite for HTML parser."""

import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parsers.html_parser import HTMLParser, parse_html_file, parse_html_string


def test_basic_elements():
    """Test detection of basic HTML5 elements."""
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

    expected = {'dialog', 'details', 'template'}
    found_expected = expected.intersection(features)

    assert found_expected == expected, f"Missing features: {expected - found_expected}"


def test_input_types():
    """Test detection of modern input types."""
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

    expected_features = ['input-datetime', 'input-color', 'input-range', 'input-email', 'input-tel']
    found_count = sum(1 for f in expected_features if f in features)

    assert found_count >= 3, f"Expected at least 3 input types, found {found_count}"


def test_attributes():
    """Test detection of modern attributes."""
    html = """
    <img src="image.jpg" loading="lazy" decoding="async" alt="Test">
    <input type="text" placeholder="Enter text" required>
    <div contenteditable="true">Editable content</div>
    <a href="file.pdf" download>Download</a>
    """

    parser = HTMLParser()
    features = parser.parse_string(html)

    expected_attrs = ['loading-lazy-attr', 'img-decoding-async', 'input-placeholder',
                     'form-validation', 'contenteditable', 'download']
    found_attrs = [attr for attr in expected_attrs if attr in features]

    assert len(found_attrs) >= 4, f"Expected at least 4 attributes, found {found_attrs}"


def test_picture_element():
    """Test detection of picture element with sources."""
    html = """
    <picture>
        <source srcset="image.webp" type="image/webp">
        <source srcset="image.jpg" type="image/jpeg">
        <img src="fallback.jpg" alt="Image">
    </picture>
    """

    parser = HTMLParser()
    features = parser.parse_string(html)

    assert 'picture' in features, "Picture element not detected"


def test_script_attributes():
    """Test detection of script async/defer and modules."""
    html = """
    <script src="script1.js" async></script>
    <script src="script2.js" defer></script>
    <script type="module" src="module.js"></script>
    """

    parser = HTMLParser()
    features = parser.parse_string(html)

    expected = ['script-async', 'script-defer', 'es6-module']
    found = [f for f in expected if f in features]

    assert len(found) >= 2, f"Expected at least 2 script features, found {found}"


def test_link_rel():
    """Test detection of link rel attributes."""
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

    link_features = [f for f in features if 'link-rel' in f]

    assert len(link_features) >= 2, f"Expected at least 2 link rel features, found {link_features}"


def test_data_attributes():
    """Test detection of data-* attributes."""
    html = """
    <div data-id="123" data-name="test" data-value="456">
        Content
    </div>
    """

    parser = HTMLParser()
    features = parser.parse_string(html)

    assert 'dataset' in features, "Data attributes not detected"


def test_sample_file():
    """Test parsing the actual sample.html file."""
    sample_path = Path(__file__).parent.parent.parent / 'examples' / 'sample.html'

    if not sample_path.exists():
        pytest.skip(f"Sample file not found: {sample_path}")

    parser = HTMLParser()
    features = parser.parse_file(str(sample_path))

    assert len(features) > 0, "No features found in sample file"

    # Get detailed report
    report = parser.get_detailed_report()
    assert 'elements_found' in report, "Report missing elements_found"


def test_statistics():
    """Test statistics generation."""
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

    assert stats['total_features'] > 0, "No features in statistics"
    assert 'total_elements_detected' in stats, "Statistics missing total_elements_detected"
    assert 'total_attributes_detected' in stats, "Statistics missing total_attributes_detected"


def test_error_handling():
    """Test error handling for invalid inputs."""
    parser = HTMLParser()

    # Test 1: Non-existent file
    with pytest.raises(FileNotFoundError):
        parser.parse_file('nonexistent.html')

    # Test 2: Empty HTML
    features = parser.parse_string('')
    assert isinstance(features, set), "Empty HTML should return a set"

    # Test 3: Malformed HTML (BeautifulSoup handles this gracefully)
    features = parser.parse_string('<div><p>Unclosed tags')
    assert isinstance(features, set), "Malformed HTML should return a set"

    # Test 4: Validate HTML
    is_valid = parser.validate_html('<html><body>Valid</body></html>')
    assert isinstance(is_valid, bool), "validate_html should return bool"


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
            test()
            passed += 1
            print(f"✓ {test.__name__}")
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
