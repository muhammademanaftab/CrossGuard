"""JavaScript Feature mapping dictionaries.

Maps detected JavaScript patterns to Can I Use feature IDs.
All feature IDs are verified against the Can I Use database.
"""

# JavaScript Syntax Features
JS_SYNTAX_FEATURES = {
    'arrow-functions': {
        'patterns': [r'=>', r'\(.*?\)\s*=>', r'\w+\s*=>'],
        'keywords': ['=>'],
        'description': 'Arrow functions'
    },
    'async-functions': {
        'patterns': [r'\basync\s+function', r'\basync\s*\(', r'\basync\s+\w+\s*=>'],
        'keywords': ['async', 'await'],
        'description': 'Async/await'
    },
    'const': {
        'patterns': [r'\bconst\s+'],
        'keywords': ['const'],
        'description': 'Const declaration'
    },
    'let': {
        'patterns': [r'\blet\s+'],
        'keywords': ['let'],
        'description': 'Let declaration'
    },
    'template-literals': {
        'patterns': [r'`[^`]*\$\{[^}]+\}[^`]*`'],
        'keywords': ['`'],
        'description': 'Template literals'
    },
    'es6': {
        'patterns': [
            # Destructuring
            r'\bconst\s*\{', r'\blet\s*\{', r'\bconst\s*\[', r'\blet\s*\[',
            # Spread/rest
            r'\.\.\.',
            # ES6 built-ins (Map, Set, WeakMap, WeakSet, Symbol, Reflect)
            r'\bnew\s+Map', r'\bnew\s+Set', r'\bnew\s+WeakMap', r'\bnew\s+WeakSet',
            r'\bSymbol\s*\(', r'\bReflect\.'
        ],
        'keywords': ['Map', 'Set', 'WeakMap', 'WeakSet', 'Symbol', 'Reflect'],
        'description': 'ES6 features (destructuring, spread, Map, Set, Symbol, Reflect)'
    },
    'rest-parameters': {
        'patterns': [r'function\s*\w*\s*\([^)]*\.\.\.[^)]*\)', r'=>\s*\([^)]*\.\.\.[^)]*\)'],
        'keywords': ['...'],
        'description': 'Rest parameters'
    },
    'es6-class': {
        'patterns': [r'\bclass\s+\w+'],
        'keywords': ['class'],
        'description': 'ES6 Classes'
    },
    'es6-generators': {
        'patterns': [r'\bfunction\s*\*', r'\byield\s+'],
        'keywords': ['function*', 'yield'],
        'description': 'ES6 Generators'
    },
}

# JavaScript API Features
JS_API_FEATURES = {
    'promises': {
        'patterns': [r'\bnew\s+Promise', r'\.then\(', r'\.catch\(', r'Promise\.'],
        'keywords': ['Promise'],
        'description': 'Promises'
    },
    'fetch': {
        'patterns': [r'\bfetch\s*\('],
        'keywords': ['fetch'],
        'description': 'Fetch API'
    },
    'bigint': {
        'patterns': [r'\bBigInt\s*\(', r'\d+n\b'],
        'keywords': ['BigInt'],
        'description': 'BigInt'
    },
    'intersectionobserver': {
        'patterns': [r'\bnew\s+IntersectionObserver', r'IntersectionObserver'],
        'keywords': ['IntersectionObserver'],
        'description': 'Intersection Observer'
    },
    'mutationobserver': {
        'patterns': [r'\bnew\s+MutationObserver', r'MutationObserver'],
        'keywords': ['MutationObserver'],
        'description': 'Mutation Observer'
    },
    'resizeobserver': {
        'patterns': [r'\bnew\s+ResizeObserver', r'ResizeObserver'],
        'keywords': ['ResizeObserver'],
        'description': 'Resize Observer'
    },
    'proxy': {
        'patterns': [r'\bnew\s+Proxy', r'\bProxy\s*\('],
        'keywords': ['Proxy'],
        'description': 'Proxy'
    },
    'json': {
        'patterns': [r'\bJSON\.parse\s*\(', r'\bJSON\.stringify\s*\(', r'\bJSON\.'],
        'keywords': ['JSON.parse', 'JSON.stringify', 'JSON'],
        'description': 'JSON parsing and stringifying'
    },
    'dragndrop': {
        'patterns': [r'\.draggable\s*=', r'addEventListener\s*\(\s*["\']drag', 
                     r'addEventListener\s*\(\s*["\']drop', r'dataTransfer'],
        'keywords': ['draggable', 'dragstart', 'drop', 'dataTransfer'],
        'description': 'Drag and Drop API'
    },
    'es5': {
        'patterns': [r'\.forEach\s*\(', r'\.map\s*\(', r'\.filter\s*\(', 
                     r'\.reduce\s*\(', r'\.some\s*\(', r'\.every\s*\('],
        'keywords': ['forEach', 'map', 'filter', 'reduce'],
        'description': 'ES5 Array methods'
    },
    'geolocation': {
        'patterns': [r'navigator\.geolocation', r'getCurrentPosition', r'watchPosition'],
        'keywords': ['geolocation'],
        'description': 'Geolocation API'
    },
    'notifications': {
        'patterns': [r'\bnew\s+Notification', r'Notification\.permission'],
        'keywords': ['Notification'],
        'description': 'Web Notifications'
    },
    'serviceworkers': {
        'patterns': [r'navigator\.serviceWorker', r'serviceWorker\.register\s*\('],
        'keywords': ['serviceWorker'],
        'description': 'Service Workers'
    },
    'webworkers': {
        'patterns': [r'\bnew\s+Worker\s*\(', r'new Worker'],
        'keywords': ['Worker'],
        'description': 'Web Workers'
    },
    'websockets': {
        'patterns': [r'\bnew\s+WebSocket', r'WebSocket'],
        'keywords': ['WebSocket'],
        'description': 'WebSockets'
    },
    'requestanimationframe': {
        'patterns': [r'requestAnimationFrame', r'cancelAnimationFrame'],
        'keywords': ['requestAnimationFrame'],
        'description': 'requestAnimationFrame'
    },
    'fullscreen': {
        'patterns': [r'requestFullscreen', r'exitFullscreen', r'\.fullscreenElement'],
        'keywords': ['requestFullscreen', 'fullscreen'],
        'description': 'Fullscreen API'
    },
    'pagevisibility': {
        'patterns': [r'document\.hidden', r'document\.visibilityState', r'visibilitychange'],
        'keywords': ['visibilityState', 'hidden'],
        'description': 'Page Visibility API'
    },
    'cryptography': {
        'patterns': [r'crypto\.subtle', r'crypto\.getRandomValues'],
        'keywords': ['crypto'],
        'description': 'Web Cryptography'
    },
    'stream': {
        'patterns': [r'ReadableStream', r'WritableStream', r'TransformStream'],
        'keywords': ['ReadableStream', 'WritableStream'],
        'description': 'Streams API'
    },
    'streams': {
        'patterns': [r'getUserMedia', r'navigator\.mediaDevices'],
        'keywords': ['getUserMedia'],
        'description': 'getUserMedia/Stream API'
    },
    'xhr2': {
        'patterns': [r'new XMLHttpRequest', r'XMLHttpRequest'],
        'keywords': ['XMLHttpRequest'],
        'description': 'XMLHttpRequest Level 2'
    },
    'online-status': {
        'patterns': [r'navigator\.onLine', r"addEventListener\s*\(\s*['\"]online['\"]", r"addEventListener\s*\(\s*['\"]offline['\"]"],
        'keywords': ['navigator.onLine'],
        'description': 'Online/offline status'
    },
    'eventsource': {
        'patterns': [r'new EventSource', r'EventSource'],
        'keywords': ['EventSource'],
        'description': 'Server-sent events'
    },
    'broadcastchannel': {
        'patterns': [r'new BroadcastChannel', r'BroadcastChannel'],
        'keywords': ['BroadcastChannel'],
        'description': 'BroadcastChannel API'
    },
    'channel-messaging': {
        'patterns': [r'MessageChannel', r'MessagePort'],
        'keywords': ['MessageChannel'],
        'description': 'Channel Messaging API'
    },
    'x-doc-messaging': {
        'patterns': [r'postMessage', r'window\.postMessage'],
        'keywords': ['postMessage'],
        'description': 'Cross-document messaging'
    },
    'indexeddb2': {
        'patterns': [r'indexedDB', r'IDBKeyRange'],
        'keywords': ['indexedDB'],
        'description': 'IndexedDB 2.0'
    },
    'filereader': {
        'patterns': [r'new FileReader', r'FileReader'],
        'keywords': ['FileReader'],
        'description': 'FileReader API'
    },
    'bloburls': {
        'patterns': [r'URL\.createObjectURL', r'createObjectURL'],
        'keywords': ['createObjectURL'],
        'description': 'Blob URLs'
    },
    'filesystem': {
        'patterns': [r'requestFileSystem', r'webkitRequestFileSystem'],
        'keywords': ['requestFileSystem'],
        'description': 'FileSystem API'
    },
    'native-filesystem-api': {
        'patterns': [r'showOpenFilePicker', r'showSaveFilePicker'],
        'keywords': ['showOpenFilePicker'],
        'description': 'File System Access API'
    },
    'fileapi': {
        'patterns': [r'new File', r'new Blob', r'File', r'Blob'],
        'keywords': ['File', 'Blob'],
        'description': 'File API'
    },
    'atob-btoa': {
        'patterns': [r'\batob\s*\(', r'\bbtoa\s*\('],
        'keywords': ['atob', 'btoa'],
        'description': 'Base64 encoding and decoding'
    },
    'textencoder': {
        'patterns': [r'new TextEncoder', r'new TextDecoder', r'TextEncoder', r'TextDecoder'],
        'keywords': ['TextEncoder', 'TextDecoder'],
        'description': 'TextEncoder & TextDecoder'
    },
    'typedarrays': {
        'patterns': [r'Int8Array', r'Uint8Array', r'ArrayBuffer', r'DataView'],
        'keywords': ['ArrayBuffer', 'Uint8Array'],
        'description': 'Typed Arrays'
    },
    'sharedarraybuffer': {
        'patterns': [r'SharedArrayBuffer', r'Atomics'],
        'keywords': ['SharedArrayBuffer'],
        'description': 'Shared Array Buffer'
    },
    'sharedworkers': {
        'patterns': [r'new SharedWorker', r'SharedWorker'],
        'keywords': ['SharedWorker'],
        'description': 'Shared Web Workers'
    },
    'rtcpeerconnection': {
        'patterns': [r'RTCPeerConnection', r'webkitRTCPeerConnection'],
        'keywords': ['RTCPeerConnection'],
        'description': 'WebRTC Peer-to-peer connections'
    },
    'webauthn': {
        'patterns': [r'navigator\.credentials', r'PublicKeyCredential'],
        'keywords': ['webauthn'],
        'description': 'Web Authentication API'
    },
    'credential-management': {
        'patterns': [r'navigator\.credentials\.get', r'PasswordCredential'],
        'keywords': ['credentials'],
        'description': 'Credential Management API'
    },
    'payment-request': {
        'patterns': [r'new PaymentRequest', r'PaymentRequest'],
        'keywords': ['PaymentRequest'],
        'description': 'Payment Request API'
    },
    'push-api': {
        'patterns': [r'PushManager', r'pushManager\.subscribe\s*\('],
        'keywords': ['PushManager'],
        'description': 'Push API'
    },
    'permissions-api': {
        'patterns': [r'navigator\.permissions', r'permissions\.query'],
        'keywords': ['permissions'],
        'description': 'Permissions API'
    },
    'battery-status': {
        'patterns': [r'navigator\.getBattery', r'BatteryManager'],
        'keywords': ['getBattery'],
        'description': 'Battery Status API'
    },
    'netinfo': {
        'patterns': [r'navigator\.connection', r'NetworkInformation'],
        'keywords': ['navigator.connection'],
        'description': 'Network Information API'
    },
    'vibration': {
        'patterns': [r'navigator\.vibrate'],
        'keywords': ['vibrate'],
        'description': 'Vibration API'
    },
    'screen-orientation': {
        'patterns': [r'screen\.orientation', r'lockOrientation'],
        'keywords': ['screen.orientation'],
        'description': 'Screen Orientation API'
    },
    'wake-lock': {
        'patterns': [r'navigator\.wakeLock', r'WakeLock'],
        'keywords': ['wakeLock'],
        'description': 'Screen Wake Lock API'
    },
    'gamepad': {
        'patterns': [r'navigator\.getGamepads', r'Gamepad'],
        'keywords': ['getGamepads'],
        'description': 'Gamepad API'
    },
    'pointer': {
        'patterns': [r'PointerEvent', r'pointerdown', r'pointerup'],
        'keywords': ['PointerEvent'],
        'description': 'Pointer Events'
    },
    'pointerlock': {
        'patterns': [r'requestPointerLock', r'pointerLockElement'],
        'keywords': ['requestPointerLock'],
        'description': 'Pointer Lock API'
    },
    'touch': {
        'patterns': [r'TouchEvent', r'touchstart', r'touchend'],
        'keywords': ['TouchEvent'],
        'description': 'Touch Events'
    },
    'deviceorientation': {
        'patterns': [r'DeviceOrientationEvent', r'deviceorientation', r'DeviceMotionEvent', r'devicemotion'],
        'keywords': ['DeviceOrientationEvent', 'DeviceMotionEvent'],
        'description': 'Device Orientation and Motion'
    },
    'ambient-light': {
        'patterns': [r'AmbientLightSensor', r'new AmbientLightSensor'],
        'keywords': ['AmbientLightSensor'],
        'description': 'Ambient Light Sensor'
    },
    'proximity': {
        'patterns': [r'ProximitySensor', r'deviceproximity'],
        'keywords': ['ProximitySensor'],
        'description': 'Proximity API'
    },
    'speech-recognition': {
        'patterns': [r'SpeechRecognition', r'webkitSpeechRecognition'],
        'keywords': ['SpeechRecognition'],
        'description': 'Speech Recognition API'
    },
    'speech-synthesis': {
        'patterns': [r'speechSynthesis', r'SpeechSynthesisUtterance'],
        'keywords': ['speechSynthesis'],
        'description': 'Speech Synthesis API'
    },
    'web-share': {
        'patterns': [r'navigator\.share', r'navigator\.share\s*\('],
        'keywords': ['navigator.share'],
        'description': 'Web Share API'
    },
    'web-animation': {
        'patterns': [r'\.animate\s*\(\s*\[', r'\.animate\s*\(\s*\w', r'\bKeyframeEffect\b', r'\.getAnimations\s*\(', r'\bnew\s+Animation\b'],
        'keywords': ['animate'],
        'description': 'Web Animations API'
    },
    'requestidlecallback': {
        'patterns': [r'requestIdleCallback', r'cancelIdleCallback'],
        'keywords': ['requestIdleCallback'],
        'description': 'requestIdleCallback'
    },
    'console-time': {
        'patterns': [r'console\.time\s*\(', r'console\.timeEnd\s*\('],
        'keywords': ['console.time'],
        'description': 'console.time and console.timeEnd'
    },
    'high-resolution-time': {
        'patterns': [r'performance\.now', r'performance\.mark'],
        'keywords': ['performance.now'],
        'description': 'High Resolution Time API'
    },
    'user-timing': {
        'patterns': [r'performance\.mark', r'performance\.measure'],
        'keywords': ['performance.mark'],
        'description': 'User Timing API'
    },
    'resource-timing': {
        'patterns': [r'performance\.getEntries', r'PerformanceResourceTiming'],
        'keywords': ['PerformanceResourceTiming'],
        'description': 'Resource Timing'
    },
    'nav-timing': {
        'patterns': [r'performance\.timing', r'performance\.navigation'],
        'keywords': ['performance.timing'],
        'description': 'Navigation Timing API'
    },
    'server-timing': {
        'patterns': [r'PerformanceServerTiming', r'serverTiming'],
        'keywords': ['PerformanceServerTiming'],
        'description': 'Server Timing'
    },
    'mediarecorder': {
        'patterns': [r'new MediaRecorder', r'MediaRecorder'],
        'keywords': ['MediaRecorder'],
        'description': 'MediaRecorder API'
    },
    'mediasource': {
        'patterns': [r'new MediaSource', r'MediaSource'],
        'keywords': ['MediaSource'],
        'description': 'Media Source Extensions'
    },
    'midi': {
        'patterns': [r'navigator\.requestMIDIAccess', r'MIDIAccess'],
        'keywords': ['requestMIDIAccess'],
        'description': 'Web MIDI API'
    },
    'web-bluetooth': {
        'patterns': [r'navigator\.bluetooth', r'bluetooth\.requestDevice'],
        'keywords': ['navigator.bluetooth'],
        'description': 'Web Bluetooth'
    },
    'web-serial': {
        'patterns': [r'navigator\.serial', r'serial\.requestPort'],
        'keywords': ['navigator.serial'],
        'description': 'Web Serial API'
    },
    'webusb': {
        'patterns': [r'navigator\.usb', r'usb\.requestDevice'],
        'keywords': ['navigator.usb'],
        'description': 'WebUSB'
    },
    'webhid': {
        'patterns': [r'navigator\.hid', r'hid\.requestDevice'],
        'keywords': ['navigator.hid'],
        'description': 'WebHID API'
    },
    'webnfc': {
        'patterns': [r'new NDEFReader', r'NDEFReader'],
        'keywords': ['NDEFReader'],
        'description': 'Web NFC'
    },
    'webgpu': {
        'patterns': [r'navigator\.gpu', r'GPUDevice'],
        'keywords': ['navigator.gpu'],
        'description': 'WebGPU'
    },
    'webxr': {
        'patterns': [r'navigator\.xr', r'XRSession'],
        'keywords': ['navigator.xr'],
        'description': 'WebXR Device API'
    },
    'webvr': {
        'patterns': [r'navigator\.getVRDisplays', r'VRDisplay'],
        'keywords': ['getVRDisplays'],
        'description': 'WebVR API'
    },
    'offscreencanvas': {
        'patterns': [r'new OffscreenCanvas', r'OffscreenCanvas'],
        'keywords': ['OffscreenCanvas'],
        'description': 'OffscreenCanvas'
    },
    'webcodecs': {
        'patterns': [r'VideoEncoder', r'VideoDecoder', r'AudioEncoder'],
        'keywords': ['VideoEncoder'],
        'description': 'WebCodecs API'
    },
    'webtransport': {
        'patterns': [r'new WebTransport', r'WebTransport'],
        'keywords': ['WebTransport'],
        'description': 'WebTransport'
    },
    'temporal': {
        'patterns': [r'Temporal\.', r'Temporal\.Now'],
        'keywords': ['Temporal'],
        'description': 'Temporal API'
    },
    'url': {
        'patterns': [r'new URL\s*\(', r'URL\.'],
        'keywords': ['URL'],
        'description': 'URL API'
    },
    'urlsearchparams': {
        'patterns': [r'new URLSearchParams', r'URLSearchParams'],
        'keywords': ['URLSearchParams'],
        'description': 'URLSearchParams'
    },
    'selection-api': {
        'patterns': [r'window\.getSelection', r'Selection'],
        'keywords': ['getSelection'],
        'description': 'Selection API'
    },
    'clipboard': {
        'patterns': [r'navigator\.clipboard', r'clipboard\.write'],
        'keywords': ['navigator.clipboard'],
        'description': 'Clipboard API'
    },
    'async-clipboard': {
        'patterns': [r'navigator\.clipboard\.read', r'clipboard\.readText'],
        'keywords': ['clipboard.read'],
        'description': 'Asynchronous Clipboard API'
    },
    'picture-in-picture': {
        'patterns': [r'requestPictureInPicture', r'PictureInPictureWindow'],
        'keywords': ['requestPictureInPicture'],
        'description': 'Picture-in-Picture'
    },
    'portals': {
        'patterns': [r'<portal', r'HTMLPortalElement'],
        'keywords': ['portal'],
        'description': 'Portals'
    },
    'view-transitions': {
        'patterns': [r'document\.startViewTransition', r'ViewTransition'],
        'keywords': ['startViewTransition'],
        'description': 'View Transitions API'
    },
    'passkeys': {
        'patterns': [r'PublicKeyCredential', r'passkey'],
        'keywords': ['passkey'],
        'description': 'Passkeys'
    },
    'unhandledrejection': {
        'patterns': [r'unhandledrejection', r'rejectionhandled'],
        'keywords': ['unhandledrejection'],
        'description': 'unhandledrejection/rejectionhandled events'
    },
    'promise-finally': {
        'patterns': [r'\.finally\s*\('],
        'keywords': ['.finally'],
        'description': 'Promise.prototype.finally'
    },
    'es6-number': {
        'patterns': [r'Number\.isNaN', r'Number\.isFinite', r'Number\.parseInt'],
        'keywords': ['Number.isNaN'],
        'description': 'ES6 Number'
    },
    'setimmediate': {
        'patterns': [r'setImmediate', r'clearImmediate'],
        'keywords': ['setImmediate'],
        'description': 'setImmediate'
    },
    'getrandomvalues': {
        'patterns': [r'crypto\.getRandomValues\s*\(', r'getRandomValues'],
        'keywords': ['getRandomValues'],
        'description': 'crypto.getRandomValues()'
    },
    'gyroscope': {
        'patterns': [r'new Gyroscope', r'Gyroscope'],
        'keywords': ['Gyroscope'],
        'description': 'Gyroscope'
    },
    'accelerometer': {
        'patterns': [r'new Accelerometer', r'Accelerometer'],
        'keywords': ['Accelerometer'],
        'description': 'Accelerometer'
    },
    'magnetometer': {
        'patterns': [r'new Magnetometer', r'Magnetometer'],
        'keywords': ['Magnetometer'],
        'description': 'Magnetometer'
    },
    'orientation-sensor': {
        'patterns': [r'OrientationSensor', r'AbsoluteOrientationSensor'],
        'keywords': ['OrientationSensor'],
        'description': 'Orientation Sensor'
    },
    'hardwareconcurrency': {
        'patterns': [r'navigator\.hardwareConcurrency'],
        'keywords': ['hardwareConcurrency'],
        'description': 'navigator.hardwareConcurrency'
    },
    'history': {
        'patterns': [r'history\.pushState', r'history\.replaceState', r'onpopstate'],
        'keywords': ['pushState', 'replaceState'],
        'description': 'Session history management'
    },
    'ime': {
        'patterns': [r'inputMethodContext', r'InputMethodContext'],
        'keywords': ['inputMethodContext'],
        'description': 'Input Method Editor API'
    },
    'import-maps': {
        'patterns': [r'<script type="importmap"', r'importmap'],
        'keywords': ['importmap'],
        'description': 'Import maps'
    },
    'imports': {
        'patterns': [r'<link rel="import"', r'HTMLImports'],
        'keywords': ['HTMLImports'],
        'description': 'HTML Imports'
    },
    'input-event': {
        'patterns': [r'oninput', r'addEventListener\s*\(\s*["\']input'],
        'keywords': ['oninput'],
        'description': 'input event'
    },
    'input-selection': {
        'patterns': [r'\.selectionStart', r'\.selectionEnd', r'\.setSelectionRange'],
        'keywords': ['selectionStart', 'selectionEnd'],
        'description': 'Selection controls for input & textarea'
    },
    'internationalization': {
        'patterns': [r'Intl\.', r'Intl\.Collator', r'Intl\.NumberFormat', r'Intl\.DateTimeFormat'],
        'keywords': ['Intl'],
        'description': 'Internationalization API'
    },
    'intersectionobserver-v2': {
        'patterns': [r'\.isVisible', r'IntersectionObserverEntry\.isVisible'],
        'keywords': ['isVisible'],
        'description': 'IntersectionObserver V2'
    },
    'intl-pluralrules': {
        'patterns': [r'Intl\.PluralRules', r'new Intl\.PluralRules'],
        'keywords': ['PluralRules'],
        'description': 'Intl.PluralRules API'
    },
    'js-regexp-lookbehind': {
        'patterns': [r'\(\?<=', r'\(\?<!'],
        'keywords': ['lookbehind'],
        'description': 'Lookbehind in JS regular expressions'
    },
    'keyboardevent-charcode': {
        'patterns': [r'\.charCode', r'event\.charCode'],
        'keywords': ['charCode'],
        'description': 'KeyboardEvent.charCode'
    },
    'keyboardevent-getmodifierstate': {
        'patterns': [r'\.getModifierState\s*\('],
        'keywords': ['getModifierState'],
        'description': 'KeyboardEvent.getModifierState()'
    },
    'keyboardevent-location': {
        'patterns': [r'\.location\b', r'\.keyLocation', r'event\.location'],
        'keywords': ['keyLocation'],
        'description': 'KeyboardEvent.location'
    },
    'lazyload': {
        'patterns': [r'<link rel="lazyload"'],
        'keywords': ['lazyload'],
        'description': 'Resource Hints: Lazyload'
    },
    'localecompare': {
        'patterns': [r'\.localeCompare\s*\('],
        'keywords': ['localeCompare'],
        'description': 'localeCompare()'
    },
    'matchesselector': {
        'patterns': [r'\.matches\s*\(', r'\.matchesSelector\s*\('],
        'keywords': ['matches', 'matchesSelector'],
        'description': 'matches() DOM method'
    },
    'matchmedia': {
        'patterns': [r'window\.matchMedia', r'matchMedia\s*\('],
        'keywords': ['matchMedia'],
        'description': 'matchMedia'
    },
    'media-fragments': {
        'patterns': [r'#t=', r'MediaFragments'],
        'keywords': ['media fragments'],
        'description': 'Media Fragments'
    },
    'mutation-events': {
        'patterns': [r'DOMAttrModified', r'DOMNodeInserted', r'DOMNodeRemoved'],
        'keywords': ['DOMAttrModified'],
        'description': 'Mutation events'
    },
    'objectrtc': {
        'patterns': [r'RTCIceTransport', r'RTCIceGatherer', r'RTCDtlsTransport'],
        'keywords': ['ORTC'],
        'description': 'Object RTC (ORTC) API for WebRTC'
    },
    'offline-apps': {
        'patterns': [r'applicationCache', r'window\.applicationCache'],
        'keywords': ['applicationCache', 'appcache'],
        'description': 'Offline web applications'
    },
    'path2d': {
        'patterns': [r'new Path2D', r'Path2D', r'\.addPath\s*\('],
        'keywords': ['Path2D'],
        'description': 'Path2D'
    },
    'permissions-policy': {
        'patterns': [r'Permissions-Policy', r'Feature-Policy'],
        'keywords': ['Permissions-Policy'],
        'description': 'Permissions Policy'
    },
    'feature-policy': {
        'patterns': [r'Feature-Policy', r'document\.featurePolicy'],
        'keywords': ['Feature-Policy'],
        'description': 'Feature Policy'
    },
    'sql-storage': {
        'patterns': [r'openDatabase', r'window\.openDatabase'],
        'keywords': ['openDatabase', 'websql'],
        'description': 'Web SQL Database'
    },
    'u2f': {
        'patterns': [r'u2f\.register', r'u2f\.sign'],
        'keywords': ['u2f', 'FIDO'],
        'description': 'FIDO U2F API'
    },
    'videotracks': {
        'patterns': [r'VideoTrack', r'VideoTrackList', r'\.videoTracks'],
        'keywords': ['VideoTrack'],
        'description': 'Video Tracks'
    },
    'audiotracks': {
        'patterns': [r'AudioTrack', r'AudioTrackList', r'\.audioTracks'],
        'keywords': ['AudioTrack'],
        'description': 'Audio Tracks'
    },
    'date-tolocaledatestring': {
        'patterns': [r'\.toLocaleDateString\s*\(', r'\.toLocaleTimeString\s*\('],
        'keywords': ['toLocaleDateString'],
        'description': 'Date.prototype.toLocaleDateString'
    },
    'eme': {
        'patterns': [r'requestMediaKeySystemAccess', r'MediaKeys'],
        'keywords': ['EME', 'MediaKeys'],
        'description': 'Encrypted Media Extensions'
    },
    'forms': {
        'patterns': [r'<form', r'HTMLFormElement'],
        'keywords': ['form'],
        'description': 'HTML5 form features'
    },
    'getelementsbyclassname': {
        'patterns': [r'\.getElementsByClassName\s*\('],
        'keywords': ['getElementsByClassName'],
        'description': 'getElementsByClassName'
    },
    'img-naturalwidth-naturalheight': {
        'patterns': [r'\.naturalWidth', r'\.naturalHeight'],
        'keywords': ['naturalWidth', 'naturalHeight'],
        'description': 'naturalWidth & naturalHeight image properties'
    },
    'input-pattern': {
        'patterns': [r'pattern\s*=', r'\.pattern\b'],
        'keywords': ['pattern'],
        'description': 'Pattern attribute for input fields'
    },
    'link-icon-svg': {
        'patterns': [r'<link.*icon.*\.svg', r'rel="icon".*\.svg'],
        'keywords': ['svg favicon'],
        'description': 'SVG favicons'
    },
    'style-scoped': {
        'patterns': [r'<style scoped', r'scoped\s+style'],
        'keywords': ['scoped'],
        'description': 'Scoped attribute'
    },
    'array-find-index': {
        'patterns': [r'\.findIndex\s*\('],
        'keywords': ['findIndex'],
        'description': 'Array.prototype.findIndex'
    },
    'audio-api': {
        'patterns': [r'AudioContext', r'webkitAudioContext', r'new AudioContext'],
        'keywords': ['AudioContext'],
        'description': 'Web Audio API'
    },
    'background-sync': {
        'patterns': [r'sync\.register', r'SyncManager'],
        'keywords': ['BackgroundSync'],
        'description': 'Background Sync API'
    },
    'beacon': {
        'patterns': [r'navigator\.sendBeacon', r'sendBeacon\s*\('],
        'keywords': ['sendBeacon'],
        'description': 'Beacon API'
    },
    'blobbuilder': {
        'patterns': [r'new Blob\s*\(', r'BlobBuilder'],
        'keywords': ['Blob'],
        'description': 'Blob constructing'
    },
    'client-hints-dpr-width-viewport': {
        'patterns': [r'Viewport-Width', r'\bdevice-memory\b', r'Sec-CH-'],
        'keywords': ['Client Hints'],
        'description': 'Client Hints: DPR, Width, Viewport-Width'
    },
    'console-basic': {
        'patterns': [r'console\.log', r'console\.warn', r'console\.error'],
        'keywords': ['console.log'],
        'description': 'Basic console logging functions'
    },
    'constraint-validation': {
        'patterns': [r'\.validity', r'\.checkValidity', r'\.setCustomValidity'],
        'keywords': ['validity', 'checkValidity'],
        'description': 'Constraint Validation API'
    },
    'cookie-store-api': {
        'patterns': [r'cookieStore', r'navigator\.cookieStore'],
        'keywords': ['cookieStore'],
        'description': 'Cookie Store API'
    },
    'cors': {
        'patterns': [r'crossOrigin', r'Access-Control'],
        'keywords': ['CORS'],
        'description': 'Cross-Origin Resource Sharing'
    },
    'createimagebitmap': {
        'patterns': [r'createImageBitmap\s*\('],
        'keywords': ['createImageBitmap'],
        'description': 'createImageBitmap'
    },
    'cross-document-view-transitions': {
        'patterns': [r'startViewTransition', r'cross-document'],
        'keywords': ['cross-document view transitions'],
        'description': 'View Transitions (cross-document)'
    },
    'css-module-scripts': {
        'patterns': [r'import.*\.css', r'CSS Module'],
        'keywords': ['CSS Module Scripts'],
        'description': 'CSS Module Scripts'
    },
    'css-paint-api': {
        'patterns': [r'CSS\.paintWorklet', r'registerPaint'],
        'keywords': ['CSS Paint API'],
        'description': 'CSS Painting API'
    },
    'css-supports-api': {
        'patterns': [r'CSS\.supports\s*\('],
        'keywords': ['CSS.supports'],
        'description': 'CSS.supports() API'
    },
    'customevent': {
        'patterns': [r'new CustomEvent', r'CustomEvent'],
        'keywords': ['CustomEvent'],
        'description': 'CustomEvent'
    },
    'decorators': {
        'patterns': [r'^\s*@\w+', r'decorator'],
        'keywords': ['decorators'],
        'description': 'Decorators'
    },
    'dispatchevent': {
        'patterns': [r'\.dispatchEvent\s*\('],
        'keywords': ['dispatchEvent'],
        'description': 'EventTarget.dispatchEvent'
    },
    'do-not-track': {
        'patterns': [r'navigator\.doNotTrack', r'doNotTrack'],
        'keywords': ['doNotTrack'],
        'description': 'Do Not Track API'
    },
    'document-currentscript': {
        'patterns': [r'document\.currentScript'],
        'keywords': ['currentScript'],
        'description': 'document.currentScript'
    },
    'dom-manip-convenience': {
        'patterns': [r'(?:document|Element|element|node|el|div|span|body|container|wrapper|parent|child)\.append\s*\(', r'\.prepend\s*\(', r'\.before\s*\(', r'\.after\s*\(', r'\.replaceWith\s*\('],
        'keywords': ['append', 'prepend'],
        'description': 'DOM manipulation convenience methods'
    },
    'dommatrix': {
        'patterns': [r'new DOMMatrix', r'DOMMatrix'],
        'keywords': ['DOMMatrix'],
        'description': 'DOMMatrix'
    },
    'element-closest': {
        'patterns': [r'\.closest\s*\('],
        'keywords': ['closest'],
        'description': 'Element.closest()'
    },
    'element-scroll-methods': {
        'patterns': [r'\.scroll\s*\(', r'\.scrollTo\s*\(', r'\.scrollBy\s*\('],
        'keywords': ['scroll', 'scrollTo'],
        'description': 'Scroll methods on elements'
    },
    'es6-module': {
        'patterns': [r'import\s+', r'export\s+'],
        'keywords': ['module'],
        'description': 'JavaScript modules via script tag'
    },
    'es6-module-dynamic-import': {
        'patterns': [r'import\s*\('],
        'keywords': ['dynamic import'],
        'description': 'JavaScript modules: dynamic import()'
    },
    'fieldset-disabled': {
        'patterns': [r'<fieldset disabled', r'fieldset.*disabled'],
        'keywords': ['fieldset disabled'],
        'description': 'disabled attribute of the fieldset element'
    },
    'filereadersync': {
        'patterns': [r'new FileReaderSync', r'FileReaderSync'],
        'keywords': ['FileReaderSync'],
        'description': 'FileReaderSync'
    },
    'font-loading': {
        'patterns': [r'document\.fonts', r'FontFace', r'FontFaceSet'],
        'keywords': ['FontFace'],
        'description': 'CSS Font Loading'
    },
    'form-attribute': {
        'patterns': [r'form\s*=', r'\.form\b'],
        'keywords': ['form attribute'],
        'description': 'Form attribute'
    },
    'form-submit-attributes': {
        'patterns': [r'formaction', r'formmethod', r'formtarget'],
        'keywords': ['formaction'],
        'description': 'Attributes for form submission'
    },
    'input-email-tel-url': {
        'patterns': [r'type="email"', r'type="tel"', r'type="url"'],
        'keywords': ['email', 'tel', 'url'],
        'description': 'Email, telephone & URL input types'
    },
    'abortcontroller': {
        'patterns': [r'new AbortController', r'AbortController', r'AbortSignal'],
        'keywords': ['AbortController', 'AbortSignal'],
        'description': 'AbortController & AbortSignal'
    },
    'alternate-stylesheet': {
        'patterns': [r'rel="alternate stylesheet"', r'alternate stylesheet'],
        'keywords': ['alternate stylesheet'],
        'description': 'Alternate stylesheet'
    },
    'canvas-blending': {
        'patterns': [r'globalCompositeOperation', r'\.globalCompositeOperation\s*='],
        'keywords': ['globalCompositeOperation', 'blend modes'],
        'description': 'Canvas blend modes'
    },
    'webgl': {
        'patterns': [r'getContext\s*\(\s*["\']webgl["\']', r'WebGLRenderingContext'],
        'keywords': ['webgl', 'WebGL'],
        'description': 'WebGL - 3D Canvas graphics'
    },
    'webgl2': {
        'patterns': [r'getContext\s*\(\s*["\']webgl2["\']', r'WebGL2RenderingContext'],
        'keywords': ['webgl2', 'WebGL2'],
        'description': 'WebGL 2.0'
    },
    'svg-css': {
        'patterns': [r'background.*\.svg', r'background-image.*svg'],
        'keywords': ['svg background'],
        'description': 'SVG in CSS backgrounds'
    },
    'svg-filters': {
        'patterns': [r'<filter', r'<feGaussianBlur', r'<feColorMatrix'],
        'keywords': ['svg filter'],
        'description': 'SVG filters'
    },
    'svg-fonts': {
        'patterns': [r'<font-face', r'<glyph'],
        'keywords': ['svg font'],
        'description': 'SVG fonts'
    },
    'svg-fragment': {
        'patterns': [r'\.svg#', r'svg.*#svgView'],
        'keywords': ['svg fragment'],
        'description': 'SVG fragment identifiers'
    },
    'svg-html': {
        'patterns': [r'<foreignObject', r'foreignObject'],
        'keywords': ['foreignObject'],
        'description': 'SVG effects for HTML'
    },
    'svg-img': {
        'patterns': [r'<img.*\.svg', r'src=.*\.svg'],
        'keywords': ['svg img'],
        'description': 'SVG in HTML img element'
    },
    'svg-smil': {
        'patterns': [r'<animate', r'<animateTransform', r'<animateMotion'],
        'keywords': ['svg animation'],
        'description': 'SVG SMIL animation'
    },
    'vector-effect': {
        'patterns': [r'vector-effect', r'non-scaling-stroke'],
        'keywords': ['vector-effect'],
        'description': 'SVG vector-effect'
    },
}

# JavaScript Array Methods
JS_ARRAY_METHODS = {
    'array-flat': {
        'patterns': [r'\.flat\s*\(', r'\.flatMap\s*\('],
        'keywords': ['.flat', '.flatMap'],
        'description': 'Array.flat/flatMap'
    },
    'array-includes': {
        'patterns': [r'\.includes\s*\('],
        'keywords': ['.includes'],
        'description': 'Array.includes'
    },
    'array-find': {
        'patterns': [r'\.find\s*\(', r'\.findIndex\s*\(', r'\.findLast\s*\(', r'\.findLastIndex\s*\('],
        'keywords': ['.find', '.findIndex', '.findLast', '.findLastIndex'],
        'description': 'Array.find/findIndex/findLast/findLastIndex'
    },
}

# JavaScript String Methods
JS_STRING_METHODS = {
    'es6-string-includes': {
        'patterns': [r'\.includes\s*\('],
        'keywords': ['.includes'],
        'description': 'String.includes'
    },
    'pad-start-end': {
        'patterns': [r'\.padStart\s*\(', r'\.padEnd\s*\('],
        'keywords': ['.padStart', '.padEnd'],
        'description': 'String.padStart/padEnd'
    },
}

# JavaScript Object Methods
JS_OBJECT_METHODS = {
    'object-entries': {
        'patterns': [r'Object\.entries\s*\('],
        'keywords': ['Object.entries'],
        'description': 'Object.entries'
    },
    'object-values': {
        'patterns': [r'Object\.values\s*\('],
        'keywords': ['Object.values'],
        'description': 'Object.values method'
    },
    'object-observe': {
        'patterns': [r'Object\.observe\s*\('],
        'keywords': ['Object.observe'],
        'description': 'Object.observe data binding'
    },
}

# Web Storage APIs
JS_STORAGE_APIS = {
    'namevalue-storage': {
        'patterns': [r'\blocalStorage', r'\bsessionStorage'],
        'keywords': ['localStorage', 'sessionStorage'],
        'description': 'Web Storage (localStorage/sessionStorage)'
    },
    'indexeddb': {
        'patterns': [r'\bindexedDB', r'\.openDatabase'],
        'keywords': ['indexedDB'],
        'description': 'IndexedDB'
    },
}

# DOM APIs
JS_DOM_APIS = {
    'queryselector': {
        'patterns': [r'\.querySelector\s*\(', r'\.querySelectorAll\s*\('],
        'keywords': ['querySelector', 'querySelectorAll'],
        'description': 'querySelector/querySelectorAll'
    },
    'classlist': {
        'patterns': [r'\.classList'],
        'keywords': ['classList'],
        'description': 'Element.classList'
    },
    'dataset': {
        'patterns': [r'\.dataset'],
        'keywords': ['dataset'],
        'description': 'HTMLElement.dataset'
    },
    'custom-elements': {
        'patterns': [r'customElements\.define', r'HTMLElement'],
        'keywords': ['customElements'],
        'description': 'Custom Elements'
    },
    'custom-elementsv1': {
        'patterns': [r'customElements\.define', r'customElements\.get'],
        'keywords': ['customElements'],
        'description': 'Custom Elements (V1)'
    },
    'addeventlistener': {
        'patterns': [r'\.addEventListener\s*\(', r'\.removeEventListener\s*\('],
        'keywords': ['addEventListener'],
        'description': 'EventTarget.addEventListener()'
    },
    'domcontentloaded': {
        'patterns': [r'DOMContentLoaded', r'addEventListener\s*\(\s*["\']DOMContentLoaded'],
        'keywords': ['DOMContentLoaded'],
        'description': 'DOMContentLoaded event'
    },
    'hashchange': {
        'patterns': [r'hashchange', r'addEventListener\s*\(\s*["\']hashchange'],
        'keywords': ['hashchange'],
        'description': 'Hashchange event'
    },
    'page-transition-events': {
        'patterns': [r'pageshow', r'pagehide', r'PageTransitionEvent'],
        'keywords': ['pageshow', 'pagehide'],
        'description': 'PageTransitionEvent'
    },
    'beforeafterprint': {
        'patterns': [r'beforeprint', r'afterprint'],
        'keywords': ['beforeprint', 'afterprint'],
        'description': 'Printing Events'
    },
    'focusin-focusout-events': {
        'patterns': [r'focusin', r'focusout'],
        'keywords': ['focusin', 'focusout'],
        'description': 'focusin & focusout events'
    },
    'getboundingclientrect': {
        'patterns': [r'\.getBoundingClientRect\s*\('],
        'keywords': ['getBoundingClientRect'],
        'description': 'Element.getBoundingClientRect()'
    },
    'element-from-point': {
        'patterns': [r'document\.elementFromPoint', r'\.elementFromPoint\s*\('],
        'keywords': ['elementFromPoint'],
        'description': 'document.elementFromPoint()'
    },
    'textcontent': {
        'patterns': [r'\.textContent'],
        'keywords': ['textContent'],
        'description': 'Node.textContent'
    },
    'innertext': {
        'patterns': [r'\.innerText'],
        'keywords': ['innerText'],
        'description': 'HTMLElement.innerText'
    },
    'insertadjacenthtml': {
        'patterns': [r'\.insertAdjacentHTML\s*\('],
        'keywords': ['insertAdjacentHTML'],
        'description': 'Element.insertAdjacentHTML()'
    },
    'insert-adjacent': {
        'patterns': [r'\.insertAdjacentElement\s*\(', r'\.insertAdjacentText\s*\('],
        'keywords': ['insertAdjacentElement'],
        'description': 'Element.insertAdjacentElement()'
    },
    'childnode-remove': {
        'patterns': [r'\.remove\s*\(\s*\)'],
        'keywords': ['.remove'],
        'description': 'ChildNode.remove()'
    },
    'dom-range': {
        'patterns': [r'document\.createRange', r'new Range', r'Range'],
        'keywords': ['Range'],
        'description': 'Document Object Model Range'
    },
    'comparedocumentposition': {
        'patterns': [r'\.compareDocumentPosition\s*\('],
        'keywords': ['compareDocumentPosition'],
        'description': 'Node.compareDocumentPosition()'
    },
    'keyboardevent-key': {
        'patterns': [r'\.key\b', r'event\.key', r'KeyboardEvent'],
        'keywords': ['event.key'],
        'description': 'KeyboardEvent.key'
    },
    'keyboardevent-code': {
        'patterns': [r'\.code\b', r'event\.code'],
        'keywords': ['event.code'],
        'description': 'KeyboardEvent.code'
    },
    'keyboardevent-which': {
        'patterns': [r'\.which\b', r'event\.which'],
        'keywords': ['event.which'],
        'description': 'KeyboardEvent.which'
    },
    'devicepixelratio': {
        'patterns': [r'window\.devicePixelRatio', r'devicePixelRatio'],
        'keywords': ['devicePixelRatio'],
        'description': 'Window.devicePixelRatio'
    },
    'getcomputedstyle': {
        'patterns': [r'getComputedStyle\s*\(', r'window\.getComputedStyle'],
        'keywords': ['getComputedStyle'],
        'description': 'getComputedStyle'
    },
    'document-execcommand': {
        'patterns': [r'document\.execCommand', r'\.execCommand\s*\('],
        'keywords': ['execCommand'],
        'description': 'Document.execCommand()'
    },
    'xml-serializer': {
        'patterns': [r'XMLSerializer', r'new XMLSerializer', r'DOMParser'],
        'keywords': ['XMLSerializer', 'DOMParser'],
        'description': 'DOM Parsing and Serialization'
    },
    'trusted-types': {
        'patterns': [r'trustedTypes', r'TrustedHTML', r'TrustedScript'],
        'keywords': ['trustedTypes'],
        'description': 'Trusted Types for DOM manipulation'
    },
    'shadowdomv1': {
        'patterns': [r'\.attachShadow\s*\(', r'shadowRoot'],
        'keywords': ['attachShadow', 'shadowRoot'],
        'description': 'Shadow DOM (V1)'
    },
    'shadowdom': {
        'patterns': [r'\.createShadowRoot\s*\('],
        'keywords': ['createShadowRoot'],
        'description': 'Shadow DOM (deprecated V0 spec)'
    },
    'imagecapture': {
        'patterns': [r'new ImageCapture', r'ImageCapture'],
        'keywords': ['ImageCapture'],
        'description': 'ImageCapture API'
    },
    'mediacapture-fromelement': {
        'patterns': [r'\.captureStream\s*\(', r'HTMLMediaElement\.captureStream'],
        'keywords': ['captureStream'],
        'description': 'Media Capture from DOM Elements API'
    },
    'rellist': {
        'patterns': [r'\.relList'],
        'keywords': ['relList'],
        'description': 'relList (DOMTokenList)'
    },
    'scrollintoview': {
        'patterns': [r'\.scrollIntoView\s*\('],
        'keywords': ['scrollIntoView'],
        'description': 'scrollIntoView'
    },
    'scrollintoviewifneeded': {
        'patterns': [r'\.scrollIntoViewIfNeeded\s*\('],
        'keywords': ['scrollIntoViewIfNeeded'],
        'description': 'Element.scrollIntoViewIfNeeded()'
    },
    'once-event-listener': {
        'patterns': [r'once\s*:\s*true', r'\{\s*once\s*:\s*true\s*\}'],
        'keywords': ['once'],
        'description': '"once" event listener option'
    },
    'passive-event-listener': {
        'patterns': [r'passive\s*:\s*true', r'\{\s*passive\s*:\s*true\s*\}'],
        'keywords': ['passive'],
        'description': 'Passive event listeners'
    },
    'auxclick': {
        'patterns': [r'auxclick', r'addEventListener\s*\(\s*["\']auxclick'],
        'keywords': ['auxclick'],
        'description': 'Auxclick'
    },
    'registerprotocolhandler': {
        'patterns': [r'navigator\.registerProtocolHandler'],
        'keywords': ['registerProtocolHandler'],
        'description': 'Custom protocol handling'
    },
    'documenthead': {
        'patterns': [r'document\.head'],
        'keywords': ['document.head'],
        'description': 'document.head'
    },
    'document-scrollingelement': {
        'patterns': [r'document\.scrollingElement'],
        'keywords': ['scrollingElement'],
        'description': 'document.scrollingElement'
    },
    'document-evaluate-xpath': {
        'patterns': [r'document\.evaluate', r'XPathResult'],
        'keywords': ['document.evaluate', 'XPath'],
        'description': 'document.evaluate & XPath'
    },
    'declarative-shadow-dom': {
        'patterns': [r'shadowrootmode', r'shadowroot'],
        'keywords': ['shadowrootmode'],
        'description': 'Declarative Shadow DOM'
    },
    # Additional HTML/DOM features accessible via JavaScript
    'dialog': {
        'patterns': [r'\.showModal\s*\(', r'\.close\s*\(', r'HTMLDialogElement'],
        'keywords': ['showModal', 'HTMLDialogElement'],
        'description': 'Dialog element (JS API)'
    },
    'template': {
        'patterns': [r'\.content\b', r'HTMLTemplateElement', r'document\.importNode'],
        'keywords': ['template.content'],
        'description': 'HTML templates (JS API)'
    },
    'picture': {
        'patterns': [r'HTMLPictureElement'],
        'keywords': ['HTMLPictureElement'],
        'description': 'Picture element (JS API)'
    },
    'indeterminate-checkbox': {
        'patterns': [r'\.indeterminate\s*=', r'\.indeterminate\b'],
        'keywords': ['indeterminate'],
        'description': 'Indeterminate checkbox state'
    },
    'maxlength': {
        'patterns': [r'\.maxLength', r'maxlength'],
        'keywords': ['maxLength'],
        'description': 'maxlength attribute (JS access)'
    },
    'readonly-attr': {
        'patterns': [r'\.readOnly\s*=', r'\.readOnly\b'],
        'keywords': ['readOnly'],
        'description': 'readonly attribute (JS access)'
    },
    'input-autocomplete-onoff': {
        'patterns': [r'\.autocomplete\s*='],
        'keywords': ['autocomplete'],
        'description': 'autocomplete attribute (JS access)'
    },
    'input-inputmode': {
        'patterns': [r'\.inputMode\s*=', r'inputmode'],
        'keywords': ['inputMode'],
        'description': 'inputmode attribute (JS access)'
    },
    'meta-theme-color': {
        'patterns': [r'theme-color', r'meta.*theme-color'],
        'keywords': ['theme-color'],
        'description': 'theme-color meta tag (JS access)'
    },
    'script-async': {
        'patterns': [r'\.async\s*=\s*true', r'script\.async'],
        'keywords': ['script.async'],
        'description': 'async attribute for scripts (JS access)'
    },
    'script-defer': {
        'patterns': [r'\.defer\s*=\s*true', r'script\.defer'],
        'keywords': ['script.defer'],
        'description': 'defer attribute for scripts (JS access)'
    },
    'link-rel-preload': {
        'patterns': [r'rel\s*=\s*["\']preload', r'link\.rel.*preload'],
        'keywords': ['preload'],
        'description': 'Resource Hints: preload (JS access)'
    },
    'link-rel-prefetch': {
        'patterns': [r'rel\s*=\s*["\']prefetch', r'link\.rel.*prefetch'],
        'keywords': ['prefetch'],
        'description': 'Resource Hints: prefetch (JS access)'
    },
    'link-rel-preconnect': {
        'patterns': [r'rel\s*=\s*["\']preconnect'],
        'keywords': ['preconnect'],
        'description': 'Resource Hints: preconnect (JS access)'
    },
    'link-rel-dns-prefetch': {
        'patterns': [r'rel\s*=\s*["\']dns-prefetch'],
        'keywords': ['dns-prefetch'],
        'description': 'Resource Hints: dns-prefetch (JS access)'
    },
    'link-rel-modulepreload': {
        'patterns': [r'rel\s*=\s*["\']modulepreload'],
        'keywords': ['modulepreload'],
        'description': 'Resource Hints: modulepreload (JS access)'
    },
    'link-rel-prerender': {
        'patterns': [r'rel\s*=\s*["\']prerender'],
        'keywords': ['prerender'],
        'description': 'Resource Hints: prerender (JS access)'
    },
    'rel-noopener': {
        'patterns': [r'rel\s*=\s*["\'].*noopener', r'\.relList\.add\s*\(\s*["\']noopener'],
        'keywords': ['noopener'],
        'description': 'rel=noopener (JS access)'
    },
    'rel-noreferrer': {
        'patterns': [r'rel\s*=\s*["\'].*noreferrer', r'\.relList\.add\s*\(\s*["\']noreferrer'],
        'keywords': ['noreferrer'],
        'description': 'rel=noreferrer (JS access)'
    },
    'input-file-directory': {
        'patterns': [r'webkitdirectory', r'\.webkitdirectory'],
        'keywords': ['webkitdirectory'],
        'description': 'Directory selection from file input (JS access)'
    },
    # WebAssembly features
    'wasm': {
        'patterns': [r'WebAssembly\.', r'WebAssembly\.instantiate', r'WebAssembly\.compile', r'\.wasm'],
        'keywords': ['WebAssembly', 'wasm'],
        'description': 'WebAssembly'
    },
    'wasm-bigint': {
        'patterns': [r'WebAssembly.*BigInt', r'i64.*BigInt'],
        'keywords': ['wasm bigint'],
        'description': 'WebAssembly BigInt to i64 conversion'
    },
    'wasm-threads': {
        'patterns': [r'SharedArrayBuffer', r'Atomics\.'],
        'keywords': ['SharedArrayBuffer', 'Atomics'],
        'description': 'WebAssembly Threads and Atomics'
    },
    'wasm-simd': {
        'patterns': [r'v128', r'SIMD'],
        'keywords': ['wasm simd'],
        'description': 'WebAssembly SIMD'
    },
    'wasm-bulk-memory': {
        'patterns': [r'memory\.copy', r'memory\.fill'],
        'keywords': ['bulk memory'],
        'description': 'WebAssembly Bulk Memory Operations'
    },
    'wasm-multi-value': {
        'patterns': [r'multi-value', r'multivalue'],
        'keywords': ['multi-value'],
        'description': 'WebAssembly Multi-Value'
    },
    'wasm-mutable-globals': {
        'patterns': [r'WebAssembly\.Global', r'mutable.*global'],
        'keywords': ['mutable globals'],
        'description': 'WebAssembly Import/Export of Mutable Globals'
    },
    'wasm-reference-types': {
        'patterns': [r'externref', r'funcref'],
        'keywords': ['externref', 'funcref'],
        'description': 'WebAssembly Reference Types'
    },
    'wasm-signext': {
        'patterns': [r'i32\.extend8_s', r'i32\.extend16_s', r'i64\.extend8_s'],
        'keywords': ['sign extension'],
        'description': 'WebAssembly Sign Extension Operators'
    },
    'wasm-nontrapping-fptoint': {
        'patterns': [r'i32\.trunc_sat', r'i64\.trunc_sat'],
        'keywords': ['trunc_sat'],
        'description': 'WebAssembly Non-trapping float-to-int Conversion'
    },
    # Data URIs
    'datauri': {
        'patterns': [r'data:image/', r'data:text/', r'data:application/'],
        'keywords': ['data:'],
        'description': 'Data URIs'
    },
    # URL Scroll-To-Text Fragment
    'url-scroll-to-text-fragment': {
        'patterns': [r':~:text='],
        'keywords': ['scroll-to-text'],
        'description': 'URL Scroll-To-Text Fragment'
    },
}

# All JavaScript features combined
ALL_JS_FEATURES = {
    **JS_SYNTAX_FEATURES,
    **JS_API_FEATURES,
    **JS_ARRAY_METHODS,
    **JS_STRING_METHODS,
    **JS_OBJECT_METHODS,
    **JS_STORAGE_APIS,
    **JS_DOM_APIS,
}
