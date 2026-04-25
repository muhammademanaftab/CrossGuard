# LaTeX edits — fix the install commands so a fresh user can follow them

While testing the install steps from Chapter 2 on a clean macOS machine, four problems came up that a brand-new user would hit. None of them are bugs in Cross Guard — they are documentation problems where the listings either use commands that don't exist on a fresh macOS install, or assume the user's default Python is already in the supported range.

These edits make the listings work for **macOS, Linux, and Windows users** without any extra steps.

All edits are in **`latex/chapters/user.tex`**.

---

## Why these edits are needed (in plain words)

1. On a fresh macOS install, the command `python` does not exist — only `python3` does. So when a Mac user copies `python --version` from the thesis, they get `command not found`.
2. The same problem hits the venv step: `python -m venv venv` fails on a fresh macOS install for the same reason.
3. The troubleshooting section already tells Linux users how to install Tk if the GUI fails to start, but says nothing for macOS users. Mac users get the exact same error and need a similar one-line fix (`brew install python-tk@3.11`).
4. Table 2.2 says the supported range is Python 3.9 to 3.12, but on a fresh Mac in 2026 the default `python3` is 3.14 (this is what Homebrew installs by default). The listing tells users to run `python3 --version` but doesn't tell them what to do if the version they see is outside the supported range. The result is the user runs `pip install -r requirements.txt` and gets a wall of red errors with no clear next step.

The fix in cases 1–3 is to follow the same pattern that the listing already uses for the activate step on line 60–61: show the macOS/Linux command and the Windows command on two lines, with a short `# macOS / Linux` and `# Windows` comment on each. The fix for case 4 is a short paragraph after Listing 2.1 explaining how to install Python 3.11 if the user's default Python is outside the supported range.

---

## Edit 1 — Listing 2.1, the Python version check (line 49)

### Find this line:

```latex
python --version
```

### Replace with:

```latex
python3 --version    # macOS / Linux
python --version     # Windows
```

### Why
On macOS, the shell only knows `python3`, not `python`. The Windows Python installer registers both names, but most macOS users only have `python3`. Splitting the command into two lines (the same way the activate step is already split) makes the listing work for all three operating systems.

---

## Edit 2 — Listing 2.1, creating the virtual environment (line 57)

### Find this line:

```latex
python -m venv venv
```

### Replace with:

```latex
python3 -m venv venv    # macOS / Linux
python -m venv venv     # Windows
```

### Why
Same reason as Edit 1. On a fresh macOS install, `python` does not exist. Inside the venv (after activation) both `python` and `python3` work, so the rest of the listing is fine — only this one creation step needs the platform split.

---

## Edit 3 — Troubleshooting listing, add the macOS Tk fix (around line 105–106)

### Find these two lines:

```latex
# Install tkinter on Linux if the GUI fails to start
sudo apt-get install python3-tk
```

### Replace with:

```latex
# Install tkinter on Linux if the GUI fails to start
sudo apt-get install python3-tk

# Install tkinter on macOS if the GUI fails to start
brew install python-tk@3.11
```

### Why
On macOS, Homebrew's Python does not include Tk by default. If a Mac user tries to launch the GUI without it, they get `ModuleNotFoundError: No module named '_tkinter'`. This is the same kind of issue Linux users hit (which is already covered in the listing), and the fix is just as short — one Homebrew command. Adding it makes the troubleshooting section symmetric across operating systems.

---

## Edit 4 — Add a paragraph after Listing 2.1 explaining what to do if Python is outside the 3.9–3.12 range

### Find the empty line right after Listing 2.1 ends (the line right after `\end{lstlisting}` on line 65 and before `\newpage` on line 66)

In the current source, line 65 is `\end{lstlisting}` and line 66 is `\newpage`. The new paragraph goes between them.

### Insert this new paragraph between line 65 and line 66:

```latex

Step 1 of the listing prints the installed Python version. The required range is 3.9 to 3.12 (see Table~\ref{tab:software-req}). If the version reported is outside this range -- for example, on a fresh macOS where Homebrew now installs Python 3.14 by default -- users should install Python 3.11 explicitly before continuing. The commands below install a supported version on each operating system:

\begin{lstlisting}[caption={Installing Python 3.11 if the default Python is outside the supported range}, basicstyle=\ttfamily\small]
brew install python@3.11           # macOS
sudo apt install python3.11        # Linux (Ubuntu / Debian)
# Windows: download Python 3.11 from python.org
\end{lstlisting}

After installing, users should create the virtual environment with the explicit version, for example \texttt{python3.11 -m venv venv} on macOS and Linux, and re-run step 5 of Listing~\ref{src:setup-all} to install the dependencies.

```

### Why
On a fresh macOS in 2026, `python3` points to Python 3.14 because that is the version Homebrew installs by default. A user who follows the listing exactly creates a Python 3.14 virtual environment, then `pip install -r requirements.txt` fails because some pinned dependencies (specifically \texttt{tree-sitter-languages==1.10.2}) only have wheels for Python 3.9 to 3.12. The error message points to the package, not to the Python version, so a user has no clear way to recover.

This paragraph closes the gap between the supported range (already documented in Table 2.2) and the actual install steps. It tells the user how to verify, and what to do if their default Python is too new.

---

## Summary table

| # | File | Line(s) | Plain-English change |
|---|------|---------|----------------------|
| 1 | `chapters/user.tex` | 49 | Split `python --version` into two lines: `python3` for macOS/Linux, `python` for Windows |
| 2 | `chapters/user.tex` | 57 | Split `python -m venv venv` into two lines the same way |
| 3 | `chapters/user.tex` | 105–106 | Add a macOS line under the existing Linux Tk fix |
| 4 | `chapters/user.tex` | between 65 and 66 | Add a short paragraph + small listing for installing Python 3.11 if the default is outside the 3.9–3.12 range |

**Total: 4 small edits, all in one file.**

---

## How to verify after editing

1. Recompile the thesis (`pdflatex` / `latexmk`).
2. Open the rendered PDF and check Listing 2.1: lines 1 and 9 should now show two commands each (macOS/Linux and Windows), matching the style of line 13 (the activate line).
3. Check the troubleshooting listing: it should now have a macOS Tk entry next to the Linux one.
4. Optional sanity grep — confirm no bare `python --version` or `python -m venv` remains in the listings:

```bash
grep -n "python --version\|python -m venv" latex/chapters/user.tex
```

It should only show lines that have a Windows comment after them.

---

## What is not changing

- **Table 2.2 (Software requirements)** already says `Python 3.9 to 3.12` — this is correct and matches what was tested. No change needed.
- **Listing 2.2 (Optional installation modes)** — the `pip install -e ".[gui]"` style commands work on every platform once the venv is active. No change needed.
- **All `python -m src.cli.main ...` lines later in the chapter** — these run from inside an activated venv, where both `python` and `python3` work. No change needed.

These three small edits are the only ones required to make Chapter 2 work end-to-end for a brand-new user on macOS, Linux, or Windows.
