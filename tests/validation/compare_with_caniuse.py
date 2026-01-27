#!/usr/bin/env python3
"""
Validation Script: Compare Cross Guard results with Can I Use website.

This script helps validate that Cross Guard produces the same results
as the Can I Use website (https://caniuse.com/).

Usage:
    python tests/validation/compare_with_caniuse.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.parsers.html_parser import HTMLParser
from src.analyzer.database import get_database
from src.analyzer.compatibility import CompatibilityAnalyzer


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def print_section(text):
    """Print formatted section header."""
    print(f"\n--- {text} ---")


def compare_feature(feature_id: str, browsers: dict):
    """Compare a single feature across browsers and show Can I Use URLs."""
    db = get_database()

    print_section(f"Feature: {feature_id}")

    # Get feature info
    info = db.get_feature_info(feature_id)
    if info:
        print(f"  Title: {info['title']}")
        print(f"  Description: {info['description'][:100]}...")
    else:
        print(f"  WARNING: Feature '{feature_id}' not found in database!")
        return

    # Can I Use URL for this feature
    caniuse_url = f"https://caniuse.com/{feature_id}"
    print(f"  Can I Use URL: {caniuse_url}")

    # Check support in each browser
    print(f"\n  Browser Support (from Cross Guard database):")
    for browser, version in browsers.items():
        status = db.check_support(feature_id, browser, version)
        status_text = {
            'y': 'Supported',
            'a': 'Partial support',
            'n': 'Not supported',
            'p': 'Polyfill available',
            'u': 'Unknown',
            'x': 'Requires prefix',
            'd': 'Disabled by default'
        }.get(status, 'Unknown')
        print(f"    {browser} {version}: {status} ({status_text})")

    print(f"\n  VERIFY: Open {caniuse_url} and compare the support data above")


def test_sample_html():
    """Test with sample HTML and show comparison data."""

    print_header("CROSS GUARD vs CAN I USE - VALIDATION TEST")

    # Define target browsers (latest versions as of 2024)
    target_browsers = {
        'chrome': '120',
        'firefox': '121',
        'safari': '17',
        'edge': '120',
        'opera': '106',
        'ie': '11',  # Internet Explorer for testing unsupported features
    }

    print(f"\nTarget Browsers:")
    for browser, version in target_browsers.items():
        print(f"  - {browser} {version}")

    # Sample HTML with various features
    sample_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="preload" href="style.css" as="style">
        <script type="module" src="app.js"></script>
    </head>
    <body>
        <main>
            <dialog id="modal">
                <p>Modal content</p>
            </dialog>

            <video src="video.mp4" controls>
                <track src="captions.vtt" kind="captions">
            </video>

            <details>
                <summary>Click to expand</summary>
                <p>Hidden content</p>
            </details>

            <form>
                <input type="date" required placeholder="Select date">
                <input type="color" value="#ff0000">
                <input type="range" min="0" max="100">
                <datalist id="options">
                    <option value="Option 1">
                </datalist>
            </form>

            <canvas id="myCanvas"></canvas>

            <my-custom-element>Custom Element</my-custom-element>
        </main>
    </body>
    </html>
    """

    # Parse HTML
    parser = HTMLParser()
    features = parser.parse_string(sample_html)

    print_header("DETECTED FEATURES")
    print(f"\nTotal features detected: {len(features)}")
    print(f"Features: {sorted(features)}")

    # Analyze compatibility
    analyzer = CompatibilityAnalyzer()
    report = analyzer.analyze(features, target_browsers)

    print_header("COMPATIBILITY ANALYSIS")
    print(f"\nOverall Score: {report.overall_score:.1f}%")
    print(f"Features Analyzed: {report.features_analyzed}")

    print("\nBrowser Scores:")
    for browser, score in report.browser_scores.items():
        print(f"  {browser}: {score.score:.1f}% ({score.supported_count} supported, "
              f"{score.partial_count} partial, {score.unsupported_count} unsupported)")

    print_header("FEATURE-BY-FEATURE COMPARISON")
    print("\nCompare each feature below with Can I Use website:")

    # Compare key features
    key_features = [
        'dialog',
        'video',
        'details',
        'input-datetime',
        'input-color',
        'input-range',
        'datalist',
        'canvas',
        'custom-elementsv1',
        'link-rel-preload',
        'es6-module',
        'webvtt',
        'html5semantic',
    ]

    for feature_id in key_features:
        if feature_id in features:
            compare_feature(feature_id, target_browsers)

    print_header("VERIFICATION CHECKLIST")
    print("""
For your thesis validation, check each feature on caniuse.com:

1. Go to the Can I Use URL shown for each feature
2. Look at the browser support table
3. Find the browser version you're testing (e.g., Chrome 120)
4. Compare the color/status:
   - Green = Supported (y)
   - Yellow/Orange = Partial support (a)
   - Red = Not supported (n)
   - Gray = Unknown (u)

5. Document any discrepancies in your thesis

Common reasons for minor differences:
- Version number format (Can I Use may show ranges like "120-122")
- Recent data updates (your local database may be slightly older)
- Prefix handling (x status)
""")

    print_header("QUICK VERIFICATION LINKS")
    print("\nOpen these URLs in your browser to verify:")

    for feature_id in sorted(features):
        print(f"  https://caniuse.com/{feature_id}")


def test_specific_features():
    """Test specific features with detailed comparison."""

    print_header("DETAILED FEATURE TESTS")

    db = get_database()

    # Test features that are easy to verify
    test_cases = [
        # (feature_id, expected_chrome_120, expected_ie_11)
        ('dialog', 'y', 'n'),  # Dialog: supported in Chrome, not in IE
        ('video', 'y', 'y'),   # Video: widely supported
        ('canvas', 'y', 'y'),  # Canvas: widely supported
        ('details', 'y', 'n'), # Details: not in IE
        ('css-grid', 'y', 'n'), # CSS Grid: not in IE
        ('flexbox', 'y', 'a'),  # Flexbox: partial in IE
    ]

    print("\nExpected vs Actual Support Status:")
    print("-" * 60)

    all_passed = True
    for feature_id, expected_chrome, expected_ie in test_cases:
        chrome_status = db.check_support(feature_id, 'chrome', '120')
        ie_status = db.check_support(feature_id, 'ie', '11')

        chrome_match = chrome_status == expected_chrome
        ie_match = ie_status == expected_ie

        status_icon = "" if (chrome_match and ie_match) else ""

        print(f"\n{status_icon} {feature_id}:")
        print(f"   Chrome 120: expected={expected_chrome}, got={chrome_status} {'✓' if chrome_match else '✗'}")
        print(f"   IE 11:      expected={expected_ie}, got={ie_status} {'✓' if ie_match else '✗'}")

        if not (chrome_match and ie_match):
            all_passed = False
            print(f"   Verify at: https://caniuse.com/{feature_id}")

    print("\n" + "-" * 60)
    if all_passed:
        print(" ALL TESTS PASSED!")
    else:
        print(" Some tests need verification - check the URLs above")


def show_database_info():
    """Show database information."""
    print_header("DATABASE INFORMATION")

    db = get_database()
    stats = db.get_statistics()

    print(f"\nDatabase loaded: {stats['loaded']}")
    print(f"Total features: {stats['total_features']}")
    print(f"Total categories: {stats['total_categories']}")
    print(f"Index size: {stats['index_size']}")

    print("\nFeatures by category:")
    for cat, count in sorted(stats['categories'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {cat}: {count}")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("   CROSS GUARD VALIDATION SCRIPT")
    print("   Compare your software results with caniuse.com")
    print("=" * 70)

    show_database_info()
    test_sample_html()
    test_specific_features()

    print("\n" + "=" * 70)
    print("   VALIDATION COMPLETE")
    print("   Review the output above and compare with caniuse.com")
    print("=" * 70 + "\n")
