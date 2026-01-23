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
        
        # Remove comments to avoid false positives
        js_content = self._remove_comments(js_content)
        
        # Detect features using regex patterns
        self._detect_features(js_content)
        
        return self.features_found
    
    def _remove_comments(self, js_content: str) -> str:
        """Remove JavaScript comments from code.
        
        Args:
            js_content: JavaScript code
            
        Returns:
            Code without comments
        """
        # Remove single-line comments
        js_content = re.sub(r'//.*?$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        return js_content
    
    def _detect_features(self, js_content: str):
        """Detect JavaScript features using regex patterns.
        
        Args:
            js_content: JavaScript code (without comments)
        """
        # Check each feature (includes both built-in and custom rules)
        for feature_id, feature_info in self._all_features.items():
            patterns = feature_info.get('patterns', [])
            
            # Check if any pattern matches
            for pattern in patterns:
                try:
                    if re.search(pattern, js_content):
                        self.features_found.add(feature_id)
                        self.feature_details.append({
                            'feature': feature_id,
                            'description': feature_info.get('description', ''),
                            'pattern': pattern
                        })
                        break  # Found this feature, move to next
                except re.error as e:
                    # Skip invalid regex patterns
                    logger.warning(f"Invalid regex pattern for {feature_id}: {e}")
                    continue
    
    def get_detailed_report(self) -> Dict:
        """Get detailed report of found features.
        
        Returns:
            Dict with detailed information about found features
        """
        return {
            'total_features': len(self.features_found),
            'features': sorted(list(self.features_found)),
            'feature_details': self.feature_details
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
