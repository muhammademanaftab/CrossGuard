# HTML Manual Validation Testing

## Overview

This directory contains HTML test files for manually validating Cross Guard's HTML feature detection against the Can I Use website.

## Directory Structure

```
html/
├── README.md                           # This file
├── CHECKLIST.md                        # HTML validation checklist
│
├── 01_elements/                        # HTML Element tests
│   ├── semantic_elements.html          # main, section, article, nav, header, footer
│   ├── media_elements.html             # video, audio, picture, canvas
│   ├── interactive_elements.html       # dialog, details, template
│   └── form_elements.html              # datalist, meter, progress
│
├── 02_input_types/                     # Input Type tests
│   ├── datetime_inputs.html            # date, time, datetime-local, month, week
│   ├── text_inputs.html                # email, tel, url, search
│   └── other_inputs.html               # color, range, number, file
│
├── 03_attributes/                      # Attribute tests
│   ├── form_attributes.html            # required, pattern, placeholder, autofocus
│   ├── loading_attributes.html         # loading, async, defer, integrity
│   └── content_attributes.html         # contenteditable, draggable, hidden, download
│
├── 04_attribute_values/                # Attribute:Value tests
│   ├── rel_values.html                 # preload, prefetch, preconnect, modulepreload
│   ├── type_values.html                # type=module, media types
│   └── referrerpolicy_values.html      # referrer policies
│
└── 05_special_patterns/                # Special Pattern tests
    ├── responsive_images.html          # srcset, sizes, picture
    ├── accessibility.html              # ARIA attributes
    └── media_formats.html              # webm, webp, avif formats
```

## Test Files Summary

| Category | Files | Features Tested |
|----------|-------|-----------------|
| 01_elements | 4 | html5semantic, video, audio, picture, canvas, webvtt, dialog, details, template, datalist, meter, progress |
| 02_input_types | 3 | input-datetime, input-email-tel-url, input-search, input-color, input-range, input-number, input-file-accept |
| 03_attributes | 3 | form-validation, input-pattern, input-placeholder, autofocus, loading-lazy-attr, script-async, script-defer, subresource-integrity, contenteditable, dragndrop, hidden, download |
| 04_attribute_values | 3 | link-rel-preload, link-rel-prefetch, link-rel-dns-prefetch, link-rel-preconnect, link-rel-modulepreload, es6-module, webm, mpeg4, mp3, referrer-policy |
| 05_special_patterns | 3 | srcset, picture, wai-aria, webp, avif, heif |
| **Total** | **16** | **48+ Features** |

## How to Use

### Step 1: Open Cross Guard
```bash
python run_gui.py
```

### Step 2: Load a Test File
- Drag and drop an HTML file into Cross Guard
- Or use the file picker to select a file

### Step 3: Check Detected Features
1. Look at the "Detected Features" count
2. Expand browser cards to see the feature list
3. Note each Can I Use ID detected

### Step 4: Verify on Can I Use
For each detected feature:
1. Open URL: `https://caniuse.com/{feature-id}`
2. Compare browser support percentages
3. Check version numbers match

### Step 5: Record Results
Update `CHECKLIST.md`:
- `[x]` = Feature detected, browser support matches
- `[!]` = Discrepancy found (add notes)
- `[ ]` = Not yet tested

## HTML File Format

Each test file follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>[Category] - Manual Validation Test</title>
    <!--
        Cross Guard Manual Validation Test
        Category: [category]
        File: [filename]

        Expected Can I Use IDs:
          - feature-id: https://caniuse.com/feature-id

        VALIDATION STEPS:
          1. Load this file in Cross Guard
          2. Verify features detected
          3. Compare with Can I Use
          4. Record results in CHECKLIST.md
    -->
</head>
<body>
    <!-- Feature demonstrations -->
</body>
</html>
```

## Quick Verification

```bash
# Count HTML test files
find . -name "*.html" | wc -l
# Expected: 16 HTML files
```

## Reporting Issues

If you find a discrepancy:
1. Mark with `[!]` in CHECKLIST.md
2. Add detailed notes including:
   - Feature ID
   - Expected browser support
   - Actual browser support shown
   - Can I Use URL
3. Log in `../results/validation_log.md`
