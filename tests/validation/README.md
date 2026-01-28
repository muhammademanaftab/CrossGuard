# Cross Guard Manual Validation Test Suite

## Overview

This test suite provides comprehensive manual validation tests to verify that Cross Guard correctly detects HTML, CSS, and JavaScript features and reports accurate browser compatibility data matching [caniuse.com](https://caniuse.com).

## Directory Structure

```
tests/validation/
├── README.md                           # This file
├── CHECKLIST.md                        # Master checklist to track progress
│
├── html/                               # HTML Feature Tests ✅ COMPLETE
│   ├── comprehensive_test.html         # All 54 HTML features in one file
│   ├── manual_test.html                # Quick manual testing
│   │
│   ├── 01_elements/                    # HTML Element tests
│   │   ├── semantic_elements.html      # main, section, article, nav, header, footer
│   │   ├── media_elements.html         # video, audio, picture, canvas
│   │   ├── interactive_elements.html   # dialog, details, template
│   │   └── form_elements.html          # datalist, meter, progress, output
│   │
│   ├── 02_input_types/                 # Input Type tests
│   │   ├── datetime_inputs.html        # date, time, datetime-local, month, week
│   │   ├── text_inputs.html            # email, tel, url, search
│   │   └── other_inputs.html           # color, range, number, file
│   │
│   ├── 03_attributes/                  # Attribute tests
│   │   ├── form_attributes.html        # required, pattern, min, max
│   │   ├── loading_attributes.html     # loading, async, defer, integrity
│   │   └── content_attributes.html     # contenteditable, draggable, hidden
│   │
│   ├── 04_attribute_values/            # Attribute:Value tests
│   │   ├── rel_values.html             # preload, prefetch, preconnect, modulepreload
│   │   ├── type_values.html            # type=module, media types
│   │   └── referrerpolicy_values.html  # referrer policies
│   │
│   └── 05_special_patterns/            # Special Pattern tests
│       ├── responsive_images.html      # srcset, sizes, picture
│       ├── accessibility.html          # ARIA attributes
│       └── media_formats.html          # webm, webp, avif formats
│
├── css/                                # CSS Feature Tests (TODO)
│   └── (to be created)
│
├── js/                                 # JavaScript Feature Tests (TODO)
│   └── (to be created)
│
└── results/                            # Store validation results
    └── validation_log.md               # Log of manual tests performed
```

---

## Test Status

| Language | Test Files | Features Covered | Status |
|----------|------------|------------------|--------|
| **HTML** | 18 files | 54+ features | ✅ COMPLETE |
| **CSS** | - | - | 🔲 TODO |
| **JavaScript** | - | - | 🔲 TODO |

---

## HTML Testing Summary ✅

### Coverage
- **Total HTML features in Can I Use:** 89
- **Features covered in maps:** 75 (84%)
- **Features tested:** 54 unique features
- **Uncovered:** 14 (mostly JS APIs, not HTML markup)

### Test Results
- All 16 category test files validated
- Comprehensive test file detects 54 features
- Random real-world HTML files tested successfully
- 100% accuracy on feature detection

### Key Features Tested
- HTML5 Semantic Elements (header, nav, main, section, article, aside, footer, figure)
- Media Elements (video, audio, picture, canvas, track)
- Interactive Elements (dialog, details, summary, template)
- Form Elements (datalist, meter, progress, output)
- Input Types (date, time, color, range, email, tel, url, search, number, file)
- Attributes (loading, async, defer, integrity, contenteditable, hidden, download)
- Attribute Values (rel preload/prefetch, type module, referrerpolicy)
- Media Formats (webm, mp4, mp3, ogg, webp, avif)
- Accessibility (WAI-ARIA roles and attributes)
- Responsive Images (srcset, sizes, picture)

---

## How to Run Manual Validation Tests

### Prerequisites

1. Cross Guard application running (`python run_gui.py`)
2. Web browser for accessing caniuse.com
3. This checklist open for recording results

### Step-by-Step Process

#### Step 1: Load Test File in Cross Guard

1. Open Cross Guard application
2. Drag and drop a test HTML/CSS/JS file (or use file picker)
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

---

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

---

## Next Steps

1. ~~Complete HTML testing~~ ✅
2. Create CSS validation tests
3. Create JavaScript validation tests
4. Final comprehensive validation report
