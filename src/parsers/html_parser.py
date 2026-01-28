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
    HTML_SPECIAL_ELEMENTS,
    HTML_ARIA_ATTRIBUTES,
    HTML_MEDIA_TYPE_VALUES,
    HTML_CSP_ATTRIBUTES,
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
        self._elements = {**HTML_ELEMENTS, **HTML_SPECIAL_ELEMENTS, **custom_html.get('elements', {})}
        self._input_types = {**HTML_INPUT_TYPES, **custom_html.get('input_types', {})}
        self._attributes = {**HTML_ATTRIBUTES, **HTML_ARIA_ATTRIBUTES, **custom_html.get('attributes', {})}
        # Parse attribute_values from "attr:value" format to tuple format
        custom_attr_values = {}
        for key, value in custom_html.get('attribute_values', {}).items():
            if ':' in key:
                attr, val = key.split(':', 1)
                custom_attr_values[(attr, val)] = value
        self._attribute_values = {**HTML_ATTRIBUTE_VALUES, **HTML_MEDIA_TYPE_VALUES, **HTML_CSP_ATTRIBUTES, **custom_attr_values}
        
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
                    value_lower = value.lower() if isinstance(value, str) else value
                    key = (attr_name, value_lower)

                    if key in self._attribute_values:
                        feature_id = self._attribute_values[key]
                        self.features_found.add(feature_id)
                        self.attributes_found.append({
                            'attribute': f'{attr_name}="{value}"',
                            'element': element.name,
                            'feature': feature_id
                        })
                    # Handle media types with codec parameters (e.g., "video/webm; codecs=vp9")
                    elif attr_name == 'type' and isinstance(value_lower, str) and ';' in value_lower:
                        # Extract base media type before semicolon
                        base_type = value_lower.split(';')[0].strip()
                        base_key = (attr_name, base_type)

                        if base_key in self._attribute_values:
                            feature_id = self._attribute_values[base_key]
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

        # Detect meta theme-color
        theme_color_meta = soup.find('meta', attrs={'name': 'theme-color'})
        if theme_color_meta:
            self.features_found.add('meta-theme-color')

        # Detect SVG in img src
        self._detect_svg_in_img(soup)

        # Detect SVG fragments
        self._detect_svg_fragments(soup)

        # Detect media fragments
        self._detect_media_fragments(soup)

        # Detect custom elements (hyphenated tag names)
        self._detect_custom_elements(soup)

        # Detect fieldset with disabled attribute
        self._detect_fieldset_disabled(soup)

        # Detect track elements in audio/video
        self._detect_track_elements(soup)

        # Detect WebVTT (.vtt files in track elements)
        self._detect_webvtt(soup)

        # Detect data URIs
        self._detect_data_uris(soup)

        # Detect XHTML (application/xhtml+xml)
        self._detect_xhtml(soup)

        # Note: meta charset is universally supported and not tracked in Can I Use
        # so we don't detect it to avoid "feature not found" warnings

    def _detect_svg_in_img(self, soup: BeautifulSoup):
        """Detect SVG images in img src attributes.

        Args:
            soup: BeautifulSoup parsed HTML
        """
        svg_pattern = re.compile(r'\.svg(\?.*)?$', re.IGNORECASE)

        # Check img elements
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if svg_pattern.search(src):
                self.features_found.add('svg-img')
                return

        # Check source elements in picture
        for source in soup.find_all('source'):
            srcset = source.get('srcset', '')
            if svg_pattern.search(srcset):
                self.features_found.add('svg-img')
                return

    def _detect_svg_fragments(self, soup: BeautifulSoup):
        """Detect SVG fragment identifiers (use href with #id).

        Args:
            soup: BeautifulSoup parsed HTML
        """
        # Check <use> elements with href containing fragment
        for use in soup.find_all('use'):
            href = use.get('href', '') or use.get('xlink:href', '')
            if '#' in href:
                self.features_found.add('svg-fragment')
                return

        # Check any element with svg fragment reference
        fragment_pattern = re.compile(r'\.svg#\w+', re.IGNORECASE)
        all_elements = soup.find_all()
        for element in all_elements:
            for attr_value in element.attrs.values():
                if isinstance(attr_value, str) and fragment_pattern.search(attr_value):
                    self.features_found.add('svg-fragment')
                    return

    def _detect_media_fragments(self, soup: BeautifulSoup):
        """Detect media fragment URIs (#t=start,end for time fragments).

        Args:
            soup: BeautifulSoup parsed HTML
        """
        # Pattern for media fragments: #t=, #track=, #xywh=
        fragment_pattern = re.compile(r'#(t|track|xywh|id)=', re.IGNORECASE)

        # Check video and audio elements
        for media in soup.find_all(['video', 'audio']):
            src = media.get('src', '')
            if fragment_pattern.search(src):
                self.features_found.add('media-fragments')
                return

            # Check nested source elements
            for source in media.find_all('source'):
                src = source.get('src', '')
                if fragment_pattern.search(src):
                    self.features_found.add('media-fragments')
                    return

    def _detect_custom_elements(self, soup: BeautifulSoup):
        """Detect custom elements (hyphenated tag names).

        Args:
            soup: BeautifulSoup parsed HTML
        """
        # Custom elements must contain a hyphen
        all_elements = soup.find_all()
        for element in all_elements:
            if element.name and '-' in element.name:
                # Skip known SVG elements with hyphens
                svg_elements = {'font-face', 'font-face-src', 'font-face-uri',
                               'font-face-format', 'font-face-name', 'missing-glyph',
                               'color-profile', 'glyph-ref'}
                if element.name.lower() not in svg_elements:
                    self.features_found.add('custom-elementsv1')
                    return

    def _detect_fieldset_disabled(self, soup: BeautifulSoup):
        """Detect fieldset elements with disabled attribute.

        Args:
            soup: BeautifulSoup parsed HTML
        """
        for fieldset in soup.find_all('fieldset'):
            if fieldset.has_attr('disabled'):
                self.features_found.add('fieldset-disabled')
                return

    def _detect_track_elements(self, soup: BeautifulSoup):
        """Detect track elements in audio/video for subtitles/captions.

        Args:
            soup: BeautifulSoup parsed HTML
        """
        # Check video elements for track children
        for video in soup.find_all('video'):
            tracks = video.find_all('track')
            if tracks:
                self.features_found.add('videotracks')

        # Check audio elements for track children
        for audio in soup.find_all('audio'):
            tracks = audio.find_all('track')
            if tracks:
                self.features_found.add('audiotracks')

    def _detect_webvtt(self, soup: BeautifulSoup):
        """Detect WebVTT usage (.vtt files in track elements).

        Args:
            soup: BeautifulSoup parsed HTML
        """
        vtt_pattern = re.compile(r'\.vtt(\?.*)?$', re.IGNORECASE)

        for track in soup.find_all('track'):
            src = track.get('src', '')
            if vtt_pattern.search(src):
                self.features_found.add('webvtt')
                return

    def _detect_data_uris(self, soup: BeautifulSoup):
        """Detect data URIs in src, href, and other URL attributes.

        Args:
            soup: BeautifulSoup parsed HTML
        """
        data_uri_pattern = re.compile(r'^data:', re.IGNORECASE)

        # Check common URL attributes
        url_attrs = ['src', 'href', 'poster', 'data']
        for attr in url_attrs:
            for element in soup.find_all(attrs={attr: data_uri_pattern}):
                self.features_found.add('datauri')
                return

        # Check srcset for data URIs
        for element in soup.find_all(attrs={'srcset': True}):
            srcset = element.get('srcset', '')
            if 'data:' in srcset:
                self.features_found.add('datauri')
                return

    def _detect_xhtml(self, soup: BeautifulSoup):
        """Detect XHTML namespace declaration.

        Args:
            soup: BeautifulSoup parsed HTML
        """
        html_elem = soup.find('html')
        if html_elem:
            xmlns = html_elem.get('xmlns', '')
            if 'xhtml' in xmlns.lower():
                self.features_found.add('xhtml')
    
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
