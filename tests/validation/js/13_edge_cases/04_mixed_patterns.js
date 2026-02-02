/**
 * Edge Case: Mixed and Complex Patterns
 * Tests various edge cases and unusual but valid patterns
 *
 * Expected features: Multiple features in unusual contexts
 */

// Arrow functions in various contexts
const a1 = () => {};
const a2 = x => x;
const a3 = (x, y) => x + y;
const a4 = (...args) => args;
const a5 = ({ x, y }) => x + y;
const a6 = ([a, b]) => a + b;

// Async in various forms
async function fn1() {}
const fn2 = async () => {};
const fn3 = async function() {};
const obj = { async method() {} };
class C { async method() {} }

// Promises in various contexts
Promise.resolve(1);
Promise.reject(new Error('e'));
Promise.all([]);
Promise.race([]);
Promise.allSettled([]);
new Promise(r => r());

// Chained promises
fetch('/a').then(r => r.json()).then(d => d).catch(e => e).finally(() => {});

// Template literals edge cases
const t1 = `simple`;
const t2 = `with ${variable}`;
const t3 = `nested ${`inner ${value}`}`;
const t4 = `multi
line`;
const tagged = tag`tagged ${template}`;

// Destructuring edge cases
const { a } = obj;
const { a: b } = obj;
const { a = 1 } = obj;
const { a: b = 1 } = obj;
const { a, ...rest } = obj;
const [x] = arr;
const [x, , z] = arr;
const [x = 1] = arr;
const [x, ...rest2] = arr;

// Rest parameters
function f1(...args) {}
const f2 = (...args) => {};
function f3(a, b, ...rest) {}

// Spread operator
const arr1 = [...arr];
const obj1 = { ...obj };
fn(...args);
Math.max(...numbers);

// Classes edge cases
class Base {}
class Derived extends Base {}
const NamedClass = class Named {};
const AnonymousClass = class {};

// Generators
function* gen1() { yield 1; }
const gen2 = function*() { yield 2; };
const genObj = { *gen() { yield 3; } };
class GenClass { *method() { yield 4; } }

// Various API patterns
document.querySelector?.('.el');                    // Optional chaining
document.querySelector('.el')?.classList?.add('c'); // Chained optional
localStorage?.getItem?.('key');                     // Optional on built-in

// Async iteration
async function asyncIter() {
    for await (const x of asyncIterable) {
        console.log(x);
    }
}

// Dynamic property names
const prop = 'method';
const obj2 = {
    [prop]() {},
    [`computed_${name}`]: value
};

// Shorthand methods
const obj3 = {
    method() {},
    async asyncMethod() {},
    *generatorMethod() {},
    get getter() { return this.value; },
    set setter(v) { this.value = v; }
};

// Proxy
const handler = {
    get(target, prop) { return target[prop]; },
    set(target, prop, value) { target[prop] = value; return true; }
};
const proxy = new Proxy({}, handler);

// Symbol usage
const sym = Symbol('description');
const sym2 = Symbol.for('global');
const wellKnown = Symbol.iterator;

// BigInt
const big1 = BigInt(123);
const big2 = 123n;
const bigCalc = 1n + 2n;

// Nullish coalescing and optional chaining (not directly Can I Use features, but modern syntax)
const val1 = null ?? 'default';
const val2 = obj?.prop?.nested;
const val3 = arr?.[0];
const val4 = fn?.();
