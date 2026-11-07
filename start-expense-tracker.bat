@echo off
title Expenses Tracker - keep this window open
cd /d "%~dp0"
start "" /min cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000/"
echo.
echo  Expenses Tracker is running at:
echo  http://localhost:8000/
echo.
echo  Live SMS auto-import listens at:
echo  http://YOUR-PC-IP:8000/api/sms
echo.
echo  Keep this window open while using the app.
echo  Press Ctrl+C to stop the server.
echo.
python expense-server.py
echo.
echo Server stopped.
pause
