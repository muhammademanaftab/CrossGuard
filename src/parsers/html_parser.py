"""HTML Parser for Feature Extraction.

This module parses HTML files and extracts modern HTML5 features
that need compatibility checking.
"""

from typing import Set, List, Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import re

from .html_feature_maps import (
    HTML_ELEMENTS,
    HTML_INPUT_TYPES,
    HTML_ATTRIBUTES,
    HTML_ATTRIBUTE_VALUES,
    ALL_HTML_FEATURES
)
from .custom_rules_loader import get_custom_html_rules
from ..utils.config import get_logger

# Module logger
logger = get_logger('parsers.html')


class HTMLParser:
    """Parser for extracting HTML5 features from HTML files."""

    def __init__(self):
        """Initialize the HTML parser."""
        self.features_found = set()
        self.elements_found = []
        self.attributes_found = []
        self.unrecognized_patterns = set()  # Patterns not matched by any rule

        # Merge built-in rules with custom rules
        custom_html = get_custom_html_rules()
        self._elements = {**HTML_ELEMENTS, **custom_html.get('elements', {})}
        self._input_types = {**HTML_INPUT_TYPES, **custom_html.get('input_types', {})}
        self._attributes = {**HTML_ATTRIBUTES, **custom_html.get('attributes', {})}
        # Parse attribute_values from "attr:value" format to tuple format
        custom_attr_values = {}
        for key, value in custom_html.get('attribute_values', {}).items():
            if ':' in key:
                attr, val = key.split(':', 1)
                custom_attr_values[(attr, val)] = value
        self._attribute_values = {**HTML_ATTRIBUTE_VALUES, **custom_attr_values}
        
    def parse_file(self, filepath: str) -> Set[str]:
        """Parse an HTML file and extract features.
        
        Args:
            filepath: Path to the HTML file
            
        Returns:
            Set of Can I Use feature IDs found in the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid HTML
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"HTML file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return self.parse_string(html_content)
            
        except UnicodeDecodeError:
            raise ValueError(f"File is not valid UTF-8: {filepath}")
        except Exception as e:
            raise ValueError(f"Error parsing HTML file: {e}")
    
    def parse_string(self, html_content: str) -> Set[str]:
        """Parse HTML string and extract features.

        Args:
            html_content: HTML content as string

        Returns:
            Set of Can I Use feature IDs found
        """
        # Reset state
        self.features_found = set()
        self.elements_found = []
        self.attributes_found = []
        self.unrecognized_patterns = set()

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract features
        self._detect_elements(soup)
        self._detect_input_types(soup)
        self._detect_attributes(soup)
        self._detect_attribute_values(soup)
        self._detect_special_patterns(soup)

        # Find unrecognized patterns
        self._find_unrecognized_patterns(soup)

        return self.features_found
    
    def _detect_elements(self, soup: BeautifulSoup):
        """Detect modern HTML5 elements.
        
        Args:
            soup: BeautifulSoup parsed HTML
        """
        for element_name, feature_id in self._elements.items():
            elements = soup.find_all(element_name)
            
            if elements:
                self.features_found.add(feature_id)
                self.elements_found.append({
                    'element': element_name,
                    'feature': feature_id,
                    'count': len(elements)
                })
    
    def _detect_input_types(self, soup: BeautifulSoup):
        """Detect modern input types.
        
        Args:
            soup: BeautifulSoup parsed HTML
        """
        # Find all input elements
        inputs = soup.find_all('input')
        
        for input_elem in inputs:
            input_type = input_elem.get('type', '').lower()
            
            if input_type in self._input_types:
                feature_id = self._input_types[input_type]
                self.features_found.add(feature_id)
                self.elements_found.append({
                    'element': f'input[type="{input_type}"]',
                    'feature': feature_id,
                    'count': 1
                })
    
    def _detect_attributes(self, soup: BeautifulSoup):
        """Detect modern HTML attributes.
        
        Args:
            soup: BeautifulSoup parsed HTML
        """
        # Find all elements
        all_elements = soup.find_all()
        
        for element in all_elements:
            for attr_name in element.attrs:
                if attr_name in self._attributes:
                    feature_id = self._attributes[attr_name]
                    self.features_found.add(feature_id)
                    self.attributes_found.append({
                        'attribute': attr_name,
                        'element': element.name,
                        'feature': feature_id
                    })
    
    def _detect_attribute_values(self, soup: BeautifulSoup):
        """Detect specific attribute value combinations.
        
        Args:
            soup: BeautifulSoup parsed HTML
        """
        all_elements = soup.find_all()
        
        for element in all_elements:
            for attr_name, attr_value in element.attrs.items():
                # Handle both single values and lists
                values = [attr_value] if isinstance(attr_value, str) else attr_value
                
                for value in values:
                    key = (attr_name, value.lower() if isinstance(value, str) else value)
                    
                    if key in self._attribute_values:
                        feature_id = self._attribute_values[key]
                        self.features_found.add(feature_id)
                        self.attributes_found.append({
                            'attribute': f'{attr_name}="{value}"',
                            'element': element.name,
                            'feature': feature_id
                        })
    
    def _detect_special_patterns(self, soup: BeautifulSoup):
        """Detect special HTML patterns and features.
        
        Args:
            soup: BeautifulSoup parsed HTML
        """
        # Detect srcset attribute (responsive images)
        elements_with_srcset = soup.find_all(attrs={'srcset': True})
        if elements_with_srcset:
            self.features_found.add('srcset')
        
        # Detect sizes attribute (responsive images)
        elements_with_sizes = soup.find_all(attrs={'sizes': True})
        if elements_with_sizes:
            self.features_found.add('srcset')  # Part of same feature
        
        # Detect picture element with source
        pictures = soup.find_all('picture')
        for picture in pictures:
            sources = picture.find_all('source')
            if sources:
                self.features_found.add('picture')
        
        # Detect data attributes (data-*)
        all_elements = soup.find_all()
        for element in all_elements:
            for attr in element.attrs:
                if attr.startswith('data-'):
                    self.features_found.add('dataset')
                    break
        
        # Detect async/defer on scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.get('async') is not None:
                self.features_found.add('script-async')
            if script.get('defer') is not None:
                self.features_found.add('script-defer')
            if script.get('type') == 'module':
                self.features_found.add('es6-module')
        
        # Detect link rel preload/prefetch
        links = soup.find_all('link')
        for link in links:
            rel = link.get('rel', [])
            if isinstance(rel, str):
                rel = [rel]
            
            for rel_value in rel:
                rel_lower = rel_value.lower()
                if rel_lower == 'preload':
                    self.features_found.add('link-rel-preload')
                elif rel_lower == 'prefetch':
                    self.features_found.add('link-rel-prefetch')
                elif rel_lower == 'dns-prefetch':
                    self.features_found.add('link-rel-dns-prefetch')
                elif rel_lower == 'preconnect':
                    self.features_found.add('link-rel-preconnect')
                elif rel_lower == 'modulepreload':
                    self.features_found.add('link-rel-modulepreload')
        
        # Detect meta viewport
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_meta:
            self.features_found.add('viewport-units')
        
        # Note: meta charset is universally supported and not tracked in Can I Use
        # so we don't detect it to avoid "feature not found" warnings
    
    def _find_unrecognized_patterns(self, soup: BeautifulSoup):
        """Find HTML elements/attributes that don't match any known rule.

        Args:
            soup: BeautifulSoup parsed HTML
        """
        # Basic HTML elements that are universally supported - skip these
        basic_elements = {
            'html', 'head', 'body', 'title', 'meta', 'link', 'script', 'style',
            'div', 'span', 'p', 'a', 'img', 'br', 'hr',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'dl', 'dt', 'dd',
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot', 'caption', 'colgroup', 'col',
            'form', 'input', 'button', 'select', 'option', 'optgroup', 'textarea', 'label', 'fieldset', 'legend',
            'iframe', 'object', 'embed', 'param',
            'strong', 'em', 'b', 'i', 'u', 's', 'small', 'big', 'sub', 'sup',
            'code', 'pre', 'blockquote', 'q', 'cite', 'abbr', 'acronym',
            'ins', 'del', 'dfn', 'kbd', 'samp', 'var', 'address',
            'noscript', 'map', 'area', 'base',
            # HTML5 semantic elements that are well-supported
            'header', 'footer', 'nav', 'article', 'section', 'aside', 'main',
            'figure', 'figcaption', 'time', 'mark', 'wbr',
        }

        # Basic attributes that are universally supported
        basic_attributes = {
            'id', 'class', 'style', 'title', 'lang', 'dir',
            'href', 'src', 'alt', 'name', 'value', 'type',
            'width', 'height', 'border', 'align', 'valign',
            'colspan', 'rowspan', 'cellpadding', 'cellspacing',
            'action', 'method', 'enctype', 'target', 'rel',
            'disabled', 'readonly', 'checked', 'selected', 'multiple',
            'maxlength', 'size', 'rows', 'cols', 'tabindex', 'accesskey',
            'onclick', 'onsubmit', 'onchange', 'onload', 'onerror',
            'onmouseover', 'onmouseout', 'onfocus', 'onblur', 'onkeydown', 'onkeyup',
            'onkeypress', 'ondblclick', 'onmousedown', 'onmouseup', 'onmousemove',
            'onreset', 'onselect', 'oninput', 'onfocusin', 'onfocusout',
            'charset', 'content', 'http-equiv', 'media',
            'for', 'form', 'accept', 'accept-charset',
            'usemap', 'ismap', 'coords', 'shape',
            'xmlns', 'xml:lang', 'role', 'aria-label', 'aria-hidden',
            # Media attributes
            'controls', 'autoplay', 'loop', 'muted', 'preload', 'poster',
            'playsinline', 'crossorigin',
            # Iframe attributes
            'frameborder', 'scrolling', 'allowfullscreen', 'sandbox',
            # Link/script attributes
            'async', 'defer', 'integrity', 'nonce', 'referrerpolicy',
            # Other common attributes
            'placeholder', 'pattern', 'min', 'max', 'step', 'list',
            'autocomplete', 'autofocus', 'required', 'novalidate',
            'hidden', 'spellcheck', 'translate', 'contenteditable', 'draggable',
            # SVG attributes (part of SVG spec, well-supported)
            'd', 'fill', 'fill-rule', 'fill-opacity', 'stroke', 'stroke-width',
            'stroke-linecap', 'stroke-linejoin', 'stroke-opacity', 'stroke-dasharray',
            'viewbox', 'viewBox', 'preserveaspectratio', 'preserveAspectRatio',
            'cx', 'cy', 'r', 'rx', 'ry', 'x', 'y', 'x1', 'y1', 'x2', 'y2',
            'points', 'transform', 'path', 'xmlns:xlink', 'xlink:href',
            'clip-path', 'clip-rule', 'mask', 'opacity', 'filter',
            'stop-color', 'stop-opacity', 'offset', 'gradientunits', 'gradientUnits',
            'patternunits', 'patternUnits', 'spreadmethod', 'spreadMethod',
            # Data attributes are handled separately
        }

        # Get all elements in the document
        all_elements = soup.find_all()

        # Track unique element names
        found_element_names = set()
        for elem in all_elements:
            if elem.name:
                found_element_names.add(elem.name.lower())

        # Check for unrecognized elements (custom elements with hyphens)
        for elem_name in found_element_names:
            if elem_name in basic_elements:
                continue
            if elem_name in self._elements:
                continue

            # Custom elements (contain hyphen) that aren't in our rules
            if '-' in elem_name:
                self.unrecognized_patterns.add(f"element: <{elem_name}>")

        # Check for unrecognized attributes
        found_attributes = set()
        for elem in all_elements:
            for attr_name in elem.attrs:
                if isinstance(attr_name, str):
                    found_attributes.add(attr_name.lower())

        for attr_name in found_attributes:
            # Skip basic attributes
            if attr_name in basic_attributes:
                continue
            # Skip data-* attributes (handled elsewhere)
            if attr_name.startswith('data-'):
                continue
            # Skip aria-* attributes
            if attr_name.startswith('aria-'):
                continue
            # Skip if in our rules
            if attr_name in self._attributes:
                continue

            # This attribute is unrecognized
            self.unrecognized_patterns.add(f"attribute: {attr_name}")

    def get_detailed_report(self) -> Dict:
        """Get detailed report of found features.

        Returns:
            Dict with detailed information about found features
        """
        return {
            'total_features': len(self.features_found),
            'features': sorted(list(self.features_found)),
            'elements_found': self.elements_found,
            'attributes_found': self.attributes_found,
            'unrecognized': sorted(list(self.unrecognized_patterns))
        }
    
    def parse_multiple_files(self, filepaths: List[str]) -> Set[str]:
        """Parse multiple HTML files and combine results.
        
        Args:
            filepaths: List of HTML file paths
            
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
    
    def validate_html(self, html_content: str) -> bool:
        """Validate if content is valid HTML.
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            True if valid HTML, False otherwise
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup is not None
        except Exception:
            return False
    
    def get_statistics(self) -> Dict:
        """Get parsing statistics.
        
        Returns:
            Dict with parsing statistics
        """
        element_counts = {}
        for elem in self.elements_found:
            element_counts[elem['element']] = element_counts.get(elem['element'], 0) + elem['count']
        
        attribute_counts = {}
        for attr in self.attributes_found:
            attr_name = attr['attribute']
            attribute_counts[attr_name] = attribute_counts.get(attr_name, 0) + 1
        
        return {
            'total_features': len(self.features_found),
            'total_elements_detected': len(self.elements_found),
            'total_attributes_detected': len(self.attributes_found),
            'element_counts': element_counts,
            'attribute_counts': attribute_counts,
            'features_list': sorted(list(self.features_found))
        }


def parse_html_file(filepath: str) -> Set[str]:
    """Convenience function to parse a single HTML file.
    
    Args:
        filepath: Path to HTML file
        
    Returns:
        Set of feature IDs found
    """
    parser = HTMLParser()
    return parser.parse_file(filepath)


def parse_html_string(html_content: str) -> Set[str]:
    """Convenience function to parse HTML string.
    
    Args:
        html_content: HTML content as string
        
    Returns:
        Set of feature IDs found
    """
    parser = HTMLParser()
    return parser.parse_string(html_content)
