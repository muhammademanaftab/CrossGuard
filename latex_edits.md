# LaTeX edits — fix the install commands so a fresh user can follow them

While testing the install steps from Chapter 2 on a clean macOS machine, three problems came up that a brand-new user would hit. None of them are bugs in Cross Guard — they are documentation problems where the listings use commands that don't exist on a fresh macOS install.

These edits make the listings work for **macOS, Linux, and Windows users** without any extra steps.

All edits are in **`latex/chapters/user.tex`**.

---

## Why these edits are needed (in plain words)

1. On a fresh macOS install, the command `python` does not exist — only `python3` does. So when a Mac user copies `python --version` from the thesis, they get `command not found`.
2. The same problem hits the venv step: `python -m venv venv` fails on a fresh macOS install for the same reason.
3. The troubleshooting section already tells Linux users how to install Tk if the GUI fails to start, but says nothing for macOS users. Mac users get the exact same error and need a similar one-line fix (`brew install python-tk@3.11`).

The fix in each case is to follow the same pattern that the listing already uses for the activate step on line 60–61: show the macOS/Linux command and the Windows command on two lines, with a short `# macOS / Linux` and `# Windows` comment on each.

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

## Summary table

| # | File | Line(s) | Plain-English change |
|---|------|---------|----------------------|
| 1 | `chapters/user.tex` | 49 | Split `python --version` into two lines: `python3` for macOS/Linux, `python` for Windows |
| 2 | `chapters/user.tex` | 57 | Split `python -m venv venv` into two lines the same way |
| 3 | `chapters/user.tex` | 105–106 | Add a macOS line under the existing Linux Tk fix |

**Total: 3 small edits, all in one file.**

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
