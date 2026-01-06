@echo off
echo ========================================
echo Webtoon AI Translator - Durum Kontrolu
echo ========================================
echo.

echo [1/4] Sanal ortam kontrolu...
if exist "venv\Scripts\activate.bat" (
    echo [OK] Sanal ortam mevcut
) else (
    echo [HATA] Sanal ortam bulunamadi! SETUP.bat calistirin.
)

echo.
echo [2/4] .env dosyasi kontrolu...
if exist ".env" (
    echo [OK] .env dosyasi mevcut
    
    REM OpenAI API key kontrolu
    findstr /C:"OPENAI_API_KEY=" .env | findstr /C:"sk-proj-" >nul 2>&1
    if errorlevel 1 (
        echo [UYARI] OPENAI_API_KEY gecerli gorunmuyor!
    ) else (
        echo [OK] OPENAI_API_KEY ayarlanmis
    )
) else (
    echo [HATA] .env dosyasi bulunamadi! ENV_OLUSTUR.md'ye bakin.
)

echo.
echo [3/4] Redis kontrolu...
docker ps | findstr redis >nul 2>&1
if errorlevel 1 (
    echo [HATA] Redis calisiyor gorunmuyor!
    echo Redis'i baslatmak icin: docker run -d -p 6379:6379 --name redis redis
) else (
    echo [OK] Redis calisiyor
)

echo.
echo [4/4] Process kontrolu...
tasklist | findstr /I "celery.exe" >nul 2>&1
if errorlevel 1 (
    echo [HATA] Celery Worker calisiyor gorunmuyor!
) else (
    echo [OK] Celery Worker calisiyor
)

tasklist | findstr /I "python.exe" | findstr /I "uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [HATA] FastAPI calisiyor gorunmuyor!
) else (
    echo [OK] FastAPI calisiyor
)

echo.
echo ========================================
echo Kontrol tamamlandi!
echo ========================================
echo.
echo API Test: http://localhost:8000/health
echo API Docs: http://localhost:8000/docs
echo.
pause

