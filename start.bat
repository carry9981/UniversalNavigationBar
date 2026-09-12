@echo off
REM Universal Navigation Bar - launcher
setlocal
title Universal Navigation Bar
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+ and run install.bat first.
    pause
    exit /b 1
)

REM Auto-install dependencies on first run
python -c "import PyQt6, pynput, pyperclip, uiautomation" >nul 2>nul
if errorlevel 1 (
    echo [INFO] First run: installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo   Universal Navigation Bar
echo ============================================
echo   The app stays in the system tray.
echo   Manage items/config from the tray menu.
echo.
echo   NOTE: If target apps run as Administrator,
echo   re-run this script as Administrator too.
echo.

REM Resolve pythonw (GUI, no console window) next to python.exe
set "PYTHONW="
for /f "delims=" %%P in ('python -c "import sys,os;print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"') do set "PYTHONW=%%P"

if defined PYTHONW if exist "%PYTHONW%" (
    start "UniversalNavBar" "%PYTHONW%" -m src.main
) else (
    start "UniversalNavBar" python -m src.main
)

echo Started. If the tray icon is missing, check the dependencies above.
pause
