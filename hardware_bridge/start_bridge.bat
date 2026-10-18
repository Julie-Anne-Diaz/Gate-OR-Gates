@echo off
cd /d "%~dp0"
if exist ".venv\bin\python.exe" (
  ".venv\bin\python.exe" bridge_practical.py
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" bridge_practical.py
) else (
  echo Copy this file and bridge_practical.py beside your existing .venv folder.
)
pause
