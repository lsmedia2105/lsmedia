@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0portable-launch.ps1"
if errorlevel 1 (
 echo Khong khoi dong duoc. Xem loi o tren. Ban chi editor: START-EDITOR-ONLY.bat
 pause
 exit /b 1
)
