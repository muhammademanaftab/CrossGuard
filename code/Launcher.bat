@echo off
REM Cross Guard launcher for Windows. Double-click to run.

setlocal EnableDelayedExpansion

cd /d "%~dp0"
set "SCRIPT_DIR=%~dp0"

echo ===========================================================
echo  Cross Guard Launcher
echo ===========================================================
echo Project folder: %SCRIPT_DIR%
echo.

REM Prefer 3.11: its Tk 8.6 keeps the GUI snappy and drag-and-drop working. Tk 9 breaks both.
echo Step 1 of 4: Looking for Python on your PC...
set "PYTHON_BIN="
for %%V in (3.11 3.10 3.9 3.12) do (
    if not defined PYTHON_BIN call :try_python %%V
)

if not defined PYTHON_BIN (
    echo     No usable Python found. Installing Python 3.11 for you.
    call :install_python
    if errorlevel 1 goto :fail
    call :try_python 3.11
)

if not defined PYTHON_BIN (
    echo     Python was installed, but I can't see it yet in this window.
    echo     Open a new Command Prompt and double-click this file again.
    goto :fail
)

echo.
echo Step 2 of 4: Setting up the virtual environment...
set "VENV_DIR=%SCRIPT_DIR%.venv"

if exist "%VENV_DIR%\Scripts\python.exe" (
    "%VENV_DIR%\Scripts\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo     The existing .venv looks broken -- wiping it.
        rmdir /s /q "%VENV_DIR%"
    )
)

if not exist "%VENV_DIR%" (
    echo     Creating .venv ^(using !PYTHON_BIN!^)...
    "!PYTHON_BIN!" -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo     Couldn't create the virtual environment.
        goto :fail
    )
)

call "%VENV_DIR%\Scripts\activate.bat"
echo     Using: %VENV_DIR%\Scripts\python.exe

echo.
echo Step 3 of 4: Checking the libraries...
if not exist "%SCRIPT_DIR%requirements.txt" (
    echo     ERROR: requirements.txt is missing. Are you running this from the Cross Guard project folder?
    goto :fail
)

REM Skip pip if requirements.txt hasn't changed since last run -- keeps relaunches fast.
set "REQ_HASH_FILE=%VENV_DIR%\.req_hash"
set "CURRENT_HASH="
for /f "delims=" %%H in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-FileHash -Algorithm SHA256 -LiteralPath '%SCRIPT_DIR%requirements.txt').Hash"') do set "CURRENT_HASH=%%H"

set "INSTALLED_HASH="
if exist "%REQ_HASH_FILE%" set /p INSTALLED_HASH=<"%REQ_HASH_FILE%"

if not "!CURRENT_HASH!"=="!INSTALLED_HASH!" (
    echo     Installing libraries ^(2-5 minutes, needs internet^)...
    python -m pip install --upgrade pip --quiet
    if errorlevel 1 (
        echo     Couldn't upgrade pip.
        goto :fail
    )
    python -m pip install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo     Library install failed. May need Microsoft C++ Build Tools:
        echo     https://visualstudio.microsoft.com/visual-cpp-build-tools/
        goto :fail
    )
    ^(echo !CURRENT_HASH!^)>"%REQ_HASH_FILE%"
    echo     All libraries installed.
) else (
    echo     Everything is already up to date.
)

echo.
echo Step 4 of 4: Starting Cross Guard...
echo ===========================================================
if not exist "%SCRIPT_DIR%run_gui.py" (
    echo     ERROR: run_gui.py is missing from this folder.
    goto :fail
)

python "%SCRIPT_DIR%run_gui.py"
set "EXIT_CODE=!errorlevel!"

if not "!EXIT_CODE!"=="0" (
    echo.
    echo Cross Guard closed with an error ^(exit code !EXIT_CODE!^).
    echo.
    echo Press any key to close this window...
    pause >nul
    exit /b !EXIT_CODE!
)
exit /b 0

:try_python
py -%1 -c "import sys" >nul 2>&1
if errorlevel 1 exit /b 0

py -%1 -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo     Skipping Python %1 -- missing tkinter.
    exit /b 0
)

for /f "delims=" %%T in ('py -%1 -c "import tkinter; print(tkinter.TkVersion)" 2^>nul') do set "TKVER=%%T"
if not "!TKVER:~0,1!"=="8" (
    echo     Skipping Python %1 -- Tk !TKVER!, need 8.x.
    exit /b 0
)

for /f "delims=" %%P in ('py -%1 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_BIN=%%P"
echo     Found Python %1 with Tk !TKVER! at !PYTHON_BIN!
exit /b 0

:install_python
where winget >nul 2>&1
if not errorlevel 1 (
    echo     Using winget ^(no password needed^)...
    winget install --id Python.Python.3.11 --source winget --silent --accept-source-agreements --accept-package-agreements
    if not errorlevel 1 (
        if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
            set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;!PATH!"
        )
        exit /b 0
    )
    echo     winget didn't succeed. Falling back to direct download.
)

set "PY_VERSION=3.11.10"
set "PKG_URL=https://www.python.org/ftp/python/%PY_VERSION%/python-%PY_VERSION%-amd64.exe"
set "PKG_FILE=%TEMP%\cg_python_%PY_VERSION%.exe"

echo     Downloading the official Python installer...
curl -L --fail --progress-bar -o "%PKG_FILE%" "%PKG_URL%"
if errorlevel 1 (
    echo     Couldn't download the installer. Check your internet.
    exit /b 1
)

echo     Running the installer ^(per-user, no password needed^)...
"%PKG_FILE%" /passive InstallAllUsers=0 PrependPath=1 Include_launcher=1
if errorlevel 1 (
    echo     The installer didn't finish.
    exit /b 1
)
del /q "%PKG_FILE%" >nul 2>&1

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;!PATH!"
)
exit /b 0

:fail
echo.
echo   Cross Guard could not start.
echo.
echo Press any key to close this window...
pause >nul
exit /b 1
