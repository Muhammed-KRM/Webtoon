@echo off
echo ===========================================
echo Webtoon AI Translator - Arac Kurulumu
echo ===========================================
echo.
echo Bu islem asagidakileri indirecek ve kuracaktir:
echo 1. Docker Desktop (Redis ve App icin gerekli)
echo 2. Redis Insight (Veritabani yonetimi icin - Opsiyonel)
echo.
echo Lutfen acilan pencerelere "Evet" veya "Install" deyin.
echo.
pause

echo.
echo [1/2] Docker Desktop indiriliyor ve kuruluyor...
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 (
    echo [HATA] Docker kurulumunda hata olustu. Yonetici olarak calistirmayi deneyin.
) else (
    echo [BASARILI] Docker kuruldu. Bilgisayari yeniden baslatmaniz gerekebilir.
)

echo.
echo [2/2] Redis Insight indiriliyor...
winget install -e --id Redis.RedisInsight --accept-package-agreements --accept-source-agreements

echo.
echo ===========================================
echo Islem tamamlandi.
echo Docker'in calismasi icin LOGOUT yapip giris yapmaniz 
echo veya BILGISAYARI YENIDEN BASLATMANIZ gerekebilir.
echo ===========================================
pause
