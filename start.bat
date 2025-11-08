@echo off
echo ========================================
echo    CI-NDA Full-Stack Application
echo    Starting Backend and Frontend
echo ========================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo IMPORTANT: Database Setup Required
echo ========================================
echo Please ensure you have:
echo 1. MySQL/XAMPP running on localhost:3306
echo 2. Database 'ci_nda_db' created
echo 3. Tables imported from database_schema.sql
echo 4. Database credentials match your .env file
echo.
echo Press any key when database is ready...
pause > nul

echo.
echo Starting Flask backend server...
echo Backend will run on: http://localhost:5000
echo.

start "CI-NDA Backend" cmd /k "python server.py"

echo.
echo ========================================
echo Opening application in browser...
echo ========================================
echo.
echo Main Application: http://localhost:5000 (served by Flask)
echo Authentication: http://localhost:5000/authentication.html
echo Test Page: http://localhost:5000/test_backend.html
echo.

timeout /t 3 /nobreak > nul

echo Opening browser...
start http://localhost:5000/index.html

echo.
echo ========================================
echo CI-NDA Application Started!
echo ========================================
echo.
echo Backend API: http://localhost:5000/api
echo Frontend: http://localhost:5000
echo.
echo To stop the application:
echo 1. Close this window
echo 2. Press Ctrl+C in the backend window
echo.
echo For testing, visit: http://localhost:5000/test_backend.html
echo.
pause