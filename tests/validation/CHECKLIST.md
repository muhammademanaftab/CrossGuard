# Manual Validation Checklist

## Instructions

Mark each item as you complete validation:

- `[ ]` = Not tested
- `[x]` = Passed (matches caniuse.com)
- `[!]` = Failed (add notes below)
- `[~]` = Partial (minor discrepancy)

**Tested by:** **\*\***\_\_\_**\*\***
**Date started:** **\*\***\_\_\_**\*\***
**Date completed:** **\*\***\_\_\_**\*\***

---

## Summary

| Category            | Files  | Features | Passed | Failed | Partial |
| ------------------- | ------ | -------- | ------ | ------ | ------- |
| 01_elements         | 4      | 18       |        |        |         |
| 02_input_types      | 3      | 12       |        |        |         |
| 03_attributes       | 3      | 15       |        |        |         |
| 04_attribute_values | 3      | 12       |        |        |         |
| 05_special_patterns | 3      | 10       |        |        |         |
| **TOTAL**           | **16** | **67**   |        |        |         |

---

## 01_elements/

### semantic_elements.html

**Expected Can I Use IDs:** `html5semantic`

| Feature        | Detected | ID Correct | Support Matches | Status |
| -------------- | -------- | ---------- | --------------- | ------ |
| `<main>`       | [ ]      | [ ]        | [ ]             |        |
| `<section>`    | [ ]      | [ ]        | [ ]             |        |
| `<article>`    | [ ]      | [ ]        | [ ]             |        |
| `<aside>`      | [ ]      | [ ]        | [ ]             |        |
| `<header>`     | [ ]      | [ ]        | [ ]             |        |
| `<footer>`     | [ ]      | [ ]        | [ ]             |        |
| `<nav>`        | [ ]      | [ ]        | [ ]             |        |
| `<figure>`     | [ ]      | [ ]        | [ ]             |        |
| `<figcaption>` | [ ]      | [ ]        | [ ]             |        |
| `<time>`       | [ ]      | [ ]        | [ ]             |        |
| `<mark>`       | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***
In html5 semantic its detecting 2 features
Html5Semnatic and viewport units. Corrected

---

### media_elements.html

**Expected Can I Use IDs:** `video`, `audio`, `picture`, `canvas`, `webvtt`

| Feature            | Detected | ID Correct | Support Matches | Status |
| ------------------ | -------- | ---------- | --------------- | ------ |
| `<video>`          | [ ]      | [ ]        | [ ]             |        |
| `<audio>`          | [ ]      | [ ]        | [ ]             |        |
| `<picture>`        | [ ]      | [ ]        | [ ]             |        |
| `<canvas>`         | [ ]      | [ ]        | [ ]             |        |
| `<track>` (WebVTT) | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### interactive_elements.html

**Expected Can I Use IDs:** `dialog`, `details`, `template`

| Feature      | Detected | ID Correct | Support Matches | Status |
| ------------ | -------- | ---------- | --------------- | ------ |
| `<dialog>`   | [ ]      | [ ]        | [ ]             |        |
| `<details>`  | [ ]      | [ ]        | [ ]             |        |
| `<summary>`  | [ ]      | [ ]        | [ ]             |        |
| `<template>` | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### form_elements.html

**Expected Can I Use IDs:** `datalist`, `meter`, `progress`, `output-element`

| Feature      | Detected | ID Correct | Support Matches | Status |
| ------------ | -------- | ---------- | --------------- | ------ |
| `<datalist>` | [ ]      | [ ]        | [ ]             |        |
| `<meter>`    | [ ]      | [ ]        | [ ]             |        |
| `<progress>` | [ ]      | [ ]        | [ ]             |        |
| `<output>`   | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

## 02_input_types/

### datetime_inputs.html

**Expected Can I Use IDs:** `input-datetime`

**Note:** All 5 input types (date, time, datetime-local, month, week) map to the SAME Can I Use feature `input-datetime`. Verify the single feature detection and browser support.

| Feature                 | Maps To        | Detected | Support Matches | Status |
| ----------------------- | -------------- | -------- | --------------- | ------ |
| `type="date"`           | input-datetime | [ ]      | [ ]             |        |
| `type="time"`           | input-datetime | [ ]      | [ ]             |        |
| `type="datetime-local"` | input-datetime | [ ]      | [ ]             |        |
| `type="month"`          | input-datetime | [ ]      | [ ]             |        |
| `type="week"`           | input-datetime | [ ]      | [ ]             |        |

**Validation:** If Cross Guard shows "Date/Time Input" (input-datetime), mark all 5 as detected.

**Notes:** \_\_\_

---

### text_inputs.html

**Expected Can I Use IDs:** `input-email-tel-url`, `input-search`

| Feature         | Detected | ID Correct | Support Matches | Status |
| --------------- | -------- | ---------- | --------------- | ------ |
| `type="email"`  | [ ]      | [ ]        | [ ]             |        |
| `type="tel"`    | [ ]      | [ ]        | [ ]             |        |
| `type="url"`    | [ ]      | [ ]        | [ ]             |        |
| `type="search"` | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### other_inputs.html

**Expected Can I Use IDs:** `input-color`, `input-range`, `input-number`, `input-file-accept`

| Feature                   | Detected | ID Correct | Support Matches | Status |
| ------------------------- | -------- | ---------- | --------------- | ------ |
| `type="color"`            | [ ]      | [ ]        | [ ]             |        |
| `type="range"`            | [ ]      | [ ]        | [ ]             |        |
| `type="number"`           | [ ]      | [ ]        | [ ]             |        |
| `type="file"` with accept | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

## 03_attributes/

### form_attributes.html

**Expected Can I Use IDs:** `form-validation`, `input-pattern`, `input-placeholder`, `autofocus`

| Feature       | Detected | ID Correct | Support Matches | Status |
| ------------- | -------- | ---------- | --------------- | ------ |
| `required`    | [ ]      | [ ]        | [ ]             |        |
| `pattern`     | [ ]      | [ ]        | [ ]             |        |
| `min`         | [ ]      | [ ]        | [ ]             |        |
| `max`         | [ ]      | [ ]        | [ ]             |        |
| `placeholder` | [ ]      | [ ]        | [ ]             |        |
| `autofocus`   | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### loading_attributes.html

**Expected Can I Use IDs:** `loading-lazy-attr`, `script-async`, `script-defer`, `subresource-integrity`

| Feature          | Detected | ID Correct | Support Matches | Status |
| ---------------- | -------- | ---------- | --------------- | ------ |
| `loading="lazy"` | [ ]      | [ ]        | [ ]             |        |
| `async`          | [ ]      | [ ]        | [ ]             |        |
| `defer`          | [ ]      | [ ]        | [ ]             |        |
| `integrity`      | [ ]      | [ ]        | [ ]             |        |
| `crossorigin`    | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### content_attributes.html

**Expected Can I Use IDs:** `contenteditable`, `dragndrop`, `hidden`, `download`

| Feature           | Detected | ID Correct | Support Matches | Status |
| ----------------- | -------- | ---------- | --------------- | ------ |
| `contenteditable` | [ ]      | [ ]        | [ ]             |        |
| `draggable`       | [ ]      | [ ]        | [ ]             |        |
| `hidden`          | [ ]      | [ ]        | [ ]             |        |
| `download`        | [ ]      | [ ]        | [ ]             |        |
| `spellcheck`      | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

## 04_attribute_values/

### rel_values.html

**Expected Can I Use IDs:** `link-rel-preload`, `link-rel-prefetch`, `link-rel-dns-prefetch`, `link-rel-preconnect`, `link-rel-modulepreload`

| Feature               | Detected | ID Correct | Support Matches | Status |
| --------------------- | -------- | ---------- | --------------- | ------ |
| `rel="preload"`       | [ ]      | [ ]        | [ ]             |        |
| `rel="prefetch"`      | [ ]      | [ ]        | [ ]             |        |
| `rel="dns-prefetch"`  | [ ]      | [ ]        | [ ]             |        |
| `rel="preconnect"`    | [ ]      | [ ]        | [ ]             |        |
| `rel="modulepreload"` | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### type_values.html

**Expected Can I Use IDs:** `es6-module`, `webm`, `mpeg4`, `mp3`, `ogg-vorbis`

| Feature             | Detected | ID Correct | Support Matches | Status |
| ------------------- | -------- | ---------- | --------------- | ------ |
| `type="module"`     | [ ]      | [ ]        | [ ]             |        |
| `type="video/webm"` | [ ]      | [ ]        | [ ]             |        |
| `type="video/mp4"`  | [ ]      | [ ]        | [ ]             |        |
| `type="audio/mpeg"` | [ ]      | [ ]        | [ ]             |        |
| `type="audio/ogg"`  | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### referrerpolicy_values.html

**Expected Can I Use IDs:** `referrer-policy`

| Feature                          | Detected | ID Correct | Support Matches | Status |
| -------------------------------- | -------- | ---------- | --------------- | ------ |
| `referrerpolicy="no-referrer"`   | [ ]      | [ ]        | [ ]             |        |
| `referrerpolicy="origin"`        | [ ]      | [ ]        | [ ]             |        |
| `referrerpolicy="strict-origin"` | [ ]      | [ ]        | [ ]             |        |
| `referrerpolicy="same-origin"`   | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

## 05_special_patterns/

### responsive_images.html

**Expected Can I Use IDs:** `srcset`, `picture`

| Feature               | Detected | ID Correct | Support Matches | Status |
| --------------------- | -------- | ---------- | --------------- | ------ |
| `srcset` attribute    | [ ]      | [ ]        | [ ]             |        |
| `sizes` attribute     | [ ]      | [ ]        | [ ]             |        |
| `<picture>` element   | [ ]      | [ ]        | [ ]             |        |
| `<source>` in picture | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### accessibility.html

**Expected Can I Use IDs:** `wai-aria`

| Feature            | Detected | ID Correct | Support Matches | Status |
| ------------------ | -------- | ---------- | --------------- | ------ |
| `role` attribute   | [ ]      | [ ]        | [ ]             |        |
| `aria-label`       | [ ]      | [ ]        | [ ]             |        |
| `aria-hidden`      | [ ]      | [ ]        | [ ]             |        |
| `aria-describedby` | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

### media_formats.html

**Expected Can I Use IDs:** `webm`, `webp`, `avif`, `heif`

| Feature           | Detected | ID Correct | Support Matches | Status |
| ----------------- | -------- | ---------- | --------------- | ------ |
| WebM video format | [ ]      | [ ]        | [ ]             |        |
| WebP image format | [ ]      | [ ]        | [ ]             |        |
| AVIF image format | [ ]      | [ ]        | [ ]             |        |
| HEIF image format | [ ]      | [ ]        | [ ]             |        |

**Notes:** **\*\***\_\_\_**\*\***

---

## Final Verification

- [ ] All 16 HTML test files processed in Cross Guard
- [ ] All features marked in checklist above
- [ ] Discrepancies documented in notes
- [ ] Results logged in `results/validation_log.md`
- [ ] Summary table at top updated with counts

## Sign-off

**Validation completed:** [ ] Yes [ ] No
**Overall accuracy:** **\_**%
**Comments:** **\*\***\_\_\_**\*\***
