# JavaScript Manual Validation Checklist

## Legend

- `[ ]` = Not tested
- `[x]` = Passed (feature detected, browser support matches)
- `[!]` = Failed (see notes for discrepancy details)

---

## 01_syntax/

### es6_syntax.js

**Expected features:** `arrow-functions`, `async-functions`, `const`, `let`, `template-literals`, `es6`, `rest-parameters`, `es6-class`, `es6-generators`, `use-strict`

| Status | Feature           | Can I Use URL                         |
| ------ | ----------------- | ------------------------------------- |
| [ ]    | arrow-functions   | https://caniuse.com/arrow-functions   |
| [ ]    | async-functions   | https://caniuse.com/async-functions   |
| [ ]    | const             | https://caniuse.com/const             |
| [ ]    | let               | https://caniuse.com/let               |
| [ ]    | template-literals | https://caniuse.com/template-literals |
| [ ]    | es6               | https://caniuse.com/es6               |
| [ ]    | rest-parameters   | https://caniuse.com/rest-parameters   |
| [ ]    | es6-class         | https://caniuse.com/es6-class         |
| [ ]    | es6-generators    | https://caniuse.com/es6-generators    |
| [ ]    | use-strict        | https://caniuse.com/use-strict        |

- [ ] All 10 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 02_promises_async/

### promises_async.js

**Expected features:** `promises`, `promise-finally`, `fetch`, `abortcontroller`, `unhandledrejection`, `requestanimationframe`, `requestidlecallback`, `setimmediate`

| Status | Feature               | Can I Use URL                             |
| ------ | --------------------- | ----------------------------------------- |
| [ ]    | promises              | https://caniuse.com/promises              |
| [ ]    | promise-finally       | https://caniuse.com/promise-finally       |
| [ ]    | fetch                 | https://caniuse.com/fetch                 |
| [ ]    | abortcontroller       | https://caniuse.com/abortcontroller       |
| [ ]    | unhandledrejection    | https://caniuse.com/unhandledrejection    |
| [ ]    | requestanimationframe | https://caniuse.com/requestanimationframe |
| [ ]    | requestidlecallback   | https://caniuse.com/requestidlecallback   |
| [ ]    | setimmediate          | https://caniuse.com/setimmediate          |

- [ ] All 8 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 03_dom_apis/

### dom_apis.js

**Expected features:** `queryselector`, `classlist`, `dataset`, `addeventlistener`, `domcontentloaded`, `hashchange`, `custom-elementsv1`, `shadowdomv1`, `template`, `getboundingclientrect`, `element-closest`, `matchesselector`, `scrollintoview`, `textcontent`, `insertadjacenthtml`, `childnode-remove`, `dom-range`, `dom-manip-convenience`, `trusted-types`

| Status | Feature               | Can I Use URL                             |
| ------ | --------------------- | ----------------------------------------- |
| [ ]    | queryselector         | https://caniuse.com/queryselector         |
| [ ]    | classlist             | https://caniuse.com/classlist             |
| [ ]    | dataset               | https://caniuse.com/dataset               |
| [ ]    | addeventlistener      | https://caniuse.com/addeventlistener      |
| [ ]    | domcontentloaded      | https://caniuse.com/domcontentloaded      |
| [ ]    | hashchange            | https://caniuse.com/hashchange            |
| [ ]    | custom-elementsv1     | https://caniuse.com/custom-elementsv1     |
| [ ]    | shadowdomv1           | https://caniuse.com/shadowdomv1           |
| [ ]    | template              | https://caniuse.com/template              |
| [ ]    | getboundingclientrect | https://caniuse.com/getboundingclientrect |
| [ ]    | element-closest       | https://caniuse.com/element-closest       |
| [ ]    | matchesselector       | https://caniuse.com/matchesselector       |
| [ ]    | scrollintoview        | https://caniuse.com/scrollintoview        |
| [ ]    | textcontent           | https://caniuse.com/textcontent           |
| [ ]    | insertadjacenthtml    | https://caniuse.com/insertadjacenthtml    |
| [ ]    | childnode-remove      | https://caniuse.com/childnode-remove      |
| [ ]    | dom-range             | https://caniuse.com/dom-range             |
| [ ]    | dom-manip-convenience | https://caniuse.com/dom-manip-convenience |
| [ ]    | trusted-types         | https://caniuse.com/trusted-types         |

- [ ] All 19+ features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 04_storage/

### web_storage.js

**Expected features:** `namevalue-storage`, `indexeddb`, `indexeddb2`, `filereader`, `fileapi`, `bloburls`, `atob-btoa`, `textencoder`, `typedarrays`, `sharedarraybuffer`, `json`

| Status | Feature           | Can I Use URL                         |
| ------ | ----------------- | ------------------------------------- |
| [ ]    | namevalue-storage | https://caniuse.com/namevalue-storage |
| [ ]    | indexeddb         | https://caniuse.com/indexeddb         |
| [ ]    | indexeddb2        | https://caniuse.com/indexeddb2        |
| [ ]    | filereader        | https://caniuse.com/filereader        |
| [ ]    | fileapi           | https://caniuse.com/fileapi           |
| [ ]    | bloburls          | https://caniuse.com/bloburls          |
| [ ]    | atob-btoa         | https://caniuse.com/atob-btoa         |
| [ ]    | textencoder       | https://caniuse.com/textencoder       |
| [ ]    | typedarrays       | https://caniuse.com/typedarrays       |
| [ ]    | sharedarraybuffer | https://caniuse.com/sharedarraybuffer |
| [ ]    | json              | https://caniuse.com/json              |

- [ ] All 11 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 05_observers_workers/

### observers_workers.js

**Expected features:** `intersectionobserver`, `mutationobserver`, `resizeobserver`, `webworkers`, `sharedworkers`, `serviceworkers`, `websockets`, `eventsource`, `broadcastchannel`, `channel-messaging`, `x-doc-messaging`

| Status | Feature              | Can I Use URL                            |
| ------ | -------------------- | ---------------------------------------- |
| [ ]    | intersectionobserver | https://caniuse.com/intersectionobserver |
| [ ]    | mutationobserver     | https://caniuse.com/mutationobserver     |
| [ ]    | resizeobserver       | https://caniuse.com/resizeobserver       |
| [ ]    | webworkers           | https://caniuse.com/webworkers           |
| [ ]    | sharedworkers        | https://caniuse.com/sharedworkers        |
| [ ]    | serviceworkers       | https://caniuse.com/serviceworkers       |
| [ ]    | websockets           | https://caniuse.com/websockets           |
| [ ]    | eventsource          | https://caniuse.com/eventsource          |
| [ ]    | broadcastchannel     | https://caniuse.com/broadcastchannel     |
| [ ]    | channel-messaging    | https://caniuse.com/channel-messaging    |
| [ ]    | x-doc-messaging      | https://caniuse.com/x-doc-messaging      |

- [ ] All 11 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 06_device_apis/

### device_apis.js

**Expected features:** `geolocation`, `battery-status`, `netinfo`, `vibration`, `screen-orientation`, `wake-lock`, `deviceorientation`, `gamepad`, `pointer`, `pointerlock`, `touch`, `hardwareconcurrency`, `pagevisibility`, `online-status`, `fullscreen`, `do-not-track`, `devicepixelratio`

| Status | Feature             | Can I Use URL                           |
| ------ | ------------------- | --------------------------------------- |
| [ ]    | geolocation         | https://caniuse.com/geolocation         |
| [ ]    | battery-status      | https://caniuse.com/battery-status      |
| [ ]    | netinfo             | https://caniuse.com/netinfo             |
| [ ]    | vibration           | https://caniuse.com/vibration           |
| [ ]    | screen-orientation  | https://caniuse.com/screen-orientation  |
| [ ]    | wake-lock           | https://caniuse.com/wake-lock           |
| [ ]    | deviceorientation   | https://caniuse.com/deviceorientation   |
| [ ]    | gamepad             | https://caniuse.com/gamepad             |
| [ ]    | pointer             | https://caniuse.com/pointer             |
| [ ]    | pointerlock         | https://caniuse.com/pointerlock         |
| [ ]    | touch               | https://caniuse.com/touch               |
| [ ]    | hardwareconcurrency | https://caniuse.com/hardwareconcurrency |
| [ ]    | pagevisibility      | https://caniuse.com/pagevisibility      |
| [ ]    | online-status       | https://caniuse.com/online-status       |
| [ ]    | fullscreen          | https://caniuse.com/fullscreen          |
| [ ]    | do-not-track        | https://caniuse.com/do-not-track        |
| [ ]    | devicepixelratio    | https://caniuse.com/devicepixelratio    |

- [ ] All 17+ features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 07_media_apis/

### media_apis.js

**Expected features:** `audio-api`, `streams`, `mediarecorder`, `mediasource`, `imagecapture`, `picture-in-picture`, `midi`, `speech-recognition`, `speech-synthesis`, `offscreencanvas`, `createimagebitmap`, `webcodecs`

| Status | Feature            | Can I Use URL                          |
| ------ | ------------------ | -------------------------------------- |
| [ ]    | audio-api          | https://caniuse.com/audio-api          |
| [ ]    | streams            | https://caniuse.com/streams            |
| [ ]    | mediarecorder      | https://caniuse.com/mediarecorder      |
| [ ]    | mediasource        | https://caniuse.com/mediasource        |
| [ ]    | imagecapture       | https://caniuse.com/imagecapture       |
| [ ]    | picture-in-picture | https://caniuse.com/picture-in-picture |
| [ ]    | midi               | https://caniuse.com/midi               |
| [ ]    | speech-recognition | https://caniuse.com/speech-recognition |
| [ ]    | speech-synthesis   | https://caniuse.com/speech-synthesis   |
| [ ]    | offscreencanvas    | https://caniuse.com/offscreencanvas    |
| [ ]    | createimagebitmap  | https://caniuse.com/createimagebitmap  |
| [ ]    | webcodecs          | https://caniuse.com/webcodecs          |

- [ ] All 12 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 08_modern_apis/

### modern_apis.js

**Expected features:** `webgl`, `webgl2`, `webgpu`, `webxr`, `web-bluetooth`, `web-serial`, `webusb`, `webhid`, `webnfc`, `rtcpeerconnection`, `web-animation`, `view-transitions`, `web-share`, `notifications`, `clipboard`, `async-clipboard`, `history`, `matchmedia`, `getcomputedstyle`, `es6-module`, `es6-module-dynamic-import`, `temporal`

| Status | Feature                   | Can I Use URL                                 |
| ------ | ------------------------- | --------------------------------------------- |
| [ ]    | webgl                     | https://caniuse.com/webgl                     |
| [ ]    | webgl2                    | https://caniuse.com/webgl2                    |
| [ ]    | webgpu                    | https://caniuse.com/webgpu                    |
| [ ]    | webxr                     | https://caniuse.com/webxr                     |
| [ ]    | web-bluetooth             | https://caniuse.com/web-bluetooth             |
| [ ]    | web-serial                | https://caniuse.com/web-serial                |
| [ ]    | webusb                    | https://caniuse.com/webusb                    |
| [ ]    | webhid                    | https://caniuse.com/webhid                    |
| [ ]    | webnfc                    | https://caniuse.com/webnfc                    |
| [ ]    | rtcpeerconnection         | https://caniuse.com/rtcpeerconnection         |
| [ ]    | web-animation             | https://caniuse.com/web-animation             |
| [ ]    | view-transitions          | https://caniuse.com/view-transitions          |
| [ ]    | web-share                 | https://caniuse.com/web-share                 |
| [ ]    | notifications             | https://caniuse.com/notifications             |
| [ ]    | clipboard                 | https://caniuse.com/clipboard                 |
| [ ]    | async-clipboard           | https://caniuse.com/async-clipboard           |
| [ ]    | history                   | https://caniuse.com/history                   |
| [ ]    | matchmedia                | https://caniuse.com/matchmedia                |
| [ ]    | getcomputedstyle          | https://caniuse.com/getcomputedstyle          |
| [ ]    | es6-module                | https://caniuse.com/es6-module                |
| [ ]    | es6-module-dynamic-import | https://caniuse.com/es6-module-dynamic-import |
| [ ]    | temporal                  | https://caniuse.com/temporal                  |

- [ ] All 22+ features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 09_security_auth/

### security_auth.js

**Expected features:** `cryptography`, `getrandomvalues`, `webauthn`, `credential-management`, `payment-request`, `permissions-api`, `u2f`

| Status | Feature               | Can I Use URL                             |
| ------ | --------------------- | ----------------------------------------- |
| [ ]    | cryptography          | https://caniuse.com/cryptography          |
| [ ]    | getrandomvalues       | https://caniuse.com/getrandomvalues       |
| [ ]    | webauthn              | https://caniuse.com/webauthn              |
| [ ]    | credential-management | https://caniuse.com/credential-management |
| [ ]    | payment-request       | https://caniuse.com/payment-request       |
| [ ]    | permissions-api       | https://caniuse.com/permissions-api       |
| [ ]    | u2f                   | https://caniuse.com/u2f                   |

- [ ] All 7 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 10_methods/

### array_string_object.js

**Expected features:** `array-flat`, `array-includes`, `array-find`, `es5`, `es6-string-includes`, `pad-start-end`, `object-entries`, `object-values`, `es6`, `bigint`, `proxy`, `es6-number`, `internationalization`, `intl-pluralrules`, `url`, `urlsearchparams`

| Status | Feature              | Can I Use URL                            |
| ------ | -------------------- | ---------------------------------------- |
| [ ]    | array-flat           | https://caniuse.com/array-flat           |
| [ ]    | array-includes       | https://caniuse.com/array-includes       |
| [ ]    | array-find           | https://caniuse.com/array-find           |
| [ ]    | es5                  | https://caniuse.com/es5                  |
| [ ]    | es6-string-includes  | https://caniuse.com/es6-string-includes  |
| [ ]    | pad-start-end        | https://caniuse.com/pad-start-end        |
| [ ]    | object-entries       | https://caniuse.com/object-entries       |
| [ ]    | object-values        | https://caniuse.com/object-values        |
| [ ]    | es6                  | https://caniuse.com/es6                  |
| [ ]    | bigint               | https://caniuse.com/bigint               |
| [ ]    | proxy                | https://caniuse.com/proxy                |
| [ ]    | es6-number           | https://caniuse.com/es6-number           |
| [ ]    | internationalization | https://caniuse.com/internationalization |
| [ ]    | intl-pluralrules     | https://caniuse.com/intl-pluralrules     |
| [ ]    | url                  | https://caniuse.com/url                  |
| [ ]    | urlsearchparams      | https://caniuse.com/urlsearchparams      |

- [ ] All 16 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 11_performance/

### performance_timing.js

**Expected features:** `high-resolution-time`, `user-timing`, `resource-timing`, `nav-timing`, `server-timing`, `console-time`, `console-basic`, `beacon`

| Status | Feature              | Can I Use URL                            |
| ------ | -------------------- | ---------------------------------------- |
| [ ]    | high-resolution-time | https://caniuse.com/high-resolution-time |
| [ ]    | user-timing          | https://caniuse.com/user-timing          |
| [ ]    | resource-timing      | https://caniuse.com/resource-timing      |
| [ ]    | nav-timing           | https://caniuse.com/nav-timing           |
| [ ]    | server-timing        | https://caniuse.com/server-timing        |
| [ ]    | console-time         | https://caniuse.com/console-time         |
| [ ]    | console-basic        | https://caniuse.com/console-basic        |
| [ ]    | beacon               | https://caniuse.com/beacon               |

- [ ] All 8 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 12_wasm_misc/

### wasm_misc.js

**Expected features:** `wasm`, `asmjs`, `xml-serializer`, `dommatrix`, `path2d`, `canvas-blending`, `stream`, `customevent`, `dispatchevent`, `css-supports-api`, `font-loading`, `xhr2`

| Status | Feature          | Can I Use URL                        |
| ------ | ---------------- | ------------------------------------ |
| [ ]    | wasm             | https://caniuse.com/wasm             |
| [ ]    | asmjs            | https://caniuse.com/asmjs            |
| [ ]    | xml-serializer   | https://caniuse.com/xml-serializer   |
| [ ]    | dommatrix        | https://caniuse.com/dommatrix        |
| [ ]    | path2d           | https://caniuse.com/path2d           |
| [ ]    | canvas-blending  | https://caniuse.com/canvas-blending  |
| [ ]    | stream           | https://caniuse.com/stream           |
| [ ]    | customevent      | https://caniuse.com/customevent      |
| [ ]    | dispatchevent    | https://caniuse.com/dispatchevent    |
| [ ]    | css-supports-api | https://caniuse.com/css-supports-api |
| [ ]    | font-loading     | https://caniuse.com/font-loading     |
| [ ]    | xhr2             | https://caniuse.com/xhr2             |

- [ ] All 12 features detected
- [ ] Browser support matches for each
- **Notes:** \_\_\_

---

## 13_edge_cases/

### 01_comments_strings.js

**Purpose:** Verify features in comments/strings are NOT detected

| Status | Test                                                                      |
| ------ | ------------------------------------------------------------------------- |
| [ ]    | Features in comments NOT detected (fetch, localStorage, WebSocket)        |
| [ ]    | Features in strings NOT detected                                          |
| [ ]    | Actual code features ARE detected (const, arrow-functions, querySelector) |

- **Notes:** \_\_\_

---

### 02_minified_code.js

**Purpose:** Verify minified code patterns are detected

| Status | Test                                        |
| ------ | ------------------------------------------- |
| [ ]    | const/let detected in minified form         |
| [ ]    | Arrow functions detected without whitespace |
| [ ]    | Chained methods detected                    |
| [ ]    | All standard patterns work in minified code |

- **Notes:** \_\_\_

---

### 03_false_positives.js

**Purpose:** Verify variable names don't trigger false positives

| Status | Test                                                             |
| ------ | ---------------------------------------------------------------- |
| [ ]    | Variable `fetchData` does NOT trigger `fetch` detection          |
| [ ]    | Property `config.fetch` does NOT trigger `fetch` detection       |
| [ ]    | Custom method `myObj.querySelector()` does NOT trigger detection |
| [ ]    | Actual `fetch('/api')` DOES trigger detection                    |

- **Notes:** \_\_\_

---

### 04_mixed_patterns.js

**Purpose:** Verify complex/unusual patterns are detected

| Status | Test                                 |
| ------ | ------------------------------------ |
| [ ]    | All arrow function variants detected |
| [ ]    | All async patterns detected          |
| [ ]    | Destructuring patterns detected      |
| [ ]    | Generator functions detected         |
| [ ]    | Proxy and Symbol detected            |

- **Notes:** \_\_\_

---

### 05_directive_strings.js

**Purpose:** Verify "use strict" and "use asm" are detected

| Status | Feature    | Can I Use URL                  |
| ------ | ---------- | ------------------------------ |
| [ ]    | use-strict | https://caniuse.com/use-strict |
| [ ]    | asmjs      | https://caniuse.com/asmjs      |

- [ ] Both directive types detected (double and single quotes)
- **Notes:** \_\_\_

---

### 06_webgl_canvas.js

**Purpose:** Verify WebGL and canvas features are detected

| Status | Feature           | Can I Use URL                         |
| ------ | ----------------- | ------------------------------------- |
| [ ]    | webgl             | https://caniuse.com/webgl             |
| [ ]    | webgl2            | https://caniuse.com/webgl2            |
| [ ]    | canvas-blending   | https://caniuse.com/canvas-blending   |
| [ ]    | path2d            | https://caniuse.com/path2d            |
| [ ]    | createimagebitmap | https://caniuse.com/createimagebitmap |

- [ ] WebGL detected via constructor reference
- **Notes:** \_\_\_

---

## 14_real_world/

### 01_react_app.js

**Purpose:** Test React application patterns

**Expected features:** `arrow-functions`, `async-functions`, `const`, `fetch`, `abortcontroller`, `namevalue-storage`, `json`, `classlist`, `es6`, `es5`

| Status | Test                               |
| ------ | ---------------------------------- |
| [ ]    | React hooks patterns detected      |
| [ ]    | State management patterns detected |
| [ ]    | API call patterns detected         |
| [ ]    | At least 15 features detected      |

- **Notes:** \_\_\_

---

### 02_vanilla_dashboard.js

**Purpose:** Test vanilla JS dashboard patterns

**Expected features:** `const`, `es6-class`, `arrow-functions`, `fetch`, `queryselector`, `classlist`, `intersectionobserver`, `mutationobserver`, `history`, `matchmedia`, `use-strict`, `dataset`, `addeventlistener`

| Status | Test                          |
| ------ | ----------------------------- |
| [ ]    | Class-based patterns detected |
| [ ]    | Observer APIs detected        |
| [ ]    | History API detected          |
| [ ]    | At least 20 features detected |

- **Notes:** \_\_\_

---

### 03_service_worker.js

**Purpose:** Test service worker patterns

**Expected features:** `const`, `arrow-functions`, `async-functions`, `fetch`, `json`, `promises`

| Status | Test                                   |
| ------ | -------------------------------------- |
| [ ]    | Service worker event patterns detected |
| [ ]    | Cache API usage detected               |
| [ ]    | At least 10 features detected          |

- **Notes:** \_\_\_

---

### 04_form_validation.js

**Purpose:** Test form validation patterns

**Expected features:** `const`, `es6-class`, `async-functions`, `queryselector`, `classlist`, `dataset`, `addeventlistener`, `fetch`, `json`, `use-strict`

| Status | Test                           |
| ------ | ------------------------------ |
| [ ]    | Form API patterns detected     |
| [ ]    | Constraint validation detected |
| [ ]    | At least 15 features detected  |

- **Notes:** \_\_\_

---

## comprehensive_test.js

**Purpose:** All features combined - should detect 150+ features

| Status | Test                             |
| ------ | -------------------------------- |
| [ ]    | 150+ unique features detected    |
| [ ]    | All major categories represented |
| [ ]    | No false positives from comments |

- **Detected count:** \_\_\_
- **Notes:** \_\_\_

---

## Summary

| Category             | Files Tested | Pass | Fail | Notes |
| -------------------- | ------------ | ---- | ---- | ----- |
| 01_syntax            | 1            |      |      |       |
| 02_promises_async    | 1            |      |      |       |
| 03_dom_apis          | 1            |      |      |       |
| 04_storage           | 1            |      |      |       |
| 05_observers_workers | 1            |      |      |       |
| 06_device_apis       | 1            |      |      |       |
| 07_media_apis        | 1            |      |      |       |
| 08_modern_apis       | 1            |      |      |       |
| 09_security_auth     | 1            |      |      |       |
| 10_methods           | 1            |      |      |       |
| 11_performance       | 1            |      |      |       |
| 12_wasm_misc         | 1            |      |      |       |
| 13_edge_cases        | 6            |      |      |       |
| 14_real_world        | 4            |      |      |       |
| comprehensive        | 1            |      |      |       |
| **Total**            | **23**       |      |      |       |

**Test Date:** **\_
**Tester:** \_**
**Version:** \_\_\_
