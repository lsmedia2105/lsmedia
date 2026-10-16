@echo off
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8:backslashreplace"
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Hay chay INSTALL-WINDOWS.bat truoc.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" app.py
if errorlevel 1 (
 echo Tool gap loi. Hay xem noi dung o tren.
 pause
)
