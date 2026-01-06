@echo off
echo ========================================
echo Webtoon AI Translator - Baslatma
echo ========================================
echo.

REM Sanal ortam kontrolu
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Sanal ortam bulunamadi!
    echo Once SETUP.bat dosyasini calistirin.
    pause
    exit /b 1
)

REM .env dosyasi kontrolu
if not exist ".env" (
    echo HATA: .env dosyasi bulunamadi!
    echo Once .env dosyasi olusturun (ENV_OLUSTUR.md'ye bakin)
    pause
    exit /b 1
)

echo [1/4] Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat

echo [2/4] Redis kontrol ediliyor...
REM Redis kontrolu (Docker ile)
docker ps | findstr redis >nul 2>&1
if errorlevel 1 (
    echo Redis bulunamadi, baslatiliyor...
    docker run -d -p 6379:6379 --name redis redis:latest >nul 2>&1
    if errorlevel 1 (
        echo UYARI: Docker bulunamadi veya Redis baslatilamadi.
        echo Redis'i manuel olarak baslatin: docker run -d -p 6379:6379 redis
        echo Veya Memurai kullanin.
        timeout /t 3 >nul
    ) else (
        echo Redis baslatildi.
        timeout /t 2 >nul
    )
) else (
    echo Redis zaten calisiyor.
)

echo [3/4] Celery Worker baslatiliyor...
start "Celery Worker" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && celery -A app.operations.translation_manager.celery_app worker --loglevel=info --pool=solo"
timeout /t 3 >nul

echo [4/4] FastAPI baslatiliyor...
echo.
echo ========================================
echo Tum servisler baslatildi!
echo ========================================
echo.
echo Acik pencereler:
echo - Celery Worker: Arka planda calisiyor
echo - FastAPI: Bu pencerede calisacak
echo.
echo Tarayici otomatik acilacak...
echo.
echo Durdurmak icin: Ctrl+C (bu pencerede)
echo Tum servisleri durdurmak icin: STOP.bat
echo.
echo ========================================
echo.

REM FastAPI'yi arka planda baslat ve tarayiciyi ac
start "FastAPI Server" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && uvicorn main:app --reload"

REM Kisa bir bekleme (FastAPI'nin baslamasi icin)
timeout /t 5 >nul

REM Tarayiciyi ac
echo Tarayici aciliyor...
start http://localhost:8000/docs

echo.
echo ========================================
echo Tarayici acildi!
echo ========================================
echo.
echo API Dokumantasyonu: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo FastAPI ayri bir pencerede calisiyor.
echo Kapatmak icin o pencerede Ctrl+C yapin.
echo.
pause

pause

