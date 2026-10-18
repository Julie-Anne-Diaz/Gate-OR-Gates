@echo off
cd /d "%~dp0"
python "tools\run_bridge.py"
if errorlevel 1 echo Check the error above.
pause
