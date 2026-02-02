/**
 * Array, String, and Object Methods Test File
 * Tests detection of modern array/string/object methods
 */

// === Array.flat/flatMap (array-flat) ===
const nested = [[1, 2], [3, 4]];
const flat = nested.flat();
const deepFlat = [[1, [2, [3]]]].flat(2);
const flatMapped = [1, 2].flatMap(x => [x, x * 2]);

// === Array.includes (array-includes) ===
const hasItem = [1, 2, 3].includes(2);
const hasFromIndex = [1, 2, 3].includes(1, 1);

// === Array.find/findIndex/findLast (array-find) ===
const found = [1, 2, 3].find(x => x > 1);
const foundIndex = [1, 2, 3].findIndex(x => x > 1);
const foundLast = [1, 2, 3, 2].findLast(x => x === 2);
const foundLastIndex = [1, 2, 3, 2].findLastIndex(x => x === 2);

// === Array.findIndex (array-find-index) ===
const idx = ['a', 'b', 'c'].findIndex(x => x === 'b');

// === ES5 Array Methods (es5) ===
[1, 2, 3].forEach(x => console.log(x));
const doubled = [1, 2, 3].map(x => x * 2);
const evens = [1, 2, 3, 4].filter(x => x % 2 === 0);
const sum = [1, 2, 3].reduce((acc, x) => acc + x, 0);
const hasEven = [1, 2, 3].some(x => x % 2 === 0);
const allPositive = [1, 2, 3].every(x => x > 0);

// === String.includes (es6-string-includes) ===
const hasSubstring = 'hello world'.includes('world');
const hasFromPos = 'hello world'.includes('o', 5);

// === String.padStart/padEnd (pad-start-end) ===
const padded = '5'.padStart(3, '0'); // '005'
const paddedEnd = 'hi'.padEnd(5, '!'); // 'hi!!!'

// === Object.entries (object-entries) ===
const entries = Object.entries({ a: 1, b: 2 });
for (const [key, value] of Object.entries(obj)) {
    console.log(key, value);
}

// === Object.values (object-values) ===
const values = Object.values({ a: 1, b: 2 });

// === Object.observe (object-observe) ===
// Deprecated but still detectable
Object.observe(obj, changes => {
    console.log(changes);
});

// === ES6 Built-ins (es6) ===
const map = new Map();
map.set('key', 'value');
map.get('key');

const set = new Set([1, 2, 3]);
set.add(4);
set.has(2);

const weakMap = new WeakMap();
weakMap.set(obj, 'data');

const weakSet = new WeakSet();
weakSet.add(obj);

const sym = Symbol('description');
const globalSym = Symbol.for('global');

Reflect.get(obj, 'prop');
Reflect.set(obj, 'prop', 'value');

// === BigInt (bigint) ===
const big = BigInt(9007199254740991);
const bigLiteral = 9007199254740991n;
const added = 1n + 2n;

// === Proxy (proxy) ===
const proxy = new Proxy(target, {
    get(target, prop) {
        return target[prop];
    },
    set(target, prop, value) {
        target[prop] = value;
        return true;
    }
});

// === ES6 Number Methods (es6-number) ===
Number.isNaN(NaN);
Number.isFinite(100);
Number.parseInt('10');
Number.parseFloat('3.14');
Number.isInteger(5);

// === Internationalization (internationalization) ===
const formatter = new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
});

const dateFormatter = new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long'
});

const collator = new Intl.Collator('de', { sensitivity: 'base' });

// === Intl.PluralRules (intl-pluralrules) ===
const pluralRules = new Intl.PluralRules('en-US');
pluralRules.select(1); // 'one'
pluralRules.select(2); // 'other'

// === Date.toLocaleDateString (date-tolocaledatestring) ===
const dateStr = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric'
});

const timeStr = new Date().toLocaleTimeString('de-DE');

// === localeCompare (localecompare) ===
'a'.localeCompare('b');
'ä'.localeCompare('z', 'de');

// === RegExp Lookbehind (js-regexp-lookbehind) ===
const lookbehind = /(?<=\$)\d+/;
const negativeLookbehind = /(?<!\$)\d+/;

// === URL API (url) ===
const url = new URL('https://example.com/path?query=value');
url.searchParams.get('query');
URL.canParse('https://example.com');

// === URLSearchParams (urlsearchparams) ===
const params = new URLSearchParams('?a=1&b=2');
params.get('a');
params.set('c', '3');
params.append('d', '4');

// Expected features:
// - array-flat
// - array-includes
// - array-find
// - array-find-index
// - es5
// - es6-string-includes
// - pad-start-end
// - object-entries
// - object-values
// - object-observe
// - es6 (Map, Set, Symbol, Reflect)
// - bigint
// - proxy
// - es6-number
// - internationalization
// - intl-pluralrules
// - date-tolocaledatestring
// - localecompare
// - js-regexp-lookbehind
// - url
// - urlsearchparams
