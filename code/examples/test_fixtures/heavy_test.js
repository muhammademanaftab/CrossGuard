/*
  Heavy JS parser test file.

  This file exercises a large slice of what the JavaScript parser can detect.
  Each section is labeled with the Can I Use feature IDs the parser is
  expected to add when this file is analyzed.

  Run:
    python3 -m src.cli.main analyze examples/test_fixtures/heavy_test.js --format table

  Sections include syntax features, built-in constructors, array/string/object
  methods, async APIs, web APIs, workers, storage, events, and a few negative
  cases at the end to verify the parser does not over-detect.
*/

// ============================================================
// Section 1: Variable declarations (const, let)
// Detects: const, let, es5 (var)
// ============================================================
const PI = 3.14;
const NAME = "Cross Guard";
let counter = 0;
let isRunning = false;
var legacyVar = "old style";

// ============================================================
// Section 2: Arrow functions
// Detects: arrow-functions
// ============================================================
const square = (x) => x * x;
const add = (a, b) => a + b;
const noop = () => {};
const multiline = (x) => {
    const doubled = x * 2;
    return doubled + 1;
};

// ============================================================
// Section 3: Template literals (with and without interpolation)
// Detects: template-literals
// ============================================================
const greeting = `Hello, ${NAME}!`;
const multiLine = `
    Line one
    Line two
    Line three
`;
const tagged = String.raw`Path: C:\Users\${NAME}`;

// ============================================================
// Section 4: Destructuring (array, object, with defaults)
// Detects: destructuring
// ============================================================
const [first, second, ...rest] = [1, 2, 3, 4, 5];
const { a, b, c = "default" } = { a: 1, b: 2 };
const { x: renamed, y } = { x: 10, y: 20 };

// ============================================================
// Section 5: Spread / rest
// Detects: rest-parameters
// ============================================================
function sumAll(...nums) {
    return nums.reduce((acc, n) => acc + n, 0);
}
const merged = [...rest, 6, 7];
const cloned = { ...({ a, b }) };

// ============================================================
// Section 6: Default parameters
// Detects: default parameters as part of es6
// ============================================================
function greet(name = "World", punct = "!") {
    return `Hello, ${name}${punct}`;
}

// ============================================================
// Section 7: ES6 classes (extends, static, private fields, getters/setters)
// Detects: es6-class, mdn-javascript_classes_private_class_fields
// ============================================================
class Animal {
    #species;
    static kingdom = "Animalia";

    constructor(species) {
        this.#species = species;
    }

    get species() {
        return this.#species;
    }

    set species(value) {
        this.#species = value;
    }

    describe() {
        return `A ${this.#species}`;
    }
}

class Dog extends Animal {
    #name;

    constructor(name) {
        super("dog");
        this.#name = name;
    }

    bark() {
        return `${this.#name} says woof`;
    }
}

const rex = new Dog("Rex");

// ============================================================
// Section 8: Optional chaining and nullish coalescing
// Detects: mdn-javascript_operators_optional_chaining,
//          mdn-javascript_operators_nullish_coalescing
// ============================================================
const user = { profile: { name: "Eman" } };
const name = user?.profile?.name;
const street = user?.address?.street;
const calls = user?.fns?.compute?.();
const itemAt = user?.items?.[0];

const label = user?.profile?.title ?? "Untitled";
const port = process?.env?.PORT ?? 3000;

// ============================================================
// Section 9: Async / await + generators
// Detects: async-functions, es6-generators
// ============================================================
async function fetchUser(id) {
    const res = await fetch(`/users/${id}`);
    const json = await res.json();
    return json;
}

function* range(start, end) {
    for (let i = start; i < end; i++) {
        yield i;
    }
}

async function* asyncRange(start, end) {
    for (let i = start; i < end; i++) {
        yield await Promise.resolve(i);
    }
}

// ============================================================
// Section 10: Promises (constructor, then/catch/finally, static helpers)
// Detects: promises
// ============================================================
const p1 = new Promise((resolve, reject) => resolve(42));
const p2 = Promise.resolve(1);
const p3 = Promise.reject(new Error("nope"));
Promise.all([p1, p2]).then((vals) => console.log(vals));
Promise.allSettled([p1, p3]).then((vals) => console.log(vals));
Promise.race([p1, p2]).catch((err) => console.error(err));
Promise.any([p1, p2]).finally(() => console.log("done"));

// ============================================================
// Section 11: BigInt
// Detects: bigint
// ============================================================
const big1 = 9007199254740993n;
const big2 = BigInt("123456789012345678901234567890");

// ============================================================
// Section 12: Built-in collections (Map, Set, WeakMap, WeakSet)
// Detects: es6-map (and similar)
// ============================================================
const map = new Map();
map.set("key", "value");
map.get("key");

const set = new Set([1, 2, 3]);
set.add(4);
set.has(2);

const weakMap = new WeakMap();
const weakSet = new WeakSet();

// ============================================================
// Section 13: Symbol, Proxy, Reflect
// Detects: es6-symbol, proxy, reflect
// ============================================================
const id = Symbol("id");
const labels = Symbol.for("labels");

const handler = {
    get(target, prop) {
        return prop in target ? target[prop] : `missing:${String(prop)}`;
    },
    set(target, prop, value) {
        target[prop] = value;
        return true;
    },
};
const proxied = new Proxy({}, handler);

const reflected = Reflect.ownKeys({ a: 1, b: 2 });
const has = Reflect.has({ x: 1 }, "x");

// ============================================================
// Section 14: Array methods
// Detects: array-includes (via [].includes), array-find, array-flat, etc.
// ============================================================
const nums = [1, 2, 3, 4, 5];
const has2 = nums.includes(2);
const found = nums.find((n) => n > 2);
const idx = nums.findIndex((n) => n === 3);
const last = nums.findLast((n) => n < 4);
const lastIdx = nums.findLastIndex((n) => n < 4);
const flatNested = [1, [2, [3, [4]]]].flat(Infinity);
const mapped = nums.flatMap((n) => [n, n * 2]);
const filled = new Array(5).fill(0);
const copied = nums.copyWithin(0, 3);

// ============================================================
// Section 15: String methods
// Detects: es6-string-includes (via "".includes), pad-start-end, etc.
// ============================================================
const text = "hello world";
const hasWorld = text.includes("world");
const startsHello = text.startsWith("hello");
const endsWorld = text.endsWith("world");
const padded = "5".padStart(3, "0");
const trimmedStart = "  hi".trimStart();
const trimmedEnd = "hi  ".trimEnd();
const replaced = "abc abc".replaceAll("abc", "xyz");
const charAt = "abc".at(-1);

// ============================================================
// Section 16: Object methods
// Detects: object-fromentries, object-values, object-entries
// ============================================================
const obj = { a: 1, b: 2, c: 3 };
const entries = Object.entries(obj);
const values = Object.values(obj);
const keys = Object.keys(obj);
const reconstructed = Object.fromEntries(entries);
const frozen = Object.freeze({ x: 1 });
const hasOwn = Object.hasOwn(obj, "a");

// ============================================================
// Section 17: Numeric methods
// ============================================================
const isInt = Number.isInteger(42);
const isSafe = Number.isSafeInteger(2 ** 53 - 1);
const isFiniteN = Number.isFinite(1 / 0);
const isNaNN = Number.isNaN(NaN);
const eps = Number.EPSILON;

// ============================================================
// Section 18: Async runtime utilities
// Detects: requestanimationframe, requestidlecallback,
//          queuemicrotask, mdn-api_structuredclone
// ============================================================
requestAnimationFrame((ts) => console.log("frame", ts));
const animId = requestAnimationFrame(() => {});
cancelAnimationFrame(animId);
requestIdleCallback((deadline) => console.log("idle", deadline));
queueMicrotask(() => console.log("microtask"));
const cloneOfObj = structuredClone({ a: 1, b: { c: 2 } });

// ============================================================
// Section 19: Fetch API and observers
// Detects: fetch, intersectionobserver, mutationobserver, resizeobserver
// ============================================================
fetch("/api/data").then((r) => r.json()).catch((e) => console.error(e));
fetch("/api/data", { method: "POST", body: JSON.stringify({ a: 1 }) });

const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => console.log(e.isIntersecting));
});
const mo = new MutationObserver((records) => {
    records.forEach((r) => console.log(r.type));
});
const ro = new ResizeObserver((entries) => {
    entries.forEach((e) => console.log(e.contentRect));
});

// ============================================================
// Section 20: Storage APIs and workers
// Detects: namevalue-storage, indexeddb2, webworkers, serviceworkers
// ============================================================
localStorage.setItem("key", "value");
const stored = localStorage.getItem("key");
sessionStorage.setItem("temp", "data");

const dbReq = indexedDB.open("MyDB", 1);
dbReq.onsuccess = () => console.log("db open");
dbReq.onerror = () => console.error("db error");

if (typeof Worker !== "undefined") {
    const worker = new Worker("worker.js");
    worker.postMessage({ task: "compute" });
    worker.onmessage = (e) => console.log(e.data);
}

if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js");
}

// ============================================================
// Section 21: WebSocket, EventSource, BroadcastChannel
// Detects: websockets, eventsource, broadcastchannel
// ============================================================
const ws = new WebSocket("wss://example.com/socket");
ws.addEventListener("message", (e) => console.log(e.data));
ws.send(JSON.stringify({ ping: true }));

const sse = new EventSource("/events");
sse.addEventListener("update", (e) => console.log(e.data));

const bc = new BroadcastChannel("app-channel");
bc.postMessage({ hello: "everyone" });
bc.onmessage = (e) => console.log(e.data);

// ============================================================
// Section 22: Crypto, encoding, blobs
// Detects: cryptography, textencoder, atob-btoa, bloburls, fileapi
// ============================================================
const buf = new Uint8Array(16);
crypto.getRandomValues(buf);
const subtle = crypto.subtle;

const encoder = new TextEncoder();
const decoder = new TextDecoder("utf-8");
const encoded = encoder.encode("hello");
const decoded = decoder.decode(encoded);

const encodedB64 = btoa("hello world");
const decodedB64 = atob(encodedB64);

const blob = new Blob(["text"], { type: "text/plain" });
const blobUrl = URL.createObjectURL(blob);
URL.revokeObjectURL(blobUrl);

const file = new File(["content"], "file.txt", { type: "text/plain" });
const reader = new FileReader();
reader.readAsText(file);

// ============================================================
// Section 23: URL APIs
// Detects: url, urlsearchparams
// ============================================================
const url = new URL("https://example.com/path?x=1&y=2");
console.log(url.hostname);
const params = new URLSearchParams("?x=1&y=2");
params.append("z", "3");

// ============================================================
// Section 24: Notifications, geolocation, page visibility, fullscreen
// Detects: notifications, geolocation, pagevisibility, fullscreen
// ============================================================
if ("Notification" in window) {
    Notification.requestPermission().then((perm) => {
        if (perm === "granted") {
            new Notification("Hello", { body: "World" });
        }
    });
}

navigator.geolocation.getCurrentPosition(
    (pos) => console.log(pos.coords),
    (err) => console.error(err),
);
navigator.geolocation.watchPosition((pos) => console.log(pos));

document.addEventListener("visibilitychange", () => {
    console.log(document.visibilityState);
});

document.documentElement.requestFullscreen();
document.exitFullscreen();

// ============================================================
// Section 25: Clipboard, AbortController, FormData
// Detects: async-clipboard
// ============================================================
navigator.clipboard.writeText("copy this").then(() => console.log("copied"));
navigator.clipboard.readText().then((t) => console.log(t));

const ac = new AbortController();
fetch("/api/slow", { signal: ac.signal });
setTimeout(() => ac.abort(), 5000);

const form = new FormData();
form.append("name", "Eman");
form.append("file", blob);

// ============================================================
// Section 26: Event listeners (various event types)
// Detects: hashchange, online-status, fullscreen events,
//          deviceorientation, gamepad
// ============================================================
window.addEventListener("hashchange", () => console.log("hash changed"));
window.addEventListener("online", () => console.log("online"));
window.addEventListener("offline", () => console.log("offline"));
window.addEventListener("DOMContentLoaded", () => console.log("ready"));
document.addEventListener("fullscreenchange", () => console.log("fs change"));
window.addEventListener("deviceorientation", (e) => console.log(e.alpha));
window.addEventListener("gamepadconnected", (e) => console.log(e.gamepad));
window.addEventListener("focusin", () => console.log("focus in"));
window.addEventListener("pageshow", () => console.log("page show"));

// ============================================================
// Section 27: Pointer events, touch, vibration
// Detects: pointer, touch, vibration
// ============================================================
document.addEventListener("pointerdown", (e) => console.log(e.pressure));
document.addEventListener("pointermove", (e) => console.log(e.x, e.y));
document.addEventListener("touchstart", (e) => e.preventDefault());

if ("vibrate" in navigator) {
    navigator.vibrate(200);
    navigator.vibrate([100, 50, 100]);
}

// ============================================================
// Section 28: Speech, payment, web share
// Detects: speech-synthesis, speech-recognition, payment-request, web-share
// ============================================================
if ("speechSynthesis" in window) {
    const utter = new SpeechSynthesisUtterance("Hello");
    speechSynthesis.speak(utter);
}

if ("share" in navigator) {
    navigator.share({ title: "Hi", text: "From the test", url: "/" });
}

// ============================================================
// Section 29: Console and timing APIs
// Detects: console-time, high-resolution-time, user-timing
// ============================================================
console.time("benchmark");
console.timeLog("benchmark", "halfway");
console.timeEnd("benchmark");

const t0 = performance.now();
performance.mark("start");
performance.measure("setup", "start");
const t1 = performance.now();
console.log(`Took ${t1 - t0}ms`);

// ============================================================
// Section 30: typed arrays, shared buffer, atomics
// Detects: typedarrays, sharedarraybuffer
// ============================================================
const i32 = new Int32Array(8);
const u8 = new Uint8Array([1, 2, 3]);
const f32 = new Float32Array([1.1, 2.2]);

if (typeof SharedArrayBuffer !== "undefined") {
    const sab = new SharedArrayBuffer(1024);
    const view = new Int32Array(sab);
    Atomics.store(view, 0, 42);
}

// ============================================================
// Section 31: Strict mode and module syntax (commented to keep file scriptable)
// Detects: use-strict (the directive below)
// ============================================================
"use strict";

// import { something } from "./module.js";
// export const foo = 1;

// ============================================================
// Negative cases
// These should NOT add any new detections. Comments and string literals are
// stripped before regex matching, and user identifiers are not the globals
// they share names with.
// ============================================================

// Comment: mentions of fetch, Promise, async, await, BigInt, structuredClone.
/* Block comment with class, extends, super, yield, import, export. */

const stringMentions1 = "this string mentions fetch and Promise but should not detect";
const stringMentions2 = "class Foo extends Bar with yield and async";
const stringMentions3 = `template with ${"interpolation"} that mentions await and BigInt`;

function helperThatLooksLikeAPI() {
    return 1;
}

const length = 10;
const value = "ok";
const result = helperThatLooksLikeAPI();
