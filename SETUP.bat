@echo off
echo ========================================
echo Webtoon AI Translator - Setup Script
echo ========================================
echo.

echo [1/5] Sanal ortam oluşturuluyor...
python -m venv venv
if errorlevel 1 (
    echo HATA: Python bulunamadı! Python 3.10+ yüklü olduğundan emin olun.
    pause
    exit /b 1
)

echo [2/5] Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat

echo [3/5] Paketler yükleniyor...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo HATA: Paket yükleme başarısız!
    pause
    exit /b 1
)

echo [4/5] .env dosyası kontrol ediliyor...
if not exist .env (
    echo .env dosyası bulunamadı, .env.example'dan kopyalanıyor...
    copy .env.example .env
    echo.
    echo ========================================
    echo ONEMLI: .env dosyasini duzenleyin!
    echo ========================================
    echo 1. SECRET_KEY: En az 32 karakter rastgele string
    echo 2. DATABASE_URL: PostgreSQL veya SQLite
    echo 3. OPENAI_API_KEY: API key'inizi ekleyin
    echo.
    echo Detayli rehber: DOC/API_KEY_REHBERI.md
    echo.
) else (
    echo .env dosyasi mevcut.
)

echo [5/5] Klasorler olusturuluyor...
if not exist storage mkdir storage
if not exist cache mkdir cache
if not exist fonts mkdir fonts

echo.
echo ========================================
echo Kurulum tamamlandi!
echo ========================================
echo.
echo Sonraki adimlar:
echo 1. .env dosyasini duzenleyin
echo 2. OpenAI API key ekleyin (DOC/API_KEY_REHBERI.md)
echo 3. Redis'i baslatin (docker run -d -p 6379:6379 redis)
echo 4. Celery worker'i baslatin (celery -A app.operations.translation_manager.celery_app worker --loglevel=info --pool=solo)
echo 5. FastAPI'yi baslatin (uvicorn main:app --reload)
echo.
pause

