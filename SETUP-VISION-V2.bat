@echo off
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8:backslashreplace"
where ollama >nul 2>nul
if errorlevel 1 (
 echo Can cai Ollama truoc: https://ollama.com/download/windows
 echo Cai xong va mo Ollama, roi chay lai file nay.
 pause
 exit /b 1
)
echo Dang tai model thi giac local. Can Internet va nhieu GB o trong.
ollama pull qwen2.5vl:3b
if errorlevel 1 (
 echo Tai model chua thanh cong. Kiem tra Ollama va Internet.
 pause
 exit /b 1
)
echo Da tai model. Mo START-STUDIO.bat de dung.
pause
