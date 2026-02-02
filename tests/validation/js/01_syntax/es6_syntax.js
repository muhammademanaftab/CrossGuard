/**
 * ES6+ Syntax Features Test File
 * Tests detection of modern JavaScript syntax features
 */

// === Arrow Functions (arrow-functions) ===
const add = (a, b) => a + b;
const square = x => x * x;
const greet = () => console.log('Hello');
const process = (data) => {
    return data.map(x => x * 2);
};

// === Async Functions (async-functions) ===
async function fetchData() {
    const response = await fetch('/api/data');
    return await response.json();
}

const asyncArrow = async () => {
    await Promise.resolve();
};

async function withTryCatch() {
    try {
        await someAsyncOperation();
    } catch (error) {
        console.error(error);
    }
}

// === Const Declaration (const) ===
const PI = 3.14159;
const CONFIG = { debug: true };
const ITEMS = ['a', 'b', 'c'];

// === Let Declaration (let) ===
let counter = 0;
let message = 'Hello';
for (let i = 0; i < 10; i++) {
    counter += i;
}

// === Template Literals (template-literals) ===
const name = 'World';
const greeting = `Hello, ${name}!`;
const multiline = `
    This is a
    multiline string
`;
const nested = `Outer ${`inner ${1 + 2}`}`;

// === ES6 Features - Destructuring & Spread (es6) ===
const { x, y } = { x: 1, y: 2 };
const [first, second] = [1, 2];
const { a, ...rest } = { a: 1, b: 2, c: 3 };
const combined = [...[1, 2], ...[3, 4]];
const obj = { ...{ a: 1 }, b: 2 };

// === Rest Parameters (rest-parameters) ===
function sum(...numbers) {
    return numbers.reduce((a, b) => a + b, 0);
}

const arrowRest = (...args) => args.length;

// === ES6 Classes (es6-class) ===
class Animal {
    constructor(name) {
        this.name = name;
    }

    speak() {
        console.log(`${this.name} makes a sound`);
    }
}

class Dog extends Animal {
    speak() {
        console.log(`${this.name} barks`);
    }
}

// === ES6 Generators (es6-generators) ===
function* numberGenerator() {
    yield 1;
    yield 2;
    yield 3;
}

function* infiniteGenerator() {
    let i = 0;
    while (true) {
        yield i++;
    }
}

// === Use Strict (use-strict) ===
"use strict";
'use strict';

// Expected features:
// - arrow-functions
// - async-functions
// - const
// - let
// - template-literals
// - es6 (destructuring, spread)
// - rest-parameters
// - es6-class
// - es6-generators
// - use-strict
