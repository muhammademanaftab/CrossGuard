/**
 * JS Custom Rules Test - Word Boundary Pattern Matching
 * Tests that \b word boundaries in custom patterns work correctly
 *
 * Prerequisites: Add to custom_rules.json under "javascript":
 *   "test-eye-dropper": {
 *     "patterns": ["\\bnew\\s+EyeDropper\\b"],
 *     "description": "EyeDropper API"
 *   },
 *   "test-barcode-api": {
 *     "patterns": ["\\bnew\\s+BarcodeDetector\\b"],
 *     "description": "Barcode Detection API"
 *   }
 *
 * Expected custom features: test-eye-dropper, test-barcode-api
 * NOT expected: These patterns should NOT trigger on substrings
 */

// === EyeDropper API (test-eye-dropper) ===
// Should match:
const eyeDropper = new EyeDropper();
const result = await eyeDropper.open();
console.log(result.sRGBHex);

// Should NOT match (no word boundary match):
const myEyeDropperWrapper = 'just a string';
const NotAnEyeDropperUsage = false;

// === Barcode Detection API (test-barcode-api) ===
// Should match:
const detector = new BarcodeDetector({ formats: ['qr_code'] });
const barcodes = await detector.detect(imageElement);

// Should NOT match (substring, no word boundary):
const fakeBarcodeDetectorName = 'testing';

// === Built-in features ===
const data = await fetch('/api');

// Expected features:
// Custom: test-eye-dropper, test-barcode-api
// Built-in: const, async-functions, fetch
