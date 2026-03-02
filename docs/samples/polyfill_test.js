// Test file to trigger polyfill recommendations
// Uses features that have entries in polyfill_map.json

// Fetch API
fetch('/api/data').then(res => res.json());

// Promises
const p = new Promise((resolve) => resolve(42));

// IntersectionObserver
const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => console.log(e));
});

// ResizeObserver
const resizer = new ResizeObserver((entries) => {
    console.log(entries);
});

// AbortController
const controller = new AbortController();

// structuredClone
const copy = structuredClone({ name: "test" });

// URLSearchParams
const params = new URLSearchParams("foo=bar");

// TextEncoder
const encoder = new TextEncoder();

// requestIdleCallback
requestIdleCallback(() => console.log("idle"));

// BroadcastChannel
const channel = new BroadcastChannel("updates");

// Array.includes
[1, 2, 3].includes(2);

// Object.entries
Object.entries({ a: 1 });

// globalThis
console.log(globalThis);
