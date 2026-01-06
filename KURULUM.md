# 🚀 Webtoon AI Translator - Kurulum Rehberi

Bu rehber, projeyi sıfırdan kurmanız için adım adım talimatlar içerir.

## 📋 Ön Gereksinimler

- **Python 3.10+** ([İndir](https://www.python.org/downloads/))
- **PostgreSQL** (veya SQLite - development için)
- **Redis** ([İndir](https://redis.io/download) veya Docker kullanın)

## 🔧 Adım Adım Kurulum

### 1. Projeyi İndirin ve Klasöre Gidin

```bash
cd C:\Webtoon
```

### 2. Sanal Ortam Oluşturun

```bash
# Windows
python -m venv venv

# Aktif edin
venv\Scripts\activate
```

### 3. Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

**Not:** EasyOCR ilk çalıştırmada model dosyalarını indirecektir (birkaç dakika sürebilir).

### 4. Environment Variables Ayarlayın

```bash
# .env.example dosyasını kopyalayın
copy .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

**`.env` dosyasını açın ve şunları doldurun:**

```env
# SECRET_KEY: En az 32 karakter, rastgele bir string
SECRET_KEY="your-super-secret-key-minimum-32-characters-long"

# DATABASE_URL: PostgreSQL veya SQLite
# PostgreSQL için:
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/webtoon_db"

# SQLite için (kolay başlangıç):
# DATABASE_URL="sqlite:///./webtoon.db"

# OPENAI_API_KEY: API key'inizi buraya koyun
# Nasıl alacağınız: DOC/API_KEY_REHBERI.md dosyasına bakın
OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 5. OpenAI API Key Alın

**Detaylı rehber:** `DOC/API_KEY_REHBERI.md` dosyasına bakın.

**Kısa özet:**
1. https://platform.openai.com/ adresine gidin
2. Hesap oluşturun / Giriş yapın
3. API keys sayfasından yeni key oluşturun
4. Key'i kopyalayıp `.env` dosyasına yapıştırın
5. Billing sayfasından kredi yükleyin (minimum $5)

### 6. Database Kurulumu

#### Seçenek A: SQLite (Kolay - Development için)

`.env` dosyasında:
```env
DATABASE_URL="sqlite:///./webtoon.db"
```

Bu kadar! Başka bir şey yapmanıza gerek yok.

#### Seçenek B: PostgreSQL (Production için)

1. **PostgreSQL'i kurun ve başlatın**

2. **Database oluşturun:**
```sql
CREATE DATABASE webtoon_db;
```

3. **`.env` dosyasında:**
```env
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/webtoon_db"
```

### 7. Redis Kurulumu

#### Windows (Docker ile - Önerilen):

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

#### Windows (Memurai - Alternatif):

1. https://www.memurai.com/ adresinden indirin
2. Kurun ve başlatın

#### Linux/Mac:

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
redis-server

# Mac
brew install redis
redis-server
```

### 8. Font Dosyaları (Opsiyonel)

Türkçe karakter desteği için font dosyaları ekleyin:

1. `fonts/` klasörüne gidin
2. Şu fontlardan birini indirin ve koyun:
   - KomikaAxis.ttf
   - Lalezar-Regular.ttf
   - Roboto-Regular.ttf

**Not:** Font olmadan da çalışır, ama sistem fontu kullanılır (Türkçe karakterlerde sorun olabilir).

### 9. Uygulamayı Başlatın

**3 terminal penceresi açın:**

#### Terminal 1: Redis (Eğer Docker kullanmıyorsanız)

```bash
redis-server
```

#### Terminal 2: Celery Worker

```bash
# Windows
celery -A app.operations.translation_manager.celery_app worker --loglevel=info --pool=solo

# Linux/Mac
celery -A app.operations.translation_manager.celery_app worker --loglevel=info
```

#### Terminal 3: FastAPI

```bash
uvicorn main:app --reload
```

### 10. Test Edin

Tarayıcıda açın:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## ✅ Kurulum Kontrol Listesi

- [ ] Python 3.10+ yüklü
- [ ] Sanal ortam oluşturuldu ve aktif
- [ ] `pip install -r requirements.txt` çalıştırıldı
- [ ] `.env` dosyası oluşturuldu ve dolduruldu
- [ ] OpenAI API key eklendi ve kredi yüklendi
- [ ] Database kuruldu (SQLite veya PostgreSQL)
- [ ] Redis çalışıyor
- [ ] Celery worker çalışıyor
- [ ] FastAPI çalışıyor
- [ ] http://localhost:8000/docs açılıyor

## 🐛 Sorun Giderme

### "Module not found" Hatası
```bash
# Sanal ortamın aktif olduğundan emin olun
# Windows: venv\Scripts\activate
# Sonra: pip install -r requirements.txt
```

### "Database connection error"
- PostgreSQL çalışıyor mu kontrol edin
- `.env` dosyasındaki `DATABASE_URL` doğru mu?

### "Redis connection error"
- Redis çalışıyor mu? `redis-cli ping` komutu ile test edin
- Docker kullanıyorsanız: `docker ps` ile container'ın çalıştığını kontrol edin

### "OpenAI API error"
- API key doğru mu? `.env` dosyasını kontrol edin
- Kredi yüklü mü? https://platform.openai.com/account/billing

### "Celery worker başlamıyor (Windows)"
- `--pool=solo` parametresini eklediniz mi?
- Windows'ta Celery için bu parametre zorunludur

## 📚 Sonraki Adımlar

1. **Scraper Service'i implemente edin:**
   - `app/services/scraper_service.py` dosyasını açın
   - Hedef webtoon sitesinin HTML yapısını analiz edin
   - Resim URL'lerini çıkaran kodu yazın

2. **Test edin:**
   - API docs'tan bir çeviri işlemi başlatın
   - Sonuçları kontrol edin

3. **Frontend geliştirin:**
   - Angular/React ile frontend oluşturun
   - API'ye bağlanın

## 💡 İpuçları

- **Development için SQLite kullanın** (daha kolay)
- **Production için PostgreSQL kullanın** (daha güvenli)
- **Font dosyaları ekleyin** (daha iyi görünüm)
- **API key'i güvenli tutun** (`.gitignore`'da `.env` var)

---

**Sorularınız için:** `DOC/` klasöründeki dokümanlara bakın.

