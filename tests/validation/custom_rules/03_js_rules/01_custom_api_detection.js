/**
 * JS Custom Rules Test - Custom API Detection
 * Tests that custom JavaScript rules defined in custom_rules.json are detected
 *
 * Prerequisites: Add to custom_rules.json under "javascript":
 *   "test-scheduler-api": {
 *     "patterns": ["\\bscheduler\\.postTask\\s*\\(", "\\bscheduler\\.yield\\s*\\("],
 *     "description": "Scheduler API"
 *   },
 *   "test-compression-api": {
 *     "patterns": ["\\bCompressionStream\\b", "\\bDecompressionStream\\b"],
 *     "description": "Compression Streams API"
 *   },
 *   "test-url-pattern": {
 *     "patterns": ["\\bnew\\s+URLPattern\\b"],
 *     "description": "URL Pattern API"
 *   }
 *
 * Expected custom features: test-scheduler-api, test-compression-api, test-url-pattern
 * Expected built-in features: promises, const, arrow-functions, async-functions
 */

// === Scheduler API (test-scheduler-api) ===
const lowPriTask = scheduler.postTask(() => {
    console.log('Low priority task');
}, { priority: 'background' });

async function processItems(items) {
    for (const item of items) {
        await scheduler.yield();
        processItem(item);
    }
}

// === Compression Streams API (test-compression-api) ===
const compressedStream = new CompressionStream('gzip');
const readable = response.body.pipeThrough(compressedStream);

const decompressor = new DecompressionStream('gzip');
const decompressed = compressed.pipeThrough(decompressor);

// === URL Pattern API (test-url-pattern) ===
const pattern = new URLPattern({ pathname: '/users/:id' });
const match = pattern.test('https://example.com/users/123');

// === Built-in features that should still work ===
const fetchData = async () => {
    const response = await fetch('/api/data');
    return new Promise((resolve) => resolve(response));
};

// Expected features:
// Custom: test-scheduler-api, test-compression-api, test-url-pattern
// Built-in: promises, const, arrow-functions, async-functions, fetch
