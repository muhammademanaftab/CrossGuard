/*
  JavaScript false-positive bait file.

  Each block below is designed to PROVOKE the JS parser into reporting
  a feature that is not actually used. Each comment names the feature
  the parser is suspected to wrongly report and explains why.

  Run:
    python3 -m src.cli.main analyze examples/test_fixtures/false_positive_bait.js --format table

  Then check the "Detected Features" section. Any feature listed below
  as a "suspected false positive" that DOES appear in the report is a
  confirmed false positive.
*/

// --- Bait 1: array .includes() should not trigger String.includes ---
// Suspected false positive: es6-string-includes
// Why: the parser cannot tell from .includes() alone whether the
// receiver is an array or a string, so it reports both.
const arrayIncludes = [1, 2, 3].includes(2);

// --- Bait 2: string .includes() should not trigger Array.includes ---
// Suspected false positive: array-includes
// Why: same reason as bait 1, in the other direction.
const stringIncludes = "hello world".includes("world");

// --- Bait 3: user-defined includes method ---
// Should NOT trigger array-includes or es6-string-includes because
// this .includes() is on a user object, not on an Array or String.
class UserSet {
    includes(item) {
        return false;
    }
}
const userIncludes = new UserSet().includes("anything");

// --- Bait 4: user-defined fetch function ---
// Should NOT trigger the "fetch" feature because the parser is supposed
// to detect calls to the GLOBAL fetch, not user-defined functions.
function fetch(url) {
    return null;
}
const myFetchResult = fetch("/anything");

// --- Bait 5: property access without a call ---
// Should NOT trigger fetch or structuredClone because there is no
// CALL here, just a property reference.
const fetchRef = window.fetch;
const cloneRef = globalThis.structuredClone;

// --- Bait 6: a custom class named Promise ---
// Should NOT trigger the "promises" feature because this Promise is
// user-defined, not the built-in Promise constructor.
class Promise {
    constructor(executor) {
        this.executor = executor;
    }
}
const myPromise = new Promise(() => {});

// --- Bait 7: array .map() and .forEach() ---
// These are universally supported and may not be flagged at all, but
// if they are, they should not trigger anything else (like Map the
// constructor, or feature ids that share the substring "map").
const mapped = [1, 2].map((x) => x * 2);
const forEachResult = [1, 2].forEach((x) => {});

// --- Bait 8: BigInt-looking number that is not a BigInt ---
// The "n" suffix is what makes it BigInt. A regular number with the
// letter n nearby in a comment or in a variable name should not
// trigger BigInt detection.
const notBigInt = 9007199254740993; // not n-suffixed
const variableNamedN = 5;

// --- Bait 9: optional chaining lookalikes ---
// Should NOT trigger optional-chaining. The parser must distinguish
// the actual ?. operator from question marks in other contexts.
const ternary = condition() ? value : fallback;
const stringWithQuestion = "is this ?.";

// --- Bait 10: nullish-coalescing lookalikes ---
// Should NOT trigger nullish-coalescing. The parser must distinguish
// ?? from || and from question marks in conditional expressions.
const orFallback = title || "Untitled";
const ternary2 = title ? title : "Untitled";

// --- Bait 11: feature names inside string literals ---
// String contents are supposed to be stripped before regex matching,
// so these mentions should produce zero detections.
const stringPromise = "this mentions Promise but should not trigger";
const stringFetch = "this mentions fetch() but should not trigger";
const stringClass = "class declaration mentioned in a string";

// --- Bait 12: feature names inside comments ---
// Comments must never trigger detections.
// async function foo() { await fetch('/x'); return new Promise(); }
// const x = a?.b ?? c;
// class Foo { #priv; }

// --- Bait 13: identifiers that look like APIs ---
// User identifiers that share names with global APIs but are not the
// APIs themselves. None of these should trigger detections.
const Map = "not the Map constructor";
const Set = "not the Set constructor";
const Symbol = "not the Symbol global";
const URL = "not the URL constructor";
const fetch_data = "underscore variable";

// --- Bait 14: helper function that is helper, despite what it looks like ---
// Should NOT trigger es6-class because there is no class keyword,
// even though the function name starts with a capital letter.
function MyComponent() {
    return null;
}

// --- Truly negative ---
// Plain JS that should produce zero feature detections.
function add(a, b) {
    return a + b;
}
var x = 1;
var y = 2;
var z = x + y;
