@echo off
title CI-NDA Flask Backend Server

echo ========================================
echo Starting CI-NDA Flask Backend Server
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo Please edit .env file with your database credentials before continuing.
    echo Press any key when ready...
    pause
)

:: Start the Flask server
echo.
echo Starting Flask server...
echo Server will be available at: http://localhost:5000
echo API endpoints at: http://localhost:5000/api
echo.
echo Press Ctrl+C to stop the server
echo.

python server.py

pause