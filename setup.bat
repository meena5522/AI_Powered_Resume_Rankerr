@echo off
echo ===================================================
echo   AI Resume Ranker - Automation Setup Script
echo ===================================================
echo.

:: Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please download and install Python 3.8+ from https://www.python.org/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/5] Creating Python Virtual Environment (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/5] Activating Virtual Environment and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [3/5] Downloading SpaCy NLP model (en_core_web_sm)...
python -m spacy download en_core_web_sm
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download SpaCy model.
    pause
    exit /b 1
)

echo [4/5] Generating candidate PDF resumes for testing...
python tests/generate_test_data.py
if %errorlevel% neq 0 (
    echo [WARNING] Could not generate sample PDF files. You can upload PDFs manually.
)

echo [5/5] Launching Flask server...
echo The application will be available at http://127.0.0.1:5000/
echo Press Ctrl+C in this terminal window to stop the server.
echo.
python app.py

pause
