@echo off
cd /d "%~dp0"
java -Xms1G -Xmx2G -jar server.jar nogui
pause
