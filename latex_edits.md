# LaTeX edits to apply

Each entry is a pure find-and-replace against the thesis source. The left column is what currently exists; the right column is what it should become. File paths are relative to the `LaTeX/` directory.

---

## Edit 7 — `chapters/user.tex` line 131 — describe BuildBadge states with actual thresholds

**Why:** three problems in one sentence — (1) the "Compatibility:" prefix doesn't appear in the actual UI, (2) the sentence only mentions Passing and Failing but the badge has three states (PASSING / WARNING / FAILING, verified in `build_badge.py:38-58`), (3) "depending on the score" tells the reader nothing about when each state is triggered.

**FIND:**
```
labelled \emph{Compatibility: Passing} (or \emph{Failing}, depending on the score), a progress bar
```

**REPLACE with:**
```
reading \emph{PASSING} when the score is 90 or above, \emph{WARNING} when it is between 70 and 89, and \emph{FAILING} when it is below 70, a progress bar
```

---

## Edit 12 — `chapters/user.tex` line 320 — align with unified save behaviour

**Why:** the old sentence said "Just like the GUI, the CLI can access the history" and "Each analysis performed through the tool can be saved and later reviewed" — both misleading before the recent code fix (CLI never saved; "can be" was vague). After the two code changes (GUI toggle now actually gates the save, and CLI analyze now saves to history under the same setting), both frontends save automatically by default, and the doc should say so clearly.

**FIND:**
```
Just like the GUI, the CLI can access the history stored in the SQLite database. Each analysis performed through the tool can be saved and later reviewed. The \texttt{history} command lists previously recorded analyses and displays information such as the file name, compatibility score, and date of execution. The \texttt{stats} command provides aggregated statistics across all stored analyses, summarizing overall results and frequently failing features.
```

**REPLACE with:**
```
Analyses from both the GUI and the CLI are automatically stored in the SQLite database and can be reviewed later. This is controlled by the \emph{Auto-save to history} setting on the Settings page (enabled by default). The \texttt{history} command lists previously recorded analyses and displays information such as the file name, compatibility score, and date of execution. The \texttt{stats} command provides aggregated statistics across all stored analyses, summarizing overall results and frequently failing features.
```

---

## Checklist

```
[ ] Edit 7  — chapters/user.tex line 131 (BuildBadge states with thresholds)
[ ] Edit 12 — chapters/user.tex line 320 (GUI+CLI save consistency)
```
