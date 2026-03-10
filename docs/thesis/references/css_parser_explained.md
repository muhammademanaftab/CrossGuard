# CSS Parser - How It Works

## What is the CSS Parser's Job?

Same idea as the HTML parser: take a CSS file, read through it, and find all the web features that might have browser compatibility issues.

For example, if your CSS uses `display: grid`, that's CSS Grid — a feature that older browsers don't support. The parser needs to find it.

Basic properties like `color`, `margin`, `padding`, `font-size` are NOT checked because they work in every browser. The parser only looks for modern features that might have compatibility issues.

---

## Why CSS is Harder Than HTML

The HTML parser uses simple dictionary lookups: "Does the HTML have a `<dialog>` element? Yes/No." That works because HTML elements have one fixed name.

CSS is different. A single feature can appear in many forms:

```css
/* All of these mean "CSS Flexbox" */
display: flex;
display: inline-flex;
flex-direction: row;
flex-wrap: wrap;
flex-grow: 1;
flex-shrink: 0;
flex-basis: 200px;
flex: 1 0 auto;
```

You can't just check "does the CSS have the word `flex`?" — that would miss `flex-direction`, `flex-wrap`, etc. And checking each one individually with a dictionary would be tedious for 150+ features.

**Solution**: We use **regex** (regular expressions) — pattern matching for text. One regex pattern can match many variations at once.

---

## What is Regex?

Regex is a mini-language for describing text patterns. Instead of searching for an exact word, you describe a **shape** of text.

### Basic Regex Symbols

| Symbol | Meaning | Example |
|--------|---------|---------|
| `\s` | Any whitespace (space, tab) | `display\s*:` matches `display:` and `display :` |
| `*` | Zero or more of the previous thing | `\s*` = zero or more spaces |
| `+` | One or more of the previous thing | `\d+` = one or more digits |
| `\d` | Any digit (0-9) | `\d+px` matches `16px`, `200px` |
| `.` | Any character | `a.c` matches `abc`, `a1c`, `a-c` |
| `(?:...)` | Group without capturing | `(?:inline-)?flex` matches `flex` and `inline-flex` |
| `?` | Zero or one of the previous thing | `(?:inline-)?` = "inline-" may or may not be there |
| `\(` | A literal `(` character | `calc\(` matches `calc(` |
| `[^}]*` | Any characters except `}` | Matches everything until a closing brace |
| `\b` | Word boundary | `\bgap\s*:` prevents matching `flexbox-gap` accidentally |
| `(?<![a-z-])` | Not preceded by a letter or dash | Prevents partial matches |

### What Does `r` Mean?

In Python, backslash `\` has special meaning in strings. `\n` = newline, `\t` = tab. But regex also uses backslashes: `\s` = whitespace, `\d` = digit.

If we write `"\s"` Python thinks: "escape sequence `\s`... I don't know that one." It might cause errors.

The `r` prefix means **raw string** — Python ignores backslashes and passes them through as-is:

```python
# Without r: Python processes backslashes first (BAD for regex)
pattern = "\s*:\s*"    # Python might misinterpret \s

# With r: Python leaves backslashes alone (GOOD for regex)
pattern = r"\s*:\s*"   # \s reaches regex engine correctly
```

**Rule**: Always use `r'...'` for regex patterns.

---

## The Two Main Files

| File | What it contains |
|------|-----------------|
| `src/parsers/css_parser.py` | The parser logic (the code that reads CSS and finds features) |
| `src/parsers/css_feature_maps.py` | The feature maps (the data that says what patterns to look for) |

---

## What is tinycss2?

tinycss2 is a Python library that parses CSS. Just like BeautifulSoup parses HTML into Python objects, tinycss2 parses CSS into Python objects (an AST — Abstract Syntax Tree).

We don't parse CSS ourselves. tinycss2 does it for us.

```python
import tinycss2

css_text = """
.box { display: flex; gap: 10px; }
@media (max-width: 768px) { .box { flex-direction: column; } }
"""
rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
```

Now `rules` is NOT a string anymore. It's a list of Python objects representing each CSS rule.

---

## tinycss2 Functions We Use

### `tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)`

Parses a full CSS stylesheet. Returns a list of rule objects.

Each object is one of these types:
- **`QualifiedRule`** — a regular CSS rule like `.box { color: red; }`
- **`AtRule`** — an @-rule like `@media`, `@keyframes`, `@font-face`
- **`ParseError`** — something tinycss2 couldn't understand
- **`WhitespaceToken`** — whitespace (we skip these)

### `tinycss2.parse_blocks_contents(content)`

Parses the contents inside a `{ }` block. Returns declarations, nested rules, etc.

We use this to look inside rule blocks and extract the properties.

### `tinycss2.serialize(nodes)`

Converts AST nodes back to text. We use this to get the text of a selector or a value.

```python
# A QualifiedRule object has a .prelude (the selector part)
selector_text = tinycss2.serialize(rule.prelude).strip()
# Returns: ".box" or "@media (max-width: 768px)" etc.
```

---

## What are the Feature Maps?

Feature maps are Python dictionaries stored in `css_feature_maps.py`. They map **regex patterns** to **Can I Use feature IDs**.

Each feature has 3 parts:

```python
'feature-id': {
    'patterns': [r'regex-pattern-1', r'regex-pattern-2'],   # What to search for
    'keywords': ['human readable name'],                      # For GUI display
    'description': 'Longer description'                       # For reports
}
```

### Example: CSS Grid

```python
'css-grid': {
    'patterns': [
        r'display\s*:\s*(?:inline-)?grid',   # matches "display: grid" or "display: inline-grid"
        r'grid-template',                      # matches "grid-template-columns", "grid-template-rows"
        r'grid-column',                        # matches "grid-column: 1 / 3"
        r'grid-row',                           # matches "grid-row: 2"
        r'grid-area',                          # matches "grid-area: header"
        r'grid-auto-columns',
        r'grid-auto-rows',
        r'grid-auto-flow',
        r'grid-gap',
        r'justify-items',
        r'justify-self',
        r'place-items',
        r'place-content',
        r'place-self'
    ],
    'keywords': ['css grid'],
    'description': 'CSS Grid Layout'
}
```

If ANY of those 14 patterns matches the CSS text, the feature `'css-grid'` is added to the results.

### Example: Flexbox Gap (Block-Aware Pattern)

```python
'flexbox-gap': {
    'patterns': [
        r'display\s*:\s*(?:inline-)?flex[^}]*\bgap\s*:',
        r'\bgap\s*:[^}]*display\s*:\s*(?:inline-)?flex',
    ],
    'keywords': ['flexbox gap'],
    'description': 'gap property for Flexbox'
}
```

This pattern uses `[^}]*` which means "any characters except `}`". This ensures `display: flex` and `gap:` are in the **same CSS block** `{ }`. Otherwise, gap in a grid block would falsely trigger this feature.

---

## The 20+ Feature Categories

The feature maps are organized into categories for maintainability:

| Category | Features | Examples |
|----------|----------|---------|
| `CSS_LAYOUT_FEATURES` | 7 | flexbox, css-grid, multicolumn |
| `CSS_TRANSFORM_ANIMATION` | 5 | transforms2d, transforms3d, css-animation |
| `CSS_COLOR_BACKGROUND` | 8 | css3-colors, css-gradients, css-backdrop-filter |
| `CSS_TYPOGRAPHY` | 22 | fontface, woff2, variable-fonts, text-overflow |
| `CSS_BOX_MODEL` | 4 | css3-boxsizing, intrinsic-width, object-fit |
| `CSS_BORDER_OUTLINE` | 4 | border-image, border-radius |
| `CSS_SHADOW_EFFECTS` | 3 | css-boxshadow, css-textshadow, css-mixblendmode |
| `CSS_SELECTORS` | 20 | css-sel3, css-has, css-focus-visible, ::placeholder |
| `CSS_MEDIA_QUERIES` | 5 | css-mediaqueries, prefers-color-scheme |
| `CSS_UNITS` | 5 | rem, viewport-units, calc, ch-unit |
| `CSS_VARIABLES` | 1 | css-variables |
| `CSS_AT_RULES` | 5 | css-featurequeries, css-paged-media |
| `CSS_POSITIONING` | 3 | css-sticky, css-fixed |
| `CSS_OVERFLOW` | 3 | css-overflow, css-clip-path |
| `CSS_INTERACTION` | 10 | css-touch-action, css-scroll-behavior |
| `CSS_MISC` | 20 | css-logical-props, css-writing-mode |
| `CSS_CONTAINER` | 2 | css-container-queries |
| `CSS_SUBGRID` | 1 | css-subgrid |
| `CSS_CASCADE` | 1 | css-cascade-layers |
| `CSS_NESTING` | 1 | css-nesting |
| `CSS_ADDITIONAL_1` | 18 | css-anchor-positioning, css-conic-gradients |
| `CSS_ADDITIONAL_2` | 18 | css-hyphens, css-masks, css-math-functions |
| `CSS_ADDITIONAL_3` | 19 | css-scrollbar, css-shapes, view-transitions |

All are merged into one big dictionary at the bottom:

```python
ALL_CSS_FEATURES = {
    **CSS_LAYOUT_FEATURES,
    **CSS_TRANSFORM_ANIMATION,
    **CSS_COLOR_BACKGROUND,
    ...all other categories...
}
```

This gives us about **150+ features** to check, each with one or more regex patterns.

---

## 7 Types of Regex Patterns

### 1. Simple Property Name

```python
r'border-radius\s*:'      # matches "border-radius:"
r'clip-path\s*:'           # matches "clip-path:"
```

The `\s*:` means "optional spaces then a colon". This matches the property no matter how it's formatted.

### 2. Property + Specific Value

```python
r'display\s*:\s*(?:inline-)?grid'   # matches "display: grid" or "display: inline-grid"
r'position\s*:\s*sticky'            # matches "position: sticky"
r'cursor\s*:\s*grab'                # matches "cursor: grab"
```

Some features aren't about the property itself — `display` works everywhere. It's the **value** that might not be supported.

### 3. Multiple Patterns Per Feature

```python
'css-animation': {
    'patterns': [
        r'@keyframes',                     # the @keyframes rule
        r'animation\s*:',                  # shorthand
        r'animation-name',                 # individual properties
        r'animation-duration',
        r'animation-timing-function',
        r'animation-delay',
        r'animation-iteration-count',
        r'animation-direction',
        r'animation-fill-mode',
        r'animation-play-state'
    ]
}
```

CSS animations can be triggered by any of these 10 patterns. If we find **any one** of them, we know the file uses CSS animations.

### 4. At-Rule Detection

```python
r'@keyframes'     # CSS animations
r'@supports'      # CSS feature queries
r'@container'     # CSS container queries
r'@layer'         # CSS cascade layers
```

### 5. Selector Detection

```python
r':has\('           # :has() selector
r':focus-visible'   # :focus-visible pseudo-class
r'::placeholder'    # ::placeholder pseudo-element
r':nth-child'       # :nth-child selector
```

### 6. Unit Detection

```python
r'\d+\.?\d*rem'     # matches "16rem", "1.5rem"
r'\d+\.?\d*vw'      # matches "100vw", "50.5vw"
```

`\d+\.?\d*` means "one or more digits, optionally a dot, optionally more digits" — this matches numbers like `16`, `1.5`, `100`, `50.5`.

### 7. Value/Function Detection

```python
r'calc\('             # calc() function
r'linear-gradient'    # gradient function
r'var\(--'            # CSS variable usage
r'min\('              # min() function
r'clamp\('            # clamp() function
```

---

## The Complete 4-Step Detection Flow

Here's what happens when you give the parser a CSS file:

```
Step 0: Read the file
Step 1: tinycss2 parses CSS into AST objects
Step 2: Extract components (declarations, @-rules, selectors)
Step 3: Build matchable text (clean text grouped by block)
Step 4: Run regex patterns against the text
```

### Step 0: Read the File (`parse_file`)

```python
def parse_file(self, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        css_content = f.read()           # Read file as string
    return self.parse_string(css_content)  # Pass to main method
```

### Step 1: Parse with tinycss2 (`parse_string`, line 84)

```python
rules = tinycss2.parse_stylesheet(
    css_content, skip_comments=True, skip_whitespace=True
)
```

Given this CSS:
```css
/* My styles */
.container { display: flex; gap: 10px; }
@media (max-width: 768px) {
    .container { flex-direction: column; }
}
```

tinycss2 returns a list of 2 objects:
1. A `QualifiedRule` for `.container { display: flex; gap: 10px; }`
2. An `AtRule` for `@media (max-width: 768px) { ... }`

Comments and whitespace are automatically skipped.

### Step 2: Extract Components (`_extract_components`)

This method walks through the tinycss2 objects and collects 3 lists:

**Declarations** — every `property: value` pair, with its selector and block ID:
```python
[
    ('display', 'flex', '.container', 0),        # block 0
    ('gap', '10px', '.container', 0),             # block 0 (same block)
    ('flex-direction', 'column', '.container', 1) # block 1 (different block)
]
```

**At-rules** — every @-rule with its prelude (the part after `@`):
```python
[
    ('media', '(max-width: 768px)')
]
```

**Selectors** — every selector string:
```python
['.container', '.container']
```

#### How Recursion Works

`@media` blocks contain other rules inside them. The method handles this by **recursing** (calling itself):

```
_extract_components finds:
    QualifiedRule (.container { display: flex; gap: 10px; })
        → extracts declarations into block 0
    AtRule (@media...)
        → records the @media at-rule
        → calls parse_blocks_contents() to get inner rules
        → calls _extract_components AGAIN on those inner rules  ← RECURSION
            → finds QualifiedRule (.container { flex-direction: column; })
                → extracts declarations into block 1
```

This means the parser can handle any level of nesting: `@media` inside `@supports` inside `@layer`, etc.

#### The @font-face Special Case

`@font-face` is different from `@media`. It has declarations **directly** inside it (not nested rules):

```css
/* @media has nested RULES inside */
@media (max-width: 768px) {
    .box { color: red; }    /* ← This is a rule */
}

/* @font-face has DECLARATIONS directly inside */
@font-face {
    font-family: 'MyFont';   /* ← This is a declaration */
    src: url('font.woff2');   /* ← This is a declaration */
}
```

The code handles this with a special check:
```python
if keyword == 'font-face':
    # Parse declarations directly from content
    self._extract_block_contents(rule.content, '@font-face', ...)
else:
    # @media, @supports, etc. — recurse for nested rules
    inner_rules = tinycss2.parse_blocks_contents(rule.content)
    self._extract_components(inner_rules)  # recursion
```

#### What is block_id?

Each `{ }` block gets a unique number. This preserves which declarations belong together.

Why does this matter? For the **flexbox-gap** pattern. The regex needs to check that `display: flex` and `gap:` are in the **same** block:

```css
/* These are in the SAME block (block 0) — IS flexbox-gap */
.flex-box { display: flex; gap: 10px; }

/* These are in DIFFERENT blocks — is NOT flexbox-gap */
.flex-box { display: flex; }    /* block 0 */
.grid-box { display: grid; gap: 10px; }  /* block 1 */
```

Without block_id tracking, the parser would falsely combine them.

### Step 3: Build Matchable Text (`_build_matchable_text`)

This method takes the 3 lists and rebuilds clean text that regex patterns can work with.

From our example, it builds:

```
.container { display: flex; gap: 10px; }
.container { flex-direction: column; }
@media (max-width: 768px)
```

**Key design decisions**:
- Each block stays separate (preserving block boundaries for patterns like flexbox-gap)
- Declarations within a block are joined with `; `
- Selectors that had declarations are wrapped in `{ }`
- @-rules are listed separately
- Blocks with the same selector but different block_ids stay separate

### Step 4: Detect Features (`_detect_features`)

This is where the actual feature finding happens. It loops through ALL 150+ features and tries their regex patterns against the text:

```python
for feature_id, feature_info in self._all_features.items():
    patterns = feature_info.get('patterns', [])
    feature_found = False

    for pattern in patterns:
        matches = re.findall(pattern, css_content, re.IGNORECASE)
        if matches:
            feature_found = True
            break  # Found it, no need to check more patterns

    if feature_found:
        self.features_found.add(feature_id)
```

For our example text, let's trace through a few features:

**Checking `'flexbox'`** — pattern `r'display\s*:\s*(?:inline-)?flex'`:
- Searches text... finds `display: flex` in block 0 → **MATCH**
- Adds `'flexbox'` to results

**Checking `'flexbox-gap'`** — pattern `r'display\s*:\s*(?:inline-)?flex[^}]*\bgap\s*:'`:
- Searches text... finds `display: flex; gap: 10px;` (same block) → **MATCH**
- Adds `'flexbox-gap'` to results

**Checking `'css-grid'`** — pattern `r'display\s*:\s*(?:inline-)?grid'`:
- Searches text... no grid anywhere → **NO MATCH**
- Skipped

**Checking `'css-mediaqueries'`** — pattern `r'@media\s*\('`:
- Searches text... finds `@media (max-width: 768px)` → **MATCH**
- Adds `'css-mediaqueries'` to results

---

## Unrecognized Patterns (Safety Net)

After feature detection, the parser runs `_find_unrecognized_patterns_structured()`. This checks every property found in the CSS against:

1. A list of **basic properties** (universally supported — `color`, `margin`, `padding`, etc.)
2. The feature map patterns

If a property doesn't match anything, it goes into `unrecognized_patterns`. This alerts users that the parser might be missing a feature.

```python
# Example: if CSS has "aspect-ratio: 16/9" but no feature pattern matched it
# (actually it does match minmaxwh, but hypothetically)
self.unrecognized_patterns.add("property: aspect-ratio")
```

This also checks @-rules. Basic ones like `@media`, `@import`, `@charset`, `@font-face`, `@page` are skipped. Unknown ones are flagged.

---

## Custom Rules

Users can extend the parser without changing source code, just like the HTML parser:

```python
def __init__(self):
    self._all_features = {**ALL_CSS_FEATURES, **get_custom_css_rules()}
```

The `{**dict1, **dict2}` syntax merges two dictionaries. Custom rules get added on top of built-in rules.

Custom rules are stored in `src/parsers/custom_rules.json` and follow the same format:
```json
{
  "css": {
    "some-feature": {
      "patterns": ["regex-pattern"],
      "description": "Human readable name"
    }
  }
}
```

---

## Other Functions in the Parser

### `get_detailed_report()`

Returns a dictionary with full information about what was found:

```python
{
    'total_features': 5,
    'features': ['css-grid', 'css-mediaqueries', 'css-variables', 'flexbox', 'rem'],
    'feature_details': [
        {'feature': 'flexbox', 'description': 'CSS Flexbox', 'matched_properties': ['display']},
        {'feature': 'css-grid', 'description': 'CSS Grid Layout', 'matched_properties': ['display']},
        ...
    ],
    'unrecognized': ['property: some-unknown-thing']
}
```

### `parse_multiple_files(filepaths)`

Takes a list of CSS files, parses each one, and combines all results into one set.

```python
parser = CSSParser()
all_features = parser.parse_multiple_files(['style.css', 'layout.css', 'theme.css'])
# Returns the union of features from all 3 files
```

### `get_statistics()`

Groups found features by category and returns counts:

```python
{
    'total_features': 12,
    'layout_features': 3,        # flexbox, css-grid, etc.
    'transform_animation': 2,    # transforms2d, css-animation
    'color_background': 1,       # css-gradients
    'typography': 2,             # fontface, woff2
    'selectors': 1,              # css-sel3
    'media_queries': 1,          # css-mediaqueries
    'other_features': 2,         # everything else
    'categories': { ... }        # lists of feature IDs per category
}
```

### `validate_css(css_content)`

Quick check: "Does this text look like CSS?" Returns `True` or `False`.

Uses tinycss2 to parse it. If tinycss2 finds any valid rules or @-rules, it's CSS. Also accepts CSS fragments with `property: value` patterns.

### Convenience Functions

Two standalone functions that create a parser, use it, and return results:

```python
# Instead of:
parser = CSSParser()
features = parser.parse_file('style.css')

# You can use:
features = parse_css_file('style.css')
features = parse_css_string('display: grid; gap: 10px;')
```

---

## The Output

After all 4 steps run, the parser returns a **set** of Can I Use feature IDs:

```python
{'flexbox', 'flexbox-gap', 'css-mediaqueries', 'rem', 'css-variables'}
```

This set then goes to the **Analyzer**, which looks up each feature ID in the Can I Use database to check which browsers support it.

---

## Full Flow Summary

```
Your CSS file
    |
    v
Read the file as a string
    |
    v
tinycss2 parses the string into AST objects
(QualifiedRule, AtRule, Declaration, etc.)
    |
    v
_extract_components walks the AST recursively:
    |
    |-- Declarations: (property, value, selector, block_id)
    |-- At-rules: (keyword, prelude)
    |-- Selectors: selector strings
    |
    v
_build_matchable_text rebuilds clean text:
    selector { property: value; property: value; }
    @keyword prelude
    |
    v
_detect_features runs 150+ regex patterns:
    |
    |-- r'display\s*:\s*(?:inline-)?flex'  → 'flexbox'
    |-- r'@media\s*\('                     → 'css-mediaqueries'
    |-- r'\d+\.?\d*rem'                    → 'rem'
    |-- r'var\(--'                         → 'css-variables'
    |-- ... 150+ more patterns
    |
    v
Set of Can I Use feature IDs
{'flexbox', 'css-mediaqueries', 'rem', 'css-variables', ...}
    |
    v
Goes to the Analyzer for browser compatibility checking
```

---

## Concrete Example

Given this CSS file:

```css
:root {
    --primary: #3b82f6;
    --gap: 1rem;
}

.container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--gap);
    max-width: 80vw;
}

.card {
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
}

.card:has(.featured) {
    border: 2px solid var(--primary);
}

@media (prefers-color-scheme: dark) {
    :root { --primary: #60a5fa; }
}

@supports (container-type: inline-size) {
    .wrapper { container-type: inline-size; }
}
```

### Step 1: tinycss2 parses into objects

Returns 6 rule objects:
1. QualifiedRule — `:root { --primary: #3b82f6; --gap: 1rem; }`
2. QualifiedRule — `.container { display: grid; ... }`
3. QualifiedRule — `.card { border-radius: 8px; ... }`
4. QualifiedRule — `.card:has(.featured) { ... }`
5. AtRule — `@media (prefers-color-scheme: dark) { ... }`
6. AtRule — `@supports (container-type: inline-size) { ... }`

### Step 2: Extract components

**Declarations** (with block IDs):
```
('--primary', '#3b82f6', ':root', 0)
('--gap', '1rem', ':root', 0)
('display', 'grid', '.container', 1)
('grid-template-columns', 'repeat(3, 1fr)', '.container', 1)
('gap', 'var(--gap)', '.container', 1)
('max-width', '80vw', '.container', 1)
('border-radius', '8px', '.card', 2)
('box-shadow', '0 2px 4px rgba(0,0,0,0.1)', '.card', 2)
('backdrop-filter', 'blur(10px)', '.card', 2)
('border', '2px solid var(--primary)', '.card:has(.featured)', 3)
('--primary', '#60a5fa', ':root', 4)
('container-type', 'inline-size', '.wrapper', 5)
```

**At-rules**:
```
('media', '(prefers-color-scheme: dark)')
('supports', '(container-type: inline-size)')
```

**Selectors**:
```
[':root', '.container', '.card', '.card:has(.featured)', ':root', '.wrapper']
```

### Step 3: Build matchable text

```
:root { --primary: #3b82f6; --gap: 1rem; }
.container { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--gap); max-width: 80vw; }
.card { border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); backdrop-filter: blur(10px); }
.card:has(.featured) { border: 2px solid var(--primary); }
:root { --primary: #60a5fa; }
.wrapper { container-type: inline-size; }
@media (prefers-color-scheme: dark)
@supports (container-type: inline-size)
```

### Step 4: Detect features

| Pattern matched | What it found | Feature ID |
|---|---|---|
| `r'--[\w-]+'` | `--primary`, `--gap` | `css-variables` |
| `r'var\(--'` | `var(--gap)`, `var(--primary)` | `css-variables` (already found) |
| `r'\d+\.?\d*rem'` | `1rem` | `rem` |
| `r'display\s*:\s*(?:inline-)?grid'` | `display: grid` | `css-grid` |
| `r'grid-template'` | `grid-template-columns` | `css-grid` (already found) |
| `r'\d+\.?\d*vw'` | `80vw` | `viewport-units` |
| `r'border-radius\s*:'` | `border-radius: 8px` | `border-radius` |
| `r'box-shadow\s*:'` | `box-shadow: 0 2px 4px...` | `css-boxshadow` |
| `r'rgba?\('` | `rgba(0,0,0,0.1)` | `css3-colors` |
| `r'backdrop-filter\s*:'` | `backdrop-filter: blur(10px)` | `css-backdrop-filter` |
| `r'blur\('` | `blur(10px)` | `css-filter-function` |
| `r':has\('` | `:has(.featured)` | `css-has` |
| `r'prefers-color-scheme'` | `prefers-color-scheme: dark` | `prefers-color-scheme` |
| `r'@media\s*\('` | `@media (prefers-color-scheme...` | `css-mediaqueries` |
| `r'@supports'` | `@supports (container-type...` | `css-featurequeries` |
| `r'container-type\s*:'` | `container-type: inline-size` | `css-container-queries` |
| `r'#[0-9a-fA-F]{6}'` | `#3b82f6`, `#60a5fa` | `css3-colors` (already found) |

### Final output set:

```python
{
    'css-variables',
    'rem',
    'css-grid',
    'viewport-units',
    'border-radius',
    'css-boxshadow',
    'css3-colors',
    'css-backdrop-filter',
    'css-filter-function',
    'css-has',
    'prefers-color-scheme',
    'css-mediaqueries',
    'css-featurequeries',
    'css-container-queries'
}
```

14 features detected. Each one goes to the Analyzer to check browser support.

---

## Comparison: HTML Parser vs CSS Parser

| Aspect | HTML Parser | CSS Parser |
|--------|------------|------------|
| **Library** | BeautifulSoup4 | tinycss2 |
| **Parsing output** | Tree of element objects | List of rule objects (AST) |
| **Detection method** | Dictionary lookup | Regex pattern matching |
| **Why that method** | Elements have fixed names (`<dialog>`) | Features appear in many forms (`flex`, `flex-direction`, etc.) |
| **Feature maps** | 6 simple dictionaries (key → value) | 20+ category dictionaries (key → patterns list) |
| **Number of features** | ~100 elements + attributes | ~150+ CSS features |
| **Recursion needed?** | No (flat HTML elements) | Yes (nested @-rules: @media inside @supports, etc.) |
| **Block awareness** | Not needed | Yes (block_id tracking for patterns like flexbox-gap) |

---

## Comparison: Our Approach vs Industry Standard (PostCSS)

The industry standard for CSS analysis is **PostCSS** (JavaScript library used by Autoprefixer, Stylelint, etc.). PostCSS uses pure AST with **no regex**:

```javascript
// PostCSS approach (JavaScript)
root.walkDecls('display', decl => {
    if (decl.value === 'grid') features.add('css-grid');
});
root.walkAtRules('media', rule => {
    features.add('css-mediaqueries');
});
```

Our approach uses **tinycss2 + regex** because:
- PostCSS is JavaScript-only (we're Python)
- tinycss2 is a lower-level parser (gives us tokens, not high-level methods like `walkDecls`)
- We need `_build_matchable_text()` to bridge tinycss2's lower-level output to regex matching

Our hybrid approach: **tinycss2 handles the structural parsing** (understanding where blocks start/end, what's a selector, what's a declaration) → **regex handles the feature detection** (matching patterns within the clean text).

---

## Key Points to Remember

1. **tinycss2** does the CSS parsing. We don't parse CSS ourselves.
2. tinycss2 turns CSS text into AST objects (QualifiedRule, AtRule, Declaration) that we walk through.
3. **Feature maps** are Python dictionaries in `css_feature_maps.py` with regex patterns. They say "if this pattern matches, it's this Can I Use feature."
4. The parser runs a **4-step flow**: parse → extract → build text → detect features.
5. **Regex** is needed because CSS features can appear in many forms (unlike HTML elements with fixed names).
6. **Raw strings** (`r'...'`) are always used for regex to prevent Python from misinterpreting backslashes.
7. **block_id** tracking keeps declarations grouped by their original `{ }` block, so patterns like flexbox-gap work correctly.
8. **Recursion** handles nested @-rules (`@media` inside `@supports` inside `@layer`, etc.).
9. **`@font-face`** is a special case — it has declarations directly (not nested rules like `@media`).
10. **Custom rules** can extend the parser. They get merged into the feature dictionary before detection starts.
11. **Unrecognized patterns** act as a safety net, flagging CSS properties that don't match any known feature.
12. The output is a **set of Can I Use feature IDs** that goes to the Analyzer next.
