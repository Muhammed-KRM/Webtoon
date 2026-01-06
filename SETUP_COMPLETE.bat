@echo off
title Webtoon AI Translator - Complete Setup
color 0B

echo ============================================
echo   WEBTOON AI TRANSLATOR
echo   COMPLETE INSTALLATION SCRIPT
echo ============================================
echo.
echo Bu script tum kurulum adimlarini otomatik olarak gerceklestirir.
echo Lutfen bekleyin...
echo.
pause

:: Check Python
echo [1/8] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi!
    echo Lutfen Python 3.10+ yukleyin: https://www.python.org/downloads/
    echo Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin!
    pause
    exit /b 1
)
echo [OK] Python bulundu.

:: Check Docker
echo.
echo [2/8] Docker kontrol ediliyor...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] Docker bulunamadi!
    echo Docker Desktop'i yukleyin: https://www.docker.com/products/docker-desktop/
    echo Kurulum sonrasi bilgisayari yeniden baslatin.
    echo.
    echo Simdilik Docker olmadan devam ediliyor...
    set DOCKER_AVAILABLE=0
) else (
    echo [OK] Docker bulundu.
    set DOCKER_AVAILABLE=1
)

:: Create Virtual Environment
echo.
echo [3/8] Virtual environment olusturuluyor...
if exist "venv" (
    echo [INFO] Virtual environment zaten mevcut.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [HATA] Virtual environment olusturulamadi!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment olusturuldu.
)

:: Activate Virtual Environment
echo.
echo [4/8] Virtual environment aktif ediliyor...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [HATA] Virtual environment aktif edilemedi!
    pause
    exit /b 1
)
echo [OK] Virtual environment aktif.

:: Upgrade pip
echo.
echo [5/8] pip guncelleniyor...
python -m pip install --upgrade pip --quiet
echo [OK] pip guncellendi.

:: Install Requirements
echo.
echo [6/8] Python paketleri kuruluyor...
echo [INFO] Bu islem birka dakika surebilir...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [HATA] Paketler kurulamadi!
    echo Manuel kurulum icin: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Tum paketler kuruldu.

:: Create .env file if not exists
echo.
echo [7/8] Yapilandirma dosyasi kontrol ediliyor...
if not exist ".env" (
    echo [INFO] .env dosyasi olusturuluyor...
    (
        echo SECRET_KEY=development_secret_key_change_in_production_32chars
        echo DATABASE_URL=sqlite:///./webtoon.db
        echo OPENAI_API_KEY=sk-your-openai-api-key-here
        echo REDIS_URL=redis://localhost:6379/0
        echo CDN_ENABLED=False
        echo STRIPE_SECRET_KEY=sk_test_your-stripe-key-here
        echo LOG_LEVEL=INFO
        echo ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
    ) > .env
    echo [OK] .env dosyasi olusturuldu.
    echo [UYARI] Production ortaminda .env dosyasindaki anahtarlari degistirin!
) else (
    echo [OK] .env dosyasi mevcut.
)

:: Initialize Database
echo.
echo [8/8] Veritabani olusturuluyor...
python init_db.py
if %errorlevel% neq 0 (
    echo [UYARI] Veritabani olusturulamadi. Manuel olarak calistirin: python init_db.py
) else (
    echo [OK] Veritabani olusturuldu.
)

:: Setup Docker Redis
if %DOCKER_AVAILABLE%==1 (
    echo.
    echo [BONUS] Docker Redis container olusturuluyor...
    docker ps | findstr "webtoon_redis" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Redis container zaten calisiyor.
    ) else (
        docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] Redis container olusturuldu ve baslatildi.
        ) else (
            echo [INFO] Redis container olusturulamadi. Manuel olarak olusturun:
            echo docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
        )
    )
)

:: Summary
echo.
echo ============================================
echo   KURULUM TAMAMLANDI!
echo ============================================
echo.
echo [BASARILI] Tum adimlar tamamlandi.
echo.
echo SONRAKI ADIMLAR:
echo.
if %DOCKER_AVAILABLE%==0 (
    echo 1. Docker Desktop'i yukleyin ve basla tin
    echo    https://www.docker.com/products/docker-desktop/
    echo.
    echo 2. Bilgisayari yeniden baslatin
    echo.
    echo 3. Docker Desktop'i acin
    echo.
    echo 4. Asagidaki komutu calistirin:
    echo    docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
    echo.
    echo 5. START_ALL.bat dosyasini calistirin
) else (
    echo 1. Docker Desktop'in acik oldugunu kontrol edin
    echo.
    echo 2. START_ALL.bat dosyasini calistirin
    echo.
    echo 3. Tarayicinizda http://localhost:8000/docs adresine gidin
)
echo.
echo ============================================
echo.
echo YARDIM:
echo - Hizli Baslangic: HIZLI_BASLANGIC.md
echo - Kurulum Dokumani: KURULUM_DOKUMANI.md
echo - API Dokumantasyonu: http://localhost:8000/docs
echo.
echo ============================================
echo.
pause
