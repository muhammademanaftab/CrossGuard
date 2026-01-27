"""CSS Parser for Feature Extraction.

This module parses CSS files and extracts modern CSS features
that need compatibility checking.
"""

from typing import Set, List, Dict, Optional
from pathlib import Path
import re

from .css_feature_maps import ALL_CSS_FEATURES
from .custom_rules_loader import get_custom_css_rules
from ..utils.config import get_logger

# Module logger
logger = get_logger('parsers.css')


class CSSParser:
    """Parser for extracting CSS features from CSS files."""

    def __init__(self):
        """Initialize the CSS parser."""
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()  # Patterns not matched by any rule
        # Merge built-in rules with custom rules
        self._all_features = {**ALL_CSS_FEATURES, **get_custom_css_rules()}
        
    def parse_file(self, filepath: str) -> Set[str]:
        """Parse a CSS file and extract features.
        
        Args:
            filepath: Path to the CSS file
            
        Returns:
            Set of Can I Use feature IDs found in the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"CSS file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            return self.parse_string(css_content)
            
        except UnicodeDecodeError:
            raise ValueError(f"File is not valid UTF-8: {filepath}")
        except Exception as e:
            raise ValueError(f"Error parsing CSS file: {e}")
    
    def parse_string(self, css_content: str) -> Set[str]:
        """Parse CSS string and extract features.

        Args:
            css_content: CSS content as string

        Returns:
            Set of Can I Use feature IDs found
        """
        # Reset state
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()

        # Remove comments to avoid false positives
        css_content = self._remove_comments(css_content)

        # Detect features using regex patterns
        self._detect_features(css_content)

        # Find unrecognized patterns
        self._find_unrecognized_patterns(css_content)

        return self.features_found
    
    def _remove_comments_and_strings(self, css_content: str) -> str:
        """Remove CSS comments and string literals from code.

        This prevents false positives from features mentioned in:
        - CSS comments /* ... */
        - content: "..." strings
        - url("...") strings

        Args:
            css_content: CSS code

        Returns:
            Code without comments and string literals
        """
        # Remove CSS comments /* ... */
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

        # Remove string literals (both single and double quoted)
        # This handles content: "...", url("..."), etc.
        # Be careful to handle escaped quotes
        css_content = re.sub(r'"(?:[^"\\]|\\.)*"', '""', css_content)
        css_content = re.sub(r"'(?:[^'\\]|\\.)*'", "''", css_content)

        return css_content

    def _remove_comments(self, css_content: str) -> str:
        """Remove CSS comments and strings from code.

        Args:
            css_content: CSS code

        Returns:
            Code without comments and strings
        """
        return self._remove_comments_and_strings(css_content)
    
    def _detect_features(self, css_content: str):
        """Detect CSS features using regex patterns.
        
        Args:
            css_content: CSS code (without comments)
        """
        # Check each feature (includes both built-in and custom rules)
        for feature_id, feature_info in self._all_features.items():
            patterns = feature_info.get('patterns', [])
            
            # Check if any pattern matches
            for pattern in patterns:
                try:
                    if re.search(pattern, css_content, re.IGNORECASE):
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
    
    def _find_unrecognized_patterns(self, css_content: str):
        """Find CSS properties/features that don't match any known rule.

        Args:
            css_content: CSS code (without comments)
        """
        # Common/basic CSS properties that are universally supported - skip these
        basic_properties = {
            # Colors and backgrounds
            'color', 'background', 'background-color', 'background-image',
            'background-position', 'background-repeat', 'background-size',
            'background-attachment', 'background-origin', 'background-clip',
            'opacity',
            # Box model
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'border', 'border-width', 'border-style', 'border-color',
            'border-top', 'border-right', 'border-bottom', 'border-left',
            'border-radius', 'border-top-left-radius', 'border-top-right-radius',
            'border-bottom-left-radius', 'border-bottom-right-radius',
            'box-shadow', 'box-sizing',
            # Sizing
            'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
            # Typography
            'font', 'font-family', 'font-size', 'font-weight', 'font-style',
            'font-variant', 'text-align', 'text-decoration', 'text-shadow',
            'line-height', 'letter-spacing', 'word-spacing', 'text-indent',
            'text-transform', 'white-space', 'word-wrap', 'word-break',
            # Layout
            'display', 'position', 'top', 'right', 'bottom', 'left',
            'float', 'clear', 'overflow', 'overflow-x', 'overflow-y',
            'visibility', 'z-index', 'clip',
            # Flex/Grid basics (feature detection handles advanced)
            'flex', 'flex-direction', 'flex-wrap', 'flex-flow',
            'flex-grow', 'flex-shrink', 'flex-basis',
            'justify-content', 'align-items', 'align-content', 'align-self',
            'order', 'gap', 'row-gap', 'column-gap',
            # Animation/transition (feature detection handles these)
            'animation', 'animation-name', 'animation-duration', 'animation-timing-function',
            'animation-delay', 'animation-iteration-count', 'animation-direction',
            'animation-fill-mode', 'animation-play-state',
            'transition', 'transition-property', 'transition-duration',
            'transition-timing-function', 'transition-delay',
            # Transform
            'transform', 'transform-origin', 'transform-style', 'perspective',
            # Other common
            'cursor', 'outline', 'outline-width', 'outline-style', 'outline-color',
            'outline-offset', 'list-style', 'list-style-type', 'list-style-position',
            'list-style-image', 'vertical-align', 'content', 'quotes',
            'counter-reset', 'counter-increment',
            # Table
            'table-layout', 'border-collapse', 'border-spacing', 'caption-side',
            'empty-cells',
            # Misc
            'direction', 'unicode-bidi', 'speak', 'resize', 'pointer-events',
            'user-select', 'appearance',
            # @font-face properties
            'src', 'font-display',
            # Object fit/position (feature detection handles these but they're also common)
            'object-fit', 'object-position',
        }

        # Extract CSS properties ONLY from inside declaration blocks
        # This avoids matching class names in selectors like .back-btn:hover
        # We look for property: value patterns that are preceded by { or ;
        # Pattern: after { or ; or newline, capture property name before :
        # But NOT after a . (class selector) or # (id selector)
        property_pattern = r'(?:^|[{;])\s*([a-z][-a-z0-9]*)\s*:'
        found_properties = set(re.findall(property_pattern, css_content, re.IGNORECASE | re.MULTILINE))

        # Extract @-rules (like @keyframes, @media, etc.)
        at_rule_pattern = r'@([a-z][-a-z0-9]*)'
        found_at_rules = set(re.findall(at_rule_pattern, css_content, re.IGNORECASE))

        # Check each property against our feature rules
        for prop in found_properties:
            prop_lower = prop.lower()

            # Skip basic properties
            if prop_lower in basic_properties:
                continue

            # Check if this property matches any feature pattern
            # We test against "property:" to match how patterns are written
            test_string = f"{prop}:"
            matched = False
            for feature_info in self._all_features.values():
                patterns = feature_info.get('patterns', [])
                for pattern in patterns:
                    try:
                        if re.search(pattern, test_string, re.IGNORECASE):
                            matched = True
                            break
                    except re.error:
                        continue
                if matched:
                    break

            if not matched:
                self.unrecognized_patterns.add(f"property: {prop}")

        # Check @-rules
        basic_at_rules = {'media', 'import', 'charset', 'font-face', 'page'}
        for at_rule in found_at_rules:
            at_rule_lower = at_rule.lower()
            if at_rule_lower in basic_at_rules:
                continue

            # Check if matches any feature
            matched = False
            for feature_info in self._all_features.values():
                patterns = feature_info.get('patterns', [])
                for pattern in patterns:
                    try:
                        if re.search(pattern, f"@{at_rule}", re.IGNORECASE):
                            matched = True
                            break
                    except re.error:
                        continue
                if matched:
                    break

            if not matched:
                self.unrecognized_patterns.add(f"@-rule: @{at_rule}")

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
        """Parse multiple CSS files and combine results.
        
        Args:
            filepaths: List of CSS file paths
            
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
        layout_features = []
        transform_animation = []
        color_background = []
        typography = []
        selectors = []
        media_queries = []
        other_features = []
        
        for feature in self.features_found:
            if feature in ['flexbox', 'flexbox-gap', 'css-grid', 'multicolumn', 'inline-block']:
                layout_features.append(feature)
            elif feature in ['transforms2d', 'transforms3d', 'css-animation', 'css-transitions']:
                transform_animation.append(feature)
            elif feature.startswith('css-gradient') or feature in ['multibackgrounds', 'css-filter-function']:
                color_background.append(feature)
            elif feature.startswith('font') or feature.startswith('text-'):
                typography.append(feature)
            elif feature.startswith('css-sel') or 'pseudo' in feature or 'selector' in feature:
                selectors.append(feature)
            elif feature.startswith('prefers-') or feature == 'css-mediaqueries':
                media_queries.append(feature)
            else:
                other_features.append(feature)
        
        return {
            'total_features': len(self.features_found),
            'layout_features': len(layout_features),
            'transform_animation': len(transform_animation),
            'color_background': len(color_background),
            'typography': len(typography),
            'selectors': len(selectors),
            'media_queries': len(media_queries),
            'other_features': len(other_features),
            'features_list': sorted(list(self.features_found)),
            'categories': {
                'layout': layout_features,
                'transform_animation': transform_animation,
                'color_background': color_background,
                'typography': typography,
                'selectors': selectors,
                'media_queries': media_queries,
                'other': other_features
            }
        }
    
    def validate_css(self, css_content: str) -> bool:
        """Basic validation if content looks like CSS.
        
        Args:
            css_content: CSS content to validate
            
        Returns:
            True if looks like valid CSS, False otherwise
        """
        # Very basic check - look for common CSS patterns
        css_patterns = [
            r'\{',
            r'\}',
            r':',
            r';',
            r'@media',
            r'@keyframes',
            r'\.[\w-]+',  # class selector
            r'#[\w-]+',   # id selector
        ]
        
        for pattern in css_patterns:
            if re.search(pattern, css_content):
                return True
        
        return False


def parse_css_file(filepath: str) -> Set[str]:
    """Convenience function to parse a single CSS file.
    
    Args:
        filepath: Path to CSS file
        
    Returns:
        Set of feature IDs found
    """
    parser = CSSParser()
    return parser.parse_file(filepath)


def parse_css_string(css_content: str) -> Set[str]:
    """Convenience function to parse CSS string.
    
    Args:
        css_content: CSS content as string
        
    Returns:
        Set of feature IDs found
    """
    parser = CSSParser()
    return parser.parse_string(css_content)
