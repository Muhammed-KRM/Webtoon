@echo off
echo ========================================
echo GitHub'a Yükleme Script
echo ========================================
echo.

echo [1/5] Git durumu kontrol ediliyor...
if not exist .git (
    echo Git repo bulunamadi, olusturuluyor...
    git init
    git config user.name "Muhammed-KRM"
    git config user.email "ustunmuhammed09@gmail.com"
    echo Git repo olusturuldu.
) else (
    echo Git repo mevcut.
)
echo.

echo [2/5] Dosyalar ekleniyor...
git add .
echo Dosyalar eklendi.
echo.

echo [3/5] Commit olusturuluyor...
git commit -m "Initial commit: Webtoon AI Translator - Complete backend with all features"
echo Commit olusturuldu.
echo.

echo [4/5] Remote yapilandiriliyor...
git remote remove origin 2>nul
git remote add origin https://github.com/Muhammed-KRM/webtoon-ai-translator.git
git branch -M main
echo Remote yapilandirildi.
echo.

echo [5/5] GitHub'a push ediliyor...
echo.
echo NOT: Eger repo henuz olusturulmadiysa, once GitHub'da olustur:
echo 1. https://github.com/Muhammed-KRM adresine git
echo 2. "New repository" butonuna tikla
echo 3. Name: webtoon-ai-translator
echo 4. Public sec ve olustur
echo.
echo Push ediliyor...
git push -u origin main
echo.
echo ========================================
echo Tamamlandi!
echo Repository: https://github.com/Muhammed-KRM/webtoon-ai-translator
echo ========================================
pause

