@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo Open your browser at http://127.0.0.1:8000 after the server starts.
.venv\Scripts\python.exe server.py
pause
exit /b
:fail
echo Setup failed. Read the message above. Python 3.12 is recommended.
pause
exit /b 1
