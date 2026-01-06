@echo off
echo ===========================================
echo Webtoon AI Translator - Basit Baslatma
echo ===========================================
echo.

echo [1/2] Redis baslat (Windows icin)...
echo Redis yoksa atlaniyor, SQLite kullanilacak.

echo.
echo [2/2] Web uygulamasi baslatiliyor...
call venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
