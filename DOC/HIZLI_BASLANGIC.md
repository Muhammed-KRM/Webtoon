# ⚡ Hızlı Başlangıç Rehberi

5 dakikada projeyi çalıştırın!

## 🚀 Hızlı Kurulum (Windows)

### 1. Otomatik Kurulum

```bash
# Proje klasöründe
SETUP.bat
```

Bu script:
- ✅ Sanal ortam oluşturur
- ✅ Paketleri yükler
- ✅ `.env` dosyası oluşturur
- ✅ Klasörleri hazırlar

### 2. .env Dosyasını Düzenle

`.env` dosyasını açın ve şunları doldurun:

```env
# SECRET_KEY: En az 32 karakter (rastgele string)
SECRET_KEY="my-super-secret-key-12345678901234567890"

# DATABASE_URL: SQLite kullan (kolay başlangıç)
DATABASE_URL="sqlite:///./webtoon.db"

# OPENAI_API_KEY: API key'inizi buraya koyun
OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**API Key nasıl alınır?** → `DOC/API_KEY_REHBERI.md`

### 3. Redis Başlat (Docker ile)

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### 4. Uygulamayı Başlat

**2 terminal penceresi açın:**

#### Terminal 1: Celery Worker
```bash
venv\Scripts\activate
celery -A app.operations.translation_manager.celery_app worker --loglevel=info --pool=solo
```

#### Terminal 2: FastAPI
```bash
venv\Scripts\activate
uvicorn main:app --reload
```

### 5. Test Et

Tarayıcıda açın:
- http://localhost:8000/docs

## ✅ Başarılı!

Artık API çalışıyor. API docs'tan test edebilirsiniz.

## 📝 Sonraki Adımlar

1. **Scraper Service'i implemente edin** (`app/services/scraper_service.py`)
2. **Font dosyaları ekleyin** (`fonts/` klasörüne)
3. **Test çevirisi yapın**

---

**Detaylı kurulum:** `KURULUM.md`  
**API Key rehberi:** `DOC/API_KEY_REHBERI.md`

