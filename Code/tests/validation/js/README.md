# JavaScript Validation Test Files

This directory contains comprehensive JavaScript test files to validate the JS parser's feature detection capabilities against the Can I Use database.

## Directory Structure

```
js/
├── 01_syntax/                 # ES6+ syntax features
│   └── es6_syntax.js
├── 02_promises_async/         # Promises and async APIs
│   └── promises_async.js
├── 03_dom_apis/               # DOM manipulation APIs
│   └── dom_apis.js
├── 04_storage/                # Web storage APIs
│   └── web_storage.js
├── 05_observers_workers/      # Observers and Workers
│   └── observers_workers.js
├── 06_device_apis/            # Device/hardware APIs
│   └── device_apis.js
├── 07_media_apis/             # Audio/Video APIs
│   └── media_apis.js
├── 08_modern_apis/            # Modern Web APIs
│   └── modern_apis.js
├── 09_security_auth/          # Security and auth
│   └── security_auth.js
├── 10_methods/                # Array/String/Object methods
│   └── array_string_object.js
├── 11_performance/            # Performance APIs
│   └── performance_timing.js
├── 12_wasm_misc/              # WebAssembly and misc
│   └── wasm_misc.js
├── 13_edge_cases/             # Edge case tests
│   ├── 01_comments_strings.js
│   ├── 02_minified_code.js
│   ├── 03_false_positives.js
│   ├── 04_mixed_patterns.js
│   ├── 05_directive_strings.js
│   └── 06_webgl_canvas.js
├── 14_real_world/             # Real-world code patterns
│   ├── 01_react_app.js
│   ├── 02_vanilla_dashboard.js
│   ├── 03_service_worker.js
│   └── 04_form_validation.js
├── comprehensive_test.js      # All features combined (150+)
├── CHECKLIST.md               # Manual testing checklist
└── README.md                  # This file
```

## Feature Coverage

The JS parser validates against **278 Can I Use feature IDs**, covering:

| Category | Features |
|----------|----------|
| ES6+ Syntax | Arrow functions, async/await, const/let, template literals, classes, generators |
| Promises | Promise API, Promise.finally, async/await patterns |
| DOM APIs | querySelector, classList, dataset, Shadow DOM, Custom Elements |
| Observers | Intersection, Mutation, Resize observers |
| Workers | Web Workers, Shared Workers, Service Workers |
| Storage | localStorage, sessionStorage, IndexedDB |
| File APIs | FileReader, File API, Blob URLs, File System Access |
| Device APIs | Geolocation, Battery, Vibration, Sensors |
| Media APIs | Web Audio, MediaRecorder, Speech APIs, WebRTC |
| Modern APIs | WebGL, WebGPU, WebXR, View Transitions |
| Security | Web Crypto, WebAuthn, Credential Management |
| Performance | High Resolution Time, User Timing, Resource Timing |
| WebAssembly | WASM, Threads, SIMD |

## Running Tests

### GUI Testing (Recommended)
```bash
python run_gui.py
```
1. Drag and drop a test file into the upload area
2. Check detected features against expected list in CHECKLIST.md
3. Verify browser support matches Can I Use

### CLI Testing
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from src.parsers.js_parser import JavaScriptParser

parser = JavaScriptParser()
features = parser.parse_file('tests/validation/js/comprehensive_test.js')
print(f"Detected {len(features)} features")
for f in sorted(features):
    print(f"  - {f}")
EOF
```

### Automated Test Suite
```bash
python3 -m pytest tests/parsers/js/ -v
```

## Expected Results

| File | Min Features | Notes |
|------|--------------|-------|
| comprehensive_test.js | 150+ | All major features combined |
| 01_syntax/es6_syntax.js | 10 | Core ES6 syntax |
| 02_promises_async/promises_async.js | 8 | Async patterns |
| 03_dom_apis/dom_apis.js | 20+ | DOM manipulation |
| 13_edge_cases/*.js | Varies | Edge case validation |
| 14_real_world/*.js | 15-27 | Real-world patterns |

## Edge Case Tests

| File | Purpose | Expected Behavior |
|------|---------|-------------------|
| 01_comments_strings.js | Comment/string handling | Features in comments NOT detected |
| 02_minified_code.js | Minified code | All patterns detected |
| 03_false_positives.js | False positive prevention | Variable names don't trigger detection |
| 04_mixed_patterns.js | Complex patterns | All valid patterns detected |
| 05_directive_strings.js | Directive strings | "use strict" and "use asm" detected |
| 06_webgl_canvas.js | WebGL detection | WebGL features detected |

## Adding New Tests

1. Add test file to appropriate numbered folder
2. Include header comment with expected features
3. Update CHECKLIST.md with new test entry
4. Run automated tests to verify detection

## Notes

- String directives (`"use strict"`, `"use asm"`) are detected before comment/string removal
- Template literals preserve `${...}` structure for detection
- Comments and string content are removed to prevent false positives
- The parser extracts API names from patterns for the property→feature mapping display
