@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" launcher.py
    exit /b 0
)

if exist ".venv\Scripts\python.exe" (
    echo pythonw.exe was not found. Starting visibly for diagnostics...
    ".venv\Scripts\python.exe" launcher.py
    pause
    exit /b 1
)

echo Dependencies are not installed.
echo Run INSTALL.bat first.
pause
