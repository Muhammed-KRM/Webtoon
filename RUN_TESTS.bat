@echo off
echo ========================================
echo Webtoon AI Translator - Test Suite
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [HATA] Sanal ortam bulunamadi! SETUP.bat calistirin.
    pause
    exit /b
)

call venv\Scripts\activate.bat


echo Testler calistiriliyor...
echo.

set PYTHONPATH=.
pytest tests/ -v


echo.
if %errorlevel% neq 0 (
    echo [HATA] Bazi testler basarisiz oldu!
) else (
    echo [BASARILI] Tum testler gecti.
)

pause
