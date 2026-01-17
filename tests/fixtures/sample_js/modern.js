/**
 * Modern JavaScript Sample File for Testing
 * Contains various ES6+ features and Web APIs
 */

// ES6 Variable Declarations
const APP_NAME = 'Cross Guard';
let counter = 0;

// Arrow Functions
const add = (a, b) => a + b;
const multiply = (a, b) => {
    return a * b;
};

// Template Literals
const greet = (name) => `Hello, ${name}! Welcome to ${APP_NAME}.`;

// Destructuring
const user = { name: 'John', age: 30, email: 'john@example.com' };
const { name, age } = user;

const numbers = [1, 2, 3, 4, 5];
const [first, second, ...rest] = numbers;

// Spread Operator
const newNumbers = [...numbers, 6, 7, 8];
const userCopy = { ...user, role: 'admin' };

// Rest Parameters
function sum(...args) {
    return args.reduce((acc, val) => acc + val, 0);
}

// ES6 Classes
class Animal {
    constructor(name) {
        this.name = name;
    }

    speak() {
        return `${this.name} makes a sound.`;
    }
}

class Dog extends Animal {
    constructor(name, breed) {
        super(name);
        this.breed = breed;
    }

    speak() {
        return `${this.name} barks!`;
    }
}

// Async/Await
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Async Arrow Function
const getData = async () => {
    const result = await fetchData('/api/data');
    return result;
};

// Promises
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

new Promise((resolve, reject) => {
    setTimeout(() => resolve('Done!'), 1000);
})
    .then(result => console.log(result))
    .catch(error => console.error(error));

// Array Methods
const items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

const doubled = items.map(n => n * 2);
const evens = items.filter(n => n % 2 === 0);
const sum2 = items.reduce((acc, n) => acc + n, 0);
const found = items.find(n => n > 5);
const foundIndex = items.findIndex(n => n > 5);
const hasEven = items.some(n => n % 2 === 0);
const allPositive = items.every(n => n > 0);
const includes5 = items.includes(5);
const flat = [[1, 2], [3, 4]].flat();
const flatMapped = items.flatMap(n => [n, n * 2]);

// String Methods
const text = '  Hello World  ';
const trimmed = text.trim();
const starts = text.startsWith('  Hello');
const ends = text.endsWith('  ');
const includesWorld = text.includes('World');
const repeated = 'abc'.repeat(3);
const padStart = '5'.padStart(3, '0');
const padEnd = '5'.padEnd(3, '0');

// Object Methods
const keys = Object.keys(user);
const values = Object.values(user);
const entries = Object.entries(user);
const assigned = Object.assign({}, user, { role: 'user' });
const frozen = Object.freeze({ x: 1 });

// ES6 Built-ins
const map = new Map();
map.set('key', 'value');
const value = map.get('key');

const set = new Set([1, 2, 3, 3, 3]);
set.add(4);

const weakMap = new WeakMap();
const weakSet = new WeakSet();

const symbol = Symbol('description');

// BigInt
const bigNumber = BigInt(9007199254740991);
const anotherBig = 123456789012345678901234567890n;

// Optional Chaining and Nullish Coalescing
const optionalUser = { profile: { name: 'John' } };
const userName = optionalUser?.profile?.name;
const defaultValue = null ?? 'default';

// Generators
function* numberGenerator() {
    yield 1;
    yield 2;
    yield 3;
}

// Web APIs
// Intersection Observer
const intersectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.5 });

// Resize Observer
const resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
        console.log('Element size:', entry.contentRect);
    }
});

// Mutation Observer
const mutationObserver = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
        console.log('Mutation:', mutation.type);
    });
});

// Local Storage
localStorage.setItem('user', JSON.stringify(user));
const storedUser = JSON.parse(localStorage.getItem('user'));
localStorage.removeItem('user');

// Session Storage
sessionStorage.setItem('session', 'active');
const sessionData = sessionStorage.getItem('session');

// DOM APIs
const element = document.querySelector('.container');
const elements = document.querySelectorAll('.item');

element?.classList.add('active');
element?.classList.remove('inactive');
element?.classList.toggle('visible');

const dataValue = element?.dataset.value;

// Proxy
const handler = {
    get: function(target, prop) {
        return prop in target ? target[prop] : 'Not found';
    }
};
const proxy = new Proxy(user, handler);

// Custom Elements
class MyElement extends HTMLElement {
    connectedCallback() {
        this.innerHTML = '<p>Hello from custom element!</p>';
    }
}
customElements.define('my-element', MyElement);

// Export (for modules)
export { Animal, Dog, fetchData, getData };
export default APP_NAME;
