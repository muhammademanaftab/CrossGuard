"""Blackbox tests for the JavaScript parser.

Tests public API only: input string -> parse_features/get_detailed_report -> assert output.
No mocking, no internal imports. One representative test per unique caniuse feature ID,
plus all edge case and combined-feature tests.
"""

import pytest


# --- ES6+ Syntax Features (1 per caniuse ID) ---

ES6_SYNTAX = [
    pytest.param("const fn = () => 1;", "arrow-functions", id="arrow-functions"),
    pytest.param(
        "async function fetchData() { return await fetch('/api'); }",
        "async-functions", id="async-functions"
    ),
    pytest.param("const PI = 3.14159;", "const", id="const"),
    pytest.param("let counter = 0;", "let", id="let"),
    pytest.param("const msg = `Hello, ${name}!`;", "template-literals", id="template-literals"),
    pytest.param("const {x, y} = point;", "es6", id="es6-destructuring"),
    pytest.param(
        "function sum(...numbers) { return numbers.reduce((a, b) => a + b); }",
        "rest-parameters", id="rest-parameters"
    ),
    pytest.param(
        "class Animal { constructor(name) { this.name = name; } }",
        "es6-class", id="es6-class"
    ),
    pytest.param("function* gen() { yield 1; yield 2; }", "es6-generators", id="es6-generators"),
    pytest.param('"use strict"; var x = 1;', "use-strict", id="use-strict"),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", ES6_SYNTAX)
def test_es6_syntax(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Array Methods (1 per caniuse ID) ---

ARRAY_METHODS = [
    pytest.param("const flat = nested.flat();", "array-flat", id="array-flat"),
    pytest.param("const hasItem = [1, 2, 3].includes(2);", "array-includes", id="array-includes"),
    pytest.param("const found = arr.find(x => x > 1);", "array-find", id="array-find"),
    pytest.param(
        "const idx = ['a', 'b'].findIndex(x => x === 'b');",
        "array-find-index", id="array-find-index"
    ),
    pytest.param("[1, 2, 3].forEach(x => console.log(x));", "es5", id="es5-forEach"),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", ARRAY_METHODS)
def test_array_methods(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Object/String Methods (1 per caniuse ID) ---

OBJECT_STRING_METHODS = [
    pytest.param("const entries = Object.entries({ a: 1 });", "object-entries", id="object-entries"),
    pytest.param("const values = Object.values({ a: 1 });", "object-values", id="object-values"),
    pytest.param(
        "const has = 'hello world'.includes('world');",
        "es6-string-includes", id="string-includes"
    ),
    pytest.param("const padded = '5'.padStart(3, '0');", "pad-start-end", id="pad-start-end"),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", OBJECT_STRING_METHODS)
def test_object_string_methods(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- ES6 Built-in Objects (1 per caniuse ID) ---

ES6_BUILTINS = [
    pytest.param("const big = BigInt(9007199254740991);", "bigint", id="bigint"),
    pytest.param("const proxy = new Proxy(target, handler);", "proxy", id="proxy"),
    pytest.param("const map = new Map();", "es6", id="es6-map"),
    pytest.param("const url = new URL('https://example.com');", "url", id="url"),
    pytest.param(
        "const params = new URLSearchParams('?a=1&b=2');",
        "urlsearchparams", id="urlsearchparams"
    ),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", ES6_BUILTINS)
def test_es6_builtins(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Promise & Async API (1 per caniuse ID) ---

PROMISE_FEATURES = [
    pytest.param(
        "const p = new Promise((resolve, reject) => { resolve('done'); });",
        "promises", id="promises"
    ),
    pytest.param(
        "fetch('/api').then(r => r.json()).finally(() => cleanup());",
        "promise-finally", id="promise-finally"
    ),
    pytest.param("fetch('/api/users');", "fetch", id="fetch"),
    pytest.param("const controller = new AbortController();", "abortcontroller", id="abortcontroller"),
    pytest.param(
        "window.onunhandledrejection = handler;",
        "unhandledrejection", id="unhandledrejection"
    ),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", PROMISE_FEATURES)
def test_promise_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Timing APIs (1 per caniuse ID) ---

TIMING_FEATURES = [
    pytest.param("requestAnimationFrame(animate);", "requestanimationframe", id="raf"),
    pytest.param("requestIdleCallback(doWork);", "requestidlecallback", id="ric"),
    pytest.param(
        "setImmediate(() => console.log('immediate'));",
        "setimmediate", id="setImmediate"
    ),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", TIMING_FEATURES)
def test_timing_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- DOM Manipulation (1 per caniuse ID) ---

DOM_MANIPULATION = [
    pytest.param(
        "element.insertAdjacentHTML('beforeend', '<span>New</span>');",
        "insertadjacenthtml", id="insertAdjacentHTML"
    ),
    pytest.param(
        "element.insertAdjacentElement('beforebegin', newElement);",
        "insert-adjacent", id="insert-adjacent"
    ),
    pytest.param("element.remove();", "childnode-remove", id="childnode-remove"),
    pytest.param("parent.append(child1, child2);", "dom-manip-convenience", id="dom-manip-convenience"),
    pytest.param("const range = document.createRange();", "dom-range", id="dom-range"),
    pytest.param("element.scrollIntoView();", "scrollintoview", id="scrollIntoView"),
    pytest.param(
        "element.scrollIntoViewIfNeeded();",
        "scrollintoviewifneeded", id="scrollIntoViewIfNeeded"
    ),
    pytest.param(
        "element.scroll({ top: 100, behavior: 'smooth' });",
        "element-scroll-methods", id="element-scroll-methods"
    ),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", DOM_MANIPULATION)
def test_dom_manipulation(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- DOM Query & Selection (1 per caniuse ID) ---

DOM_QUERY = [
    pytest.param("document.querySelector('.my-class');", "queryselector", id="queryselector"),
    pytest.param("element.classList.add('active');", "classlist", id="classlist"),
    pytest.param("element.dataset.userId = '123';", "dataset", id="dataset"),
    pytest.param("element.addEventListener('click', handler);", "addeventlistener", id="addeventlistener"),
    pytest.param(
        "document.getElementsByClassName('item');",
        "getelementsbyclassname", id="getelementsbyclassname"
    ),
    pytest.param("element.textContent = 'New text';", "textcontent", id="textcontent"),
    pytest.param("element.innerText = 'Visible text';", "innertext", id="innertext"),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", DOM_QUERY)
def test_dom_query(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Modern Web APIs (1 per caniuse ID) ---

MODERN_APIS = [
    pytest.param("const ctx = new WebGLRenderingContext();", "webgl", id="webgl"),
    pytest.param("const ctx = new WebGL2RenderingContext();", "webgl2", id="webgl2"),
    pytest.param(
        "const adapter = await navigator.gpu.requestAdapter();",
        "webgpu", id="webgpu"
    ),
    pytest.param("const pc = new RTCPeerConnection(config);", "rtcpeerconnection", id="rtcpeerconnection"),
    pytest.param(
        "element.animate([{ opacity: 0 }, { opacity: 1 }], 1000);",
        "web-animation", id="web-animation"
    ),
    pytest.param(
        "document.startViewTransition(() => updateDOM());",
        "view-transitions", id="view-transitions"
    ),
    pytest.param(
        "navigator.share({ title: 'Title', url: 'https://example.com' });",
        "web-share", id="web-share"
    ),
    pytest.param(
        "const notification = new Notification('Hello', { body: 'World' });",
        "notifications", id="notifications"
    ),
    pytest.param(
        "navigator.clipboard.writeText('copied text');",
        "clipboard", id="clipboard"
    ),
    pytest.param(
        "const items = await navigator.clipboard.read();",
        "async-clipboard", id="async-clipboard"
    ),
    pytest.param(
        "history.pushState({ page: 1 }, 'Title', '/page1');",
        "history", id="history"
    ),
    pytest.param(
        "const mq = window.matchMedia('(prefers-color-scheme: dark)');",
        "matchmedia", id="matchmedia"
    ),
    pytest.param("const styles = getComputedStyle(element);", "getcomputedstyle", id="getcomputedstyle"),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", MODERN_APIS)
def test_modern_apis(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Observers (1 per caniuse ID) ---

OBSERVER_FEATURES = [
    pytest.param(
        "const observer = new IntersectionObserver(callback);",
        "intersectionobserver", id="intersectionobserver"
    ),
    pytest.param(
        "if (entry.isVisible) { console.log('visible'); }",
        "intersectionobserver-v2", id="intersectionobserver-v2"
    ),
    pytest.param(
        "const observer = new MutationObserver(callback);",
        "mutationobserver", id="mutationobserver"
    ),
    pytest.param(
        "const observer = new ResizeObserver(callback);",
        "resizeobserver", id="resizeobserver"
    ),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", OBSERVER_FEATURES)
def test_observer_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Workers & Communication (1 per caniuse ID) ---

WORKER_FEATURES = [
    pytest.param("const worker = new Worker('worker.js');", "webworkers", id="webworkers"),
    pytest.param("const worker = new SharedWorker('shared.js');", "sharedworkers", id="sharedworkers"),
    pytest.param(
        "navigator.serviceWorker.register('/sw.js');",
        "serviceworkers", id="serviceworkers"
    ),
    pytest.param(
        "const socket = new WebSocket('wss://example.com');",
        "websockets", id="websockets"
    ),
    pytest.param(
        "const source = new EventSource('/events');",
        "eventsource", id="eventsource"
    ),
    pytest.param(
        "const channel = new BroadcastChannel('my-channel');",
        "broadcastchannel", id="broadcastchannel"
    ),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", WORKER_FEATURES)
def test_worker_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Storage & Binary (1 per caniuse ID) ---

STORAGE_FEATURES = [
    pytest.param("localStorage.setItem('key', 'value');", "namevalue-storage", id="namevalue-storage"),
    pytest.param(
        "const request = indexedDB.open('myDatabase', 1);",
        "indexeddb", id="indexeddb"
    ),
    pytest.param("const range = IDBKeyRange.bound(1, 100);", "indexeddb2", id="indexeddb2"),
    pytest.param("const reader = new FileReader();", "filereader", id="filereader"),
    pytest.param("const file = new File(['content'], 'filename.txt');", "fileapi", id="fileapi"),
    pytest.param("const url = URL.createObjectURL(blob);", "bloburls", id="bloburls"),
    pytest.param("const encoded = btoa('Hello World');", "atob-btoa", id="atob-btoa"),
    pytest.param("const encoder = new TextEncoder();", "textencoder", id="textencoder"),
    pytest.param("const arr = new Uint8Array(buffer);", "typedarrays", id="typedarrays"),
    pytest.param(
        "const sab = new SharedArrayBuffer(1024);",
        "sharedarraybuffer", id="sharedarraybuffer"
    ),
    pytest.param("const obj = JSON.parse(jsonStr);", "json", id="json"),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", STORAGE_FEATURES)
def test_storage_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Combined Feature Tests ---

@pytest.mark.blackbox
def test_modern_js_file_detects_multiple_features(parse_features):
    """Modern JS file should detect multiple ES6+ features."""
    js = """
    const add = (a, b) => a + b;
    let counter = 0;
    class Calculator extends Base {
        constructor() { super(); }
    }
    async function compute() { return await Promise.resolve(42); }
    """
    features = parse_features(js)
    for expected in ['arrow-functions', 'const', 'let', 'es6-class', 'async-functions']:
        assert expected in features


@pytest.mark.blackbox
def test_fetch_with_abort_controller(parse_features):
    """Fetch with AbortController detects both features."""
    js = """
    const controller = new AbortController();
    fetch('/api', { signal: controller.signal });
    """
    features = parse_features(js)
    assert 'fetch' in features
    assert 'abortcontroller' in features


# --- Edge Cases: Comment Stripping (3 tests) ---

class TestCommentStripping:
    """Tests that comments don't trigger false positives."""

    @pytest.mark.blackbox
    def test_single_line_comment(self, parse_features):
        js = """
        // fetch('/api') is commented out
        var x = 1;
        """
        assert 'fetch' not in parse_features(js)

    @pytest.mark.blackbox
    def test_multi_line_comment(self, parse_features):
        js = """
        /*
        const promise = new Promise((resolve) => resolve());
        promise.then(console.log);
        */
        var x = 1;
        """
        assert 'promises' not in parse_features(js)

    @pytest.mark.blackbox
    def test_code_after_comment(self, parse_features):
        js = """
        // This is a comment
        fetch('/api');
        """
        assert 'fetch' in parse_features(js)


# --- Edge Cases: String Handling (2 tests) ---

class TestStringHandling:
    """Tests that string contents don't trigger false positives."""

    @pytest.mark.blackbox
    def test_api_name_in_string(self, parse_features):
        js = """
        const message = "We should use fetch instead of XMLHttpRequest";
        """
        assert 'fetch' not in parse_features(js)

    @pytest.mark.blackbox
    def test_use_strict_detected(self, parse_features):
        js = '"use strict"; var x = 1;'
        assert 'use-strict' in parse_features(js)


# --- Edge Cases: Minified Code (3 tests) ---

class TestMinifiedCode:
    """Tests detection in minified code."""

    @pytest.mark.blackbox
    def test_minified_arrow_function(self, parse_features):
        js = "const a=(b,c)=>b+c;const d=e=>e*2;"
        assert 'arrow-functions' in parse_features(js)

    @pytest.mark.blackbox
    def test_minified_promise(self, parse_features):
        js = "new Promise(r=>r(1)).then(x=>x*2).catch(e=>e)"
        assert 'promises' in parse_features(js)

    @pytest.mark.blackbox
    def test_minified_fetch(self, parse_features):
        js = "fetch('/api').then(r=>r.json())"
        assert 'fetch' in parse_features(js)


# --- Edge Cases: Empty and Minimal Input (3 tests) ---

class TestEmptyAndMinimal:
    """Tests for empty and minimal input."""

    @pytest.mark.blackbox
    def test_empty_string(self, parse_features):
        features = parse_features("")
        assert len(features) == 0

    @pytest.mark.blackbox
    def test_whitespace_only(self, parse_features):
        features = parse_features("   \n\t   ")
        assert len(features) == 0

    @pytest.mark.blackbox
    def test_minimal_js(self, parse_features):
        features = parse_features("var x = 1;")
        assert 'const' not in features
        assert 'let' not in features
        assert 'arrow-functions' not in features


# --- Edge Cases: Combined Features (1 test) ---

class TestCombinedFeatures:

    @pytest.mark.blackbox
    def test_multiple_features(self, parse_features):
        js = """
        const fetchData = async () => {
            const response = await fetch('/api');
            return response.json();
        };

        document.querySelector('.btn').addEventListener('click', () => {
            localStorage.setItem('clicked', 'true');
        });
        """
        features = parse_features(js)
        for expected in [
            'const', 'arrow-functions', 'async-functions', 'fetch',
            'queryselector', 'addeventlistener', 'namevalue-storage'
        ]:
            assert expected in features


# --- Edge Cases: Feature Details (2 tests) ---

class TestFeatureDetails:

    @pytest.mark.blackbox
    def test_feature_details_populated(self, get_feature_details):
        js = "const fn = () => 1; fetch('/api');"
        details = get_feature_details(js)
        assert len(details) > 0

    @pytest.mark.blackbox
    def test_feature_details_has_matched_apis(self, get_feature_details):
        js = "navigator.geolocation.getCurrentPosition(callback);"
        details = get_feature_details(js)
        geo_detail = next((d for d in details if d['feature'] == 'geolocation'), None)
        assert geo_detail is not None
        assert 'matched_apis' in geo_detail


# --- Edge Cases: Real-World Patterns (3 tests) ---

class TestRealWorldPatterns:

    @pytest.mark.blackbox
    def test_react_component(self, parse_features):
        js = """
        const MyComponent = () => {
            const [state, setState] = useState(null);

            useEffect(() => {
                fetch('/api/data')
                    .then(r => r.json())
                    .then(setState);
            }, []);

            return state;
        };
        """
        features = parse_features(js)
        for expected in ['arrow-functions', 'const', 'fetch']:
            assert expected in features

    @pytest.mark.blackbox
    def test_async_await_pattern(self, parse_features):
        js = """
        async function loadData() {
            try {
                const response = await fetch('/api');
                const data = await response.json();
                localStorage.setItem('data', JSON.stringify(data));
                return data;
            } catch (error) {
                console.error(error);
            }
        }
        """
        features = parse_features(js)
        for expected in ['async-functions', 'fetch', 'namevalue-storage', 'json']:
            assert expected in features

    @pytest.mark.blackbox
    def test_class_with_observers(self, parse_features):
        js = """
        class LazyLoader {
            constructor() {
                this.observer = new IntersectionObserver(this.handleIntersect);
            }

            observe(element) {
                this.observer.observe(element);
            }
        }
        """
        features = parse_features(js)
        for expected in ['es6-class', 'intersectionobserver']:
            assert expected in features
