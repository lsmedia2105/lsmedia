@echo off
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8:backslashreplace"
cd /d "%~dp0"
py -3.11 setup.py
if errorlevel 1 (
 echo Cai dat that bai. Can Python 3.11 64-bit va Internet. Xem loi o tren.
 pause
 exit /b 1
)
echo Cai dat xong. Mo START-WINDOWS.bat de chay.
pause
