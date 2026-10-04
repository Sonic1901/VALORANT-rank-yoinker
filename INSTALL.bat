@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -3.11 -m venv .venv
    if %ERRORLEVEL% NEQ 0 py -3 -m venv .venv
) else (
    python -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
    echo Could not create the Python virtual environment.
    echo Install Python 3.10 or 3.11 and try again.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo.
echo Dependencies installed in .venv successfully.
echo Run START.bat to launch the WebView2 app.
pause
