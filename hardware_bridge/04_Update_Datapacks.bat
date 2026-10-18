@echo off
cd /d "%~dp0"
python "tools\update_datapacks.py"
if errorlevel 1 echo Check the error above.
pause
