"""JS parser -- extracts browser features using tree-sitter AST with regex fallback."""

from typing import Set, List, Dict, Optional
from pathlib import Path
import re

from .js_feature_maps import (
    ALL_JS_FEATURES,
    AST_SYNTAX_NODE_MAP,
    AST_NEW_EXPRESSION_MAP,
    AST_CALL_EXPRESSION_MAP,
    AST_MEMBER_EXPRESSION_MAP,
    AST_IDENTIFIER_MAP,
    AST_OPERATOR_MAP,
)
from .custom_rules_loader import get_custom_js_rules
from ..utils.config import get_logger

logger = get_logger('parsers.js')

# tree-sitter is optional -- falls back to regex-only if unavailable
_TREE_SITTER_AVAILABLE = False
_JS_LANGUAGE = None
_JS_PARSER = None
try:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        from tree_sitter_languages import get_language, get_parser as _get_ts_parser
        _JS_LANGUAGE = get_language('javascript')
        _JS_PARSER = _get_ts_parser('javascript')
    _TREE_SITTER_AVAILABLE = True
except (ImportError, Exception):
    pass


class JavaScriptParser:
    """Extracts Can I Use feature IDs from JavaScript files."""

    def __init__(self):
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()
        self._matched_apis = set()
        self._all_features = {**ALL_JS_FEATURES, **get_custom_js_rules()}

    def parse_file(self, filepath: str) -> Set[str]:
        """Parse a JS file and return detected feature IDs."""
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
        """Parse JS string. Uses tree-sitter AST when available, regex otherwise."""
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()
        self._matched_apis = set()

        # Must run before string removal -- these ARE string literals
        self._detect_directives(js_content)

        # Event names live inside string args, so detect before stripping
        self._detect_event_listeners(js_content)

        tree = self._parse_with_tree_sitter(js_content)

        if tree is not None:
            source_bytes = js_content.encode('utf-8')
            root_node = tree.root_node

            # Tier 1: syntax features from node types (zero false positives)
            self._detect_ast_syntax_features(root_node, source_bytes)

            # Tier 2: API features from identifiers, calls, member expressions
            self._detect_ast_api_features(root_node, source_bytes)

            # Build text with comments/strings stripped via AST
            matchable = self._build_matchable_text_from_ast(root_node, source_bytes)

            # Tier 3: regex patterns on cleaned text
            self._detect_features(matchable)
            self._find_unrecognized_patterns(matchable)
        else:
            # Fallback: regex-only pipeline
            cleaned_content = self._remove_comments(js_content)
            self._detect_features(cleaned_content)
            self._find_unrecognized_patterns(cleaned_content)

        return self.features_found

    def _detect_directives(self, js_content: str):
        """Detect "use strict" and "use asm" before string removal."""
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

        Event names like 'unhandledrejection' are inside string args and
        would be lost after stripping string content.
        """
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
            'focusin': ('focusin-focusout-events', 'focusin event'),
            'focusout': ('focusin-focusout-events', 'focusout event'),
            'pageshow': ('page-transition-events', 'pageshow event'),
            'pagehide': ('page-transition-events', 'pagehide event'),
            'beforeprint': ('beforeafterprint', 'beforeprint event'),
            'afterprint': ('beforeafterprint', 'afterprint event'),
            'auxclick': ('auxclick', 'auxclick event'),
        }

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
        """Strip comments and string content to prevent false positives.

        Keeps quote delimiters and template literal structure (backticks + ${x})
        so template-literal detection still works.
        """
        result = []
        i = 0
        length = len(js_content)

        while i < length:
            if i < length - 1 and js_content[i:i+2] == '//':
                while i < length and js_content[i] != '\n':
                    i += 1
                continue

            if i < length - 1 and js_content[i:i+2] == '/*':
                i += 2
                while i < length - 1 and js_content[i:i+2] != '*/':
                    i += 1
                i += 2
                continue

            if js_content[i] == '"':
                result.append('"')
                i += 1
                while i < length:
                    if js_content[i] == '\\' and i + 1 < length:
                        i += 2
                    elif js_content[i] == '"':
                        result.append('"')
                        i += 1
                        break
                    else:
                        i += 1
                continue

            if js_content[i] == "'":
                result.append("'")
                i += 1
                while i < length:
                    if js_content[i] == '\\' and i + 1 < length:
                        i += 2
                    elif js_content[i] == "'":
                        result.append("'")
                        i += 1
                        break
                    else:
                        i += 1
                continue

            if js_content[i] == '`':
                result.append('`')
                i += 1
                while i < length:
                    if js_content[i] == '\\' and i + 1 < length:
                        i += 2
                    elif js_content[i] == '`':
                        result.append('`')
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

            result.append(js_content[i])
            i += 1

        return ''.join(result)

    def _remove_comments(self, js_content: str) -> str:
        return self._remove_comments_and_strings(js_content)

    # --- Tree-sitter AST methods ---

    def _parse_with_tree_sitter(self, js_content: str):
        """Try to parse with tree-sitter. Returns tree or None."""
        if not _TREE_SITTER_AVAILABLE or _JS_PARSER is None:
            return None
        try:
            tree = _JS_PARSER.parse(js_content.encode('utf-8'))
            return tree
        except Exception as e:
            logger.debug(f"tree-sitter parse failed: {e}")
            return None

    def _add_ast_feature(self, feature_id: str, api_name: str, description: str):
        """Record a feature found via AST, merging into existing details."""
        self.features_found.add(feature_id)
        for detail in self.feature_details:
            if detail['feature'] == feature_id:
                if api_name not in detail['matched_apis']:
                    detail['matched_apis'].append(api_name)
                return
        self.feature_details.append({
            'feature': feature_id,
            'description': description,
            'matched_apis': [api_name],
        })

    def _detect_ast_syntax_features(self, root_node, source_bytes: bytes):
        """Tier 1: detect features by AST node type (zero false positives)."""
        stack = [root_node]
        while stack:
            node = stack.pop()
            node_type = node.type

            if node_type in AST_SYNTAX_NODE_MAP:
                feature_id = AST_SYNTAX_NODE_MAP[node_type]
                self._add_ast_feature(feature_id, node_type, feature_id)

            # const/let via lexical_declaration
            if node_type == 'lexical_declaration':
                if node.child_count > 0:
                    keyword = node.children[0].type
                    if keyword == 'const':
                        self._add_ast_feature('const', 'const', 'Const declaration')
                    elif keyword == 'let':
                        self._add_ast_feature('let', 'let', 'Let declaration')
                    # Destructuring in variable declarators
                    for child in node.children:
                        if child.type == 'variable_declarator':
                            name_node = child.child_by_field_name('name')
                            if name_node and name_node.type in ('object_pattern', 'array_pattern'):
                                self._add_ast_feature('es6', 'destructuring', 'ES6 destructuring')

            # async functions -- check if node text starts with 'async'
            if node_type in ('function_declaration', 'function',
                             'arrow_function', 'method_definition'):
                text_start = source_bytes[node.start_byte:min(node.start_byte + 20, len(source_bytes))].decode('utf-8', errors='replace')
                if text_start.startswith('async'):
                    self._add_ast_feature('async-functions', 'async', 'Async/await')

            # Optional chaining (?.) via optional_chain child
            if node_type == 'member_expression' or node_type == 'call_expression':
                for child in node.children:
                    if child.type == 'optional_chain':
                        self._add_ast_feature(
                            AST_OPERATOR_MAP.get('?.', 'mdn-javascript_operators_optional_chaining'),
                            '?.', 'Optional chaining'
                        )
                        break

            # Private fields (#x)
            if node_type == 'private_property_identifier':
                self._add_ast_feature(
                    'mdn-javascript_classes_private_class_fields',
                    '#private', 'Private class fields'
                )

            # Nullish coalescing (??) via binary_expression operator
            if node_type == 'binary_expression':
                operator_node = node.child_by_field_name('operator')
                if operator_node:
                    op_text = source_bytes[operator_node.start_byte:operator_node.end_byte].decode('utf-8', errors='replace')
                    if op_text == '??':
                        self._add_ast_feature(
                            AST_OPERATOR_MAP.get('??', 'mdn-javascript_operators_nullish_coalescing'),
                            '??', 'Nullish coalescing'
                        )

            for child in node.children:
                stack.append(child)

    def _detect_ast_api_features(self, root_node, source_bytes: bytes):
        """Tier 2: detect API features from constructors, calls, members, identifiers."""
        stack = [root_node]
        while stack:
            node = stack.pop()
            node_type = node.type

            # new Expression: new Promise(...), new Worker(...), etc.
            if node_type == 'new_expression':
                constructor = node.child_by_field_name('constructor')
                if constructor:
                    name = source_bytes[constructor.start_byte:constructor.end_byte].decode('utf-8', errors='replace')
                    if name in AST_NEW_EXPRESSION_MAP:
                        feature_id = AST_NEW_EXPRESSION_MAP[name]
                        self._add_ast_feature(feature_id, f'new {name}', feature_id)

            # Call expressions: fetch(), requestAnimationFrame(), obj.method()
            elif node_type == 'call_expression':
                func_node = node.child_by_field_name('function')
                if func_node:
                    func_text = source_bytes[func_node.start_byte:func_node.end_byte].decode('utf-8', errors='replace')

                    if func_text in AST_CALL_EXPRESSION_MAP:
                        feature_id = AST_CALL_EXPRESSION_MAP[func_text]
                        self._add_ast_feature(feature_id, f'{func_text}()', feature_id)

                    if func_node.type == 'member_expression':
                        obj_node = func_node.child_by_field_name('object')
                        prop_node = func_node.child_by_field_name('property')
                        if obj_node and prop_node:
                            obj_text = source_bytes[obj_node.start_byte:obj_node.end_byte].decode('utf-8', errors='replace')
                            prop_text = source_bytes[prop_node.start_byte:prop_node.end_byte].decode('utf-8', errors='replace')
                            member_key = f'{obj_text}.{prop_text}'
                            if member_key in AST_MEMBER_EXPRESSION_MAP:
                                feature_id = AST_MEMBER_EXPRESSION_MAP[member_key]
                                self._add_ast_feature(feature_id, member_key, feature_id)

            # Member expressions (non-call): navigator.geolocation, document.hidden
            elif node_type == 'member_expression':
                # Skip if already handled as call_expression function
                parent = node.parent
                if parent and parent.type == 'call_expression' and parent.child_by_field_name('function') == node:
                    pass
                else:
                    obj_node = node.child_by_field_name('object')
                    prop_node = node.child_by_field_name('property')
                    if obj_node and prop_node:
                        obj_text = source_bytes[obj_node.start_byte:obj_node.end_byte].decode('utf-8', errors='replace')
                        prop_text = source_bytes[prop_node.start_byte:prop_node.end_byte].decode('utf-8', errors='replace')
                        member_key = f'{obj_text}.{prop_text}'
                        if member_key in AST_MEMBER_EXPRESSION_MAP:
                            feature_id = AST_MEMBER_EXPRESSION_MAP[member_key]
                            self._add_ast_feature(feature_id, member_key, feature_id)

            # Standalone identifiers: SharedArrayBuffer, ReadableStream, etc.
            elif node_type == 'identifier':
                name = source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
                if name in AST_IDENTIFIER_MAP:
                    feature_id = AST_IDENTIFIER_MAP[name]
                    self._add_ast_feature(feature_id, name, feature_id)

            for child in node.children:
                stack.append(child)

    def _build_matchable_text_from_ast(self, root_node, source_bytes: bytes) -> str:
        """Build regex-matchable text from AST with comments/strings stripped.

        Comments become spaces (preserving line structure).
        Strings keep delimiters, content removed.
        Template literals keep backticks and ${x} markers.
        """
        source_text = source_bytes.decode('utf-8', errors='replace')
        length = len(source_text)

        replacements = []

        stack = [root_node]
        while stack:
            node = stack.pop()
            node_type = node.type

            if node_type == 'comment':
                start, end = node.start_byte, node.end_byte
                comment_text = source_text[start:end]
                replacement = ''.join('\n' if c == '\n' else ' ' for c in comment_text)
                replacements.append((start, end, replacement))
                continue

            if node_type == 'string':
                start, end = node.start_byte, node.end_byte
                text = source_text[start:end]
                if len(text) >= 2:
                    quote = text[0]
                    replacement = quote + quote
                else:
                    replacement = text
                replacements.append((start, end, replacement))
                continue

            if node_type == 'template_string':
                self._process_template_string(node, source_text, replacements)
                continue

            for child in node.children:
                stack.append(child)

        if not replacements:
            return source_text

        replacements.sort(key=lambda x: x[0])

        parts = []
        last_end = 0
        for start, end, replacement in replacements:
            if start < last_end:
                continue  # Skip overlapping
            parts.append(source_text[last_end:start])
            parts.append(replacement)
            last_end = end
        parts.append(source_text[last_end:])

        return ''.join(parts)

    def _process_template_string(self, node, source_text: str, replacements: list):
        """Keep backtick delimiters and ${x} markers, strip literal text."""
        start = node.start_byte
        end = node.end_byte
        text = source_text[start:end]

        result = []
        i = 0
        length = len(text)

        if length == 0:
            return

        result.append('`')
        i = 1

        while i < length:
            if text[i] == '`':
                result.append('`')
                i += 1
                break
            elif text[i] == '\\' and i + 1 < length:
                i += 2
            elif text[i:i+2] == '${':
                result.append('${x}')
                i += 2
                depth = 1
                while i < length and depth > 0:
                    if text[i] == '{':
                        depth += 1
                    elif text[i] == '}':
                        depth -= 1
                    i += 1
            else:
                i += 1

        replacements.append((start, end, ''.join(result)))

    def _detect_features(self, js_content: str):
        """Match regex patterns from feature maps against cleaned text."""
        for feature_id, feature_info in self._all_features.items():
            patterns = feature_info.get('patterns', [])
            matched_apis = []
            feature_found = False

            for pattern in patterns:
                try:
                    if re.search(pattern, js_content):
                        feature_found = True
                        api_name = self._extract_api_name(pattern)
                        if api_name and api_name not in matched_apis:
                            matched_apis.append(api_name)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern for {feature_id}: {e}")
                    continue

            if feature_found:
                self.features_found.add(feature_id)
                if not any(d['feature'] == feature_id for d in self.feature_details):
                    self.feature_details.append({
                        'feature': feature_id,
                        'description': feature_info.get('description', ''),
                        'matched_apis': matched_apis,
                    })
                # Track matched API names for unrecognized pattern filtering
                for api in matched_apis:
                    api_clean = api.replace('()', '').replace('new ', '')
                    parts = api_clean.split('.')
                    for part in parts:
                        if part:
                            self._matched_apis.add(part)

    def _extract_api_name(self, pattern: str) -> str:
        """Try to extract a human-readable API name from a regex pattern."""
        cleaned = pattern.replace('\\b', '').replace('\\s*', '').replace('\\s+', ' ')
        cleaned = cleaned.replace('\\(', '(').replace('\\)', ')')
        cleaned = cleaned.replace('\\.', '.').replace('\\[', '[').replace('\\]', ']')

        new_match = re.match(r'^new\s+([A-Z]\w*)', cleaned)
        if new_match:
            return f'new {new_match.group(1)}'

        match = re.match(r'^([a-zA-Z_$][\w.]*)', cleaned)
        if match:
            api = match.group(1)
            if '(' in cleaned:
                api += '()'
            return api

        return ''

    def _find_unrecognized_patterns(self, js_content: str):
        """Find JS APIs/methods not matched by any feature rule."""
        # Universally supported -- no need to flag
        basic_patterns = {
            'function', 'return', 'if', 'else', 'for', 'while', 'do',
            'switch', 'case', 'break', 'continue', 'try', 'catch', 'throw',
            'new', 'this', 'typeof', 'instanceof', 'delete', 'void', 'in',
            'true', 'false', 'null', 'undefined', 'var', 'with',
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
            'floor', 'ceil', 'round', 'random', 'abs', 'max', 'min', 'pow', 'sqrt',
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'exp', 'log',
            'parse', 'stringify',
            'forEach', 'map', 'filter', 'reduce', 'reduceRight', 'every', 'some',
            'keys', 'create', 'defineProperty', 'defineProperties', 'getOwnPropertyDescriptor',
            'getOwnPropertyNames', 'getPrototypeOf', 'freeze', 'seal', 'preventExtensions',
            'isSealed', 'isFrozen', 'isExtensible',
            'hasAttribute', 'removeAttribute', 'getAttributeNode', 'setAttributeNode',
            'insertRow', 'deleteRow', 'insertCell', 'deleteCell',
            'getItem', 'setItem', 'removeItem', 'clear',
            'isArray',
            'add', 'remove', 'toggle', 'contains', 'item',
            'trimStart', 'trimEnd', 'trimLeft', 'trimRight',
            'firstChild', 'lastChild', 'nextSibling', 'previousSibling',
            'firstElementChild', 'lastElementChild', 'nextElementSibling', 'previousElementSibling',
            'nodeName', 'nodeType', 'nodeValue', 'ownerDocument',
            'from', 'of',
            'setData', 'getData', 'clearData', 'setDragImage',

            # Methods covered by their parent features (e.g. .then -> promises)
            'resolve', 'reject', 'then', 'catch', 'finally', 'all', 'race', 'allSettled', 'any',
            'abort', 'timeout', 'throwIfAborted',
            'json', 'text', 'blob', 'arrayBuffer', 'formData', 'clone', 'ok', 'status',
            'headers', 'redirect', 'body', 'bytes',
            'timeRemaining', 'didTimeout',
            'animate', 'getAnimations', 'cancel', 'finish', 'pause', 'play', 'reverse',
            'commitStyles', 'persist', 'updatePlaybackRate',
            'createPolicy', 'createHTML', 'createScript', 'createScriptURL', 'isHTML',
            'isScript', 'isScriptURL', 'getAttributeType', 'getPropertyType',
            'selectNode', 'selectNodeContents', 'setStart', 'setEnd', 'setStartBefore',
            'setStartAfter', 'setEndBefore', 'setEndAfter', 'collapse', 'cloneRange',
            'deleteContents', 'extractContents', 'cloneContents', 'insertNode', 'surroundContents',
            'compareBoundaryPoints', 'createContextualFragment', 'isPointInRange', 'comparePoint',
            'whenDefined', 'define', 'upgrade',
            'attachShadow', 'getInnerHTML', 'setHTMLUnsafe',
            'closest', 'matches', 'querySelectorAll', 'getRootNode',
            'readAsText', 'readAsDataURL', 'readAsArrayBuffer', 'readAsBinaryString', 'abort',
            'encode', 'decode', 'encodeInto',
            'open', 'deleteDatabase', 'cmp', 'bound', 'only', 'lowerBound', 'upperBound',
            'createObjectStore', 'transaction', 'objectStore', 'put', 'delete', 'cursor',
            'openCursor', 'openKeyCursor', 'getKey', 'getAll', 'getAllKeys', 'count', 'advance',
            'continue', 'continuePrimaryKey', 'createIndex', 'deleteIndex', 'index',
            'revokeObjectURL', 'createObjectURL',
            'wait', 'notify', 'load', 'store', 'exchange', 'compareExchange', 'add', 'sub',
            'and', 'or', 'xor', 'isLockFree', 'waitAsync',
            'observe', 'unobserve', 'disconnect', 'takeRecords',
            'send', 'close', 'binaryType',
            'start', 'postMessage',
            'waitUntil', 'respondWith', 'register', 'unregister', 'getRegistration',
            'getRegistrations', 'skipWaiting', 'claim', 'update', 'active', 'installing', 'waiting',
            'getSubscription', 'subscribe', 'permissionState', 'unsubscribe',
            'requestPermission', 'show', 'close', 'vibrate',
            'getCurrentPosition', 'watchPosition', 'clearWatch',
            'encrypt', 'decrypt', 'sign', 'verify', 'digest', 'generateKey', 'deriveKey',
            'deriveBits', 'importKey', 'exportKey', 'wrapKey', 'unwrapKey',
            'createOscillator', 'createGain', 'createAnalyser', 'createBiquadFilter',
            'createBuffer', 'createBufferSource', 'createMediaStreamSource', 'connect',
            'destination', 'currentTime', 'sampleRate', 'decodeAudioData', 'resume', 'suspend',
            'ondataavailable', 'onerror', 'onstop', 'onstart', 'requestData',
            'addSourceBuffer', 'removeSourceBuffer', 'endOfStream', 'setLiveSeekableRange',
            'clearLiveSeekableRange', 'appendBuffer', 'appendBufferAsync', 'changeType',
            'onresult', 'onnomatch', 'onerror', 'onstart', 'onend', 'onsoundstart', 'onsoundend',
            'onspeechstart', 'onspeechend', 'onaudiostart', 'onaudioend',
            'speak', 'getVoices', 'onvoiceschanged', 'pending', 'speaking', 'paused',
            'writeText', 'readText', 'write', 'read',
            'getGamepads', 'vibrationActuator', 'hapticActuators',
            'requestPointerLock', 'exitPointerLock',
            'requestFullscreen', 'exitFullscreen', 'fullscreenElement', 'fullscreenEnabled',
            'lock', 'unlock', 'angle', 'type', 'onchange',
            'request', 'release', 'released',
            'charging', 'chargingTime', 'dischargingTime', 'level', 'onchargingchange',
            'onchargingtimechange', 'ondischargingtimechange', 'onlevelchange',
            'createOffer', 'createAnswer', 'setLocalDescription', 'setRemoteDescription',
            'addIceCandidate', 'addTrack', 'removeTrack', 'addTransceiver', 'getTransceivers',
            'getSenders', 'getReceivers', 'createDataChannel', 'getStats', 'restartIce',
            'onicecandidate', 'ontrack', 'ondatachannel', 'oniceconnectionstatechange',
            'onnegotiationneeded', 'onsignalingstatechange', 'onicegatheringstatechange',
            'getContext', 'getExtension', 'createShader', 'shaderSource', 'compileShader',
            'createProgram', 'attachShader', 'linkProgram', 'useProgram', 'createBuffer',
            'bindBuffer', 'bufferData', 'createTexture', 'bindTexture', 'texImage2D',
            'drawArrays', 'drawElements', 'viewport', 'clear', 'clearColor', 'enable', 'disable',
            'blendFunc', 'depthFunc', 'cullFace', 'uniform1f', 'uniform2f', 'uniform3f', 'uniform4f',
            'uniformMatrix4fv', 'getAttribLocation', 'getUniformLocation', 'vertexAttribPointer',
            'enableVertexAttribArray', 'disableVertexAttribArray',
            'requestAdapter', 'requestDevice', 'createCommandEncoder', 'createRenderPipeline',
            'createComputePipeline', 'createBindGroup', 'createBindGroupLayout',
            'createPipelineLayout', 'createShaderModule', 'createSampler', 'createQuerySet',
            'beginRenderPass', 'beginComputePass', 'copyBufferToBuffer', 'copyTextureToTexture',
            'submit', 'writeBuffer', 'writeTexture', 'mapAsync', 'getMappedRange', 'unmap',
            'isSessionSupported', 'requestSession', 'requestReferenceSpace', 'requestAnimationFrame',
            'getViewerPose', 'getPose', 'requestHitTestSource', 'updateRenderState',
            'canMakePayment', 'show', 'abort', 'complete', 'retry',
            'create', 'store', 'preventSilentAccess',
            'isUserVerifyingPlatformAuthenticatorAvailable', 'isConditionalMediationAvailable',
            'query', 'request', 'revoke',
            'now', 'mark', 'measure', 'getEntries', 'getEntriesByName', 'getEntriesByType',
            'clearMarks', 'clearMeasures', 'clearResourceTimings', 'setResourceTimingBufferSize',
            'toJSON',
            'sendBeacon',
            'getReader', 'getWriter', 'pipeTo', 'pipeThrough', 'tee', 'enqueue', 'desiredSize',
            'ready', 'releaseLock', 'locked',
            'append', 'set', 'get', 'getAll', 'has', 'delete', 'sort', 'toString', 'forEach',
            'searchParams', 'href', 'origin', 'protocol', 'host', 'hostname', 'port', 'pathname',
            'search', 'hash', 'username', 'password',
            'format', 'formatToParts', 'resolvedOptions', 'supportedLocalesOf', 'compare',
            'select', 'selectRange',
            'canShare', 'share',
            'getAll', 'set', 'delete', 'onchange',
            'getFile', 'createWritable', 'remove', 'isSameEntry', 'queryPermission',
            'requestPermission', 'getDirectory', 'entries', 'values', 'keys', 'resolve',
            'pushState', 'replaceState', 'go', 'back', 'forward', 'state', 'scrollRestoration',
            'startViewTransition', 'skipTransition', 'updateCallbackDone', 'ready', 'finished',
            'requestMIDIAccess', 'inputs', 'outputs', 'onstatechange',
            'requestDevice', 'getAvailability', 'getPrimaryService', 'getPrimaryServices',
            'getCharacteristic', 'getCharacteristics', 'readValue', 'writeValue',
            'writeValueWithResponse', 'writeValueWithoutResponse', 'startNotifications',
            'stopNotifications', 'getDescriptor', 'getDescriptors',
            'getDevices', 'requestDevice', 'open', 'close', 'selectConfiguration',
            'claimInterface', 'releaseInterface', 'selectAlternateInterface', 'controlTransferIn',
            'controlTransferOut', 'transferIn', 'transferOut', 'isochronousTransferIn',
            'isochronousTransferOut', 'reset', 'forget',
            'getPorts', 'requestPort', 'readable', 'writable', 'getSignals', 'setSignals',
            'getDevices', 'requestDevice', 'open', 'close', 'sendReport', 'sendFeatureReport',
            'receiveFeatureReport', 'oninputreport',
            'write', 'scan', 'makeReadOnly',
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
            'convertToBlob', 'transferToImageBitmap',
            'onopen', 'onmessage', 'onerror', 'readyState', 'url', 'withCredentials',
            'createBidirectionalStream', 'createUnidirectionalStream', 'datagrams',
            'incomingBidirectionalStreams', 'incomingUnidirectionalStreams',
            'contentRect', 'borderBoxSize', 'contentBoxSize', 'devicePixelContentBoxSize', 'target',
            'boundingClientRect', 'intersectionRatio', 'intersectionRect', 'isIntersecting',
            'rootBounds', 'time',
            'on', 'off', 'once', 'emit', 'trigger', 'fire',
            'set', 'get', 'has', 'entries', 'values', 'keys', 'size', 'clear', 'delete',
            'forEach', 'next', 'done', 'value', 'return', 'throw',
            'takePhoto', 'grabFrame', 'getPhotoCapabilities', 'getPhotoSettings',
            'stop', 'getTracks', 'getVideoTracks', 'getAudioTracks', 'addTrack', 'removeTrack',
            'getTrackById', 'clone', 'active', 'muted', 'enabled', 'readyState',
            'instant', 'plainDateTimeISO', 'plainDate', 'plainTime', 'plainYearMonth',
            'plainMonthDay', 'zonedDateTimeISO', 'now', 'from', 'compare', 'duration',
            'toInstant', 'toZonedDateTime', 'toPlainDate', 'toPlainTime', 'toPlainDateTime',
            'with', 'add', 'subtract', 'until', 'since', 'round', 'equals', 'toString',
            'allowsFeature', 'features', 'allowedFeatures', 'getAllowlistForFeature',
            'canParse', 'parse',
            'isInteger', 'isFinite', 'isNaN', 'isSafeInteger', 'parseFloat', 'parseInt',
            'toExponential', 'toFixed', 'toPrecision',
            'parseFromString', 'serializeToString',
            'rotateSelf', 'translateSelf', 'scaleSelf', 'skewXSelf', 'skewYSelf',
            'invertSelf', 'multiplySelf', 'preMultiplySelf', 'setMatrixValue',
            'rotate', 'translate', 'scale', 'skewX', 'skewY', 'multiply', 'inverse',
            'flipX', 'flipY', 'transformPoint', 'toFloat32Array', 'toFloat64Array',
            'addModule',
            'compile', 'compileStreaming', 'instantiate', 'instantiateStreaming', 'validate',
            'load', 'play', 'pause', 'fastSeek', 'setMediaKeys', 'setSinkId', 'captureStream',
            'getSelection', 'anchorNode', 'focusNode', 'rangeCount', 'getRangeAt',
            'addRange', 'removeRange', 'removeAllRanges', 'selectAllChildren', 'collapseToStart',
            'collapseToEnd', 'extend', 'containsNode', 'deleteFromDocument',
            'scrollTo', 'scrollBy', 'scrollIntoView', 'scrollIntoViewIfNeeded',
            'getBoundingClientRect', 'getClientRects',
            'focus', 'blur', 'hasFocus',
            'submit', 'reset', 'checkValidity', 'reportValidity', 'setCustomValidity',
            'select', 'setSelectionRange', 'setRangeText', 'stepUp', 'stepDown',
            'getAttribute', 'setAttribute', 'removeAttribute', 'hasAttribute',
            'getAttributeNS', 'setAttributeNS', 'removeAttributeNS', 'hasAttributeNS',
            'toggleAttribute', 'getAttributeNames', 'insertAdjacentElement',
            'insertAdjacentHTML', 'insertAdjacentText', 'before', 'after', 'replaceWith',
            'append', 'prepend', 'replaceChildren',
            'cloneNode', 'appendChild', 'insertBefore', 'removeChild', 'replaceChild',
            'normalize', 'isEqualNode', 'isSameNode', 'compareDocumentPosition',
            'contains', 'lookupPrefix', 'lookupNamespaceURI', 'isDefaultNamespace',
            'log', 'warn', 'error', 'info', 'debug', 'trace', 'dir', 'dirxml', 'table',
            'time', 'timeEnd', 'timeLog', 'count', 'countReset', 'group', 'groupCollapsed',
            'groupEnd', 'clear', 'assert', 'profile', 'profileEnd', 'timeStamp',
        }

        # Common programming verbs -- skip to avoid noise
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
            'apply', 'navigate', 'route', 'redirect', 'goto', 'visit', 'browse',
            'theme', 'style', 'color', 'class', 'attr', 'prop', 'data', 'state', 'store',
            'component', 'element', 'node', 'item', 'list', 'array', 'object', 'value',
            'action', 'event', 'callback', 'handler', 'listener', 'hook', 'effect',
            'use', 'provide', 'consume', 'context', 'ref', 'memo', 'lazy', 'suspend',
        }

        # React components, UI names, etc. -- not browser APIs
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

        method_pattern = r'\.([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('
        found_methods = set(re.findall(method_pattern, js_content))

        global_api_pattern = r'\b([A-Z][a-zA-Z0-9_$]*)\.'
        found_globals = set(re.findall(global_api_pattern, js_content))

        basic_patterns_lower = {b.lower() for b in basic_patterns}

        for method in found_methods:
            method_lower = method.lower()

            if method_lower in basic_patterns_lower:
                continue
            if method in self._matched_apis:
                continue
            if len(method) < 4:
                continue

            skip = False
            for prefix in common_prefixes:
                if method_lower.startswith(prefix) or method_lower.endswith(prefix):
                    skip = True
                    break
            if skip:
                continue

            if method[0].islower() and not any(c.isupper() for c in method[1:3] if len(method) > 2):
                pass

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

        for global_api in found_globals:
            if global_api in basic_patterns:
                continue
            if global_api in self._matched_apis:
                continue
            if global_api in common_globals:
                continue

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
        return {
            'total_features': len(self.features_found),
            'features': sorted(list(self.features_found)),
            'feature_details': self.feature_details,
            'unrecognized': sorted(list(self.unrecognized_patterns))
        }

    def parse_multiple_files(self, filepaths: List[str]) -> Set[str]:
        all_features = set()

        for filepath in filepaths:
            try:
                features = self.parse_file(filepath)
                all_features.update(features)
            except Exception as e:
                logger.warning(f"Could not parse {filepath}: {e}")

        return all_features

    def get_statistics(self) -> Dict:
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
        """Quick check if content looks like JavaScript."""
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
    parser = JavaScriptParser()
    return parser.parse_file(filepath)


def parse_js_string(js_content: str) -> Set[str]:
    parser = JavaScriptParser()
    return parser.parse_string(js_content)
