@echo off
echo ========================================
echo Complete Installation Script
echo ========================================
echo.
echo This will install ALL packages including optional ones.
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [1/5] Installing core requirements...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install core requirements!
    pause
    exit /b 1
)
echo ✓ Core packages installed

echo.
echo [2/5] Installing Hugging Face Transformers and PyTorch...
pip install transformers==4.36.2 torch==2.1.2 --quiet
if %errorlevel% neq 0 (
    echo WARNING: Failed to install transformers/torch
) else (
    echo ✓ Hugging Face Transformers installed
)

echo.
echo [3/5] Installing Argos Translate...
pip install argostranslate==1.9.0 --quiet
if %errorlevel% neq 0 (
    echo WARNING: Failed to install argostranslate
) else (
    echo ✓ Argos Translate installed
)

echo.
echo [4/5] Installing spaCy...
pip install spacy==3.7.2 --quiet
if %errorlevel% neq 0 (
    echo WARNING: Failed to install spacy
) else (
    echo ✓ spaCy installed
)

echo.
echo [5/6] Downloading spaCy language models...
echo Downloading English model (en_core_web_sm)...
python -m spacy download en_core_web_sm --quiet
if %errorlevel% neq 0 (
    echo WARNING: Failed to download English spaCy model
) else (
    echo ✓ English spaCy model downloaded
)

echo.
echo [6/6] Initializing Argos Translate packages...
python -c "import argostranslate.package; argostranslate.package.update_package_index(); print('✓ Argos Translate packages updated')" 2>nul
if %errorlevel% neq 0 (
    echo INFO: Argos Translate will download packages on first use
) else (
    echo ✓ Argos Translate ready
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo All packages installed:
echo - Core packages (FastAPI, Celery, etc.)
echo - Hugging Face Transformers (offline AI translation)
echo - Argos Translate (offline free translation)
echo - spaCy (advanced NER)
echo.
echo You can now run START.bat to start the application.
echo.
pause

