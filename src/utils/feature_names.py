"""
Feature Names Resolver - Convert technical feature IDs to human-readable names.

Resolution order:
1. Feature map description field
2. Can I Use database title field
3. Fallback: Convert ID to title case
"""

from typing import Dict, Optional

# Common feature ID to human-readable name mappings
FEATURE_NAMES = {
    # CSS Layout
    'css-grid': 'CSS Grid Layout',
    'flexbox': 'Flexbox',
    'flexbox-gap': 'Flexbox Gap Property',
    'multicolumn': 'Multi-Column Layout',
    'inline-block': 'Inline Block Display',
    'flow-root': 'Flow Root Display',
    'css-subgrid': 'CSS Subgrid',
    'css-container-queries': 'Container Queries',
    'css-container-queries-style': 'Container Style Queries',

    # CSS Transforms & Animations
    'transforms2d': '2D Transforms',
    'transforms3d': '3D Transforms',
    'css-animation': 'CSS Animations',
    'css-transitions': 'CSS Transitions',
    'will-change': 'Will-Change Property',

    # CSS Colors & Backgrounds
    'css3-colors': 'CSS3 Colors (RGB/HSL)',
    'currentcolor': 'currentColor Value',
    'css-gradients': 'CSS Gradients',
    'multibackgrounds': 'Multiple Backgrounds',
    'background-img-opts': 'Background Image Options',
    'css-filters': 'CSS Filters',
    'css-backdrop-filter': 'Backdrop Filter',
    'css-color-function': 'Color Function',
    'hwb': 'HWB Color',
    'css-lch-lab': 'LCH/Lab Colors',

    # CSS Layout Control
    'css-sticky': 'Sticky Positioning',
    'object-fit': 'Object Fit',
    'css-overflow-anchor': 'Scroll Anchoring',
    'css-scroll-snap': 'Scroll Snap',
    'css-overscroll-behavior': 'Overscroll Behavior',
    'css-aspect-ratio': 'Aspect Ratio',

    # CSS Variables & Functions
    'css-variables': 'CSS Custom Properties (Variables)',
    'calc': 'CSS calc() Function',
    'css-math-functions': 'CSS Math Functions',
    'font-size-adjust': 'Font Size Adjust',
    'css-clamp': 'CSS clamp() Function',
    'css-min-max': 'CSS min()/max() Functions',

    # CSS Selectors
    'css-sel3': 'CSS3 Selectors',
    'css-sel2': 'CSS2 Selectors',
    'css-not-sel-list': ':not() Selector List',
    'css-has': ':has() Selector',
    'css-is-where': ':is() and :where()',
    'css-focus-visible': ':focus-visible',
    'css-focus-within': ':focus-within',
    'css-placeholder': '::placeholder',
    'css-marker-pseudo': '::marker Pseudo-element',

    # CSS Typography
    'fontface': '@font-face',
    'woff': 'WOFF Fonts',
    'woff2': 'WOFF2 Fonts',
    'variable-fonts': 'Variable Fonts',
    'font-feature': 'Font Feature Settings',
    'font-variant-alternates': 'Font Variants',
    'css-hyphens': 'CSS Hyphens',
    'css-text-orientation': 'Text Orientation',
    'css-writing-mode': 'Writing Mode',

    # CSS Modern Features
    'css-logical-props': 'Logical Properties',
    'css-nesting': 'CSS Nesting',
    'css-cascade-layers': 'Cascade Layers (@layer)',
    'css-cascade-scope': 'CSS @scope',
    'css-color-adjust': 'Color Scheme',
    'prefers-color-scheme': 'Dark Mode Media Query',
    'prefers-reduced-motion': 'Reduced Motion Query',

    # JavaScript APIs
    'async-functions': 'Async/Await',
    'promises': 'Promises',
    'fetch': 'Fetch API',
    'arrow-functions': 'Arrow Functions',
    'let': 'let/const Declarations',
    'template-literals': 'Template Literals',
    'es6-class': 'ES6 Classes',
    'es6-module': 'ES6 Modules',
    'es6-module-dynamic-import': 'Dynamic Import',
    'destructuring': 'Destructuring',
    'spread': 'Spread Operator',
    'rest-parameters': 'Rest Parameters',
    'default-parameter': 'Default Parameters',
    'object-shorthand': 'Object Shorthand',
    'for-of': 'for...of Loop',
    'for-in': 'for...in Loop',
    'symbols': 'Symbols',
    'map-set': 'Map and Set',
    'weakmap-weakset': 'WeakMap and WeakSet',
    'proxy': 'Proxy Object',
    'reflect': 'Reflect API',
    'generators': 'Generators',
    'iterators': 'Iterators',

    # JavaScript DOM/Web APIs
    'intersectionobserver': 'Intersection Observer',
    'resizeobserver': 'Resize Observer',
    'mutationobserver': 'Mutation Observer',
    'queryselector': 'querySelector',
    'classlist': 'classList API',
    'dataset': 'Data Attributes API',
    'geolocation': 'Geolocation API',
    'webworkers': 'Web Workers',
    'serviceworkers': 'Service Workers',
    'push-api': 'Push API',
    'notifications': 'Notifications API',
    'websockets': 'WebSockets',
    'webrtc': 'WebRTC',
    'indexeddb': 'IndexedDB',
    'localstorage': 'Local Storage',
    'sessionstorage': 'Session Storage',
    'history': 'History API',
    'hashchange': 'Hashchange Event',
    'requestanimationframe': 'requestAnimationFrame',
    'web-animation': 'Web Animations API',
    'clipboard': 'Clipboard API',
    'beacon': 'Beacon API',
    'broadcastchannel': 'Broadcast Channel',
    'channel-messaging': 'Channel Messaging',

    # HTML5 Features
    'audio': 'HTML5 Audio',
    'video': 'HTML5 Video',
    'canvas': 'Canvas',
    'webgl': 'WebGL',
    'webgl2': 'WebGL 2',
    'picture': 'Picture Element',
    'srcset': 'Srcset Attribute',
    'loading-lazy-attr': 'Lazy Loading (loading="lazy")',
    'dialog': 'Dialog Element',
    'details': 'Details/Summary',
    'datalist': 'Datalist Element',
    'input-color': 'Color Input',
    'input-datetime-local': 'Datetime Local Input',
    'input-email-tel-url': 'Email/Tel/URL Inputs',
    'input-number': 'Number Input',
    'input-range': 'Range Input',
    'input-search': 'Search Input',
    'form-validation': 'Form Validation',
    'contenteditable': 'Contenteditable',
    'dragndrop': 'Drag and Drop',
    'semantic-elements': 'Semantic Elements',

    # Security & Performance
    'subresource-integrity': 'Subresource Integrity',
    'csp': 'Content Security Policy',
    'cors': 'CORS',
    'cryptography': 'Web Cryptography',

    # Media & Graphics
    'webp': 'WebP Images',
    'avif': 'AVIF Images',
    'svg': 'SVG',
    'svg-filters': 'SVG Filters',
    'svg-css': 'SVG in CSS',
}

# Fix suggestions for common issues
FIX_SUGGESTIONS = {
    'css-grid': 'Use @supports to provide flexbox fallback for older browsers',
    'flexbox-gap': 'Consider margin-based spacing as fallback for browsers without gap support',
    'css-variables': 'Provide fallback values inline: color: blue; color: var(--primary, blue)',
    'css-container-queries': 'Use @supports to detect container query support; provide mobile-first fallbacks',
    'css-has': 'Use JavaScript feature detection as fallback for :has() selector',
    'css-nesting': 'Use a CSS preprocessor (Sass/Less) for broader nesting support',
    'async-functions': 'Transpile with Babel or use Promise chains as fallback',
    'es6-module': 'Use a bundler like webpack/rollup with appropriate targets',
    'fetch': 'Include a fetch polyfill for older browsers',
    'intersectionobserver': 'Include IntersectionObserver polyfill from W3C',
    'resizeobserver': 'Include ResizeObserver polyfill for broader support',
    'webp': 'Use picture element with fallback formats (JPEG/PNG)',
    'avif': 'Use picture element with WebP and JPEG fallbacks',
    'dialog': 'Use dialog polyfill or custom modal implementation',
    'loading-lazy-attr': 'Use JavaScript lazy loading library as fallback',
    'css-backdrop-filter': 'Provide solid background color fallback',
    'css-scroll-snap': 'Works as enhancement; no critical fallback needed',
    'serviceworkers': 'Progressive enhancement - app works without SW',
    'webrtc': 'Check for feature support before using; provide fallback messaging',
    'css-sticky': 'Use JavaScript-based sticky positioning as fallback',
    'css-filters': 'Filters degrade gracefully; consider SVG filters for critical effects',
    'css-aspect-ratio': 'Use padding-top hack for aspect ratio in older browsers',
}


def get_feature_name(
    feature_id: str,
    feature_maps: Optional[Dict] = None,
    caniuse_data: Optional[Dict] = None
) -> str:
    """Get human-readable name for a feature ID.

    Args:
        feature_id: Technical feature ID (e.g., 'css-grid')
        feature_maps: Optional dict of feature maps with descriptions
        caniuse_data: Optional Can I Use database data

    Returns:
        Human-readable feature name
    """
    # 1. Check our predefined mappings
    if feature_id in FEATURE_NAMES:
        return FEATURE_NAMES[feature_id]

    # 2. Check feature maps description
    if feature_maps:
        for category in feature_maps.values():
            if isinstance(category, dict) and feature_id in category:
                desc = category[feature_id].get('description')
                if desc:
                    return desc

    # 3. Check Can I Use title
    if caniuse_data and feature_id in caniuse_data:
        title = caniuse_data[feature_id].get('title')
        if title:
            return title

    # 4. Fallback: Convert ID to title case
    return _id_to_title(feature_id)


def _id_to_title(feature_id: str) -> str:
    """Convert feature ID to title case.

    Examples:
        'css-grid' -> 'CSS Grid'
        'async-functions' -> 'Async Functions'
        'intersectionobserver' -> 'Intersection Observer'
    """
    # Handle common prefixes
    prefixes = {
        'css-': 'CSS ',
        'js-': 'JavaScript ',
        'html-': 'HTML ',
        'es6-': 'ES6 ',
        'web-': 'Web ',
    }

    result = feature_id
    for prefix, replacement in prefixes.items():
        if result.startswith(prefix):
            result = result[len(prefix):]
            result = replacement + result
            break

    # Replace hyphens with spaces
    result = result.replace('-', ' ')

    # Handle camelCase by inserting spaces
    import re
    result = re.sub(r'([a-z])([A-Z])', r'\1 \2', result)

    # Title case
    result = result.title()

    # Fix common acronyms that should be uppercase
    acronyms = ['Api', 'Css', 'Html', 'Js', 'Dom', 'Svg', 'Url', 'Uri', 'Xhr', 'Ajax', 'Json', 'Xml']
    for acronym in acronyms:
        result = result.replace(acronym, acronym.upper())

    return result


def get_fix_suggestion(feature_id: str) -> Optional[str]:
    """Get fix suggestion for a feature.

    Args:
        feature_id: Technical feature ID

    Returns:
        Fix suggestion text or None
    """
    return FIX_SUGGESTIONS.get(feature_id)


def get_severity(support_status: str) -> str:
    """Convert support status to severity level.

    Args:
        support_status: 'n' (no), 'a' (partial), 'y' (yes), etc.

    Returns:
        'critical' for unsupported, 'warning' for partial
    """
    if support_status in ('n', 'u'):  # no support or unknown
        return 'critical'
    elif support_status in ('a', 'p', 'd'):  # partial, polyfill, disabled
        return 'warning'
    return 'info'
