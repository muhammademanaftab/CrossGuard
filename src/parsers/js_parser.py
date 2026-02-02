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

        # Remove comments to avoid false positives
        js_content = self._remove_comments(js_content)

        # Detect features using regex patterns
        self._detect_features(js_content)

        # Find unrecognized patterns
        self._find_unrecognized_patterns(js_content)

        return self.features_found
    
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
                self.feature_details.append({
                    'feature': feature_id,
                    'description': feature_info.get('description', ''),
                    'matched_apis': matched_apis,
                })

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
        }

        # Find potential API calls and method usage
        # Pattern for method calls: .methodName( or Object.method(
        method_pattern = r'\.([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('
        found_methods = set(re.findall(method_pattern, js_content))

        # Pattern for global objects/APIs: CapitalizedName.
        global_api_pattern = r'\b([A-Z][a-zA-Z0-9_$]*)\.'
        found_globals = set(re.findall(global_api_pattern, js_content))

        # Check methods
        for method in found_methods:
            if method.lower() in [b.lower() for b in basic_patterns]:
                continue

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

            if not matched and len(method) > 2:  # Skip very short names
                self.unrecognized_patterns.add(f"method: .{method}()")

        # Check global APIs
        for global_api in found_globals:
            if global_api in basic_patterns:
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
                          'rest-parameters', 'optional-chaining', 'nullish-coalescing', 
                          'es6-class']:
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
