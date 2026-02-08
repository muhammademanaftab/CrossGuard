"""CSS Parser for Feature Extraction.

This module parses CSS files and extracts modern CSS features
that need compatibility checking. Uses tinycss2 for structural
CSS parsing (W3C CSS Syntax Level 3 compliant), then applies
regex patterns from feature maps for feature detection.
"""

from typing import Set, List, Dict, Tuple
from collections import OrderedDict
from pathlib import Path
import re

import tinycss2

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
        self._block_counter = 0  # Unique block ID for preserving block boundaries
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

        Uses tinycss2 to structurally parse the CSS, then applies
        regex feature patterns against the extracted components.

        Args:
            css_content: CSS content as string

        Returns:
            Set of Can I Use feature IDs found
        """
        # Reset state
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()
        self._block_counter = 0

        # Parse with tinycss2 (comments and whitespace are skipped)
        rules = tinycss2.parse_stylesheet(
            css_content, skip_comments=True, skip_whitespace=True
        )

        # Extract structured components from the AST
        declarations, at_rules, selectors = self._extract_components(rules)

        # Build clean text for regex feature matching
        matchable_text = self._build_matchable_text(
            declarations, at_rules, selectors
        )

        # Detect features using existing regex patterns on clean text
        self._detect_features(matchable_text)

        # Find unrecognized patterns using structured data
        self._find_unrecognized_patterns_structured(declarations, at_rules)

        return self.features_found

    def _extract_components(self, rules) -> Tuple[
        List[Tuple[str, str, str, int]],
        List[Tuple[str, str]],
        List[str]
    ]:
        """Extract declarations, @-rules, and selectors from parsed CSS.

        Recursively walks the tinycss2 AST to collect structured data.

        Args:
            rules: List of tinycss2 AST nodes

        Returns:
            tuple: (declarations, at_rules, selectors)
            - declarations: list of (property_name, value_string, selector, block_id)
            - at_rules: list of (at_keyword, prelude_string) tuples
            - selectors: list of selector strings
        """
        declarations = []
        at_rules_list = []
        selectors = []

        for rule in rules:
            if isinstance(rule, tinycss2.ast.ParseError):
                logger.warning(f"CSS parse error: {rule.message}")
                continue

            if isinstance(rule, tinycss2.ast.QualifiedRule):
                # Regular rule: selector { declarations }
                selector_text = tinycss2.serialize(rule.prelude).strip()
                selectors.append(selector_text)

                # Parse content for declarations and nested rules
                self._extract_block_contents(
                    rule.content, selector_text,
                    declarations, at_rules_list, selectors
                )

            elif isinstance(rule, tinycss2.ast.AtRule):
                keyword = rule.at_keyword.lower()
                prelude_text = tinycss2.serialize(rule.prelude).strip()
                at_rules_list.append((keyword, prelude_text))

                if rule.content is not None:
                    if keyword == 'font-face':
                        # @font-face has declarations directly
                        self._extract_block_contents(
                            rule.content, '@font-face',
                            declarations, at_rules_list, selectors
                        )
                    else:
                        # @media, @supports, @keyframes, @layer, @container, etc.
                        # Recurse into content for nested rules
                        inner_rules = tinycss2.parse_blocks_contents(
                            rule.content
                        )
                        # Filter whitespace
                        inner_rules = [
                            r for r in inner_rules
                            if not isinstance(r, tinycss2.ast.WhitespaceToken)
                        ]
                        sub_decls, sub_at, sub_sel = self._extract_components(
                            inner_rules
                        )
                        declarations.extend(sub_decls)
                        at_rules_list.extend(sub_at)
                        selectors.extend(sub_sel)

        return declarations, at_rules_list, selectors

    def _extract_block_contents(
        self, content, selector_text,
        declarations, at_rules_list, selectors
    ):
        """Extract declarations and nested rules from a block's content.

        Args:
            content: tinycss2 block content (list of tokens)
            selector_text: The selector/context this block belongs to
            declarations: Accumulator list for (property, value, selector, block_id)
            at_rules_list: Accumulator list for (keyword, prelude)
            selectors: Accumulator list for selector strings
        """
        block_id = self._block_counter
        self._block_counter += 1
        parsed = tinycss2.parse_blocks_contents(content)
        for item in parsed:
            if isinstance(item, tinycss2.ast.Declaration):
                value_text = tinycss2.serialize(item.value).strip()
                declarations.append((item.name, value_text, selector_text, block_id))
            elif isinstance(item, tinycss2.ast.QualifiedRule):
                # Nested rule (CSS nesting or @keyframes stops)
                nested_sel = tinycss2.serialize(item.prelude).strip()
                selectors.append(nested_sel)
                self._extract_block_contents(
                    item.content, nested_sel,
                    declarations, at_rules_list, selectors
                )
            elif isinstance(item, tinycss2.ast.AtRule):
                keyword = item.at_keyword.lower()
                prelude_text = tinycss2.serialize(item.prelude).strip()
                at_rules_list.append((keyword, prelude_text))
                if item.content is not None:
                    inner = tinycss2.parse_blocks_contents(item.content)
                    inner = [
                        r for r in inner
                        if not isinstance(r, tinycss2.ast.WhitespaceToken)
                    ]
                    sub_d, sub_a, sub_s = self._extract_components(inner)
                    declarations.extend(sub_d)
                    at_rules_list.extend(sub_a)
                    selectors.extend(sub_s)

    def _build_matchable_text(self, declarations, at_rules, selectors) -> str:
        """Build clean text from components for regex feature matching.

        Constructs text that preserves the structure existing regex patterns
        expect. Each rule block is reconstructed as:
            selector { property: value; ... }
        @-rules are included as:
            @keyword prelude
        This ensures patterns like flexbox-gap that use [^}]* to match
        within a block continue to work correctly. Blocks are kept separate
        even when selectors repeat, preserving original block boundaries.

        Args:
            declarations: list of (property_name, value_string, selector, block_id)
            at_rules: list of (at_keyword, prelude_string)
            selectors: list of selector strings

        Returns:
            Clean text string for regex matching
        """
        parts = []

        # Group declarations by block_id to preserve original block boundaries
        # (duplicate selectors in separate blocks stay separate)
        blocks = OrderedDict()
        for prop, value, sel, block_id in declarations:
            if block_id not in blocks:
                blocks[block_id] = (sel, [])
            blocks[block_id][1].append((prop, value))

        # Build rule blocks
        selectors_with_decls = set()
        for block_id, (sel, decl_list) in blocks.items():
            selectors_with_decls.add(sel)
            decl_text = '; '.join(
                f"{prop}: {val}" for prop, val in decl_list
            )
            parts.append(f"{sel} {{ {decl_text}; }}")

        # Add selectors that might not have declarations (e.g., empty rules)
        # These are needed for selector-based pattern matching
        for sel in selectors:
            if sel not in selectors_with_decls:
                parts.append(f"{sel} {{ }}")
                selectors_with_decls.add(sel)

        # Add @-rules
        for keyword, prelude in at_rules:
            if prelude:
                parts.append(f"@{keyword} {prelude}")
            else:
                parts.append(f"@{keyword}")

        return '\n'.join(parts)

    def _detect_features(self, css_content: str):
        """Detect CSS features using regex patterns.

        Args:
            css_content: Clean CSS text for pattern matching
        """
        # Check each feature (includes both built-in and custom rules)
        for feature_id, feature_info in self._all_features.items():
            patterns = feature_info.get('patterns', [])
            matched_properties = []
            feature_found = False

            # Check all patterns and collect matched properties
            for pattern in patterns:
                try:
                    matches = re.findall(pattern, css_content, re.IGNORECASE)
                    if matches:
                        feature_found = True
                        # Try to extract property name from the pattern
                        # Pattern like 'scrollbar-color\s*:' -> property 'scrollbar-color'
                        # Pattern like '\d+rem' -> no property (it's a value pattern)
                        prop_match = re.match(r'^([a-z][-a-z0-9]*)', pattern, re.IGNORECASE)
                        if prop_match:
                            prop_name = prop_match.group(1)
                            if prop_name not in matched_properties:
                                matched_properties.append(prop_name)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern for {feature_id}: {e}")
                    continue

            if feature_found:
                self.features_found.add(feature_id)
                self.feature_details.append({
                    'feature': feature_id,
                    'description': feature_info.get('description', ''),
                    'matched_properties': matched_properties,  # May be empty for value patterns
                })

    def _find_unrecognized_patterns_structured(self, declarations, at_rules):
        """Find CSS properties/features that don't match any known rule.

        Uses structured data from tinycss2 instead of regex extraction.

        Args:
            declarations: list of (property_name, value_string, selector, block_id) tuples
            at_rules: list of (at_keyword, prelude_string) tuples
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
            'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
            'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
            'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
            'border-radius', 'border-top-left-radius', 'border-top-right-radius',
            'border-bottom-left-radius', 'border-bottom-right-radius',
            'box-shadow', 'box-sizing',
            # SVG properties
            'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin',
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
            'animation-fill-mode', 'animation-play-state', 'animation-timeline',
            'animation-range', 'animation-range-start', 'animation-range-end',
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
            'user-select', 'appearance', 'accent-color',
            # @font-face properties
            'src', 'font-display',
            # Object fit/position (feature detection handles these but they're also common)
            'object-fit', 'object-position',
        }

        # Get unique property names from structured declarations
        found_properties = set(prop for prop, _, _, _ in declarations)

        # Check each property against our feature rules
        for prop in found_properties:
            prop_lower = prop.lower()

            # Skip basic properties
            if prop_lower in basic_properties:
                continue

            # Skip custom properties (--var-name)
            if prop_lower.startswith('--'):
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
        found_at_keywords = set(kw for kw, _ in at_rules)
        for at_rule in found_at_keywords:
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
            'unrecognized': sorted(list(self.unrecognized_patterns)),
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

        # Selector/pseudo-class/pseudo-element feature IDs
        selector_features = {
            'css-sel2', 'css-sel3', 'css-not-sel-list',
            'css-has', 'css-matches-pseudo',
            'css-focus-within', 'css-focus-visible',
            'css-any-link', 'css-read-only-write',
            'css-in-out-of-range', 'css-case-insensitive',
            'css-optional-pseudo', 'css-default-pseudo',
            'css-indeterminate-pseudo', 'css-dir-pseudo',
            'css-cascade-scope',
            'css-first-letter', 'css-first-line',
            'css-selection', 'css-placeholder', 'css-placeholder-shown',
            'css-marker-pseudo', 'css-gencontent',
        }

        for feature in self.features_found:
            if feature in ['flexbox', 'flexbox-gap', 'css-grid', 'multicolumn', 'inline-block']:
                layout_features.append(feature)
            elif feature in ['transforms2d', 'transforms3d', 'css-animation', 'css-transitions']:
                transform_animation.append(feature)
            elif feature.startswith('css-gradient') or feature in ['multibackgrounds', 'css-filter-function']:
                color_background.append(feature)
            elif feature.startswith('font') or feature.startswith('text-'):
                typography.append(feature)
            elif feature in selector_features:
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
        """Validate if content looks like CSS using tinycss2 parsing.

        Uses tinycss2 to structurally parse the content. Accepts content
        that contains valid stylesheet rules (selectors with blocks, @-rules)
        or CSS fragments like standalone declarations (property: value).

        Args:
            css_content: CSS content to validate

        Returns:
            True if looks like valid CSS, False otherwise
        """
        if not css_content or not css_content.strip():
            return False

        try:
            rules = tinycss2.parse_stylesheet(
                css_content, skip_comments=True, skip_whitespace=True
            )
        except Exception:
            return False

        # Check for full stylesheet rules (selector blocks, @-rules)
        for rule in rules:
            if isinstance(rule, (tinycss2.ast.QualifiedRule, tinycss2.ast.AtRule)):
                return True

        # Also accept CSS fragments: standalone declarations (property: value)
        # These aren't valid stylesheets but are valid CSS content
        if re.search(r'[\w-]+\s*:', css_content):
            return True

        # Accept content with braces (even empty rule blocks)
        if re.search(r'\{', css_content):
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
