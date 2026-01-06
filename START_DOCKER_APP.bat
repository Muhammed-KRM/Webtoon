@echo off
echo ===========================================
echo Webtoon AI Translator - Docker Baslatiliyor
echo ===========================================
echo.

echo Docker containerlari ayaga kaldiriliyor...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Docker baslatilamadi!
    echo 1. Docker Desktop uygulamasinin acik oldugundan emin olun.
    echo 2. Bilgisayari yeni kurduysaniz yeniden baslatin.
    pause
    exit /b 1
)

echo.
echo [BASARILI] Sistem calisiyor!
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Loglari gormek icin: docker-compose logs -f
echo.
pause
