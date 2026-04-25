"""
Comprehensive Custom Rules Validation Script

Run with:
    .venv/bin/python tests/validation/custom_rules/comprehensive_test.py

This script validates the custom rules system end-to-end by:
1. Loading the current custom_rules.json
2. Running CSS parser on test CSS files with custom rules
3. Running JS parser on test JS files with custom rules
4. Running HTML parser on test HTML files with custom rules
5. Verifying detection accuracy for all file types
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.parsers.css_parser import CSSParser
from src.parsers.js_parser import JavaScriptParser
from src.parsers.html_parser import HTMLParser
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    get_custom_css_rules,
    get_custom_js_rules,
    get_custom_html_rules,
    load_raw_custom_rules,
)

VALIDATION_DIR = Path(__file__).parent


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def subsection(title):
    print(f"\n  --- {title} ---")


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    symbol = "[+]" if condition else "[!]"
    print(f"    {symbol} {label}: {status}")
    return condition


def parse_css_file(filepath):
    """Parse a CSS file and return features and report."""
    parser = CSSParser()
    content = filepath.read_text(encoding='utf-8')
    features = parser.parse_string(content)
    report = parser.get_detailed_report()
    return features, report


def parse_js_file(filepath):
    """Parse a JS file and return features and report."""
    parser = JavaScriptParser()
    content = filepath.read_text(encoding='utf-8')
    features = parser.parse_string(content)
    report = parser.get_detailed_report()
    return features, report


def parse_html_file(filepath):
    """Parse an HTML file and return features and report."""
    parser = HTMLParser()
    content = filepath.read_text(encoding='utf-8')
    features = parser.parse_string(content)
    report = parser.get_detailed_report()
    return features, report


def main():
    results = {'pass': 0, 'fail': 0}

    def track(label, condition):
        if check(label, condition):
            results['pass'] += 1
        else:
            results['fail'] += 1

    # ========================================
    section("1. CUSTOM RULES LOADER STATE")
    # ========================================

    raw = load_raw_custom_rules()
    css_rules = get_custom_css_rules()
    js_rules = get_custom_js_rules()
    html_rules = get_custom_html_rules()

    print(f"\n    Current custom_rules.json:")
    print(f"      CSS rules:  {len(css_rules)} features")
    print(f"      JS rules:   {len(js_rules)} features")
    html_count = sum(len(v) for v in html_rules.values() if isinstance(v, dict))
    print(f"      HTML rules:  {html_count} entries")

    if css_rules:
        print(f"\n    CSS feature IDs: {', '.join(sorted(css_rules.keys()))}")
    if js_rules:
        print(f"    JS feature IDs:  {', '.join(sorted(js_rules.keys()))}")
    if html_rules.get('elements'):
        print(f"    HTML elements:   {', '.join(sorted(html_rules['elements'].keys()))}")

    # ========================================
    section("2. CSS PARSER WITH EXISTING CUSTOM RULES")
    # ========================================

    css_test = VALIDATION_DIR / "02_css_rules" / "04_existing_rules.css"
    if css_test.exists():
        features, report = parse_css_file(css_test)

        subsection(f"File: {css_test.name} ({len(features)} features detected)")

        # Check for existing custom rules from custom_rules.json
        if 'special-animation-custom' in css_rules:
            track("special-animation-custom detected", 'special-animation-custom' in features)
        if 'my-custom-property' in css_rules:
            track("my-custom-property detected", 'my-custom-property' in features)

        # Built-in should still work
        track("Built-in flexbox detected", 'flexbox' in features)
        track("Built-in css-grid detected", 'css-grid' in features)

        print(f"\n    All detected: {sorted(features)}")
    else:
        print(f"    [~] Skipping: {css_test} not found")

    # No-false-positives test
    css_nofp = VALIDATION_DIR / "02_css_rules" / "03_no_false_positives.css"
    if css_nofp.exists():
        features, _ = parse_css_file(css_nofp)
        subsection(f"File: {css_nofp.name} (false positive check)")

        for rule_id in css_rules:
            track(f"Custom rule '{rule_id}' NOT falsely triggered", rule_id not in features)

        track("Built-in flexbox detected", 'flexbox' in features)

    # ========================================
    section("3. JS PARSER WITH CUSTOM RULES")
    # ========================================

    js_nofp = VALIDATION_DIR / "03_js_rules" / "03_no_false_positives.js"
    if js_nofp.exists():
        features, _ = parse_js_file(js_nofp)
        subsection(f"File: {js_nofp.name} (false positive check)")

        for rule_id in js_rules:
            track(f"Custom JS rule '{rule_id}' NOT falsely triggered", rule_id not in features)

        track("Built-in const detected", 'const' in features)
        track("Built-in let detected", 'let' in features)
        track("Built-in arrow-functions detected", 'arrow-functions' in features)

        print(f"\n    All detected: {sorted(features)}")

    js_comments = VALIDATION_DIR / "03_js_rules" / "04_comments_strings.js"
    if js_comments.exists():
        features, _ = parse_js_file(js_comments)
        subsection(f"File: {js_comments.name} (comments/strings check)")

        for rule_id in js_rules:
            track(f"Custom JS rule '{rule_id}' NOT detected in comments", rule_id not in features)

        track("Built-in const detected", 'const' in features)
        track("Built-in arrow-functions detected", 'arrow-functions' in features)

    # ========================================
    section("4. HTML PARSER WITH EXISTING CUSTOM RULES")
    # ========================================

    html_test = VALIDATION_DIR / "04_html_rules" / "05_existing_rules.html"
    if html_test.exists():
        features, report = parse_html_file(html_test)
        subsection(f"File: {html_test.name} ({len(features)} features detected)")

        # Check custom element from custom_rules.json
        if 'my-component' in html_rules.get('elements', {}):
            track("custom-elementsv1 detected (my-component)", 'custom-elementsv1' in features)

        # Built-in should still work
        track("Built-in video detected", 'video' in features)
        track("Built-in html5semantic detected", 'html5semantic' in features)

        print(f"\n    All detected: {sorted(features)}")

    # Edge case HTML
    html_edge = VALIDATION_DIR / "06_edge_cases" / "06_edge_test.html"
    if html_edge.exists():
        features, _ = parse_html_file(html_edge)
        subsection(f"File: {html_edge.name} (edge cases)")

        track("custom-elementsv1 detected (actual elements)", 'custom-elementsv1' in features)
        track("Built-in video detected", 'video' in features)
        track("Built-in html5semantic detected", 'html5semantic' in features)

    # ========================================
    section("5. CSS EDGE CASES")
    # ========================================

    css_edge = VALIDATION_DIR / "06_edge_cases" / "05_edge_test.css"
    if css_edge.exists():
        features, report = parse_css_file(css_edge)
        subsection(f"File: {css_edge.name} ({len(features)} features detected)")

        if 'special-animation-custom' in css_rules:
            track("Custom rule detected despite unusual whitespace",
                  'special-animation-custom' in features)
        if 'my-custom-property' in css_rules:
            track("Custom rule detected in long declaration block",
                  'my-custom-property' in features)

        print(f"\n    All detected: {sorted(features)}")

    # ========================================
    section("6. REAL-WORLD FILES")
    # ========================================

    # Design system CSS
    rw_css = VALIDATION_DIR / "07_real_world" / "01_design_system.css"
    if rw_css.exists():
        features, _ = parse_css_file(rw_css)
        subsection(f"File: {rw_css.name} ({len(features)} features)")

        if 'special-animation-custom' in css_rules:
            track("Custom special-animation-custom in design system",
                  'special-animation-custom' in features)
        if 'my-custom-property' in css_rules:
            track("Custom my-custom-property in design system",
                  'my-custom-property' in features)
        track("Built-in flexbox in design system", 'flexbox' in features)
        track("Built-in css-grid in design system", 'css-grid' in features)
        track("Built-in css-variables in design system", 'css-variables' in features)

        print(f"    Total features: {len(features)}")

    # Web component page
    rw_html = VALIDATION_DIR / "07_real_world" / "02_web_component.html"
    if rw_html.exists():
        features, _ = parse_html_file(rw_html)
        subsection(f"File: {rw_html.name} ({len(features)} features)")

        track("custom-elementsv1 in web component page", 'custom-elementsv1' in features)
        track("video in web component page", 'video' in features)
        track("html5semantic in web component page", 'html5semantic' in features)
        track("At least 10 features detected", len(features) >= 10)

        print(f"    Total features: {len(features)}")
        print(f"    All detected: {sorted(features)}")

    # SPA JavaScript
    rw_js = VALIDATION_DIR / "07_real_world" / "03_spa_app.js"
    if rw_js.exists():
        features, _ = parse_js_file(rw_js)
        subsection(f"File: {rw_js.name} ({len(features)} features)")

        # No custom JS rules in current config, so none should be detected
        for rule_id in js_rules:
            track(f"Custom '{rule_id}' not falsely detected in SPA", rule_id not in features)

        track("Built-in const in SPA", 'const' in features)
        track("Built-in fetch in SPA", 'fetch' in features)
        track("Built-in es6-class in SPA", 'es6-class' in features)
        track("Built-in use-strict in SPA", 'use-strict' in features)
        track("At least 15 features detected in SPA", len(features) >= 15)

        print(f"    Total features: {len(features)}")

    # ========================================
    section("7. CROSS-PARSER INTEGRATION")
    # ========================================

    cross_files = [
        (VALIDATION_DIR / "05_cross_parser" / "01_mixed_file_project.html", parse_html_file),
        (VALIDATION_DIR / "05_cross_parser" / "02_paired_css.css", parse_css_file),
        (VALIDATION_DIR / "05_cross_parser" / "03_paired_js.js", parse_js_file),
    ]

    total_cross_features = set()
    for filepath, parser_fn in cross_files:
        if filepath.exists():
            features, _ = parser_fn(filepath)
            total_cross_features.update(features)
            subsection(f"File: {filepath.name} ({len(features)} features)")
            print(f"    Detected: {sorted(features)}")

    if total_cross_features:
        print(f"\n    Combined features across all 3 files: {len(total_cross_features)}")
        track("Cross-parser: At least 20 combined features", len(total_cross_features) >= 20)

    # ========================================
    section("SUMMARY")
    # ========================================

    total = results['pass'] + results['fail']
    print(f"\n    Total checks:  {total}")
    print(f"    Passed:        {results['pass']}")
    print(f"    Failed:        {results['fail']}")

    if results['fail'] == 0:
        print("\n    ALL CHECKS PASSED")
    else:
        print(f"\n    {results['fail']} CHECK(S) FAILED")

    return results['fail'] == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
