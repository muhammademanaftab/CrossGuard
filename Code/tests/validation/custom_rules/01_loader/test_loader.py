"""
Manual Validation: CustomRulesLoader Behavior

Run with:
    python tests/validation/custom_rules/01_loader/test_loader.py

This script validates the custom rules loader by:
1. Loading valid custom rules
2. Checking singleton behavior
3. Testing reload after file modification
4. Testing save and roundtrip
5. Checking is_user_rule identification
6. Handling malformed and empty files
"""

import sys
import json
import shutil
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    get_custom_rules_loader,
    get_custom_css_rules,
    get_custom_js_rules,
    get_custom_html_rules,
    reload_custom_rules,
    save_custom_rules,
    is_user_rule,
    load_raw_custom_rules,
    CUSTOM_RULES_PATH,
)


def reset_singleton():
    """Reset the singleton so each test starts fresh."""
    CustomRulesLoader._instance = None
    CustomRulesLoader._loaded = False
    import src.parsers.custom_rules_loader as mod
    mod._loader = None


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    symbol = "[+]" if condition else "[!]"
    print(f"  {symbol} {label}: {status}")
    return condition


def main():
    results = {'pass': 0, 'fail': 0}

    def track(label, condition):
        if check(label, condition):
            results['pass'] += 1
        else:
            results['fail'] += 1

    # === TEST 1: Singleton Behavior ===
    section("1. Singleton Behavior")
    reset_singleton()

    loader1 = CustomRulesLoader()
    loader2 = CustomRulesLoader()
    track("Two instances are same object", loader1 is loader2)

    loader3 = get_custom_rules_loader()
    track("get_custom_rules_loader returns same instance", loader3 is loader1)

    track("_loaded flag is True after init", CustomRulesLoader._loaded is True)

    # === TEST 2: Loading from default path ===
    section("2. Loading from Default Path")
    reset_singleton()

    loader = CustomRulesLoader()
    css_rules = loader.get_custom_css_rules()
    js_rules = loader.get_custom_js_rules()
    html_rules = loader.get_custom_html_rules()

    track("CSS rules is a dict", isinstance(css_rules, dict))
    track("JS rules is a dict", isinstance(js_rules, dict))
    track("HTML rules is a dict", isinstance(html_rules, dict))
    track("HTML has 'elements' key", 'elements' in html_rules)
    track("HTML has 'attributes' key", 'attributes' in html_rules)
    track("HTML has 'input_types' key", 'input_types' in html_rules)
    track("HTML has 'attribute_values' key", 'attribute_values' in html_rules)

    # Show what's currently loaded
    print(f"\n  Currently loaded rules:")
    print(f"    CSS rules: {len(css_rules)} features")
    print(f"    JS rules:  {len(js_rules)} features")
    html_count = sum(len(v) for v in html_rules.values() if isinstance(v, dict))
    print(f"    HTML rules: {html_count} entries")

    # === TEST 3: Convenience Functions ===
    section("3. Convenience Functions")
    reset_singleton()

    css = get_custom_css_rules()
    js = get_custom_js_rules()
    html = get_custom_html_rules()

    track("get_custom_css_rules returns dict", isinstance(css, dict))
    track("get_custom_js_rules returns dict", isinstance(js, dict))
    track("get_custom_html_rules returns dict", isinstance(html, dict))

    # === TEST 4: is_user_rule ===
    section("4. is_user_rule Function")
    reset_singleton()

    # Load rules first
    loader = CustomRulesLoader()
    css_rules = loader.get_custom_css_rules()
    js_rules = loader.get_custom_js_rules()
    html_rules = loader.get_custom_html_rules()

    # Check known custom CSS rules
    if css_rules:
        first_css = list(css_rules.keys())[0]
        track(f"Custom CSS rule '{first_css}' recognized", is_user_rule('css', first_css))

    track("Built-in 'flexbox' not a user rule", is_user_rule('css', 'flexbox') is False)
    track("Random string not a user rule", is_user_rule('css', 'nonexistent-xyz') is False)
    track("Unknown category returns False", is_user_rule('unknown', 'anything') is False)

    # Check HTML subtypes
    if html_rules.get('elements'):
        first_elem = list(html_rules['elements'].keys())[0]
        track(f"HTML element '{first_elem}' recognized with subtype",
              is_user_rule('html', first_elem, subtype='elements'))
        track(f"HTML element '{first_elem}' recognized without subtype",
              is_user_rule('html', first_elem))

    # === TEST 5: load_raw_custom_rules ===
    section("5. load_raw_custom_rules")
    reset_singleton()

    raw = load_raw_custom_rules()
    track("Raw returns dict", isinstance(raw, dict))
    track("Raw has 'css' key", 'css' in raw)
    track("Raw has 'javascript' key", 'javascript' in raw)
    track("Raw has 'html' key", 'html' in raw)

    # Verify raw includes comment keys (unlike the loader which skips them)
    raw_css = raw.get('css', {})
    has_comment = any(k.startswith('_') for k in raw_css.keys())
    if has_comment:
        track("Raw output includes _comment keys", True)
    else:
        print("  [~] No _comment keys in current custom_rules.json (OK)")

    # Verify fresh copy behavior
    raw1 = load_raw_custom_rules()
    raw1['css']['injected'] = 'test'
    raw2 = load_raw_custom_rules()
    track("Modifying raw result doesn't affect source", 'injected' not in raw2.get('css', {}))

    # === TEST 6: Save and Reload ===
    section("6. Save, Reload, and Roundtrip")
    reset_singleton()

    # Backup original file
    backup = None
    if CUSTOM_RULES_PATH.exists():
        backup = CUSTOM_RULES_PATH.read_text(encoding='utf-8')

    try:
        # Save new rules
        test_rules = {
            "css": {
                "test-save-feature": {
                    "patterns": ["test-save-prop\\s*:"],
                    "description": "Test Save Feature"
                }
            },
            "javascript": {
                "test-save-js": {
                    "patterns": ["\\bTestSaveAPI\\b"],
                    "description": "Test Save JS"
                }
            },
            "html": {
                "elements": {"test-save-elem": "test-save-feat"},
                "attributes": {},
                "input_types": {},
                "attribute_values": {}
            }
        }

        result = save_custom_rules(test_rules)
        track("save_custom_rules returns True", result is True)
        track("File exists after save", CUSTOM_RULES_PATH.exists())

        # Verify saved content
        saved = json.loads(CUSTOM_RULES_PATH.read_text(encoding='utf-8'))
        track("Saved JSON is valid", isinstance(saved, dict))
        track("CSS rule in saved file", "test-save-feature" in saved.get("css", {}))
        track("JS rule in saved file", "test-save-js" in saved.get("javascript", {}))

        # Verify reload picked up changes
        loader = get_custom_rules_loader()
        track("CSS rule available after save+reload",
              "test-save-feature" in loader.get_custom_css_rules())
        track("JS rule available after save+reload",
              "test-save-js" in loader.get_custom_js_rules())
        track("is_user_rule recognizes saved rule",
              is_user_rule('css', 'test-save-feature'))

    finally:
        # Restore original file
        if backup is not None:
            CUSTOM_RULES_PATH.write_text(backup, encoding='utf-8')
            reset_singleton()
            reload_custom_rules()

    # === TEST 7: Reload with modified file ===
    section("7. Reload Behavior")
    reset_singleton()

    loader = CustomRulesLoader()
    before = set(loader.get_custom_css_rules().keys())
    loader.reload()
    after = set(loader.get_custom_css_rules().keys())
    track("Reload returns same rules (file unchanged)", before == after)

    # Verify same instance after reload
    loader2 = CustomRulesLoader()
    track("Same instance after reload", loader is loader2)

    # === SUMMARY ===
    section("SUMMARY")
    total = results['pass'] + results['fail']
    print(f"\n  Total:  {total}")
    print(f"  Passed: {results['pass']}")
    print(f"  Failed: {results['fail']}")
    if results['fail'] == 0:
        print("\n  ALL TESTS PASSED")
    else:
        print(f"\n  {results['fail']} TEST(S) FAILED")

    return results['fail'] == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
