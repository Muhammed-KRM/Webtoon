@echo off
echo ========================================
echo Webtoon AI Translator - Durdurma
echo ========================================
echo.

echo [1/3] Celery Worker durduruluyor...
taskkill /FI "WINDOWTITLE eq Celery Worker*" /T /F >nul 2>&1
if errorlevel 1 (
    echo Celery Worker bulunamadi veya zaten durdurulmus.
) else (
    echo Celery Worker durduruldu.
)

echo [2/3] Python process'leri durduruluyor...
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq uvicorn*" /T /F >nul 2>&1
if errorlevel 1 (
    echo FastAPI process bulunamadi.
) else (
    echo FastAPI durduruldu.
)

echo [3/3] Redis durduruluyor (Docker)...
docker stop redis >nul 2>&1
if errorlevel 1 (
    echo Redis container bulunamadi veya zaten durdurulmus.
) else (
    echo Redis durduruldu.
)

echo.
echo ========================================
echo Tum servisler durduruldu!
echo ========================================
echo.
pause

