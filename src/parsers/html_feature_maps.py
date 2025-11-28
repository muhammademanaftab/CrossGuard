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
    'source': 'picture',  # Used with picture
    'track': 'track',
    'video': 'video',
    'audio': 'audio',
    'canvas': 'canvas',
    'svg': 'svg',
    'meter': 'meter',
    'progress': 'progress',
    'output': 'output',
    'datalist': 'datalist',
    'keygen': 'keygen',
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
    'tel': 'input-tel',
    'url': 'input-url',
    'email': 'input-email',
    'number': 'input-number',
    'file': 'input-file-accept',
}

# HTML Attributes to Feature ID mapping
HTML_ATTRIBUTES = {
    'loading': 'loading-lazy-attr',
    'decoding': 'img-decoding-async',
    'autocomplete': 'input-autocomplete-onoff',
    'autofocus': 'autofocus',
    'placeholder': 'input-placeholder',
    'required': 'form-validation',
    'pattern': 'form-validation',
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
    'enterkeyhint': 'input-enterkeyhint',
    'readonly': 'readonly-attr',
    'disabled': 'disabled-attribute',
    'tabindex': 'tabindex-attr',
    'ping': 'ping',
    'async': 'script-async',
    'defer': 'script-defer',
    'integrity': 'subresource-integrity',
    'is': 'custom-elementsv1',
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
    ('loading', 'lazy'): 'loading-lazy-attr',
    ('decoding', 'async'): 'img-decoding-async',
}

# Form-related features
HTML_FORM_FEATURES = {
    'form': 'form',
    'fieldset': 'form',
    'legend': 'form',
    'label': 'form',
    'input': 'form',
    'textarea': 'form',
    'select': 'form',
    'option': 'form',
    'button': 'form',
}

# Media-related features
HTML_MEDIA_FEATURES = {
    'video': 'video',
    'audio': 'audio',
    'source': 'video',
    'track': 'track',
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
}
