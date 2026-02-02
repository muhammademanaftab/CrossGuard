# JavaScript Validation Test Files

This directory contains comprehensive JavaScript test files to validate the JS parser's feature detection capabilities against the Can I Use database.

## Directory Structure

```
js/
├── 01_es6_syntax.js         # ES6 syntax features
├── 02_promises_async.js     # Promises and async APIs
├── 03_dom_apis.js           # DOM manipulation APIs
├── 04_web_storage.js        # Storage APIs
├── 05_observers_workers.js  # Observers and Workers
├── 06_device_apis.js        # Device/hardware APIs
├── 07_media_apis.js         # Audio/Video APIs
├── 08_modern_apis.js        # Modern Web APIs
├── 09_security_auth.js      # Security and auth
├── 10_array_string_object.js # Array/String/Object methods
├── 11_performance_timing.js # Performance APIs
├── 12_wasm_misc.js          # WebAssembly and misc
├── comprehensive_test.js    # All features combined
├── real_world/              # Real-world code patterns
│   ├── 01_react_app.js      # React application
│   ├── 02_vanilla_dashboard.js # Vanilla JS dashboard
│   ├── 03_service_worker.js # PWA service worker
│   └── 04_form_validation.js # Form validation
└── edge_cases/              # Edge case tests
    ├── 01_comments_strings.js   # Comment/string handling
    ├── 02_minified_code.js      # Minified JS
    ├── 03_false_positives.js    # False positive tests
    ├── 04_mixed_patterns.js     # Complex patterns
    ├── 05_directive_strings.js  # "use strict"/"use asm"
    └── 06_webgl_canvas.js       # WebGL/Canvas APIs
```

## Test File Structure

| File | Description | Key Features |
|------|-------------|--------------|
| `01_es6_syntax.js` | ES6+ syntax features | Arrow functions, async/await, const/let, classes, generators |
| `02_promises_async.js` | Promises and async APIs | Promises, fetch, AbortController, requestAnimationFrame |
| `03_dom_apis.js` | DOM manipulation APIs | querySelector, classList, Shadow DOM, Custom Elements |
| `04_web_storage.js` | Storage and data APIs | localStorage, IndexedDB, FileReader, Blob URLs |
| `05_observers_workers.js` | Observers and workers | IntersectionObserver, Web Workers, WebSockets |
| `06_device_apis.js` | Device/hardware APIs | Geolocation, Battery, Sensors, Gamepad |
| `07_media_apis.js` | Media and audio APIs | Web Audio, MediaRecorder, Speech APIs |
| `08_modern_apis.js` | Modern web APIs | WebGL, WebGPU, WebXR, View Transitions |
| `09_security_auth.js` | Security/auth APIs | Web Crypto, WebAuthn, Payment Request |
| `10_array_string_object.js` | Array/String/Object methods | flat(), includes(), entries(), BigInt |
| `11_performance_timing.js` | Performance APIs | High Resolution Time, User Timing, Beacon |
| `12_wasm_misc.js` | WebAssembly and misc | WASM, Path2D, DOMMatrix, Streams |
| `comprehensive_test.js` | All features combined | 150+ features in one file |

## Feature Coverage

The JS parser validates against **278 Can I Use feature IDs**, covering:

- **ES6+ Syntax**: Arrow functions, async/await, const/let, template literals, classes, generators
- **Promises**: Promise API, Promise.finally, async/await patterns
- **DOM APIs**: querySelector, classList, dataset, Shadow DOM, Custom Elements
- **Observers**: Intersection, Mutation, Resize observers
- **Workers**: Web Workers, Shared Workers, Service Workers
- **Storage**: localStorage, sessionStorage, IndexedDB
- **File APIs**: FileReader, File API, Blob URLs, File System Access
- **Device APIs**: Geolocation, Battery, Vibration, Sensors
- **Media APIs**: Web Audio, MediaRecorder, Speech APIs, WebRTC
- **Modern APIs**: WebGL, WebGPU, WebXR, View Transitions
- **Security**: Web Crypto, WebAuthn, Credential Management
- **Performance**: High Resolution Time, User Timing, Resource Timing
- **WebAssembly**: WASM, Threads, SIMD

## Running Tests

### Manual Test
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from src.parsers.js_parser import JavaScriptParser

parser = JavaScriptParser()
features = parser.parse_file('tests/validation/js/comprehensive_test.js')
print(f"Detected {len(features)} features")
EOF
```

### Full Test Suite
```bash
python3 -m pytest tests/ -v
```

## Expected Results

- `comprehensive_test.js` should detect **150+ unique features**
- Each category test file should detect features specific to its category
- No false negatives on standard JavaScript patterns
- Unrecognized patterns should only be novel/experimental APIs

## Feature Detection Details

The parser provides detailed information about detected features:

```python
parser = JavaScriptParser()
parser.parse_file('file.js')

# Access feature details with matched APIs
for detail in parser.feature_details:
    print(f"{detail['feature']}: {detail['description']}")
    print(f"  Matched APIs: {', '.join(detail['matched_apis'])}")
```

## Adding New Features

1. Add pattern to `src/parsers/js_feature_maps.py` in the appropriate category
2. Add test case to the relevant category test file
3. Update `comprehensive_test.js` with example usage
4. Run tests to verify detection

## Edge Case Tests

Tests in `edge_cases/` verify parser robustness:

| File | What to Verify |
|------|---------------|
| `01_comments_strings.js` | Features in comments/strings are NOT detected |
| `02_minified_code.js` | Minified code patterns ARE detected |
| `03_false_positives.js` | Only real API calls detected, not variable names |
| `04_mixed_patterns.js` | Complex/unusual patterns detected correctly |
| `05_directive_strings.js` | "use strict" and "use asm" detected |
| `06_webgl_canvas.js` | WebGL via constructor reference detected |

## Real-World Tests

Tests in `real_world/` simulate actual user code:

| File | Patterns Tested |
|------|-----------------|
| `01_react_app.js` | React hooks, state, fetch patterns |
| `02_vanilla_dashboard.js` | Classes, observers, history API |
| `03_service_worker.js` | Service worker, caching, push API |
| `04_form_validation.js` | Form handling, constraint validation |

## Critical Manual Tests

### 1. Comment/String Stripping
Test `edge_cases/01_comments_strings.js`:
- ❌ Should NOT detect: fetch, localStorage, WebSocket (in comments)
- ✅ Should detect: const, arrow-functions, querySelector, JSON

### 2. Directive Strings
Test `edge_cases/05_directive_strings.js`:
- ✅ Should detect: use-strict, asmjs
- These are detected BEFORE comment/string stripping

### 3. WebGL Detection
Test `edge_cases/06_webgl_canvas.js`:
- ✅ Should detect: webgl, webgl2
- Uses `WebGLRenderingContext` which survives string stripping

### 4. False Positive Prevention
Test `edge_cases/03_false_positives.js`:
- ❌ Variable names like `fetchData` should NOT trigger fetch detection
- ✅ Actual API calls like `fetch('/api')` SHOULD be detected

## Notes

- String directives (`"use strict"`, `"use asm"`) are detected before comment/string removal
- Template literals preserve `${...}` structure for detection
- Comments and string content are removed to prevent false positives
- The parser extracts API names from patterns for the property→feature mapping display
