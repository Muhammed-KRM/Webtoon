@echo off
title Webtoon AI Translator - Endpoint Test
color 0B

echo ============================================
echo   WEBTOON AI TRANSLATOR - ENDPOINT TEST
echo ============================================
echo.

echo Sistem kontrol ediliyor...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/health 2>nul | findstr "200" >nul 2>&1
if errorlevel 1 (
    echo [HATA] Web Server calisiyor gorunmuyor!
    echo        Lutfen once START_ALL.bat dosyasini calistirin.
    echo.
    pause
    exit /b 1
)

echo [OK] Web Server calisiyor
echo.
echo Endpoint testleri baslatiliyor...
echo Bu islem birka dakika surebilir...
echo.

venv\Scripts\python.exe test_endpoints_detailed.py

echo.
echo Test tamamlandi!
echo Rapor dosyasi olusturuldu: endpoint_test_report_*.txt
echo.
pause

