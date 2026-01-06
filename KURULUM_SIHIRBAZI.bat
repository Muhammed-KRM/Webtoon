@echo off
title Webtoon AI Translator - Quick Start Guide
color 0E

cls
echo.
echo ============================================
echo   WEBTOON AI TRANSLATOR
echo   HIZLI KURULUM REHBERI
echo ============================================
echo.
echo Bu rehber size kurulum adimlarini gosterecektir.
echo.
echo ============================================
echo   ADIM 1: GEREKLI PROGRAMLAR
echo ============================================
echo.
echo Asagidaki programlarin kurulu olmasi gerekiyor:
echo.
echo [1] Python 3.10+
echo     https://www.python.org/downloads/
echo     ! "Add Python to PATH" secenegini isaretleyin!
echo.
echo [2] Git
echo     https://git-scm.com/download/win
echo.
echo [3] Docker Desktop
echo     https://www.docker.com/products/docker-desktop/
echo     ! Kurulum sonrasi bilgisayari yeniden baslatin!
echo.
echo ============================================
echo.
echo Tum programlari kurdunuz mu?
pause

cls
echo.
echo ============================================
echo   ADIM 2: PROJEYI INDIRIN
echo ============================================
echo.
echo Seceneklerden birini secin:
echo.
echo [A] GitHub'dan indirin:
echo     git clone https://github.com/KULLANICI_ADI/Webtoon.git
echo     cd Webtoon
echo.
echo [B] ZIP dosyasindan:
echo     1. ZIP dosyasini indirin
echo     2. D:\Webtoon klasorune cikart in
echo     3. Terminal'i D:\Webtoon\Webtoon klasorunde acin
echo.
echo ============================================
echo.
echo Projeyi indirdiniz mi?
pause

cls
echo.
echo ============================================
echo   ADIM 3: OTOMATIK KURULUM
echo ============================================
echo.
echo Simdi otomatik kurulum scriptini calistiracagiz.
echo Bu script:
echo.
echo - Virtual environment olusturur
echo - Python paketlerini kurar
echo - Veritabanini olusturur
echo - .env dosyasini yapilandirir
echo - Redis container'ini baslatir
echo.
echo Beklenen sure: 3-5 dakika
echo.
echo ============================================
echo.
echo Hazir misiniz?
pause

echo.
echo [INFO] SETUP_COMPLETE.bat calistiriliyor...
echo.
call SETUP_COMPLETE.bat

cls
echo.
echo ============================================
echo   ADIM 4: DOCKER DESKTOP
echo ============================================
echo.
echo 1. Docker Desktop uygulamasini acin
echo.
echo 2. Sol alt kosede "Engine running" yazisini bekleyin
echo.
echo 3. Sol menueden "Containers" sekmesine tiklayin
echo.
echo 4. "webtoon_redis" container'ini bulun
echo.
echo 5. Yaninda yesil nokta olmali (calisiyor)
echo.
echo 6. Eger kirmizi nokta varsa, "Start" butonuna basin
echo.
echo ============================================
echo.
echo Docker Desktop hazir mi?
pause

cls
echo.
echo ============================================
echo   ADIM 5: SISTEMI BASLATIN
echo ============================================
echo.
echo Simdi sistemi baslat acagiz.
echo.
echo 3 terminal penceresi acilacak:
echo - Web Server (Port 8000)
echo - Celery Worker
echo - Sistem Monitoru
echo.
echo ! Bu pencereleri KAPATMAYIN!
echo.
echo ============================================
echo.
echo Hazir misiniz?
pause

echo.
echo [INFO] START_ALL.bat calistiriliyor...
echo.
call START_ALL.bat

cls
echo.
echo ============================================
echo   KURULUM TAMAMLANDI!
echo ============================================
echo.
echo Sistem basariyla baslatildi!
echo.
echo ERISIM ADRESLERI:
echo.
echo - API Dokumantasyonu: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/health
echo - Ana Sayfa: http://localhost:8000
echo.
echo ============================================
echo   GUNLUK KULLANIM
echo ============================================
echo.
echo Sistemi Baslatmak:
echo   START_ALL.bat
echo.
echo Sistemi Durdurmak:
echo   STOP_ALL.bat
echo.
echo ============================================
echo   YARDIM DOKUMANLARI
echo ============================================
echo.
echo - KURULUM_DOKUMANI.md
echo - ADIM_ADIM_KURULUM.md
echo - HIZLI_BASLANGIC.md
echo - DOC/COMPLETE_DOCUMENTATION.md
echo.
echo ============================================
echo.
echo Iyi calismalar!
echo.
pause
