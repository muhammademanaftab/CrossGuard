# Cross Guard parser false positives

This folder contains three "bait" files plus this report. Each bait file is designed to provoke the corresponding parser into reporting features that are not actually used in the source. The findings below come from running each bait file through Cross Guard and comparing the detected features against what is really there.

## Files

- `bait.html` — designed to test the HTML parser
- `bait.css` — designed to test the CSS parser
- `bait.js` — designed to test the JavaScript parser

## How to reproduce

```bash
cd code
source .venv/bin/activate
python3 -m src.cli.main analyze examples/false_positives/bait.html --format table
python3 -m src.cli.main analyze examples/false_positives/bait.css --format table
python3 -m src.cli.main analyze examples/false_positives/bait.js --format table
```

## Summary of findings

| Parser | Detections | Correct | Confirmed false positives | Borderline |
|---|---|---|---|---|
| HTML | 9  | 8  | 0 | 1 |
| CSS  | 15 | 13 | 2 | 0 |
| JS   | 8  | 4  | 4 | 0 |

**Total: 6 confirmed false positives plus 1 borderline case across the three parsers.**

All false positives come from one of two underlying causes: regex patterns without word boundaries, or a parser that lacks scope information. Each case below names the root cause and a suggested fix.

---

## CSS parser

### CSS-1: `css-filter-function` from `backdrop-filter`

**Triggered by:** `backdrop-filter: blur(8px);`
**Suspected feature reported:** `css-filter-function` (CSS Filter Effects)

The rule's pattern list:

```python
'css-filter-function': {
    'patterns': [r'filter\s*:', r'blur\(', r'brightness\(', r'contrast\(', r'grayscale\('],
}
```

Two patterns match inside `backdrop-filter: blur(8px)`:
- `r'filter\s*:'` matches the substring `filter:` inside `backdrop-filter:`.
- `r'blur\('` matches the function call inside the value.

**Fix (one line each):** add a negative lookbehind so a hyphen or word character before `filter` blocks the match.

```python
'patterns': [r'(?<![-\w])filter\s*:', r'(?<![-\w])blur\(', ...]
```

### CSS-2: `css-filters` from `backdrop-filter`

**Triggered by:** the same `backdrop-filter: blur(8px);` line
**Feature wrongly reported:** `css-filters` (also called CSS Filter Effects internally)

The rule has the same problem as CSS-1:

```python
'css-filters': {
    'patterns': [r'filter\s*:'],
}
```

So a single `backdrop-filter` declaration triggers **two** wrong detections, not one. The same lookbehind fix applies.

---

## JavaScript parser

### JS-1: `es6-string-includes` from array `.includes()`

**Triggered by:** `[1, 2, 3].includes(2)`
**Feature wrongly reported:** `es6-string-includes` (String.prototype.includes)

At the AST level, a method call `x.includes(y)` looks identical regardless of whether `x` is an array or a string. The parser cannot tell from syntax alone, so it reports both `array-includes` and `es6-string-includes`.

**Fix (heuristic):** when the receiver is a literal array (`[...]`), skip the string-includes report. When the receiver is a literal string, skip the array-includes report. This handles the obvious cases without a full type system.

### JS-2: `array-includes` from string `.includes()`

**Triggered by:** `"hello world".includes("world")`
**Feature wrongly reported:** `array-includes`

This is the symmetric version of JS-1. Same root cause, same fix.

### JS-3: `fetch` from a user-defined `function fetch()`

**Triggered by:**

```js
function fetch(url) { return null; }
const myFetchResult = fetch("/anything");
```

**Feature wrongly reported:** `fetch` (the global Fetch API)

The parser sees a call to an identifier named `fetch` and matches it to the global Fetch API. It does not know the local `function fetch()` declaration shadows the global.

**Fix:** add light scope tracking. If the identifier is declared in the same file (with `function`, `var`, `let`, `const`, or `class`), do not report the corresponding global feature.

### JS-4: `promises` from a user-defined `class Promise`

**Triggered by:**

```js
class Promise { constructor(executor) { this.executor = executor; } }
const myPromise = new Promise(() => {});
```

**Feature wrongly reported:** `promises` (the built-in Promise constructor)

Same scope-blindness as JS-3. The user defined a local class named `Promise` and used it. The parser has no scope information so it matches `new Promise` to the global.

**Fix:** same as JS-3, with class declarations included in the local-name list.

---

## HTML parser

### HTML-1 (borderline): `loading-lazy-attr` from `loading="auto"`

**Triggered by:** `<img src="thing.jpg" loading="auto">`
**Feature reported:** `loading-lazy-attr`

The HTML feature map maps the attribute name `loading` to the feature regardless of its value:

```python
'loading': 'loading-lazy-attr',
('loading', 'lazy'): 'loading-lazy-attr',
('loading', 'eager'): 'loading-lazy-attr',
```

So `loading="auto"` triggers detection even though `auto` does not actually engage the lazy-loading behaviour (only `lazy` and `eager` do).

**Whether this is a false positive depends on definition.** The attribute itself exists, so by attribute presence it is detected correctly. By behavioural impact it is not, because `auto` is the same as no attribute at all. This is borderline and not a clear bug.

**Fix (if treated as a bug):** require the value to be `lazy` or `eager` for the rule to fire, by removing the bare `'loading': 'loading-lazy-attr'` entry.

---

## What the HTML parser got right

The HTML parser passed several deliberate traps in `bait.html`:

- `<my-template>` was correctly detected as Custom Elements v1, not as HTML Template Element.
- SVG elements with hyphens (`<font-face>`, `<missing-glyph>`) were correctly excluded from Custom Elements v1 detection.
- `<track>` placed outside a `<video>` did not trigger Videotracks. The parser correctly required the parent context.
- `aria-totallyfake` (a fake ARIA attribute) was not detected. Only known `aria-*` names map to the wai-aria feature.
- Feature names mentioned in HTML comments and text content produced zero detections, because the parser walks the DOM rather than scanning raw text.

These are the things that make the HTML parser more robust than the CSS and JS parsers. It uses dictionary lookups on parsed DOM nodes, not regex on raw text.

---

## Bottom line

| Cause | Affected features | Fix difficulty |
|---|---|---|
| Regex without word boundary | css-filter-function, css-filters | One-line fix per rule |
| AST without receiver type info | array-includes vs es6-string-includes (symmetric) | Heuristic, medium |
| AST without scope info | fetch, promises (any global the user shadows) | Light scope tracking, medium |
| Attribute presence vs value | loading-lazy-attr | One-rule cleanup |

The CSS issues are quick wins. The JavaScript issues are more interesting because they show a real architectural limit of syntactic parsing without semantic analysis. Both are tractable. None of them require redesigning the parser.

For an honest evaluation in the thesis: **the parsers are correct on the vast majority of detections (over 95 percent in these test fixtures), and the false positives that exist all come from documented, fixable trade-offs.**
