# Cross Guard Manual Validation Test Suite

## Overview

This test suite provides comprehensive manual validation tests to verify that Cross Guard correctly detects HTML features and reports accurate browser compatibility data matching [caniuse.com](https://caniuse.com).

## Directory Structure

```
tests/validation/
├── README.md                           # This file
├── CHECKLIST.md                        # Master checklist to track progress
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
│   ├── form_attributes.html            # required, pattern, min, max
│   ├── loading_attributes.html         # loading, async, defer, integrity
│   └── content_attributes.html         # contenteditable, draggable, hidden
│
├── 04_attribute_values/                # Attribute:Value tests
│   ├── rel_values.html                 # preload, prefetch, preconnect, modulepreload
│   ├── type_values.html                # type=module, media types
│   └── referrerpolicy_values.html      # referrer policies
│
├── 05_special_patterns/                # Special Pattern tests
│   ├── responsive_images.html          # srcset, sizes, picture
│   ├── accessibility.html              # ARIA attributes
│   └── media_formats.html              # webm, webp, avif formats
│
└── results/                            # Store validation results
    └── validation_log.md               # Log of manual tests performed
```

## How to Run Manual Validation Tests

### Prerequisites

1. Cross Guard application running (`python run_gui.py`)
2. Web browser for accessing caniuse.com
3. This checklist open for recording results

### Step-by-Step Process

#### Step 1: Load Test File in Cross Guard

1. Open Cross Guard application
2. Drag and drop a test HTML file (or use file picker)
3. Wait for analysis to complete

#### Step 2: Note Detected Features

1. Check the "Detected Features" count displayed
2. Expand browser cards to see the full feature list
3. Note each feature's name and Can I Use ID

#### Step 3: Verify Against Can I Use Website

For each detected feature:

1. Go to `https://caniuse.com/{feature-id}`
2. Compare browser support percentages
3. Verify version support ranges match
4. Check for any discrepancies in support status (full, partial, none)

#### Step 4: Record Results

1. Open `CHECKLIST.md`
2. Mark each feature as PASS `[x]` or FAIL `[!]`
3. Add notes for any discrepancies
4. Log detailed results in `results/validation_log.md`

## Test Categories

### 01_elements/ - HTML Elements

Tests semantic, media, interactive, and form elements introduced in HTML5 and later.

**Key Features:**
- Semantic: `<main>`, `<section>`, `<article>`, `<aside>`, `<header>`, `<footer>`, `<nav>`
- Media: `<video>`, `<audio>`, `<picture>`, `<canvas>`, `<track>`
- Interactive: `<dialog>`, `<details>`, `<summary>`, `<template>`
- Forms: `<datalist>`, `<meter>`, `<progress>`, `<output>`

### 02_input_types/ - Input Types

Tests HTML5 input types for dates, text, and other specialized inputs.

**Key Features:**
- Date/Time: `date`, `time`, `datetime-local`, `month`, `week`
- Text: `email`, `tel`, `url`, `search`
- Other: `color`, `range`, `number`, `file`

### 03_attributes/ - HTML Attributes

Tests form validation, loading optimization, and content attributes.

**Key Features:**
- Form: `required`, `pattern`, `min`, `max`, `placeholder`, `autofocus`
- Loading: `loading="lazy"`, `async`, `defer`, `integrity`
- Content: `contenteditable`, `draggable`, `hidden`, `download`

### 04_attribute_values/ - Attribute Values

Tests specific attribute values that have their own Can I Use entries.

**Key Features:**
- `rel` values: `preload`, `prefetch`, `dns-prefetch`, `preconnect`, `modulepreload`
- `type` values: `module` (ES6 modules)
- `referrerpolicy` values: various referrer policies

### 05_special_patterns/ - Special Patterns

Tests complex feature patterns like responsive images and accessibility.

**Key Features:**
- Responsive: `srcset`, `sizes`, `<picture>`
- Accessibility: ARIA roles and attributes
- Media formats: WebM, WebP, AVIF, HEIF

## Validation Criteria

### What to Check

1. **Feature Detection**: Is the feature correctly identified?
2. **Can I Use ID**: Does Cross Guard use the correct Can I Use feature ID?
3. **Browser Support**: Do support percentages match caniuse.com?
4. **Version Ranges**: Are minimum supported versions accurate?
5. **Support Status**: Are full/partial/no support states correct?

### Pass/Fail Criteria

- **PASS**: Feature detected AND browser support matches caniuse.com within 2%
- **FAIL**: Feature not detected OR browser support differs by more than 5%
- **PARTIAL**: Minor version discrepancies (within 1-2 versions)

## Success Criteria

- [ ] All 16 HTML test files processed
- [ ] At least 50 unique features validated
- [ ] 95%+ accuracy (features match Can I Use data)
- [ ] All discrepancies documented
- [ ] Validation log completed

## Troubleshooting

### Feature Not Detected

1. Check if the feature is in Cross Guard's feature maps
2. Verify the HTML syntax is correct
3. Check `src/parsers/html_feature_maps.py` for supported features

### Browser Support Mismatch

1. Verify Can I Use database is up to date (use "Update Database" button)
2. Check the exact feature ID being used
3. Note that Can I Use data updates frequently

### Application Errors

1. Check the terminal for error messages
2. Verify Python dependencies are installed
3. Try restarting the application

## Contributing

To add new validation tests:

1. Create a new HTML file in the appropriate category folder
2. Follow the existing file template
3. Add entries to `CHECKLIST.md`
4. Document expected features and Can I Use IDs
