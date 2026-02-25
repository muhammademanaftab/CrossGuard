// Modern JavaScript Features for Testing

// Arrow functions
const greet = (name) => `Hello, ${name}!`;      // → "const" + "arrow-functions" + "template-literals"

// Async/await
async function fetchData() {                     // → "async-functions"
    try {
        const response = await fetch('https://api.example.com/data'); // → "fetch"
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);          // → "console-basic"
    }
}

// Optional chaining
const user = {
    profile: {
        name: 'John'
    }
};
const userName = user?.profile?.name;            // → "mdn-javascript_operators_optional_chaining"

// Nullish coalescing
const value = null ?? 'default value';           // → "mdn-javascript_operators_nullish_coalescing"

// Array methods
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);         // → "es5"
const flattened = [[1, 2], [3, 4]].flat();       // → "array-flat"
const found = numbers.find(n => n > 3);          // → "array-find"

// Object methods
const obj1 = { a: 1 };
const obj2 = { b: 2 };
const merged = Object.assign({}, obj1, obj2);
const entries = Object.entries(obj1);            // → "object-entries"

// Promises
const promise = new Promise((resolve, reject) => { // → "promises"
    setTimeout(() => resolve('Done!'), 1000);
});

// Classes
class Animal {                                   // → "es6-class"
    constructor(name) {
        this.name = name;
    }

    speak() {
        console.log(`${this.name} makes a sound`);
    }
}

// Template literals
const message = `User ${userName} logged in`;    // → "template-literals"

// Destructuring
const { profile } = user;                       // → "es6" (destructuring + spread share this)
const [first, second] = numbers;                // → "es6"

// Spread operator
const newArray = [...numbers, 6, 7];            // → "es6"
const newObj = { ...obj1, c: 3 };               // → "es6"

// Modern APIs
const observer = new IntersectionObserver((entries) => { // → "intersectionobserver"
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            console.log('Element is visible');
        }
    });
});

// Web Storage
localStorage.setItem('key', 'value');            // → "namevalue-storage"
const stored = localStorage.getItem('key');      // → "namevalue-storage"

// Fetch API
fetch('https://api.example.com/data')            // → "fetch"
    .then(response => response.json())           // → "promises" (.then is a Promise method)
    .then(data => console.log(data));

// BigInt
const bigNumber = 9007199254740991n;             // → "bigint"

// String methods
const text = 'Hello World';
const replaced = text.replaceAll('o', '0');      // → "es6-string-includes"
const trimmed = text.trim();

// Array.includes
const hasThree = numbers.includes(3);            // → "array-includes"
// Score: 90.0 | Grade: A | 20 features found
