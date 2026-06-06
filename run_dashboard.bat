@echo off
cd /d "%~dp0"
echo Starting Regime Detection Engine dashboard...
echo Open http://localhost:8501 in your browser.
regime-dashboard 2>nul || streamlit run dashboard.py
