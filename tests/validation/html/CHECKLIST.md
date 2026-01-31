# HTML Manual Validation Checklist

## Legend
- `[ ]` = Not tested
- `[x]` = Passed (feature detected, browser support matches)
- `[!]` = Failed (see notes for discrepancy details)

---

## 01_elements/

### semantic_elements.html
**Expected features:** `html5semantic`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | html5semantic | https://caniuse.com/html5semantic |

**Elements tested:** main, section, article, aside, header, footer, nav, figure, figcaption, time, mark

- [ ] All semantic elements detected under `html5semantic`
- [ ] Browser support matches Can I Use
- **Notes:** ___

---

### media_elements.html
**Expected features:** `video`, `audio`, `picture`, `canvas`, `webvtt`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | video | https://caniuse.com/video |
| [ ] | audio | https://caniuse.com/audio |
| [ ] | picture | https://caniuse.com/picture |
| [ ] | canvas | https://caniuse.com/canvas |
| [ ] | webvtt | https://caniuse.com/webvtt |

- [ ] All 5 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

### interactive_elements.html
**Expected features:** `dialog`, `details`, `template`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | dialog | https://caniuse.com/dialog |
| [ ] | details | https://caniuse.com/details |
| [ ] | template | https://caniuse.com/template |

- [ ] All 3 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

### form_elements.html
**Expected features:** `datalist`, `meter`, `progress`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | datalist | https://caniuse.com/datalist |
| [ ] | meter | https://caniuse.com/meter |
| [ ] | progress | https://caniuse.com/progress |

- [ ] All 3 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

## 02_input_types/

### datetime_inputs.html
**Expected features:** `input-datetime`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | input-datetime | https://caniuse.com/input-datetime |

**Input types tested:** date, datetime-local, time, month, week

- [ ] Feature detected
- [ ] Browser support matches Can I Use
- **Notes:** ___

---

### text_inputs.html
**Expected features:** `input-email-tel-url`, `input-search`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | input-email-tel-url | https://caniuse.com/input-email-tel-url |
| [ ] | input-search | https://caniuse.com/input-search |

**Input types tested:** email, tel, url, search

- [ ] Both features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

### other_inputs.html
**Expected features:** `input-color`, `input-range`, `input-number`, `input-file-accept`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | input-color | https://caniuse.com/input-color |
| [ ] | input-range | https://caniuse.com/input-range |
| [ ] | input-number | https://caniuse.com/input-number |
| [ ] | input-file-accept | https://caniuse.com/input-file-accept |

- [ ] All 4 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

## 03_attributes/

### form_attributes.html
**Expected features:** `form-validation`, `input-pattern`, `input-placeholder`, `autofocus`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | form-validation | https://caniuse.com/form-validation |
| [ ] | input-pattern | https://caniuse.com/input-pattern |
| [ ] | input-placeholder | https://caniuse.com/input-placeholder |
| [ ] | autofocus | https://caniuse.com/autofocus |

**Attributes tested:** required, pattern, min, max, placeholder, autofocus

- [ ] All 4 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

### loading_attributes.html
**Expected features:** `loading-lazy-attr`, `script-async`, `script-defer`, `subresource-integrity`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | loading-lazy-attr | https://caniuse.com/loading-lazy-attr |
| [ ] | script-async | https://caniuse.com/script-async |
| [ ] | script-defer | https://caniuse.com/script-defer |
| [ ] | subresource-integrity | https://caniuse.com/subresource-integrity |

- [ ] All 4 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

### content_attributes.html
**Expected features:** `contenteditable`, `dragndrop`, `hidden`, `download`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | contenteditable | https://caniuse.com/contenteditable |
| [ ] | dragndrop | https://caniuse.com/dragndrop |
| [ ] | hidden | https://caniuse.com/hidden |
| [ ] | download | https://caniuse.com/download |

- [ ] All 4 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

## 04_attribute_values/

### rel_values.html
**Expected features:** `link-rel-preload`, `link-rel-prefetch`, `link-rel-dns-prefetch`, `link-rel-preconnect`, `link-rel-modulepreload`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | link-rel-preload | https://caniuse.com/link-rel-preload |
| [ ] | link-rel-prefetch | https://caniuse.com/link-rel-prefetch |
| [ ] | link-rel-dns-prefetch | https://caniuse.com/link-rel-dns-prefetch |
| [ ] | link-rel-preconnect | https://caniuse.com/link-rel-preconnect |
| [ ] | link-rel-modulepreload | https://caniuse.com/link-rel-modulepreload |

- [ ] All 5 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

### type_values.html
**Expected features:** `es6-module`, `webm`, `mpeg4`, `mp3`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | es6-module | https://caniuse.com/es6-module |
| [ ] | webm | https://caniuse.com/webm |
| [ ] | mpeg4 | https://caniuse.com/mpeg4 |
| [ ] | mp3 | https://caniuse.com/mp3 |

- [ ] All 4 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

### referrerpolicy_values.html
**Expected features:** `referrer-policy`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | referrer-policy | https://caniuse.com/referrer-policy |

**Values tested:** no-referrer, no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url

- [ ] Feature detected
- [ ] Browser support matches Can I Use
- **Notes:** ___

---

## 05_special_patterns/

### responsive_images.html
**Expected features:** `srcset`, `picture`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | srcset | https://caniuse.com/srcset |
| [ ] | picture | https://caniuse.com/picture |

- [ ] Both features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

### accessibility.html
**Expected features:** `wai-aria`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | wai-aria | https://caniuse.com/wai-aria |

**ARIA attributes tested:** role, aria-label, aria-labelledby, aria-describedby, aria-hidden, aria-expanded, aria-controls, aria-live

- [ ] Feature detected
- [ ] Browser support matches Can I Use
- **Notes:** ___

---

### media_formats.html
**Expected features:** `webm`, `webp`, `avif`, `heif`

| Status | Feature | Can I Use URL |
|--------|---------|---------------|
| [ ] | webm | https://caniuse.com/webm |
| [ ] | webp | https://caniuse.com/webp |
| [ ] | avif | https://caniuse.com/avif |
| [ ] | heif | https://caniuse.com/heif |

- [ ] All 4 features detected
- [ ] Browser support matches for each
- **Notes:** ___

---

## Summary

### Total Features to Validate

| Category | Files | Features |
|----------|-------|----------|
| 01_elements | 4 | 12 |
| 02_input_types | 3 | 7 |
| 03_attributes | 3 | 12 |
| 04_attribute_values | 3 | 10 |
| 05_special_patterns | 3 | 7 |
| **Total** | **16** | **48** |

### Validation Progress

- [ ] 01_elements complete
- [ ] 02_input_types complete
- [ ] 03_attributes complete
- [ ] 04_attribute_values complete
- [ ] 05_special_patterns complete

### Final Results

- **Total features tested:** ___
- **Features passed:** ___
- **Features failed:** ___
- **Accuracy:** ___%

**Validated by:** ___
**Date:** ___
