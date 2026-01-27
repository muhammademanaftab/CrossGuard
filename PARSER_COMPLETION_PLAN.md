# Cross Guard - Complete Parser Implementation Plan

## Executive Summary

This document outlines the complete plan to achieve **100% Can I Use database coverage** across all three parsers (HTML, CSS, JavaScript).

### Current Status Overview

| Parser | Current Coverage | Missing Features | Effort Required |
|--------|-----------------|------------------|-----------------|
| **CSS** | 92.9% (169/182) | 4 font formats | LOW (1 hour) |
| **JS** | 83.3% (249/299) | 50 features | MEDIUM (1-2 days) |
| **HTML** | 85%* (74/88) | 14 features | LOW (2-3 hours) |

*Note: HTML has 148 features in CIU, but 60 are JS APIs that belong in JS parser.

---

## PHASE 1: CSS Parser Completion

### 1.1 Current State
- **Total CSS features in Can I Use:** 182
- **Currently mapped:** 169 (92.9%)
- **Missing:** 4 font format features

### 1.2 Missing Features (4 total)

| Feature ID | Title | Detection Pattern |
|------------|-------|-------------------|
| `colr` | COLR/CPAL(v0) Font Formats | `format('colr')` |
| `colr-v1` | COLR/CPAL(v1) Font Formats | `format('colr-v1')` |
| `eot` | EOT Embedded OpenType | `format('embedded-opentype')`, `.eot` |
| `svg-fonts` | SVG fonts | `format('svg')`, `.svg#` |

### 1.3 Implementation

**File to modify:** `src/parsers/css_feature_maps.py`

Add to `CSS_TYPOGRAPHY`:
```python
# Font format features
'colr': {
    'patterns': [r'format\s*\(\s*["\']colr["\']'],
    'keywords': [],
    'description': 'COLR/CPAL Font Formats'
},
'colr-v1': {
    'patterns': [r'format\s*\(\s*["\']colr-v1["\']'],
    'keywords': [],
    'description': 'COLR/CPAL(v1) Font Formats'
},
'eot': {
    'patterns': [r'format\s*\(\s*["\']embedded-opentype["\']', r'\.eot["\'\)]'],
    'keywords': [],
    'description': 'EOT - Embedded OpenType fonts'
},
'svg-fonts': {
    'patterns': [r'format\s*\(\s*["\']svg["\']', r'\.svg#'],
    'keywords': [],
    'description': 'SVG fonts'
},
```

### 1.4 Tests Required
- Test `@font-face` with each format
- Test URL patterns with extensions
- Test case variations

**Estimated time:** 1 hour

---

## PHASE 2: HTML Parser Completion

### 2.1 Current State
- **Total HTML5/DOM features in Can I Use:** 148
- **Features detectable in HTML:** ~88 (60 are JS APIs)
- **Currently mapped:** 74 (84% of HTML-detectable)
- **Missing HTML-detectable:** 14 features

### 2.2 Missing Features (14 total)

#### 2.2.1 Input Types - Map to Combined Feature
Currently we have separate `input-email`, `input-tel`, `input-url`. CIU has them combined.

| Our Feature | CIU Feature | Action |
|-------------|-------------|--------|
| `input-email` | `input-email-tel-url` | Add alias mapping |
| `input-tel` | `input-email-tel-url` | Add alias mapping |
| `input-url` | `input-email-tel-url` | Add alias mapping |

#### 2.2.2 New Elements to Add

| Feature ID | Element/Attribute | Detection Pattern |
|------------|-------------------|-------------------|
| `portals` | `<portal>` element | `soup.find_all('portal')` |

#### 2.2.3 New Attributes to Add

| Feature ID | Attribute | Detection Pattern |
|------------|-----------|-------------------|
| `hashchange` | `onhashchange` | Attribute detection |
| `offline-apps` | `manifest` on html | `<html manifest="...">` |

#### 2.2.4 Event Attributes to Add

| Feature ID | Attributes | Detection Pattern |
|------------|------------|-------------------|
| `touch` | `ontouchstart`, `ontouchmove`, `ontouchend`, `ontouchcancel` | Attribute detection |
| `pointer` | `onpointerdown`, `onpointermove`, `onpointerup`, etc. | Attribute detection |
| `focusin-focusout-events` | `onfocusin`, `onfocusout` | Attribute detection |

#### 2.2.5 Deprecated Features (optional)

| Feature ID | What | Notes |
|------------|------|-------|
| `imports` | `<link rel="import">` | Deprecated, but still in CIU |
| `style-scoped` | `<style scoped>` | Removed from spec |

#### 2.2.6 Features to Keep (newer than CIU database)

These are valid features we already have that aren't in our CIU version:
- `inert` - Valid HTML attribute
- `popover` - Popover API
- `img-decoding-async` - decoding attribute
- `input-enterkeyhint` - enterkeyhint attribute

### 2.3 Implementation

**File to modify:** `src/parsers/html_feature_maps.py`

```python
# Add to HTML_ELEMENTS
'portal': 'portals',

# Add to HTML_ATTRIBUTES
'onhashchange': 'hashchange',
'manifest': 'offline-apps',

# Touch events
'ontouchstart': 'touch',
'ontouchmove': 'touch',
'ontouchend': 'touch',
'ontouchcancel': 'touch',

# Pointer events
'onpointerdown': 'pointer',
'onpointermove': 'pointer',
'onpointerup': 'pointer',
'onpointercancel': 'pointer',
'onpointerenter': 'pointer',
'onpointerleave': 'pointer',
'onpointerover': 'pointer',
'onpointerout': 'pointer',
'ongotpointercapture': 'pointer',
'onlostpointercapture': 'pointer',

# Focus events
'onfocusin': 'focusin-focusout-events',
'onfocusout': 'focusin-focusout-events',

# Add to HTML_ATTRIBUTE_VALUES
('rel', 'import'): 'imports',
```

**File to modify:** `src/parsers/html_parser.py`

Add detection for:
- `<html manifest="...">` detection
- `<style scoped>` detection

### 2.4 Tests Required
- Test portal element
- Test all touch event attributes
- Test all pointer event attributes
- Test manifest attribute
- Test scoped style

**Estimated time:** 2-3 hours

---

## PHASE 3: JavaScript Parser Completion

### 3.1 Current State
- **Total JS/DOM features in Can I Use:** 299
- **Currently mapped:** 249 (83.3%)
- **Missing:** 50 features

### 3.2 Missing Features by Category

#### 3.2.1 HIGH PRIORITY - DOM APIs from HTML Parser (18 features)

These are currently "missing" from HTML but should be in JS parser:

| Feature ID | Detection Pattern | Description |
|------------|-------------------|-------------|
| `addeventlistener` | `addEventListener` | Event listener API |
| `classlist` | `classList` | DOMTokenList API |
| `queryselector` | `querySelector`, `querySelectorAll` | DOM selectors |
| `getelementsbyclassname` | `getElementsByClassName` | DOM method |
| `element-closest` | `.closest(` | Element.closest() |
| `element-from-point` | `elementFromPoint`, `elementsFromPoint` | Document method |
| `matches-selector` | `.matches(` | Element.matches() |
| `textcontent` | `textContent` | Node.textContent |
| `innertext` | `innerText` | HTMLElement.innerText |
| `childnode-remove` | `.remove()` | ChildNode.remove() |
| `insert-adjacent` | `insertAdjacentElement`, `insertAdjacentText`, `insertAdjacentHTML` | DOM methods |
| `dom-manip-convenience` | `append`, `prepend`, `before`, `after`, `replaceWith` | DOM convenience |
| `documenthead` | `document.head` | Document.head |
| `comparedocumentposition` | `compareDocumentPosition` | Node method |
| `domcontentloaded` | `DOMContentLoaded` | Event |
| `dispatchevent` | `dispatchEvent` | EventTarget method |
| `customevent` | `CustomEvent` | Constructor |
| `rellist` | `relList` | DOMTokenList on links |

#### 3.2.2 HIGH PRIORITY - Observer APIs (4 features)

| Feature ID | Detection Pattern | Description |
|------------|-------------------|-------------|
| `mutationobserver` | `MutationObserver` | DOM mutation observer |
| `intersectionobserver` | `IntersectionObserver` | Intersection observer |
| `intersectionobserver-v2` | `IntersectionObserver` + `trackVisibility` | V2 features |
| `resizeobserver` | `ResizeObserver` | Resize observer |

#### 3.2.3 HIGH PRIORITY - Event APIs (8 features)

| Feature ID | Detection Pattern | Description |
|------------|-------------------|-------------|
| `passive-event-listener` | `passive: true`, `{ passive` | Passive listeners |
| `once-event-listener` | `once: true`, `{ once` | Once listeners |
| `touch` | `touchstart`, `touchmove`, `TouchEvent` | Touch events |
| `pointer` | `pointerdown`, `PointerEvent` | Pointer events |
| `focusin-focusout-events` | `focusin`, `focusout` | Focus events |
| `auxclick` | `auxclick` | Auxiliary click |
| `hashchange` | `hashchange`, `onhashchange` | Hash change event |
| `beforeafterprint` | `beforeprint`, `afterprint` | Print events |

#### 3.2.4 MEDIUM PRIORITY - Keyboard Events (6 features)

| Feature ID | Detection Pattern | Description |
|------------|-------------------|-------------|
| `keyboardevent-key` | `.key`, `KeyboardEvent` + `key` | KeyboardEvent.key |
| `keyboardevent-code` | `.code`, `KeyboardEvent` + `code` | KeyboardEvent.code |
| `keyboardevent-location` | `.location` | KeyboardEvent.location |
| `keyboardevent-which` | `.which` | KeyboardEvent.which (deprecated) |
| `keyboardevent-charcode` | `.charCode` | KeyboardEvent.charCode (deprecated) |
| `keyboardevent-getmodifierstate` | `getModifierState` | Modifier state method |

#### 3.2.5 MEDIUM PRIORITY - Scroll APIs (4 features)

| Feature ID | Detection Pattern | Description |
|------------|-------------------|-------------|
| `element-scroll-methods` | `scrollTo`, `scrollBy`, `scroll` | Element scroll methods |
| `scrollintoview` | `scrollIntoView` | Element.scrollIntoView() |
| `scrollintoviewifneeded` | `scrollIntoViewIfNeeded` | Non-standard scroll |
| `document-scrollingelement` | `scrollingElement` | document.scrollingElement |

#### 3.2.6 MEDIUM PRIORITY - Other DOM APIs (10 features)

| Feature ID | Detection Pattern | Description |
|------------|-------------------|-------------|
| `dom-range` | `createRange`, `Range` | DOM Range API |
| `dommatrix` | `DOMMatrix`, `DOMPoint` | Geometry APIs |
| `getcomputedstyle` | `getComputedStyle` | Window method |
| `matchmedia` | `matchMedia` | Media query JS API |
| `devicepixelratio` | `devicePixelRatio` | Window property |
| `input-selection` | `selectionStart`, `selectionEnd`, `setSelectionRange` | Input selection |
| `mutation-events` | `DOMSubtreeModified`, `DOMNodeInserted` | Mutation events (deprecated) |
| `page-transition-events` | `pageshow`, `pagehide` | Page transition |
| `history` | `history.pushState`, `history.replaceState` | History API |
| `registerprotocolhandler` | `registerProtocolHandler` | Protocol handler |

### 3.3 Implementation

**File to modify:** `src/parsers/js_feature_maps.py`

```python
# DOM API features
JS_DOM_APIS = {
    'addeventlistener': {
        'patterns': [r'\baddEventListener\s*\('],
        'description': 'EventTarget.addEventListener()'
    },
    'classlist': {
        'patterns': [r'\.classList\b'],
        'description': 'classList (DOMTokenList)'
    },
    'queryselector': {
        'patterns': [r'\bquerySelector\s*\(', r'\bquerySelectorAll\s*\('],
        'description': 'querySelector/querySelectorAll'
    },
    # ... etc
}

# Observer APIs
JS_OBSERVERS = {
    'mutationobserver': {
        'patterns': [r'\bMutationObserver\b'],
        'description': 'Mutation Observer'
    },
    'intersectionobserver': {
        'patterns': [r'\bIntersectionObserver\b'],
        'description': 'Intersection Observer'
    },
    'resizeobserver': {
        'patterns': [r'\bResizeObserver\b'],
        'description': 'Resize Observer'
    },
}

# Event features
JS_EVENTS = {
    'passive-event-listener': {
        'patterns': [r'passive\s*:\s*true', r'\{\s*passive\b'],
        'description': 'Passive event listeners'
    },
    'once-event-listener': {
        'patterns': [r'once\s*:\s*true', r'\{\s*once\b'],
        'description': 'Once event listeners'
    },
    'touch': {
        'patterns': [r'\btouchstart\b', r'\btouchmove\b', r'\bTouchEvent\b'],
        'description': 'Touch events'
    },
    'pointer': {
        'patterns': [r'\bpointerdown\b', r'\bPointerEvent\b', r'\bpointermove\b'],
        'description': 'Pointer events'
    },
}

# Keyboard events
JS_KEYBOARD = {
    'keyboardevent-key': {
        'patterns': [r'\.key\b', r'KeyboardEvent.*key'],
        'description': 'KeyboardEvent.key'
    },
    'keyboardevent-code': {
        'patterns': [r'\.code\b', r'KeyboardEvent.*code'],
        'description': 'KeyboardEvent.code'
    },
}

# Scroll APIs
JS_SCROLL = {
    'element-scroll-methods': {
        'patterns': [r'\.scrollTo\s*\(', r'\.scrollBy\s*\(', r'\.scroll\s*\('],
        'description': 'Element scroll methods'
    },
    'scrollintoview': {
        'patterns': [r'\.scrollIntoView\s*\('],
        'description': 'Element.scrollIntoView()'
    },
}
```

**File to modify:** `src/parsers/js_parser.py`

Add detection loops for all new categories.

### 3.4 Tests Required
- Test each DOM API pattern
- Test observer constructors
- Test event listener options
- Test keyboard event properties
- Test scroll methods
- Test edge cases (false positives in strings/comments)

**Estimated time:** 1-2 days

---

## PHASE 4: Validation & Testing

### 4.1 Create Validation Script

Create a script to verify all feature IDs exist in Can I Use:

```python
# scripts/validate_feature_ids.py
def validate_all_parsers():
    """Verify all mapped feature IDs exist in Can I Use database."""
    # Load CIU database
    # Load all feature maps
    # Compare and report mismatches
```

### 4.2 Test Coverage Goals

| Parser | Target Coverage |
|--------|----------------|
| CSS | 95%+ |
| JS | 95%+ |
| HTML | 95%+ |

### 4.3 Test File Structure

```
tests/
├── conftest.py
├── parsers/
│   ├── test_html_parser.py    (EXISTS - 173 tests)
│   ├── test_css_parser.py     (CREATE)
│   └── test_js_parser.py      (CREATE)
└── validation/
    └── test_feature_ids.py    (CREATE)
```

---

## Implementation Timeline

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|--------------|
| 1 | CSS Parser Completion | 1 hour | None |
| 2 | HTML Parser Completion | 2-3 hours | None |
| 3 | JS Parser Completion | 1-2 days | None |
| 4 | Validation & Testing | 1 day | Phases 1-3 |

**Total estimated time: 2-3 days**

---

## Final Coverage Goals

After implementation:

| Parser | Before | After | Change |
|--------|--------|-------|--------|
| CSS | 92.9% | 100% | +7.1% |
| HTML | 85% | 100% | +15% |
| JS | 83.3% | 100% | +16.7% |

---

## Files to Modify

### Phase 1 (CSS)
- `src/parsers/css_feature_maps.py`

### Phase 2 (HTML)
- `src/parsers/html_feature_maps.py`
- `src/parsers/html_parser.py`

### Phase 3 (JS)
- `src/parsers/js_feature_maps.py`
- `src/parsers/js_parser.py`

### Phase 4 (Testing)
- `tests/parsers/test_css_parser.py` (new)
- `tests/parsers/test_js_parser.py` (new)
- `tests/validation/test_feature_ids.py` (new)

---

## Success Criteria

1. [ ] All CSS font format features added and tested
2. [ ] All HTML elements, attributes, and events added and tested
3. [ ] All JS DOM APIs, observers, and events added and tested
4. [ ] Validation script confirms all feature IDs exist in Can I Use
5. [ ] 95%+ test coverage on all parsers
6. [ ] No false positives (features detected in comments/strings)
7. [ ] All 173+ existing HTML tests still pass

---

## Notes

### Features Intentionally NOT Added

1. **HTTP-only features** (CSP headers, CORS headers) - Not detectable in code
2. **Server-side features** (Client hints) - Require server config
3. **Media format features** (Video codecs, image formats) - Not CSS/JS/HTML
4. **Deprecated V0 specs** (old Shadow DOM, old Custom Elements) - Use V1 instead

### Features We Have Beyond Can I Use

Our parsers include some features newer than the CIU database version:
- `inert` attribute
- `popover` API
- `img-decoding-async`
- `input-enterkeyhint`

These are valid and should be kept.
