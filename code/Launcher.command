#!/bin/bash
# Cross Guard launcher for Mac.
# Just double-click this file. The first time, it sets everything up for you
# (Python, all the libraries, etc.). After that, it just opens the app right away.

set -uo pipefail

# Always work from the folder this script lives in (the project folder),
# even if someone double-clicks it from somewhere else.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

echo "==========================================================="
echo " Cross Guard Launcher  —  $(date '+%Y-%m-%d %H:%M:%S')"
echo "==========================================================="
echo "Project folder: $SCRIPT_DIR"
echo

# Tiny helper. Anytime something goes wrong, we call this so the user sees
# a clear message and the Terminal window stays open instead of vanishing.
fail() {
    echo
    echo "  Cross Guard could not start: $1"
    echo
    echo "Press Return to close this window..."
    read -r _ || true
    exit 1
}

# Quick internet check. We only really need internet on the very first run
# (to download Python and the libraries), so we only call this when needed.
require_internet() {
    if ! curl -s --head --max-time 5 https://www.python.org/ >/dev/null 2>&1; then
        fail "No internet connection. The first-time setup needs to download some things. Please connect to the internet and double-click this file again."
    fi
}

# -------------------------------------------------------------
# Step 1: Find a Python that will work for Cross Guard
# -------------------------------------------------------------
# Cross Guard works with Python 3.9 through 3.12. We try 3.11 FIRST because
# it ships with Tcl/Tk 8.6, which is what CustomTkinter and tkinterdnd2 are
# built for. Python 3.12 from Homebrew uses Tcl/Tk 9, which makes the GUI
# noticeably laggy and breaks drag-and-drop on this Mac. Newer isn't always
# better — for this app's GUI stack, 3.11 is the sweet spot.
echo "Step 1 of 4: Looking for Python on your Mac..."
PYTHON_BIN=""
for cmd in python3.11 python3.10 python3.9 python3.12; do
    if command -v "$cmd" >/dev/null 2>&1; then
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        if [ -n "$ver" ]; then
            # Make sure tkinter is included (needed for the GUI).
            if ! "$cmd" -c "import tkinter" >/dev/null 2>&1; then
                echo "    Skipping $cmd (Python $ver) — it's missing tkinter, can't use it."
                continue
            fi
            # Also make sure it's using Tcl/Tk 8.x. Tk 9 (which Homebrew's
            # Python 3.12 uses) makes the GUI laggy and breaks drag-and-drop.
            tkver=$("$cmd" -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null || true)
            tkmajor=$(echo "$tkver" | cut -d. -f1)
            if [ "$tkmajor" != "8" ]; then
                echo "    Skipping $cmd (Python $ver) — its Tk is $tkver, we need 8.x for fast UI and drag-and-drop."
                continue
            fi
            PYTHON_BIN=$(command -v "$cmd")
            echo "    Found Python $ver with Tk $tkver at $PYTHON_BIN"
            break
        fi
    fi
done

# If no usable Python was found above, install one for the user.
# We try Homebrew first (because it doesn't need a password). If brew
# isn't available, we fall back to the official installer from python.org.
if [ -z "$PYTHON_BIN" ]; then
    echo "    No Python found. Going to install Python 3.11 for you."
    require_internet

    if command -v brew >/dev/null 2>&1; then
        echo "    Homebrew is here, using it (no password needed)..."
        brew install python@3.11 || fail "Homebrew couldn't install python@3.11."
        if [ -x "$(brew --prefix python@3.11)/bin/python3.11" ]; then
            PYTHON_BIN="$(brew --prefix python@3.11)/bin/python3.11"
        elif command -v python3.11 >/dev/null 2>&1; then
            PYTHON_BIN="$(command -v python3.11)"
        else
            fail "Homebrew said it installed Python, but I can't find the python3.11 command. Try opening a new Terminal window and running this again."
        fi
    else
        # No Homebrew → grab the official .pkg installer from python.org.
        # The "macos11" file is the universal2 build, so it works on both
        # Apple Silicon Macs and older Intel ones.
        echo "    Homebrew isn't installed. Downloading the official Python installer..."
        PYTHON_VERSION="3.11.10"
        PKG_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-macos11.pkg"
        PKG_FILE="${TMPDIR:-/tmp}/python_${PYTHON_VERSION}_installer.pkg"
        echo "    From: $PKG_URL"
        curl -L --fail --progress-bar -o "$PKG_FILE" "$PKG_URL" || fail "Couldn't download the Python installer. Check your internet."
        echo
        echo "    Now running the installer. Mac will ask for your password —"
        echo "    that's normal, this is the official Python installer from python.org."
        sudo installer -pkg "$PKG_FILE" -target / || fail "The Python installer didn't finish (you may have cancelled the password prompt)."
        rm -f "$PKG_FILE"
        # Make sure the new Python is on PATH for the rest of this run.
        export PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:$PATH"
        if command -v python3.11 >/dev/null 2>&1; then
            PYTHON_BIN="$(command -v python3.11)"
        else
            fail "Python installed, but I can't see python3.11 in this Terminal. Open a new Terminal and double-click this file again."
        fi
    fi

    # Sanity check the new Python — version in range AND tkinter works.
    "$PYTHON_BIN" -c "import sys, tkinter; assert (3,9) <= sys.version_info < (3,13)" 2>/dev/null \
        || fail "Python was installed but doesn't seem usable (wrong version, or tkinter is missing)."
    echo "    All set: $("$PYTHON_BIN" --version)"
fi

# -------------------------------------------------------------
# Step 2: Set up the virtual environment (a folder for all the libraries)
# -------------------------------------------------------------
# A venv keeps Cross Guard's libraries separate from the rest of your system,
# so nothing else on your Mac gets affected. Lives in a hidden .venv folder.
echo
echo "Step 2 of 4: Setting up the virtual environment..."
VENV_DIR="$SCRIPT_DIR/.venv"

# If the venv exists but is broken (e.g. you upgraded Python and the old
# venv now points at a Python that's gone), throw it away and start fresh.
if [ -d "$VENV_DIR" ]; then
    if ! "$VENV_DIR/bin/python" --version >/dev/null 2>&1; then
        echo "    The existing .venv looks broken — wiping it and starting fresh."
        rm -rf "$VENV_DIR"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "    Creating .venv (using $PYTHON_BIN)..."
    "$PYTHON_BIN" -m venv "$VENV_DIR" || fail "Couldn't create the virtual environment."
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate" || fail "Couldn't activate the virtual environment."
echo "    Using: $(which python)  ($(python --version))"

# -------------------------------------------------------------
# Step 3: Install Cross Guard's dependencies (only if needed)
# -------------------------------------------------------------
# We only run pip install if requirements.txt has actually changed since
# last time. We check that by hashing the file and comparing to a saved hash.
# That way, normal launches stay fast — no pip running every time.
echo
echo "Step 3 of 4: Checking the libraries..."
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    fail "requirements.txt is missing. Are you running this from the Cross Guard project folder?"
fi

REQ_HASH_FILE="$VENV_DIR/.req_hash"
CURRENT_HASH=$(shasum -a 256 "$SCRIPT_DIR/requirements.txt" | awk '{print $1}')
INSTALLED_HASH=""
[ -f "$REQ_HASH_FILE" ] && INSTALLED_HASH=$(cat "$REQ_HASH_FILE" 2>/dev/null || echo "")

if [ "$CURRENT_HASH" != "$INSTALLED_HASH" ]; then
    echo "    First run (or requirements.txt changed) — installing libraries now."
    echo "    This usually takes 2 to 5 minutes. Needs internet."
    require_internet
    python -m pip install --upgrade pip --quiet || fail "Couldn't upgrade pip."
    python -m pip install -r "$SCRIPT_DIR/requirements.txt" \
        || fail "Library install failed. Usually this is no internet, or a package needs Apple's command line tools — try running 'xcode-select --install' in Terminal, then double-click this file again."
    echo "$CURRENT_HASH" > "$REQ_HASH_FILE"
    echo "    All libraries installed."
else
    echo "    Everything is already up to date."
fi

# -------------------------------------------------------------
# Step 4: Launch the GUI
# -------------------------------------------------------------
echo
echo "Step 4 of 4: Starting Cross Guard..."
echo "==========================================================="
if [ ! -f "$SCRIPT_DIR/run_gui.py" ]; then
    fail "run_gui.py is missing from this folder. Can't start the app."
fi

python "$SCRIPT_DIR/run_gui.py"
EXIT_CODE=$?

# If the app crashed, hold the window open so the user can read the error
# instead of having Terminal slam shut on them.
if [ $EXIT_CODE -ne 0 ]; then
    echo
    echo "Cross Guard closed with an error (exit code $EXIT_CODE)."
    echo "Press Return to close this window..."
    read -r _ || true
    exit $EXIT_CODE
fi
