// Test file for custom JavaScript rules

// This will be detected by custom rule (maps to fetch)
async function getData() {
    const result = await myCustomFetch('/api/data');
    return result;
}

// Standard JS features for comparison
const items = [1, 2, 3];
const doubled = items.map(x => x * 2);

// Promise-based code
fetch('/api/users')
    .then(response => response.json())
    .then(data => console.log(data));

// Modern JS
const obj = { a: 1, b: 2, ...otherObj };
