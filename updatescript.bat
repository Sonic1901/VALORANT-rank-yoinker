@echo off
setlocal
set "STAGING=%~1"
set "TARGET=%~2"
set "WORK=%~3"

timeout /t 2 /nobreak >nul
robocopy "%STAGING%" "%TARGET%" /E /MOVE /R:3 /W:1 >nul
if errorlevel 8 exit /b 1

rd /s /q "%STAGING%" >nul 2>&1
start "" "%TARGET%\vry.exe"
del "%~f0"
