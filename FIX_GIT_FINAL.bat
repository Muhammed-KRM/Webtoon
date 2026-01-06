@echo off
echo ===========================================
echo Webtoon AI Translator - Final Git Onarimi
echo ===========================================
echo.

echo [1/4] Sorunlu dosya kontrol ediliyor...
if exist "DockerInstaller.exe" (
    echo [BILGI] DockerInstaller.exe tespit edildi, Downloads klasorune tasiniyor...
    move DockerInstaller.exe "%USERPROFILE%\Downloads\" >nul 2>&1
)

echo.
echo [2/4] Git gecmisi temizleniyor...
:: Son yapilan hatali commit'leri temizle
git reset --mixed HEAD~3 >nul 2>&1

echo.
echo [3/4] Temiz kodlar paketleniyor...
git add .
git commit -m "Clean update (installer removed)"

echo.
echo [4/4] GitHub'a gonderiliyor...
git push origin main --force

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Bir sorun olustu.
    pause
    exit /b 1
)

echo.
echo ===========================================
echo [BASARILI] Sorun tamamen cozuldu!
echo DockerInstaller.exe dosyasini "Indirilenler" klasorunde bulabilirsiniz.
echo ===========================================
pause
