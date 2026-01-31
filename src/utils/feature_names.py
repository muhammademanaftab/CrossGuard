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
    'flexbox': 'CSS Flexbox',
    'flexbox-gap': 'Flexbox Gap Property',
    'multicolumn': 'Multi-Column Layout',
    'inline-block': 'CSS display: inline-block',
    'flow-root': 'CSS display: flow-root',
    'run-in': 'CSS display: run-in',
    'css-subgrid': 'CSS Subgrid',
    'css-container-queries': 'Container Queries',
    'css-container-queries-style': 'Container Style Queries',

    # CSS Transforms & Animations
    'transforms2d': 'CSS 2D Transforms',
    'transforms3d': 'CSS 3D Transforms',
    'css-animation': 'CSS Animations',
    'css-transitions': 'CSS Transitions',
    'will-change': 'CSS will-change Property',
    'css-motion-paths': 'CSS Motion Path',

    # CSS Interaction
    'css-resize': 'CSS resize Property',
    'pointer-events': 'CSS pointer-events',
    'user-select-none': 'CSS user-select',
    'css-appearance': 'CSS appearance Property',
    'css-caret-color': 'CSS caret-color',
    'css-touch-action': 'CSS touch-action',
    'css3-cursors': 'CSS3 Cursors',
    'css3-cursors-grab': 'CSS grab/grabbing Cursors',
    'css3-cursors-newer': 'CSS zoom-in/zoom-out Cursors',
    'css-scrollbar': 'CSS Scrollbar Styling',

    # CSS Misc
    'css-opacity': 'CSS Opacity',
    'css-featurequeries': 'CSS @supports (Feature Queries)',
    'css-counters': 'CSS Counters',
    'css-page-break': 'CSS Page Break Properties',
    'css-paged-media': 'CSS @page (Paged Media)',
    'css-shapes': 'CSS Shapes',
    'css-masks': 'CSS Masks',
    'css-containment': 'CSS Containment',
    'css-content-visibility': 'CSS content-visibility',
    'css-display-contents': 'CSS display: contents',
    'css-all': 'CSS all Property',
    'css-unset-value': 'CSS unset Value',
    'css-initial-value': 'CSS initial Value',
    'css-revert-value': 'CSS revert Value',
    'css-widows-orphans': 'CSS widows & orphans',
    'css-image-set': 'CSS image-set()',
    'css-crisp-edges': 'CSS image-rendering',
    'view-transitions': 'View Transitions API',
    'cross-document-view-transitions': 'Cross-Document View Transitions',

    # CSS Colors & Backgrounds
    'css3-colors': 'CSS3 Colors (RGB/HSL)',
    'currentcolor': 'CSS currentColor',
    'css-gradients': 'CSS Gradients',
    'css-conic-gradients': 'CSS Conic Gradients',
    'css-repeating-gradients': 'CSS Repeating Gradients',
    'multibackgrounds': 'Multiple Backgrounds',
    'background-img-opts': 'Background Image Options',
    'background-clip-text': 'CSS background-clip: text',
    'css-filters': 'CSS Filters',
    'css-filter-function': 'CSS Filter Effects',
    'css-backdrop-filter': 'CSS Backdrop Filter',
    'css-color-function': 'CSS color() Function',
    'hwb': 'HWB Color',
    'css-lch-lab': 'LCH/Lab Colors',
    'css-rrggbbaa': 'CSS #RRGGBBAA Hex Colors',
    'css-mixblendmode': 'CSS mix-blend-mode',
    'css-backgroundblendmode': 'CSS background-blend-mode',

    # CSS Layout Control
    'css-sticky': 'CSS position: sticky',
    'css-fixed': 'CSS position: fixed',
    'css-table': 'CSS display: table',
    'object-fit': 'CSS object-fit/object-position',
    'css-overflow': 'CSS Overflow Property',
    'css-overflow-anchor': 'CSS Scroll Anchoring',
    'css-snappoints': 'CSS Scroll Snap Points',
    'css-scroll-snap': 'CSS Scroll Snap',
    'css-scroll-behavior': 'CSS scroll-behavior',
    'css-overscroll-behavior': 'CSS overscroll-behavior',
    'css-aspect-ratio': 'CSS aspect-ratio',
    'css-clip-path': 'CSS clip-path',

    # CSS Variables & Functions
    'css-variables': 'CSS Custom Properties (Variables)',
    'calc': 'CSS calc() Function',
    'css-math-functions': 'CSS min()/max()/clamp()',
    'font-size-adjust': 'CSS font-size-adjust',
    'css-clamp': 'CSS clamp() Function',
    'css-min-max': 'CSS min()/max() Functions',
    'css-env-function': 'CSS env() Function',
    'css3-attr': 'CSS attr() Function',

    # CSS Units
    'rem': 'rem (Root em) Units',
    'ch-unit': 'ch (Character Width) Unit',
    'viewport-units': 'Viewport Units (vw/vh/vmin/vmax)',
    'viewport-unit-variants': 'Viewport Units (svw/lvw/dvw)',
    'css-container-query-units': 'Container Query Units (cqw/cqh)',

    # CSS Box Model
    'css3-boxsizing': 'CSS box-sizing',
    'minmaxwh': 'CSS min/max Width & Height',
    'intrinsic-width': 'CSS min-content/max-content/fit-content',
    'border-radius': 'CSS Border Radius',
    'border-image': 'CSS Border Image',
    'css-boxshadow': 'CSS Box Shadow',
    'css-textshadow': 'CSS Text Shadow',
    'outline': 'CSS Outline Properties',
    'css-boxdecorationbreak': 'CSS box-decoration-break',

    # CSS Selectors
    'css-sel3': 'CSS3 Selectors',
    'css-sel2': 'CSS2.1 Selectors',
    'css-not-sel-list': ':not() Selector List',
    'css-has': 'CSS :has() Selector',
    'css-matches-pseudo': 'CSS :is()/:where() Selectors',
    'css-is-where': ':is() and :where()',
    'css-focus-visible': 'CSS :focus-visible',
    'css-focus-within': 'CSS :focus-within',
    'css-placeholder': 'CSS ::placeholder',
    'css-placeholder-shown': 'CSS :placeholder-shown',
    'css-marker-pseudo': 'CSS ::marker',
    'css-gencontent': 'CSS ::before/::after',
    'css-first-letter': 'CSS ::first-letter',
    'css-first-line': 'CSS ::first-line',
    'css-selection': 'CSS ::selection',
    'css-optional-pseudo': 'CSS :optional/:required',
    'css-indeterminate-pseudo': 'CSS :indeterminate',
    'css-default-pseudo': 'CSS :default',
    'css-dir-pseudo': 'CSS :dir()',
    'css-any-link': 'CSS :any-link',
    'css-read-only-write': 'CSS :read-only/:read-write',
    'css-case-insensitive': 'CSS Case-Insensitive Selectors',
    'css-in-out-of-range': 'CSS :in-range/:out-of-range',
    'css-nth-child-of': 'CSS :nth-child(of)',

    # CSS Typography
    'fontface': 'CSS @font-face',
    'woff': 'WOFF Web Fonts',
    'woff2': 'WOFF2 Web Fonts',
    'ttf': 'TTF/OTF Fonts',
    'eot': 'EOT Fonts',
    'svg-fonts': 'SVG Fonts',
    'colr': 'COLR/CPAL Font Formats',
    'colr-v1': 'COLR v1 Font Formats',
    'variable-fonts': 'Variable Fonts',
    'font-feature': 'CSS font-feature-settings',
    'font-kerning': 'CSS font-kerning',
    'font-variant-alternates': 'CSS font-variant-alternates',
    'font-variant-numeric': 'CSS font-variant-numeric',
    'font-unicode-range': 'CSS unicode-range',
    'font-family-system-ui': 'CSS system-ui Font',
    'extended-system-fonts': 'CSS ui-serif/ui-sans-serif',
    'font-smooth': 'CSS font-smoothing',
    'font-stretch': 'CSS font-stretch',
    'css-hyphens': 'CSS Hyphenation',
    'css-text-orientation': 'CSS text-orientation',
    'css-writing-mode': 'CSS writing-mode',
    'text-overflow': 'CSS text-overflow',
    'text-decoration': 'CSS text-decoration Styling',
    'text-emphasis': 'CSS text-emphasis',
    'text-stroke': 'CSS text-stroke',
    'text-size-adjust': 'CSS text-size-adjust',
    'css-text-wrap-balance': 'CSS text-wrap',
    'css-line-clamp': 'CSS line-clamp',
    'word-break': 'CSS word-break',
    'wordwrap': 'CSS overflow-wrap/word-wrap',
    'css3-tabsize': 'CSS tab-size',
    'css-text-align-last': 'CSS text-align-last',
    'css-text-indent': 'CSS text-indent',
    'css-text-justify': 'CSS text-justify',
    'css-letter-spacing': 'CSS letter-spacing',

    # CSS Modern Features
    'css-logical-props': 'CSS Logical Properties',
    'css-nesting': 'CSS Nesting',
    'css-cascade-layers': 'CSS @layer (Cascade Layers)',
    'css-cascade-scope': 'CSS @scope',
    'css-color-adjust': 'CSS print-color-adjust',
    'prefers-color-scheme': 'prefers-color-scheme Media Query',
    'prefers-reduced-motion': 'prefers-reduced-motion Media Query',
    'css-mediaqueries': 'CSS3 Media Queries',
    'css-media-resolution': 'Media Query: resolution',
    'css-media-range-syntax': 'Media Query Range Syntax',
    'css-media-interaction': 'Media Query: hover/pointer',
    'css-media-scripting': 'Media Query: scripting',

    # JavaScript ES6+ Features
    'async-functions': 'JS Async/Await',
    'promises': 'JS Promises',
    'fetch': 'Fetch API',
    'arrow-functions': 'JS Arrow Functions',
    'let': 'JS let Declaration',
    'const': 'JS const Declaration',
    'template-literals': 'JS Template Literals',
    'es6-class': 'JS ES6 Classes',
    'es6-module': 'JS ES6 Modules',
    'es6-module-dynamic-import': 'JS Dynamic Import',
    'es6': 'JS ES6 Features',
    'es6-generators': 'JS Generators',
    'es5': 'JS ES5 Array Methods',
    'destructuring': 'JS Destructuring',
    'spread': 'JS Spread Operator',
    'rest-parameters': 'JS Rest Parameters',
    'default-parameter': 'JS Default Parameters',
    'object-shorthand': 'JS Object Shorthand',
    'for-of': 'JS for...of Loop',
    'for-in': 'JS for...in Loop',
    'symbols': 'JS Symbols',
    'map-set': 'JS Map and Set',
    'weakmap-weakset': 'JS WeakMap/WeakSet',
    'proxy': 'JS Proxy Object',
    'reflect': 'JS Reflect API',
    'generators': 'JS Generators',
    'iterators': 'JS Iterators',
    'bigint': 'JS BigInt',
    'json': 'JSON Parsing',
    'strict-mode': 'JS Strict Mode',
    'object-values-entries': 'Object.values/entries',
    'object-observe': 'Object.observe',
    'array-includes': 'Array.includes',
    'array-flat': 'Array.flat/flatMap',
    'optional-chaining': 'JS Optional Chaining (?.)',
    'nullish-coalescing': 'JS Nullish Coalescing (??)',

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
    'canvas': 'HTML5 Canvas',
    'webgl': 'WebGL',
    'webgl2': 'WebGL 2.0',
    'picture': 'HTML Picture Element',
    'srcset': 'HTML srcset Attribute',
    'loading-lazy-attr': 'HTML loading="lazy" Attribute',
    'dialog': 'HTML Dialog Element',
    'details': 'HTML Details/Summary Elements',
    'datalist': 'HTML Datalist Element',
    'template': 'HTML Template Element',
    'meter': 'HTML Meter Element',
    'progress': 'HTML Progress Element',
    'output-element': 'HTML Output Element',
    'menu': 'HTML Menu Element',
    'ruby': 'HTML Ruby Annotations',
    'wbr-element': 'HTML wbr Element',
    'html5semantic': 'HTML5 Semantic Elements',
    'webvtt': 'WebVTT (Video Captions)',
    'input-color': 'HTML Color Input',
    'input-datetime': 'HTML Date/Time Inputs',
    'input-datetime-local': 'HTML datetime-local Input',
    'input-email-tel-url': 'HTML Email/Tel/URL Inputs',
    'input-number': 'HTML Number Input',
    'input-range': 'HTML Range Input',
    'input-search': 'HTML Search Input',
    'input-file-accept': 'HTML File Input Accept',
    'input-file-multiple': 'HTML File Input Multiple',
    'input-file-directory': 'HTML Directory Upload',
    'input-placeholder': 'HTML Placeholder Attribute',
    'input-pattern': 'HTML Pattern Attribute',
    'input-minlength': 'HTML minlength Attribute',
    'input-inputmode': 'HTML inputmode Attribute',
    'input-autocomplete-onoff': 'HTML Autocomplete Attribute',
    'form-validation': 'HTML5 Form Validation',
    'form-attribute': 'HTML form Attribute',
    'form-submit-attributes': 'HTML Form Submit Attributes',
    'autofocus': 'HTML autofocus Attribute',
    'maxlength': 'HTML maxlength Attribute',
    'contenteditable': 'HTML contenteditable',
    'dragndrop': 'HTML Drag and Drop',
    'spellcheck-attribute': 'HTML spellcheck Attribute',
    'hidden': 'HTML hidden Attribute',
    'download': 'HTML download Attribute',
    'ping': 'HTML ping Attribute',
    'script-async': 'HTML async Script',
    'script-defer': 'HTML defer Script',
    'iframe-sandbox': 'HTML iframe sandbox',
    'iframe-srcdoc': 'HTML iframe srcdoc',
    'ol-reversed': 'HTML ol reversed Attribute',
    'custom-elementsv1': 'Custom Elements v1',
    'shadowdomv1': 'Shadow DOM v1',
    'declarative-shadow-dom': 'Declarative Shadow DOM',

    # HTML Link Features
    'link-rel-preload': 'rel="preload"',
    'link-rel-prefetch': 'rel="prefetch"',
    'link-rel-dns-prefetch': 'rel="dns-prefetch"',
    'link-rel-preconnect': 'rel="preconnect"',
    'link-rel-modulepreload': 'rel="modulepreload"',
    'link-rel-prerender': 'rel="prerender"',
    'link-icon-png': 'PNG Favicon',
    'link-icon-svg': 'SVG Favicon',
    'rel-noopener': 'rel="noopener"',
    'rel-noreferrer': 'rel="noreferrer"',
    'referrer-policy': 'Referrer Policy',
    'permissions-policy': 'Permissions Policy',
    'html-media-capture': 'HTML Media Capture',

    # Touch & Pointer Events
    'touch': 'Touch Events',
    'pointer': 'Pointer Events',
    'focusin-focusout-events': 'focusin/focusout Events',
    'hashchange': 'Hashchange Event',
    'page-transition-events': 'Page Transition Events',
    'beforeafterprint': 'beforeprint/afterprint Events',
    'input-event': 'Input Event',

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
