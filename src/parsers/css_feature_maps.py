"""
CSS Feature Maps
Maps CSS properties, selectors, and features to Can I Use database feature IDs.
Organized by category for maintainability.
"""

# CSS Layout Features
CSS_LAYOUT_FEATURES = {
    'flexbox': {
        'patterns': [r'display\s*:\s*(?:inline-)?flex', r'flex-direction', r'flex-wrap', r'justify-content', r'align-items'],
        'keywords': ['flex', 'flexbox'],
        'description': 'CSS Flexible Box Layout Module'
    },
    'flexbox-gap': {
        'patterns': [r'gap\s*:', r'row-gap\s*:', r'column-gap\s*:'],
        'keywords': ['gap', 'flexbox gap'],
        'description': 'gap property for Flexbox'
    },
    'css-grid': {
        'patterns': [r'display\s*:\s*(?:inline-)?grid', r'grid-template', r'grid-column', r'grid-row', r'grid-area', r'grid-auto-columns', r'grid-auto-rows', r'grid-auto-flow'],
        'keywords': ['grid', 'css grid'],
        'description': 'CSS Grid Layout'
    },
    'multicolumn': {
        'patterns': [r'column-count', r'column-width', r'column-gap', r'column-rule', r'columns\s*:', r'column-span', r'column-fill'],
        'keywords': ['columns', 'multicolumn'],
        'description': 'CSS3 Multiple column layout'
    },
    'inline-block': {
        'patterns': [r'display\s*:\s*inline-block'],
        'keywords': ['inline-block'],
        'description': 'CSS inline-block'
    },
    'flow-root': {
        'patterns': [r'display\s*:\s*flow-root'],
        'keywords': ['flow-root'],
        'description': 'display: flow-root'
    },
    'run-in': {
        'patterns': [r'display\s*:\s*run-in'],
        'keywords': ['run-in'],
        'description': 'display: run-in'
    },
}

# CSS Transform & Animation Features
CSS_TRANSFORM_ANIMATION = {
    'transforms2d': {
        'patterns': [r'transform\s*:', r'translate\(', r'rotate\(', r'scale\(', r'skew\('],
        'keywords': ['transform', '2d transforms'],
        'description': 'CSS3 2D Transforms'
    },
    'transforms3d': {
        'patterns': [r'translate3d', r'translateZ', r'rotateX', r'rotateY', r'rotateZ', r'rotate3d', r'scale3d', r'scaleZ', r'perspective', r'transform-style', r'backface-visibility', r'matrix3d'],
        'keywords': ['3d transforms', 'perspective'],
        'description': 'CSS3 3D Transforms'
    },
    'css-animation': {
        'patterns': [r'@keyframes', r'animation\s*:', r'animation-name', r'animation-duration', r'animation-timing-function', r'animation-delay', r'animation-iteration-count', r'animation-direction', r'animation-fill-mode', r'animation-play-state'],
        'keywords': ['animation', 'keyframes'],
        'description': 'CSS3 Animation'
    },
    'css-transitions': {
        'patterns': [r'transition\s*:', r'transition-property', r'transition-duration', r'transition-timing-function', r'transition-delay'],
        'keywords': ['transition'],
        'description': 'CSS3 Transitions'
    },
    'will-change': {
        'patterns': [r'will-change\s*:'],
        'keywords': ['will-change'],
        'description': 'CSS will-change property'
    },
}

# CSS Color & Background Features
CSS_COLOR_BACKGROUND = {
    'css3-colors': {
        'patterns': [r'rgba?\(', r'hsla?\(', r'#[0-9a-fA-F]{6}'],
        'keywords': ['rgb', 'rgba', 'hsl', 'hsla'],
        'description': 'CSS3 Colors'
    },
    'currentcolor': {
        'patterns': [r'currentColor'],
        'keywords': ['currentColor'],
        'description': 'CSS currentColor value'
    },
    'css-gradients': {
        'patterns': [r'linear-gradient', r'radial-gradient', r'repeating-linear-gradient'],
        'keywords': ['gradient'],
        'description': 'CSS Gradients'
    },
    'multibackgrounds': {
        'patterns': [r'background.*,.*url', r'background-image.*,'],
        'keywords': ['multiple backgrounds'],
        'description': 'CSS3 Multiple backgrounds'
    },
    'background-img-opts': {
        'patterns': [r'background-size', r'background-origin', r'background-clip'],
        'keywords': ['background-size', 'cover', 'contain'],
        'description': 'CSS3 Background-image options'
    },
    'background-clip-text': {
        'patterns': [r'background-clip\s*:\s*text', r'-webkit-background-clip\s*:\s*text'],
        'keywords': ['background-clip: text'],
        'description': 'Background-clip: text'
    },
    'css-filter-function': {
        'patterns': [r'filter\s*:', r'blur\(', r'brightness\(', r'contrast\(', r'grayscale\('],
        'keywords': ['filter', 'blur', 'brightness'],
        'description': 'CSS Filter Effects'
    },
    'css-backdrop-filter': {
        'patterns': [r'backdrop-filter\s*:'],
        'keywords': ['backdrop-filter'],
        'description': 'CSS backdrop-filter'
    },
}

# CSS Typography Features
CSS_TYPOGRAPHY = {
    'fontface': {
        'patterns': [r'@font-face'],
        'keywords': ['font-face', 'web fonts'],
        'description': '@font-face Web fonts'
    },
    'woff': {
        'patterns': [r'\.woff', r'format\(["\']woff["\']'],
        'keywords': ['woff'],
        'description': 'WOFF - Web Open Font Format'
    },
    'woff2': {
        'patterns': [r'\.woff2', r'format\(["\']woff2["\']'],
        'keywords': ['woff2'],
        'description': 'WOFF 2.0 - Web Open Font Format'
    },
    'ttf': {
        'patterns': [r'\.ttf', r'\.otf', r'format\(["\']truetype["\']'],
        'keywords': ['ttf', 'otf'],
        'description': 'TTF/OTF - TrueType and OpenType font support'
    },
    'eot': {
        'patterns': [r'\.eot', r'format\s*\(\s*["\']embedded-opentype["\']'],
        'keywords': ['eot', 'embedded-opentype'],
        'description': 'EOT - Embedded OpenType fonts'
    },
    'colr': {
        'patterns': [r'format\s*\(\s*["\']colr["\']', r'font-technology\s*\(\s*colr\s*\)'],
        'keywords': ['colr'],
        'description': 'COLR/CPAL(v0) Font Formats'
    },
    'colr-v1': {
        'patterns': [r'format\s*\(\s*["\']colr-v1["\']', r'colr-v1'],
        'keywords': ['colr-v1'],
        'description': 'COLR/CPAL(v1) Font Formats'
    },
    'svg-fonts': {
        'patterns': [r'format\s*\(\s*["\']svg["\']', r'\.svg#'],
        'keywords': ['svg fonts'],
        'description': 'SVG fonts'
    },
    'variable-fonts': {
        'patterns': [r'font-variation-settings', r'font-optical-sizing'],
        'keywords': ['variable fonts'],
        'description': 'Variable fonts'
    },
    'font-feature': {
        'patterns': [r'font-feature-settings', r'font-variant-ligatures'],
        'keywords': ['font-feature-settings'],
        'description': 'CSS font-feature-settings'
    },
    'font-kerning': {
        'patterns': [r'font-kerning\s*:'],
        'keywords': ['font-kerning'],
        'description': 'CSS3 font-kerning'
    },
    'font-size-adjust': {
        'patterns': [r'font-size-adjust\s*:'],
        'keywords': ['font-size-adjust'],
        'description': 'CSS font-size-adjust'
    },
    'font-smooth': {
        'patterns': [r'-webkit-font-smoothing', r'-moz-osx-font-smoothing'],
        'keywords': ['font-smoothing'],
        'description': 'CSS font-smooth'
    },
    'font-variant-alternates': {
        'patterns': [r'font-variant-alternates\s*:'],
        'keywords': ['font-variant-alternates'],
        'description': 'CSS font-variant-alternates'
    },
    'font-variant-numeric': {
        'patterns': [r'font-variant-numeric\s*:'],
        'keywords': ['font-variant-numeric'],
        'description': 'CSS font-variant-numeric'
    },
    'font-unicode-range': {
        'patterns': [r'unicode-range\s*:'],
        'keywords': ['unicode-range'],
        'description': 'Font unicode-range subsetting'
    },
    'font-family-system-ui': {
        'patterns': [r'font-family.*system-ui'],
        'keywords': ['system-ui'],
        'description': 'system-ui value for font-family'
    },
    'extended-system-fonts': {
        'patterns': [r'ui-serif', r'ui-sans-serif', r'ui-monospace', r'ui-rounded'],
        'keywords': ['ui-serif', 'ui-sans-serif'],
        'description': 'ui-serif, ui-sans-serif, ui-monospace and ui-rounded values for font-family'
    },
    'text-overflow': {
        'patterns': [r'text-overflow\s*:'],
        'keywords': ['text-overflow', 'ellipsis'],
        'description': 'CSS3 Text-overflow'
    },
    'text-decoration': {
        'patterns': [r'text-decoration-line', r'text-decoration-style', r'text-decoration-color', r'text-decoration-thickness', r'text-underline-offset'],
        'keywords': ['text-decoration'],
        'description': 'text-decoration styling'
    },
    'text-emphasis': {
        'patterns': [r'text-emphasis', r'text-emphasis-style'],
        'keywords': ['text-emphasis'],
        'description': 'text-emphasis styling'
    },
    'text-stroke': {
        'patterns': [r'-webkit-text-stroke', r'text-stroke'],
        'keywords': ['text-stroke'],
        'description': 'CSS text-stroke and text-fill'
    },
    'text-size-adjust': {
        'patterns': [r'text-size-adjust\s*:'],
        'keywords': ['text-size-adjust'],
        'description': 'CSS text-size-adjust'
    },
    'word-break': {
        'patterns': [r'word-break\s*:'],
        'keywords': ['word-break'],
        'description': 'CSS3 word-break'
    },
    'wordwrap': {
        'patterns': [r'word-wrap\s*:', r'overflow-wrap\s*:'],
        'keywords': ['word-wrap', 'overflow-wrap'],
        'description': 'CSS3 Overflow-wrap'
    },
    'css3-tabsize': {
        'patterns': [r'tab-size\s*:'],
        'keywords': ['tab-size'],
        'description': 'CSS3 tab-size'
    },
}

# CSS Box Model & Sizing Features
CSS_BOX_MODEL = {
    'css3-boxsizing': {
        'patterns': [r'box-sizing\s*:\s*border-box', r'box-sizing\s*:\s*content-box'],
        'keywords': ['box-sizing', 'border-box'],
        'description': 'CSS3 Box-sizing'
    },
    'minmaxwh': {
        'patterns': [r'min-width\s*:', r'min-height\s*:', r'max-width\s*:', r'max-height\s*:'],
        'keywords': ['min-width', 'max-width'],
        'description': 'CSS min/max-width/height'
    },
    'intrinsic-width': {
        'patterns': [r'width\s*:\s*min-content', r'width\s*:\s*max-content', r'width\s*:\s*fit-content'],
        'keywords': ['min-content', 'max-content', 'fit-content'],
        'description': 'Intrinsic & Extrinsic Sizing'
    },
    'object-fit': {
        'patterns': [r'object-fit\s*:', r'object-position\s*:'],
        'keywords': ['object-fit', 'object-position'],
        'description': 'CSS3 object-fit/object-position'
    },
}

# CSS Border & Outline Features
CSS_BORDER_OUTLINE = {
    'border-image': {
        'patterns': [r'border-image\s*:', r'border-image-source'],
        'keywords': ['border-image'],
        'description': 'CSS3 Border images'
    },
    'border-radius': {
        'patterns': [r'border-radius\s*:'],
        'keywords': ['border-radius', 'rounded corners'],
        'description': 'CSS3 Border-radius (rounded corners)'
    },
    'outline': {
        'patterns': [r'outline\s*:', r'outline-width', r'outline-style', r'outline-color', r'outline-offset'],
        'keywords': ['outline'],
        'description': 'CSS outline properties'
    },
    'css-boxdecorationbreak': {
        'patterns': [r'box-decoration-break\s*:'],
        'keywords': ['box-decoration-break'],
        'description': 'CSS box-decoration-break'
    },
}

# CSS Shadow & Effects Features
CSS_SHADOW_EFFECTS = {
    'css-boxshadow': {
        'patterns': [r'box-shadow\s*:'],
        'keywords': ['box-shadow'],
        'description': 'CSS3 Box-shadow'
    },
    'css-textshadow': {
        'patterns': [r'text-shadow\s*:'],
        'keywords': ['text-shadow'],
        'description': 'CSS3 Text-shadow'
    },
    'css-mixblendmode': {
        'patterns': [r'mix-blend-mode\s*:'],
        'keywords': ['mix-blend-mode'],
        'description': 'Blending of HTML/SVG elements'
    },
}

# CSS Selectors Features
CSS_SELECTORS = {
    'css-sel2': {
        'patterns': [r'\[.*\]', r':hover', r':active', r':focus'],
        'keywords': ['CSS 2.1 selectors'],
        'description': 'CSS 2.1 selectors'
    },
    'css-sel3': {
        'patterns': [r':nth-child', r':nth-of-type', r':nth-last-child', r':nth-last-of-type', r':first-of-type', r':last-of-type', r':only-child', r':only-of-type', r':empty', r':not\('],
        'keywords': ['nth-child', 'nth-of-type'],
        'description': 'CSS3 selectors'
    },
    'css-gencontent': {
        'patterns': [r'::before', r'::after', r':before', r':after', r'content\s*:'],
        'keywords': ['::before', '::after', 'content'],
        'description': 'CSS Generated content for pseudo-elements'
    },
    'css-first-letter': {
        'patterns': [r'::first-letter', r':first-letter'],
        'keywords': ['first-letter'],
        'description': 'CSS ::first-letter'
    },
    'css-first-line': {
        'patterns': [r'::first-line', r':first-line'],
        'keywords': ['first-line'],
        'description': 'CSS ::first-line'
    },
    'css-selection': {
        'patterns': [r'::selection'],
        'keywords': ['::selection'],
        'description': 'CSS ::selection'
    },
    'css-placeholder': {
        'patterns': [r'::placeholder', r'::-webkit-input-placeholder'],
        'keywords': ['placeholder'],
        'description': 'CSS ::placeholder'
    },
    'css-marker-pseudo': {
        'patterns': [r'::marker'],
        'keywords': ['::marker'],
        'description': 'CSS ::marker pseudo-element'
    },
    'css-case-insensitive': {
        'patterns': [r'\[.*\si\]'],
        'keywords': ['case-insensitive'],
        'description': 'Case-insensitive CSS attribute selectors'
    },
    'css-optional-pseudo': {
        'patterns': [r':optional', r':required'],
        'keywords': ['optional', 'required'],
        'description': 'CSS :optional and :required pseudo-classes'
    },
    'css-placeholder-shown': {
        'patterns': [r':placeholder-shown'],
        'keywords': ['placeholder-shown'],
        'description': 'CSS :placeholder-shown'
    },
    'css-default-pseudo': {
        'patterns': [r':default'],
        'keywords': ['default'],
        'description': 'CSS :default pseudo-class'
    },
    'css-indeterminate-pseudo': {
        'patterns': [r':indeterminate'],
        'keywords': ['indeterminate'],
        'description': 'CSS :indeterminate pseudo-class'
    },
    'css-dir-pseudo': {
        'patterns': [r':dir\('],
        'keywords': ['dir'],
        'description': 'CSS :dir() pseudo-class'
    },
    'css-any-link': {
        'patterns': [r':any-link'],
        'keywords': ['any-link'],
        'description': 'CSS :any-link selector'
    },
    'css-read-only-write': {
        'patterns': [r':read-only', r':read-write'],
        'keywords': ['read-only', 'read-write'],
        'description': 'CSS :read-only and :read-write selectors'
    },
    'css-cascade-scope': {
        'patterns': [r':scope'],
        'keywords': ['scope'],
        'description': 'CSS :scope pseudo-class'
    },
    'css-matches-pseudo': {
        'patterns': [r':is\(', r':matches\(', r':where\('],
        'keywords': ['is', 'matches', 'where'],
        'description': 'CSS :is(), :matches(), :where() pseudo-classes'
    },
    'css-has': {
        'patterns': [r':has\('],
        'keywords': ['has'],
        'description': 'CSS :has() relational pseudo-class'
    },
    'css-focus-within': {
        'patterns': [r':focus-within'],
        'keywords': ['focus-within'],
        'description': 'CSS :focus-within pseudo-class'
    },
    'css-focus-visible': {
        'patterns': [r':focus-visible'],
        'keywords': ['focus-visible'],
        'description': 'CSS :focus-visible pseudo-class'
    },
}

# CSS Media Queries Features
CSS_MEDIA_QUERIES = {
    'css-mediaqueries': {
        'patterns': [r'@media', r'min-width', r'max-width'],
        'keywords': ['media queries'],
        'description': 'CSS3 Media Queries'
    },
    'prefers-color-scheme': {
        'patterns': [r'prefers-color-scheme'],
        'keywords': ['prefers-color-scheme', 'dark mode'],
        'description': 'prefers-color-scheme media query'
    },
    'prefers-reduced-motion': {
        'patterns': [r'prefers-reduced-motion'],
        'keywords': ['prefers-reduced-motion'],
        'description': 'prefers-reduced-motion media query'
    },
    'css-media-resolution': {
        'patterns': [r'min-resolution', r'max-resolution'],
        'keywords': ['resolution'],
        'description': 'Media Queries: resolution feature'
    },
    'css-media-range-syntax': {
        'patterns': [r'@media.*[<>=]'],
        'keywords': ['range syntax'],
        'description': 'Media Queries: Range Syntax'
    },
}

# CSS Units Features
CSS_UNITS = {
    'rem': {
        'patterns': [r'\d+\.?\d*rem'],
        'keywords': ['rem'],
        'description': 'rem (root em) units'
    },
    'viewport-units': {
        'patterns': [r'\d+\.?\d*vw', r'\d+\.?\d*vh', r'\d+\.?\d*vmin', r'\d+\.?\d*vmax'],
        'keywords': ['vw', 'vh', 'vmin', 'vmax'],
        'description': 'Viewport units: vw, vh, vmin, vmax'
    },
    'viewport-unit-variants': {
        'patterns': [r'svw', r'svh', r'lvw', r'lvh', r'dvw', r'dvh'],
        'keywords': ['svw', 'lvw', 'dvw'],
        'description': 'Small, Large, and Dynamic viewport units'
    },
    'calc': {
        'patterns': [r'calc\('],
        'keywords': ['calc'],
        'description': 'CSS calc() function'
    },
    'ch-unit': {
        'patterns': [r'\d+\.?\d*ch'],
        'keywords': ['ch unit'],
        'description': 'CSS ch unit'
    },
}

# CSS Variables & Custom Properties
CSS_VARIABLES = {
    'css-variables': {
        'patterns': [r'--[\w-]+', r'var\(--'],
        'keywords': ['css variables', 'custom properties', 'var()'],
        'description': 'CSS Variables (Custom Properties)'
    },
}

# CSS At-Rules Features
CSS_AT_RULES = {
    'css-featurequeries': {
        'patterns': [r'@supports'],
        'keywords': ['@supports', 'feature queries'],
        'description': 'CSS Feature Queries'
    },
    'css-counters': {
        'patterns': [r'counter-reset', r'counter-increment', r'counter\(', r'counters\('],
        'keywords': ['counter'],
        'description': 'CSS Counters'
    },
    'css-page-break': {
        'patterns': [r'page-break-before', r'page-break-after', r'page-break-inside'],
        'keywords': ['page-break'],
        'description': 'CSS page-break properties'
    },
    'css-paged-media': {
        'patterns': [r'@page'],
        'keywords': ['@page'],
        'description': 'CSS Paged Media (@page)'
    },
    'css-when-else': {
        'patterns': [r'@when', r'@else'],
        'keywords': ['@when', '@else'],
        'description': 'CSS @when / @else conditional rules'
    },
}

# CSS Positioning & Display Features
CSS_POSITIONING = {
    'css-sticky': {
        'patterns': [r'position\s*:\s*sticky'],
        'keywords': ['sticky'],
        'description': 'CSS position: sticky'
    },
    'css-fixed': {
        'patterns': [r'position\s*:\s*fixed'],
        'keywords': ['fixed'],
        'description': 'CSS position: fixed'
    },
    'css-table': {
        'patterns': [r'display\s*:\s*table', r'display\s*:\s*table-cell'],
        'keywords': ['display: table'],
        'description': 'CSS Table display'
    },
}

# CSS Overflow & Clipping Features
CSS_OVERFLOW = {
    'css-overflow': {
        'patterns': [r'overflow\s*:', r'overflow-x\s*:', r'overflow-y\s*:'],
        'keywords': ['overflow'],
        'description': 'CSS overflow property'
    },
    'css-overflow-anchor': {
        'patterns': [r'overflow-anchor\s*:'],
        'keywords': ['overflow-anchor'],
        'description': 'CSS overflow-anchor (Scroll Anchoring)'
    },
    'css-clip-path': {
        'patterns': [r'clip-path\s*:'],
        'keywords': ['clip-path'],
        'description': 'CSS clip-path property (for HTML)'
    },
}

# CSS Interaction Features
CSS_INTERACTION = {
    'css-resize': {
        'patterns': [r'resize\s*:'],
        'keywords': ['resize'],
        'description': 'CSS resize property'
    },
    'pointer-events': {
        'patterns': [r'pointer-events\s*:'],
        'keywords': ['pointer-events'],
        'description': 'CSS pointer-events (for HTML)'
    },
    'user-select-none': {
        'patterns': [r'user-select\s*:\s*none', r'-webkit-user-select'],
        'keywords': ['user-select'],
        'description': 'CSS user-select: none'
    },
    'css-appearance': {
        'patterns': [r'appearance\s*:', r'-webkit-appearance'],
        'keywords': ['appearance'],
        'description': 'CSS appearance property'
    },
    'css-caret-color': {
        'patterns': [r'caret-color\s*:'],
        'keywords': ['caret-color'],
        'description': 'CSS caret-color'
    },
    'css-touch-action': {
        'patterns': [r'touch-action\s*:'],
        'keywords': ['touch-action'],
        'description': 'CSS touch-action property'
    },
    'css-scroll-behavior': {
        'patterns': [r'scroll-behavior\s*:'],
        'keywords': ['scroll-behavior'],
        'description': 'CSS scroll-behavior'
    },
    'css3-cursors': {
        'patterns': [r'cursor\s*:'],
        'keywords': ['cursor'],
        'description': 'CSS3 Cursors (original values)'
    },
    'css3-cursors-grab': {
        'patterns': [r'cursor\s*:\s*grab', r'cursor\s*:\s*grabbing'],
        'keywords': ['grab', 'grabbing'],
        'description': 'CSS grab & grabbing cursors'
    },
    'css3-cursors-newer': {
        'patterns': [r'cursor\s*:\s*zoom-in', r'cursor\s*:\s*zoom-out'],
        'keywords': ['zoom-in', 'zoom-out'],
        'description': 'CSS3 Cursors: zoom-in & zoom-out'
    },
}

# CSS Miscellaneous Features
CSS_MISC = {
    'css-opacity': {
        'patterns': [r'opacity\s*:'],
        'keywords': ['opacity'],
        'description': 'CSS3 Opacity'
    },
    'css-zoom': {
        'patterns': [r'zoom\s*:'],
        'keywords': ['zoom'],
        'description': 'CSS zoom'
    },
    'css-all': {
        'patterns': [r'all\s*:'],
        'keywords': ['all'],
        'description': 'CSS all property'
    },
    'css-unset-value': {
        'patterns': [r':\s*unset'],
        'keywords': ['unset'],
        'description': 'CSS unset value'
    },
    'css-initial-value': {
        'patterns': [r':\s*initial'],
        'keywords': ['initial'],
        'description': 'CSS initial value'
    },
    'css-revert-value': {
        'patterns': [r':\s*revert'],
        'keywords': ['revert'],
        'description': 'CSS revert value'
    },
    'css-widows-orphans': {
        'patterns': [r'widows\s*:', r'orphans\s*:'],
        'keywords': ['widows', 'orphans'],
        'description': 'CSS widows & orphans'
    },
    'css-writing-mode': {
        'patterns': [r'writing-mode\s*:'],
        'keywords': ['writing-mode'],
        'description': 'CSS writing-mode property'
    },
    'css-logical-props': {
        'patterns': [r'margin-inline', r'padding-block', r'inset-inline'],
        'keywords': ['logical properties'],
        'description': 'CSS Logical Properties'
    },
    'css-color-adjust': {
        'patterns': [r'print-color-adjust\s*:', r'color-adjust\s*:'],
        'keywords': ['print-color-adjust', 'color-adjust'],
        'description': 'CSS color-adjust/print-color-adjust'
    },
    'css-image-set': {
        'patterns': [r'image-set\('],
        'keywords': ['image-set'],
        'description': 'CSS image-set'
    },
    'css-element-function': {
        'patterns': [r'element\('],
        'keywords': ['element()'],
        'description': 'CSS element() function'
    },
    'css-cross-fade': {
        'patterns': [r'cross-fade\('],
        'keywords': ['cross-fade'],
        'description': 'CSS cross-fade() function'
    },
    'css-crisp-edges': {
        'patterns': [r'image-rendering\s*:\s*crisp-edges', r'image-rendering\s*:\s*pixelated'],
        'keywords': ['crisp-edges', 'pixelated'],
        'description': 'CSS image-rendering: crisp-edges/pixelated'
    },
    'css-unicode-bidi': {
        'patterns': [r'unicode-bidi\s*:'],
        'keywords': ['unicode-bidi'],
        'description': 'CSS unicode-bidi property'
    },
    'css3-attr': {
        'patterns': [r'attr\('],
        'keywords': ['attr()'],
        'description': 'CSS3 attr() function for all properties'
    },
    'kerning-pairs-ligatures': {
        'patterns': [r'text-rendering\s*:\s*optimizeLegibility'],
        'keywords': ['optimizeLegibility'],
        'description': 'High-quality kerning pairs & ligatures'
    },
    'justify-content-space-evenly': {
        'patterns': [r'justify-content\s*:\s*space-evenly'],
        'keywords': ['space-evenly'],
        'description': 'CSS justify-content: space-evenly'
    },
    'background-position-x-y': {
        'patterns': [r'background-position-x', r'background-position-y'],
        'keywords': ['background-position-x'],
        'description': 'background-position-x & background-position-y'
    },
    'background-repeat-round-space': {
        'patterns': [r'background-repeat\s*:\s*round', r'background-repeat\s*:\s*space'],
        'keywords': ['round', 'space'],
        'description': 'CSS background-repeat round and space'
    },
    'background-attachment': {
        'patterns': [r'background-attachment\s*:'],
        'keywords': ['background-attachment'],
        'description': 'CSS background-attachment'
    },
    'webkit-user-drag': {
        'patterns': [r'-webkit-user-drag\s*:'],
        'keywords': ['webkit-user-drag'],
        'description': 'CSS -webkit-user-drag property'
    },
}

# CSS Container Queries
CSS_CONTAINER = {
    'css-container-queries': {
        'patterns': [r'@container', r'container-type\s*:', r'container-name\s*:'],
        'keywords': ['container queries'],
        'description': 'CSS Container Queries'
    },
    'css-container-query-units': {
        'patterns': [r'cqw', r'cqh', r'cqi', r'cqb'],
        'keywords': ['cqw', 'cqh'],
        'description': 'CSS Container Query Units'
    },
}

# CSS Subgrid
CSS_SUBGRID = {
    'css-subgrid': {
        'patterns': [r'grid-template-columns\s*:\s*subgrid', r'grid-template-rows\s*:\s*subgrid'],
        'keywords': ['subgrid'],
        'description': 'CSS Subgrid'
    },
}

# CSS Cascade Layers
CSS_CASCADE = {
    'css-cascade-layers': {
        'patterns': [r'@layer'],
        'keywords': ['@layer', 'cascade layers'],
        'description': 'CSS Cascade Layers'
    },
}

# CSS Nesting
CSS_NESTING = {
    'css-nesting': {
        'patterns': [r'&\s*{', r'&:hover', r'&\s+\.'],
        'keywords': ['nesting', '&'],
        'description': 'CSS Nesting'
    },
}

# CSS Additional Features (Part 1)
CSS_ADDITIONAL_1 = {
    'css-anchor-positioning': {
        'patterns': [r'anchor-name\s*:', r'position-anchor\s*:', r'anchor\('],
        'keywords': ['anchor', 'anchor-name'],
        'description': 'CSS Anchor Positioning'
    },
    'css-at-counter-style': {
        'patterns': [r'@counter-style'],
        'keywords': ['@counter-style'],
        'description': 'CSS Counter Styles'
    },
    'css-background-offsets': {
        'patterns': [r'background-position.*\s+from\s+'],
        'keywords': ['background-position offsets'],
        'description': 'CSS background-position edge offsets'
    },
    'css-backgroundblendmode': {
        'patterns': [r'background-blend-mode\s*:'],
        'keywords': ['background-blend-mode'],
        'description': 'CSS background-blend-mode'
    },
    'css-canvas': {
        'patterns': [r'-webkit-canvas\('],
        'keywords': ['canvas()'],
        'description': 'CSS Canvas Drawings'
    },
    'css-cascade-scope': {
        'patterns': [r'@scope'],
        'keywords': ['@scope'],
        'description': 'Scoped Styles: the @scope rule'
    },
    'css-color-adjust': {
        'patterns': [r'color-adjust\s*:', r'print-color-adjust\s*:'],
        'keywords': ['color-adjust'],
        'description': 'CSS print-color-adjust'
    },
    'css-color-function': {
        'patterns': [r'color\('],
        'keywords': ['color()'],
        'description': 'CSS color() function'
    },
    'css-conic-gradients': {
        'patterns': [r'conic-gradient\(', r'repeating-conic-gradient\('],
        'keywords': ['conic-gradient'],
        'description': 'CSS Conical Gradients'
    },
    'css-container-queries-style': {
        'patterns': [r'@container\s+style\('],
        'keywords': ['style query'],
        'description': 'CSS Container Style Queries'
    },
    'css-containment': {
        'patterns': [r'contain\s*:'],
        'keywords': ['contain'],
        'description': 'CSS Containment'
    },
    'css-content-visibility': {
        'patterns': [r'content-visibility\s*:'],
        'keywords': ['content-visibility'],
        'description': 'CSS content-visibility'
    },
    'css-descendant-gtgt': {
        'patterns': [r'>>'],
        'keywords': ['>>'],
        'description': 'Explicit descendant combinator >>'
    },
    'css-deviceadaptation': {
        'patterns': [r'@viewport'],
        'keywords': ['@viewport'],
        'description': 'CSS Device Adaptation'
    },
    'css-display-contents': {
        'patterns': [r'display\s*:\s*contents'],
        'keywords': ['display: contents'],
        'description': 'CSS display: contents'
    },
    'css-env-function': {
        'patterns': [r'env\('],
        'keywords': ['env()'],
        'description': 'CSS Environment Variables env()'
    },
    'css-exclusions': {
        'patterns': [r'wrap-flow\s*:', r'wrap-through\s*:'],
        'keywords': ['wrap-flow'],
        'description': 'CSS Exclusions Level 1'
    },
    'css-filters': {
        'patterns': [r'filter\s*:'],
        'keywords': ['filter'],
        'description': 'CSS Filter Effects'
    },
    'css-font-palette': {
        'patterns': [r'font-palette\s*:'],
        'keywords': ['font-palette'],
        'description': 'CSS font-palette'
    },
    'css-font-rendering-controls': {
        'patterns': [r'font-display\s*:'],
        'keywords': ['font-display'],
        'description': 'CSS font-display'
    },
}

# CSS Additional Features (Part 2)
CSS_ADDITIONAL_2 = {
    'css-font-stretch': {
        'patterns': [r'font-stretch\s*:'],
        'keywords': ['font-stretch'],
        'description': 'CSS font-stretch'
    },
    'css-grid-animation': {
        'patterns': [r'grid-template.*transition', r'grid.*animation'],
        'keywords': ['grid animation'],
        'description': 'CSS Grid animation'
    },
    'css-hanging-punctuation': {
        'patterns': [r'hanging-punctuation\s*:'],
        'keywords': ['hanging-punctuation'],
        'description': 'CSS hanging-punctuation'
    },
    'css-hyphens': {
        'patterns': [r'hyphens\s*:'],
        'keywords': ['hyphens'],
        'description': 'CSS Hyphenation'
    },
    'css-if': {
        'patterns': [r'if\('],
        'keywords': ['if()'],
        'description': 'CSS if() function'
    },
    'css-image-orientation': {
        'patterns': [r'image-orientation\s*:'],
        'keywords': ['image-orientation'],
        'description': 'CSS3 image-orientation'
    },
    'css-in-out-of-range': {
        'patterns': [r':in-range', r':out-of-range'],
        'keywords': ['in-range', 'out-of-range'],
        'description': ':in-range and :out-of-range CSS pseudo-classes'
    },
    'css-initial-letter': {
        'patterns': [r'initial-letter\s*:'],
        'keywords': ['initial-letter'],
        'description': 'CSS Initial Letter'
    },
    'css-lch-lab': {
        'patterns': [r'lch\(', r'lab\('],
        'keywords': ['lch', 'lab'],
        'description': 'LCH and Lab color values'
    },
    'css-letter-spacing': {
        'patterns': [r'letter-spacing\s*:'],
        'keywords': ['letter-spacing'],
        'description': 'letter-spacing CSS property'
    },
    'css-line-clamp': {
        'patterns': [r'line-clamp\s*:', r'-webkit-line-clamp\s*:'],
        'keywords': ['line-clamp'],
        'description': 'CSS line-clamp'
    },
    'css-masks': {
        'patterns': [r'mask\s*:', r'mask-image\s*:', r'mask-border\s*:'],
        'keywords': ['mask'],
        'description': 'CSS Masks'
    },
    'css-math-functions': {
        'patterns': [r'min\(', r'max\(', r'clamp\('],
        'keywords': ['min()', 'max()', 'clamp()'],
        'description': 'CSS math functions min(), max() and clamp()'
    },
    'css-media-interaction': {
        'patterns': [r'@media.*hover', r'@media.*pointer'],
        'keywords': ['hover', 'pointer'],
        'description': 'Media Queries: interaction media features'
    },
    'css-media-scripting': {
        'patterns': [r'@media.*scripting'],
        'keywords': ['scripting'],
        'description': 'Media Queries: scripting media feature'
    },
    'css-motion-paths': {
        'patterns': [r'offset-path\s*:', r'offset-distance\s*:', r'offset-rotate\s*:'],
        'keywords': ['offset-path'],
        'description': 'CSS Motion Path'
    },
    'css-namespaces': {
        'patterns': [r'@namespace'],
        'keywords': ['@namespace'],
        'description': 'CSS namespaces'
    },
    'css-not-sel-list': {
        'patterns': [r':not\([^)]*,'],
        'keywords': [':not() list'],
        'description': 'selector list argument of :not()'
    },
    'css-nth-child-of': {
        'patterns': [r':nth-child\([^)]*of\s+'],
        'keywords': [':nth-child of'],
        'description': 'selector list argument of :nth-child and :nth-last-child CSS'
    },
    'css-overflow-overlay': {
        'patterns': [r'overflow\s*:\s*overlay'],
        'keywords': ['overflow: overlay'],
        'description': 'CSS overflow: overlay'
    },
}

# CSS Additional Features (Part 3)
CSS_ADDITIONAL_3 = {
    'css-overscroll-behavior': {
        'patterns': [r'overscroll-behavior(?:-[xy])?\s*:'],
        'keywords': ['overscroll-behavior'],
        'description': 'CSS overscroll-behavior'
    },
    'css-paint-api': {
        'patterns': [r'paint\(', r'CSS\.paintWorklet'],
        'keywords': ['paint()'],
        'description': 'CSS Painting API'
    },
    'css-rebeccapurple': {
        'patterns': [r'rebeccapurple'],
        'keywords': ['rebeccapurple'],
        'description': 'Rebeccapurple color'
    },
    'css-reflections': {
        'patterns': [r'-webkit-box-reflect\s*:'],
        'keywords': ['box-reflect'],
        'description': 'CSS Reflections'
    },
    'css-regions': {
        'patterns': [r'flow-into\s*:', r'flow-from\s*:'],
        'keywords': ['regions'],
        'description': 'CSS Regions'
    },
    'css-relative-colors': {
        'patterns': [r'from\s+'],
        'keywords': ['relative colors'],
        'description': 'CSS Relative color syntax'
    },
    'css-repeating-gradients': {
        'patterns': [r'repeating-linear-gradient\(', r'repeating-radial-gradient\('],
        'keywords': ['repeating-linear-gradient'],
        'description': 'CSS Repeating Gradients'
    },
    'css-rrggbbaa': {
        'patterns': [r'#[0-9a-fA-F]{8}'],
        'keywords': ['#rrggbbaa'],
        'description': '#rrggbbaa hex color notation'
    },
    'css-scrollbar': {
        'patterns': [r'scrollbar-width\s*:', r'scrollbar-color\s*:'],
        'keywords': ['scrollbar'],
        'description': 'CSS scrollbar styling'
    },
    'css-shapes': {
        'patterns': [r'shape-outside\s*:', r'shape-margin\s*:', r'circle\(', r'polygon\('],
        'keywords': ['shape-outside'],
        'description': 'CSS Shapes Level 1'
    },
    'css-snappoints': {
        'patterns': [r'scroll-snap-type\s*:', r'scroll-snap-align\s*:', r'scroll-snap-stop\s*:'],
        'keywords': ['scroll-snap'],
        'description': 'CSS Scroll Snap'
    },
    'css-text-align-last': {
        'patterns': [r'text-align-last\s*:'],
        'keywords': ['text-align-last'],
        'description': 'CSS3 text-align-last'
    },
    'css-text-box-trim': {
        'patterns': [r'text-box-trim\s*:', r'leading-trim\s*:'],
        'keywords': ['text-box-trim'],
        'description': 'CSS Text Box'
    },
    'css-text-indent': {
        'patterns': [r'text-indent\s*:'],
        'keywords': ['text-indent'],
        'description': 'CSS text-indent'
    },
    'css-text-justify': {
        'patterns': [r'text-justify\s*:'],
        'keywords': ['text-justify'],
        'description': 'CSS text-justify'
    },
    'css-text-orientation': {
        'patterns': [r'text-orientation\s*:'],
        'keywords': ['text-orientation'],
        'description': 'CSS text-orientation'
    },
    'css-text-spacing': {
        'patterns': [r'text-spacing\s*:'],
        'keywords': ['text-spacing'],
        'description': 'CSS Text 4 text-spacing'
    },
    'css-text-wrap-balance': {
        'patterns': [r'text-wrap\s*:\s*balance'],
        'keywords': ['text-wrap: balance'],
        'description': 'CSS text-wrap: balance'
    },
    'devicepixelratio': {
        'patterns': [r'window\.devicePixelRatio', r'devicePixelRatio'],
        'keywords': ['devicePixelRatio'],
        'description': 'Window.devicePixelRatio'
    },
    'font-loading': {
        'patterns': [r'document\.fonts', r'FontFace', r'FontFaceSet'],
        'keywords': ['FontFace'],
        'description': 'CSS Font Loading'
    },
    'fullscreen': {
        'patterns': [r'requestFullscreen', r'exitFullscreen', r':fullscreen'],
        'keywords': ['fullscreen'],
        'description': 'Fullscreen API'
    },
    'getcomputedstyle': {
        'patterns': [r'getComputedStyle\s*\(', r'window\.getComputedStyle'],
        'keywords': ['getComputedStyle'],
        'description': 'getComputedStyle'
    },
    'pointer': {
        'patterns': [r'PointerEvent', r'pointerdown', r'pointermove'],
        'keywords': ['pointer events'],
        'description': 'Pointer events'
    },
    'style-scoped': {
        'patterns': [r'<style scoped', r'scoped\s+style'],
        'keywords': ['scoped'],
        'description': 'Scoped attribute'
    },
    'svg-css': {
        'patterns': [r'background.*\.svg', r'background-image.*svg'],
        'keywords': ['svg background'],
        'description': 'SVG in CSS backgrounds'
    },
    'view-transitions': {
        'patterns': [r'startViewTransition', r'ViewTransition', r'::view-transition-old', r'::view-transition-new', r'::view-transition-group', r'::view-transition-image-pair'],
        'keywords': ['ViewTransition'],
        'description': 'View Transitions API (single-document)'
    },
    'cross-document-view-transitions': {
        'patterns': [r'@view-transition', r'view-transition-name\s*:'],
        'keywords': ['cross-document view transitions'],
        'description': 'View Transitions (cross-document)'
    },
}

# All CSS features combined for quick lookup
ALL_CSS_FEATURES = {
    **CSS_LAYOUT_FEATURES,
    **CSS_TRANSFORM_ANIMATION,
    **CSS_COLOR_BACKGROUND,
    **CSS_TYPOGRAPHY,
    **CSS_BOX_MODEL,
    **CSS_BORDER_OUTLINE,
    **CSS_SHADOW_EFFECTS,
    **CSS_SELECTORS,
    **CSS_MEDIA_QUERIES,
    **CSS_UNITS,
    **CSS_VARIABLES,
    **CSS_AT_RULES,
    **CSS_POSITIONING,
    **CSS_OVERFLOW,
    **CSS_INTERACTION,
    **CSS_MISC,
    **CSS_CONTAINER,
    **CSS_SUBGRID,
    **CSS_CASCADE,
    **CSS_NESTING,
    **CSS_ADDITIONAL_1,
    **CSS_ADDITIONAL_2,
    **CSS_ADDITIONAL_3,
}
