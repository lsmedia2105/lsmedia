@echo off
cd /d "%~dp0scene-studio"
py -3.11 server.py
if errorlevel 1 (
 echo Can Python 3.11 64-bit. Xem loi o tren.
 pause
)
