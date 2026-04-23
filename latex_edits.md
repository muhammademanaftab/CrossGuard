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
...Analyses can also be bookmarked, so it is easy to come back to important results later.
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
...\texttt{StatisticsService} reads from the same database to show numbers like the average, best, and worst scores, the grade distribution, and the file-type distribution.
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
Once the results are ready, the scoring is handed over to the \texttt{CompatibilityScorer} class in \texttt{src/analyzer/scorer.py}. This class is built around a \texttt{STATUS\_SCORES} lookup table that gives each Can I Use status code a score out of 100 ('y' is 100, 'a' and 'x' are 50, and everything else is 0), so the scoring rules can be changed in one place. The \texttt{score\_statuses()} method takes the average of these points for one browser, \texttt{overall\_score()} then averages the browser scores into a single number from 0 to 100, \texttt{grade()} turns that number into a letter grade from A to F, and \texttt{risk\_level()} labels the result as \texttt{none}, \texttt{low}, \texttt{medium}, or \texttt{high} risk.
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
\texttt{PolyfillLoader} follows the singleton pattern, which means the JSON file is read only once through the private \texttt{\_load\_data()} method and then kept in \texttt{\_data}. Its public \texttt{get\_polyfill(feature\_id)} method returns the mapping for a given feature, or \texttt{None} if no match is found. The caller then looks at the returned dictionary and decides whether to use a JavaScript polyfill or a CSS fallback.
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
PASSING, WARNING, or FAILING, depending on the score
```

---

## 2. Image replacements — DONE

All 7 updated diagrams are now the canonical versions in `LaTeX/images/`, and the old snapshots have been archived in `LaTeX/images/before/`.

**`LaTeX/images/`** (main folder — what the thesis uses):
- `cg_pipeline.png` — new (pipeline diagram with parsers showing 3 public methods)
- `cg_database.png` — new (StatisticsService trimmed to 11 methods)
- `cg_gui.png` — new (AnalyzerService at 49 methods, all bypasses removed)
- `cg_parsers.png` — new (parsers at 3 public methods each)
- `cg_polyfill.png` — new (only `get_polyfill` + `reload` shown)
- `cg_directory.png` — new (49 methods, 22 widgets, utils description fixed)
- `cg_sequence.png` — new (`classify_features` + 4 scorer messages)
- `cg_ai.png`, `cg_architecture.png`, `cg_usecase.png` — unchanged (never needed updating)
- `cg_cli_*.png`, `cg_gui_dashboard/rules/settings/upload.png` — screenshots, unchanged

**`LaTeX/images/before/`** (archive — frozen old snapshots for historical reference):
- `cg_pipeline.png`, `cg_database.png`, `cg_gui.png`, `cg_parsers.png`, `cg_polyfill.png`, `cg_directory.png`, `cg_sequence.png`

Nothing in the thesis references the `before/` folder; it's only there in case you ever need to compare old vs new.

---

## 3. Quick checklist

```
[x] Edit 1 — chapters/user.tex line 196 (remove "or tagged")
[x] Edit 2 — chapters/impl.tex line 110 (remove "add tags,")
[x] Edit 3 — chapters/impl.tex line 213 (StatisticsService metrics list)
[x] Edit 4 — chapters/impl.tex line 219 (remove "and attach a note")
[x] Edit 5 — chapters/impl.tex line 106 (scoring sentence rewrite)
[x] Edit 6 — chapters/impl.tex line 271 (drop has_polyfill/is_polyfillable)
[ ] (Optional) Edit 7 — chapters/user.tex line 131 (BuildBadge states)
[x] All 7 diagram images promoted to canonical; old snapshots archived in images/before/
```

Everything the thesis needs is now in place. Only Edit 7 remains, and it is optional (cosmetic phrasing of the PASSING/WARNING/FAILING banner).
