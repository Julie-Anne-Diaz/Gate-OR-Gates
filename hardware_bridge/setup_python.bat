@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 goto failed
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
) else if exist ".venv\bin\python.exe" (
  ".venv\bin\python.exe" -m pip install -r requirements.txt
) else (
  goto failed
)
if errorlevel 1 goto failed
echo Ready. Configure COM port in bridge_practical.py before starting.
pause
exit /b 0
:failed
echo Setup failed. Use a Python installation that supports venv and pip.
pause
exit /b 1
