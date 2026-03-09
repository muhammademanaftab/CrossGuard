"""Consolidated AST-specific tests for the JavaScript parser.

Tests tree-sitter AST detection (syntax nodes, API detection, member expressions),
false positive prevention (comments/strings), and regex fallback behavior.
"""

import pytest
from unittest.mock import patch
from src.parsers.js_parser import JavaScriptParser, _TREE_SITTER_AVAILABLE


# --- Tier 1: AST Syntax Node Detection ---

AST_SYNTAX_FEATURES = [
    pytest.param("const fn = () => 1;", "arrow-functions", id="arrow-simple"),
    pytest.param("const fn = (x) => { return x; };", "arrow-functions", id="arrow-body"),
    pytest.param("[1,2].map(x => x * 2);", "arrow-functions", id="arrow-callback"),
    pytest.param("const s = `hello ${name}`;", "template-literals", id="template-expr"),
    pytest.param("const s = html`<div>${x}</div>`;", "template-literals", id="tagged-template"),
    pytest.param("class Foo {}", "es6-class", id="class-decl"),
    pytest.param("class Bar extends Foo {}", "es6-class", id="class-extends"),
    pytest.param("const Foo = class {};", "es6-class", id="class-expr"),
    pytest.param("function* gen() { yield 1; }", "es6-generators", id="generator"),
    pytest.param("function* g() { yield 42; }", "es6-generators", id="yield"),
    pytest.param("const x = 1;", "const", id="const"),
    pytest.param("let y = 2;", "let", id="let"),
    pytest.param("foo(...args);", "es6", id="spread-call"),
    pytest.param("const arr = [...a, ...b];", "es6", id="spread-array"),
    pytest.param("function foo(...args) {}", "rest-parameters", id="rest-param"),
    pytest.param("async function fetchData() {}", "async-functions", id="async-fn"),
    pytest.param(
        "async function f() { await fetch('/api'); }",
        "async-functions", id="await-expr"
    ),
    pytest.param("const fn = async () => { await x; };", "async-functions", id="async-arrow"),
    pytest.param(
        "const x = a ?? b;",
        "mdn-javascript_operators_nullish_coalescing", id="nullish-coalescing"
    ),
    pytest.param(
        "const x = obj?.prop;",
        "mdn-javascript_operators_optional_chaining", id="optional-chain-prop"
    ),
    pytest.param(
        "obj?.method();",
        "mdn-javascript_operators_optional_chaining", id="optional-chain-call"
    ),
]


@pytest.mark.parametrize("js_input,expected_id", AST_SYNTAX_FEATURES)
def test_ast_syntax(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


def test_ast_private_class_field(parse_features):
    """Private class fields need multiline input."""
    js = """
    class Foo {
        #value = 42;
        get() { return this.#value; }
    }
    """
    assert "mdn-javascript_classes_private_class_fields" in parse_features(js)


def test_ast_const_destructuring_detects_es6(parse_features):
    """Destructuring with const triggers ES6 detection."""
    assert "es6" in parse_features("const { a, b } = obj;")


# --- Tier 2: AST API Detection (new expressions, calls, members, identifiers) ---

AST_NEW_EXPRESSIONS = [
    pytest.param("new Promise((resolve) => resolve());", "promises", id="promise"),
    pytest.param("const w = new Worker('worker.js');", "webworkers", id="worker"),
    pytest.param("const ws = new WebSocket('ws://host');", "websockets", id="websocket"),
    pytest.param("new IntersectionObserver(cb);", "intersectionobserver", id="intersection"),
    pytest.param("new MutationObserver(cb);", "mutationobserver", id="mutation"),
    pytest.param("new ResizeObserver(cb);", "resizeobserver", id="resize"),
    pytest.param("new BroadcastChannel('ch');", "broadcastchannel", id="broadcast"),
    pytest.param("const ctrl = new AbortController();", "abortcontroller", id="abort"),
    pytest.param("const u = new URL('https://example.com');", "url", id="url"),
    pytest.param("const enc = new TextEncoder();", "textencoder", id="textencoder"),
    pytest.param("const dec = new TextDecoder();", "textencoder", id="textdecoder"),
    pytest.param("new Blob(['data']);", "blobbuilder", id="blob"),
    pytest.param("new CustomEvent('test');", "customevent", id="customevent"),
    pytest.param("const m = new Map();", "es6", id="map"),
    pytest.param("const s = new Set();", "es6", id="set"),
]


@pytest.mark.parametrize("js_input,expected_id", AST_NEW_EXPRESSIONS)
def test_ast_new_expressions(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


AST_CALL_EXPRESSIONS = [
    pytest.param("fetch('/api/data');", "fetch", id="fetch"),
    pytest.param("requestAnimationFrame(loop);", "requestanimationframe", id="raf"),
    pytest.param("requestIdleCallback(cb);", "requestidlecallback", id="ric"),
    pytest.param("const x = atob(encoded);", "atob-btoa", id="atob"),
    pytest.param("const x = btoa(data);", "atob-btoa", id="btoa"),
    pytest.param("matchMedia('(max-width: 600px)');", "matchmedia", id="matchmedia"),
    pytest.param("createImageBitmap(img);", "createimagebitmap", id="createimagebitmap"),
]


@pytest.mark.parametrize("js_input,expected_id", AST_CALL_EXPRESSIONS)
def test_ast_call_expressions(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


AST_MEMBER_EXPRESSIONS = [
    pytest.param(
        "navigator.geolocation.getCurrentPosition(cb);",
        "geolocation", id="geolocation"
    ),
    pytest.param(
        "navigator.serviceWorker.register('/sw.js');",
        "serviceworkers", id="serviceworker"
    ),
    pytest.param("navigator.clipboard.writeText('hi');", "clipboard", id="clipboard"),
    pytest.param(
        "crypto.subtle.encrypt(algo, key, data);",
        "cryptography", id="cryptography"
    ),
    pytest.param("if (document.hidden) { /* pause */ }", "pagevisibility", id="pagevisibility"),
    pytest.param("history.pushState({}, '', '/new');", "history", id="history"),
    pytest.param("const t = performance.now();", "high-resolution-time", id="perf-now"),
    pytest.param("Promise.all([p1, p2]);", "promises", id="promise-all"),
    pytest.param("Object.entries(obj);", "object-entries", id="object-entries"),
    pytest.param("Object.values(obj);", "object-values", id="object-values"),
    pytest.param("navigator.share({ title: 'Hi' });", "web-share", id="web-share"),
    pytest.param(
        "const adapter = navigator.gpu.requestAdapter();",
        "webgpu", id="webgpu"
    ),
    pytest.param("CSS.supports('display', 'grid');", "css-supports-api", id="css-supports"),
]


@pytest.mark.parametrize("js_input,expected_id", AST_MEMBER_EXPRESSIONS)
def test_ast_member_expressions(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


AST_IDENTIFIERS = [
    pytest.param("const buf = SharedArrayBuffer;", "sharedarraybuffer", id="sharedarraybuffer"),
    pytest.param("const s = new ReadableStream({});", "stream", id="readable-stream"),
    pytest.param("const s = new WritableStream({});", "stream", id="writable-stream"),
    pytest.param("const sr = new SpeechRecognition();", "speech-recognition", id="speech"),
    pytest.param(
        "PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();",
        "webauthn", id="webauthn"
    ),
    pytest.param("const parser = new DOMParser();", "xml-serializer", id="domparser"),
    pytest.param("new PointerEvent('pointerdown');", "pointer", id="pointer"),
]


@pytest.mark.parametrize("js_input,expected_id", AST_IDENTIFIERS)
def test_ast_identifiers(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- False Positive Prevention (comments & strings) ---

@pytest.mark.skipif(not _TREE_SITTER_AVAILABLE, reason="tree-sitter not available")
class TestFalsePositiveComments:
    """Features inside comments should not be detected."""

    FP_COMMENT_CASES = [
        pytest.param(
            "// We might use navigator.bluetooth later\nvar x = 1;",
            "web-bluetooth", id="single-line"
        ),
        pytest.param(
            "/* TODO: add navigator.geolocation support */\nvar x = 1;",
            "geolocation", id="multi-line"
        ),
        pytest.param(
            "/* new WebSocket('ws://host') */\nvar x = 1;",
            "websockets", id="block-comment"
        ),
        pytest.param(
            "// fetch('/api/data')\nvar x = 1;",
            "fetch", id="fetch-comment"
        ),
    ]

    @pytest.mark.parametrize("js_input,unwanted_id", FP_COMMENT_CASES)
    def test_feature_in_comment_not_detected(self, parse_features, js_input, unwanted_id):
        assert unwanted_id not in parse_features(js_input)


@pytest.mark.skipif(not _TREE_SITTER_AVAILABLE, reason="tree-sitter not available")
class TestFalsePositiveStrings:
    """Features inside string literals should not be detected."""

    FP_STRING_CASES = [
        pytest.param(
            'const msg = "navigator.bluetooth is not supported";',
            "web-bluetooth", id="double-quote"
        ),
        pytest.param(
            "const msg = 'WebSocket connection failed';",
            "websockets", id="single-quote"
        ),
        pytest.param(
            'const msg = "Use new IntersectionObserver for lazy loading";',
            "intersectionobserver", id="constructor-in-string"
        ),
        pytest.param(
            "const msg = `navigator.gpu is ${status}`;",
            "webgpu", id="template-text"
        ),
    ]

    @pytest.mark.parametrize("js_input,unwanted_id", FP_STRING_CASES)
    def test_feature_in_string_not_detected(self, parse_features, js_input, unwanted_id):
        assert unwanted_id not in parse_features(js_input)


@pytest.mark.skipif(not _TREE_SITTER_AVAILABLE, reason="tree-sitter not available")
class TestFalsePositiveMixed:
    """Mixed scenarios: real code plus strings/comments."""

    def test_real_fetch_not_string_fetch(self, parse_features):
        js = '''
        const label = "fetch data from server";
        fetch('/api/real');
        '''
        assert 'fetch' in parse_features(js)

    def test_comment_doesnt_mask_real_code(self, parse_features):
        js = '''
        // This uses Proxy
        const p = new Proxy(target, handler);
        '''
        assert 'proxy' in parse_features(js)

    def test_multiple_false_positives(self, parse_features):
        js = '''
        // navigator.bluetooth, navigator.serial, navigator.usb
        /* SharedArrayBuffer, WebTransport, WebGPU */
        const msg = "We support ReadableStream and WritableStream";
        var x = 1;
        '''
        features = parse_features(js)
        assert 'web-bluetooth' not in features
        assert 'web-serial' not in features
        assert 'webusb' not in features


# --- Regex Fallback Tests ---

FALLBACK_FEATURES = [
    pytest.param("const fn = () => 1;", "arrow-functions", id="arrow"),
    pytest.param("fetch('/api');", "fetch", id="fetch"),
    pytest.param("new Promise((resolve) => resolve());", "promises", id="promises"),
    pytest.param("const x = 1;", "const", id="const"),
    pytest.param("const s = `hello ${name}`;", "template-literals", id="template"),
    pytest.param("async function f() { await x; }", "async-functions", id="async"),
    pytest.param("class Foo {}", "es6-class", id="class"),
    pytest.param('"use strict"; var x = 1;', "use-strict", id="use-strict"),
]


@pytest.mark.parametrize("js_input,expected_id", FALLBACK_FEATURES)
def test_regex_fallback(js_input, expected_id):
    """Verify features detected when tree-sitter is disabled."""
    with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
        parser = JavaScriptParser()
        features = parser.parse_string(js_input)
        assert expected_id in features


def test_fallback_event_listeners():
    """Regex fallback detects event listener strings."""
    with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
        parser = JavaScriptParser()
        features = parser.parse_string(
            "window.addEventListener('hashchange', handler);"
        )
        assert 'hashchange' in features


def test_fallback_detailed_report():
    """Regex fallback produces valid detailed report."""
    with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
        parser = JavaScriptParser()
        parser.parse_string("fetch('/api'); const x = 1;")
        report = parser.get_detailed_report()
        assert report['total_features'] > 0
        assert 'fetch' in report['features']


def test_tree_sitter_parse_failure_falls_back():
    """When tree-sitter parse returns None, regex fallback is used."""
    parser = JavaScriptParser()
    with patch.object(parser, '_parse_with_tree_sitter', return_value=None):
        features = parser.parse_string("const x = () => 1; fetch('/api');")
        assert 'arrow-functions' in features
        assert 'fetch' in features
