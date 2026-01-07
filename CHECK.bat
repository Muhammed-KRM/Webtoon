@echo off
title Webtoon AI Translator - System Status Check
color 0B

echo ============================================
echo   WEBTOON AI TRANSLATOR - SYSTEM CHECK
echo ============================================
echo.

set ERROR_COUNT=0

echo [1/6] Virtual Environment kontrolu...
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment mevcut
) else (
    echo [HATA] Virtual environment bulunamadi!
    set /a ERROR_COUNT+=1
)

echo.
echo [2/6] .env dosyasi kontrolu...
if exist ".env" (
    echo [OK] .env dosyasi mevcut
    
    REM OpenAI API key kontrolu
    findstr /C:"OPENAI_API_KEY=" .env | findstr /C:"sk-" >nul 2>&1
    if errorlevel 1 (
        echo [UYARI] OPENAI_API_KEY gecerli gorunmuyor!
    ) else (
        echo [OK] OPENAI_API_KEY ayarlanmis
    )
) else (
    echo [HATA] .env dosyasi bulunamadi!
    set /a ERROR_COUNT+=1
)

echo.
echo [3/6] Veritabani kontrolu...
if exist "webtoon.db" (
    echo [OK] Veritabani mevcut
) else (
    echo [UYARI] Veritabani bulunamadi! (Ilk kurulum olabilir)
)

echo.
echo [4/6] Redis kontrolu...
docker ps | findstr "webtoon_redis" >nul 2>&1
if errorlevel 1 (
    echo [HATA] Redis container calisiyor gorunmuyor!
    echo        Redis'i baslatmak icin: docker start webtoon_redis
    set /a ERROR_COUNT+=1
) else (
    echo [OK] Redis container calisiyor
)

echo.
echo [5/6] Python Process kontrolu...
tasklist | findstr /I "python.exe" >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python process calisiyor gorunmuyor!
    set /a ERROR_COUNT+=1
) else (
    echo [OK] Python process calisiyor
    tasklist | findstr /I "python.exe" | find /C "python.exe"
    echo        adet Python process bulundu
)

echo.
echo [6/6] Web Server kontrolu...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/health 2>nul | findstr "200" >nul 2>&1
if errorlevel 1 (
    echo [HATA] Web Server yanit vermiyor!
    echo        Port 8000 kontrol ediliyor...
    netstat -ano | findstr ":8000" >nul 2>&1
    if errorlevel 1 (
        echo [HATA] Port 8000 acik degil!
        set /a ERROR_COUNT+=1
    ) else (
        echo [UYARI] Port 8000 acik ama yanit vermiyor
        set /a ERROR_COUNT+=1
    )
) else (
    echo [OK] Web Server calisiyor ve yanit veriyor
)

echo.
echo ============================================
echo   KONTROL SONUCLARI
echo ============================================
echo.

if %ERROR_COUNT% equ 0 (
    echo [BASARILI] Tum kontroller gecti!
    echo.
    echo API Test: http://localhost:8000/health
    echo API Docs: http://localhost:8000/docs
    echo.
    echo Endpoint testi icin: python test_endpoints_detailed.py
) else (
    echo [UYARI] %ERROR_COUNT% hata bulundu!
    echo.
    echo Cozum onerileri:
    echo 1. SETUP_COMPLETE.bat dosyasini calistirin
    echo 2. START_ALL.bat dosyasini calistirin
    echo 3. Docker Desktop'in acik oldugundan emin olun
    echo.
)

echo ============================================
echo.
pause
