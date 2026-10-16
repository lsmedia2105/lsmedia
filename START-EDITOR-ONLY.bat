@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0portable-launch.ps1" -EditorOnly
if errorlevel 1 (
 pause
 exit /b 1
)
