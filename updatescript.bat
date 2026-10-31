@echo off
setlocal
set "STAGING=%~1"
set "TARGET=%~2"
set "WORK=%~3"
set "UPDATE_LOG=%WORK%\update.log"

rem Give the closing app a moment to release its files.
ping -n 3 127.0.0.1 >nul
robocopy "%STAGING%" "%TARGET%" /E /MOVE /R:3 /W:1 /LOG:"%UPDATE_LOG%" >nul
if errorlevel 8 goto failed

rem robocopy can exit 0 without copying anything when it cannot open the
rem install folder. /MOVE removes every copied file from staging, so any
rem file left behind means the update did not install.
dir /s /b /a-d "%STAGING%" 2>nul | findstr "^" >nul && goto failed

rd /s /q "%STAGING%" >nul 2>&1
call :relaunch
goto cleanup

:failed
call :relaunch
powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [void][System.Windows.MessageBox]::Show('VALORANT Rank Yoinker could not install the update. Details: ' + $env:UPDATE_LOG, 'VALORANT Rank Yoinker Update')"
goto cleanup

:relaunch
rem The script may run as administrator for Program Files installs. Starting
rem the app through Explorer keeps the relaunched app un-elevated.
explorer.exe "%TARGET%\vry.exe"
exit /b

:cleanup
rem Deleting a running batch file normally prints "The batch file cannot be
rem found." Leaving the script first avoids that message.
(goto) 2>nul & del "%~f0"
