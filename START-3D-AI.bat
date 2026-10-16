@echo off
cd /d "%~dp0photo-3d-ai"
if not exist ".venv\Scripts\python.exe" (
 echo Lan dau: cai Python 3.11 64-bit, roi chay INSTALL-WINDOWS.bat trong photo-3d-ai.
 pause
 exit /b 1
)
call START-WINDOWS.bat
