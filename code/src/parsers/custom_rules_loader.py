"""Loads user-defined detection rules from custom_rules.json."""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from ..utils.config import get_logger

logger = get_logger('parsers.custom_rules')

CUSTOM_RULES_PATH = Path(__file__).parent / "custom_rules.json"


class CustomRulesLoader:
    """Singleton that loads and caches custom detection rules."""

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
        if not CUSTOM_RULES_PATH.exists():
            logger.debug("No custom_rules.json found, using built-in rules only")
            return

        try:
            # utf-8-sig strips an optional UTF-8 BOM that macOS TextEdit /
            # Windows Notepad may have added on save.
            with open(CUSTOM_RULES_PATH, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

            css_data = data.get('css', {})
            for feature_id, feature_info in css_data.items():
                if feature_id.startswith('_'):
                    continue  # Skip metadata keys
                if isinstance(feature_info, dict) and isinstance(feature_info.get('patterns'), list):
                    self._css_rules[feature_id] = feature_info
                    logger.debug(f"Loaded custom CSS rule: {feature_id}")

            js_data = data.get('javascript', {})
            for feature_id, feature_info in js_data.items():
                if feature_id.startswith('_'):
                    continue
                if isinstance(feature_info, dict) and isinstance(feature_info.get('patterns'), list):
                    self._js_rules[feature_id] = feature_info
                    logger.debug(f"Loaded custom JS rule: {feature_id}")

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
        return self._css_rules.copy()

    def get_custom_js_rules(self) -> Dict[str, Dict]:
        return self._js_rules.copy()

    def get_custom_html_rules(self) -> Dict[str, Any]:
        return self._html_rules.copy()

    def reload(self):
        self._css_rules = {}
        self._js_rules = {}
        self._html_rules = {
            'elements': {},
            'attributes': {},
            'input_types': {},
            'attribute_values': {}
        }
        self._load_rules()


_loader: Optional[CustomRulesLoader] = None


def get_custom_rules_loader() -> CustomRulesLoader:
    global _loader
    if _loader is None:
        _loader = CustomRulesLoader()
    return _loader


def get_custom_css_rules() -> Dict[str, Dict]:
    return get_custom_rules_loader().get_custom_css_rules()


def get_custom_js_rules() -> Dict[str, Dict]:
    return get_custom_rules_loader().get_custom_js_rules()


def get_custom_html_rules() -> Dict[str, Any]:
    return get_custom_rules_loader().get_custom_html_rules()


def reload_custom_rules():
    get_custom_rules_loader().reload()


def is_user_rule(category: str, feature_id: str, subtype: str = None) -> bool:
    loader = get_custom_rules_loader()

    if category == 'css':
        return feature_id in loader._css_rules
    elif category == 'javascript':
        return feature_id in loader._js_rules
    elif category == 'html':
        if subtype:
            return feature_id in loader._html_rules.get(subtype, {})
        for subcat in ['elements', 'attributes', 'input_types', 'attribute_values']:
            if feature_id in loader._html_rules.get(subcat, {}):
                return True
        return False
    return False


def save_custom_rules(rules_data: dict) -> bool:
    try:
        with open(CUSTOM_RULES_PATH, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, indent=2)

        reload_custom_rules()
        return True
    except Exception as e:
        logger.error(f"Error saving custom rules: {e}")
        return False


def load_raw_custom_rules() -> dict:
    try:
        if CUSTOM_RULES_PATH.exists():
            with open(CUSTOM_RULES_PATH, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading raw custom rules: {e}")

    return {
        "css": {},
        "javascript": {},
        "html": {
            "elements": {},
            "attributes": {},
            "input_types": {},
            "attribute_values": {}
        }
    }
