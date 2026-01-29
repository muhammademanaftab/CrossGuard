# CSS Manual Validation Testing

## Overview

This directory contains CSS test files for manually validating Cross Guard's CSS feature detection against the Can I Use website.

## Purpose

- Verify that Cross Guard correctly detects CSS features from user stylesheets
- Confirm browser compatibility data matches caniuse.com
- Document any discrepancies for future fixes

## Directory Structure

```
tests/validation/css/
├── README.md                           # This file
├── CSS_CHECKLIST.md                    # CSS validation checklist
│
├── 01_layout/                          # Layout features
│   ├── flexbox.css
│   ├── grid.css
│   └── multicolumn.css
│
├── 02_transforms_animation/            # Transforms & Animation
│   ├── transforms.css
│   ├── animations.css
│   └── transitions.css
│
├── 03_colors_backgrounds/              # Colors & Backgrounds
│   ├── colors.css
│   ├── gradients.css
│   └── filters_blend.css
│
├── 04_typography/                      # Typography
│   ├── fonts.css
│   ├── text_properties.css
│   └── font_features.css
│
├── 05_selectors/                       # Selectors & Pseudo
│   ├── pseudo_classes.css
│   └── pseudo_elements.css
│
├── 06_units_values/                    # Units & Variables
│   ├── units.css
│   └── variables.css
│
├── 07_box_model/                       # Box Model
│   └── box_properties.css
│
├── 08_interaction/                     # Interaction
│   ├── scroll.css
│   └── user_interaction.css
│
├── 09_modern_css/                      # Modern CSS
│   ├── container_queries.css
│   ├── nesting.css
│   ├── cascade_layers.css
│   └── view_transitions.css
│
├── 10_media_queries/                   # Media Queries
│   └── media_features.css
│
└── comprehensive_test.css              # Master file with ALL features
```

## How to Use

### Step 1: Open Cross Guard
```bash
python run_gui.py
```

### Step 2: Load a CSS Test File
- Drag and drop a `.css` file into Cross Guard
- Or use the file picker

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
Update `CSS_CHECKLIST.md`:
- `[x]` = Feature detected, browser support matches
- `[!]` = Discrepancy found (add notes)
- `[ ]` = Not yet tested

## Test File Categories

| Category | Files | Features Tested |
|----------|-------|-----------------|
| 01_layout | 3 | Flexbox, Grid, Multicolumn |
| 02_transforms_animation | 3 | 2D/3D Transforms, Animations, Transitions |
| 03_colors_backgrounds | 3 | Modern Colors, Gradients, Filters |
| 04_typography | 3 | Fonts, Text Properties |
| 05_selectors | 2 | Pseudo-classes, Pseudo-elements |
| 06_units_values | 2 | Modern Units, CSS Variables |
| 07_box_model | 1 | Border, Shadow, Sizing |
| 08_interaction | 2 | Scroll, User Interaction |
| 09_modern_css | 4 | Container Queries, Nesting, Layers, View Transitions |
| 10_media_queries | 1 | Media Features |

## Expected Results

- **Total CSS files**: 21 category files + 1 comprehensive
- **Unique features**: 100+ CSS features
- **Accuracy Target**: 95%+ match with Can I Use data

## CSS File Format

Each CSS file is written as realistic user code with comments indicating:
- Feature being tested
- Can I Use URL for verification
- Validation steps

Example:
```css
/*
 * Cross Guard CSS Manual Validation Test
 * Category: 01_layout
 * File: flexbox.css
 *
 * Expected Can I Use IDs:
 *   - flexbox: https://caniuse.com/flexbox
 */

.container {
    display: flex;
    flex-direction: row;
}
```

## Quick Verification

```bash
# Count CSS test files
find tests/validation/css -name "*.css" | wc -l

# Run Cross Guard
python run_gui.py

# Load comprehensive_test.css - should detect 50+ features
```

## Reporting Discrepancies

If you find a discrepancy:
1. Document it in `CSS_CHECKLIST.md` with `[!]`
2. Add detailed notes including:
   - Feature ID
   - Expected browser support
   - Actual browser support shown
   - Can I Use URL
3. Record in `../results/validation_log.md`
