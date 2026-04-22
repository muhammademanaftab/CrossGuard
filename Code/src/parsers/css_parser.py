"""CSS parser -- extracts browser features using tinycss2 AST + regex matching."""

from typing import Set, List, Dict, Tuple
from collections import OrderedDict
from pathlib import Path
import re

import tinycss2

from .css_feature_maps import ALL_CSS_FEATURES
from .custom_rules_loader import get_custom_css_rules
from ..utils.config import get_logger

logger = get_logger('parsers.css')


# Universally-supported properties we don't need to flag
_BASIC_PROPERTIES = frozenset({
    'color', 'background', 'background-color', 'background-image',
    'background-position', 'background-repeat', 'background-size',
    'background-attachment', 'background-origin', 'background-clip',
    'opacity',
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
    'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin',
    'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
    'font', 'font-family', 'font-size', 'font-weight', 'font-style',
    'font-variant', 'text-align', 'text-decoration', 'text-shadow',
    'line-height', 'letter-spacing', 'word-spacing', 'text-indent',
    'text-transform', 'white-space', 'word-wrap', 'word-break',
    'display', 'position', 'top', 'right', 'bottom', 'left',
    'float', 'clear', 'overflow', 'overflow-x', 'overflow-y',
    'visibility', 'z-index', 'clip',
    'flex', 'flex-direction', 'flex-wrap', 'flex-flow',
    'flex-grow', 'flex-shrink', 'flex-basis',
    'justify-content', 'align-items', 'align-content', 'align-self',
    'order', 'gap', 'row-gap', 'column-gap',
    'animation', 'animation-name', 'animation-duration', 'animation-timing-function',
    'animation-delay', 'animation-iteration-count', 'animation-direction',
    'animation-fill-mode', 'animation-play-state', 'animation-timeline',
    'animation-range', 'animation-range-start', 'animation-range-end',
    'transition', 'transition-property', 'transition-duration',
    'transition-timing-function', 'transition-delay',
    'transform', 'transform-origin', 'transform-style', 'perspective',
    'cursor', 'outline', 'outline-width', 'outline-style', 'outline-color',
    'outline-offset', 'list-style', 'list-style-type', 'list-style-position',
    'list-style-image', 'vertical-align', 'content', 'quotes',
    'counter-reset', 'counter-increment',
    'table-layout', 'border-collapse', 'border-spacing', 'caption-side',
    'empty-cells',
    'direction', 'unicode-bidi', 'speak', 'resize', 'pointer-events',
    'user-select', 'appearance', 'accent-color',
    'src', 'font-display',
    'object-fit', 'object-position',
})


class CSSParser:
    """Extracts Can I Use feature IDs from CSS files."""

    def __init__(self):
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()
        self._block_counter = 0  # Preserves block boundaries in matchable text
        self._all_features = {**ALL_CSS_FEATURES, **get_custom_css_rules()}

    def parse_file(self, filepath: str) -> Set[str]:
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"CSS file not found: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                css_content = f.read()

            return self.parse_string(css_content)

        except UnicodeDecodeError as e:
            raise ValueError(f"File is not valid UTF-8: {filepath}") from e
        except Exception as e:
            raise ValueError(f"Error parsing CSS file: {e}") from e

    def parse_string(self, css_content: str) -> Set[str]:
        self.features_found = set()
        self.feature_details = []
        self.unrecognized_patterns = set()
        self._block_counter = 0

        rules = tinycss2.parse_stylesheet(
            css_content, skip_comments=True, skip_whitespace=True
        )

        declarations, at_rules, selectors = self._extract_components(rules)

        # Reconstruct text that preserves block structure for regex patterns
        matchable_text = self._build_matchable_text(
            declarations, at_rules, selectors
        )

        self._detect_features(matchable_text)
        self._find_unrecognized_patterns_structured(declarations, at_rules)

        return self.features_found

    def _extract_components(self, rules) -> Tuple[
        List[Tuple[str, str, str, int]],
        List[Tuple[str, str]],
        List[str]
    ]:
        declarations = []
        at_rules_list = []
        selectors = []

        for rule in rules:
            if isinstance(rule, tinycss2.ast.ParseError):
                logger.warning(f"CSS parse error: {rule.message}")
                continue

            if isinstance(rule, tinycss2.ast.QualifiedRule):
                selector_text = tinycss2.serialize(rule.prelude).strip()
                selectors.append(selector_text)

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
                        # @font-face has declarations directly, not nested rules
                        self._extract_block_contents(
                            rule.content, '@font-face',
                            declarations, at_rules_list, selectors
                        )
                    else:
                        # @media, @supports, @keyframes, etc. -- recurse
                        inner_rules = tinycss2.parse_blocks_contents(
                            rule.content
                        )
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
        # Block boundaries are preserved so [^}]* patterns (e.g. flexbox-gap) can't match across rules.
        parts = []

        # Group by block_id to keep separate blocks separate
        blocks = OrderedDict()
        for prop, value, sel, block_id in declarations:
            if block_id not in blocks:
                blocks[block_id] = (sel, [])
            blocks[block_id][1].append((prop, value))

        selectors_with_decls = set()
        for block_id, (sel, decl_list) in blocks.items():
            selectors_with_decls.add(sel)
            decl_text = '; '.join(
                f"{prop}: {val}" for prop, val in decl_list
            )
            parts.append(f"{sel} {{ {decl_text}; }}")

        # Empty rules still matter for selector-based matching
        for sel in selectors:
            if sel not in selectors_with_decls:
                parts.append(f"{sel} {{ }}")
                selectors_with_decls.add(sel)

        for keyword, prelude in at_rules:
            if prelude:
                parts.append(f"@{keyword} {prelude}")
            else:
                parts.append(f"@{keyword}")

        return '\n'.join(parts)

    def _detect_features(self, css_content: str):
        for feature_id, feature_info in self._all_features.items():
            patterns = feature_info.get('patterns', [])
            matched_properties = []
            feature_found = False

            for pattern in patterns:
                try:
                    matches = re.findall(pattern, css_content, re.IGNORECASE)
                    if matches:
                        feature_found = True
                        # Try to pull a property name from the pattern for reporting
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
                    'matched_properties': matched_properties,
                })

    def _find_unrecognized_patterns_structured(self, declarations, at_rules):
        found_properties = set(prop for prop, _, _, _ in declarations)

        for prop in found_properties:
            prop_lower = prop.lower()

            if prop_lower in _BASIC_PROPERTIES:
                continue
            if prop_lower.startswith('--'):
                continue

            # Test "property:" against feature patterns
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

        basic_at_rules = {'media', 'import', 'charset', 'font-face', 'page'}
        found_at_keywords = set(kw for kw, _ in at_rules)
        for at_rule in found_at_keywords:
            at_rule_lower = at_rule.lower()
            if at_rule_lower in basic_at_rules:
                continue

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
        return {
            'total_features': len(self.features_found),
            'features': sorted(list(self.features_found)),
            'feature_details': self.feature_details,
            'unrecognized': sorted(list(self.unrecognized_patterns)),
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
        layout_features = []
        transform_animation = []
        color_background = []
        typography = []
        selectors = []
        media_queries = []
        other_features = []

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
        if not css_content or not css_content.strip():
            return False

        try:
            rules = tinycss2.parse_stylesheet(
                css_content, skip_comments=True, skip_whitespace=True
            )
        except Exception:
            return False

        for rule in rules:
            if isinstance(rule, (tinycss2.ast.QualifiedRule, tinycss2.ast.AtRule)):
                return True

        # Also accept standalone declarations (property: value) -- valid CSS fragments
        if re.search(r'[\w-]+\s*:', css_content):
            return True

        if re.search(r'\{', css_content):
            return True

        return False


def parse_css_file(filepath: str) -> Set[str]:
    parser = CSSParser()
    return parser.parse_file(filepath)


def parse_css_string(css_content: str) -> Set[str]:
    parser = CSSParser()
    return parser.parse_string(css_content)
