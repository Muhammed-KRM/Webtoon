@echo off
echo ===========================================
echo Webtoon AI Translator - Guvenli GitHub Push
echo ===========================================
echo.

echo [1/4] Git ayarlari optimize ediliyor (Timeout onlemi)...
:: Buffer boyutunu 500MB'a cikart
git config http.postBuffer 524288000
:: Hiz limitini kaldir
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999
:: HTTP surumunu 1.1'e zorla (bazi proxy sorunlarini cozer)
git config http.version HTTP/1.1

echo.
echo [2/4] Desigiklikler ekleniyor...
git add .

echo.
echo [3/4] Commit olusturuluyor...
set /p commit_msg="Commit mesaji girin (Enter'a basarsaniz 'Auto update' olur): "
if "%commit_msg%"=="" set commit_msg=Auto update with fixes
git commit -m "%commit_msg%"

echo.
echo [4/4] GitHub'a gonderiliyor (Push)...
echo Lutfen bekleyin, bu islem internet hiziniza gore surebilir...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Push islemi basarisiz oldu!
    echo Olasiliklar:
    echo 1. Internet baglantinizda kopma oldu.
    echo 2. Dosyalar cok buyuk.
    echo 3. GitHub sunuculari yogun.
    echo.
    echo "git push" komutunu tekrar deneyin.
) else (
    echo.
    echo [BASARILI] Kodlar GitHub'a gonderildi.
)
echo.
pause
