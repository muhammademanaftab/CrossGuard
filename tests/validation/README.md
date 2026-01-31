# Cross Guard Manual Validation Testing

## Overview

This directory contains test files for manually validating Cross Guard's feature detection against the Can I Use website.

## Purpose

- Verify that Cross Guard correctly detects HTML and CSS features
- Confirm browser compatibility data matches caniuse.com
- Document any discrepancies for future fixes

## Directory Structure

```
tests/validation/
├── README.md                     # This file
│
├── html/                         # HTML validation tests
│   ├── README.md                 # HTML testing instructions
│   ├── CHECKLIST.md              # HTML validation checklist
│   ├── 01_elements/              # Semantic, media, interactive, form elements
│   ├── 02_input_types/           # Date/time, text, other input types
│   ├── 03_attributes/            # Form, loading, content attributes
│   ├── 04_attribute_values/      # rel, type, referrerpolicy values
│   └── 05_special_patterns/      # Responsive images, ARIA, media formats
│
├── css/                          # CSS validation tests
│   ├── README.md                 # CSS testing instructions
│   ├── CHECKLIST.md              # CSS validation checklist
│   ├── 01_layout/                # Flexbox, Grid, Multicolumn
│   ├── 02_transforms_animation/  # Transforms, Animations, Transitions
│   ├── 03_colors_backgrounds/    # Colors, Gradients, Filters
│   ├── 04_typography/            # Fonts, Text properties
│   ├── 05_selectors/             # Pseudo-classes, Pseudo-elements
│   ├── 06_units_values/          # Units, CSS Variables
│   ├── 07_box_model/             # Border, Shadow, Sizing
│   ├── 08_interaction/           # Scroll, User interaction
│   ├── 09_modern_css/            # Container queries, Nesting, Layers
│   ├── 10_media_queries/         # Media features
│   └── comprehensive_test.css    # Master file with ALL features
│
└── results/                      # Validation results
    └── validation_log.md         # Log of manual tests performed
```

## Quick Start

### 1. Open Cross Guard
```bash
python run_gui.py
```

### 2. Run Validation Tests

**For HTML validation:**
- Navigate to `html/` folder
- Load test files one by one in Cross Guard
- Follow instructions in `html/README.md`
- Track progress in `html/CHECKLIST.md`

**For CSS validation:**
- Navigate to `css/` folder
- Load test files one by one in Cross Guard
- Follow instructions in `css/README.md`
- Track progress in `css/CHECKLIST.md`

### 3. Record Results
- Mark features as passed/failed in the respective CHECKLIST.md
- Log detailed findings in `results/validation_log.md`

## Test Coverage

| Category | Files | Features |
|----------|-------|----------|
| HTML | 16 | 48+ Can I Use IDs |
| CSS | 25 | 50+ Can I Use IDs |
| **Total** | **41** | **98+ Features** |

## Validation Process

For each test file:

1. **Load** the file in Cross Guard
2. **Note** detected features and browser support
3. **Verify** against caniuse.com
4. **Record** results in checklist:
   - `[x]` = Passed
   - `[!]` = Failed (add notes)
   - `[ ]` = Not tested

## Success Criteria

- 95%+ accuracy matching Can I Use data
- All discrepancies documented
- Both HTML and CSS validation complete
