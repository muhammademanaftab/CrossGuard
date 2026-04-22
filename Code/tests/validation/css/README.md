# CSS Manual Validation Testing

## Overview

This directory contains CSS test files for manually validating Cross Guard's CSS feature detection against the Can I Use website.

## Directory Structure

```
css/
├── README.md                           # This file
├── CHECKLIST.md                        # CSS validation checklist
│
├── 01_layout/                          # Layout features
│   ├── flexbox.css                     # display: flex, gap
│   ├── grid.css                        # display: grid, subgrid
│   └── multicolumn.css                 # columns, column-gap
│
├── 02_transforms_animation/            # Transforms & Animation
│   ├── transforms.css                  # transform 2D/3D
│   ├── animations.css                  # @keyframes, animation
│   └── transitions.css                 # transition properties
│
├── 03_colors_backgrounds/              # Colors & Backgrounds
│   ├── colors.css                      # rgb, hsl, oklch, color()
│   ├── gradients.css                   # linear, radial, conic gradients
│   └── filters_blend.css               # filter, backdrop-filter, blend
│
├── 04_typography/                      # Typography
│   ├── fonts.css                       # @font-face, variable fonts
│   ├── text_properties.css             # text-overflow, line-clamp
│   └── font_features.css               # font-kerning, ligatures
│
├── 05_selectors/                       # Selectors & Pseudo
│   ├── pseudo_classes.css              # :has, :is, :where, :focus-visible
│   └── pseudo_elements.css             # ::before, ::after, ::marker
│
├── 06_units_values/                    # Units & Variables
│   ├── units.css                       # rem, vh, vw, calc, clamp
│   └── variables.css                   # --custom-property, var()
│
├── 07_box_model/                       # Box Model
│   └── box_properties.css              # border-radius, box-shadow
│
├── 08_interaction/                     # Interaction
│   ├── scroll.css                      # scroll-snap, scroll-behavior
│   └── user_interaction.css            # cursor, pointer-events
│
├── 09_modern_css/                      # Modern CSS
│   ├── container_queries.css           # @container
│   ├── nesting.css                     # & selector
│   ├── cascade_layers.css              # @layer
│   └── view_transitions.css            # view-transition-name
│
├── 10_media_queries/                   # Media Queries
│   └── media_features.css              # @media, prefers-*
│
└── comprehensive_test.css              # Master file with ALL features
```

## Test Files Summary

| Category | Files | Can I Use IDs |
|----------|-------|---------------|
| 01_layout | 3 | flexbox, flexbox-gap, css-grid, css-subgrid, multicolumn |
| 02_transforms_animation | 3 | transforms2d, transforms3d, css-animation, will-change, css-transitions |
| 03_colors_backgrounds | 3 | css3-colors, css-lch-lab, css-color-function, css-gradients, css-conic-gradients, css-filters, css-backdrop-filter, css-mixblendmode |
| 04_typography | 3 | fontface, variable-fonts, woff2, text-overflow, css-line-clamp, css-text-wrap-balance, font-kerning, font-feature |
| 05_selectors | 2 | css-has, css-matches-pseudo, css-focus-visible, css-gencontent, css-marker-pseudo |
| 06_units_values | 2 | rem, viewport-units, calc, css-math-functions, css-variables |
| 07_box_model | 1 | border-radius, css-boxshadow, css3-boxsizing |
| 08_interaction | 2 | css-snappoints, css-scroll-behavior, css-scrollbar, css3-cursors, pointer-events, css-resize |
| 09_modern_css | 4 | css-container-queries, css-nesting, css-cascade-layers, view-transitions |
| 10_media_queries | 1 | css-mediaqueries, prefers-color-scheme, prefers-reduced-motion |
| comprehensive | 1 | All of the above |
| **Total** | **25** | **50+ Features** |

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
Update `CHECKLIST.md`:
- `[x]` = Feature detected, browser support matches
- `[!]` = Discrepancy found (add notes)
- `[ ]` = Not yet tested

## CSS File Format

Each CSS file is written as realistic user code with comments:

```css
/*
 * Cross Guard CSS Manual Validation Test
 * Category: [category]
 * File: [filename]
 *
 * Expected Can I Use IDs:
 *   - feature-id: https://caniuse.com/feature-id
 *
 * VALIDATION STEPS:
 *   1. Load this file in Cross Guard
 *   2. Verify features detected
 *   3. Compare with Can I Use
 *   4. Record results in CHECKLIST.md
 */

/* Feature: feature-name */
.selector {
    property: value;
}
```

## Quick Verification

```bash
# Count CSS test files
find . -name "*.css" | wc -l
# Expected: 25 CSS files

# Test comprehensive file
# Load comprehensive_test.css - should detect 50+ features
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
