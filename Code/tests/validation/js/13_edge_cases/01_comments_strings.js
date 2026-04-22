/**
 * Edge Case: Comments and Strings
 * Tests that features inside comments/strings are NOT detected
 * (unless they're actual code)
 *
 * Expected features: const, let, arrow-functions, queryselector, json
 * NOT expected: fetch, localStorage, WebSocket (they're in comments/strings)
 */

// This should NOT detect fetch:
// fetch('/api/data').then(r => r.json())

/*
   This multi-line comment mentions localStorage
   localStorage.setItem('key', 'value')
   But it should NOT be detected
*/

/**
 * @example
 * // Example code in JSDoc - should NOT be detected
 * const ws = new WebSocket('wss://example.com');
 * navigator.geolocation.getCurrentPosition(callback);
 */

// Actual code that SHOULD be detected:
const message = 'Hello World';
let count = 0;

const greet = (name) => {
    return `Hello, ${name}!`;
};

// String containing feature-like text - should NOT trigger detection
const text = "We use localStorage for persistence";
const info = 'Try fetch for API calls';
const url = "Check out WebSocket at wss://example.com";

// Template literal with feature-like text - should NOT trigger
const docs = `
To save data, use localStorage.setItem('key', 'value');
To fetch data, call fetch('/api/endpoint');
For real-time, use new WebSocket('wss://server');
`;

// Actual code that SHOULD be detected:
const element = document.querySelector('#app');
const data = JSON.parse('{"key": "value"}');
const jsonStr = JSON.stringify({ a: 1 });

// More comments with "false positive" content:
// Promise.all([p1, p2]) - just a comment
// IntersectionObserver - mentioned but not used
// new Worker('worker.js') - this is a comment

// End of test file
console.log('Edge case test loaded');
