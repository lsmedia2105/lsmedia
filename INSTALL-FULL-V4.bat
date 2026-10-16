@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0portable-launch.ps1" -InstallOnly
if errorlevel 1 (
 echo Mot so thanh phan chua cai xong. Xem loi o tren va thu lai khi co Internet.
 pause
 exit /b 1
)
echo Da chuan bi xong. Chay START-STUDIO.bat.
pause
