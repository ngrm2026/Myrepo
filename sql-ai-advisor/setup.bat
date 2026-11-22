@echo off
REM One-time setup on Windows: creates a virtual environment and installs packages.
cd /d "%~dp0"
python -m venv .venv || (echo Python 3.10+ is required & exit /b 1)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo.
echo Setup done. Edit .env (server, database, LLM key), then run run.bat
