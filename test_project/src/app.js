// Modern JavaScript Features for Testing

// ES6+ Features
const greeting = `Hello, World!`;
const [first, ...rest] = [1, 2, 3, 4, 5];
const { name, age } = { name: 'John', age: 30 };

// Arrow Functions
const multiply = (a, b) => a * b;

// Classes
class User {
    #privateField = 'secret';

    constructor(name) {
        this.name = name;
    }

    static create(name) {
        return new User(name);
    }
}

// Async/Await
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}

// Promises
const promise = new Promise((resolve, reject) => {
    setTimeout(() => resolve('Done!'), 1000);
});

promise.then(result => console.log(result));

// Optional Chaining & Nullish Coalescing
const user = { profile: { name: 'Alice' } };
const userName = user?.profile?.name ?? 'Anonymous';

// Array Methods
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
const evens = numbers.filter(n => n % 2 === 0);
const sum = numbers.reduce((acc, n) => acc + n, 0);
const found = numbers.find(n => n > 3);
const hasEven = numbers.some(n => n % 2 === 0);
const allPositive = numbers.every(n => n > 0);
const flattened = [[1, 2], [3, 4]].flat();
const included = numbers.includes(3);

// Object Methods
const keys = Object.keys(user);
const values = Object.values(user);
const entries = Object.entries(user);
const merged = Object.assign({}, user, { age: 25 });

// Modern APIs
// Intersection Observer
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            console.log('Element visible');
        }
    });
});

// Resize Observer
const resizeObserver = new ResizeObserver((entries) => {
    for (let entry of entries) {
        console.log('Size changed:', entry.contentRect);
    }
});

// Mutation Observer
const mutationObserver = new MutationObserver((mutations) => {
    mutations.forEach(mutation => console.log(mutation));
});

// Web Storage
localStorage.setItem('key', 'value');
sessionStorage.setItem('temp', 'data');

// Geolocation
navigator.geolocation.getCurrentPosition(
    position => console.log(position.coords),
    error => console.error(error)
);

// Fetch API
fetch('https://api.example.com/data')
    .then(res => res.json())
    .then(data => console.log(data));

// Web Workers
const worker = new Worker('worker.js');
worker.postMessage({ task: 'process' });

// Service Worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
}

// WebSocket
const socket = new WebSocket('wss://example.com/socket');
socket.onmessage = (event) => console.log(event.data);

// Broadcast Channel
const channel = new BroadcastChannel('my_channel');
channel.postMessage('Hello from another tab!');

// Clipboard API
navigator.clipboard.writeText('Copied text');

// Dialog Element
const dialog = document.getElementById('myDialog');
dialog?.showModal();

// Console
console.log('Log message');
console.warn('Warning message');
console.error('Error message');
console.table({ a: 1, b: 2 });
