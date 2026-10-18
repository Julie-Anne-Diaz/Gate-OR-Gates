@echo off
cd /d "%~dp0"
python "tools\setup.py"
if errorlevel 1 echo Check the error above.
pause
