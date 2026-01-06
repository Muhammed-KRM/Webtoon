# 🚀 Webtoon AI Translator - Yeni Bilgisayar Kurulum Rehberi

## 📋 Gereksinimler

### Kurulması Gerekenler (Manuel):

1. **Python 3.10 veya üzeri**

   - İndir: https://www.python.org/downloads/
   - ⚠️ Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin!

2. **Git**

   - İndir: https://git-scm.com/download/win
   - Varsayılan ayarlarla kurabilirsiniz

3. **Docker Desktop**
   - İndir: https://www.docker.com/products/docker-desktop/
   - Kurulum sonrası bilgisayarı yeniden başlatmanız gerekecek

---

## 🔧 Kurulum Adımları

### Adım 1: Projeyi İndirin

**Seçenek A - GitHub'dan:**

```bash
git clone https://github.com/KULLANICI_ADI/Webtoon.git
cd Webtoon
```

**Seçenek B - ZIP Dosyasından:**

1. Proje ZIP dosyasını indirin
2. İstediğiniz klasöre çıkartın (örn: `D:\Webtoon\Webtoon`)
3. Terminal'i o klasörde açın

---

### Adım 2: Otomatik Kurulum

Proje klasöründe aşağıdaki komutu çalıştırın:

```bash
SETUP_COMPLETE.bat
```

Bu script:

- ✅ Virtual environment oluşturur
- ✅ Tüm Python paketlerini kurar
- ✅ Veritabanını oluşturur
- ✅ `.env` dosyasını yapılandırır
- ✅ Docker Redis container'ını başlatır

---

### Adım 3: Docker Desktop'ı Başlatın

1. Docker Desktop uygulamasını açın
2. Sol menüden **"Containers"** sekmesine tıklayın
3. `webtoon_redis` container'ının çalıştığını kontrol edin (yeşil nokta)

**Eğer container çalışmıyorsa:**

```bash
docker start webtoon_redis
```

---

### Adım 4: Sistemi Başlatın

```bash
START_ALL.bat
```

Bu komut:

- ✅ Redis'i kontrol eder
- ✅ Web Server'ı başlatır (Port 8000)
- ✅ Celery Worker'ı başlatır
- ✅ Tarayıcıda API dokümantasyonunu açar

---

## 🎯 Hızlı Başlangıç (Özet)

```bash
# 1. Projeyi indirin
git clone https://github.com/KULLANICI_ADI/Webtoon.git
cd Webtoon

# 2. Otomatik kurulum
SETUP_COMPLETE.bat

# 3. Docker Desktop'ı açın ve Redis'in çalıştığını kontrol edin

# 4. Sistemi başlatın
START_ALL.bat
```

---

## 📍 Erişim Adresleri

Kurulum tamamlandıktan sonra:

- **Ana Sayfa:** http://localhost:8000
- **API Dokümantasyonu:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🛑 Sistemi Durdurmak

```bash
STOP_ALL.bat
```

---

## 🐛 Sorun Giderme

### Python Bulunamadı Hatası

```bash
# Python'un kurulu olduğunu kontrol edin
python --version

# Eğer hata veriyorsa, Python'u PATH'e ekleyin:
# Sistem Özellikleri > Gelişmiş > Ortam Değişkenleri > Path
```

### Docker Bağlantı Hatası

```bash
# Docker Desktop'ın çalıştığını kontrol edin
docker ps

# Redis container'ını manuel başlatın
docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
```

### Port Zaten Kullanımda (8000)

```bash
# Portu kullanan işlemi bulun
netstat -ano | findstr :8000

# İşlemi sonlandırın (PID ile)
taskkill /PID <PID_NUMARASI> /F
```

### Veritabanı Hatası

```bash
# Veritabanını yeniden oluşturun
venv\Scripts\python init_db.py
```

---

## 📦 Manuel Kurulum (İleri Seviye)

Eğer otomatik kurulum çalışmazsa:

### 1. Virtual Environment Oluştur

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Paketleri Kur

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. .env Dosyası Oluştur

`.env` dosyasını kök dizine oluşturun:

```env
SECRET_KEY=your-secret-key-here-change-this-in-production
DATABASE_URL=sqlite:///./webtoon.db
OPENAI_API_KEY=your-openai-api-key-here
REDIS_URL=redis://localhost:6379/0
CDN_ENABLED=False
STRIPE_SECRET_KEY=your-stripe-key-here
LOG_LEVEL=INFO
```

### 4. Veritabanını Oluştur

```bash
python init_db.py
```

### 5. Redis'i Başlat

```bash
docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
```

### 6. Servisleri Başlat

```bash
# Terminal 1: Web Server
venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Celery Worker
venv\Scripts\celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

---

## 🔐 Güvenlik Notları

**Production ortamında mutlaka değiştirin:**

- `SECRET_KEY` - Güçlü bir anahtar oluşturun
- `OPENAI_API_KEY` - Gerçek API anahtarınızı girin
- `STRIPE_SECRET_KEY` - Gerçek Stripe anahtarınızı girin
- `DATABASE_URL` - Production için PostgreSQL kullanın

---

## 📞 Destek

Sorun yaşarsanız:

1. `STOP_ALL.bat` ile sistemi durdurun
2. `SETUP_COMPLETE.bat` ile yeniden kurun
3. Log dosyalarını kontrol edin (`logs/` klasörü)

---

## 📝 Notlar

- **İlk Kullanım:** Sistem ilk başlatıldığında veritabanı boş olacaktır
- **Test Kullanıcısı:** `/api/v1/auth/register` endpoint'i ile kayıt olun
- **Geliştirme Modu:** `--reload` parametresi kod değişikliklerini otomatik algılar
- **Production:** `--reload` parametresini kaldırın ve Gunicorn kullanın

---

## 🎓 Ek Kaynaklar

- **API Dokümantasyonu:** http://localhost:8000/docs
- **Proje Dokümantasyonu:** `DOC/COMPLETE_DOCUMENTATION.md`
- **Hızlı Başlangıç:** `HIZLI_BASLANGIC.md`
