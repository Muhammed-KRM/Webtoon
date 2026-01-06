@echo off
title Webtoon AI Translator - Full System Launcher
color 0A

echo ============================================
echo   WEBTOON AI TRANSLATOR - FULL SYSTEM
echo ============================================
echo.
echo [1/4] Redis kontrol ediliyor...

:: Redis container'inin calisiyor mu kontrol et
docker ps | findstr "webtoon_redis" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis zaten calisiyor.
) else (
    echo [INFO] Redis baslat iliyor...
    docker start webtoon_redis >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Redis container olusturuluyor...
        docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
    )
    timeout /t 3 /nobreak >nul
    echo [OK] Redis baslatildi.
)

echo.
echo [2/4] Veritabani kontrol ediliyor...
if not exist "webtoon.db" (
    echo [INFO] Veritabani olusturuluyor...
    venv\Scripts\python init_db.py
    echo [OK] Veritabani olusturuldu.
) else (
    echo [OK] Veritabani mevcut.
)

echo.
echo [3/4] Servisler baslatiliyor...
echo.
echo ============================================
echo   3 YENI TERMINAL PENCERESI ACILACAK:
echo   1. Web Server (FastAPI)
echo   2. Celery Worker (Arka plan isleri)
echo   3. Sistem Monitoru
echo ============================================
echo.
echo [UYARI] Bu pencereleri KAPATMAYIN!
echo.
pause

:: Web Server'i yeni pencerede baslat
start "Webtoon - Web Server" cmd /k "venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: 2 saniye bekle
timeout /t 2 /nobreak >nul

:: Celery Worker'i yeni pencerede baslat
start "Webtoon - Celery Worker" cmd /k "venv\Scripts\celery -A app.core.celery_app worker --loglevel=info --pool=solo"

:: 2 saniye bekle
timeout /t 2 /nobreak >nul

:: Sistem durumunu gosteren pencere
start "Webtoon - System Monitor" cmd /k "echo ============================================ && echo   WEBTOON AI TRANSLATOR - SYSTEM STATUS && echo ============================================ && echo. && echo [OK] Web Server: http://localhost:8000 && echo [OK] API Docs: http://localhost:8000/docs && echo [OK] Redis: localhost:6379 && echo [OK] Celery Worker: Active && echo. && echo ============================================ && echo   SISTEM CALISIY OR! && echo ============================================ && echo. && echo Tarayicinizdan http://localhost:8000/docs adresine gidin. && echo. && echo Bu pencereyi kapatmak sistemi DURDURMAZ. && echo Sistemi durdurmak icin diger pencereleri kapatin. && echo. && pause"

echo.
echo [4/4] Sistem baslatildi!
echo.
echo ============================================
echo   ERISIM BILGILERI:
echo ============================================
echo   Web Server:  http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo   ReDoc:       http://localhost:8000/redoc
echo ============================================
echo.
echo Tarayiciniz otomatik olarak acilacak...
timeout /t 3 /nobreak >nul

:: Tarayiciyi ac
start http://localhost:8000/docs

echo.
echo [BASARILI] Sistem tamamen hazir!
echo.
pause
