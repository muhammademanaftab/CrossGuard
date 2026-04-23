# Thesis fixes — final round

There are **13 small things to fix** across the two thesis chapters and one code-repo doc. Apply one at a time. Each has a **FIND** block (the exact current text) and a **REPLACE with** block (the exact new text).

| Group | What it fixes | Where | How many |
|---|---|---|---|
| A | Test counts are old numbers | impl.tex | 5 edits |
| B | Some places still say "A+ to F" but the app only uses A to F | impl.tex | 3 edits |
| C | A line mentions a method that was deleted | impl.tex | (done by B3) |
| D | The AI section says the old way (before `--ai` flag) | impl.tex | 1 edit |
| E | The risk-level rule doesn't match what the code does | user.tex + impl.tex | 2 edits |
| F | The status-code table has wrong numbers for some letters | impl.tex | 1 edit |
| G | A doc file mentions old methods that don't exist anymore | uml_explained.md | 2 edits |

---

# A — Test counts (5 edits in impl.tex)

The code has **116** tests now, not 111. Table 2 rows also need fixing.

## ✏️ A1 — Line 462

### FIND:
```
Cross Guard includes a comprehensive automated test suite with 111 tests implemented using pytest
```
### REPLACE with:
```
Cross Guard includes a comprehensive automated test suite with 116 tests implemented using pytest
```

## ✏️ A2 — Line 476, Database row

### FIND:
```
        Database      & 3 & 2 & 2 & 7  \\ \hline
```
### REPLACE with:
```
        Database      & 5 & 2 & - & 7  \\ \hline
```

## ✏️ A3 — Line 477, CLI row

### FIND:
```
        CLI           & 4 & 4 & 2 & 10 \\ \hline
```
### REPLACE with:
```
        CLI           & 9 & 4 & 2 & 15 \\ \hline
```

## ✏️ A4 — Line 482, Total row

### FIND:
```
        \textbf{Total} & \textbf{58} & \textbf{34} & \textbf{19} & \textbf{111} \\ \hline
```
### REPLACE with:
```
        \textbf{Total} & \textbf{65} & \textbf{34} & \textbf{17} & \textbf{116} \\ \hline
```

## ✏️ A5 — Line 525

### FIND:
```
The current test suite successfully executes all 111 automated tests in approximately under a second
```
### REPLACE with:
```
The current test suite successfully executes all 116 automated tests in approximately under a second
```

---

# B — "A+ to F" → "A to F" (3 edits in impl.tex)

The old 13-level grade scale is gone. The app only gives out A, B, C, D, F now.

## ✏️ B1 — Line 14

### FIND:
```
    \item Assign a letter grade from A+ to F.
```
### REPLACE with:
```
    \item Assign a letter grade from A to F.
```

## ✏️ B2 — Line 37

### FIND:
```
a scoring algorithm calculates a weighted compatibility score (0--100) and assigns a letter grade (A+ to F); details are given in Section~\ref{sec:scoring}.
```
### REPLACE with:
```
a scoring algorithm calculates a compatibility score (0--100) and assigns a letter grade (A to F); details are given in Section~\ref{sec:scoring}.
```

## ✏️ B3 — Line 106 (also fixes Group C)

This sentence also mentions `calculate_weighted_score()` — that method was deleted. The replacement removes it too.

### FIND:
```
\texttt{CompatibilityScorer} then takes these results and calculates a score from 0 to 100 along with a letter grade from A+ to F. The methods \texttt{calculate\_simple\_score()} and \texttt{calculate\_weighted\_score()} handle this computation.
```
### REPLACE with:
```
After gathering these results, Cross Guard calculates a score from 0 to 100 in \texttt{src/analyzer/main.py} and assigns a letter grade from A to F. A small helper called \texttt{calculate\_simple\_score()} on \texttt{CompatibilityScorer} is used for per-browser scoring.
```

---

# C — (handled by B3)

B3's replacement already removes the deleted method name. Nothing extra needed.

---

# D — AI section in CLI paragraph (1 edit in impl.tex)

The old text says "just pass `--api-key` to turn AI on". That's not how it works anymore — you need `--ai`.

## ✏️ D1 — Line 284

### FIND:
```
In the GUI, a ``Get AI Suggestions'' button appears in the Issues section of the results dashboard. The API call only happens when the user clicks this button, not during the analysis itself, which avoids unnecessary API calls and keeps analysis fast. The request runs in a background thread so the interface stays responsive while waiting for a response. In the CLI, the \texttt{-{}-api-key} and \texttt{-{}-ai-provider} flags enable AI suggestions. When provided, an ``AI Fix Suggestions'' section is appended to the end of the output.
```

### REPLACE with:
```
In the GUI, a ``Get AI Suggestions'' button appears in the Issues section of the results dashboard. The API call only happens when the user clicks this button, not during the analysis itself, which avoids unnecessary API calls and keeps analysis fast. The request runs in the background so the interface stays responsive while waiting for a response. In the CLI, AI suggestions have to be turned on for each run with the \texttt{-{}-ai} flag on the \texttt{analyze} command. When \texttt{-{}-ai} is used, the CLI looks for the API key in three places: the \texttt{-{}-api-key} flag, the \texttt{CROSSGUARD\_AI\_KEY} environment variable, and the key saved through \texttt{config -{}-set-api-key}. If no key is found, the CLI shows a warning and the analysis continues without AI. Without \texttt{-{}-ai}, the CLI never calls the AI service, even if a key is available.
```

---

# E — Risk level rule (2 edits, one in each chapter)

The code actually decides risk level from the **score**, not from how many browsers are failing. Both chapters describe the wrong rule. These fixes make the docs match the code.

What the code really does (`src/analyzer/main.py`):
- No unsupported features → `none`
- Score is 80 or above → `low`
- Score is 60 to 79 → `medium`
- Score below 60 → `high`

## ✏️ E1 — user.tex, line 153

### FIND:
```
A risk level is also assigned based on the number of unsupported features, categorized as none (no issues detected), low (only partial support issues), medium (some features are unsupported), or high (more than half of the target browsers lack support).
```
### REPLACE with:
```
The app also gives each analysis a risk level based on the compatibility score: \texttt{none} when no features are unsupported, \texttt{low} when the score is 80 or above, \texttt{medium} for scores between 60 and 79, and \texttt{high} for scores below 60.
```

## ✏️ E2 — impl.tex, line 197

### FIND:
```
Alongside the numeric score, the analyzer categorises each analysis into a risk level based on unsupported features: \texttt{none} if no unsupported or partial features exist, \texttt{low} if only partial support issues are found, \texttt{medium} if some features are unsupported in fewer than half the browsers, and \texttt{high} if more than half of the browsers lack support (e.g. 3 of 5 target browsers don't support \texttt{css-container-queries} $\to$ high risk).
```
### REPLACE with:
```
Alongside the score, each analysis is tagged with a risk level based on the score itself: \texttt{none} when there are no unsupported features, \texttt{low} when the score is 80 or above, \texttt{medium} for scores between 60 and 79, and \texttt{high} for scores below 60. For example, a file that scores 45 with unsupported features falls into the \texttt{high} bucket.
```

---

# F — Status-code table in impl.tex (1 edit, lines 180 to 195)

The current table puts `a` (almost supported) in the 100-point row, but the code actually treats it as 50 (partial). It also puts `p` in the 50-point row, but the code doesn't score `p` at all. This fix matches the table to the code.

## ✏️ F1 — Replace the whole table

**Why this shape:** keeps the same 3 rows (matching the intro sentence "supported, partially supported, or unsupported"), just fixes the rows that had letters in the wrong place — `a` moves from the 100 row to the 50 row, and the bottom row now covers `n` plus everything else the code doesn't recognise.

### FIND:
```
\begin{table}[H]
    \centering
    \begin{tabular}{|c|l|c|}
        \hline
        \textbf{Status Codes} & \textbf{Meaning} & \textbf{Contribution} \\
        \hline \hline
        y, a & Supported & 100 \\
        \hline
        x, p & Partial support & 50 \\
        \hline
        d, n, u & Unsupported or unknown & 0 \\
        \hline
    \end{tabular}
    \caption{Can I Use status codes and their contribution to the score}
    \label{tab:status-scores}
\end{table}
```

### REPLACE with:
```
\begin{table}[H]
    \centering
    \begin{tabular}{|c|l|c|}
        \hline
        \textbf{Status Codes} & \textbf{Meaning} & \textbf{Contribution} \\
        \hline \hline
        y & Supported & 100 \\
        \hline
        a, x & Partial support or needs a vendor prefix & 50 \\
        \hline
        n (or any other code) & Unsupported or unknown & 0 \\
        \hline
    \end{tabular}
    \caption{Can I Use status codes and their contribution to the score}
    \label{tab:status-scores}
\end{table}
```

---

# G — UML doc (2 edits)

**File:** `Code/docs/diagrams/uml_explained.md` — this is not the thesis, it's a code-repo doc. If you say so, I can edit it directly instead of you doing it.

## ✏️ G1 — CompatibilityScorer description

### FIND:
```
**CompatibilityScorer** -- Takes support data and calculates: a simple score (0-100 average), a weighted score (browsers weighted by importance), and a compatibility index with letter grade (A+ through F).
```
### REPLACE with:
```
**CompatibilityScorer** -- Holds the `STATUS_SCORES` table that maps each Can I Use status code to a point value (y/a → 100, x/p → 50, d/n/u → 0), plus a small `calculate_simple_score()` helper. The overall score and letter grade (A, B, C, D, F) are computed inside `CrossGuardAnalyzer` in `src/analyzer/main.py`.
```

## ✏️ G2 — AnalyzerService method count

### FIND:
```
**AnalyzerService** -- The facade. This is the ONE class that both frontends talk to. It has 28 public methods covering
```
### REPLACE with:
```
**AnalyzerService** -- The facade. This is the ONE class that both frontends talk to. It has around 60 public methods covering
```

---

# Don't touch these (they're already correct)

- The grade-scale table in user.tex (A/B/C/D/F with ranges) — matches the code
- The scoring paragraph in user.tex — matches the code
- The polyfill naming ("Recommendations") in both chapters — correct
- The AI CLI subsection in user.tex — already updated
- The `update-db` NPM-registry text — correct
- The export-format count (6 formats) — correct
- Anything in other chapters (intro, summary)
- Any code block (`lstlisting`) not listed above
- Any figure or caption

---

# Checklist

```
A — Test counts (impl.tex, 5 edits):
  [ ] A1   "111 tests" → "116 tests"              line 462
  [ ] A2   Table 2 Database row                   line 476
  [ ] A3   Table 2 CLI row                        line 477
  [ ] A4   Table 2 Total row                      line 482
  [ ] A5   "all 111" → "all 116"                  line 525

B — "A+ to F" → "A to F" (impl.tex, 3 edits):
  [ ] B1   Line 14
  [ ] B2   Line 37
  [ ] B3   Line 106 (also removes deleted method name)

D — AI CLI paragraph (impl.tex, 1 edit):
  [ ] D1   Line 284

E — Risk-level rule (2 edits):
  [ ] E1   user.tex line 153
  [ ] E2   impl.tex line 197

F — Status-code table (impl.tex, 1 edit):
  [ ] F1   Lines 180-195

G — UML doc (2 edits, not LaTeX):
  [ ] G1   CompatibilityScorer description
  [ ] G2   AnalyzerService method count
```

**Total: 13 small edits.** Ping me when done and I'll check.
