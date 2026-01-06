# Webtoon AI Translator - Hızlı Başlangıç Rehberi

## 🚀 Sistemi Başlatma

### Tek Komutla Başlatma (Önerilen)

```bash
START_ALL.bat
```

Bu komut:

- ✅ Redis'i kontrol eder ve gerekirse başlatır
- ✅ Veritabanını kontrol eder ve gerekirse oluşturur
- ✅ Web Server'ı başlatır (Port 8000)
- ✅ Celery Worker'ı başlatır
- ✅ Tarayıcıda API dokümantasyonunu açar

### Manuel Başlatma (İleri Seviye)

**1. Redis'i Başlat:**

```bash
docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
```

**2. Web Server'ı Başlat:**

```bash
venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**3. Celery Worker'ı Başlat:**

```bash
venv\Scripts\celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

---

## 🛑 Sistemi Durdurma

```bash
STOP_ALL.bat
```

---

## 📍 Erişim Adresleri

- **Ana Sayfa:** http://localhost:8000
- **API Dokümantasyonu:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🔧 Sistem Gereksinimleri

- ✅ Python 3.10+
- ✅ Docker Desktop
- ✅ Redis (Docker üzerinden)
- ✅ Virtual Environment (venv)

---

## 📊 Servis Durumu Kontrolü

### Redis Kontrolü:

```bash
docker ps | findstr webtoon_redis
```

### Web Server Kontrolü:

```bash
curl http://localhost:8000/health
```

---

## 🐛 Sorun Giderme

### Redis Bağlantı Hatası

```bash
docker start webtoon_redis
```

### Port Zaten Kullanımda

```bash
# 8000 portunu kullanan işlemi bul
netstat -ano | findstr :8000

# İşlemi sonlandır (PID ile)
taskkill /PID <PID_NUMARASI> /F
```

### Veritabanı Hatası

```bash
venv\Scripts\python init_db.py
```

---

## 📝 Notlar

- **Geliştirme Modu:** `--reload` parametresi kod değişikliklerini otomatik algılar
- **Production Modu:** `--reload` parametresini kaldırın
- **Log Seviyesi:** Celery için `--loglevel=debug` kullanabilirsiniz

---

## 🎯 İlk Kullanım

1. `START_ALL.bat` dosyasını çalıştırın
2. Tarayıcıda http://localhost:8000/docs adresine gidin
3. `/api/v1/auth/register` endpoint'ini kullanarak kayıt olun
4. `/api/v1/translate/start` ile çeviri başlatın

---

## 📞 Destek

Sorun yaşarsanız:

1. `STOP_ALL.bat` ile sistemi durdurun
2. `START_ALL.bat` ile yeniden başlatın
3. Log dosyalarını kontrol edin
