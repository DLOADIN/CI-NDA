@echo off
echo ========================================
echo CI-NDA Flask Backend Setup
echo ========================================
echo.

echo 1. Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from https://python.org
    pause
    exit /b 1
)
python --version

echo.
echo 2. Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

echo.
echo 3. Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 4. Installing Python dependencies...
pip install -r requirements.txt

echo.
echo 5. Creating .env file from template...
if not exist ".env" (
    copy .env.example .env
    echo .env file created. Please edit it with your database credentials.
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit the .env file with your database credentials
echo 2. Import database_schema.sql into phpMyAdmin
echo 3. Run: python server.py
echo.
echo Database setup:
echo - Open phpMyAdmin
echo - Import the file: database_schema.sql
echo - This will create the 'cinda_db' database with all tables
echo.
echo To start the server:
echo - Run: python server.py
echo - Server will be available at: http://localhost:5000
echo - API endpoints will be available at: http://localhost:5000/api
echo.
pause