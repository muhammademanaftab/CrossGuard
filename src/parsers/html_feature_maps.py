"""HTML Feature mapping dictionaries.

Maps detected HTML elements, attributes, and input types to Can I Use feature IDs.
All feature IDs are verified against the Can I Use database.
"""

# HTML Element to Feature ID mapping
HTML_ELEMENTS = {
    # Modern HTML5 elements
    'dialog': 'dialog',
    'details': 'details',
    'summary': 'details',  # Part of details element
    'template': 'template',
    'picture': 'picture',
    # Note: 'source' is NOT mapped here because it's used in video/audio too
    # The 'picture' feature is detected when <picture> element is found
    'track': 'webvtt',  # Track element for captions (maps to WebVTT)
    'video': 'video',
    'audio': 'audio',
    'canvas': 'canvas',
    'svg': 'svg',
    'meter': 'meter',
    'progress': 'progress',
    'datalist': 'datalist',
    'output': 'output-element',  # Output element for form calculations
    'time': 'html5semantic',
    'mark': 'html5semantic',
    'main': 'html5semantic',
    'section': 'html5semantic',
    'article': 'html5semantic',
    'aside': 'html5semantic',
    'header': 'html5semantic',
    'footer': 'html5semantic',
    'nav': 'html5semantic',
    'figure': 'html5semantic',
    'figcaption': 'html5semantic',
    'slot': 'shadowdomv1',  # Shadow DOM slots
    'wbr': 'wbr-element',  # Word break opportunity
    'ruby': 'ruby',  # Ruby annotations
    'rt': 'ruby',  # Ruby text
    'rp': 'ruby',  # Ruby parentheses
    'rb': 'ruby',  # Ruby base
    'rtc': 'ruby',  # Ruby text container
    'menu': 'menu',  # Menu element
    'portal': 'portals',  # Portal element for prerendering
}

# HTML Input Types to Feature ID mapping
HTML_INPUT_TYPES = {
    'date': 'input-datetime',
    'datetime-local': 'input-datetime',
    'time': 'input-datetime',
    'month': 'input-datetime',
    'week': 'input-datetime',
    'color': 'input-color',
    'range': 'input-range',
    'search': 'input-search',
    'tel': 'input-email-tel-url',
    'url': 'input-email-tel-url',
    'email': 'input-email-tel-url',
    'number': 'input-number',
    'file': 'input-file-accept',
}

# HTML Attributes to Feature ID mapping
HTML_ATTRIBUTES = {
    'datetime': 'html5semantic',  # datetime attribute on <time> element
    'open': 'details',  # open attribute on <details> element
    'high': 'meter',  # high attribute on <meter> element
    'low': 'meter',  # low attribute on <meter> element
    'optimum': 'meter',  # optimum attribute on <meter> element
    'as': 'link-rel-preload',  # as attribute for link preload (as="style", as="font", etc.)
    'allow': 'permissions-policy',  # allow attribute on iframes for Permissions Policy
    'loading': 'loading-lazy-attr',
    'autocomplete': 'input-autocomplete-onoff',
    'autofocus': 'autofocus',
    'placeholder': 'input-placeholder',
    'required': 'form-validation',
    'pattern': 'input-pattern',  # Separate feature for pattern attribute
    'min': 'form-validation',
    'max': 'form-validation',
    'step': 'form-validation',
    'minlength': 'input-minlength',
    'maxlength': 'maxlength',
    'multiple': 'input-file-multiple',
    'accept': 'input-file-accept',
    'capture': 'html-media-capture',
    'contenteditable': 'contenteditable',
    'draggable': 'dragndrop',
    'spellcheck': 'spellcheck-attribute',
    'translate': 'internationalization',
    'hidden': 'hidden',
    'download': 'download',
    'sandbox': 'iframe-sandbox',
    'srcdoc': 'iframe-srcdoc',
    'reversed': 'ol-reversed',
    'novalidate': 'form-validation',
    'formnovalidate': 'form-validation',
    'inputmode': 'input-inputmode',
    'readonly': 'readonly-attr',
    'tabindex': 'tabindex-attr',
    'ping': 'ping',
    'async': 'script-async',
    'defer': 'script-defer',
    'integrity': 'subresource-integrity',
    'is': 'custom-elementsv1',
    # Form submit attributes (form-submit-attributes)
    'formaction': 'form-submit-attributes',
    'formmethod': 'form-submit-attributes',
    'formenctype': 'form-submit-attributes',
    'formtarget': 'form-submit-attributes',
    # Form attribute - associate element with form by ID
    'form': 'form-attribute',
    # Declarative Shadow DOM
    'shadowroot': 'declarative-shadow-dom',
    'shadowrootmode': 'declarative-shadow-dom',
    # Input event attribute
    'oninput': 'input-event',
    # Touch event attributes
    'ontouchstart': 'touch',
    'ontouchmove': 'touch',
    'ontouchend': 'touch',
    'ontouchcancel': 'touch',
    # Pointer event attributes
    'onpointerdown': 'pointer',
    'onpointermove': 'pointer',
    'onpointerup': 'pointer',
    'onpointercancel': 'pointer',
    'onpointerenter': 'pointer',
    'onpointerleave': 'pointer',
    'onpointerover': 'pointer',
    'onpointerout': 'pointer',
    'ongotpointercapture': 'pointer',
    'onlostpointercapture': 'pointer',
    # Focus events
    'onfocusin': 'focusin-focusout-events',
    'onfocusout': 'focusin-focusout-events',
    # Hash change event
    'onhashchange': 'hashchange',
    # Offline apps (manifest attribute on html element)
    'manifest': 'offline-apps',
    # Page transition events
    'onpageshow': 'page-transition-events',
    'onpagehide': 'page-transition-events',
    # Print events
    'onbeforeprint': 'beforeafterprint',
    'onafterprint': 'beforeafterprint',
    # Scoped style attribute (deprecated)
    'scoped': 'style-scoped',
    # Directory attribute for file input
    'webkitdirectory': 'input-file-directory',
    'directory': 'input-file-directory',
}

# HTML Attribute Values to Feature ID mapping
HTML_ATTRIBUTE_VALUES = {
    ('rel', 'preload'): 'link-rel-preload',
    ('rel', 'prefetch'): 'link-rel-prefetch',
    ('rel', 'dns-prefetch'): 'link-rel-dns-prefetch',
    ('rel', 'preconnect'): 'link-rel-preconnect',
    ('rel', 'modulepreload'): 'link-rel-modulepreload',
    ('rel', 'prerender'): 'link-rel-prerender',
    ('rel', 'icon'): 'link-icon-png',
    ('rel', 'noopener'): 'rel-noopener',
    ('rel', 'noreferrer'): 'rel-noreferrer',
    ('type', 'module'): 'es6-module',
    ('crossorigin', 'anonymous'): 'cors',
    ('crossorigin', 'use-credentials'): 'cors',
    ('referrerpolicy', 'no-referrer'): 'referrer-policy',
    ('referrerpolicy', 'origin'): 'referrer-policy',
    ('referrerpolicy', 'no-referrer-when-downgrade'): 'referrer-policy',
    ('referrerpolicy', 'origin-when-cross-origin'): 'referrer-policy',
    ('referrerpolicy', 'same-origin'): 'referrer-policy',
    ('referrerpolicy', 'strict-origin'): 'referrer-policy',
    ('referrerpolicy', 'strict-origin-when-cross-origin'): 'referrer-policy',
    ('referrerpolicy', 'unsafe-url'): 'referrer-policy',
    ('loading', 'lazy'): 'loading-lazy-attr',
    ('loading', 'eager'): 'loading-lazy-attr',
    # SVG icon type
    ('type', 'image/svg+xml'): 'link-icon-svg',
    # HTML Imports (deprecated but still in CIU)
    ('rel', 'import'): 'imports',
}

# Form-related features
HTML_FORM_FEATURES = {
    'form': 'forms',
    'fieldset': 'forms',
    'legend': 'forms',
    'label': 'forms',
    'input': 'forms',
    'textarea': 'forms',
    'select': 'forms',
    'option': 'forms',
    'button': 'forms',
}

# Media-related features
HTML_MEDIA_FEATURES = {
    'video': 'video',
    'audio': 'audio',
    'source': 'video',
    'track': 'webvtt',  # Track element for captions
}

# Additional HTML features that need to be detected
HTML_ADDITIONAL_FEATURES = {
    'srcset': 'srcset',
    'sizes': 'srcset',
    'dataset': 'dataset',
    'ruby': 'ruby',
    'menu': 'menu',
    'menuitem': 'menu',
    'meta-theme-color': 'meta-theme-color',
    'indeterminate-checkbox': 'indeterminate-checkbox',
    'input-file-directory': 'input-file-directory',
    'web-app-manifest': 'web-app-manifest',
    'svg-html5': 'svg-html5',
    'iframe-seamless': 'iframe-seamless',
    'selectlist': 'selectlist',
    'canvas-text': 'canvas-text',
    'passwordrules': 'passwordrules',
    'rel-noopener': 'rel-noopener',
    # SVG-related features
    'svg-img': 'svg-img',  # SVG in img src
    'svg-fragment': 'svg-fragment',  # SVG fragment identifiers (#id)
    # Media fragments
    'media-fragments': 'media-fragments',  # #t=10,20 time fragments
    # Track elements for audio/video
    'audiotracks': 'audiotracks',
    'videotracks': 'videotracks',
    # Custom elements
    'custom-elements': 'custom-elementsv1',
    # Fieldset disabled
    'fieldset-disabled': 'fieldset-disabled',
    # Portals
    'portals': 'portals',
    # Touch events
    'touch': 'touch',
    # Pointer events
    'pointer': 'pointer',
    # Focus events
    'focusin-focusout-events': 'focusin-focusout-events',
    # Hash change
    'hashchange': 'hashchange',
    # Offline apps
    'offline-apps': 'offline-apps',
    # Page transitions
    'page-transition-events': 'page-transition-events',
    # Print events
    'beforeafterprint': 'beforeafterprint',
    # HTML imports (deprecated)
    'imports': 'imports',
    # Style scoped (deprecated)
    'style-scoped': 'style-scoped',
    # Combined input type feature (alias for email, tel, url)
    'input-email-tel-url': 'input-email-tel-url',
    # WAI-ARIA accessibility features
    'wai-aria': 'wai-aria',
    # MathML
    'mathml': 'mathml',
    # WebVTT
    'webvtt': 'webvtt',
    # Data URIs
    'datauri': 'datauri',
    # XHTML
    'xhtml': 'xhtml',
    # Media formats (detectable via type attribute)
    'webm': 'webm',
    'webp': 'webp',
    'mp3': 'mp3',
    'ogg-vorbis': 'ogg-vorbis',
    'ogv': 'ogv',
    'mpeg4': 'mpeg4',
    'aac': 'aac',
    'wav': 'wav',
    'flac': 'flac',
    'opus': 'opus',
    'avif': 'avif',
    'heif': 'heif',
    'jpeg2000': 'jpeg2000',
    'jpegxl': 'jpegxl',
    'jpegxr': 'jpegxr',
    'apng': 'apng',
    'hevc': 'hevc',
    'av1': 'av1',
}

# HTML Elements for special detection
HTML_SPECIAL_ELEMENTS = {
    # MathML element
    'math': 'mathml',
}

# ARIA attributes for WAI-ARIA detection
HTML_ARIA_ATTRIBUTES = {
    'role': 'wai-aria',
    'aria-label': 'wai-aria',
    'aria-labelledby': 'wai-aria',
    'aria-describedby': 'wai-aria',
    'aria-hidden': 'wai-aria',
    'aria-live': 'wai-aria',
    'aria-atomic': 'wai-aria',
    'aria-busy': 'wai-aria',
    'aria-controls': 'wai-aria',
    'aria-current': 'wai-aria',
    'aria-disabled': 'wai-aria',
    'aria-expanded': 'wai-aria',
    'aria-haspopup': 'wai-aria',
    'aria-invalid': 'wai-aria',
    'aria-pressed': 'wai-aria',
    'aria-selected': 'wai-aria',
    'aria-checked': 'wai-aria',
    'aria-valuemin': 'wai-aria',
    'aria-valuemax': 'wai-aria',
    'aria-valuenow': 'wai-aria',
    'aria-valuetext': 'wai-aria',
    'aria-modal': 'wai-aria',
    'aria-orientation': 'wai-aria',
    'aria-autocomplete': 'wai-aria',
    'aria-multiline': 'wai-aria',
    'aria-multiselectable': 'wai-aria',
    'aria-readonly': 'wai-aria',
    'aria-required': 'wai-aria',
    'aria-sort': 'wai-aria',
    'aria-level': 'wai-aria',
    'aria-posinset': 'wai-aria',
    'aria-setsize': 'wai-aria',
    'aria-owns': 'wai-aria',
    'aria-flowto': 'wai-aria',
    'aria-activedescendant': 'wai-aria',
    'aria-errormessage': 'wai-aria',
    'aria-details': 'wai-aria',
    'aria-keyshortcuts': 'wai-aria',
    'aria-roledescription': 'wai-aria',
}

# Media type attribute values for format detection
HTML_MEDIA_TYPE_VALUES = {
    ('type', 'video/webm'): 'webm',
    ('type', 'video/ogg'): 'ogv',
    ('type', 'video/mp4'): 'mpeg4',
    ('type', 'video/av1'): 'av1',
    ('type', 'audio/webm'): 'webm',
    ('type', 'audio/ogg'): 'ogg-vorbis',
    ('type', 'audio/mpeg'): 'mp3',
    ('type', 'audio/mp3'): 'mp3',
    ('type', 'audio/wav'): 'wav',
    ('type', 'audio/flac'): 'flac',
    ('type', 'audio/aac'): 'aac',
    ('type', 'audio/opus'): 'opus',
    ('type', 'image/webp'): 'webp',
    ('type', 'image/avif'): 'avif',
    ('type', 'image/heif'): 'heif',
    ('type', 'image/heic'): 'heif',
    ('type', 'image/jp2'): 'jpeg2000',
    ('type', 'image/jxl'): 'jpegxl',
    ('type', 'image/jxr'): 'jpegxr',
    ('type', 'image/apng'): 'apng',
    # AC-3 (Dolby Digital) and EC-3 (Dolby Digital Plus) codecs
    ('type', 'audio/ac3'): 'ac3-ec3',
    ('type', 'audio/eac3'): 'ac3-ec3',
    ('type', 'audio/ec3'): 'ac3-ec3',
}

# CSP meta tag detection (values are lowercase for matching)
HTML_CSP_ATTRIBUTES = {
    ('http-equiv', 'content-security-policy'): 'contentsecuritypolicy2',
    ('http-equiv', 'x-content-security-policy'): 'contentsecuritypolicy',
}

# All features combined for quick lookup
ALL_HTML_FEATURES = {
    **HTML_ELEMENTS,
    **HTML_INPUT_TYPES,  # Include all input types!
    **HTML_FORM_FEATURES,
    **HTML_MEDIA_FEATURES,
    **HTML_ADDITIONAL_FEATURES,
    **HTML_ATTRIBUTES,  # Include all attributes!
    **{v: v for k, v in HTML_ATTRIBUTE_VALUES.items()},  # Include attribute values!
    **HTML_SPECIAL_ELEMENTS,  # MathML, etc.
    **HTML_ARIA_ATTRIBUTES,  # WAI-ARIA attributes
    **{v: v for k, v in HTML_MEDIA_TYPE_VALUES.items()},  # Media format types
    **{v: v for k, v in HTML_CSP_ATTRIBUTES.items()},  # CSP meta tags
}
