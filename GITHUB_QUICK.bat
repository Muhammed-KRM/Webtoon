@echo off
REM Hızlı GitHub push script
REM Önce GitHub'da repo oluştur: https://github.com/Muhammed-KRM/webtoon-ai-translator

git init
git config user.name "Muhammed-KRM"
git config user.email "ustunmuhammed09@gmail.com"
git add .
git commit -m "Initial commit: Webtoon AI Translator - Complete backend with all features"
git remote add origin https://github.com/Muhammed-KRM/webtoon-ai-translator.git 2>nul
git remote set-url origin https://github.com/Muhammed-KRM/webtoon-ai-translator.git
git branch -M main
git push -u origin main

pause

