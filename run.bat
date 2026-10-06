@echo off
setlocal
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set HELPMORA_JWT_SECRET=helpmora_local_secret_key_1234567890123456
cd /d "%~dp0helpmora"
echo Starting HELPmora at http://localhost:8000 ...
"%~dp0.venv312\Scripts\python.exe" -m jaclang start app.jac --no-dev --port 8000 --host 127.0.0.1
endlocal
