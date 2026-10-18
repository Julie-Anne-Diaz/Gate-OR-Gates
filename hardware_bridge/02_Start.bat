@echo off
cd /d "%~dp0"
python "tools\launch.py"
if errorlevel 1 echo Check the error above.
pause
