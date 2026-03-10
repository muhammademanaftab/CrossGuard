# HTML Parser - How It Works

## What is the HTML Parser's Job?

Its job is simple: take an HTML file, read through it, and find all the web features that might have browser compatibility issues.

For example, if your HTML uses `<dialog>`, that's a feature that some older browsers don't support. The parser needs to find it.

Features like `<div>`, `<p>`, `<span>`, `<a>` are NOT checked because they work in every browser. The parser only looks for features that might have compatibility issues.

---

## The Two Main Files

| File | What it contains |
|------|-----------------|
| `src/parsers/html_parser.py` | The parser logic (the code that searches through HTML) |
| `src/parsers/html_feature_maps.py` | The feature maps / dictionaries (the data that says what to look for) |

---

## What is BeautifulSoup?

BeautifulSoup is a Python library that parses HTML. We don't parse HTML ourselves. BeautifulSoup does it for us.

When we give it an HTML string, it builds a **tree of Python objects** in memory. Each HTML element becomes a Python object that we can interact with using functions.

```python
from bs4 import BeautifulSoup

html_text = '<html><body><dialog open>Hello</dialog><img loading="lazy" src="photo.jpg"></body></html>'
soup = BeautifulSoup(html_text, 'html.parser')
```

Now `soup` is NOT a string anymore. It's a Python object with methods we can call to search and read the HTML.

---

## BeautifulSoup Functions We Use

### `soup.find_all('element_name')`

Finds all elements with that tag name. Returns a list.

```python
soup.find_all('dialog')
# Returns: [<dialog open>Hello</dialog>]
# Found 1 dialog element

soup.find_all('input')
# Returns: [<input type="date"/>, <input type="text"/>]
# Found 2 input elements

soup.find_all('canvas')
# Returns: []
# Found nothing
```

### `soup.find_all()` (no argument)

Finds ALL elements in the entire HTML.

```python
all_elements = soup.find_all()
for elem in all_elements:
    print(elem.name)
# html, body, dialog, img, input, input, video, source ...
```

### `element.get('attribute_name')`

Reads a specific attribute from an element. Returns `None` if it doesn't exist.

```python
img = soup.find_all('img')[0]    # <img loading="lazy" src="photo.jpg">
img.get('loading')                # Returns: 'lazy'
img.get('src')                    # Returns: 'photo.jpg'
img.get('class')                  # Returns: None (doesn't exist)
```

### `element.attrs`

Returns ALL attributes of an element as a Python dictionary.

```python
img = soup.find_all('img')[0]    # <img loading="lazy" src="photo.jpg">
img.attrs
# Returns: {'loading': 'lazy', 'src': 'photo.jpg'}

# We can loop through them:
for attr_name, attr_value in img.attrs.items():
    print(f"{attr_name} = {attr_value}")
# loading = lazy
# src = photo.jpg
```

### `element.name`

Returns the tag name of an element.

```python
elem = soup.find_all('dialog')[0]
elem.name    # Returns: 'dialog'
```

### `soup.find_all(attrs={'loading': True})`

Finds all elements that HAVE a specific attribute, no matter what element type they are.

```python
soup.find_all(attrs={'loading': True})
# Returns: [<img loading="lazy" src="photo.jpg">]
# Only the img has a 'loading' attribute
```

---

## What are the Feature Maps (Dictionaries)?

Feature maps are Python dictionaries stored in `html_feature_maps.py`. They map something we find in the HTML to a Can I Use feature ID.

The left side is the **key** (what we search for in the HTML).
The right side is the **value** (the Can I Use feature ID).

We have 6 main feature maps:

### 1. `HTML_ELEMENTS` - Maps element names to feature IDs

```python
HTML_ELEMENTS = {
    'dialog': 'dialog',
    'details': 'details',
    'template': 'template',
    'picture': 'picture',
    'video': 'video',
    'audio': 'audio',
    'canvas': 'canvas',
    'svg': 'svg',
    'meter': 'meter',
    'progress': 'progress',
    'datalist': 'datalist',
    'slot': 'shadowdomv1',
    # ... about 40 elements total
}
```

### 2. `HTML_INPUT_TYPES` - Maps input type values to feature IDs

```python
HTML_INPUT_TYPES = {
    'date': 'input-datetime',
    'datetime-local': 'input-datetime',
    'time': 'input-datetime',
    'color': 'input-color',
    'range': 'input-range',
    'number': 'input-number',
    'email': 'input-email-tel-url',
    'tel': 'input-email-tel-url',
    # ...
}
```

### 3. `HTML_ATTRIBUTES` - Maps attribute names to feature IDs

```python
HTML_ATTRIBUTES = {
    'loading': 'loading-lazy-attr',
    'contenteditable': 'contenteditable',
    'draggable': 'dragndrop',
    'inputmode': 'input-inputmode',
    'download': 'download',
    'sandbox': 'iframe-sandbox',
    'popover': 'popover',
    'inert': 'inert',
    'placeholder': 'input-placeholder',
    # ... about 80 attributes
}
```

### 4. `HTML_ATTRIBUTE_VALUES` - Maps (attribute, value) pairs to feature IDs

```python
HTML_ATTRIBUTE_VALUES = {
    ('rel', 'preload'): 'link-rel-preload',
    ('rel', 'prefetch'): 'link-rel-prefetch',
    ('type', 'module'): 'es6-module',
    ('loading', 'lazy'): 'loading-lazy-attr',
    ('crossorigin', 'anonymous'): 'cors',
    # ...
}
```

### 5. `HTML_ARIA_ATTRIBUTES` - Maps ARIA attributes to feature IDs

```python
HTML_ARIA_ATTRIBUTES = {
    'role': 'wai-aria',
    'aria-label': 'wai-aria',
    'aria-hidden': 'wai-aria',
    'aria-live': 'wai-aria',
    # ... all map to 'wai-aria'
}
```

### 6. `HTML_MEDIA_TYPE_VALUES` - Maps media type values to feature IDs

```python
HTML_MEDIA_TYPE_VALUES = {
    ('type', 'video/webm'): 'webm',
    ('type', 'video/mp4'): 'mpeg4',
    ('type', 'audio/mp3'): 'mp3',
    ('type', 'image/webp'): 'webp',
    ('type', 'image/avif'): 'avif',
    # ...
}
```

There is also `ELEMENT_SPECIFIC_ATTRIBUTES` for attributes that only matter on certain elements (like `label` only matters on `<track>`, not on `<option>`).

---

## The 5 Detection Steps

After BeautifulSoup parses the HTML, the parser runs 5 detection methods one after another:

```python
self._detect_elements(soup)          # Step 1
self._detect_input_types(soup)       # Step 2
self._detect_attributes(soup)        # Step 3
self._detect_attribute_values(soup)  # Step 4
self._detect_special_patterns(soup)  # Step 5
```

### Step 1: Detect Elements (`_detect_elements`)

Loops through the `HTML_ELEMENTS` dictionary. For each entry, asks BeautifulSoup "does this HTML have this element?"

```python
for element_name, feature_id in self._elements.items():
    elements = soup.find_all(element_name)   # Ask BS4: find all <dialog>
    if elements:                              # Found any?
        self.features_found.add(feature_id)   # Add 'dialog' to results
```

Example: HTML has `<dialog>` -> parser finds it -> adds `'dialog'` to results.

### Step 2: Detect Input Types (`_detect_input_types`)

Finds all `<input>` elements, reads their `type` attribute, and checks it against `HTML_INPUT_TYPES`.

```python
inputs = soup.find_all('input')           # Find all <input> elements
for input_elem in inputs:
    input_type = input_elem.get('type')   # Get the type attribute
    if input_type in self._input_types:   # Is it in our dictionary?
        feature_id = self._input_types[input_type]
        self.features_found.add(feature_id)
```

Example: `<input type="date">` -> type is `'date'` -> maps to `'input-datetime'` -> added to results.

Why separate from Step 1? Because the element is always `<input>`, but the `type` attribute changes the behavior. `<input type="text">` works everywhere, but `<input type="date">` doesn't.

### Step 3: Detect Attributes (`_detect_attributes`)

Gets ALL elements, loops through ALL their attributes, and checks each attribute name against `HTML_ATTRIBUTES`.

```python
all_elements = soup.find_all()               # Get every element
for element in all_elements:
    for attr_name in element.attrs:           # Loop through its attributes
        if attr_name in self._attributes:     # Is this attribute in our dict?
            feature_id = self._attributes[attr_name]
            self.features_found.add(feature_id)
```

Example: `<img loading="lazy">` -> has attribute `loading` -> maps to `'loading-lazy-attr'` -> added to results.

Also checks `ELEMENT_SPECIFIC_ATTRIBUTES` for attributes that only matter on certain elements. For example, `label` on `<track>` maps to `'webvtt'`, but `label` on `<option>` is ignored.

### Step 4: Detect Attribute Values (`_detect_attribute_values`)

Checks specific (attribute, value) combinations against `HTML_ATTRIBUTE_VALUES`.

```python
for element in all_elements:
    for attr_name, attr_value in element.attrs.items():
        key = (attr_name, attr_value.lower())        # Make a tuple
        if key in self._attribute_values:             # Look it up
            feature_id = self._attribute_values[key]
            self.features_found.add(feature_id)
```

Example: `<link rel="preload">` -> tuple is `('rel', 'preload')` -> maps to `'link-rel-preload'` -> added to results.

Also handles media types with codecs like `type="video/webm; codecs=vp9"` by stripping the part after the semicolon.

### Step 5: Detect Special Patterns (`_detect_special_patterns`)

Some features need custom logic that can't be done with simple dictionary lookups. This method handles about 15 special cases:

- **srcset** (responsive images): checks if any element has a `srcset` attribute
- **script async/defer**: checks `<script>` elements for `async`, `defer`, or `type="module"`
- **link preload/prefetch**: checks `<link>` elements for `rel="preload"`, `rel="prefetch"`, etc.
- **SVG in img tags**: checks if any `<img>` has a `.svg` file in its `src`
- **Custom elements**: checks if any element has a hyphen in its name (like `<my-component>`)
- **data-* attributes**: checks for `data-` prefixed attributes
- **meta viewport**: checks for `<meta name="viewport">`
- **Data URIs**: checks for `data:` in src/href attributes
- **WebVTT**: checks for `.vtt` files in `<track>` elements
- **Media fragments**: checks for `#t=` time fragments in video/audio sources
- **XHTML**: checks for XHTML namespace on `<html>` element

---

## Custom Rules

Users can extend the parser without changing source code. Before detection starts, the parser merges user-defined rules with the built-in feature maps:

```python
custom_html = get_custom_html_rules()   # Load from custom_rules.json
self._elements = {**HTML_ELEMENTS, **custom_html.get('elements', {})}
self._attributes = {**HTML_ATTRIBUTES, **custom_html.get('attributes', {})}
```

The `{**dict1, **dict2}` syntax merges two dictionaries. Custom rules get added on top of built-in rules.

---

## The Output

After all 5 detection methods run, the parser returns a **set** of Can I Use feature IDs:

```python
{'dialog', 'loading-lazy-attr', 'input-datetime', 'srcset', 'video', 'webm'}
```

This set then goes to the **Analyzer**, which looks up each feature ID in the Can I Use database to check which browsers support it.

---

## Full Flow Summary

```
Your HTML file
    |
    v
Read the file as a string
    |
    v
BeautifulSoup parses the string into a tree of Python objects
    |
    v
5 detection methods run:
    |
    |-- 1. Element names      <dialog> -> 'dialog'
    |-- 2. Input types        <input type="date"> -> 'input-datetime'
    |-- 3. Attribute names    loading="lazy" -> 'loading-lazy-attr'
    |-- 4. Attribute values   rel="preload" -> 'link-rel-preload'
    |-- 5. Special patterns   srcset, SVG, custom elements, etc.
    |
    v
Set of Can I Use feature IDs
{'dialog', 'input-datetime', 'loading-lazy-attr', ...}
    |
    v
Goes to the Analyzer for browser compatibility checking
```

---

## Concrete Example

Given this HTML:

```html
<html>
  <body>
    <dialog open>Hello</dialog>
    <img loading="lazy" src="photo.jpg">
    <input type="date">
    <input type="text" placeholder="Name">
    <video>
      <source type="video/webm" src="clip.webm">
    </video>
    <link rel="preload" href="font.woff2" as="font">
  </body>
</html>
```

The parser finds:

| What it found | Which detection step | Feature ID |
|---|---|---|
| `<dialog>` element | Step 1 (elements) | `dialog` |
| `<video>` element | Step 1 (elements) | `video` |
| `<input type="date">` | Step 2 (input types) | `input-datetime` |
| `loading` attribute on `<img>` | Step 3 (attributes) | `loading-lazy-attr` |
| `placeholder` attribute on `<input>` | Step 3 (attributes) | `input-placeholder` |
| `rel="preload"` on `<link>` | Step 4 (attribute values) | `link-rel-preload` |
| `type="video/webm"` on `<source>` | Step 4 (attribute values) | `webm` |

Final output set: `{'dialog', 'video', 'input-datetime', 'loading-lazy-attr', 'input-placeholder', 'link-rel-preload', 'webm'}`

---

## Key Points to Remember

1. **BeautifulSoup** does the HTML parsing. We don't parse HTML ourselves.
2. BeautifulSoup turns HTML text into a tree of Python objects that we can search with `find_all()`, read with `.attrs` and `.get()`.
3. **Feature maps** are Python dictionaries in `html_feature_maps.py`. They say "if you see X in the HTML, it maps to Y feature ID".
4. The parser runs **5 detection methods**: elements, input types, attributes, attribute values, and special patterns.
5. **Custom rules** can extend the parser. They get merged into the dictionaries before detection starts.
6. The parser **only looks for features that might have compatibility issues**. Basic elements like `<div>`, `<p>`, `<span>` are skipped.
7. The output is a **set of Can I Use feature IDs** that goes to the Analyzer next.
