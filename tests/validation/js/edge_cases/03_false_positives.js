/**
 * Edge Case: Potential False Positives
 * Tests cases where patterns might match incorrectly
 *
 * This file checks that the parser correctly identifies ACTUAL features
 * and doesn't get confused by similar-looking but unrelated code.
 */

// Variable names that look like features but aren't features
const fetchData = 'not the fetch API';
const promiseValue = 42;
const localStorageKey = 'key';
const webSocketUrl = 'wss://test';
const observerPattern = 'design pattern';

// Property names that might trigger false positives
const config = {
    fetch: true,        // Not the fetch API
    promise: 'value',   // Not a Promise
    async: false,       // Not async keyword
    await: 'nothing',   // Not await keyword
    map: 'location',    // Not Array.map or Map
    set: 'value'        // Not Set
};

// Method names on custom objects (NOT the standard APIs)
const myObj = {
    querySelector: function(s) { return s; },  // Not document.querySelector
    classList: { add: () => {} },              // Not Element.classList
    localStorage: { get: () => {} }            // Not window.localStorage
};

// Calling custom methods (these SHOULD NOT trigger standard API detection)
myObj.querySelector('.test');
myObj.classList.add('class');

// BUT these SHOULD be detected as real features:
document.querySelector('.real');          // Real querySelector
element.classList.add('real-class');      // Real classList
localStorage.setItem('k', 'v');           // Real localStorage

// Function names that might cause confusion
function fetchUser() { return null; }     // Not fetch API
function mapData(arr) { return arr; }     // Not Array.map
function setConfig(c) { return c; }       // Not Set

// Object property access that might look like features
const user = { match: () => true };
user.match('pattern');  // Not String.match exactly

// Array that happens to have method-like property names
const arr = ['map', 'filter', 'reduce', 'forEach'];

// ACTUAL features that SHOULD be detected:
const actualPromise = new Promise((resolve) => resolve(1));
actualPromise.then(x => x);

const actualMap = new Map();
actualMap.set('key', 'value');

[1, 2, 3].map(x => x * 2);
[1, 2, 3].filter(x => x > 1);
[1, 2, 3].forEach(x => console.log(x));

// Check that real fetch is detected
fetch('/real/api/endpoint');

// Real async/await
async function realAsync() {
    const data = await fetch('/api');
    return data;
}
