// Modern JavaScript Features for Testing

// Arrow functions
const greet = (name) => `Hello, ${name}!`;

// Async/await
async function fetchData() {
    try {
        const response = await fetch('https://api.example.com/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Optional chaining
const user = {
    profile: {
        name: 'John'
    }
};
const userName = user?.profile?.name;

// Nullish coalescing
const value = null ?? 'default value';

// Array methods
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
const flattened = [[1, 2], [3, 4]].flat();
const found = numbers.find(n => n > 3);

// Object methods
const obj1 = { a: 1 };
const obj2 = { b: 2 };
const merged = Object.assign({}, obj1, obj2);
const entries = Object.entries(obj1);

// Promises
const promise = new Promise((resolve, reject) => {
    setTimeout(() => resolve('Done!'), 1000);
});

// Classes
class Animal {
    constructor(name) {
        this.name = name;
    }
    
    speak() {
        console.log(`${this.name} makes a sound`);
    }
}

// Template literals
const message = `User ${userName} logged in`;

// Destructuring
const { profile } = user;
const [first, second] = numbers;

// Spread operator
const newArray = [...numbers, 6, 7];
const newObj = { ...obj1, c: 3 };

// Modern APIs
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            console.log('Element is visible');
        }
    });
});

// Web Storage
localStorage.setItem('key', 'value');
const stored = localStorage.getItem('key');

// Fetch API
fetch('https://api.example.com/data')
    .then(response => response.json())
    .then(data => console.log(data));

// BigInt
const bigNumber = 9007199254740991n;

// String methods
const text = 'Hello World';
const replaced = text.replaceAll('o', '0');
const trimmed = text.trim();

// Array.includes
const hasThree = numbers.includes(3);
