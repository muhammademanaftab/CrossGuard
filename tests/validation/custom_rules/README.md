# Custom Rules Manual Validation Tests

This directory contains comprehensive manual test files to validate the Custom Rules system in Cross Guard. Tests cover the `CustomRulesLoader` singleton, CSS/JS/HTML custom rule parsing and detection, cross-parser integration, edge cases, and real-world scenarios.

## Directory Structure

```
custom_rules/
├── 01_loader/                         # Loader unit validation
│   ├── test_loader.py                 # Runnable loader validation script
│   ├── custom_rules_valid.json        # Valid rules file for testing
│   ├── custom_rules_malformed.json    # Malformed rules (partial invalid entries)
│   ├── custom_rules_empty.json        # Empty rules (all sections empty)
│   └── custom_rules_broken.txt        # Invalid JSON syntax
│
├── 02_css_rules/                      # CSS custom rule detection
│   ├── 01_basic_properties.css        # Basic custom CSS property detection
│   ├── 02_multiple_patterns.css       # Rules with multiple regex patterns
│   ├── 03_no_false_positives.css      # Verify no false positives
│   └── 04_existing_rules.css          # Tests actual custom_rules.json entries
│
├── 03_js_rules/                       # JS custom rule detection
│   ├── 01_custom_api_detection.js     # Custom JS API detection
│   ├── 02_word_boundary_patterns.js   # \b word boundary regex testing
│   ├── 03_no_false_positives.js       # Verify no false positives
│   └── 04_comments_strings.js         # Custom rules in comments/strings
│
├── 04_html_rules/                     # HTML custom rule detection
│   ├── 01_custom_elements.html        # Custom element rules
│   ├── 02_custom_attributes.html      # Custom attribute rules
│   ├── 03_custom_input_types.html     # Custom input type rules
│   ├── 04_custom_attribute_values.html # Custom attribute value rules
│   └── 05_existing_rules.html         # Tests actual custom_rules.json entries
│
├── 05_cross_parser/                   # Multi-file integration
│   ├── 01_mixed_file_project.html     # HTML page with custom elements
│   ├── 02_paired_css.css              # CSS companion with custom properties
│   └── 03_paired_js.js               # JS companion (built-in features)
│
├── 06_edge_cases/                     # Edge cases and boundary tests
│   ├── 01_unicode_patterns.json       # Unicode in regex patterns
│   ├── 02_special_regex.json          # Complex regex (alternation, lookahead)
│   ├── 03_colon_in_attr_values.json   # Colon parsing in attribute values
│   ├── 04_duplicate_ids.json          # Same feature ID across CSS and JS
│   ├── 05_edge_test.css               # CSS edge cases (comments, whitespace)
│   └── 06_edge_test.html              # HTML edge cases (comments, text, attrs)
│
├── 07_real_world/                     # Real-world code patterns
│   ├── 01_design_system.css           # Design system stylesheet
│   ├── 02_web_component.html          # Web component page
│   └── 03_spa_app.js                  # Single page application
│
├── comprehensive_test.py             # End-to-end validation script
├── CHECKLIST.md                       # Manual testing checklist
└── README.md                          # This file
```

## What Custom Rules Are Currently Defined

The production `src/parsers/custom_rules.json` contains:

| Section | Rule ID | Pattern | Description |
|---------|---------|---------|-------------|
| CSS | `special-animation-custom` | `special-animation` | Special Animation Property |
| CSS | `my-custom-property` | `my-custom-property` | My Custom Property |
| HTML | `my-component` (element) | N/A | Maps to `custom-elementsv1` |

The JavaScript section is currently empty.

## Running Tests

### Comprehensive Validation Script (Recommended)

Runs all parsers on the test files and validates detection:

```bash
.venv/bin/python tests/validation/custom_rules/comprehensive_test.py
```

### Loader Validation Script

Tests the CustomRulesLoader singleton, save, reload, and is_user_rule:

```bash
.venv/bin/python tests/validation/custom_rules/01_loader/test_loader.py
```

### GUI Testing

1. Run the GUI: `python run_gui.py`
2. Drag and drop test files from this directory
3. Check detected features against the expected list in each file header
4. Verify browser support matches Can I Use

### CLI Testing (Individual Files)

```bash
# Test a CSS file
.venv/bin/python3 << 'EOF'
import sys; sys.path.insert(0, '.')
from src.parsers.css_parser import CSSParser
parser = CSSParser()
content = open('tests/validation/custom_rules/02_css_rules/04_existing_rules.css').read()
features = parser.parse_string(content)
print(f"Detected {len(features)} features:")
for f in sorted(features):
    print(f"  - {f}")
EOF

# Test a JS file
.venv/bin/python3 << 'EOF'
import sys; sys.path.insert(0, '.')
from src.parsers.js_parser import JavaScriptParser
parser = JavaScriptParser()
content = open('tests/validation/custom_rules/07_real_world/03_spa_app.js').read()
features = parser.parse_string(content)
print(f"Detected {len(features)} features:")
for f in sorted(features):
    print(f"  - {f}")
EOF

# Test an HTML file
.venv/bin/python3 << 'EOF'
import sys; sys.path.insert(0, '.')
from src.parsers.html_parser import HTMLParser
parser = HTMLParser()
content = open('tests/validation/custom_rules/04_html_rules/05_existing_rules.html').read()
features = parser.parse_string(content)
print(f"Detected {len(features)} features:")
for f in sorted(features):
    print(f"  - {f}")
EOF
```

### Automated Test Suite

```bash
# Custom rules loader unit tests
.venv/bin/pytest tests/parsers/custom_rules/ -v

# CSS parser custom rules tests
.venv/bin/pytest tests/parsers/css/custom_rules/ -v

# JS parser custom rules tests
.venv/bin/pytest tests/parsers/js/custom_rules/ -v

# HTML extended custom rules tests
.venv/bin/pytest tests/parsers/html/integration/test_custom_rules_extended.py -v

# All custom rules tests
.venv/bin/pytest tests/parsers/custom_rules/ tests/parsers/css/custom_rules/ tests/parsers/js/custom_rules/ tests/parsers/html/integration/test_custom_rules_extended.py -v
```

## Test Categories

### 1. Loader Tests (`01_loader/`)

| Test | Purpose |
|------|---------|
| Singleton behavior | Same instance returned on multiple calls |
| File loading | Valid, empty, malformed, missing JSON files |
| Section loading | CSS, JS, HTML rules extracted correctly |
| Save & reload | Round-trip save, reload picks up new data |
| `is_user_rule` | Distinguishes custom from built-in rules |
| `load_raw_custom_rules` | Returns full JSON including comments |

### 2. CSS Parser Tests (`02_css_rules/`)

| File | Purpose | Expected Custom Features |
|------|---------|------------------------|
| 01_basic_properties.css | Basic property detection | Requires adding test rules |
| 02_multiple_patterns.css | Multiple patterns per rule | Requires adding test rules |
| 03_no_false_positives.css | No false triggering | NONE |
| 04_existing_rules.css | Production rules | `special-animation-custom`, `my-custom-property` |

### 3. JS Parser Tests (`03_js_rules/`)

| File | Purpose | Expected Custom Features |
|------|---------|------------------------|
| 01_custom_api_detection.js | API pattern detection | Requires adding test rules |
| 02_word_boundary_patterns.js | `\b` word boundary matching | Requires adding test rules |
| 03_no_false_positives.js | No false triggering | NONE |
| 04_comments_strings.js | Patterns in comments/strings | NONE |

### 4. HTML Parser Tests (`04_html_rules/`)

| File | Purpose | Expected Custom Features |
|------|---------|------------------------|
| 01_custom_elements.html | Element rule detection | Requires adding test rules |
| 02_custom_attributes.html | Attribute rule detection | Requires adding test rules |
| 03_custom_input_types.html | Input type rules | Built-in input types |
| 04_custom_attribute_values.html | Attribute value rules | Requires adding test rules |
| 05_existing_rules.html | Production rules | `custom-elementsv1` |

### 5. Cross-Parser Tests (`05_cross_parser/`)

Tests multi-file analysis using HTML + CSS + JS files together.

### 6. Edge Cases (`06_edge_cases/`)

| File | Purpose |
|------|---------|
| 01_unicode_patterns.json | Unicode characters in regex patterns |
| 02_special_regex.json | Alternation, lookahead, character classes |
| 03_colon_in_attr_values.json | Colon-separated attribute value keys |
| 04_duplicate_ids.json | Same feature ID in CSS and JS sections |
| 05_edge_test.css | Comments, whitespace, multiple occurrences |
| 06_edge_test.html | Comments, text content, attribute values |

### 7. Real-World Tests (`07_real_world/`)

| File | Simulates | Min Features |
|------|-----------|-------------|
| 01_design_system.css | Design system with custom properties | 10+ |
| 02_web_component.html | Web component page | 12+ |
| 03_spa_app.js | Single page application | 15+ |

## How Custom Rules Work

### CSS & JS Rules

Custom CSS and JS rules use regex patterns:

```json
{
  "css": {
    "feature-id": {
      "patterns": ["regex-pattern-1", "regex-pattern-2"],
      "description": "Human readable description"
    }
  }
}
```

Patterns are merged with built-in rules at parser initialization:
- CSS: `{**ALL_CSS_FEATURES, **get_custom_css_rules()}`
- JS: `{**ALL_JS_FEATURES, **get_custom_js_rules()}`

### HTML Rules

HTML rules use element/attribute/value mappings:

```json
{
  "html": {
    "elements": { "element-name": "caniuse-feature-id" },
    "attributes": { "attr-name": "caniuse-feature-id" },
    "input_types": { "type-value": "caniuse-feature-id" },
    "attribute_values": { "attr:value": "caniuse-feature-id" }
  }
}
```

The `attribute_values` keys use `attr:value` format, which the HTML parser converts to `(attr, value)` tuples for lookup.

## Adding New Test Rules

To test files in `01_basic_properties.css`, `01_custom_api_detection.js`, etc., add the rules listed in each file's header comment to `src/parsers/custom_rules.json`, then run the tests. Each file documents its prerequisites clearly.

## Notes

- Files marked "Requires adding test rules" need corresponding entries in `custom_rules.json`
- Files testing "existing rules" work with the current production `custom_rules.json`
- Comments and string content should never trigger custom rule detection
- The HTML parser uses BeautifulSoup, so tag-based detection is DOM-aware
- Custom rules are merged with built-in rules via dict unpacking, so custom rules take precedence for duplicate keys
