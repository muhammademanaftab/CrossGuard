/**
 * JS Custom Rules Test - Comments and Strings
 * Verifies custom rules in comments and strings are NOT detected
 *
 * Prerequisites: Same custom rules as 01_custom_api_detection.js
 *
 * Expected custom features: NONE
 * Expected built-in features: const, arrow-functions
 */

// Custom API patterns in comments - should NOT be detected:
// scheduler.postTask(() => doWork());
// new CompressionStream('gzip');
// new URLPattern({ pathname: '/:id' });

/*
 * Multi-line comment with custom API usage:
 * const stream = new CompressionStream('deflate');
 * const dropper = new EyeDropper();
 * const detector = new BarcodeDetector({ formats: ['qr_code'] });
 */

/**
 * JSDoc with custom API examples:
 * @example
 * scheduler.yield();
 * new DecompressionStream('gzip');
 */

// Custom API patterns in strings - should NOT be detected:
const docs1 = "Use scheduler.postTask() for background tasks";
const docs2 = 'Try new CompressionStream("gzip") for compression';
const docs3 = `The URLPattern API: new URLPattern({ pathname: '/:id' })`;

// Actual code that SHOULD be detected:
const greeting = (name) => `Hello, ${name}`;

// Expected features:
// Custom: NONE (all mentions are in comments/strings)
// Built-in: const, arrow-functions, template-literals
