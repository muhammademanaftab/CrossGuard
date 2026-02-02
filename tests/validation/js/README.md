# JavaScript Validation Test Files

This directory contains comprehensive JavaScript test files to validate the JS parser's feature detection capabilities against the Can I Use database.

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

## Notes

- String directives (`"use strict"`, `"use asm"`) are detected before comment/string removal
- Template literals preserve `${...}` structure for detection
- Comments and string content are removed to prevent false positives
- The parser extracts API names from patterns for the property→feature mapping display
