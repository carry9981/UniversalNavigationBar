@echo off
REM Universal Navigation Bar - uninstaller
setlocal
cd /d "%~dp0"

echo [1/1] Removing auto-start on login...
python -c "import sys; sys.path.insert(0, 'src'); from utils.autostart import set_enabled; set_enabled(False)"

echo.
echo Done. To fully remove the app, delete this folder and:
echo     %APPDATA%\UniversalNavBar
echo.
pause
