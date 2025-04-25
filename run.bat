@echo off
REM Simple one-click installer/launcher for Windows
echo Setting up Interior Design Generator...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.8+ from python.org first.
    pause
    exit /b
)

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install requirements
pip install -r requirements.txt

REM Launch the app
echo Starting the Interior Design Generator...
streamlit run main.py

pause
