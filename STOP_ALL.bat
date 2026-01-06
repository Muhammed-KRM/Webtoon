@echo off
title Webtoon AI Translator - System Shutdown
color 0C

echo ============================================
echo   WEBTOON AI TRANSLATOR - SHUTDOWN
echo ============================================
echo.
echo [UYARI] Tum servisler kapatilacak!
echo.
pause

echo.
echo [1/3] Redis durduruluyor...
docker stop webtoon_redis >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis durduruldu.
) else (
    echo [INFO] Redis zaten durmus.
)

echo.
echo [2/3] Celery Worker durduruluyor...
taskkill /FI "WINDOWTITLE eq Webtoon - Celery Worker*" /F >nul 2>&1
echo [OK] Celery Worker durduruldu.

echo.
echo [3/3] Web Server durduruluyor...
taskkill /FI "WINDOWTITLE eq Webtoon - Web Server*" /F >nul 2>&1
echo [OK] Web Server durduruldu.

echo.
echo ============================================
echo   TUM SERVISLER DURDURULDU
echo ============================================
echo.
pause
