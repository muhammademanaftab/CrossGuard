# LaTeX edits — pending changes for the thesis

This document lists every edit that needs to land in the LaTeX source. There are two groups:

- **Group A** — install commands (existing, 4 edits)
- **Group B** — remove the Tag feature from the docs (new, 6 edits + 2 diagrams)

All edits are in `/Users/home/Documents/Educational/Thesis/latex/`.

---

# Group A — Install commands so a fresh user can follow Chapter 2

While testing the install steps from Chapter 2 on a clean macOS machine, four problems came up that a brand-new user would hit. None of them are bugs in Cross Guard — they are documentation problems where the listings either use commands that don't exist on a fresh macOS install, or assume the user's default Python is already in the supported range.

These edits make the listings work for **macOS, Linux, and Windows users** without any extra steps.

All Group A edits are in **`latex/chapters/user.tex`**.

## Why these edits are needed (in plain words)

1. On a fresh macOS install, the command `python` does not exist — only `python3` does. So when a Mac user copies `python --version` from the thesis, they get `command not found`.
2. The same problem hits the venv step: `python -m venv venv` fails on a fresh macOS install for the same reason.
3. The troubleshooting section already tells Linux users how to install Tk if the GUI fails to start, but says nothing for macOS users. Mac users get the exact same error and need a similar one-line fix (`brew install python-tk@3.11`).
4. Table 2.2 says the supported range is Python 3.9 to 3.12, but on a fresh Mac in 2026 the default `python3` is 3.14 (this is what Homebrew installs by default). The listing tells users to run `python3 --version` but doesn't tell them what to do if the version they see is outside the supported range.

The fix in cases 1–3 is to follow the same pattern that the listing already uses for the activate step on line 60–61: show the macOS/Linux command and the Windows command on two lines, with a short `# macOS / Linux` and `# Windows` comment on each. The fix for case 4 is a short paragraph after Listing 2.1 explaining how to install Python 3.11 if the user's default Python is outside the supported range.

---

## Edit A1 — Listing 2.1, the Python version check (line 49)

**Find this line:**

```latex
python --version
```

**Replace with:**

```latex
python3 --version    # macOS / Linux
python --version     # Windows
```

**Why:** On macOS, the shell only knows `python3`, not `python`. The Windows Python installer registers both names, but most macOS users only have `python3`. Splitting the command into two lines (the same way the activate step is already split) makes the listing work for all three operating systems.

---

## Edit A2 — Listing 2.1, creating the virtual environment (line 57)

**Find this line:**

```latex
python -m venv venv
```

**Replace with:**

```latex
python3 -m venv venv    # macOS / Linux
python -m venv venv     # Windows
```

**Why:** Same reason as Edit A1. On a fresh macOS install, `python` does not exist. Inside the venv (after activation) both `python` and `python3` work, so the rest of the listing is fine — only this one creation step needs the platform split.

---

## Edit A3 — Troubleshooting listing, add the macOS Tk fix (around line 105–106)

**Find these two lines:**

```latex
# Install tkinter on Linux if the GUI fails to start
sudo apt-get install python3-tk
```

**Replace with:**

```latex
# Install tkinter on Linux if the GUI fails to start
sudo apt-get install python3-tk

# Install tkinter on macOS if the GUI fails to start
brew install python-tk@3.11
```

**Why:** On macOS, Homebrew's Python does not include Tk by default. If a Mac user tries to launch the GUI without it, they get `ModuleNotFoundError: No module named '_tkinter'`. This is the same kind of issue Linux users hit (which is already covered in the listing), and the fix is just as short — one Homebrew command. Adding it makes the troubleshooting section symmetric across operating systems.

---

## Edit A4 — Add a paragraph after Listing 2.1 explaining what to do if Python is outside the 3.9–3.12 range

**Find the empty line right after Listing 2.1 ends** (right after `\end{lstlisting}` on line 65 and before `\newpage` on line 66).

**Insert this new paragraph between line 65 and line 66:**

```latex

Step 1 of the listing prints the installed Python version. The required range is 3.9 to 3.12 (see Table~\ref{tab:software-req}). If the version reported is outside this range -- for example, on a fresh macOS where Homebrew now installs Python 3.14 by default -- users should install Python 3.11 explicitly before continuing. The commands below install a supported version on each operating system:

\begin{lstlisting}[caption={Installing Python 3.11 if the default Python is outside the supported range}, basicstyle=\ttfamily\small]
brew install python@3.11           # macOS
sudo apt install python3.11        # Linux (Ubuntu / Debian)
# Windows: download Python 3.11 from python.org
\end{lstlisting}

After installing, users should create the virtual environment with the explicit version, for example \texttt{python3.11 -m venv venv} on macOS and Linux, and re-run step 5 of Listing~\ref{src:setup-all} to install the dependencies.

```

**Why:** On a fresh macOS in 2026, `python3` points to Python 3.14 because that is the version Homebrew installs by default. A user who follows the listing exactly creates a Python 3.14 virtual environment, then `pip install -r requirements.txt` fails because some pinned dependencies (specifically `tree-sitter-languages==1.10.2`) only have wheels for Python 3.9 to 3.12. The error message points to the package, not to the Python version, so a user has no clear way to recover.

---

## Group A summary

| # | File | Line(s) | Plain-English change |
|---|------|---------|----------------------|
| A1 | `chapters/user.tex` | 49 | Split `python --version` into two lines (macOS/Linux + Windows) |
| A2 | `chapters/user.tex` | 57 | Split `python -m venv venv` the same way |
| A3 | `chapters/user.tex` | 105–106 | Add a macOS line under the Linux Tk fix |
| A4 | `chapters/user.tex` | between 65 and 66 | Add a short paragraph + small listing for installing Python 3.11 if default Python is outside range |

---

# Group B — Remove the Tag feature from the docs

## Why these edits are needed (in plain words)

The Tag feature has been removed from Cross Guard's code. Tags were a half-feature: users could create labels and attach them to past analyses, but there was no way to filter, search, or group analyses by tag, so tags were purely decorative and added implementation surface that did not justify itself in a thesis-defense context. Rather than build full filter/search behind it, the cleaner choice is to drop the feature entirely.

The codebase no longer contains any of the following: the `Tag` data model, the `TagsRepository`, the `tags` and `analysis_tags` SQL tables, the `tag_widget.py` GUI module (with `TagChip`, `TagList`, `TagSelector`, `TagManagerDialog` classes), the **Tags** button on the History page, or any service-layer methods like `create_tag`, `add_tag_to_analysis`, etc. The schema now has 6 tables instead of 8.

The thesis text needs to be aligned with the new code. Below are the 6 LaTeX edits + 2 diagram updates required.

All Group B text edits are in **`latex/chapters/impl.tex`**. The diagram source files are in **`code/docs/diagrams/scripts/`**.

---

## Edit B1 — Section 3.1 overview, drop "tags" from the storage list (line 37)

**Find this sentence inside the paragraph at line 37:**

```latex
Analysis results, bookmarks, tags, and settings are stored in an SQLite database using repository classes, as explained in Section~\ref{sec:database}.
```

**Replace with:**

```latex
Analysis results, bookmarks, and settings are stored in an SQLite database using repository classes, as explained in Section~\ref{sec:database}.
```

**Why:** Tags are no longer stored in the database. Only analyses, bookmarks, and settings remain.

---

## Edit B2 — Database section, drop `TagsRepository` from the repository list (line 204)

**Find this sentence:**

```latex
The database connection is managed by a singleton in \texttt{src/database/connection.py}, meaning only one connection exists throughout the entire runtime. All database operations pass through repository classes defined in \texttt{src/database/repositories.py}: \texttt{AnalysisRepository} for analysis records, \texttt{SettingsRepository} for key-value settings, \texttt{BookmarksRepository} for bookmarked analyses, and \texttt{TagsRepository} for colored labels. The following diagram shows the database layer and how the data is structured:
```

**Replace with:**

```latex
The database connection is managed by a singleton in \texttt{src/database/connection.py}, meaning only one connection exists throughout the entire runtime. All database operations pass through repository classes defined in \texttt{src/database/repositories.py}: \texttt{AnalysisRepository} for analysis records, \texttt{SettingsRepository} for key-value settings, and \texttt{BookmarksRepository} for bookmarked analyses. The following diagram shows the database layer and how the data is structured:
```

**Why:** `TagsRepository` no longer exists. Only three repositories remain.

---

## Edit B3 — Database diagram explanation, drop the Tag relationship sentence (line 219)

**Find this sentence (line 219):**

```latex
On the left, \texttt{Bookmark} references an \texttt{Analysis} through a solid line. Users can bookmark any analysis. On the right, \texttt{Tag} has a $0..*$ relationship with \texttt{Analysis}, meaning one analysis can have multiple labels and one label can apply to multiple analyses.
```

**Replace with:**

```latex
On the left, \texttt{Bookmark} references an \texttt{Analysis} through a solid line. Users can bookmark any analysis.
```

**Why:** The `Tag` class has been removed from the data model.

---

## Edit B4 — "All five data model classes" → "All four" (line 221)

**Find this sentence (line 221):**

```latex
All five data model classes share the same methods: \texttt{to\_dict()} for JSON export and \texttt{from\_row()} for creating objects from database rows.
```

**Replace with:**

```latex
All four data model classes share the same methods: \texttt{to\_dict()} for JSON export and \texttt{from\_row()} for creating objects from database rows.
```

**Why:** The five classes were Analysis, AnalysisFeature, BrowserResult, Bookmark, Tag. Now there are only four (Tag removed).

---

## Edit B5 — V2 tables list, drop `tags` and `analysis_tags` (line 223)

**Find this sentence (line 223):**

```latex
The database schema is organized into two versions. V1 tables (\texttt{analyses}, \texttt{analysis\_features}, \texttt{browser\_results}) handle core analysis storage. V2 tables (\texttt{settings}, \texttt{bookmarks}, \texttt{tags}, \texttt{analysis\_tags}, \texttt{schema\_version}) add user features. All foreign keys use \texttt{ON DELETE CASCADE}, so deleting an analysis removes all its related data automatically.
```

**Replace with:**

```latex
The database schema is organized into two versions. V1 tables (\texttt{analyses}, \texttt{analysis\_features}, \texttt{browser\_results}) handle core analysis storage. V2 tables (\texttt{settings}, \texttt{bookmarks}, \texttt{schema\_version}) add user features. All foreign keys use \texttt{ON DELETE CASCADE}, so deleting an analysis removes all its related data automatically.
```

**Why:** The schema has been simplified — `tags` and `analysis_tags` no longer exist. V2 now has 3 tables (settings, bookmarks, schema_version).

---

## Edit B6 — GUI widgets list, drop "tag chips" (line 343)

**Find this sentence (line 343):**

```latex
Each page is composed of smaller widgets from \texttt{src/gui/widgets/}. Components like the score card, browser cards, issue cards, polyfill cards, and tag chips are all separate classes.
```

**Replace with:**

```latex
Each page is composed of smaller widgets from \texttt{src/gui/widgets/}. Components like the score card, browser cards, issue cards, and polyfill cards are all separate classes.
```

**Why:** The `TagChip` widget no longer exists.

---

## Edit B7 — Repository pattern explanation, "Four" → "Three" (line 421)

**Find this sentence (line 421):**

```latex
The \textbf{Repository pattern}~\cite{fowler2002peaa} separates database logic from the rest of the application. Four repository classes manage all SQL operations for analyses, settings, bookmarks, and tags. This ensures that no other part of the codebase interacts with SQL directly, improving maintainability and testability.
```

**Replace with:**

```latex
The \textbf{Repository pattern}~\cite{fowler2002peaa} separates database logic from the rest of the application. Three repository classes manage all SQL operations for analyses, settings, and bookmarks. This ensures that no other part of the codebase interacts with SQL directly, improving maintainability and testability.
```

**Why:** Only three repositories remain.

---

## Diagram update D1 — `cg_database.png` (database class diagram)

**Source file:** `code/docs/diagrams/scripts/3.9_database.py`

The current diagram shows a `Tag` class on the right side, connected to `Analysis` with a `0..*` line. After the code change, the diagram needs to drop the `Tag` node entirely.

### Lines to change in `3.9_database.py`:

1. **Line 82** — remove the `g.node('Tag', ...)` block that creates the Tag node.
2. **Line 113** — remove the comment `# Bookmark and Tag` and adjust to just `# Bookmark`.
3. **Line 115** — remove the line `g.edge('Analysis', 'Tag', arrowhead='none', label=' 0..* ')`.
4. **Line 129** — remove the line `s.node('Tag')` from the cluster grouping.

### Then re-render:

```bash
cd code/docs/diagrams
python scripts/3.9_database.py        # regenerates images/3.9_database.png
cp images/3.9_database.png ../../latex/images/cg_database.png
```

The thesis figure (`\includegraphics{cg_database}` on line 208) will then point to the new image.

---

## Diagram update D2 — GUI/service class diagram

**Source file:** `code/docs/diagrams/scripts/3.13_gui.py`

The current diagram includes `get_all_tags() : List` as a method on the `AnalyzerService` class. That method has been removed.

### Line to change in `3.13_gui.py`:

- **Line 77** — delete the line `'+ get_all_tags() : List',`

### Then re-render:

```bash
cd code/docs/diagrams
python scripts/3.13_gui.py            # regenerates the GUI diagram PNG
```

(The output PNG name and the corresponding `latex/images/` filename should match — copy whichever file `3.13_gui.py` produces over the matching one in `latex/images/`.)

---

## Group B summary

| # | File | Line(s) | Plain-English change |
|---|------|---------|----------------------|
| B1 | `chapters/impl.tex` | 37 | Drop "tags" from the storage list |
| B2 | `chapters/impl.tex` | 204 | Drop `TagsRepository` from the repository list (4 → 3 repos) |
| B3 | `chapters/impl.tex` | 219 | Delete the `Tag` 0..* relationship sentence |
| B4 | `chapters/impl.tex` | 221 | Change "All five data model classes" → "All four" |
| B5 | `chapters/impl.tex` | 223 | Drop `tags` and `analysis_tags` from V2 tables list |
| B6 | `chapters/impl.tex` | 343 | Drop "tag chips" from the GUI widget examples |
| B7 | `chapters/impl.tex` | 421 | Change "Four repository classes" → "Three" and drop "and tags" |
| D1 | `docs/diagrams/scripts/3.9_database.py` + render | 82, 113, 115, 129 | Remove `Tag` node, edge, cluster entry; re-render to `cg_database.png` |
| D2 | `docs/diagrams/scripts/3.13_gui.py` + render | 77 | Remove `get_all_tags()` from method list; re-render |

---

## How to verify after editing

1. Recompile the thesis (`pdflatex` / `latexmk`).
2. Search for any remaining "Tag" references that should not be there:

```bash
grep -ni "tag" latex/chapters/*.tex | grep -v "html tag\|HTML tag\|caniuse\|tag name\|tagged with a risk"
```

The only legitimate hits should be:
- HTML tag references in the parser section (e.g. `soup.find_all("dialog")`)
- The phrase "tagged with a risk level" on line 197 of `impl.tex` — this is metaphorical (assigning a risk-level label to an analysis based on its score) and has nothing to do with the removed Tag feature. Leave it.

3. Open the new `cg_database.png` and verify:
   - No `Tag` class on the right side
   - Only `Analysis`, `AnalysisFeature`, `BrowserResult`, and `Bookmark` remain

4. Open the GUI/service diagram and verify `get_all_tags()` is no longer listed under `AnalyzerService`.

---

# Group C — Readability rewrites in `impl.tex`

These edits don't change any factual claim. They just rewrite paragraphs that are dense or hard to grasp on first read into shorter, plain-English versions.

All Group C edits are in **`latex/chapters/impl.tex`**.

---

## Edit C1 — HTML parser, simplify the "special patterns" paragraph (line 137)

### The problem

The current paragraph packs four different special-case checks into one long sentence with nested code examples in parentheses. A reader has to re-read it to follow what each check is for.

### Find the entire paragraph at line 137:

```latex
Some features require additional logic beyond dictionary lookups. These are handled by \texttt{\_detect\_special\_patterns()}, which includes custom checks for cases such as custom elements with hyphenated names (\texttt{<my-widget></my-widget>}), SVG fragment identifiers where \texttt{href} contains \texttt{.svg\#} (\texttt{<use href="icons.svg\#star">}), data URIs, and different values of the \texttt{link rel} attribute such as \texttt{preload}, \texttt{prefetch}, and \texttt{dns-prefetch} (\texttt{<link rel="preload" href="style.css">}). Each detection method adds the matched feature ID to \texttt{self.features\_found} and records the match in \texttt{self.\_feature\_matches} for reporting.
```

### Replace with:

```latex
Some features cannot be detected by a simple dictionary lookup, because they depend on the shape of the value rather than the element or attribute name on its own. These are handled by \texttt{\_detect\_special\_patterns()}, which runs four extra checks. The first looks for custom elements, which always have a hyphen in the tag name (e.g.\ \texttt{<my-widget>}). The second looks for SVG fragment identifiers, where an \texttt{href} value contains \texttt{.svg\#} (e.g.\ \texttt{<use href="icons.svg\#star">}). The third looks for data URIs. The fourth looks at the \texttt{rel} attribute on a \texttt{<link>} element and matches values such as \texttt{preload}, \texttt{prefetch}, and \texttt{dns-prefetch}. Whenever any of these checks finds a match, the feature ID is added to \texttt{self.features\_found}, and the match itself is recorded in \texttt{self.\_feature\_matches} so it can appear in the report.
```

### What changed and why

| Change | Why |
|--------|-----|
| Opening sentence rewritten with **why** these need special handling ("depend on the shape of the value, not just the name") | The original just said "additional logic" without explaining what makes these cases different. The new wording tells the reader the *reason*. |
| The four cases became four short sentences ("The first…", "The second…", "The third…", "The fourth…") | The original packed all four cases into one long sentence with parenthetical examples. Splitting them gives the reader breathing room. |
| Removed the `<my-widget></my-widget>` and `<link rel="preload" href="style.css">` redundant examples | Single-tag forms (e.g.\ `<my-widget>`) make the same point with less visual noise. |
| Closing sentence rewritten with "**so it can appear in the report**" | The original said "for reporting" which was vague. The new wording tells the reader what `self._feature_matches` is *used for*. |

### What stays identical (correctness preserved)

- All four detection cases are kept (custom elements, SVG `#fragments`, data URIs, link `rel` values).
- All variable/method names unchanged: `_detect_special_patterns`, `self.features_found`, `self._feature_matches`.
- The example values for `rel` (`preload`, `prefetch`, `dns-prefetch`) are kept verbatim.

---

## Group C summary

| # | File | Line | Plain-English change |
|---|------|------|----------------------|
| C1 | `chapters/impl.tex` | 137 | Rewrite the dense "special patterns" paragraph as one short opener + four short "The first/second/third/fourth…" sentences |

---

## Total

**Group A:** 4 LaTeX edits, all in `user.tex`
**Group B:** 7 LaTeX edits in `impl.tex` + 2 diagrams to re-render
**Group C:** 1 LaTeX edit in `impl.tex` (readability rewrite)

**Grand total: 12 LaTeX edits + 2 regenerated diagrams.**
