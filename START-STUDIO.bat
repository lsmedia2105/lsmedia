@echo off
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8:backslashreplace"
cd /d "%~dp0scene-studio"
py -3.11 server.py
if errorlevel 1 (
 echo Can Python 3.11 64-bit. Xem loi o tren.
 pause
)
