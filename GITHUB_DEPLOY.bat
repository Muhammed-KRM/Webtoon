@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 GitHub'a Yükleme Script
echo ========================================
echo.

REM Git init
echo [1/6] Git repo kontrol ediliyor...
if not exist .git (
    echo Git repo bulunamadı, oluşturuluyor...
    call git init
    call git config user.name "Muhammed-KRM"
    call git config user.email "ustunmuhammed09@gmail.com"
    echo ✓ Git repo oluşturuldu
) else (
    echo ✓ Git repo mevcut
)
echo.

REM Git config
echo [2/6] Git yapılandırması...
call git config user.name "Muhammed-KRM"
call git config user.email "ustunmuhammed09@gmail.com"
echo ✓ Git yapılandırması tamamlandı
echo.

REM Add files
echo [3/6] Dosyalar ekleniyor...
call git add .
echo ✓ Dosyalar eklendi
echo.

REM Commit
echo [4/6] Commit oluşturuluyor...
call git commit -m "Initial commit: Webtoon AI Translator - Complete backend with all features"
echo ✓ Commit oluşturuldu
echo.

REM Remote
echo [5/6] Remote yapılandırılıyor...
call git remote remove origin 2>nul
call git remote add origin https://github.com/Muhammed-KRM/webtoon-ai-translator.git
call git branch -M main
echo ✓ Remote yapılandırıldı
echo.

REM GitHub repo oluşturma uyarısı
echo ⚠️  ÖNEMLİ: GitHub'da repo oluşturman gerekiyor!
echo.
echo 1. https://github.com/Muhammed-KRM adresine git
echo 2. "New repository" butonuna tıkla
echo 3. Repository name: webtoon-ai-translator
echo 4. Description: Webtoon AI Translator - Professional machine translation platform
echo 5. Public seç
echo 6. "Create repository" butonuna tıkla
echo.
set /p continue="Repo oluşturuldu mu? (E/H): "
if /i not "%continue%"=="E" (
    echo İşlem iptal edildi. Repo oluşturduktan sonra tekrar çalıştır.
    pause
    exit /b
)
echo.

REM Push
echo [6/6] GitHub'a push ediliyor...
echo.
echo Kullanıcı adı: Muhammed-KRM
echo Şifre: GitHub Personal Access Token kullan (şifre değil!)
echo.
echo Personal Access Token oluşturmak için:
echo 1. GitHub → Settings → Developer settings → Personal access tokens
echo 2. "Generate new token (classic)"
echo 3. Note: webtoon-ai-translator
echo 4. Scopes: repo seç
echo 5. Generate ve token'ı kopyala
echo.
call git push -u origin main
echo.
echo ========================================
echo ✅ Tamamlandı!
echo Repository: https://github.com/Muhammed-KRM/webtoon-ai-translator
echo ========================================
pause

