# LaTeX edits to apply

Each entry is a pure find-and-replace against the thesis source. The left column is what currently exists; the right column is what it should become. File paths are relative to the `LaTeX/` directory.

All edits below are the reconciliation of the thesis text with the cleaned-up code after the module-by-module audit (analyzer, api, cli, config, database, gui, parsers, polyfill, utils, export). If an item is marked **Optional**, the thesis is not literally wrong without it — it's a tighter-alignment polish.

---

## 1. Text edits

### Edit 1 — `chapters/user.tex` line 196 — remove "or tagged"

**Why:** tagging creation exists in code, but no UI lets a user attach a tag to a specific analysis, so this sentence overstates the feature.

**FIND:**
```
...Analyses can also be bookmarked or tagged for easier organization, making it simple to return to important results later.
```

**REPLACE with:**
```
...Analyses can also be bookmarked for easier organization, making it simple to return to important results later.
```

---

### Edit 2 — `chapters/impl.tex` line 110 — remove "add tags,"

**Why:** same as Edit 1 — no tag-attach control in the Results view.

**FIND:**
```
Users can also bookmark the result, add tags, or export it as a report.
```

**REPLACE with:**
```
Users can also bookmark the result or export it as a report.
```

---

### Edit 3 — `chapters/impl.tex` line 213 — fix StatisticsService metrics list

**Why:** `StatisticsService.get_score_trend()` was deleted (it had zero callers). `sum.tex:28` already lists trend charts as future work, so the two sentences used to contradict each other — after this edit they agree.

**FIND:**
```
...\texttt{StatisticsService} queries the same database to provide metrics such as average scores, score trends, and grade distribution.
```

**REPLACE with:**
```
...\texttt{StatisticsService} queries the same database to provide metrics such as average/best/worst scores, grade distribution, and file-type distribution.
```

---

### Edit 4 — `chapters/impl.tex` line 219 — remove "and attach a note"

**Why:** the `Bookmark` dataclass still has a `note` column and the API accepts a note at creation, but no UI lets a user edit that note afterwards.

**FIND:**
```
On the left, \texttt{Bookmark} references an \texttt{Analysis} through a solid line. Users can bookmark any analysis and attach a note.
```

**REPLACE with:**
```
On the left, \texttt{Bookmark} references an \texttt{Analysis} through a solid line. Users can bookmark any analysis.
```

---

### Edit 5 — `chapters/impl.tex` line 106 — rewrite scoring sentence

**Why:** `calculate_simple_score()` no longer exists. Scoring was refactored around a `STATUS_SCORES` lookup table (Arch B) and four helper methods on `CompatibilityScorer`. The sentence has to describe the new shape.

**FIND:**
```
The scoring module in \texttt{src/analyzer/main.py} then takes these results and calculates a score from 0 to 100 along with a letter grade from A to F. The \texttt{calculate\_simple\_score()} helper on \texttt{CompatibilityScorer} exposes the per-browser contribution logic used during this computation.
```

**REPLACE with:**
```
After gathering these results, the scoring work is delegated to the \texttt{CompatibilityScorer} class in \texttt{src/analyzer/scorer.py}. At its core is a \texttt{STATUS\_SCORES} lookup table that maps each Can I Use status code to a point contribution out of 100 ('y' = 100, 'a'/'x' = 50, everything else = 0), making the scoring policy a single edit away. \texttt{score\_statuses()} averages those points over all checked features for one browser, \texttt{overall\_score()} averages across browsers into a single number from 0 to 100, \texttt{grade()} maps that score to a letter grade from A to F, and \texttt{risk\_level()} tags the analysis as \texttt{none}, \texttt{low}, \texttt{medium}, or \texttt{high}.
```

---

### Edit 6 — `chapters/impl.tex` line 271 — drop `has_polyfill` / `is_polyfillable` references

**Why:** both methods were deleted from `PolyfillLoader` (zero callers anywhere). Only `get_polyfill` survives as the public lookup. The regenerated `cg_polyfill.png` (once promoted from `_after`) also reflects this.

**FIND:**
```
\texttt{PolyfillLoader} follows the singleton pattern, meaning the JSON file is read only once through the private \texttt{\_load\_data()} method and stored in \texttt{\_data}. Its public methods handle straightforward lookups in a way that \texttt{get\_polyfill(feature\_id)} returns the mapping for a given feature, or \texttt{None} if no match is found; \texttt{has\_polyfill()} checks whether any polyfill or fallback is available; and \texttt{is\_polyfillable()} checks specifically for JavaScript polyfills.
```

**REPLACE with:**
```
\texttt{PolyfillLoader} follows the singleton pattern, meaning the JSON file is read only once through the private \texttt{\_load\_data()} method and stored in \texttt{\_data}. Its public \texttt{get\_polyfill(feature\_id)} method returns the mapping for a given feature, or \texttt{None} if no match is found; callers inspect the returned dictionary themselves to decide whether to use a JavaScript polyfill or a CSS fallback.
```

---

### Edit 7 (Optional) — `chapters/user.tex` line 131 — align BuildBadge description

**Why:** cosmetic drift. The `BuildBadge` widget actually renders three states (`PASSING` / `WARNING` / `FAILING`, in uppercase, without the `Compatibility:` prefix). Not literally wrong but tightens alignment.

**FIND:**
```
Compatibility: Passing (or Failing, depending on the score)
```

**REPLACE with:**
```
PASSING, WARNING, or FAILING (depending on the score)
```

---

## 2. Image replacements

The `LaTeX/images/` directory currently holds frozen "before" snapshots and refreshed "after" renders alongside each canonical PNG. `\includegraphics{cg_X}` still resolves because the canonical filename is unchanged; promotion is just a rename.

| Canonical filename | Rename this file to it |
|---|---|
| `cg_pipeline.png` (currently deleted) | `cg_pipeline_after.png` |
| `cg_database.png` | `cg_database_after.png` |
| `cg_gui.png` | `cg_gui_after.png` |
| `cg_parsers.png` | `cg_parsers_after.png` |
| `cg_polyfill.png` | `cg_polyfill_after.png` |

After each rename, the matching `cg_X_before.png` can stay in-repo as an archival record or be deleted — whichever you prefer.

---

## 3. External diagram — `LaTeX/images/cg_sequence.png`

The sequence diagram was authored externally (no `Code/docs/diagrams/scripts/` source exists for it), so this one needs to be edited in whichever tool produced it.

**Two message labels are out of date and need to change:**

1. `CrossGuardAnalyzer → CompatibilityAnalyzer: analyze(features, browsers)`
   → should become `classify_features(features, browsers)`

2. `CrossGuardAnalyzer → CompatibilityScorer: calculate_weighted_score(status)`
   → this method never existed after the Arch B refactor. The scorer is now driven by a `STATUS_SCORES` lookup and four helpers (`score_statuses`, `overall_score`, `grade`, `risk_level`). Replace with either:
   - one simplified arrow labelled `score_statuses / overall_score / grade / risk_level`, returning `score + grade`, or
   - four arrows (one per helper) if you want the full picture.

---

## 4. Quick checklist

```
[ ] Edit 1 — chapters/user.tex line 196 (remove "or tagged")
[ ] Edit 2 — chapters/impl.tex line 110 (remove "add tags,")
[ ] Edit 3 — chapters/impl.tex line 213 (StatisticsService metrics list)
[ ] Edit 4 — chapters/impl.tex line 219 (remove "and attach a note")
[ ] Edit 5 — chapters/impl.tex line 106 (scoring sentence rewrite)
[ ] Edit 6 — chapters/impl.tex line 271 (drop has_polyfill/is_polyfillable)
[ ] (Optional) Edit 7 — chapters/user.tex line 131 (BuildBadge states)
[ ] Rename images/cg_pipeline_after.png  → images/cg_pipeline.png
[ ] Rename images/cg_database_after.png  → images/cg_database.png
[ ] Rename images/cg_gui_after.png       → images/cg_gui.png
[ ] Rename images/cg_parsers_after.png   → images/cg_parsers.png
[ ] Rename images/cg_polyfill_after.png  → images/cg_polyfill.png
[ ] Update images/cg_sequence.png in external editor (two message relabels)
```
