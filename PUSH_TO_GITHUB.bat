@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 GitHub'a Push İşlemi
echo ========================================
echo.

echo [1/4] Remote kontrol ediliyor...
git remote remove origin 2>nul
git remote add origin https://github.com/Muhammed-KRM/webtoon-ai-translator.git
git remote -v
echo ✓ Remote yapılandırıldı
echo.

echo [2/4] Branch kontrol ediliyor...
git branch -M main
echo ✓ Branch main olarak ayarlandı
echo.

echo [3/4] Commit kontrol ediliyor...
git log --oneline -1
echo.

echo [4/4] GitHub'a push ediliyor...
echo.
echo ⚠️  Authentication gerekebilir!
echo Username: Muhammed-KRM
echo Password: GitHub Personal Access Token kullan (şifre değil!)
echo.
git push -u origin main
echo.

if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo ✅ BAŞARILI! Proje GitHub'a yüklendi!
    echo ========================================
    echo.
    echo Repository: https://github.com/Muhammed-KRM/webtoon-ai-translator
    echo.
) else (
    echo ========================================
    echo ❌ Push başarısız oldu
    echo ========================================
    echo.
    echo Olası nedenler:
    echo 1. Authentication hatası - Personal Access Token kullan
    echo 2. Repo henüz oluşturulmamış
    echo 3. Network sorunu
    echo.
    echo Personal Access Token oluştur:
    echo 1. GitHub → Settings → Developer settings
    echo 2. Personal access tokens → Tokens (classic)
    echo 3. Generate new token (classic)
    echo 4. Scopes: repo seç
    echo 5. Generate ve token'ı kopyala
    echo 6. Push sırasında şifre yerine token kullan
    echo.
)

pause

