/**
 * Performance and Timing APIs Test File
 * Tests detection of performance monitoring APIs
 */

// === High Resolution Time (high-resolution-time) ===
const startTime = performance.now();
// ... do work
const endTime = performance.now();
console.log(`Took ${endTime - startTime}ms`);

performance.mark('start');
// ... do work
performance.mark('end');

// === User Timing API (user-timing) ===
performance.mark('fetchStart');
// ... fetch data
performance.mark('fetchEnd');
performance.measure('fetch', 'fetchStart', 'fetchEnd');

const measures = performance.getEntriesByType('measure');

// === Resource Timing (resource-timing) ===
const resources = performance.getEntries();
const resourceEntry = new PerformanceResourceTiming();
const timing = performance.getEntriesByType('resource')[0];
console.log('Duration:', timing.duration);

// === Navigation Timing (nav-timing) ===
const navTiming = performance.timing;
const loadTime = navTiming.loadEventEnd - navTiming.navigationStart;

const navigation = performance.navigation;
console.log('Redirects:', navigation.redirectCount);

// === Server Timing (server-timing) ===
const serverTiming = performance.getEntriesByType('navigation')[0].serverTiming;
const serverTimingEntry = new PerformanceServerTiming();

// === console.time/timeEnd (console-time) ===
console.time('operation');
// ... operation
console.timeEnd('operation');

console.time('loop');
for (let i = 0; i < 1000; i++) {}
console.timeEnd('loop');

// === Basic Console (console-basic) ===
console.log('Log message');
console.warn('Warning message');
console.error('Error message');

// === Beacon API (beacon) ===
navigator.sendBeacon('/analytics', JSON.stringify({ event: 'pageview' }));
const sent = sendBeacon('/log', data);

// Expected features:
// - high-resolution-time
// - user-timing
// - resource-timing
// - nav-timing
// - server-timing
// - console-time
// - console-basic
// - beacon
