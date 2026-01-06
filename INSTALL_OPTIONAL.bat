@echo off
echo ========================================
echo Installing Optional Packages
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run SETUP.bat first or create venv manually.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [1/4] Installing Hugging Face Transformers and PyTorch...
pip install transformers==4.36.2 torch==2.1.2 --quiet
if %errorlevel% neq 0 (
    echo WARNING: Failed to install transformers/torch
) else (
    echo ✓ Hugging Face Transformers installed
)

echo.
echo [2/4] Installing Argos Translate...
pip install argostranslate==1.9.0 --quiet
if %errorlevel% neq 0 (
    echo WARNING: Failed to install argostranslate
) else (
    echo ✓ Argos Translate installed
)

echo.
echo [3/4] Installing spaCy...
pip install spacy==3.7.2 --quiet
if %errorlevel% neq 0 (
    echo WARNING: Failed to install spacy
) else (
    echo ✓ spaCy installed
)

echo.
echo [4/5] Downloading spaCy language models...
echo Downloading English model (en_core_web_sm)...
python -m spacy download en_core_web_sm --quiet
if %errorlevel% neq 0 (
    echo WARNING: Failed to download English spaCy model
) else (
    echo ✓ English spaCy model downloaded
)

echo.
echo [5/5] Initializing Argos Translate packages...
python -c "import argostranslate.package; argostranslate.package.update_package_index(); print('✓ Argos Translate packages updated')" 2>nul
if %errorlevel% neq 0 (
    echo INFO: Argos Translate will download packages on first use
) else (
    echo ✓ Argos Translate ready
)

echo.
echo ========================================
echo Optional Packages Installation Complete!
echo ========================================
echo.
echo Installed packages:
echo - Hugging Face Transformers (for offline AI translation)
echo - Argos Translate (for offline free translation)
echo - spaCy (for advanced named entity recognition)
echo.
echo Your translation system will now automatically use these
echo services when available, with Google Translate as fallback.
echo.
pause

