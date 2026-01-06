@echo off
echo ========================================
echo Webtoon AI Translator - Setup Script
echo ========================================
echo.

echo [1/8] Sanal ortam oluşturuluyor...
python -m venv venv
if errorlevel 1 (
    echo HATA: Python bulunamadı! Python 3.10+ yüklü olduğundan emin olun.
    pause
    exit /b 1
)

echo [2/8] Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat

echo [3/8] Temel paketler yükleniyor...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo HATA: Paket yükleme başarısız!
    pause
    exit /b 1
)

echo [4/8] Opsiyonel paketler yükleniyor (Hugging Face, Argos, spaCy)...
pip install transformers==4.36.2 torch==2.1.2 argostranslate==1.9.0 spacy==3.7.2 --quiet
if errorlevel 1 (
    echo UYARI: Bazı opsiyonel paketler yüklenemedi (sistem yine de çalışır)
) else (
    echo Opsiyonel paketler yüklendi.
)

echo [5/8] spaCy İngilizce modeli indiriliyor...
python -m spacy download en_core_web_sm --quiet
if errorlevel 1 (
    echo UYARI: spaCy modeli indirilemedi (regex fallback kullanılacak)
) else (
    echo spaCy modeli indirildi.
)

echo [6/8] Argos Translate paketleri hazırlanıyor...
python -c "import argostranslate.package; argostranslate.package.update_package_index(); print('Argos Translate hazir')" 2>nul
if errorlevel 1 (
    echo INFO: Argos Translate ilk kullanımda paketleri indirecek
) else (
    echo Argos Translate hazir.
)

echo [7/8] .env dosyası kontrol ediliyor...
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

echo [8/8] Klasorler olusturuluyor...
if not exist storage mkdir storage
if not exist cache mkdir cache
if not exist fonts mkdir fonts

echo.
echo ========================================
echo Kurulum tamamlandi!
echo ========================================
echo.
echo Kurulu paketler:
echo - Temel paketler (FastAPI, Celery, Redis, vb.)
echo - Opsiyonel: Hugging Face Transformers (offline AI çeviri)
echo - Opsiyonel: Argos Translate (offline ücretsiz çeviri)
echo - Opsiyonel: spaCy (gelişmiş özel isim tespiti)
echo.
echo Sistem otomatik olarak en iyi çeviri servisini seçecek:
echo 1. Hugging Face (varsa) - En kaliteli, offline
echo 2. Argos Translate (varsa) - Hızlı, offline
echo 3. Google Translate (her zaman) - Online, ücretsiz
echo.
echo Sonraki adimlar:
echo 1. .env dosyasini duzenleyin
echo 2. OpenAI API key ekleyin (DOC/API_KEY_REHBERI.md)
echo 3. START.bat ile projeyi baslatin
echo.
pause

