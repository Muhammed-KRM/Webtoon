@echo off
echo ===========================================
echo Webtoon AI Translator - Git Upload Duzeltici
echo ===========================================
echo.

echo [1/5] Hatali commitler geri aliniyor (Dosyalariniz silinmez)...
:: Son 5 commiti geri al ama dosyalari koru (mixed reset)
git reset --mixed HEAD~5 2>nul
if %errorlevel% neq 0 (
    echo (Uyari: Geri alinacak o kadar commit yok, sorun degil devam ediliyor)
)

echo.
echo [2/5] Buyuk dosyalar engelleniyor...
echo. >> .gitignore
echo *.exe >> .gitignore
echo DockerInstaller.exe >> .gitignore

echo.
echo [3/5] Dosyalar tekrar ekleniyor (Buyuk dosyalar haric)...
git add .

echo.
echo [4/5] Temiz commit olusturuluyor...
git commit -m "Code base update (cleaned large files)"

echo.
echo [5/5] GitHub'a gonderiliyor...
echo Bu islem bu sefer hizli bitmeli...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo [BILGI] Normal push reddedildi, zorla gonderiliyor (Force Push)...
    git push origin main --force
)

echo.
echo ===========================================
echo Islem tamamlandi!
echo ===========================================
pause
