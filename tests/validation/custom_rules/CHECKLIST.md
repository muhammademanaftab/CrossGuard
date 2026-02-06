# Custom Rules Manual Validation Checklist

## Legend

- `[ ]` = Not tested
- `[x]` = Passed (feature detected correctly / behavior correct)
- `[!]` = Failed (see notes for discrepancy details)

---

## 01_loader/

### test_loader.py

**Purpose:** Validate CustomRulesLoader singleton, loading, saving, reloading, and is_user_rule

| Status | Test |
| ------ | ---- |
| [ ] | Singleton returns same instance |
| [ ] | get_custom_rules_loader returns same instance |
| [ ] | _loaded flag set after init |
| [ ] | CSS rules loaded as dict |
| [ ] | JS rules loaded as dict |
| [ ] | HTML rules has elements, attributes, input_types, attribute_values |
| [ ] | Convenience functions return dicts |
| [ ] | is_user_rule identifies custom CSS rules |
| [ ] | is_user_rule returns False for built-in rules |
| [ ] | is_user_rule returns False for unknown rules |
| [ ] | load_raw_custom_rules returns full JSON |
| [ ] | Raw output modifying doesn't affect source |
| [ ] | save_custom_rules writes file and reloads |
| [ ] | Roundtrip save/load preserves data |
| [ ] | Reload picks up file changes |

- [ ] All checks passed
- **Notes:** \_\_\_

**Run:** `.venv/bin/python tests/validation/custom_rules/01_loader/test_loader.py`

---

### custom_rules_valid.json

**Purpose:** Reference valid custom rules file

| Status | Test |
| ------ | ---- |
| [ ] | File parses as valid JSON |
| [ ] | Has css, javascript, html sections |
| [ ] | CSS rules have patterns and description |
| [ ] | JS rules have patterns and description |
| [ ] | HTML has elements, attributes, input_types, attribute_values |

- **Notes:** \_\_\_

---

### custom_rules_malformed.json

**Purpose:** Partially invalid entries that should be handled gracefully

| Status | Test |
| ------ | ---- |
| [ ] | File loads without crash |
| [ ] | Valid entries still loaded (valid-rule, also-valid) |
| [ ] | Missing patterns key skipped (missing-patterns) |
| [ ] | Non-dict value skipped (not-a-dict) |
| [ ] | Comment key skipped (_comment) |
| [ ] | Empty patterns list loaded (empty-patterns) |
| [ ] | Unknown section ignored (extra_unknown_section) |

- **Notes:** \_\_\_

---

### custom_rules_empty.json

**Purpose:** All-empty rules file

| Status | Test |
| ------ | ---- |
| [ ] | Loads without crash |
| [ ] | Returns empty CSS rules |
| [ ] | Returns empty JS rules |
| [ ] | Returns empty HTML sub-dicts |

- **Notes:** \_\_\_

---

### custom_rules_broken.txt

**Purpose:** Invalid JSON syntax

| Status | Test |
| ------ | ---- |
| [ ] | Loader does not crash |
| [ ] | Returns empty rules for all sections |
| [ ] | Error logged (check console output) |

- **Notes:** \_\_\_

---

## 02_css_rules/

### 04_existing_rules.css (Uses production custom_rules.json)

**Expected custom features:** `special-animation-custom`, `my-custom-property`
**Expected built-in features:** `flexbox`, `css-grid`

| Status | Feature | Type |
| ------ | ------- | ---- |
| [ ] | special-animation-custom | Custom |
| [ ] | my-custom-property | Custom |
| [ ] | flexbox | Built-in |
| [ ] | css-grid | Built-in |

- [ ] All 4 features detected
- [ ] Custom and built-in coexist correctly
- **Notes:** \_\_\_

---

### 03_no_false_positives.css

**Expected custom features:** NONE
**Expected built-in features:** `flexbox`, `css-transitions`

| Status | Test |
| ------ | ---- |
| [ ] | No custom rules triggered |
| [ ] | flexbox detected (built-in) |
| [ ] | css-transitions detected (built-in) |
| [ ] | linear-gradient does NOT trigger custom-gradient |
| [ ] | scroll-behavior does NOT trigger scroll-timeline |

- **Notes:** \_\_\_

---

### 01_basic_properties.css (Requires adding test rules)

**Prerequisites:** Add `test-custom-gradient`, `test-scroll-timeline`, `test-anchor-position` to CSS section

**Expected custom features:** `test-custom-gradient`, `test-scroll-timeline`, `test-anchor-position`
**Expected built-in features:** `flexbox`, `css-grid`

| Status | Feature | Type |
| ------ | ------- | ---- |
| [ ] | test-custom-gradient | Custom |
| [ ] | test-scroll-timeline | Custom |
| [ ] | test-anchor-position | Custom |
| [ ] | flexbox | Built-in |
| [ ] | css-grid | Built-in |

- [ ] All 5 features detected
- **Notes:** \_\_\_

---

### 02_multiple_patterns.css (Requires adding test rules)

**Prerequisites:** Add `test-container-queries`, `test-view-transitions` to CSS section

**Expected custom features:** `test-container-queries`, `test-view-transitions`

| Status | Feature | Patterns Tested |
| ------ | ------- | --------------- |
| [ ] | test-container-queries | @container, container-type, container-name |
| [ ] | test-view-transitions | view-transition-name, ::view-transition |

- [ ] All patterns in each rule trigger detection
- **Notes:** \_\_\_

---

## 03_js_rules/

### 03_no_false_positives.js

**Expected custom features:** NONE
**Expected built-in features:** `const`, `let`, `arrow-functions`

| Status | Test |
| ------ | ---- |
| [ ] | No custom JS rules triggered |
| [ ] | Variable name 'taskScheduler' does NOT trigger scheduler API |
| [ ] | String 'CompressionStream' does NOT trigger compression API |
| [ ] | const detected (built-in) |
| [ ] | let detected (built-in) |
| [ ] | arrow-functions detected (built-in) |

- **Notes:** \_\_\_

---

### 04_comments_strings.js

**Expected custom features:** NONE
**Expected built-in features:** `const`, `arrow-functions`, `template-literals`

| Status | Test |
| ------ | ---- |
| [ ] | Custom APIs in single-line comments NOT detected |
| [ ] | Custom APIs in multi-line comments NOT detected |
| [ ] | Custom APIs in JSDoc NOT detected |
| [ ] | Custom APIs in string literals NOT detected |
| [ ] | Custom APIs in template literals NOT detected |
| [ ] | const detected (actual code) |
| [ ] | arrow-functions detected (actual code) |

- **Notes:** \_\_\_

---

### 01_custom_api_detection.js (Requires adding test rules)

**Prerequisites:** Add `test-scheduler-api`, `test-compression-api`, `test-url-pattern` to JS section

**Expected custom features:** `test-scheduler-api`, `test-compression-api`, `test-url-pattern`

| Status | Feature | Can I Use URL |
| ------ | ------- | ------------- |
| [ ] | test-scheduler-api | https://caniuse.com/scheduler-postTask |
| [ ] | test-compression-api | https://caniuse.com/compressstream |
| [ ] | test-url-pattern | https://caniuse.com/urlpattern |

- [ ] All 3 custom features detected
- [ ] Built-in features (promises, fetch) also detected
- **Notes:** \_\_\_

---

### 02_word_boundary_patterns.js (Requires adding test rules)

**Prerequisites:** Add `test-eye-dropper`, `test-barcode-api` to JS section

| Status | Test |
| ------ | ---- |
| [ ] | `new EyeDropper()` triggers test-eye-dropper |
| [ ] | `myEyeDropperWrapper` does NOT trigger (substring) |
| [ ] | `new BarcodeDetector()` triggers test-barcode-api |
| [ ] | `fakeBarcodeDetectorName` does NOT trigger (substring) |

- **Notes:** \_\_\_

---

## 04_html_rules/

### 05_existing_rules.html (Uses production custom_rules.json)

**Expected custom features:** `custom-elementsv1`
**Expected built-in features:** `video`, `html5semantic`

| Status | Feature | Source |
| ------ | ------- | ------ |
| [ ] | custom-elementsv1 | my-component element |
| [ ] | video | Built-in video element |
| [ ] | html5semantic | Built-in main element |

- [ ] All 3 features detected
- [ ] Text mention of 'my-component' does NOT trigger detection
- **Notes:** \_\_\_

---

### 01_custom_elements.html (Requires adding test rules)

**Prerequisites:** Add `app-header`, `data-table`, `ui-modal` to HTML elements section

| Status | Test |
| ------ | ---- |
| [ ] | Nested custom element detected (data-table inside div/article/section) |
| [ ] | Self-closing custom element detected (ui-modal) |
| [ ] | Custom element with attributes detected (app-header with class, data-theme) |
| [ ] | Text content 'app-header' does NOT trigger detection |

- **Notes:** \_\_\_

---

### 02_custom_attributes.html (Requires adding test rules)

**Prerequisites:** Add `x-data`, `v-if`, `hx-get` to HTML attributes section

| Status | Feature | Source |
| ------ | ------- | ------ |
| [ ] | alpine-reactive | x-data attribute |
| [ ] | vue-directive | v-if attribute |
| [ ] | htmx-feature | hx-get attribute |
| [ ] | input-placeholder | Built-in placeholder |
| [ ] | form-validation | Built-in required |
| [ ] | contenteditable | Built-in contenteditable |

- **Notes:** \_\_\_

---

### 03_custom_input_types.html

**Expected features:** `input-datetime`, `input-email-tel-url`, `input-color`, `input-range`

| Status | Feature | Input Type |
| ------ | ------- | ---------- |
| [ ] | input-datetime | date, time, week, month |
| [ ] | input-email-tel-url | email |
| [ ] | input-color | color |
| [ ] | input-range | range |

- [ ] All 4 features detected
- **Notes:** \_\_\_

---

### 04_custom_attribute_values.html (Requires adding test rules)

**Prerequisites:** Add `fetchpriority:high`, `rel:modulepreload`, `loading:lazy` to attribute_values

| Status | Feature | Attribute Value |
| ------ | ------- | --------------- |
| [ ] | fetch-priority | fetchpriority="high" |
| [ ] | link-rel-modulepreload-custom | rel="modulepreload" |
| [ ] | loading-lazy-custom | loading="lazy" |
| [ ] | link-rel-preload | Built-in rel="preload" |
| [ ] | es6-module | Built-in type="module" |

- [ ] Case-insensitive matching works (loading="Lazy") |
- **Notes:** \_\_\_

---

## 05_cross_parser/

### Multi-file integration

**Purpose:** Upload all 3 files together to test cross-parser detection

| Status | Test |
| ------ | ---- |
| [ ] | HTML file: custom-elementsv1 detected (my-component) |
| [ ] | HTML file: Built-in features detected (video, html5semantic, dialog, etc.) |
| [ ] | CSS file: special-animation-custom detected |
| [ ] | CSS file: my-custom-property detected |
| [ ] | CSS file: Built-in features detected (flexbox, css-grid, css-animation) |
| [ ] | JS file: No custom rules falsely triggered |
| [ ] | JS file: Built-in features detected (const, fetch, promises, etc.) |
| [ ] | Combined: At least 20 unique features across all files |

- **Notes:** \_\_\_

---

## 06_edge_cases/

### 05_edge_test.css

**Purpose:** CSS detection edge cases with existing custom rules

| Status | Test |
| ------ | ---- |
| [ ] | Custom property in CSS comment NOT detected |
| [ ] | Custom property with extra whitespace IS detected |
| [ ] | Custom property in long declaration block IS detected |
| [ ] | Multiple occurrences of same custom property counted correctly |

- **Notes:** \_\_\_

---

### 06_edge_test.html

**Purpose:** HTML detection edge cases with existing custom rules

| Status | Test |
| ------ | ---- |
| [ ] | my-component in HTML comment NOT detected |
| [ ] | my-component in text content NOT detected |
| [ ] | my-component in attribute value NOT detected |
| [ ] | Actual my-component elements ARE detected |
| [ ] | Self-closing my-component IS detected |
| [ ] | Built-in video element IS detected |

- **Notes:** \_\_\_

---

### JSON Edge Case Files

| Status | File | Test |
| ------ | ---- | ---- |
| [ ] | 01_unicode_patterns.json | Unicode in patterns loads without error |
| [ ] | 02_special_regex.json | Alternation/lookahead patterns load correctly |
| [ ] | 03_colon_in_attr_values.json | Colon-separated keys parse to tuples |
| [ ] | 04_duplicate_ids.json | Same ID in CSS and JS works independently |

- **Notes:** \_\_\_

---

## 07_real_world/

### 01_design_system.css

**Expected custom features:** `special-animation-custom`, `my-custom-property`
**Expected built-in features:** `css-variables`, `flexbox`, `css-grid`, `css-animation`, `css-transitions`, `border-radius`, `css-gradients`, `transforms2d`, `css-filters`, `css-boxshadow`

| Status | Test |
| ------ | ---- |
| [ ] | Custom special-animation-custom detected |
| [ ] | Custom my-custom-property detected |
| [ ] | At least 10 features detected total |
| [ ] | No false positives from custom rules |

- **Detected count:** \_\_\_
- **Notes:** \_\_\_

---

### 02_web_component.html

**Expected custom features:** `custom-elementsv1`
**Expected built-in features:** `html5semantic`, `dialog`, `details`, `video`, `webm`, `srcset`, `input-email-tel-url`, `input-placeholder`, `form-validation`, `contenteditable`, `wai-aria`, `dataset`, `es6-module`, `link-rel-preload`, `viewport-units`

| Status | Test |
| ------ | ---- |
| [ ] | custom-elementsv1 detected (my-component) |
| [ ] | At least 12 features detected total |
| [ ] | All major categories represented |

- **Detected count:** \_\_\_
- **Notes:** \_\_\_

---

### 03_spa_app.js

**Expected custom features:** NONE (JS section is empty in custom_rules.json)
**Expected built-in features:** `const`, `let`, `arrow-functions`, `async-functions`, `template-literals`, `es6`, `promises`, `fetch`, `abortcontroller`, `namevalue-storage`, `json`, `queryselector`, `classlist`, `history`, `intersectionobserver`, `matchmedia`, `es6-class`, `use-strict`

| Status | Test |
| ------ | ---- |
| [ ] | No custom JS rules falsely triggered |
| [ ] | const detected |
| [ ] | fetch detected |
| [ ] | es6-class detected |
| [ ] | use-strict detected |
| [ ] | At least 15 features detected total |

- **Detected count:** \_\_\_
- **Notes:** \_\_\_

---

## comprehensive_test.py

**Purpose:** End-to-end validation script covering all parsers

| Status | Test |
| ------ | ---- |
| [ ] | All loader checks pass |
| [ ] | CSS existing rules detected |
| [ ] | CSS no false positives confirmed |
| [ ] | JS no false positives confirmed |
| [ ] | JS comments/strings ignored |
| [ ] | HTML existing rules detected |
| [ ] | HTML edge cases pass |
| [ ] | CSS edge cases pass |
| [ ] | Real-world CSS features detected |
| [ ] | Real-world HTML features detected |
| [ ] | Real-world JS features detected |
| [ ] | Cross-parser combined features >= 20 |

- **Run:** `.venv/bin/python tests/validation/custom_rules/comprehensive_test.py`
- **Notes:** \_\_\_

---

## Summary

| Category | Files | Pass | Fail | Notes |
| -------- | ----- | ---- | ---- | ----- |
| 01_loader | 5 | | | |
| 02_css_rules | 4 | | | |
| 03_js_rules | 4 | | | |
| 04_html_rules | 5 | | | |
| 05_cross_parser | 3 | | | |
| 06_edge_cases | 6 | | | |
| 07_real_world | 3 | | | |
| comprehensive | 1 | | | |
| **Total** | **31** | | | |

**Test Date:** \_\_\_
**Tester:** \_\_\_
**Version:** \_\_\_
