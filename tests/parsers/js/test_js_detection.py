"""Consolidated JS feature detection tests.

Parametrized tests for all feature categories: ES6+ syntax, array/object methods,
promises/async, DOM APIs, modern APIs, observers/workers, and storage.
"""

import pytest


# --- ES6+ Syntax Features ---

ES6_ARROW_FUNCTIONS = [
    pytest.param("const fn = () => 1;", "arrow-functions", id="simple-arrow"),
    pytest.param("const add = (a, b) => a + b;", "arrow-functions", id="arrow-params"),
    pytest.param("arr.map(x => x * 2);", "arrow-functions", id="arrow-callback"),
    pytest.param("const fn = (x) => { return x * 2; };", "arrow-functions", id="arrow-block"),
]

ES6_ASYNC = [
    pytest.param(
        "async function fetchData() { return await fetch('/api'); }",
        "async-functions", id="async-function"
    ),
    pytest.param(
        "const fn = async () => { await Promise.resolve(); };",
        "async-functions", id="async-arrow"
    ),
]

ES6_CONST_LET = [
    pytest.param("const PI = 3.14159;", "const", id="const-primitive"),
    pytest.param("const config = { debug: true };", "const", id="const-object"),
    pytest.param("const { x, y } = point;", "const", id="const-destructuring"),
    pytest.param("let counter = 0;", "let", id="let-simple"),
    pytest.param("for (let i = 0; i < 10; i++) {}", "let", id="let-loop"),
]

ES6_TEMPLATE_LITERALS = [
    pytest.param("const msg = `Hello, ${name}!`;", "template-literals", id="interpolation"),
    pytest.param(
        "const html = `<div>${content}</div>`;",
        "template-literals", id="multiline"
    ),
    pytest.param("const msg = `Outer ${`inner ${value}`}`;", "template-literals", id="nested"),
]

ES6_DESTRUCTURING_SPREAD = [
    pytest.param("const {x, y} = point;", "es6", id="object-destructuring"),
    pytest.param("const [first, second] = items;", "es6", id="array-destructuring"),
    pytest.param("const combined = [...arr1];", "es6", id="spread-operator"),
    pytest.param("const { a, ...rest } = obj;", "es6", id="rest-pattern"),
]

ES6_REST_PARAMS = [
    pytest.param(
        "function sum(...numbers) { return numbers.reduce((a, b) => a + b); }",
        "rest-parameters", id="rest-function"
    ),
    pytest.param(
        "function process(first, ...rest) { return rest; }",
        "rest-parameters", id="rest-named"
    ),
]

ES6_CLASSES = [
    pytest.param(
        "class Animal { constructor(name) { this.name = name; } }",
        "es6-class", id="class-decl"
    ),
    pytest.param(
        "class Dog extends Animal { bark() { console.log('woof'); } }",
        "es6-class", id="class-extends"
    ),
]

ES6_GENERATORS = [
    pytest.param("function* gen() { yield 1; yield 2; }", "es6-generators", id="generator"),
    pytest.param(
        "function* infinite() { let i = 0; while (true) { yield i++; } }",
        "es6-generators", id="generator-infinite"
    ),
]

ES6_USE_STRICT = [
    pytest.param('"use strict"; var x = 1;', "use-strict", id="double-quotes"),
    pytest.param("'use strict'; var x = 1;", "use-strict", id="single-quotes"),
    pytest.param('function fn() { "use strict"; return 1; }', "use-strict", id="in-function"),
]


@pytest.mark.parametrize("js_input,expected_id", [
    *ES6_ARROW_FUNCTIONS,
    *ES6_ASYNC,
    *ES6_CONST_LET,
    *ES6_TEMPLATE_LITERALS,
    *ES6_DESTRUCTURING_SPREAD,
    *ES6_REST_PARAMS,
    *ES6_CLASSES,
    *ES6_GENERATORS,
    *ES6_USE_STRICT,
])
def test_es6_syntax_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Array Method Features ---

ARRAY_METHODS = [
    pytest.param("const flat = nested.flat();", "array-flat", id="flat"),
    pytest.param("const result = arr.flatMap(x => [x, x * 2]);", "array-flat", id="flatMap"),
    pytest.param("const hasItem = [1, 2, 3].includes(2);", "array-includes", id="includes"),
    pytest.param("const found = arr.find(x => x > 1);", "array-find", id="find"),
    pytest.param("const idx = arr.findIndex(x => x > 1);", "array-find", id="findIndex-via-find"),
    pytest.param("const last = arr.findLast(x => x === 2);", "array-find", id="findLast"),
    pytest.param(
        "const idx = ['a', 'b'].findIndex(x => x === 'b');",
        "array-find-index", id="findIndex-separate"
    ),
    pytest.param("[1, 2, 3].forEach(x => console.log(x));", "es5", id="forEach"),
    pytest.param("const doubled = arr.map(x => x * 2);", "es5", id="map"),
    pytest.param("const evens = arr.filter(x => x % 2 === 0);", "es5", id="filter"),
    pytest.param("const sum = arr.reduce((a, b) => a + b, 0);", "es5", id="reduce"),
    pytest.param("const hasEven = arr.some(x => x % 2 === 0);", "es5", id="some"),
    pytest.param("const allPositive = arr.every(x => x > 0);", "es5", id="every"),
]


@pytest.mark.parametrize("js_input,expected_id", ARRAY_METHODS)
def test_array_methods(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Object/String Method Features ---

OBJECT_STRING_METHODS = [
    pytest.param("const entries = Object.entries({ a: 1 });", "object-entries", id="entries"),
    pytest.param(
        "for (const [k, v] of Object.entries(obj)) {}",
        "object-entries", id="entries-iteration"
    ),
    pytest.param("const values = Object.values({ a: 1 });", "object-values", id="values"),
    pytest.param(
        "const has = 'hello world'.includes('world');",
        "es6-string-includes", id="string-includes"
    ),
    pytest.param("const padded = '5'.padStart(3, '0');", "pad-start-end", id="padStart"),
    pytest.param("const padded = 'hi'.padEnd(5, '!');", "pad-start-end", id="padEnd"),
]


@pytest.mark.parametrize("js_input,expected_id", OBJECT_STRING_METHODS)
def test_object_string_methods(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- ES6 Built-in Objects ---

ES6_BUILTINS = [
    pytest.param("const big = BigInt(9007199254740991);", "bigint", id="bigint-constructor"),
    pytest.param("const big = 9007199254740991n;", "bigint", id="bigint-literal"),
    pytest.param("const proxy = new Proxy(target, handler);", "proxy", id="proxy"),
    pytest.param("const map = new Map();", "es6", id="map"),
    pytest.param("const set = new Set([1, 2, 3]);", "es6", id="set"),
    pytest.param("const wm = new WeakMap();", "es6", id="weakmap"),
    pytest.param("const ws = new WeakSet();", "es6", id="weakset"),
    pytest.param("const sym = Symbol('description');", "es6", id="symbol"),
    pytest.param("Reflect.get(obj, 'prop');", "es6", id="reflect"),
    pytest.param("const url = new URL('https://example.com');", "url", id="url"),
    pytest.param(
        "const params = new URLSearchParams('?a=1&b=2');",
        "urlsearchparams", id="urlsearchparams"
    ),
]


@pytest.mark.parametrize("js_input,expected_id", ES6_BUILTINS)
def test_es6_builtins(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Promise & Async API Features ---

PROMISE_FEATURES = [
    pytest.param(
        "const p = new Promise((resolve, reject) => { resolve('done'); });",
        "promises", id="constructor"
    ),
    pytest.param("promise.then(result => console.log(result));", "promises", id="then"),
    pytest.param("Promise.all([p1, p2, p3]).then(results => {});", "promises", id="all"),
    pytest.param("Promise.resolve('value').then(console.log);", "promises", id="resolve"),
    pytest.param(
        "fetch('/api').then(r => r.json()).finally(() => cleanup());",
        "promise-finally", id="finally"
    ),
    pytest.param("fetch('/api/users');", "fetch", id="fetch-simple"),
    pytest.param(
        "fetch('/api').then(r => r.json()).then(data => console.log(data));",
        "fetch", id="fetch-chain"
    ),
    pytest.param("const controller = new AbortController();", "abortcontroller", id="abort"),
    pytest.param("const signal = AbortSignal.timeout(5000);", "abortcontroller", id="abort-signal"),
    pytest.param(
        "window.onunhandledrejection = handler;",
        "unhandledrejection", id="unhandledrejection"
    ),
    pytest.param(
        "window.onrejectionhandled = handler;",
        "unhandledrejection", id="rejectionhandled"
    ),
]


@pytest.mark.parametrize("js_input,expected_id", PROMISE_FEATURES)
def test_promise_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Timing API Features ---

TIMING_FEATURES = [
    pytest.param("requestAnimationFrame(animate);", "requestanimationframe", id="raf"),
    pytest.param(
        "const id = requestAnimationFrame(fn); cancelAnimationFrame(id);",
        "requestanimationframe", id="cancel-raf"
    ),
    pytest.param("requestIdleCallback(doWork);", "requestidlecallback", id="ric"),
    pytest.param("cancelIdleCallback(idleId);", "requestidlecallback", id="cancel-ric"),
    pytest.param(
        "setImmediate(() => console.log('immediate'));",
        "setimmediate", id="setImmediate"
    ),
    pytest.param("clearImmediate(immediateId);", "setimmediate", id="clearImmediate"),
]


@pytest.mark.parametrize("js_input,expected_id", TIMING_FEATURES)
def test_timing_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- DOM Manipulation Features ---

DOM_MANIPULATION = [
    pytest.param(
        "element.insertAdjacentHTML('beforeend', '<span>New</span>');",
        "insertadjacenthtml", id="insertAdjacentHTML"
    ),
    pytest.param(
        "element.insertAdjacentElement('beforebegin', newElement);",
        "insert-adjacent", id="insertAdjacentElement"
    ),
    pytest.param(
        "element.insertAdjacentText('afterend', 'Text node');",
        "insert-adjacent", id="insertAdjacentText"
    ),
    pytest.param("element.remove();", "childnode-remove", id="remove"),
    pytest.param("parent.append(child1, child2);", "dom-manip-convenience", id="append"),
    pytest.param("parent.prepend(firstChild);", "dom-manip-convenience", id="prepend"),
    pytest.param("element.before(sibling);", "dom-manip-convenience", id="before"),
    pytest.param("element.after(nextSibling);", "dom-manip-convenience", id="after"),
    pytest.param("const range = document.createRange();", "dom-range", id="createRange"),
    pytest.param("const range = new Range();", "dom-range", id="new-Range"),
    pytest.param("element.scrollIntoView();", "scrollintoview", id="scrollIntoView"),
    pytest.param(
        "element.scrollIntoView({ behavior: 'smooth', block: 'center' });",
        "scrollintoview", id="scrollIntoView-options"
    ),
    pytest.param(
        "element.scrollIntoViewIfNeeded();",
        "scrollintoviewifneeded", id="scrollIntoViewIfNeeded"
    ),
    pytest.param(
        "element.scroll({ top: 100, behavior: 'smooth' });",
        "element-scroll-methods", id="scroll"
    ),
    pytest.param("element.scrollTo(0, 500);", "element-scroll-methods", id="scrollTo"),
    pytest.param(
        "element.scrollBy({ top: 50, left: 0 });",
        "element-scroll-methods", id="scrollBy"
    ),
]


@pytest.mark.parametrize("js_input,expected_id", DOM_MANIPULATION)
def test_dom_manipulation(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- DOM Query & Selection Features ---

DOM_QUERY = [
    pytest.param("document.querySelector('.my-class');", "queryselector", id="querySelector"),
    pytest.param(
        "document.querySelectorAll('div.container');",
        "queryselector", id="querySelectorAll"
    ),
    pytest.param("element.classList.add('active');", "classlist", id="classList-add"),
    pytest.param("element.classList.toggle('open');", "classlist", id="classList-toggle"),
    pytest.param("const classes = element.classList;", "classlist", id="classList-access"),
    pytest.param("element.dataset.userId = '123';", "dataset", id="dataset-set"),
    pytest.param("const id = element.dataset.userId;", "dataset", id="dataset-get"),
    pytest.param("element.addEventListener('click', handler);", "addeventlistener", id="addEventListener"),
    pytest.param(
        "element.addEventListener('scroll', handler, { passive: true });",
        "addeventlistener", id="addEventListener-options"
    ),
    pytest.param(
        "element.removeEventListener('click', handler);",
        "addeventlistener", id="removeEventListener"
    ),
    pytest.param(
        "document.getElementsByClassName('item');",
        "getelementsbyclassname", id="getElementsByClassName"
    ),
    pytest.param("element.textContent = 'New text';", "textcontent", id="textContent-set"),
    pytest.param("const text = element.textContent;", "textcontent", id="textContent-get"),
    pytest.param("element.innerText = 'Visible text';", "innertext", id="innerText-set"),
    pytest.param("const visible = element.innerText;", "innertext", id="innerText-get"),
]


@pytest.mark.parametrize("js_input,expected_id", DOM_QUERY)
def test_dom_query(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Modern Web API Features ---

MODERN_APIS = [
    pytest.param("const ctx = new WebGLRenderingContext();", "webgl", id="webgl"),
    pytest.param("const ctx = new WebGL2RenderingContext();", "webgl2", id="webgl2"),
    pytest.param(
        "const adapter = await navigator.gpu.requestAdapter();",
        "webgpu", id="webgpu"
    ),
    pytest.param("const pc = new RTCPeerConnection(config);", "rtcpeerconnection", id="rtc"),
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
        "notifications", id="notification"
    ),
    pytest.param(
        "navigator.clipboard.writeText('copied text');",
        "clipboard", id="clipboard-write"
    ),
    pytest.param(
        "const text = await navigator.clipboard.readText();",
        "clipboard", id="clipboard-read"
    ),
    pytest.param(
        "const items = await navigator.clipboard.read();",
        "async-clipboard", id="async-clipboard"
    ),
    pytest.param(
        "history.pushState({ page: 1 }, 'Title', '/page1');",
        "history", id="pushState"
    ),
    pytest.param("history.replaceState({}, '', '/new-url');", "history", id="replaceState"),
    pytest.param(
        "window.onpopstate = function(event) { console.log(event); };",
        "history", id="onpopstate"
    ),
    pytest.param(
        "const mq = window.matchMedia('(prefers-color-scheme: dark)');",
        "matchmedia", id="matchMedia"
    ),
    pytest.param("const styles = getComputedStyle(element);", "getcomputedstyle", id="getComputedStyle"),
]


@pytest.mark.parametrize("js_input,expected_id", MODERN_APIS)
def test_modern_apis(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Observer Features ---

OBSERVER_FEATURES = [
    pytest.param(
        "const observer = new IntersectionObserver(callback);",
        "intersectionobserver", id="intersection"
    ),
    pytest.param(
        "if (entry.isVisible) { console.log('visible'); }",
        "intersectionobserver-v2", id="intersection-v2"
    ),
    pytest.param(
        "const observer = new MutationObserver(callback);",
        "mutationobserver", id="mutation"
    ),
    pytest.param(
        "const observer = new ResizeObserver(callback);",
        "resizeobserver", id="resize"
    ),
]


@pytest.mark.parametrize("js_input,expected_id", OBSERVER_FEATURES)
def test_observer_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Worker & Communication Features ---

WORKER_FEATURES = [
    pytest.param("const worker = new Worker('worker.js');", "webworkers", id="worker"),
    pytest.param("const worker = new SharedWorker('shared.js');", "sharedworkers", id="shared"),
    pytest.param(
        "navigator.serviceWorker.register('/sw.js');",
        "serviceworkers", id="serviceworker"
    ),
    pytest.param(
        "const socket = new WebSocket('wss://example.com');",
        "websockets", id="websocket"
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


@pytest.mark.parametrize("js_input,expected_id", WORKER_FEATURES)
def test_worker_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Storage & Binary Features ---

STORAGE_FEATURES = [
    pytest.param(
        "localStorage.setItem('key', 'value');",
        "namevalue-storage", id="localStorage-set"
    ),
    pytest.param(
        "const value = localStorage.getItem('key');",
        "namevalue-storage", id="localStorage-get"
    ),
    pytest.param(
        "sessionStorage.setItem('session', 'data');",
        "namevalue-storage", id="sessionStorage-set"
    ),
    pytest.param("localStorage.clear();", "namevalue-storage", id="localStorage-clear"),
    pytest.param(
        "const request = indexedDB.open('myDatabase', 1);",
        "indexeddb", id="indexeddb"
    ),
    pytest.param("const range = IDBKeyRange.bound(1, 100);", "indexeddb2", id="indexeddb2"),
    pytest.param("const reader = new FileReader();", "filereader", id="filereader"),
    pytest.param("const file = new File(['content'], 'filename.txt');", "fileapi", id="file"),
    pytest.param(
        "const blob = new Blob(['data'], { type: 'text/plain' });",
        "fileapi", id="blob"
    ),
    pytest.param("const url = URL.createObjectURL(blob);", "bloburls", id="createObjectURL"),
    pytest.param("const encoded = btoa('Hello World');", "atob-btoa", id="btoa"),
    pytest.param("const decoded = atob('SGVsbG8=');", "atob-btoa", id="atob"),
    pytest.param("const encoder = new TextEncoder();", "textencoder", id="textencoder"),
    pytest.param("const decoder = new TextDecoder('utf-8');", "textencoder", id="textdecoder"),
    pytest.param("const arr = new Uint8Array(buffer);", "typedarrays", id="uint8array"),
    pytest.param("const buffer = new ArrayBuffer(16);", "typedarrays", id="arraybuffer"),
    pytest.param("const view = new DataView(buffer);", "typedarrays", id="dataview"),
    pytest.param(
        "const sab = new SharedArrayBuffer(1024);",
        "sharedarraybuffer", id="sharedarraybuffer"
    ),
    pytest.param("Atomics.wait(int32Array, 0, 0);", "sharedarraybuffer", id="atomics"),
    pytest.param("const obj = JSON.parse(jsonStr);", "json", id="json-parse"),
    pytest.param(
        "const str = JSON.stringify({ key: 'value' });",
        "json", id="json-stringify"
    ),
]


@pytest.mark.parametrize("js_input,expected_id", STORAGE_FEATURES)
def test_storage_features(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Combined Feature Tests ---

def test_modern_js_file(parse_features):
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


def test_fetch_with_abort_controller(parse_features):
    """Fetch with AbortController detects both features."""
    js = """
    const controller = new AbortController();
    fetch('/api', { signal: controller.signal });
    """
    features = parse_features(js)
    assert 'fetch' in features
    assert 'abortcontroller' in features
