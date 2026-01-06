@echo off
echo ===========================================
echo Webtoon AI Translator - Celery Worker
echo ===========================================
echo.

echo [INFO] Celery Worker baslatiliyor...
echo Bu pencereyi ACIK BIRAKIN!
echo.

venv\Scripts\celery -A app.core.celery_app worker --loglevel=info --pool=solo

pause
