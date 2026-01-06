@echo off
echo ========================================
echo Webtoon AI Translator - Setup Script (AUTO)
echo ========================================
echo.

echo [1/8] Sanal ortam oluşturuluyor...
python -m venv venv
if errorlevel 1 (
    echo HATA: Python bulunamadı!
    exit /b 1
)

echo [2/8] Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat

echo [3/8] Temel paketler yükleniyor...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo HATA: Paket yükleme başarısız!
    exit /b 1
)

echo [4/8] Opsiyonel paketler yükleniyor...
pip install transformers==4.36.2 torch==2.1.2 argostranslate==1.9.0 spacy==3.7.2 --quiet

echo [5/8] spaCy İngilizce modeli indiriliyor...
python -m spacy download en_core_web_sm --quiet

echo [6/8] Argos Translate paketleri hazırlanıyor...
python -c "import argostranslate.package; argostranslate.package.update_package_index(); print('Argos Translate hazir')" 2>nul

echo [7/8] .env dosyası kontrol ediliyor...
if not exist .env (
    echo .env dosyası bulunamadı, .env.example'dan kopyalanıyor...
    copy .env.example .env
) else (
    echo .env dosyasi mevcut.
)

echo [8/8] Klasorler olusturuluyor...
if not exist storage mkdir storage
if not exist cache mkdir cache
if not exist fonts mkdir fonts

echo ========================================
echo Kurulum tamamlandi!
echo ========================================
