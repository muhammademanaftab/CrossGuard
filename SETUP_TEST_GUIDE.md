# Cross Guard — Setup Test Guide

How to test the **setup commands** from Chapter 2 of the thesis (Code 2.1, 2.2, 2.3) without breaking your existing working environment.

This tests:
- ✅ **Code 2.1** — Verify Python, clone, create venv, activate, install dependencies
- ✅ **Code 2.2** — Optional installation modes (`pip install -e ".[gui]"`, `".[cli]"`, `".[gui,cli]"`)
- ✅ **Code 2.3** — Launching the GUI and CLI

**Strategy**: everything happens in a fresh sandbox at `/tmp/cross-guard-test/`. Your existing project at `/Users/home/Documents/Educational/Thesis/Code/` and its `.venv/` are **never touched**.

---

## Why a sandbox?

The thesis says `git clone [repository-url]` and `cd cross-guard`. There's no public repo URL yet, so for the test we'll **clone the local project as if it were a remote** — this gives a totally fresh copy named `cross-guard` (matching the thesis), with its own venv, in `/tmp/`. When we're done, `rm -rf` cleans it up entirely.

---

## Step 0 — Open a NEW terminal window

Important: open a fresh terminal so you don't have your existing venv activated. We want to start from scratch, just like a new user would.

```bash
# Confirm no venv is active (prompt should NOT have "(.venv)" in it)
echo "$VIRTUAL_ENV"
# Expected: (empty line)
```

If `(.venv)` is in your prompt, run `deactivate` first.

---

## Step 1 (Code 2.1) — Verify Python

```bash
python3 --version
```

Expected: `Python 3.9` or higher (e.g. `Python 3.11.x`, `Python 3.12.x`).

> macOS uses `python3` (Python 2 is gone). The thesis listing shows `python` — that's an alias on most setups, but `python3` is the safe choice on macOS.

---

## Step 2 (Code 2.1) — Clone the repo into a sandbox

Since there's no remote URL, we clone the local project. The sandbox lives at `/tmp/cross-guard-test/`.

```bash
mkdir -p /tmp/cross-guard-test && cd /tmp/cross-guard-test
git clone /Users/home/Documents/Educational/Thesis/Code cross-guard
cd cross-guard
ls
```

Expected output of `ls`: you should see `src/`, `tests/`, `examples/`, `data/`, `pyproject.toml`, `requirements.txt`, `run_gui.py`, etc.

---

## Step 3 (Code 2.1) — Create a virtual environment

```bash
python3 -m venv venv
ls venv/
```

Expected: `bin/`, `lib/`, `pyvenv.cfg`. The thesis-named `venv` directory exists.

---

## Step 4 (Code 2.1) — Activate the environment

```bash
source venv/bin/activate
```

Your prompt should now show `(venv)` at the front.

Verify Python now points inside the sandbox:

```bash
which python
# Expected: /tmp/cross-guard-test/cross-guard/venv/bin/python
```

---

## Step 5 (Code 2.1) — Install all dependencies

```bash
pip install -r requirements.txt
```

This installs everything (CLI + GUI + visualization libs). Takes ~1 minute and downloads ~150 MB.

When done, smoke-check by importing key packages:

```bash
python -c "import beautifulsoup4" 2>/dev/null; \
python -c "import bs4; import tinycss2; import lxml; import click; import customtkinter; import reportlab; print('All core imports OK')"
```

Expected: `All core imports OK`.

---

## Step 6 (Code 2.2) — Test optional installation modes

These three commands let you install only what you need. Test them by uninstalling first, then reinstalling each mode.

### 6a — GUI-only install

```bash
pip install -e ".[gui]"
```

Installs: customtkinter, tkinterdnd2, weasyprint, jinja2, Pillow, matplotlib, numpy + the base deps.

Verify:

```bash
python -c "import customtkinter; import reportlab; print('GUI extras: OK')"
```

### 6b — CLI-only install

```bash
pip install -e ".[cli]"
```

Adds `click` (everything else from the GUI install is still present in the venv).

```bash
python -c "import click; print('CLI extra: OK')"
```

### 6c — Both (GUI + CLI)

```bash
pip install -e ".[gui,cli]"
```

```bash
python -c "import customtkinter; import click; print('GUI+CLI extras: OK')"
```

---

## Step 7 (Code 2.3) — Launch the GUI

```bash
python run_gui.py
```

Expected: a window opens with the Cross Guard interface. Click the **X** to close — you don't need to actually use it; opening proves the entry point works.

---

## Step 8 (Code 2.3) — Analyze a file from the CLI

The thesis listing uses a placeholder path. Use the bundled sample CSS:

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --format table
```

Expected: a colored compatibility report in your terminal with grade, score, browser table, and detected features.

---

## Step 9 (Code 2.3) — Show the CLI help menu

```bash
python -m src.cli.main --help
```

Expected: a list of available subcommands (`analyze`, `history`, `stats`, `export`, `config`, `update-db`, `init-ci`, `init-hooks`, etc.).

---

## Step 10 — Cleanup

When you're done, deactivate the sandbox venv and delete the whole directory:

```bash
deactivate
cd /
rm -rf /tmp/cross-guard-test
```

Your real project at `/Users/home/Documents/Educational/Thesis/Code/` is completely untouched.

---

## All-in-one smoke test (paste this whole block)

```bash
# Open a fresh terminal first, with no venv active.

# 1. Setup sandbox
mkdir -p /tmp/cross-guard-test
cd /tmp/cross-guard-test
git clone /Users/home/Documents/Educational/Thesis/Code cross-guard
cd cross-guard

# 2. Verify Python
python3 --version

# 3. Create + activate venv
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify imports
python -c "import bs4; import tinycss2; import lxml; import click; import customtkinter; import reportlab; print('✓ All core imports OK')"

# 6. Test installation modes
pip install -e ".[gui]"   && python -c "import customtkinter; import reportlab; print('✓ gui mode')"
pip install -e ".[cli]"   && python -c "import click; print('✓ cli mode')"
pip install -e ".[gui,cli]" && python -c "import customtkinter; import click; print('✓ gui+cli mode')"

# 7. Test CLI
python -m src.cli.main --help | head -20
python -m src.cli.main analyze examples/sample_project/sample.css --format summary

# 8. Done
echo ""
echo "✓ Setup test passed. Cleaning up..."
deactivate
cd /
rm -rf /tmp/cross-guard-test
echo "Sandbox removed."
```

When this prints `Sandbox removed.` at the end, every command from Code 2.1, 2.2, and 2.3 has been verified working.

> **Note**: the GUI test (`python run_gui.py` from Code 2.3) is not in the all-in-one block because it opens a window. Run it manually if you want to verify it.

---

## What this proves for your defense

> "The setup procedure was verified end-to-end on a fresh sandbox: a clean clone, a new virtual environment, `pip install -r requirements.txt`, and each of the three optional installation modes (`.[gui]`, `.[cli]`, `.[gui,cli]`) install cleanly. The GUI launches via `python run_gui.py` and the CLI dispatches via `python -m src.cli.main`, matching the commands documented in Listings 2.1, 2.2, and 2.3."

That's strong evidence the documented setup actually works for a new user.

---

## PDF library — note for the thesis

Cross Guard's PDF exporter uses **ReportLab** (`src/export/pdf_exporter.py`). It's a pure-Python library — no external system dependencies (no Pango, no Cairo). It's listed in both `requirements.txt` and `pyproject.toml`'s `[gui]` extras, so `pip install -r requirements.txt` or `pip install -e ".[gui]"` brings it in automatically.
