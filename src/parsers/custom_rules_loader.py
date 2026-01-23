"""Custom Rules Loader for Cross Guard.

This module loads user-defined detection rules from custom_rules.json
and merges them with the built-in feature maps.

Users can extend the built-in feature detection by editing custom_rules.json
without modifying the core application code.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from ..utils.config import get_logger

logger = get_logger('parsers.custom_rules')

# Path to the custom rules file
CUSTOM_RULES_PATH = Path(__file__).parent / "custom_rules.json"


class CustomRulesLoader:
    """Loads and manages custom detection rules."""
    
    _instance: Optional['CustomRulesLoader'] = None
    _loaded: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if CustomRulesLoader._loaded:
            return
        CustomRulesLoader._loaded = True
        
        self._css_rules: Dict[str, Dict] = {}
        self._js_rules: Dict[str, Dict] = {}
        self._html_rules: Dict[str, Any] = {
            'elements': {},
            'attributes': {},
            'input_types': {},
            'attribute_values': {}
        }
        self._load_rules()
    
    def _load_rules(self):
        """Load custom rules from JSON file."""
        if not CUSTOM_RULES_PATH.exists():
            logger.debug("No custom_rules.json found, using built-in rules only")
            return
        
        try:
            with open(CUSTOM_RULES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load CSS rules
            css_data = data.get('css', {})
            for feature_id, feature_info in css_data.items():
                if feature_id.startswith('_'):
                    continue  # Skip comments/metadata
                if isinstance(feature_info, dict) and 'patterns' in feature_info:
                    self._css_rules[feature_id] = feature_info
                    logger.debug(f"Loaded custom CSS rule: {feature_id}")
            
            # Load JavaScript rules
            js_data = data.get('javascript', {})
            for feature_id, feature_info in js_data.items():
                if feature_id.startswith('_'):
                    continue
                if isinstance(feature_info, dict) and 'patterns' in feature_info:
                    self._js_rules[feature_id] = feature_info
                    logger.debug(f"Loaded custom JS rule: {feature_id}")
            
            # Load HTML rules
            html_data = data.get('html', {})
            
            elements = html_data.get('elements', {})
            for key, value in elements.items():
                if not key.startswith('_'):
                    self._html_rules['elements'][key] = value
            
            attributes = html_data.get('attributes', {})
            for key, value in attributes.items():
                if not key.startswith('_'):
                    self._html_rules['attributes'][key] = value
            
            input_types = html_data.get('input_types', {})
            for key, value in input_types.items():
                if not key.startswith('_'):
                    self._html_rules['input_types'][key] = value
            
            attr_values = html_data.get('attribute_values', {})
            for key, value in attr_values.items():
                if not key.startswith('_'):
                    self._html_rules['attribute_values'][key] = value
            
            total = len(self._css_rules) + len(self._js_rules)
            total += sum(len(v) for v in self._html_rules.values() if isinstance(v, dict))
            
            if total > 0:
                logger.info(f"Loaded {total} custom detection rules from custom_rules.json")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in custom_rules.json: {e}")
        except Exception as e:
            logger.error(f"Error loading custom rules: {e}")
    
    def get_custom_css_rules(self) -> Dict[str, Dict]:
        """Get custom CSS detection rules."""
        return self._css_rules.copy()
    
    def get_custom_js_rules(self) -> Dict[str, Dict]:
        """Get custom JavaScript detection rules."""
        return self._js_rules.copy()
    
    def get_custom_html_rules(self) -> Dict[str, Any]:
        """Get custom HTML detection rules."""
        return self._html_rules.copy()
    
    def reload(self):
        """Reload custom rules from file."""
        self._css_rules = {}
        self._js_rules = {}
        self._html_rules = {
            'elements': {},
            'attributes': {},
            'input_types': {},
            'attribute_values': {}
        }
        self._load_rules()


# Singleton instance
_loader: Optional[CustomRulesLoader] = None


def get_custom_rules_loader() -> CustomRulesLoader:
    """Get the custom rules loader instance."""
    global _loader
    if _loader is None:
        _loader = CustomRulesLoader()
    return _loader


def get_custom_css_rules() -> Dict[str, Dict]:
    """Convenience function to get custom CSS rules."""
    return get_custom_rules_loader().get_custom_css_rules()


def get_custom_js_rules() -> Dict[str, Dict]:
    """Convenience function to get custom JS rules."""
    return get_custom_rules_loader().get_custom_js_rules()


def get_custom_html_rules() -> Dict[str, Any]:
    """Convenience function to get custom HTML rules."""
    return get_custom_rules_loader().get_custom_html_rules()


def reload_custom_rules():
    """Reload custom rules from file."""
    get_custom_rules_loader().reload()
