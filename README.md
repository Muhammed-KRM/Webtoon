# 🚀 Webtoon AI Translator

Profesyonel webtoon makine çeviri uygulaması. Görüntü işleme (Computer Vision), doğal dil işleme (NLP) ve asenkron iş akışları ile desteklenen kurumsal seviye bir çeviri platformu.

## ⚡ Hızlı Başlangıç

### 1. İlk Kurulum (Sadece bir kez)

```bash
# Otomatik kurulum
SETUP.bat
```

Bu script:
- ✅ Sanal ortam oluşturur
- ✅ Paketleri yükler
- ✅ `.env` dosyası oluşturur
- ✅ Klasörleri hazırlar

### 2. Environment Variables Ayarla

`.env` dosyasını düzenleyin:
- `SECRET_KEY`: En az 32 karakter rastgele string
- `OPENAI_API_KEY`: API key'inizi ekleyin
- `DATABASE_URL`: SQLite veya PostgreSQL

**Detaylar:** `ENV_OLUSTUR.md` ve `DOC/API_KEY_REHBERI.md`

### 3. Projeyi Başlat

```bash
# Tek komutla her şeyi başlat
START.bat
```

Bu script:
- ✅ Redis'i başlatır (Docker ile)
- ✅ Celery Worker'ı başlatır (ayrı pencere)
- ✅ FastAPI'yi başlatır

### 4. Durdurma

```bash
# Tüm servisleri durdur
STOP.bat
```

## 📁 Dosya Yapısı

```
Webtoon/
├── START.bat          # Projeyi başlat (TEK KOMUT!)
├── STOP.bat           # Tüm servisleri durdur
├── RESTART.bat        # Yeniden başlat
├── CHECK.bat          # Durum kontrolü
├── SETUP.bat          # İlk kurulum
├── main.py            # FastAPI uygulama
├── app/               # Uygulama kodu
│   ├── api/           # API endpoints
│   ├── core/          # Config, security
│   ├── services/      # Business logic
│   ├── operations/    # Celery tasks
│   └── models/        # Database models
└── DOC/               # Dokümantasyon
```

## 🎯 Kullanım

### API Dokümantasyonu

Proje başladıktan sonra:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### İş Akışı

1. **Register/Login:** `POST /api/v1/auth/register` veya `/login`
2. **Çeviri Başlat:** `POST /api/v1/translate/start`
3. **Durum Kontrol:** `GET /api/v1/translate/status/{task_id}`
4. **Sonuç Al:** `GET /api/v1/translate/result/{task_id}`

## 🔧 Yönetim Komutları

| Komut | Açıklama |
|-------|----------|
| `SETUP.bat` | İlk kurulum (sadece bir kez) |
| `START.bat` | Tüm servisleri başlat |
| `STOP.bat` | Tüm servisleri durdur |
| `RESTART.bat` | Yeniden başlat |
| `CHECK.bat` | Durum kontrolü |

## ✨ Özellikler

- ✅ **Otomatik Web Scraping** - Webtoon sayfalarından görselleri indirme
- ✅ **Akıllı OCR** - EasyOCR ile metin tespiti
- ✅ **Context-Aware Çeviri** - OpenAI GPT-4o-mini ile tutarlı çeviri
- ✅ **Cached Input** - %50 maliyet tasarrufu
- ✅ **Görüntü İşleme** - In-painting + Türkçe metin yerleştirme
- ✅ **Akıllı Metin Sığdırma** - Otomatik font boyutu ayarlama
- ✅ **Cache Sistemi** - Aynı bölümü tekrar çevirmeme
- ✅ **Asenkron İşlem** - Celery + Redis

## 📚 Dokümantasyon

- **Kurulum:** `KURULUM.md`
- **Hızlı Başlangıç:** `DOC/HIZLI_BASLANGIC.md`
- **API Key Rehberi:** `DOC/API_KEY_REHBERI.md`
- **Environment Variables:** `ENV_OLUSTUR.md`
- **Maliyet Analizi:** `DOC/MaliyetAnalizi.md`
- **Geliştirme Planı:** `DOC/GelistirmePlani.md`

## 🛠️ Teknoloji Yığını

- **Backend:** FastAPI
- **Database:** PostgreSQL / SQLite
- **Task Queue:** Celery + Redis
- **OCR:** EasyOCR
- **Translation:** OpenAI GPT-4o-mini
- **Image Processing:** OpenCV + Pillow

## ⚠️ Önemli Notlar

1. **Scraper Service:** `app/services/scraper_service.py` dosyasında hedef webtoon sitesine özel scraping mantığını implemente etmeniz gerekiyor.

2. **Font Dosyaları:** `fonts/` klasörüne Türkçe karakter desteği olan font dosyaları ekleyin (opsiyonel).

3. **API Key:** OpenAI API key'inizi `.env` dosyasına ekleyin ve kredi yükleyin.

## 🐛 Sorun Giderme

### Servisler başlamıyor
```bash
CHECK.bat
```
Bu komut tüm servislerin durumunu kontrol eder.

### Redis hatası
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### Celery hatası (Windows)
`--pool=solo` parametresi zorunludur (START.bat'da zaten var).

## 📝 Lisans

Bu proje eğitim amaçlıdır.

---

**Sorularınız için:** `DOC/` klasöründeki dokümanlara bakın.
