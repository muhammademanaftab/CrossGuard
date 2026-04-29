#!/bin/bash
# Cross Guard launcher for Mac. Double-click to run.

set -uo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

echo "==========================================================="
echo " Cross Guard Launcher  —  $(date '+%Y-%m-%d %H:%M:%S')"
echo "==========================================================="
echo "Project folder: $SCRIPT_DIR"
echo

fail() {
    echo
    echo "  Cross Guard could not start: $1"
    echo
    echo "Press Return to close this window..."
    read -r _ || true
    exit 1
}

require_internet() {
    if ! curl -s --head --max-time 5 https://www.python.org/ >/dev/null 2>&1; then
        fail "No internet connection. The first-time setup needs to download some things."
    fi
}

# Prefer 3.11: its Tk 8.6 keeps the GUI snappy and drag-and-drop working. Tk 9 breaks both.
echo "Step 1 of 4: Looking for Python on your Mac..."
PYTHON_BIN=""
for cmd in python3.11 python3.10 python3.9 python3.12; do
    if command -v "$cmd" >/dev/null 2>&1; then
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        if [ -n "$ver" ]; then
            if ! "$cmd" -c "import tkinter" >/dev/null 2>&1; then
                echo "    Skipping $cmd (Python $ver) — missing tkinter."
                continue
            fi
            tkver=$("$cmd" -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null || true)
            tkmajor=$(echo "$tkver" | cut -d. -f1)
            if [ "$tkmajor" != "8" ]; then
                echo "    Skipping $cmd (Python $ver) — Tk $tkver, need 8.x."
                continue
            fi
            PYTHON_BIN=$(command -v "$cmd")
            echo "    Found Python $ver with Tk $tkver at $PYTHON_BIN"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "    No Python found. Installing Python 3.11 for you."
    require_internet

    if command -v brew >/dev/null 2>&1; then
        echo "    Using Homebrew (no password needed)..."
        brew install python@3.11 || fail "Homebrew couldn't install python@3.11."
        if [ -x "$(brew --prefix python@3.11)/bin/python3.11" ]; then
            PYTHON_BIN="$(brew --prefix python@3.11)/bin/python3.11"
        elif command -v python3.11 >/dev/null 2>&1; then
            PYTHON_BIN="$(command -v python3.11)"
        else
            fail "Homebrew said it installed Python, but I can't find python3.11."
        fi
    else
        echo "    Homebrew isn't installed. Downloading from python.org..."
        PYTHON_VERSION="3.11.10"
        PKG_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-macos11.pkg"
        PKG_FILE="${TMPDIR:-/tmp}/python_${PYTHON_VERSION}_installer.pkg"
        curl -L --fail --progress-bar -o "$PKG_FILE" "$PKG_URL" || fail "Couldn't download the Python installer."
        echo
        echo "    Mac will ask for your password — that's the official python.org installer."
        sudo installer -pkg "$PKG_FILE" -target / || fail "The Python installer didn't finish."
        rm -f "$PKG_FILE"
        export PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:$PATH"
        if command -v python3.11 >/dev/null 2>&1; then
            PYTHON_BIN="$(command -v python3.11)"
        else
            fail "Python installed, but python3.11 isn't visible. Open a new Terminal and try again."
        fi
    fi

    "$PYTHON_BIN" -c "import sys, tkinter; assert (3,9) <= sys.version_info < (3,13)" 2>/dev/null \
        || fail "Python was installed but doesn't seem usable."
    echo "    All set: $("$PYTHON_BIN" --version)"
fi

echo
echo "Step 2 of 4: Setting up the virtual environment..."
VENV_DIR="$SCRIPT_DIR/.venv"

if [ -d "$VENV_DIR" ] && ! "$VENV_DIR/bin/python" --version >/dev/null 2>&1; then
    echo "    The existing .venv looks broken — wiping it."
    rm -rf "$VENV_DIR"
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "    Creating .venv (using $PYTHON_BIN)..."
    "$PYTHON_BIN" -m venv "$VENV_DIR" || fail "Couldn't create the virtual environment."
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate" || fail "Couldn't activate the virtual environment."
echo "    Using: $(which python)  ($(python --version))"

echo
echo "Step 3 of 4: Checking the libraries..."
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    fail "requirements.txt is missing. Are you running this from the Cross Guard project folder?"
fi

# Skip pip if requirements.txt hasn't changed since last run — keeps relaunches fast.
REQ_HASH_FILE="$VENV_DIR/.req_hash"
CURRENT_HASH=$(shasum -a 256 "$SCRIPT_DIR/requirements.txt" | awk '{print $1}')
INSTALLED_HASH=""
[ -f "$REQ_HASH_FILE" ] && INSTALLED_HASH=$(cat "$REQ_HASH_FILE" 2>/dev/null || echo "")

if [ "$CURRENT_HASH" != "$INSTALLED_HASH" ]; then
    echo "    Installing libraries (2-5 minutes, needs internet)..."
    require_internet
    python -m pip install --upgrade pip --quiet || fail "Couldn't upgrade pip."
    python -m pip install -r "$SCRIPT_DIR/requirements.txt" \
        || fail "Library install failed. Try 'xcode-select --install' in Terminal first."
    echo "$CURRENT_HASH" > "$REQ_HASH_FILE"
    echo "    All libraries installed."
else
    echo "    Everything is already up to date."
fi

echo
echo "Step 4 of 4: Starting Cross Guard..."
echo "==========================================================="
if [ ! -f "$SCRIPT_DIR/run_gui.py" ]; then
    fail "run_gui.py is missing from this folder."
fi

python "$SCRIPT_DIR/run_gui.py"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo
    echo "Cross Guard closed with an error (exit code $EXIT_CODE)."
    echo "Press Return to close this window..."
    read -r _ || true
    exit $EXIT_CODE
fi
