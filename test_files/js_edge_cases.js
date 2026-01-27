/**
 * JavaScript Edge Case Test File
 *
 * This file tests patterns that should NOT trigger feature detection.
 * All JavaScript features here are either:
 * 1. Inside comments (should be ignored)
 * 2. Inside string literals (should be ignored)
 * 3. Property names that look like features (should be ignored)
 *
 * Expected result: ZERO or minimal features detected
 */

// ============================================================================
// FEATURES IN SINGLE-LINE COMMENTS - SHOULD NOT BE DETECTED
// ============================================================================

// const arrow = () => {};
// let variable = 1;
// async function asyncFn() {}
// class MyClass {}
// new Promise()
// fetch('/api')
// new IntersectionObserver()
// new MutationObserver()
// new ResizeObserver()
// localStorage.setItem()
// sessionStorage.getItem()
// new Map()
// new Set()
// document.querySelector()
// element.classList.add()
// await fetch()
// import module from './module'
// export default function

// ============================================================================
// FEATURES IN MULTI-LINE COMMENTS - SHOULD NOT BE DETECTED
// ============================================================================

/*
const arrowInComment = () => {};
let inComment = 'value';
async function asyncInComment() {
    await fetch('/api');
}
class ClassInComment {}
new Promise((resolve) => resolve());
new IntersectionObserver(() => {});
localStorage.setItem('key', 'value');
*/

/**
 * JSDoc-style comment with features:
 * @example
 * const fn = () => {};
 * async function example() {}
 * new Promise()
 * fetch('/api')
 */

// ============================================================================
// FEATURES IN REGULAR STRINGS - SHOULD NOT BE DETECTED
// ============================================================================

var message1 = "Use arrow functions like () => {} for cleaner syntax";
var message2 = "The fetch API is great for HTTP requests";
var message3 = "async functions use the await keyword";
var message4 = "ES6 class syntax: class MyClass {}";
var message5 = "Promise.all is useful for concurrent operations";
var message6 = "new Map() creates a Map data structure";
var message7 = "new Set() creates a Set data structure";
var message8 = "IntersectionObserver is used for lazy loading";
var message9 = "localStorage.setItem() stores data";
var message10 = "document.querySelector() finds elements";

// Template literals containing feature-like text (the backticks ARE a feature)
// So we use regular strings here to avoid detection
var code1 = 'Example: const fn = () => {}';
var code2 = 'Example: async function getData() {}';
var code3 = 'Example: new Promise((resolve, reject) => {})';
var code4 = 'Example: await fetch("/api/data")';
var code5 = 'Example: class Component extends React.Component {}';

// ============================================================================
// URLS IN STRINGS - BUG TEST (contains //)
// ============================================================================

var apiUrl = "http://api.example.com/data";
var secureUrl = "https://secure.example.com/endpoint";
var wsUrl = "wss://websocket.example.com/socket";
var ftpUrl = "ftp://files.example.com/download";
var protocolRelative = "//cdn.example.com/script.js";

// ============================================================================
// COMMENT-LIKE SYNTAX IN STRINGS - BUG TEST
// ============================================================================

var notAComment1 = "/* This is not a comment */";
var notAComment2 = "// This is also not a comment";
var codeExample = "// const x = 1; /* comment */";
var mixedSyntax = "Code: /* display: flex; */ end";

// ============================================================================
// FEATURE KEYWORDS AS OBJECT PROPERTY NAMES - SHOULD NOT DETECT
// ============================================================================

var config = {
    fetch: false,           // 'fetch' as property, not function call
    async: true,            // 'async' as property, not keyword
    class: "button",        // 'class' as property, not declaration
    const: "value",         // 'const' as property, not declaration
    let: "data",            // 'let' as property, not declaration
    Map: null,              // 'Map' as property, not constructor
    Set: undefined,         // 'Set' as property, not constructor
    Promise: {},            // 'Promise' as property, not constructor
    Proxy: [],              // 'Proxy' as property, not constructor
    Symbol: 0,              // 'Symbol' as property, not constructor
    localStorage: "mock",   // 'localStorage' as property
    sessionStorage: "mock"  // 'sessionStorage' as property
};

var features = {
    "IntersectionObserver": "supported",
    "MutationObserver": "supported",
    "ResizeObserver": "supported",
    "WebSocket": "supported",
    "Worker": "supported",
    "ServiceWorker": "supported"
};

// ============================================================================
// OBJECT PROPERTY ACCESS THAT LOOKS LIKE FEATURES
// ============================================================================

// These access properties named like features, not actual features
var obj = {};
obj.fetch = function() {};      // Assigning to property
obj.async = true;               // Assigning to property
obj.class = "item";             // Assigning to property
var x = obj.fetch;              // Reading property
var y = obj.class;              // Reading property

// ============================================================================
// STRINGS THAT CONTAIN REGEX-LIKE PATTERNS
// ============================================================================

var pattern1 = "Match: .then(";
var pattern2 = "Pattern: .catch(";
var pattern3 = "Regex: new Promise";
var pattern4 = "Search: => arrow";
var pattern5 = "Find: async function";

// ============================================================================
// JSON STRINGS CONTAINING FEATURE KEYWORDS
// ============================================================================

var jsonString = '{"fetch": true, "async": false, "class": "MyClass"}';
var jsonData = '{"Promise": null, "Map": {}, "Set": []}';
var jsonConfig = '{"localStorage": "mock", "sessionStorage": "mock"}';

// ============================================================================
// HTML-LIKE STRINGS (for innerHTML, etc.)
// ============================================================================

var htmlString = '<div class="container">Content</div>';
var htmlWithScript = '<script>const x = 1;</script>';
var htmlTemplate = '<template><div class="card"></div></template>';

// ============================================================================
// ARRAY OF FEATURE NAMES AS STRINGS
// ============================================================================

var featureNames = [
    "arrow-functions",
    "async-functions",
    "const",
    "let",
    "template-literals",
    "promises",
    "fetch",
    "IntersectionObserver",
    "MutationObserver",
    "localStorage",
    "sessionStorage"
];

// ============================================================================
// DOCUMENTATION STRINGS
// ============================================================================

var docs = {
    arrow: "Arrow functions () => {} are ES6 feature",
    async: "Async/await syntax: async function name() { await promise; }",
    class: "Class syntax: class Name { constructor() {} }",
    promise: "Promise: new Promise((resolve, reject) => {})",
    observer: "Observer: new IntersectionObserver(callback)"
};

// ============================================================================
// ESCAPED CHARACTERS IN STRINGS
// ============================================================================

var escaped1 = "Arrow\\: () \\=\\> {}";
var escaped2 = "async\\sfunction";
var escaped3 = "class\\sMyClass";
var escaped4 = "new\\sPromise";

// ============================================================================
// BASIC VARIABLE DECLARATIONS (not using const/let)
// ============================================================================

var basicVar1 = 1;
var basicVar2 = "string";
var basicVar3 = true;
var basicVar4 = null;
var basicVar5 = undefined;
var basicVar6 = [];
var basicVar7 = {};

// ============================================================================
// BASIC FUNCTION DECLARATIONS (not arrow functions)
// ============================================================================

function basicFunction1() {
    return 1;
}

function basicFunction2(a, b) {
    return a + b;
}

function basicFunction3() {
    var result = 0;
    return result;
}

// ============================================================================
// IIFE WITHOUT MODERN FEATURES
// ============================================================================

(function() {
    var privateVar = "private";
    return privateVar;
})();

// ============================================================================
// CALLBACK STYLE (not Promise-based)
// ============================================================================

function callbackStyle(callback) {
    setTimeout(function() {
        callback(null, "result");
    }, 1000);
}

// ============================================================================
// OLD-STYLE EVENT HANDLING
// ============================================================================

// Note: addEventListener IS a feature, so using old onclick style
function handleClick() {
    alert("Clicked!");
}

// ============================================================================
// TYPEOF CHECKS (string comparisons)
// ============================================================================

if (typeof Promise === "undefined") {
    // Polyfill needed
}

if (typeof fetch === "undefined") {
    // Polyfill needed
}

if (typeof Map === "undefined") {
    // Polyfill needed
}

// ============================================================================
// MINIFIED-LOOKING CODE (but basic)
// ============================================================================

var a=1,b=2,c=3;function d(e,f){return e+f}var g=d(a,b);

// ============================================================================
// EMPTY/MINIMAL FUNCTIONS
// ============================================================================

function empty() {}
function noop() { return; }
function identity(x) { return x; }
