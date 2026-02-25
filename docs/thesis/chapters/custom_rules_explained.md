# Custom Rules in Cross Guard

Cross Guard comes with 200+ CSS, 270+ JS, and 150+ HTML built-in detection rules. But web standards evolve fast — new APIs, properties, and elements show up all the time. Custom rules let users add their own detection rules without touching the source code.

## Where Custom Rules Live

All custom rules are stored in a single JSON file:

```
src/parsers/custom_rules.json
```

It has three sections — one for each language:

```json
{
  "css": { ... },
  "javascript": { ... },
  "html": { ... }
}
```

## How CSS and JS Rules Work (Regex Matching)

CSS and JS rules use **regex patterns** to find features in source code. Each rule has a feature ID, one or more patterns, and a description:

```json
{
  "css": {
    "css-grid-lanes": {
      "patterns": ["masonry"],
      "description": "CSS Grid Lanes (Masonry Layout)",
      "keywords": ["masonry", "grid-lanes"]
    }
  }
}
```

When the parser scans a file, it runs `re.search(pattern, source_code)` for every pattern in every rule. If any pattern matches, that feature ID gets reported.

### JS Example

```json
{
  "javascript": {
    "test-compression-api": {
      "patterns": [
        "\\bCompressionStream\\b",
        "\\bDecompressionStream\\b"
      ],
      "description": "Compression Streams API"
    }
  }
}
```

If a JS file contains `new CompressionStream('gzip')`, the regex `\bCompressionStream\b` matches, and `test-compression-api` is reported as a detected feature.

### How They Merge With Built-in Rules

At parser init time, custom rules get merged into the built-in rules using Python's dict unpacking:

```python
self._all_features = {**ALL_CSS_FEATURES, **get_custom_css_rules()}
```

This creates a single combined dictionary. If a custom rule has the same feature ID as a built-in rule, the custom one overrides it. After merging, the parser treats all rules identically — there's no difference in how built-in vs custom rules are scanned.

## How HTML Rules Work (DOM Lookup)

HTML detection does **not** use regex. Instead, BeautifulSoup parses the HTML into a DOM tree, and the parser checks tags, attributes, and values against lookup dictionaries.

HTML custom rules have four categories:

```json
{
  "html": {
    "elements": {},
    "attributes": {},
    "input_types": {},
    "attribute_values": {}
  }
}
```

Each category is a simple key-value mapping:

| Category | Key | Value | What It Detects |
|---|---|---|---|
| `elements` | tag name | caniuse feature ID | `<tag-name>` in the HTML |
| `attributes` | attribute name | caniuse feature ID | The attribute on any element |
| `input_types` | type value | caniuse feature ID | `<input type="value">` |
| `attribute_values` | `attr:value` | caniuse feature ID | A specific attribute+value pair |

### HTML Example

```json
{
  "html": {
    "elements": {
      "my-component": "custom-elementsv1"
    }
  }
}
```

When BeautifulSoup encounters `<my-component>` in the HTML, the parser looks up `"my-component"` in the elements map, finds `"custom-elementsv1"`, and reports it. The analyzer then checks Can I Use for browser support of `custom-elementsv1`.

### How HTML Rules Merge

Same idea — dict merge at init:

```python
custom_html = get_custom_html_rules()
self._elements = {**HTML_ELEMENTS, **custom_html.get('elements', {})}
self._input_types = {**HTML_INPUT_TYPES, **custom_html.get('input_types', {})}
self._attributes = {**HTML_ATTRIBUTES, **custom_html.get('attributes', {})}
```

Custom entries join the built-in lookup maps. The parser does a simple dict lookup — no distinction between built-in and custom.

## The Feature ID Matters

The feature ID (the key in CSS/JS rules, the value in HTML rules) should match a Can I Use feature ID. That's how the analyzer knows which browser support data to pull.

- `"css-grid-lanes"` → looked up in the Can I Use database
- If the ID exists, you get real browser support data
- If it doesn't exist, the feature shows up as "unknown" in results

## Managing Custom Rules

Custom rules can be managed through:

1. **GUI** — The Rules Manager (visible in the sidebar) lets you add, edit, and delete custom rules with a form. Custom rules show a "Custom" badge and have Edit/Delete buttons.
2. **Directly editing** `src/parsers/custom_rules.json` — any valid JSON following the format above works.
3. **API** — `reload_custom_rules()` reloads from disk without restarting the app.

Keys starting with `_` are skipped during loading, so you can use them for comments or metadata:

```json
{
  "css": {
    "_note": "These are experimental rules for testing",
    "my-feature": { "patterns": ["..."], "description": "..." }
  }
}
```

## Summary

| Language | Detection Method | Rule Format | Merges Into |
|---|---|---|---|
| CSS | `re.search(pattern, source)` | `{ "patterns": [...], "description": "..." }` | `ALL_CSS_FEATURES` dict |
| JS | `re.search(pattern, source)` | `{ "patterns": [...], "description": "..." }` | `ALL_JS_FEATURES` dict |
| HTML | BeautifulSoup DOM lookup | `{ "tag": "caniuse-id" }` | 4 separate lookup dicts |
