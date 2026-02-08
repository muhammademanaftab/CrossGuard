"""JavaScript Parser for Feature Extraction.

This module parses JavaScript files and extracts modern ES6+ features
that need compatibility checking.
"""

from typing import Set, List, Dict, Optional
from pathlib import Path
import re

from .js_feature_maps import ALL_JS_FEATURES
from .custom_rules_loader import get_custom_js_rules
from ..utils.config import get_logger

# Module logger
logger = get_logger('parsers.js')


class JavaScriptParser:
    """Parser for extracting JavaScript features from JS files."""

    def __init__(self):
        """Initialize the JavaScript parser."""
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()  # Patterns not matched by any rule
        self._matched_apis = set()  # Track APIs/methods matched during detection
        # Merge built-in rules with custom rules
        self._all_features = {**ALL_JS_FEATURES, **get_custom_js_rules()}
        
    def parse_file(self, filepath: str) -> Set[str]:
        """Parse a JavaScript file and extract features.
        
        Args:
            filepath: Path to the JavaScript file
            
        Returns:
            Set of Can I Use feature IDs found in the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"JavaScript file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            return self.parse_string(js_content)
            
        except UnicodeDecodeError:
            raise ValueError(f"File is not valid UTF-8: {filepath}")
        except Exception as e:
            raise ValueError(f"Error parsing JavaScript file: {e}")
    
    def parse_string(self, js_content: str) -> Set[str]:
        """Parse JavaScript string and extract features.

        Args:
            js_content: JavaScript content as string

        Returns:
            Set of Can I Use feature IDs found
        """
        # Reset state
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()
        self._matched_apis = set()

        # Detect directive strings BEFORE removing comments/strings
        # (because "use strict" and "use asm" are string directives)
        self._detect_directives(js_content)

        # Detect event listeners BEFORE removing strings
        # (because event names like 'unhandledrejection' are inside strings)
        self._detect_event_listeners(js_content)

        # Remove comments to avoid false positives
        cleaned_content = self._remove_comments(js_content)

        # Detect features using regex patterns
        self._detect_features(cleaned_content)

        # Find unrecognized patterns
        self._find_unrecognized_patterns(cleaned_content)

        return self.features_found

    def _detect_directives(self, js_content: str):
        """Detect JavaScript directive strings like 'use strict' and 'use asm'.

        These need to be detected before string removal since they ARE strings.

        Args:
            js_content: Original JavaScript content
        """
        # Directives to detect (feature_id, patterns, description)
        directives = [
            ('use-strict', [r'["\']use strict["\']'], 'ECMAScript 5 Strict Mode'),
            ('asmjs', [r'["\']use asm["\']'], 'asm.js'),
        ]

        for feature_id, patterns, description in directives:
            for pattern in patterns:
                try:
                    if re.search(pattern, js_content):
                        self.features_found.add(feature_id)
                        self.feature_details.append({
                            'feature': feature_id,
                            'description': description,
                            'matched_apis': ['"use strict"' if 'strict' in pattern else '"use asm"'],
                        })
                        break
                except re.error:
                    continue

    def _detect_event_listeners(self, js_content: str):
        """Detect event listeners before string removal.

        Event names like 'unhandledrejection' appear inside addEventListener()
        string arguments and would be missed after string content is removed.

        Args:
            js_content: Original JavaScript content
        """
        # Event name to Can I Use feature mapping
        event_features = {
            'unhandledrejection': ('unhandledrejection', 'unhandledrejection event'),
            'rejectionhandled': ('unhandledrejection', 'rejectionhandled event'),
            'hashchange': ('hashchange', 'hashchange event'),
            'DOMContentLoaded': ('domcontentloaded', 'DOMContentLoaded event'),
            'online': ('online-status', 'online event'),
            'offline': ('online-status', 'offline event'),
            'visibilitychange': ('pagevisibility', 'visibilitychange event'),
            'deviceorientation': ('deviceorientation', 'deviceorientation event'),
            'devicemotion': ('deviceorientation', 'devicemotion event'),
            'orientationchange': ('screen-orientation', 'orientationchange event'),
            'fullscreenchange': ('fullscreen', 'fullscreenchange event'),
            'fullscreenerror': ('fullscreen', 'fullscreenerror event'),
            'pointerlockchange': ('pointerlock', 'pointerlockchange event'),
            'pointerlockerror': ('pointerlock', 'pointerlockerror event'),
            'gamepadconnected': ('gamepad', 'gamepadconnected event'),
            'gamepaddisconnected': ('gamepad', 'gamepaddisconnected event'),
            # Focus events
            'focusin': ('focusin-focusout-events', 'focusin event'),
            'focusout': ('focusin-focusout-events', 'focusout event'),
            # Page transition events
            'pageshow': ('page-transition-events', 'pageshow event'),
            'pagehide': ('page-transition-events', 'pagehide event'),
            # Print events
            'beforeprint': ('beforeafterprint', 'beforeprint event'),
            'afterprint': ('beforeafterprint', 'afterprint event'),
            # Mouse events
            'auxclick': ('auxclick', 'auxclick event'),
        }

        # Pattern to match addEventListener('eventName', ...) or on('eventName', ...)
        event_pattern = r'''(?:addEventListener|on)\s*\(\s*['"](\w+)['"]'''

        for match in re.finditer(event_pattern, js_content):
            event_name = match.group(1)
            if event_name in event_features:
                feature_id, description = event_features[event_name]
                if feature_id not in self.features_found:
                    self.features_found.add(feature_id)
                    self.feature_details.append({
                        'feature': feature_id,
                        'description': description,
                        'matched_apis': [f"addEventListener('{event_name}')"],
                    })

    def _remove_comments_and_strings(self, js_content: str) -> str:
        """Remove JavaScript comments and string literals from code.

        This prevents false positives from features mentioned in:
        - Single-line comments //
        - Multi-line comments /* */
        - String literals "..." and '...'
        - Template literals `...` (but not the backticks themselves)

        The order of operations is important:
        1. First remove strings (so // inside strings doesn't get treated as comment)
        2. Then remove comments

        Args:
            js_content: JavaScript code

        Returns:
            Code without comments and string literals
        """
        result = []
        i = 0
        length = len(js_content)

        while i < length:
            # Check for single-line comment
            if i < length - 1 and js_content[i:i+2] == '//':
                # Skip until end of line
                while i < length and js_content[i] != '\n':
                    i += 1
                continue

            # Check for multi-line comment
            if i < length - 1 and js_content[i:i+2] == '/*':
                # Skip until */
                i += 2
                while i < length - 1 and js_content[i:i+2] != '*/':
                    i += 1
                i += 2  # Skip */
                continue

            # Check for double-quoted string
            if js_content[i] == '"':
                result.append('"')  # Keep opening quote
                i += 1
                while i < length:
                    if js_content[i] == '\\' and i + 1 < length:
                        i += 2  # Skip escaped character
                    elif js_content[i] == '"':
                        result.append('"')  # Keep closing quote
                        i += 1
                        break
                    else:
                        i += 1
                continue

            # Check for single-quoted string
            if js_content[i] == "'":
                result.append("'")  # Keep opening quote
                i += 1
                while i < length:
                    if js_content[i] == '\\' and i + 1 < length:
                        i += 2  # Skip escaped character
                    elif js_content[i] == "'":
                        result.append("'")  # Keep closing quote
                        i += 1
                        break
                    else:
                        i += 1
                continue

            # Check for template literal
            if js_content[i] == '`':
                result.append('`')  # Keep backtick for template-literal detection
                i += 1
                while i < length:
                    if js_content[i] == '\\' and i + 1 < length:
                        i += 2  # Skip escaped character
                    elif js_content[i] == '`':
                        result.append('`')  # Keep closing backtick
                        i += 1
                        break
                    elif js_content[i:i+2] == '${':
                        # Keep ${x} structure for template literal detection
                        result.append('${x}')
                        i += 2
                        depth = 1
                        while i < length and depth > 0:
                            if js_content[i] == '{':
                                depth += 1
                            elif js_content[i] == '}':
                                depth -= 1
                            i += 1
                    else:
                        i += 1
                continue

            # Regular character - keep it
            result.append(js_content[i])
            i += 1

        return ''.join(result)

    def _remove_comments(self, js_content: str) -> str:
        """Remove JavaScript comments and strings from code.

        Args:
            js_content: JavaScript code

        Returns:
            Code without comments and string content
        """
        return self._remove_comments_and_strings(js_content)
    
    def _detect_features(self, js_content: str):
        """Detect JavaScript features using regex patterns.

        Args:
            js_content: JavaScript code (without comments)
        """
        # Check each feature (includes both built-in and custom rules)
        for feature_id, feature_info in self._all_features.items():
            patterns = feature_info.get('patterns', [])
            matched_apis = []
            feature_found = False

            # Check all patterns and collect matched APIs
            for pattern in patterns:
                try:
                    if re.search(pattern, js_content):
                        feature_found = True
                        # Extract API name from pattern
                        # Patterns like 'navigator\.geolocation' -> 'navigator.geolocation'
                        # Patterns like '\bfetch\s*\(' -> 'fetch()'
                        # Patterns like '\bnew\s+Promise' -> 'new Promise'
                        api_name = self._extract_api_name(pattern)
                        if api_name and api_name not in matched_apis:
                            matched_apis.append(api_name)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern for {feature_id}: {e}")
                    continue

            if feature_found:
                self.features_found.add(feature_id)
                # Deduplicate: only append if feature_id not already in feature_details
                if not any(d['feature'] == feature_id for d in self.feature_details):
                    self.feature_details.append({
                        'feature': feature_id,
                        'description': feature_info.get('description', ''),
                        'matched_apis': matched_apis,
                    })
                # Track matched APIs for unrecognized pattern filtering
                for api in matched_apis:
                    # Extract method/API name from matched API
                    # e.g., "Promise.all()" -> "Promise", "all"
                    # e.g., ".then()" -> "then"
                    # e.g., "new Promise" -> "Promise"
                    api_clean = api.replace('()', '').replace('new ', '')
                    parts = api_clean.split('.')
                    for part in parts:
                        if part:
                            self._matched_apis.add(part)

    def _extract_api_name(self, pattern: str) -> str:
        """Extract a readable API name from a regex pattern.

        Args:
            pattern: Regex pattern string

        Returns:
            Human-readable API name or empty string
        """
        # Remove common regex escapes and word boundaries
        cleaned = pattern.replace('\\b', '').replace('\\s*', '').replace('\\s+', ' ')
        cleaned = cleaned.replace('\\(', '(').replace('\\)', ')')
        cleaned = cleaned.replace('\\.', '.').replace('\\[', '[').replace('\\]', ']')

        # Handle 'new X' patterns
        new_match = re.match(r'^new\s+([A-Z]\w*)', cleaned)
        if new_match:
            return f'new {new_match.group(1)}'

        # Extract the main API identifier
        # Match patterns like: navigator.geolocation, fetch(), localStorage, etc.
        match = re.match(r'^([a-zA-Z_$][\w.]*)', cleaned)
        if match:
            api = match.group(1)
            # Add () if pattern had parenthesis
            if '(' in cleaned:
                api += '()'
            return api

        return ''
    
    def _find_unrecognized_patterns(self, js_content: str):
        """Find JS APIs/methods that don't match any known rule.

        Args:
            js_content: JavaScript code (without comments)
        """
        # Basic JS constructs that are universally supported - skip these
        basic_patterns = {
            'function', 'return', 'if', 'else', 'for', 'while', 'do',
            'switch', 'case', 'break', 'continue', 'try', 'catch', 'throw',
            'new', 'this', 'typeof', 'instanceof', 'delete', 'void', 'in',
            'true', 'false', 'null', 'undefined', 'var', 'with',
            # Common methods that are very old and universal
            'toString', 'valueOf', 'hasOwnProperty', 'isPrototypeOf',
            'push', 'pop', 'shift', 'unshift', 'slice', 'splice', 'concat',
            'join', 'reverse', 'sort', 'indexOf', 'lastIndexOf',
            'charAt', 'charCodeAt', 'substring', 'substr', 'toLowerCase', 'toUpperCase',
            'split', 'replace', 'match', 'search', 'trim',
            'Math', 'Date', 'String', 'Number', 'Boolean', 'Array', 'Object',
            'RegExp', 'Error', 'JSON', 'parseInt', 'parseFloat', 'isNaN', 'isFinite',
            'encodeURI', 'decodeURI', 'encodeURIComponent', 'decodeURIComponent',
            'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
            'alert', 'confirm', 'prompt', 'console', 'log', 'warn', 'error',
            'document', 'window', 'location', 'history', 'navigator',
            'getElementById', 'getElementsByClassName', 'getElementsByTagName',
            'createElement', 'appendChild', 'removeChild', 'setAttribute', 'getAttribute',
            'addEventListener', 'removeEventListener', 'preventDefault', 'stopPropagation',
            'innerHTML', 'textContent', 'style', 'className', 'parentNode', 'childNodes',
            'length', 'prototype', 'constructor', 'call', 'apply', 'bind',
            # Math methods (universally supported ES1-ES5)
            'floor', 'ceil', 'round', 'random', 'abs', 'max', 'min', 'pow', 'sqrt',
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'exp', 'log',
            # JSON methods (ES5, universally supported)
            'parse', 'stringify',
            # Array methods (ES5, universally supported)
            'forEach', 'map', 'filter', 'reduce', 'reduceRight', 'every', 'some',
            # Object methods (ES5, universally supported)
            'keys', 'create', 'defineProperty', 'defineProperties', 'getOwnPropertyDescriptor',
            'getOwnPropertyNames', 'getPrototypeOf', 'freeze', 'seal', 'preventExtensions',
            'isSealed', 'isFrozen', 'isExtensible',
            # DOM attribute methods (universally supported)
            'hasAttribute', 'removeAttribute', 'getAttributeNode', 'setAttributeNode',
            # DOM table methods (universally supported)
            'insertRow', 'deleteRow', 'insertCell', 'deleteCell',
            # localStorage/sessionStorage methods (covered by namevalue-storage feature)
            'getItem', 'setItem', 'removeItem', 'clear',
            # Array static methods (ES5)
            'isArray',
            # classList methods (covered by classlist feature)
            'add', 'remove', 'toggle', 'contains', 'item',
            # String trim methods (ES5)
            'trimStart', 'trimEnd', 'trimLeft', 'trimRight',
            # Common DOM traversal
            'firstChild', 'lastChild', 'nextSibling', 'previousSibling',
            'firstElementChild', 'lastElementChild', 'nextElementSibling', 'previousElementSibling',
            # Common DOM properties
            'nodeName', 'nodeType', 'nodeValue', 'ownerDocument',
            # Array static methods covered by specific features
            'from', 'of',
            # DataTransfer methods (covered by dragndrop feature)
            'setData', 'getData', 'clearData', 'setDragImage',
            # ============================================================
            # COMPREHENSIVE API METHODS LIST
            # All methods below are covered by their parent feature
            # ============================================================

            # --- Promises (promises) ---
            'resolve', 'reject', 'then', 'catch', 'finally', 'all', 'race', 'allSettled', 'any',

            # --- AbortController (abortcontroller) ---
            'abort', 'timeout', 'throwIfAborted',

            # --- Fetch API (fetch) ---
            'json', 'text', 'blob', 'arrayBuffer', 'formData', 'clone', 'ok', 'status',
            'headers', 'redirect', 'body', 'bytes',

            # --- requestIdleCallback (requestidlecallback) ---
            'timeRemaining', 'didTimeout',

            # --- requestAnimationFrame (requestanimationframe) ---
            # (no additional methods)

            # --- Web Animation (web-animation) ---
            'animate', 'getAnimations', 'cancel', 'finish', 'pause', 'play', 'reverse',
            'commitStyles', 'persist', 'updatePlaybackRate',

            # --- Trusted Types (trusted-types) ---
            'createPolicy', 'createHTML', 'createScript', 'createScriptURL', 'isHTML',
            'isScript', 'isScriptURL', 'getAttributeType', 'getPropertyType',

            # --- DOM Range (dom-range) ---
            'selectNode', 'selectNodeContents', 'setStart', 'setEnd', 'setStartBefore',
            'setStartAfter', 'setEndBefore', 'setEndAfter', 'collapse', 'cloneRange',
            'deleteContents', 'extractContents', 'cloneContents', 'insertNode', 'surroundContents',
            'compareBoundaryPoints', 'createContextualFragment', 'isPointInRange', 'comparePoint',

            # --- Custom Elements (custom-elementsv1) ---
            'whenDefined', 'define', 'upgrade',

            # --- Shadow DOM (shadowdomv1) ---
            'attachShadow', 'getInnerHTML', 'setHTMLUnsafe',

            # --- DOM Traversal (universally supported) ---
            'closest', 'matches', 'querySelectorAll', 'getRootNode',

            # --- FileReader (filereader) ---
            'readAsText', 'readAsDataURL', 'readAsArrayBuffer', 'readAsBinaryString', 'abort',

            # --- TextEncoder/TextDecoder (textencoder) ---
            'encode', 'decode', 'encodeInto',

            # --- IndexedDB (indexeddb, indexeddb2) ---
            'open', 'deleteDatabase', 'cmp', 'bound', 'only', 'lowerBound', 'upperBound',
            'createObjectStore', 'transaction', 'objectStore', 'put', 'delete', 'cursor',
            'openCursor', 'openKeyCursor', 'getKey', 'getAll', 'getAllKeys', 'count', 'advance',
            'continue', 'continuePrimaryKey', 'createIndex', 'deleteIndex', 'index',

            # --- Blob URLs (bloburls) ---
            'revokeObjectURL', 'createObjectURL',

            # --- SharedArrayBuffer/Atomics (sharedarraybuffer, wasm-threads) ---
            'wait', 'notify', 'load', 'store', 'exchange', 'compareExchange', 'add', 'sub',
            'and', 'or', 'xor', 'isLockFree', 'waitAsync',

            # --- Observers (intersectionobserver, mutationobserver, resizeobserver) ---
            'observe', 'unobserve', 'disconnect', 'takeRecords',

            # --- WebSocket (websockets) ---
            'send', 'close', 'binaryType',

            # --- Channel Messaging (channel-messaging) ---
            'start', 'postMessage',

            # --- BroadcastChannel (broadcastchannel) ---
            # uses postMessage, close (already listed)

            # --- Service Workers (serviceworkers) ---
            'waitUntil', 'respondWith', 'register', 'unregister', 'getRegistration',
            'getRegistrations', 'skipWaiting', 'claim', 'update', 'active', 'installing', 'waiting',

            # --- Push API (push-api) ---
            'getSubscription', 'subscribe', 'permissionState', 'unsubscribe',

            # --- Notifications (notifications) ---
            'requestPermission', 'show', 'close', 'vibrate',

            # --- Geolocation (geolocation) ---
            'getCurrentPosition', 'watchPosition', 'clearWatch',

            # --- Web Crypto (cryptography) ---
            'encrypt', 'decrypt', 'sign', 'verify', 'digest', 'generateKey', 'deriveKey',
            'deriveBits', 'importKey', 'exportKey', 'wrapKey', 'unwrapKey',

            # --- Web Audio (audio-api) ---
            'createOscillator', 'createGain', 'createAnalyser', 'createBiquadFilter',
            'createBuffer', 'createBufferSource', 'createMediaStreamSource', 'connect',
            'destination', 'currentTime', 'sampleRate', 'decodeAudioData', 'resume', 'suspend',

            # --- Media Recorder (mediarecorder) ---
            'ondataavailable', 'onerror', 'onstop', 'onstart', 'requestData',

            # --- MediaSource (mediasource) ---
            'addSourceBuffer', 'removeSourceBuffer', 'endOfStream', 'setLiveSeekableRange',
            'clearLiveSeekableRange', 'appendBuffer', 'appendBufferAsync', 'changeType',

            # --- Speech Recognition (speech-recognition) ---
            'onresult', 'onnomatch', 'onerror', 'onstart', 'onend', 'onsoundstart', 'onsoundend',
            'onspeechstart', 'onspeechend', 'onaudiostart', 'onaudioend',

            # --- Speech Synthesis (speech-synthesis) ---
            'speak', 'getVoices', 'onvoiceschanged', 'pending', 'speaking', 'paused',

            # --- Clipboard (async-clipboard, clipboard) ---
            'writeText', 'readText', 'write', 'read',

            # --- Gamepad (gamepad) ---
            'getGamepads', 'vibrationActuator', 'hapticActuators',

            # --- Pointer Lock (pointerlock) ---
            'requestPointerLock', 'exitPointerLock',

            # --- Fullscreen (fullscreen) ---
            'requestFullscreen', 'exitFullscreen', 'fullscreenElement', 'fullscreenEnabled',

            # --- Screen Orientation (screen-orientation) ---
            'lock', 'unlock', 'angle', 'type', 'onchange',

            # --- Wake Lock (wake-lock) ---
            'request', 'release', 'released',

            # --- Battery (battery-status) ---
            'charging', 'chargingTime', 'dischargingTime', 'level', 'onchargingchange',
            'onchargingtimechange', 'ondischargingtimechange', 'onlevelchange',

            # --- Vibration (vibration) ---
            # uses navigator.vibrate() - pattern matched separately

            # --- WebRTC (rtcpeerconnection) ---
            'createOffer', 'createAnswer', 'setLocalDescription', 'setRemoteDescription',
            'addIceCandidate', 'addTrack', 'removeTrack', 'addTransceiver', 'getTransceivers',
            'getSenders', 'getReceivers', 'createDataChannel', 'getStats', 'restartIce',
            'onicecandidate', 'ontrack', 'ondatachannel', 'oniceconnectionstatechange',
            'onnegotiationneeded', 'onsignalingstatechange', 'onicegatheringstatechange',

            # --- WebGL (webgl, webgl2) ---
            'getContext', 'getExtension', 'createShader', 'shaderSource', 'compileShader',
            'createProgram', 'attachShader', 'linkProgram', 'useProgram', 'createBuffer',
            'bindBuffer', 'bufferData', 'createTexture', 'bindTexture', 'texImage2D',
            'drawArrays', 'drawElements', 'viewport', 'clear', 'clearColor', 'enable', 'disable',
            'blendFunc', 'depthFunc', 'cullFace', 'uniform1f', 'uniform2f', 'uniform3f', 'uniform4f',
            'uniformMatrix4fv', 'getAttribLocation', 'getUniformLocation', 'vertexAttribPointer',
            'enableVertexAttribArray', 'disableVertexAttribArray',

            # --- WebGPU (webgpu) ---
            'requestAdapter', 'requestDevice', 'createCommandEncoder', 'createRenderPipeline',
            'createComputePipeline', 'createBindGroup', 'createBindGroupLayout',
            'createPipelineLayout', 'createShaderModule', 'createSampler', 'createQuerySet',
            'beginRenderPass', 'beginComputePass', 'copyBufferToBuffer', 'copyTextureToTexture',
            'submit', 'writeBuffer', 'writeTexture', 'mapAsync', 'getMappedRange', 'unmap',

            # --- WebXR (webxr) ---
            'isSessionSupported', 'requestSession', 'requestReferenceSpace', 'requestAnimationFrame',
            'getViewerPose', 'getPose', 'requestHitTestSource', 'updateRenderState',

            # --- Payment Request (payment-request) ---
            'canMakePayment', 'show', 'abort', 'complete', 'retry',

            # --- Credential Management (credential-management) ---
            'create', 'store', 'preventSilentAccess',

            # --- WebAuthn (webauthn) ---
            'isUserVerifyingPlatformAuthenticatorAvailable', 'isConditionalMediationAvailable',

            # --- Permissions (permissions-api) ---
            'query', 'request', 'revoke',

            # --- Performance (high-resolution-time, user-timing, resource-timing, nav-timing) ---
            'now', 'mark', 'measure', 'getEntries', 'getEntriesByName', 'getEntriesByType',
            'clearMarks', 'clearMeasures', 'clearResourceTimings', 'setResourceTimingBufferSize',
            'toJSON',

            # --- Beacon (beacon) ---
            'sendBeacon',

            # --- Streams (streams) ---
            'getReader', 'getWriter', 'pipeTo', 'pipeThrough', 'tee', 'enqueue', 'desiredSize',
            'ready', 'releaseLock', 'locked',

            # --- URL (url, urlsearchparams) ---
            'append', 'set', 'get', 'getAll', 'has', 'delete', 'sort', 'toString', 'forEach',
            'searchParams', 'href', 'origin', 'protocol', 'host', 'hostname', 'port', 'pathname',
            'search', 'hash', 'username', 'password',

            # --- Intl (internationalization) ---
            'format', 'formatToParts', 'resolvedOptions', 'supportedLocalesOf', 'compare',
            'select', 'selectRange',

            # --- Web Share (web-share) ---
            'canShare', 'share',

            # --- Cookie Store (cookie-store-api) ---
            'getAll', 'set', 'delete', 'onchange',

            # --- File System Access (native-filesystem-api) ---
            'getFile', 'createWritable', 'remove', 'isSameEntry', 'queryPermission',
            'requestPermission', 'getDirectory', 'entries', 'values', 'keys', 'resolve',

            # --- History (history) ---
            'pushState', 'replaceState', 'go', 'back', 'forward', 'state', 'scrollRestoration',

            # --- View Transitions (view-transitions) ---
            'startViewTransition', 'skipTransition', 'updateCallbackDone', 'ready', 'finished',

            # --- MIDI (midi) ---
            'requestMIDIAccess', 'inputs', 'outputs', 'onstatechange',

            # --- Bluetooth (web-bluetooth) ---
            'requestDevice', 'getAvailability', 'getPrimaryService', 'getPrimaryServices',
            'getCharacteristic', 'getCharacteristics', 'readValue', 'writeValue',
            'writeValueWithResponse', 'writeValueWithoutResponse', 'startNotifications',
            'stopNotifications', 'getDescriptor', 'getDescriptors',

            # --- USB (webusb) ---
            'getDevices', 'requestDevice', 'open', 'close', 'selectConfiguration',
            'claimInterface', 'releaseInterface', 'selectAlternateInterface', 'controlTransferIn',
            'controlTransferOut', 'transferIn', 'transferOut', 'isochronousTransferIn',
            'isochronousTransferOut', 'reset', 'forget',

            # --- Serial (web-serial) ---
            'getPorts', 'requestPort', 'readable', 'writable', 'getSignals', 'setSignals',

            # --- HID (webhid) ---
            'getDevices', 'requestDevice', 'open', 'close', 'sendReport', 'sendFeatureReport',
            'receiveFeatureReport', 'oninputreport',

            # --- NFC (webnfc) ---
            'write', 'scan', 'makeReadOnly',

            # --- Canvas (canvas, canvas-blending, path2d) ---
            'getContext', 'toDataURL', 'toBlob', 'transferControlToOffscreen', 'captureStream',
            'fillRect', 'strokeRect', 'clearRect', 'fillText', 'strokeText', 'measureText',
            'beginPath', 'closePath', 'moveTo', 'lineTo', 'bezierCurveTo', 'quadraticCurveTo',
            'arc', 'arcTo', 'ellipse', 'rect', 'fill', 'stroke', 'clip', 'isPointInPath',
            'isPointInStroke', 'createLinearGradient', 'createRadialGradient', 'createPattern',
            'drawImage', 'createImageData', 'getImageData', 'putImageData', 'save', 'restore',
            'scale', 'rotate', 'translate', 'transform', 'setTransform', 'resetTransform',
            'globalCompositeOperation', 'globalAlpha', 'shadowColor', 'shadowBlur',
            'shadowOffsetX', 'shadowOffsetY', 'lineCap', 'lineJoin', 'lineWidth', 'miterLimit',
            'setLineDash', 'getLineDash', 'lineDashOffset', 'font', 'textAlign', 'textBaseline',
            'direction', 'imageSmoothingEnabled', 'imageSmoothingQuality', 'addPath', 'roundRect',

            # --- OffscreenCanvas (offscreencanvas) ---
            'convertToBlob', 'transferToImageBitmap',

            # --- createImageBitmap (createimagebitmap) ---
            # (global function, handled separately)

            # --- EventSource (eventsource) ---
            'onopen', 'onmessage', 'onerror', 'readyState', 'url', 'withCredentials',

            # --- Web Transport (webtransport) ---
            'createBidirectionalStream', 'createUnidirectionalStream', 'datagrams',
            'incomingBidirectionalStreams', 'incomingUnidirectionalStreams',

            # --- Resize Observer Entry properties ---
            'contentRect', 'borderBoxSize', 'contentBoxSize', 'devicePixelContentBoxSize', 'target',

            # --- Intersection Observer Entry properties ---
            'boundingClientRect', 'intersectionRatio', 'intersectionRect', 'isIntersecting',
            'rootBounds', 'time',

            # --- Generic event handlers (covered by addeventlistener) ---
            'on', 'off', 'once', 'emit', 'trigger', 'fire',

            # --- Common utility methods used everywhere ---
            'set', 'get', 'has', 'entries', 'values', 'keys', 'size', 'clear', 'delete',
            'forEach', 'next', 'done', 'value', 'return', 'throw',

            # --- ImageCapture (imagecapture) ---
            'takePhoto', 'grabFrame', 'getPhotoCapabilities', 'getPhotoSettings',

            # --- MediaStream/MediaRecorder (mediarecorder, getusermedia) ---
            'stop', 'getTracks', 'getVideoTracks', 'getAudioTracks', 'addTrack', 'removeTrack',
            'getTrackById', 'clone', 'active', 'muted', 'enabled', 'readyState',

            # --- Temporal (temporal) ---
            'instant', 'plainDateTimeISO', 'plainDate', 'plainTime', 'plainYearMonth',
            'plainMonthDay', 'zonedDateTimeISO', 'now', 'from', 'compare', 'duration',
            'toInstant', 'toZonedDateTime', 'toPlainDate', 'toPlainTime', 'toPlainDateTime',
            'with', 'add', 'subtract', 'until', 'since', 'round', 'equals', 'toString',

            # --- Feature Policy / Permissions Policy ---
            'allowsFeature', 'features', 'allowedFeatures', 'getAllowlistForFeature',

            # --- URL (url) ---
            'canParse', 'parse',

            # --- Number methods (es6-number) ---
            'isInteger', 'isFinite', 'isNaN', 'isSafeInteger', 'parseFloat', 'parseInt',
            'toExponential', 'toFixed', 'toPrecision',

            # --- DOMParser / XMLSerializer (xml-serializer) ---
            'parseFromString', 'serializeToString',

            # --- DOMMatrix (dommatrix) ---
            'rotateSelf', 'translateSelf', 'scaleSelf', 'skewXSelf', 'skewYSelf',
            'invertSelf', 'multiplySelf', 'preMultiplySelf', 'setMatrixValue',
            'rotate', 'translate', 'scale', 'skewX', 'skewY', 'multiply', 'inverse',
            'flipX', 'flipY', 'transformPoint', 'toFloat32Array', 'toFloat64Array',

            # --- Worklet (css-paint-api, audio-api worklet) ---
            'addModule',

            # --- WebAssembly (wasm) ---
            'compile', 'compileStreaming', 'instantiate', 'instantiateStreaming', 'validate',

            # --- General media controls ---
            'load', 'play', 'pause', 'fastSeek', 'setMediaKeys', 'setSinkId', 'captureStream',

            # --- Selection API (selection-api) ---
            'getSelection', 'anchorNode', 'focusNode', 'rangeCount', 'getRangeAt',
            'addRange', 'removeRange', 'removeAllRanges', 'selectAllChildren', 'collapseToStart',
            'collapseToEnd', 'extend', 'containsNode', 'deleteFromDocument',

            # --- Resize / Scroll ---
            'scrollTo', 'scrollBy', 'scrollIntoView', 'scrollIntoViewIfNeeded',
            'getBoundingClientRect', 'getClientRects',

            # --- Focus management ---
            'focus', 'blur', 'hasFocus',

            # --- Form methods ---
            'submit', 'reset', 'checkValidity', 'reportValidity', 'setCustomValidity',
            'select', 'setSelectionRange', 'setRangeText', 'stepUp', 'stepDown',

            # --- Element methods ---
            'getAttribute', 'setAttribute', 'removeAttribute', 'hasAttribute',
            'getAttributeNS', 'setAttributeNS', 'removeAttributeNS', 'hasAttributeNS',
            'toggleAttribute', 'getAttributeNames', 'insertAdjacentElement',
            'insertAdjacentHTML', 'insertAdjacentText', 'before', 'after', 'replaceWith',
            'append', 'prepend', 'replaceChildren',

            # --- Node manipulation ---
            'cloneNode', 'appendChild', 'insertBefore', 'removeChild', 'replaceChild',
            'normalize', 'isEqualNode', 'isSameNode', 'compareDocumentPosition',
            'contains', 'lookupPrefix', 'lookupNamespaceURI', 'isDefaultNamespace',

            # --- Console methods (universally supported) ---
            'log', 'warn', 'error', 'info', 'debug', 'trace', 'dir', 'dirxml', 'table',
            'time', 'timeEnd', 'timeLog', 'count', 'countReset', 'group', 'groupCollapsed',
            'groupEnd', 'clear', 'assert', 'profile', 'profileEnd', 'timeStamp',
        }

        # Common programming method prefixes/patterns - skip these
        common_prefixes = {
            'get', 'set', 'add', 'remove', 'update', 'delete', 'create', 'build', 'make',
            'find', 'fetch', 'load', 'save', 'read', 'write', 'send', 'receive', 'emit',
            'on', 'off', 'handle', 'process', 'parse', 'format', 'convert', 'transform',
            'init', 'initialize', 'setup', 'config', 'configure', 'register', 'unregister',
            'start', 'stop', 'begin', 'end', 'open', 'close', 'show', 'hide', 'toggle',
            'enable', 'disable', 'lock', 'unlock', 'check', 'validate', 'verify', 'test',
            'is', 'has', 'can', 'should', 'will', 'do', 'run', 'execute', 'call', 'invoke',
            'render', 'draw', 'paint', 'display', 'print', 'log', 'debug', 'trace',
            'to', 'from', 'as', 'into', 'with', 'for', 'by', 'at', 'of',
            'sort', 'filter', 'map', 'reduce', 'find', 'some', 'every', 'includes',
            'push', 'pop', 'shift', 'unshift', 'splice', 'slice', 'concat', 'join',
            'split', 'replace', 'match', 'search', 'trim', 'pad', 'fill', 'copy',
            'reset', 'clear', 'flush', 'refresh', 'reload', 'retry', 'repeat',
            'attach', 'detach', 'bind', 'unbind', 'connect', 'disconnect', 'link', 'unlink',
            'mount', 'unmount', 'inject', 'extract', 'insert', 'append', 'prepend',
            'wrap', 'unwrap', 'encode', 'decode', 'encrypt', 'decrypt', 'hash', 'sign',
            'listen', 'watch', 'observe', 'subscribe', 'unsubscribe', 'notify', 'dispatch',
            'wait', 'sleep', 'delay', 'timeout', 'interval', 'schedule', 'cancel', 'abort',
            'click', 'focus', 'blur', 'select', 'change', 'input', 'submit', 'keydown', 'keyup',
            'mouse', 'touch', 'scroll', 'resize', 'drag', 'drop', 'move', 'enter', 'leave',
            # Additional common patterns
            'apply', 'navigate', 'route', 'redirect', 'goto', 'visit', 'browse',
            'theme', 'style', 'color', 'class', 'attr', 'prop', 'data', 'state', 'store',
            'component', 'element', 'node', 'item', 'list', 'array', 'object', 'value',
            'action', 'event', 'callback', 'handler', 'listener', 'hook', 'effect',
            'use', 'provide', 'consume', 'context', 'ref', 'memo', 'lazy', 'suspend',
        }

        # Common capitalized names (React components, UI states, etc.) - not browser APIs
        common_globals = {
            'Loading', 'Error', 'Success', 'Warning', 'Info', 'Pending', 'Complete',
            'Component', 'Container', 'Wrapper', 'Layout', 'Page', 'View', 'Screen',
            'App', 'Root', 'Main', 'Header', 'Footer', 'Sidebar', 'Nav', 'Menu',
            'Button', 'Input', 'Form', 'Modal', 'Dialog', 'Popup', 'Tooltip', 'Card',
            'List', 'Item', 'Row', 'Col', 'Grid', 'Table', 'Cell', 'Panel', 'Box',
            'Text', 'Label', 'Title', 'Icon', 'Image', 'Avatar', 'Badge', 'Tag',
            'Link', 'Tab', 'Tabs', 'Accordion', 'Dropdown', 'Select', 'Checkbox',
            'Radio', 'Switch', 'Slider', 'Progress', 'Spinner', 'Loader', 'Skeleton',
            'Provider', 'Consumer', 'Context', 'Store', 'State', 'Action', 'Reducer',
            'Router', 'Route', 'Routes', 'Navigate', 'Redirect', 'Outlet', 'Link',
            'Fragment', 'Suspense', 'Lazy', 'Memo', 'Ref', 'Effect', 'Callback',
            'Props', 'Children', 'Parent', 'Child', 'Sibling', 'Ancestor', 'Descendant',
            'User', 'Admin', 'Guest', 'Auth', 'Login', 'Logout', 'Register', 'Profile',
            'Home', 'About', 'Contact', 'Dashboard', 'Settings', 'Search', 'Results',
            'Theme', 'Style', 'Config', 'Options', 'Params', 'Query', 'Data', 'Model',
        }

        # Find potential API calls and method usage
        # Pattern for method calls: .methodName( or Object.method(
        method_pattern = r'\.([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('
        found_methods = set(re.findall(method_pattern, js_content))

        # Pattern for global objects/APIs: CapitalizedName.
        global_api_pattern = r'\b([A-Z][a-zA-Z0-9_$]*)\.'
        found_globals = set(re.findall(global_api_pattern, js_content))

        # Convert basic_patterns to lowercase for comparison
        basic_patterns_lower = {b.lower() for b in basic_patterns}

        # Check methods
        for method in found_methods:
            method_lower = method.lower()

            # Skip if in basic patterns
            if method_lower in basic_patterns_lower:
                continue

            # Skip if this method was already matched to a feature
            if method in self._matched_apis:
                continue

            # Skip very short names (< 4 chars)
            if len(method) < 4:
                continue

            # Skip methods that start with common programming prefixes
            skip = False
            for prefix in common_prefixes:
                if method_lower.startswith(prefix) or method_lower.endswith(prefix):
                    skip = True
                    break
            if skip:
                continue

            # Skip camelCase methods that look like custom code (e.g., myCustomMethod)
            # Only flag methods that look like browser APIs
            if method[0].islower() and not any(c.isupper() for c in method[1:3] if len(method) > 2):
                # Likely a custom method like "customThing" - skip unless it matches a pattern
                pass

            # Check if matches any feature pattern
            matched = False
            for feature_info in self._all_features.values():
                patterns = feature_info.get('patterns', [])
                for pattern in patterns:
                    try:
                        if re.search(pattern, f".{method}(", re.IGNORECASE):
                            matched = True
                            break
                    except re.error:
                        continue
                if matched:
                    break

            if not matched:
                self.unrecognized_patterns.add(f"method: .{method}()")

        # Check global APIs
        for global_api in found_globals:
            if global_api in basic_patterns:
                continue

            # Skip if this API was already matched to a feature
            if global_api in self._matched_apis:
                continue

            # Skip common capitalized names (React components, UI states, etc.)
            if global_api in common_globals:
                continue

            # Check if matches any feature pattern
            matched = False
            for feature_info in self._all_features.values():
                patterns = feature_info.get('patterns', [])
                for pattern in patterns:
                    try:
                        if re.search(pattern, global_api, re.IGNORECASE):
                            matched = True
                            break
                    except re.error:
                        continue
                if matched:
                    break

            if not matched:
                self.unrecognized_patterns.add(f"API: {global_api}")

    def get_detailed_report(self) -> Dict:
        """Get detailed report of found features.

        Returns:
            Dict with detailed information about found features
        """
        return {
            'total_features': len(self.features_found),
            'features': sorted(list(self.features_found)),
            'feature_details': self.feature_details,
            'unrecognized': sorted(list(self.unrecognized_patterns))
        }
    
    def parse_multiple_files(self, filepaths: List[str]) -> Set[str]:
        """Parse multiple JavaScript files and combine results.
        
        Args:
            filepaths: List of JavaScript file paths
            
        Returns:
            Combined set of all features found
        """
        all_features = set()
        
        for filepath in filepaths:
            try:
                features = self.parse_file(filepath)
                all_features.update(features)
            except Exception as e:
                logger.warning(f"Could not parse {filepath}: {e}")
        
        return all_features
    
    def get_statistics(self) -> Dict:
        """Get parsing statistics.
        
        Returns:
            Dict with parsing statistics
        """
        # Group features by category
        syntax_features = []
        api_features = []
        array_methods = []
        string_methods = []
        object_methods = []
        storage_apis = []
        dom_apis = []
        
        for feature in self.features_found:
            if feature in ['arrow-functions', 'async-functions', 'const', 'let',
                          'template-literals', 'destructuring', 'spread',
                          'rest-parameters', 'es6-class']:
                syntax_features.append(feature)
            elif feature.startswith('array-'):
                array_methods.append(feature)
            elif feature.startswith('string-'):
                string_methods.append(feature)
            elif feature.startswith('object-'):
                object_methods.append(feature)
            elif feature in ['namevalue-storage', 'indexeddb']:
                storage_apis.append(feature)
            elif feature in ['queryselector', 'classlist', 'dataset', 'custom-elements']:
                dom_apis.append(feature)
            else:
                api_features.append(feature)
        
        return {
            'total_features': len(self.features_found),
            'syntax_features': len(syntax_features),
            'api_features': len(api_features),
            'array_methods': len(array_methods),
            'string_methods': len(string_methods),
            'object_methods': len(object_methods),
            'storage_apis': len(storage_apis),
            'dom_apis': len(dom_apis),
            'features_list': sorted(list(self.features_found)),
            'categories': {
                'syntax': syntax_features,
                'apis': api_features,
                'array_methods': array_methods,
                'string_methods': string_methods,
                'object_methods': object_methods,
                'storage': storage_apis,
                'dom': dom_apis
            }
        }
    
    def validate_javascript(self, js_content: str) -> bool:
        """Basic validation if content looks like JavaScript.
        
        Args:
            js_content: JavaScript content to validate
            
        Returns:
            True if looks like valid JavaScript, False otherwise
        """
        # Very basic check - look for common JS patterns
        js_patterns = [
            r'\bfunction\b',
            r'\bconst\b',
            r'\blet\b',
            r'\bvar\b',
            r'=>',
            r'\bclass\b',
            r'\{',
            r'\}',
        ]
        
        for pattern in js_patterns:
            if re.search(pattern, js_content):
                return True
        
        return False


def parse_js_file(filepath: str) -> Set[str]:
    """Convenience function to parse a single JavaScript file.
    
    Args:
        filepath: Path to JavaScript file
        
    Returns:
        Set of feature IDs found
    """
    parser = JavaScriptParser()
    return parser.parse_file(filepath)


def parse_js_string(js_content: str) -> Set[str]:
    """Convenience function to parse JavaScript string.
    
    Args:
        js_content: JavaScript content as string
        
    Returns:
        Set of feature IDs found
    """
    parser = JavaScriptParser()
    return parser.parse_string(js_content)
