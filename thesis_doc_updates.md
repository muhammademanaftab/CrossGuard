# Thesis updates — CLI `--ai` flag + key management

The CLI now gates AI suggestions behind an explicit `--ai` flag, and adds key-management flags on the `config` command. This doc lists **every thesis edit** needed to reflect the new behavior.

Apply each in order. Each has exact **FIND** / **REPLACE with** blocks.

---

# PART A — user.tex changes

**File:** `LaTeX/chapters/user.tex`

## ✏️ Edit 1 — Rewrite AI Fix Suggestions (CLI) subsection (line ~296 onward)

### FIND this exact paragraph + lstlisting + paragraph block:

```
The CLI also supports AI-generated fix suggestions through two optional flags. The \texttt{-{}-api-key} flag provides the API key for the language model service, and the \texttt{-{}-ai-provider} flag selects the provider (\texttt{anthropic} or \texttt{openai}, with \texttt{none} used as the default). The same key can also be set as an environment variable to avoid including it in every command, as shown in Listing~\ref{src:ai-cli}.

\begin{lstlisting}[caption={Enable AI fix suggestions via flags or environment variable}, label=src:ai-cli, basicstyle=\ttfamily\small, breaklines=true]
# Pass the API key directly on the command line
python -m src.cli.main analyze style.css --format table --api-key sk-... --ai-provider openai

# Or set it once as an environment variable
export CROSSGUARD_AI_KEY=sk-...
python -m src.cli.main analyze style.css --format table
\end{lstlisting}

When an API key is provided and the analysis detects unsupported or partially supported features, the CLI adds an ``AI Fix Suggestions'' section at the end of the output. Each suggestion includes the feature name, a short explanation of the recommended fix, and a code example showing how it can be implemented. If no API key is provided, the analysis runs normally without generating AI suggestions. The feature is completely optional and does not change the standard analysis output.
```

### REPLACE with:

```
AI fix suggestions on the CLI are off by default and must be turned on for each run with the \texttt{-{}-ai} flag, mirroring the ``Get AI Suggestions'' button in the GUI. This prevents accidental API calls when a key is saved on the machine. When \texttt{-{}-ai} is used, the CLI looks for an API key in this order: the \texttt{-{}-api-key} flag, the \texttt{CROSSGUARD\_AI\_KEY} environment variable, and finally the key stored in local settings (saved via \texttt{config -{}-set-api-key}). If no key is found, the CLI prints a warning and continues the analysis without AI suggestions.

\begin{lstlisting}[caption={Enable AI fix suggestions per run with \texttt{-{}-ai}}, label=src:ai-cli, basicstyle=\ttfamily\small, breaklines=true]
# Save the API key once (prompts with hidden input if no value is given)
python -m src.cli.main config --set-api-key sk-...
python -m src.cli.main config --set-ai-provider anthropic

# Each analysis that needs AI explicitly opts in with --ai
python -m src.cli.main analyze style.css --format table --ai

# Override the saved key for a single run
python -m src.cli.main analyze style.css --format table --ai --api-key sk-other

# Clear the saved key when no longer needed
python -m src.cli.main config --clear-api-key
\end{lstlisting}

When \texttt{-{}-ai} is passed and the analysis detects unsupported or partially supported features, the CLI adds an ``AI Fix Suggestions'' section at the end of the output. Each suggestion includes the feature name, a short explanation of the recommended fix, and a code example showing how it can be implemented. Without \texttt{-{}-ai}, the analysis runs normally and no request is sent to the language model provider, even if a key is available. This keeps the feature optional and predictable for scripts and CI jobs.
```

---

## ✏️ Edit 2 — Expand the `config` command description (line ~347)

### FIND this exact sentence:

```
The CLI also includes commands for managing configuration and updating compatibility data. The \texttt{config} command shows the current configuration settings or creates a configuration file that can store default options for future runs. The \texttt{update-db} command refreshes the local Can I Use database used for compatibility checks, ensuring that the latest browser support information is used during analysis.
```

### REPLACE with:

```
The CLI also includes commands for managing configuration and updating compatibility data. The \texttt{config} command shows the current configuration settings, creates a configuration file that can store default options, and manages the saved AI credentials (via \texttt{-{}-set-api-key}, \texttt{-{}-set-ai-provider}, and \texttt{-{}-clear-api-key}). When displaying configuration, any saved API key is masked so only the first and last four characters appear. The \texttt{update-db} command refreshes the local Can I Use database used for compatibility checks, ensuring that the latest browser support information is used during analysis.
```

---

# PART B — impl.tex changes

**File:** `LaTeX/chapters/impl.tex`

Five small edits: three to Table 2 (test counts), two to the narrative around it.

## ✏️ Edit 3 — Test count in intro paragraph (line ~462)

### FIND:

```
Cross Guard includes a comprehensive automated test suite with 111 tests implemented using pytest
```

### REPLACE with:

```
Cross Guard includes a comprehensive automated test suite with 116 tests implemented using pytest
```

---

## ✏️ Edit 4 — Table 2 Database row (line ~476)

This row in the current file still says `3 & 2 & 2 & 7`. Actual: 5 blackbox + 2 whitebox + 0 integration = 7 total.

### FIND:

```
        Database      & 3 & 2 & 2 & 7  \\ \hline
```

### REPLACE with:

```
        Database      & 5 & 2 & - & 7  \\ \hline
```

---

## ✏️ Edit 5 — Table 2 CLI row (line ~477)

Added 5 new blackbox tests: `4 → 9`. Total: `10 → 15`.

### FIND:

```
        CLI           & 4 & 4 & 2 & 10 \\ \hline
```

### REPLACE with:

```
        CLI           & 9 & 4 & 2 & 15 \\ \hline
```

---

## ✏️ Edit 6 — Table 2 Total row (line ~482)

New totals: BB 65, WB 34, Int 17, Total 116.

### FIND:

```
        \textbf{Total} & \textbf{58} & \textbf{34} & \textbf{19} & \textbf{111} \\ \hline
```

### REPLACE with:

```
        \textbf{Total} & \textbf{65} & \textbf{34} & \textbf{17} & \textbf{116} \\ \hline
```

---

## ✏️ Edit 7 — Closing test execution paragraph (line ~525)

### FIND:

```
The current test suite successfully executes all 111 automated tests in approximately under a second
```

### REPLACE with:

```
The current test suite successfully executes all 116 automated tests in approximately under a second
```

---

# PART C — WHAT NOT TO CHANGE

## 🚫 Do not touch

- All code blocks (`lstlisting`) outside the two subsections edited above — they are unrelated
- Any figure or caption
- The grade scale table in user.tex — already correct
- The scoring section in impl.tex — already correct
- Any earlier chapter (intro, system requirements, installation, GUI workflow)
- Any other CLI subsection (browsers flag, history, stats, export, update-db explanation)
- The Polyfill Recommendations subsection
- The Custom Rules section
- `impl.tex` §3.13 GUI Structure (the change is CLI-only)

---

# Quick checklist

```
[ ] Edit 1 — user.tex  AI Fix Suggestions (CLI) subsection   (big paragraph + lstlisting + paragraph)
[ ] Edit 2 — user.tex  config command description            (one sentence)
[ ] Edit 3 — impl.tex  "111 tests" → "116 tests" intro
[ ] Edit 4 — impl.tex  Table 2 Database row                  (3/2/2/7 → 5/2/-/7)
[ ] Edit 5 — impl.tex  Table 2 CLI row                       (4/4/2/10 → 9/4/2/15)
[ ] Edit 6 — impl.tex  Table 2 Total row                     (58/34/19/111 → 65/34/17/116)
[ ] Edit 7 — impl.tex  "all 111 automated tests" → "all 116 automated tests"
```

7 edits total. 2 in user.tex, 5 in impl.tex.

After applying, tell me and I'll verify.
