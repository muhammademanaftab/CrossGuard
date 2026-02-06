/**
 * JS Custom Rules Test - No False Positives
 * Ensures custom rules don't trigger on unrelated JavaScript
 *
 * Prerequisites: Same custom rules as 01_custom_api_detection.js
 *
 * Expected custom features: NONE
 * Expected built-in features: const, let, arrow-functions
 */

// Regular JavaScript - should NOT trigger custom rules

const x = 1;
let y = 2;
const add = (a, b) => a + b;

// Mentions "scheduler" in a variable name, not the API
const taskScheduler = {
    queue: [],
    addTask: function(task) {
        this.queue.push(task);
    }
};

// Mentions "compression" in a string, not the API
const config = {
    compressionEnabled: true,
    compressionLevel: 9,
    message: "CompressionStream is cool but this is just a string"
};

// Normal URL usage, not URLPattern
const url = new URL('https://example.com/path');

// Regular function calls that look similar but aren't custom rules
function process() {
    console.log('Processing...');
}

// Expected features:
// Custom: NONE (no custom patterns should match)
// Built-in: const, let, arrow-functions
