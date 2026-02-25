# JavaScript Parser - How It Works

## What is the JS Parser's Job?

Same as HTML and CSS parsers: take a JavaScript file, read through it, and find all the web features that might have browser compatibility issues.

For example, if your JS uses `fetch()`, that's a feature some older browsers don't support. If it uses `const`, that's another feature. The parser needs to find them.

Basic things like `var`, `function`, `if/else`, `for` loops are NOT checked because they work in every browser. The parser only looks for features that might have issues.

---

## The Two Main Files

| File | What it contains |
|------|--------------------|
| `src/parsers/js_parser.py` | The parser logic (the code that searches through JavaScript) |
| `src/parsers/js_feature_maps.py` | The feature maps / dictionaries (the data that says what to look for) |

---

## Why JavaScript is the Hardest to Parse

JavaScript is much harder than HTML or CSS because:

1. **Same syntax, different meaning** — `entries()` could be `Object.entries()` (feature!) or `myArray.entries()` (different!) or `getEntries()` (not a feature at all)
2. **Features hidden in syntax** — `?.`, `??`, `=>`, `#field` are syntax features, not names you can search for
3. **278 features to detect** — more than HTML (~100) and CSS (~150)
4. **Comments and strings are tricky** — template literals `` `hello ${code}` `` have real code INSIDE strings

---

## What is tree-sitter?

tree-sitter is a parser library. Just like tinycss2 parses CSS, tree-sitter parses JavaScript.

When we give it JavaScript code, it builds a **tree** (called AST — Abstract Syntax Tree). Every piece of code becomes a "node" in the tree.

```javascript
fetch("https://api.com")
```

tree-sitter builds this tree:
```
call_expression              <-- node TYPE
  ├── identifier: "fetch"    <-- node NAME inside
  └── arguments
       └── string: "https://api.com"
```

Each node has a **type** (what kind of code it is) and sometimes a **name** (the actual word used).

**Important:** tree-sitter is optional. If it's not installed, the parser falls back to regex-only mode.

```python
# At the top of js_parser.py
_TREE_SITTER_AVAILABLE = False
try:
    from tree_sitter_languages import get_language, get_parser
    _JS_LANGUAGE = get_language('javascript')
    _JS_PARSER = get_parser('javascript')
    _TREE_SITTER_AVAILABLE = True
except (ImportError, Exception):
    pass  # Falls back to regex-only
```

---

## The Feature Maps (Dictionaries)

Feature maps are stored in `js_feature_maps.py`. They tell the parser what to look for.

### Regex-Based Feature Maps (7 categories)

These are used by Tier 3 (regex detection). Each feature has:
- `patterns` — list of regex patterns to search for
- `keywords` — GUI display names
- `description` — human-readable name

#### 1. `JS_SYNTAX_FEATURES` — Language syntax (~9 features)

```python
JS_SYNTAX_FEATURES = {
    'arrow-functions': {
        'patterns': [r'=>', r'\(.*?\)\s*=>', r'\w+\s*=>'],
        'keywords': ['=>'],
        'description': 'Arrow functions'
    },
    'const': {
        'patterns': [r'\bconst\s+'],
        'keywords': ['const'],
        'description': 'Const declaration'
    },
    'template-literals': {
        'patterns': [r'`[^`]*\$\{[^}]+\}[^`]*`'],
        'keywords': ['`'],
        'description': 'Template literals'
    },
    'es6-class': {
        'patterns': [r'\bclass\s+\w+'],
        'keywords': ['class'],
        'description': 'ES6 Classes'
    },
    # Also: async-functions, let, es6, rest-parameters, es6-generators
}
```

#### 2. `JS_API_FEATURES` — Browser APIs (~160 features)

The biggest category. Web APIs like fetch, WebSocket, geolocation, etc.

```python
JS_API_FEATURES = {
    'promises': {
        'patterns': [r'\bnew\s+Promise', r'\.then\(', r'\.catch\(', r'Promise\.'],
        'keywords': ['Promise'],
        'description': 'Promises'
    },
    'fetch': {
        'patterns': [r'\bfetch\s*\('],
        'keywords': ['fetch'],
        'description': 'Fetch API'
    },
    'intersectionobserver': {
        'patterns': [r'\bnew\s+IntersectionObserver', r'IntersectionObserver'],
        'keywords': ['IntersectionObserver'],
        'description': 'Intersection Observer'
    },
    'serviceworkers': {
        'patterns': [r'navigator\.serviceWorker', r'serviceWorker\.register\s*\('],
        'keywords': ['serviceWorker'],
        'description': 'Service Workers'
    },
    # ... about 160 more features
}
```

#### 3-7. Smaller categories

```python
JS_ARRAY_METHODS    # 3 features: flat/flatMap, includes, find/findIndex
JS_STRING_METHODS   # 2 features: includes, padStart/padEnd
JS_OBJECT_METHODS   # 3 features: entries, values, observe
JS_STORAGE_APIS     # 2 features: localStorage/sessionStorage, indexedDB
JS_DOM_APIS         # ~40 features: querySelector, classList, dataset, events, etc.
```

#### All merged together

```python
ALL_JS_FEATURES = {
    **JS_SYNTAX_FEATURES,    # ~9
    **JS_API_FEATURES,       # ~160
    **JS_ARRAY_METHODS,      # 3
    **JS_STRING_METHODS,     # 2
    **JS_OBJECT_METHODS,     # 3
    **JS_STORAGE_APIS,       # 2
    **JS_DOM_APIS,           # ~40
}
# Total: ~278 features with regex patterns
```

### AST-Based Feature Maps (6 dictionaries)

These are used by Tier 1 and Tier 2 (tree-sitter detection). They are simple dictionaries — no regex, just name lookups.

#### `AST_SYNTAX_NODE_MAP` — Tier 1 (node types)

Maps tree-sitter node types to feature IDs. These are detected purely by the node's TYPE.

```python
AST_SYNTAX_NODE_MAP = {
    'arrow_function': 'arrow-functions',
    'template_string': 'template-literals',
    'class_declaration': 'es6-class',
    'generator_function': 'es6-generators',
    'yield_expression': 'es6-generators',
    'await_expression': 'async-functions',
    'spread_element': 'es6',
    'rest_pattern': 'rest-parameters',
    # ~10 entries
}
```

Why only ~10? Because most JavaScript features DON'T have a unique node type. All function calls are `call_expression`, all property accesses are `member_expression`, etc.

#### `AST_NEW_EXPRESSION_MAP` — Tier 2a (constructor names)

Maps `new Something()` constructor names to feature IDs.

```python
AST_NEW_EXPRESSION_MAP = {
    'Promise': 'promises',
    'Worker': 'webworkers',
    'WebSocket': 'websockets',
    'IntersectionObserver': 'intersectionobserver',
    'AbortController': 'abortcontroller',
    'Map': 'es6',
    'Set': 'es6',
    # ~50 entries
}
```

When tree-sitter sees `new_expression`, Tier 2 reads the constructor name inside and looks it up here.

#### `AST_CALL_EXPRESSION_MAP` — Tier 2b (function call names)

Maps direct function call names to feature IDs.

```python
AST_CALL_EXPRESSION_MAP = {
    'fetch': 'fetch',
    'requestAnimationFrame': 'requestanimationframe',
    'requestIdleCallback': 'requestidlecallback',
    'atob': 'atob-btoa',
    'btoa': 'atob-btoa',
    'matchMedia': 'matchmedia',
    'getComputedStyle': 'getcomputedstyle',
    # ~20 entries
}
```

When tree-sitter sees `call_expression`, Tier 2 reads the function name and looks it up here.

#### `AST_MEMBER_EXPRESSION_MAP` — Tier 2c (property access chains)

Maps `object.property` chains to feature IDs. This is the **biggest** AST map.

```python
AST_MEMBER_EXPRESSION_MAP = {
    'navigator.geolocation': 'geolocation',
    'navigator.serviceWorker': 'serviceworkers',
    'navigator.clipboard': 'clipboard',
    'navigator.bluetooth': 'web-bluetooth',
    'crypto.subtle': 'cryptography',
    'document.fonts': 'font-loading',
    'performance.now': 'high-resolution-time',
    'Promise.all': 'promises',
    'Object.entries': 'object-entries',
    'CSS.supports': 'css-supports-api',
    # ~90 entries
}
```

When tree-sitter sees `member_expression`, Tier 2 reads both the object name and property name, joins them with `.`, and looks up the result.

#### `AST_IDENTIFIER_MAP` — Tier 2d (standalone names)

Maps standalone identifier names (not part of calls or member access) to feature IDs.

```python
AST_IDENTIFIER_MAP = {
    'SharedArrayBuffer': 'sharedarraybuffer',
    'ReadableStream': 'stream',
    'SpeechRecognition': 'speech-recognition',
    'PublicKeyCredential': 'webauthn',
    'PointerEvent': 'pointer',
    'TouchEvent': 'touch',
    'DOMParser': 'xml-serializer',
    # ~40 entries
}
```

When tree-sitter sees a standalone `identifier` node, Tier 2 reads the name and looks it up here.

#### `AST_OPERATOR_MAP` — Tier 1 helper (operators)

```python
AST_OPERATOR_MAP = {
    '??': 'mdn-javascript_operators_nullish_coalescing',
    '?.': 'mdn-javascript_operators_optional_chaining',
}
```

Used by Tier 1 to detect `??` and `?.` operators.

---

## The Complete Flow

```python
def parse_string(self, js_content: str) -> Set[str]:
    # Reset state
    self.features_found = set()

    # Pre-detection (before removing comments/strings)
    self._detect_directives(js_content)        # "use strict", "use asm"
    self._detect_event_listeners(js_content)   # addEventListener('eventName')

    # Try tree-sitter
    tree = self._parse_with_tree_sitter(js_content)

    if tree is not None:
        # PATH A: tree-sitter available
        self._detect_ast_syntax_features(root_node)    # Tier 1
        self._detect_ast_api_features(root_node)       # Tier 2
        matchable = self._build_matchable_text_from_ast(root_node)  # Clean text
        self._detect_features(matchable)               # Tier 3
    else:
        # PATH B: fallback (regex only)
        cleaned = self._remove_comments_and_strings(js_content)
        self._detect_features(cleaned)                 # Tier 3 only

    return self.features_found
```

Two paths:
- **Path A** (tree-sitter available): All 3 tiers run
- **Path B** (tree-sitter not installed): Only Tier 3 (regex) runs on manually cleaned text

---

## Pre-Detection: Before Anything Else

Some features MUST be detected before we remove comments and strings, because they live INSIDE strings.

### `_detect_directives()` — Directive strings

```javascript
"use strict";    // This IS a string, but it's also a feature
"use asm";       // Same — it's a directive
```

If we remove strings first, these directives disappear. So we detect them first.

```python
def _detect_directives(self, js_content):
    directives = [
        ('use-strict', [r'["\']use strict["\']'], 'ECMAScript 5 Strict Mode'),
        ('asmjs', [r'["\']use asm["\']'], 'asm.js'),
    ]
    for feature_id, patterns, description in directives:
        for pattern in patterns:
            if re.search(pattern, js_content):
                self.features_found.add(feature_id)
                break
```

### `_detect_event_listeners()` — Event names inside strings

```javascript
window.addEventListener('unhandledrejection', handler);
//                       ^^^^^^^^^^^^^^^^^^^^
//                       This event name is inside a STRING
```

After string removal, `'unhandledrejection'` disappears. But it tells us the code uses the `unhandledrejection` event (a browser feature). So we detect it before string removal.

```python
def _detect_event_listeners(self, js_content):
    event_features = {
        'unhandledrejection': ('unhandledrejection', 'unhandledrejection event'),
        'hashchange': ('hashchange', 'hashchange event'),
        'visibilitychange': ('pagevisibility', 'visibilitychange event'),
        'fullscreenchange': ('fullscreen', 'fullscreenchange event'),
        'gamepadconnected': ('gamepad', 'gamepadconnected event'),
        # ... about 25 event names total
    }

    event_pattern = r'''(?:addEventListener|on)\s*\(\s*['"](\w+)['"]'''
    for match in re.finditer(event_pattern, js_content):
        event_name = match.group(1)
        if event_name in event_features:
            feature_id, description = event_features[event_name]
            self.features_found.add(feature_id)
```

---

## Tier 1: AST Syntax Features (`_detect_ast_syntax_features`)

**What it does:** Walks through every node in the tree and checks its TYPE against `AST_SYNTAX_NODE_MAP`.

**How it works:** Uses a stack-based tree walk (not recursion).

```python
def _detect_ast_syntax_features(self, root_node, source_bytes):
    stack = [root_node]
    while stack:
        node = stack.pop()
        node_type = node.type

        # Simple lookup: is this node type a known feature?
        if node_type in AST_SYNTAX_NODE_MAP:
            feature_id = AST_SYNTAX_NODE_MAP[node_type]
            self._add_ast_feature(feature_id, node_type, feature_id)

        # Special case: const/let declarations
        if node_type == 'lexical_declaration':
            keyword = node.children[0].type  # First child is 'const' or 'let'
            if keyword == 'const':
                self._add_ast_feature('const', 'const', 'Const declaration')
            elif keyword == 'let':
                self._add_ast_feature('let', 'let', 'Let declaration')

        # Special case: optional chaining (?.)
        if node_type in ('member_expression', 'call_expression'):
            for child in node.children:
                if child.type == 'optional_chain':
                    self._add_ast_feature(AST_OPERATOR_MAP['?.'], '?.', 'Optional chaining')

        # Special case: nullish coalescing (??)
        if node_type == 'binary_expression':
            operator_node = node.child_by_field_name('operator')
            if operator_node:
                op_text = source_bytes[operator_node.start_byte:operator_node.end_byte].decode()
                if op_text == '??':
                    self._add_ast_feature(AST_OPERATOR_MAP['??'], '??', 'Nullish coalescing')

        # Special case: private fields (#x)
        if node_type == 'private_property_identifier':
            self._add_ast_feature('mdn-javascript_classes_private_class_fields', '#private', 'Private class fields')

        # Add all children to stack to continue walking
        for child in node.children:
            stack.append(child)
```

### What Tier 1 catches (~10 features)

| Code | Node Type | Feature ID |
|------|-----------|-----------|
| `() => {}` | `arrow_function` | `arrow-functions` |
| `` `hello ${x}` `` | `template_string` | `template-literals` |
| `class Dog {}` | `class_declaration` | `es6-class` |
| `function* gen() {}` | `generator_function` | `es6-generators` |
| `yield value` | `yield_expression` | `es6-generators` |
| `await promise` | `await_expression` | `async-functions` |
| `...array` | `spread_element` | `es6` |
| `...rest` | `rest_pattern` | `rest-parameters` |
| `obj?.name` | `optional_chain` child | optional chaining |
| `x ?? y` | binary_expression with `??` | nullish coalescing |
| `#secret` | `private_property_identifier` | private class fields |
| `const x = 1` | `lexical_declaration` + const child | `const` |
| `let y = 2` | `lexical_declaration` + let child | `let` |

### Why Tier 1 can only catch ~10 features

Because most features DON'T have unique node types:

```javascript
fetch("url")           // type: call_expression
alert("hello")         // type: call_expression
console.log("test")    // type: call_expression
myFunction(42)         // type: call_expression
```

ALL function calls have the SAME type: `call_expression`. Tier 1 can't tell them apart.

---

## Tier 2: AST API Features (`_detect_ast_api_features`)

**What it does:** Walks through every node, but instead of just checking the type, it READS THE NAME inside each node and looks it up in dictionaries.

```python
def _detect_ast_api_features(self, root_node, source_bytes):
    stack = [root_node]
    while stack:
        node = stack.pop()
        node_type = node.type

        # new Something() — read the constructor name
        if node_type == 'new_expression':
            constructor = node.child_by_field_name('constructor')
            if constructor:
                name = source_bytes[constructor.start_byte:constructor.end_byte].decode()
                if name in AST_NEW_EXPRESSION_MAP:
                    feature_id = AST_NEW_EXPRESSION_MAP[name]
                    self._add_ast_feature(feature_id, f'new {name}', feature_id)

        # functionCall() — read the function name
        elif node_type == 'call_expression':
            func_node = node.child_by_field_name('function')
            if func_node:
                func_text = source_bytes[func_node.start_byte:func_node.end_byte].decode()

                # Direct call: fetch()
                if func_text in AST_CALL_EXPRESSION_MAP:
                    feature_id = AST_CALL_EXPRESSION_MAP[func_text]
                    self._add_ast_feature(feature_id, f'{func_text}()', feature_id)

                # Member call: navigator.geolocation.getCurrentPosition()
                if func_node.type == 'member_expression':
                    obj = source_bytes[func_node.child_by_field_name('object').start_byte:...].decode()
                    prop = source_bytes[func_node.child_by_field_name('property').start_byte:...].decode()
                    member_key = f'{obj}.{prop}'
                    if member_key in AST_MEMBER_EXPRESSION_MAP:
                        feature_id = AST_MEMBER_EXPRESSION_MAP[member_key]
                        self._add_ast_feature(feature_id, member_key, feature_id)

        # obj.prop (not a call) — navigator.geolocation, document.hidden
        elif node_type == 'member_expression':
            # (Same logic: read obj.prop, look up in AST_MEMBER_EXPRESSION_MAP)

        # Standalone identifier: SharedArrayBuffer, ReadableStream
        elif node_type == 'identifier':
            name = source_bytes[node.start_byte:node.end_byte].decode()
            if name in AST_IDENTIFIER_MAP:
                feature_id = AST_IDENTIFIER_MAP[name]
                self._add_ast_feature(feature_id, name, feature_id)

        for child in node.children:
            stack.append(child)
```

### Tier 2 example walkthrough

Given this code:
```javascript
const data = await fetch("https://api.com");
const observer = new IntersectionObserver(callback);
navigator.clipboard.readText();
```

Tier 2 walks the tree:

| Node | Node Type | Reads Name | Dictionary | Result |
|------|-----------|-----------|------------|--------|
| `fetch(...)` | `call_expression` | `"fetch"` | `AST_CALL_EXPRESSION_MAP` | Found! `fetch` |
| `new IntersectionObserver(...)` | `new_expression` | `"IntersectionObserver"` | `AST_NEW_EXPRESSION_MAP` | Found! `intersectionobserver` |
| `navigator.clipboard` | `member_expression` | `"navigator.clipboard"` | `AST_MEMBER_EXPRESSION_MAP` | Found! `clipboard` |

### What Tier 2 catches (~200 features)

Any feature whose name is in one of the 4 AST dictionaries:
- ~50 constructor names (`new Promise`, `new Worker`, `new Map`, etc.)
- ~20 function call names (`fetch`, `requestAnimationFrame`, etc.)
- ~90 member expressions (`navigator.geolocation`, `Promise.all`, etc.)
- ~40 standalone identifiers (`SharedArrayBuffer`, `PointerEvent`, etc.)

---

## Building Clean Text from AST (`_build_matchable_text_from_ast`)

Before Tier 3 (regex) runs, we need to remove comments and string content from the code. tree-sitter helps us do this accurately.

**What it does:** Walks the AST and:
- **Comments** → replaced with spaces (keeps line numbers correct)
- **String content** → keep the quotes, remove text between them
- **Template literals** → keep backticks and `${x}` markers, remove text
- **Everything else** → kept as-is

```python
def _build_matchable_text_from_ast(self, root_node, source_bytes):
    replacements = []
    stack = [root_node]

    while stack:
        node = stack.pop()

        if node.type == 'comment':
            # Replace comment with spaces
            comment_text = source_text[node.start_byte:node.end_byte]
            replacement = ''.join('\n' if c == '\n' else ' ' for c in comment_text)
            replacements.append((node.start_byte, node.end_byte, replacement))
            continue  # Don't go deeper

        if node.type == 'string':
            # Keep quotes, remove content: "hello world" → ""
            text = source_text[node.start_byte:node.end_byte]
            quote = text[0]
            replacements.append((node.start_byte, node.end_byte, quote + quote))
            continue

        if node.type == 'template_string':
            # Keep backticks and ${x}, remove text
            # `Hello ${name}!` → `${x}`
            self._process_template_string(node, source_text, replacements)
            continue

        for child in node.children:
            stack.append(child)

    # Apply all replacements to get clean text
    return apply_replacements(source_text, replacements)
```

### Example

Original:
```javascript
// This is a comment
const msg = "hello world";
fetch(`/api/${userId}`);
```

After cleaning:
```javascript

const msg = "";
fetch(`${x}`);
```

Now regex can safely search this text without false positives from comments or strings.

---

## Tier 3: Regex Feature Detection (`_detect_features`)

**What it does:** Takes the clean text and checks every regex pattern from ALL_JS_FEATURES.

```python
def _detect_features(self, js_content):
    for feature_id, feature_info in self._all_features.items():
        patterns = feature_info.get('patterns', [])
        for pattern in patterns:
            if re.search(pattern, js_content):
                self.features_found.add(feature_id)
                break  # Found this feature, move to next
```

This is the same approach as the CSS parser — loop through all features, check each pattern.

### What Tier 3 catches

- **~70 features** not in AST maps
- **Custom rules** added by users
- **Aliased variables** (e.g., `const f = fetch`)
- **Complex patterns** that are easier to express as regex

### Why Tier 3 is needed even with Tiers 1 and 2

1. **Aliases:** `const f = fetch; f(url)` — Tier 2 sees `f()`, not `fetch()`. But the regex `\bfetch\b` still matches the first line.
2. **Custom rules:** Users add their own patterns in `custom_rules.json`. Only regex can run them.
3. **Coverage:** ~70 features don't have AST map entries yet.

---

## Fallback Path (No tree-sitter)

When tree-sitter is NOT installed, the parser uses `_remove_comments_and_strings()` — a manual character-by-character processor.

```python
def _remove_comments_and_strings(self, js_content):
    result = []
    i = 0
    while i < length:
        # Check for // single-line comment
        if js_content[i:i+2] == '//':
            # Skip until end of line
            while i < length and js_content[i] != '\n':
                i += 1
            continue

        # Check for /* multi-line comment */
        if js_content[i:i+2] == '/*':
            i += 2
            while i < length - 1 and js_content[i:i+2] != '*/':
                i += 1
            i += 2
            continue

        # Check for "double-quoted string"
        if js_content[i] == '"':
            result.append('"')  # Keep opening quote
            i += 1
            while i < length:
                if js_content[i] == '\\':
                    i += 2  # Skip escaped character
                elif js_content[i] == '"':
                    result.append('"')  # Keep closing quote
                    i += 1
                    break
                else:
                    i += 1  # Skip string content
            continue

        # Same for 'single-quoted', `template literals`
        # ...

        result.append(js_content[i])  # Keep regular code
        i += 1

    return ''.join(result)
```

This works but is less accurate than tree-sitter because:
- Can get confused by edge cases like regex literals `/pattern/`
- Doesn't understand code structure as deeply
- More prone to false positives/negatives

---

## Unrecognized Pattern Detection (`_find_unrecognized_patterns`)

After all 3 tiers, the parser runs a safety net to find API calls that NONE of our rules matched. This helps find features we might have missed.

```python
def _find_unrecognized_patterns(self, js_content):
    # Find method calls: .methodName(
    method_pattern = r'\.([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('
    found_methods = set(re.findall(method_pattern, js_content))

    # Find global API objects: CapitalizedName.
    global_api_pattern = r'\b([A-Z][a-zA-Z0-9_$]*)\.'
    found_globals = set(re.findall(global_api_pattern, js_content))

    for method in found_methods:
        # Skip basic/universal methods (push, pop, forEach, etc.)
        if method in basic_patterns:
            continue
        # Skip already-matched methods
        if method in self._matched_apis:
            continue
        # Skip common programming prefixes (get, set, handle, etc.)
        # Skip short names (< 4 chars)
        # If it doesn't match ANY feature pattern → add to unrecognized
        self.unrecognized_patterns.add(f"method: .{method}()")
```

The method maintains 3 large filter lists:
- **`basic_patterns`** (~500 entries): universal JS methods like `push`, `pop`, `forEach`, `toString`
- **`common_prefixes`** (~180 entries): programming verbs like `get`, `set`, `handle`, `create`
- **`common_globals`** (~150 entries): React component names like `Loading`, `Button`, `App`

These filters prevent false positives — we don't want to flag `Button.render()` as an unrecognized API.

---

## Custom Rules

Users can add their own detection rules in `custom_rules.json`:

```json
{
  "javascript": {
    "some-feature": {
      "patterns": ["myCompanyAPI\\.track"],
      "description": "Company tracking API"
    }
  }
}
```

At initialization, custom rules get merged with built-in rules:

```python
def __init__(self):
    self._all_features = {**ALL_JS_FEATURES, **get_custom_js_rules()}
```

Custom rules are always regex patterns — they run in Tier 3.

---

## The Two Paths (Complete Flow Diagram)

```
JavaScript text
    |
    v
Pre-detection (on ORIGINAL text, before any cleaning):
    |-- _detect_directives()       → "use strict", "use asm"
    |-- _detect_event_listeners()  → addEventListener('eventName')
    |
    v
Try tree-sitter: _parse_with_tree_sitter()
    |
    ├── SUCCESS (tree-sitter available) ─── PATH A
    |   |
    |   ├── Tier 1: _detect_ast_syntax_features()
    |   |   Walk tree, check node TYPES
    |   |   arrow_function → 'arrow-functions'
    |   |   template_string → 'template-literals'
    |   |   optional_chain → optional chaining
    |   |   Catches ~10 features
    |   |
    |   ├── Tier 2: _detect_ast_api_features()
    |   |   Walk tree, READ NAMES inside nodes
    |   |   new Promise → 'promises'
    |   |   fetch() → 'fetch'
    |   |   navigator.clipboard → 'clipboard'
    |   |   Catches ~200 features
    |   |
    |   ├── Build clean text: _build_matchable_text_from_ast()
    |   |   Comments → spaces
    |   |   String content → removed (quotes kept)
    |   |   Template text → removed (backticks + ${x} kept)
    |   |
    |   └── Tier 3: _detect_features(clean_text)
    |       Regex patterns on clean text
    |       Catches ~70 remaining features + custom rules
    |
    └── FAILURE (tree-sitter not installed) ─── PATH B
        |
        ├── _remove_comments_and_strings()
        |   Manual character-by-character cleaning
        |
        └── Tier 3: _detect_features(clean_text)
            Regex patterns only (all ~278 features checked)
    |
    v
Final: _find_unrecognized_patterns()
    Safety net — finds API calls that no rule matched
    |
    v
Output: Set of Can I Use feature IDs
{'fetch', 'promises', 'arrow-functions', 'const', 'intersectionobserver', ...}
    |
    v
Goes to the Analyzer for browser compatibility checking
```

---

## Concrete Example

Given this JavaScript:

```javascript
"use strict";

const fetchData = async () => {
    const response = await fetch("https://api.example.com/data");
    const data = await response.json();
    return data;
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
});

navigator.clipboard.readText().then(text => console.log(text));

window.addEventListener('hashchange', () => {
    console.log(location.hash);
});
```

### Pre-detection finds:

| What | Method | Feature ID |
|------|--------|-----------|
| `"use strict"` | `_detect_directives()` | `use-strict` |
| `addEventListener('hashchange')` | `_detect_event_listeners()` | `hashchange` |

### Tier 1 finds:

| What | Node Type | Feature ID |
|------|-----------|-----------|
| `() => { ... }` | `arrow_function` | `arrow-functions` |
| `await fetch(...)` | `await_expression` | `async-functions` |
| `...` in forEach callback | `arrow_function` | `arrow-functions` (already found) |

### Tier 2 finds:

| What | Dictionary | Feature ID |
|------|-----------|-----------|
| `fetch(...)` | `AST_CALL_EXPRESSION_MAP` | `fetch` |
| `new IntersectionObserver(...)` | `AST_NEW_EXPRESSION_MAP` | `intersectionobserver` |
| `navigator.clipboard` | `AST_MEMBER_EXPRESSION_MAP` | `clipboard` |

### Tier 1 also catches (special cases):

| What | How | Feature ID |
|------|-----|-----------|
| `const fetchData` | lexical_declaration + const child | `const` |
| `async () =>` | checks for 'async' keyword before arrow function | `async-functions` (already found) |

### Tier 3 finds (on clean text):

| What | Pattern | Feature ID |
|------|---------|-----------|
| `.classList` | `r'\.classList'` | `classlist` |
| `.then(...)` | `r'\.then\('` | `promises` |
| `console.log(...)` | `r'console\.log'` | `console-basic` |

### Final output:

```python
{
    'use-strict', 'hashchange', 'arrow-functions', 'async-functions',
    'const', 'fetch', 'intersectionobserver', 'clipboard',
    'classlist', 'promises', 'console-basic'
}
```

This set goes to the Analyzer, which checks each feature against the Can I Use database.

---

## Key Points to Remember

1. **tree-sitter** parses JavaScript into a tree (AST). Each node has a TYPE and sometimes a NAME.
2. **3 tiers** detect features at different levels:
   - **Tier 1** — checks node TYPES (catches ~10 features with unique types)
   - **Tier 2** — reads node NAMES, looks up in dictionaries (catches ~200 features)
   - **Tier 3** — runs regex on clean text (catches remaining ~70 + custom rules)
3. **Pre-detection** happens BEFORE cleaning: directives (`"use strict"`) and event listener names live inside strings.
4. **Two paths**: With tree-sitter (all 3 tiers) or without (regex only).
5. **Feature maps** are in `js_feature_maps.py`: 7 regex categories merged into `ALL_JS_FEATURES`, plus 6 AST dictionaries.
6. **Custom rules** can extend detection via `custom_rules.json`. They run as regex in Tier 3.
7. **Unrecognized patterns** are flagged as a safety net (with large filter lists to avoid false positives).
8. **The output** is a set of Can I Use feature IDs, same as HTML and CSS parsers.

---

## Comparison: All 3 Parsers

| | HTML Parser | CSS Parser | JS Parser |
|---|---|---|---|
| **Structure tool** | BeautifulSoup | tinycss2 | tree-sitter |
| **Detection method** | Dictionary lookups | Regex on clean text | 3 tiers (AST types + AST names + regex) |
| **Features detected** | ~100 | ~150 | ~278 |
| **Feature maps file** | `html_feature_maps.py` | `css_feature_maps.py` | `js_feature_maps.py` |
| **Complexity** | Simplest | Medium | Most complex |
| **Why?** | HTML features are exact names | CSS features are text patterns | JS has syntax + API + name features |
| **Pre-detection** | None needed | None needed | Directives + event listeners |
| **Fallback** | None (BS4 always works) | None (tinycss2 always works) | Regex-only when tree-sitter missing |
| **Custom rules** | Merged into element/attribute dicts | Merged into ALL_CSS_FEATURES | Merged into ALL_JS_FEATURES |
