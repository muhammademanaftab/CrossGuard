# Cross Guard Parsers — How They Work

This document explains how the three parsers (HTML, CSS, JavaScript) detect browser compatibility features. Each parser follows the same high-level pattern — **parse the file structurally, then match features against the Can I Use database** — but they use different parsing strategies suited to each language.

---

## Architecture Overview

```
                     ┌──────────────────┐
   User File ───────>│  Parser          │──────> Set of Can I Use Feature IDs
   (.html/.css/.js)  │  (language-      │        e.g. {'flexbox', 'css-grid',
                     │   specific)      │         'arrow-functions', 'dialog'}
                     └──────────────────┘
                              │
                     Uses feature maps from:
                     - html_feature_maps.py
                     - css_feature_maps.py
                     - js_feature_maps.py
                     - custom_rules.json (user-defined)
```

All three parsers share:
- **Feature Maps** — dictionaries mapping patterns/elements to Can I Use feature IDs
- **Custom Rules** — user-defined rules loaded from `custom_rules.json` (merged at init)
- **Public API** — `parse_file(path)`, `parse_string(content)`, `get_detailed_report()`, `get_statistics()`
- **Output** — a `Set[str]` of Can I Use feature IDs (e.g. `{'flexbox', 'promises'}`)

---

## HTML Parser

**Library:** BeautifulSoup4
**Strategy:** DOM tree walking — no regex needed
**File:** `html_parser.py` + `html_feature_maps.py`

### How It Works

```
HTML string
    │
    ▼
BeautifulSoup(html, 'html.parser')     ← Parses into DOM tree
    │
    ├── _detect_elements(soup)           ← Find <dialog>, <video>, <canvas>, etc.
    │     Walks all elements, looks up tag name in HTML_ELEMENTS map
    │     e.g. <dialog> → 'dialog', <canvas> → 'canvas'
    │
    ├── _detect_input_types(soup)        ← Find <input type="date">, type="color", etc.
    │     Checks type= attribute of <input> elements against HTML_INPUT_TYPES
    │     e.g. type="date" → 'input-datetime', type="range" → 'input-range'
    │
    ├── _detect_attributes(soup)         ← Find contenteditable, draggable, loading, etc.
    │     Walks all elements and their attributes
    │     Checks against HTML_ATTRIBUTES (global) and ELEMENT_SPECIFIC_ATTRIBUTES
    │     e.g. contenteditable → 'contenteditable', loading → 'loading-lazy-attr'
    │
    ├── _detect_attribute_values(soup)   ← Find specific attr=value combinations
    │     e.g. rel="preload" → 'link-rel-preload', type="module" → 'es6-module'
    │
    ├── _detect_special_patterns(soup)   ← Compound patterns (srcset, picture+source, data-*)
    │
    └── _find_unrecognized_patterns()    ← Flag unknown elements/attributes
```

### Feature Map Structure

```python
# Simple element name → feature ID
HTML_ELEMENTS = {
    'dialog': 'dialog',
    'video': 'video',
    'canvas': 'canvas',
    'section': 'html5semantic',
    ...
}

# Input type → feature ID
HTML_INPUT_TYPES = {
    'date': 'input-datetime',
    'color': 'input-color',
    'range': 'input-range',
    ...
}

# Attribute name → feature ID
HTML_ATTRIBUTES = {
    'contenteditable': 'contenteditable',
    'draggable': 'dragndrop',
    'loading': 'loading-lazy-attr',
    ...
}

# (attribute, value) tuple → feature ID
HTML_ATTRIBUTE_VALUES = {
    ('rel', 'preload'): 'link-rel-preload',
    ('type', 'module'): 'es6-module',
    ...
}
```

### Why BeautifulSoup?

HTML is a document tree, not a text-based language. BeautifulSoup gives us:
- Proper DOM traversal (parent/child/sibling relationships)
- Attribute access (including multi-valued attributes like `class`)
- Tolerance for malformed HTML (missing closing tags, etc.)
- No regex needed — we just walk the tree and look up names in dictionaries

---

## CSS Parser

**Library:** tinycss2 (W3C CSS Syntax Level 3 compliant) + regex
**Strategy:** Hybrid — tinycss2 AST for structural parsing, regex for feature detection
**File:** `css_parser.py` + `css_feature_maps.py`

### How It Works

The CSS parser does **NOT** use tinycss2 alone. It uses two tools together:

1. **tinycss2** — parses the CSS into a structured AST (handles syntax, nesting, comments)
2. **Regex** — runs 150+ patterns against AST-extracted text to detect features

Neither tool works alone. tinycss2 doesn't know what "flexbox" is. Regex can't handle nested `@media` blocks or comments. Together they cover both needs.

```
CSS string
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: tinycss2 (Structural Parsing)                               │
│                                                                     │
│ tinycss2.parse_stylesheet()          ← Parses into AST              │
│     │                                  Strips comments/whitespace   │
│     ▼                                  Resolves nesting             │
│ _extract_components(rules)           ← Recursively walks the AST    │
│     │                                  Collects:                    │
│     │                                  - declarations (property,    │
│     │                                    value, selector, block_id) │
│     │                                  - at_rules (@media, etc.)   │
│     │                                  - selectors (.class, #id)   │
│     ▼                                                               │
│ _build_matchable_text()              ← Rebuilds clean text from     │
│     │                                  AST components, preserving   │
│     │                                  { } block boundaries         │
└─────┼───────────────────────────────────────────────────────────────┘
      │
      ▼  matchable_text (clean CSS, no comments, structured blocks)
      │
┌─────┼───────────────────────────────────────────────────────────────┐
│ STEP 2: Regex (Feature Detection)                                   │
│     │                                                               │
│     ├── _detect_features(matchable_text)                            │
│     │     Runs 150+ regex patterns from css_feature_maps.py         │
│     │     e.g. r'display\s*:\s*(?:inline-)?flex' → 'flexbox'       │
│     │     e.g. r'@supports' → 'css-featurequeries'                 │
│     │                                                               │
│     └── _find_unrecognized_patterns_structured()                    │
│           Uses structured declarations from Step 1                  │
│           Tests property names against regex patterns               │
│           Flags unknown properties/at-rules                         │
└─────────────────────────────────────────────────────────────────────┘
```

### What tinycss2 Does (and Doesn't Do)

**tinycss2 handles:**
- Parsing CSS syntax into an AST (W3C CSS Syntax Level 3 compliant)
- Stripping comments and whitespace (`skip_comments=True, skip_whitespace=True`)
- Resolving nested structures (`@media { @supports { .foo { ... } } }`)
- Separating declarations (`property: value`) from selectors and at-rules
- Handling special blocks: `@font-face` (declarations directly), `@keyframes` (inner stops as QualifiedRules)

**tinycss2 does NOT handle:**
- Knowing what any CSS property means (it doesn't know "display: flex" is flexbox)
- Detecting whether a feature needs compatibility checking
- Pattern matching against the Can I Use database

That's where regex comes in.

### What Regex Does (and Doesn't Do)

**Regex handles:**
- Feature detection: 150+ patterns in `css_feature_maps.py`
- Matching properties (`scrollbar-color\s*:`), values (`display\s*:\s*grid`), selectors (`:has\(`), at-rules (`@container`)
- Custom rules (same regex format, from `custom_rules.json`)

**Regex does NOT handle:**
- Parsing CSS structure (would fail on nested blocks, comments with CSS-like text)
- Knowing block boundaries without `{ }` markers from the AST

### Why Both? Why Not Just One?

**Why not tinycss2 alone?**
tinycss2 is a *syntax* parser — it tells you "this is a declaration with property `display` and value `flex`". It doesn't map that to a Can I Use feature ID. We'd need to write 150+ manual `if property == 'display' and 'flex' in value` checks. Regex patterns are more expressive and maintainable for this.

**Why not regex alone?**
Pure regex on raw CSS would break because:
- `/* display: flex */` in a comment → false positive
- Nested `@media { @supports { ... } }` → regex can't track nesting depth
- `@keyframes` inner blocks (`from`, `to`, `50%`) → look like selectors to regex
- Patterns like `flexbox-gap` need to match `display: flex` AND `gap` in the **same block** — regex needs `{ }` block boundaries to do this

### The `_build_matchable_text()` Bridge

This is the key method connecting the two steps. It takes AST-extracted components and rebuilds text that regex patterns can match against:

```
tinycss2 AST output:                     matchable_text for regex:
┌─────────────────────┐                  ┌──────────────────────────────┐
│ selector: ".box"    │                  │ .box { display: flex;        │
│ property: "display" │    ────────>     │        gap: 10px; }          │
│ value: "flex"       │                  │ @media (min-width: 768px)    │
│ property: "gap"     │                  │ @supports (display: grid)    │
│ value: "10px"       │                  └──────────────────────────────┘
│ @media: min-width   │
│ @supports: grid     │
└─────────────────────┘
```

The `{ }` block boundaries are preserved so patterns like `flexbox-gap` (which check for `display: flex` and `gap` in the **same block** using `[^}]*`) still work correctly.

### Feature Map Structure

```python
CSS_LAYOUT_FEATURES = {
    'flexbox': {
        'patterns': [r'display\s*:\s*(?:inline-)?flex', r'flex-direction', ...],
        'description': 'CSS Flexbox'
    },
    'flexbox-gap': {
        'patterns': [r'display\s*:\s*(?:inline-)?flex[^}]*\bgap\s*:', ...],
        'description': 'gap property for Flexbox'
    },
    ...
}
```

---

## JavaScript Parser

**Library:** tree-sitter (via tree-sitter-languages)
**Strategy:** Hybrid — AST for syntax + API detection, regex for everything else
**File:** `js_parser.py` + `js_feature_maps.py`

### How It Works

```
JS string
    │
    ├── _detect_directives(raw)            ← BEFORE any processing (runs on raw input)
    │     "use strict" → 'use-strict'        These ARE string literals, so must detect
    │     "use asm"    → 'asmjs'             before strings are stripped
    │
    ├── _detect_event_listeners(raw)       ← BEFORE any processing (runs on raw input)
    │     addEventListener('hashchange')     Event names are inside string arguments
    │     → 'hashchange'                     so must detect before strings are stripped
    │
    ▼
_parse_with_tree_sitter(js_content)        ← Parse into AST
    │
    ├── IF tree-sitter succeeds:
    │   │
    │   ├── Tier 1: _detect_ast_syntax_features()     ← AST node types
    │   │     arrow_function      → 'arrow-functions'
    │   │     template_string     → 'template-literals'
    │   │     class_declaration   → 'es6-class'
    │   │     generator_function  → 'es6-generators'
    │   │     await_expression    → 'async-functions'
    │   │     spread_element      → 'es6'
    │   │     lexical_declaration → 'const' or 'let'
    │   │     optional_chain      → optional chaining (?.)
    │   │     binary_expression ?? → nullish coalescing (??)
    │   │     private_property_identifier → private fields (#x)
    │   │
    │   ├── Tier 2: _detect_ast_api_features()         ← AST identifiers/calls
    │   │     new Promise(...)        → 'promises'
    │   │     new Worker(...)         → 'webworkers'
    │   │     fetch(...)              → 'fetch'
    │   │     navigator.geolocation   → 'geolocation'
    │   │     crypto.subtle           → 'cryptography'
    │   │     Promise.all(...)        → 'promises'
    │   │     Object.entries(...)     → 'object-entries'
    │   │     SharedArrayBuffer       → 'sharedarraybuffer'
    │   │
    │   ├── _build_matchable_text_from_ast()           ← Strip comments/strings via AST
    │   │     Comments     → replaced with whitespace
    │   │     Strings      → keep quotes, strip content ("..." → "")
    │   │     Templates    → keep backticks + ${x} markers
    │   │     Code         → preserved as-is
    │   │
    │   ├── Tier 3: _detect_features(matchable)        ← Regex patterns (280+ features)
    │   │     Same regex engine, but runs on cleaner AST-extracted text
    │   │     Also handles custom rules from custom_rules.json
    │   │
    │   └── _find_unrecognized_patterns(matchable)     ← Flag unknown APIs
    │
    └── ELSE (tree-sitter unavailable):
        │
        ├── _remove_comments_and_strings()  ← Regex-based comment/string stripping
        ├── _detect_features(cleaned)       ← Same regex patterns
        └── _find_unrecognized_patterns()   ← Same unrecognized detection
```

### The Three Detection Tiers

| Tier | Method | What It Detects | False Positive Risk | How |
|------|--------|-----------------|--------------------|----|
| **1** | AST node types | Arrow functions, template literals, classes, generators, const/let, spread, rest, await, `?.`, `??`, `#private` | **Zero** — these are unique syntax constructs in the AST | Walk tree, check `node.type` against `AST_SYNTAX_NODE_MAP` |
| **2** | AST identifiers | `new Promise`, `fetch()`, `navigator.geolocation`, `Promise.all`, `SharedArrayBuffer` | **Low** — confirmed code context (not strings/comments) | Check constructor names, function calls, member expressions, identifiers |
| **3** | Regex on AST text | Everything else + custom rules (280+ patterns) | **Same as before**, but cleaner input | Existing `_detect_features()` runs against AST-stripped text |

### Why tree-sitter + Regex (Hybrid)?

Pure regex had three problems:
1. **False positives** — `navigator.bluetooth` inside a comment or string would be detected
2. **Can't detect syntax** — `?.` (optional chaining), `??` (nullish coalescing), `#x` (private fields) have no reliable regex pattern
3. **No scope awareness** — can't distinguish code from comments/strings

tree-sitter solves all three. But we keep regex for Tier 3 because:
- 280+ existing patterns already work well
- Custom rules use regex format
- Some features don't have a clean AST signature (e.g. `performance.mark` could be any member expression)

### The `_build_matchable_text_from_ast()` Bridge

Same concept as the CSS parser's `_build_matchable_text()`. It takes the AST and produces clean text by:

```
Source code:                              Matchable text:
┌──────────────────────────────┐         ┌──────────────────────────────┐
│ // Use fetch for API calls   │         │                              │  ← comment → spaces
│ const data = "some string";  │         │ const data = "";             │  ← string content stripped
│ const url = `api/${id}`;     │         │ const url = `${x}`;          │  ← template text stripped
│ fetch(url);                  │  ───>   │ fetch(url);                  │  ← code preserved
│ /* navigator.bluetooth */    │         │                              │  ← comment → spaces
│ navigator.clipboard.read();  │         │ navigator.clipboard.read();  │  ← code preserved
└──────────────────────────────┘         └──────────────────────────────┘
```

This means existing regex patterns match the same way they always did, but they no longer see features hidden inside comments or strings.

### Graceful Fallback

If tree-sitter is not installed, the parser falls back to the original regex-only pipeline automatically:

```python
_TREE_SITTER_AVAILABLE = False
try:
    from tree_sitter_languages import get_language, get_parser
    _JS_PARSER = get_parser('javascript')
    _TREE_SITTER_AVAILABLE = True
except (ImportError, Exception):
    pass  # Falls back to regex-only
```

This means the application works on any system — tree-sitter just makes it more accurate.

### Feature Map Structure

```python
# Regex-based (Tier 3) — existing format, shared with custom rules
ALL_JS_FEATURES = {
    'promises': {
        'patterns': [r'\bnew\s+Promise', r'\.then\(', r'Promise\.'],
        'description': 'Promises'
    },
    'fetch': {
        'patterns': [r'\bfetch\s*\('],
        'description': 'Fetch API'
    },
    ...
}

# AST-based (Tier 1) — node type → feature ID
AST_SYNTAX_NODE_MAP = {
    'arrow_function': 'arrow-functions',
    'template_string': 'template-literals',
    'class_declaration': 'es6-class',
    ...
}

# AST-based (Tier 2) — constructor/call/member → feature ID
AST_NEW_EXPRESSION_MAP = { 'Promise': 'promises', 'Worker': 'webworkers', ... }
AST_CALL_EXPRESSION_MAP = { 'fetch': 'fetch', 'atob': 'atob-btoa', ... }
AST_MEMBER_EXPRESSION_MAP = { 'navigator.geolocation': 'geolocation', ... }
AST_IDENTIFIER_MAP = { 'SharedArrayBuffer': 'sharedarraybuffer', ... }
AST_OPERATOR_MAP = { '??': 'nullish-coalescing', '?.': 'optional-chaining' }
```

---

## Custom Rules System

All three parsers support user-defined rules via `custom_rules.json`. The `CustomRulesLoader` (singleton) loads them once and each parser merges them at initialization.

```
custom_rules.json
    │
    ▼
CustomRulesLoader (singleton)
    │
    ├── get_custom_css_rules()  → merged into CSSParser._all_features
    ├── get_custom_js_rules()   → merged into JavaScriptParser._all_features
    └── get_custom_html_rules() → merged into HTMLParser._elements, _attributes, etc.
```

### Format

```json
{
  "css": {
    "feature-id": {
      "patterns": ["regex-pattern"],
      "description": "Human readable name"
    }
  },
  "javascript": {
    "feature-id": {
      "patterns": ["regex-pattern"],
      "description": "Human readable name"
    }
  },
  "html": {
    "elements": { "element-name": "caniuse-feature-id" },
    "attributes": { "attr-name": "caniuse-feature-id" },
    "attribute_values": { "attr:value": "caniuse-feature-id" }
  }
}
```

CSS and JS custom rules go through the **regex pipeline** (Tier 3 for JS), so they work identically whether tree-sitter is available or not. HTML custom rules are dictionary lookups (no regex).

---

## Side-by-Side Comparison

| Aspect | HTML Parser | CSS Parser | JS Parser |
|--------|-------------|------------|-----------|
| **Parsing library** | BeautifulSoup4 | tinycss2 + regex | tree-sitter + regex |
| **AST role** | Gives DOM tree for lookups | Structural parsing (nesting, comments) | Syntax + API detection (Tier 1 & 2) |
| **Regex role** | Not used | Feature detection (150+ patterns) | Feature detection (280+ patterns, Tier 3) |
| **Detection method** | Dictionary lookup (exact) | Regex on AST-cleaned text | AST node types + AST identifiers + regex |
| **False positive handling** | N/A (DOM is exact) | tinycss2 strips comments | tree-sitter strips comments/strings |
| **Fallback** | None needed | None needed | Regex-only (if tree-sitter unavailable) |
| **Feature map count** | 100+ elements/attrs | 150+ properties/features | 280+ regex patterns + 6 AST maps |
| **Custom rules** | Dict entries | Regex patterns | Regex patterns (Tier 3) |
| **Test count** | ~1800 | 532 | 332 (245 regex + 87 AST) |

---

## Adding a New Feature Rule

### CSS
Edit `css_feature_maps.py`, add to the appropriate category dict:
```python
'feature-id': {
    'patterns': [r'property-name\s*:'],
    'description': 'Human readable name'
}
```

### JavaScript
Edit `js_feature_maps.py`:
- For **syntax features** (node types): add to `AST_SYNTAX_NODE_MAP`
- For **API features** (constructors): add to `AST_NEW_EXPRESSION_MAP`
- For **API features** (function calls): add to `AST_CALL_EXPRESSION_MAP`
- For **API features** (member expressions): add to `AST_MEMBER_EXPRESSION_MAP`
- For **regex patterns**: add to the appropriate dict in `ALL_JS_FEATURES`

### HTML
Edit `html_feature_maps.py`:
- Elements: add to `HTML_ELEMENTS`
- Attributes: add to `HTML_ATTRIBUTES`
- Input types: add to `HTML_INPUT_TYPES`
- Attribute values: add to `HTML_ATTRIBUTE_VALUES`

### Custom Rules (No Code Changes)
Edit `custom_rules.json` or use the GUI's Custom Rules manager.

---

## File Map

```
src/parsers/
├── html_parser.py          ← HTML parser (BeautifulSoup)
├── html_feature_maps.py    ← HTML element/attribute → feature ID maps
├── css_parser.py           ← CSS parser (tinycss2 + regex)
├── css_feature_maps.py     ← CSS property/selector → feature ID maps
├── js_parser.py            ← JS parser (tree-sitter + regex)
├── js_feature_maps.py      ← JS pattern/AST → feature ID maps
├── custom_rules.json       ← User-defined detection rules
├── custom_rules_loader.py  ← Singleton loader for custom rules
└── PARSERS.md              ← This file
```
