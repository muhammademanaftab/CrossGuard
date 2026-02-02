/**
 * Promises and Async APIs Test File
 * Tests detection of Promise-related and async features
 */

// === Promises (promises) ===
const promise = new Promise((resolve, reject) => {
    setTimeout(() => resolve('Done'), 1000);
});

promise.then(result => console.log(result));
promise.catch(error => console.error(error));

Promise.all([promise1, promise2]).then(results => {
    console.log(results);
});

Promise.race([promise1, promise2]).then(winner => {
    console.log(winner);
});

Promise.resolve('immediate').then(console.log);
Promise.reject(new Error('failed')).catch(console.error);

Promise.allSettled([p1, p2, p3]).then(results => {
    results.forEach(result => console.log(result.status));
});

// === Promise.finally (promise-finally) ===
fetch('/api')
    .then(response => response.json())
    .catch(error => console.error(error))
    .finally(() => {
        console.log('Cleanup complete');
    });

// === Fetch API (fetch) ===
fetch('/api/users')
    .then(response => response.json())
    .then(data => console.log(data));

fetch('/api/data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: 'value' })
});

// === AbortController (abortcontroller) ===
const controller = new AbortController();
const signal = controller.signal;

fetch('/api', { signal })
    .then(response => response.json())
    .catch(error => {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        }
    });

controller.abort();

const abortSignal = AbortSignal.timeout(5000);

// === unhandledrejection Event (unhandledrejection) ===
window.addEventListener('unhandledrejection', event => {
    console.error('Unhandled promise rejection:', event.reason);
});

window.addEventListener('rejectionhandled', event => {
    console.log('Rejection handled');
});

// === Request Animation Frame (requestanimationframe) ===
function animate() {
    // Animation logic
    requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

const animationId = requestAnimationFrame(callback);
cancelAnimationFrame(animationId);

// === Request Idle Callback (requestidlecallback) ===
requestIdleCallback(deadline => {
    while (deadline.timeRemaining() > 0) {
        // Do background work
    }
});

const idleId = requestIdleCallback(callback, { timeout: 2000 });
cancelIdleCallback(idleId);

// === setImmediate (setimmediate) ===
setImmediate(() => {
    console.log('Executed immediately');
});
clearImmediate(immediateId);

// Expected features:
// - promises
// - promise-finally
// - fetch
// - abortcontroller
// - unhandledrejection
// - requestanimationframe
// - requestidlecallback
// - setimmediate
