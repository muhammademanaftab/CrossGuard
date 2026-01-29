# Cross Guard Manual Validation Testing

## Overview

This directory contains test files for manually validating Cross Guard's feature detection against the Can I Use website.

## Purpose

- Verify that Cross Guard correctly detects HTML, CSS, and JavaScript features
- Confirm browser compatibility data matches caniuse.com
- Document any discrepancies for future fixes

## Directory Structure

```
tests/validation/
├── README.md                    # This file
├── CHECKLIST.md                 # Master checklist to track progress
│
├── 01_elements/                 # HTML Element tests
├── 02_input_types/              # Input Type tests
├── 03_attributes/               # Attribute tests
├── 04_attribute_values/         # Attribute:Value tests
├── 05_special_patterns/         # Special Pattern tests
│
├── css/                         # CSS validation tests
│   ├── README.md
│   ├── CSS_CHECKLIST.md
│   └── [category folders]
│
└── results/                     # Validation results
    └── validation_log.md
```

## How to Use

### Step 1: Open Cross Guard
```bash
python run_gui.py
```

### Step 2: Load a Test File
- Drag and drop a test HTML/CSS file into Cross Guard
- Or use the file picker to select a file

### Step 3: Note Detected Features
1. Look at the "Detected Features" count
2. Expand browser cards to see the feature list
3. Note each feature's name and Can I Use ID

### Step 4: Verify on Can I Use
For each detected feature:
1. Go to `https://caniuse.com/{feature-id}`
2. Compare browser support shown on Can I Use with Cross Guard
3. Verify version ranges match

### Step 5: Record Results
1. Open `CHECKLIST.md` (for HTML) or `css/CSS_CHECKLIST.md` (for CSS)
2. Mark features as:
   - `[x]` = Passed (feature detected, support matches)
   - `[!]` = Failed (add notes about discrepancy)
   - `[ ]` = Not yet tested
3. Add detailed notes in `results/validation_log.md`

## Test File Categories

### HTML Tests

| Category | Files | Features Tested |
|----------|-------|-----------------|
| 01_elements | 4 | Semantic, media, interactive, form elements |
| 02_input_types | 3 | Date/time, text, other input types |
| 03_attributes | 3 | Form, loading, content attributes |
| 04_attribute_values | 3 | rel, type, referrerpolicy values |
| 05_special_patterns | 3 | Responsive images, ARIA, media formats |

### CSS Tests

| Category | Files | Features Tested |
|----------|-------|-----------------|
| 01_layout | 3 | Flexbox, Grid, Multicolumn |
| 02_transforms_animation | 3 | Transforms, Animations, Transitions |
| 03_colors_backgrounds | 3 | Colors, Gradients, Filters |
| 04_typography | 3 | Fonts, Text properties |
| 05_selectors | 2 | Pseudo-classes, Pseudo-elements |
| 06_units_values | 2 | Units, CSS Variables |
| 07_box_model | 1 | Border, Shadow, Sizing |
| 08_interaction | 2 | Scroll, User interaction |
| 09_modern_css | 4 | Container queries, Nesting, Layers |
| 10_media_queries | 1 | Media features |

## Expected Results

- **HTML**: 60+ unique features across 16 test files
- **CSS**: 100+ unique features across 21 test files
- **Accuracy Target**: 95%+ match with Can I Use data

## Reporting Issues

If you find a discrepancy:
1. Document it in `results/validation_log.md`
2. Note the feature ID, expected value, and actual value
3. Include the Can I Use URL for reference

## Quick Verification

```bash
# Count HTML test files
find tests/validation -maxdepth 2 -name "*.html" | wc -l

# Count CSS test files
find tests/validation/css -name "*.css" | wc -l

# Run Cross Guard
python run_gui.py
```
