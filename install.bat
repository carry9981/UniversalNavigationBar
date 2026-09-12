@echo off
REM Universal Navigation Bar - installer
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+ first.
    pause
    exit /b 1
)

echo [1/2] Installing dependencies...
python -m pip install -r requirements.txt

echo [2/2] Registering auto-start on login...
python -c "import sys; sys.path.insert(0, 'src'); from utils.autostart import set_enabled; set_enabled(True)"

echo.
echo Install finished. Launch the app with start.bat
echo.
pause
