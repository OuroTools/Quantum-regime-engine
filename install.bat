@echo off
cd /d "%~dp0"
echo ========================================
echo  Regime Detection Engine - Install
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo Installing package and all dependencies...
python -m pip install --upgrade pip
python -m pip install -e ".[all]"

if errorlevel 1 (
    echo.
    echo Install failed. Try: pip install -e .
    pause
    exit /b 1
)

echo.
echo Running verification...
python scripts\verify.py

echo.
echo ========================================
echo  Install complete!
echo ========================================
echo.
echo   regime-engine          - run analysis in terminal
echo   regime-dashboard       - open web dashboard
echo   python main.py         - same as regime-engine
echo.
pause
