# LaTeX edits — reduce export formats from 6 to 4

After cutting CSV and Checkstyle XML from the codebase, the thesis text needs to be aligned. Cross Guard now supports **4 export formats**: JSON, PDF, SARIF, JUnit XML.

Below is every line you need to edit in the LaTeX source. Open each file, find the line, and replace it.

---

## Edit 1 — `latex/chapters/impl.tex`

### Line 37

**FIND** (currently in the paragraph that ends Section 3.1):
```latex
Beyond parsing, Cross Guard relies on three additional subsystems. Detected features are looked up in a local copy of the Can I Use database to check browser support, and a scoring algorithm calculates a weighted compatibility score (0--100) and assigns a letter grade (A to F); details are given in Section~\ref{sec:scoring}. Analysis results, bookmarks, tags, and settings are stored in an SQLite database using repository classes, as explained in Section~\ref{sec:database}. Finally, results can be exported in six formats: JSON, PDF, SARIF, JUnit XML, Checkstyle XML, and CSV, with details in Section~\ref{sec:export}.
```

**REPLACE WITH**:
```latex
Beyond parsing, Cross Guard relies on three additional subsystems. Detected features are looked up in a local copy of the Can I Use database to check browser support, and a scoring algorithm calculates a weighted compatibility score (0--100) and assigns a letter grade (A to F); details are given in Section~\ref{sec:scoring}. Analysis results, bookmarks, tags, and settings are stored in an SQLite database using repository classes, as explained in Section~\ref{sec:database}. Finally, results can be exported in four formats: JSON, PDF, SARIF, and JUnit XML, with details in Section~\ref{sec:export}.
```

**Diff**: `six formats: JSON, PDF, SARIF, JUnit XML, Checkstyle XML, and CSV` → `four formats: JSON, PDF, SARIF, and JUnit XML`

---

## Edit 2 — `latex/chapters/user.tex`

### Line 220 (GUI export section)

**FIND**:
```latex
After completing an analysis, the results can be exported as reports. These reports allow the compatibility findings to be shared with other developers or included in documentation and project reports. The GUI supports exporting the results as PDF or JSON files. Additional formats such as SARIF, JUnit XML, Checkstyle XML, and CSV are available through the CLI.
```

**REPLACE WITH**:
```latex
After completing an analysis, the results can be exported as reports. These reports allow the compatibility findings to be shared with other developers or included in documentation and project reports. The GUI supports exporting the results as PDF or JSON files. Additional formats such as SARIF and JUnit XML are available through the CLI.
```

**Diff**: `SARIF, JUnit XML, Checkstyle XML, and CSV` → `SARIF and JUnit XML`

---

### Line 263 (CLI format intro paragraph)

**FIND**:
```latex
The \texttt{analyze} command accepts seven values for its \texttt{-{}-format} flag, summarized in Table~\ref{tab:cli-formats}. Two of them (\texttt{table} and \texttt{summary}) print results directly to the terminal, while the other five write machine-readable output. PDF exports are produced separately through the \texttt{export} command rather than through \texttt{-{}-format}.
```

**REPLACE WITH**:
```latex
The \texttt{analyze} command accepts five values for its \texttt{-{}-format} flag, summarized in Table~\ref{tab:cli-formats}. Two of them (\texttt{table} and \texttt{summary}) print results directly to the terminal, while the other three write machine-readable output. PDF exports are produced separately through the \texttt{export} command rather than through \texttt{-{}-format}.
```

**Diff**:
- `seven values` → `five values`
- `the other five` → `the other three`

---

### Lines 265–281 (Table of formats)

**FIND** (the entire table block):
```latex
\begin{table}[H]
    \centering
    \begin{tabular}{|l|l|}
        \hline
        \textbf{Format} & \textbf{Purpose} \\
        \hline \hline
        Table          & Human-readable terminal output. \\ \hline
        Summary        & A one-line quick compatibility check. \\ \hline
        JSON           & Machine-readable output for scripts and tools. \\ \hline
        SARIF          & Integration with GitHub Code Scanning. \\ \hline
        JUnit XML      & Compatibility with CI systems such as Jenkins or GitLab. \\ \hline
        Checkstyle XML & Integration with static analysis tools such as SonarQube. \\ \hline
        CSV            & Export suitable for spreadsheet analysis or reporting. \\ \hline
    \end{tabular}
    \caption{Output formats supported by the CLI}
    \label{tab:cli-formats}
\end{table}
```

**REPLACE WITH**:
```latex
\begin{table}[H]
    \centering
    \begin{tabular}{|l|l|}
        \hline
        \textbf{Format} & \textbf{Purpose} \\
        \hline \hline
        Table     & Human-readable terminal output. \\ \hline
        Summary   & A one-line quick compatibility check. \\ \hline
        JSON      & Machine-readable output for scripts and tools. \\ \hline
        SARIF     & Integration with GitHub Code Scanning. \\ \hline
        JUnit XML & Compatibility with CI systems such as Jenkins or GitLab. \\ \hline
    \end{tabular}
    \caption{Output formats supported by the CLI}
    \label{tab:cli-formats}
\end{table}
```

**Diff**: delete the two rows for `Checkstyle XML` and `CSV`. The table now has 5 rows instead of 7.

---

### Line 352 (CI tools paragraph)

**FIND**:
```latex
Export formats such as SARIF, JUnit XML, and Checkstyle XML are especially useful when Cross Guard is used in automated environments. Many CI/CD platforms understand these formats and can display compatibility problems directly inside their reporting interfaces.
```

**REPLACE WITH**:
```latex
Export formats such as SARIF and JUnit XML are especially useful when Cross Guard is used in automated environments. Many CI/CD platforms understand these formats and can display compatibility problems directly inside their reporting interfaces.
```

**Diff**: `SARIF, JUnit XML, and Checkstyle XML` → `SARIF and JUnit XML`

---

## Summary of all edits

| File | Line(s) | Change |
|------|---------|--------|
| `chapters/impl.tex` | 37 | "six formats: JSON, PDF, SARIF, JUnit XML, Checkstyle XML, and CSV" → "four formats: JSON, PDF, SARIF, and JUnit XML" |
| `chapters/user.tex` | 220 | "SARIF, JUnit XML, Checkstyle XML, and CSV" → "SARIF and JUnit XML" |
| `chapters/user.tex` | 263 | "seven values…the other five" → "five values…the other three" |
| `chapters/user.tex` | 265–281 | Delete 2 table rows: `Checkstyle XML` and `CSV` |
| `chapters/user.tex` | 352 | "SARIF, JUnit XML, and Checkstyle XML" → "SARIF and JUnit XML" |

**Total: 5 small edits, all in 2 files.**

---

## How to verify after editing

After making these edits, recompile the thesis (`pdflatex` / `latexmk`) and check:

1. The phrase "four formats" appears in Section 3.1 (impl.tex)
2. Table 2.x in user.tex (CLI formats) has only 5 rows (Table, Summary, JSON, SARIF, JUnit XML)
3. The CSV / Checkstyle words no longer appear anywhere in the thesis text:
   ```bash
   grep -ni "checkstyle\|\\bcsv\\b" latex/chapters/*.tex
   ```
   should return nothing (or only false positives — e.g. "css" inside the word "cascading").

---

## What was changed in the codebase (for your reference)

- `src/export/csv_exporter.py` — **deleted**
- `src/export/checkstyle_exporter.py` — **deleted**
- `src/export/__init__.py` — removed 2 imports
- `src/api/service.py` — removed `export_to_csv()` and `export_to_checkstyle()` methods
- `src/cli/main.py` — removed `csv` / `checkstyle` from `--format` choices, removed `--output-csv` / `--output-checkstyle` flags, removed from validation and dispatch
- `tests/export/test_export_blackbox.py` — removed 2 tests
- `CLAUDE.md` — updated all "6 formats" references to "4 formats", test totals 98 → 96, blackbox 68 → 66, export module 7 → 5
- `TEST_COMMANDS.md` — removed CSV/Checkstyle commands

**Test suite: 96/96 passing.**
