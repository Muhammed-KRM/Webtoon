# 🎨 Webtoon AI Translator

> Profesyonel Webtoon Çeviri ve Yayın Platformu

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Hızlı Başlangıç

### Yeni Bilgisayarda Kurulum (5 Dakika)

```bash
# 1. Projeyi indirin
git clone https://github.com/KULLANICI_ADI/Webtoon.git
cd Webtoon

# 2. Otomatik kurulum
KURULUM_SIHIRBAZI.bat

# 3. Sistemi başlatın
START_ALL.bat
```

**Tarayıcınızda:** http://localhost:8000/docs

---

## 📋 Özellikler

### ✨ Çeviri Özellikleri

- 🌐 **Çoklu Dil Desteği** - 50+ dil arası çeviri
- 🤖 **AI Destekli Çeviri** - OpenAI GPT entegrasyonu
- 📝 **Glossary Sistemi** - Tutarlı terim çevirisi
- 🎯 **Context-Aware** - Bağlama duyarlı çeviri
- 🔄 **Batch Translation** - Toplu çeviri desteği

### 🖼️ Görüntü İşleme

- 🎨 **OCR (Optical Character Recognition)** - EasyOCR
- 🧹 **Text Cleaning** - Otomatik metin temizleme
- ✍️ **Text Rendering** - Çevrilmiş metni görüntüye ekleme
- 🖌️ **Font Customization** - Özelleştirilebilir fontlar
- 📐 **Auto Layout** - Otomatik metin yerleştirme

### 📚 İçerik Yönetimi

- 📖 **Series Management** - Seri yönetimi
- 📄 **Chapter Organization** - Bölüm organizasyonu
- 🏷️ **Tag System** - Etiket sistemi
- ⭐ **Rating & Reviews** - Değerlendirme sistemi
- 💬 **Comments** - Yorum sistemi

### 👥 Kullanıcı Özellikleri

- 🔐 **Authentication** - JWT tabanlı kimlik doğrulama
- 📊 **Reading History** - Okuma geçmişi
- 🔖 **Bookmarks** - Yer işaretleri
- 🔔 **Notifications** - Bildirimler
- 💳 **Subscription** - Abonelik sistemi

### 🛠️ Teknik Özellikler

- ⚡ **FastAPI** - Yüksek performanslı API
- 🗄️ **SQLAlchemy ORM** - Veritabanı yönetimi
- 📦 **Redis Cache** - Hızlı önbellekleme
- 🔄 **Celery** - Arka plan işleri
- 🐳 **Docker** - Kolay deployment
- 📝 **Auto Documentation** - Swagger/ReDoc

---

## 📦 Kurulum

### Gereksinimler

- Python 3.10+
- Docker Desktop
- Git

### Detaylı Kurulum

**Adım 1: Gerekli Programları Kurun**

1. **Python:** https://www.python.org/downloads/
2. **Docker:** https://www.docker.com/products/docker-desktop/
3. **Git:** https://git-scm.com/download/win

**Adım 2: Projeyi İndirin**

```bash
git clone https://github.com/KULLANICI_ADI/Webtoon.git
cd Webtoon
```

**Adım 3: Kurulum Sihirbazını Çalıştırın**

```bash
KURULUM_SIHIRBAZI.bat
```

**Adım 4: Sistemi Başlatın**

```bash
START_ALL.bat
```

**Detaylı kurulum için:** [ADIM_ADIM_KURULUM.md](ADIM_ADIM_KURULUM.md)

---

## 🎯 Kullanım

### Sistemi Başlatma

```bash
START_ALL.bat
```

### Sistemi Durdurma

```bash
STOP_ALL.bat
```

### API Dokümantasyonu

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### İlk Kullanım

1. http://localhost:8000/docs adresine gidin
2. `/api/v1/auth/register` ile kayıt olun
3. `/api/v1/auth/login` ile giriş yapın
4. Token'ı alın ve "Authorize" butonuna tıklayın
5. API'yi keşfedin!

---

## 📚 Dokümantasyon

| Dosya                                                          | Açıklama                 |
| -------------------------------------------------------------- | ------------------------ |
| [KURULUM_DOKUMANI.md](KURULUM_DOKUMANI.md)                     | Kapsamlı kurulum rehberi |
| [ADIM_ADIM_KURULUM.md](ADIM_ADIM_KURULUM.md)                   | Adım adım kurulum        |
| [HIZLI_BASLANGIC.md](HIZLI_BASLANGIC.md)                       | Hızlı başlangıç kılavuzu |
| [DOSYALAR_REHBERI.md](DOSYALAR_REHBERI.md)                     | Dosyalar rehberi         |
| [DOC/COMPLETE_DOCUMENTATION.md](DOC/COMPLETE_DOCUMENTATION.md) | Tam API dokümantasyonu   |

---

## 🏗️ Proje Yapısı

```
Webtoon/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── tasks/        # Celery tasks
├── tests/            # Test files
├── DOC/              # Documentation
├── START_ALL.bat     # Start system
├── STOP_ALL.bat      # Stop system
└── README.md         # This file
```

---

## 🔧 Teknolojiler

### Backend

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Celery** - Task queue
- **Redis** - Cache & message broker

### AI & ML

- **OpenAI GPT** - AI translation
- **EasyOCR** - Text recognition
- **Deep Translator** - Free translation
- **spaCy** - NLP (optional)

### Image Processing

- **OpenCV** - Image manipulation
- **Pillow** - Image processing
- **NumPy** - Numerical operations

### Web Scraping

- **BeautifulSoup4** - HTML parsing
- **Selenium** - Dynamic content
- **httpx** - HTTP client

---

## 📊 API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Kullanıcı kaydı
- `POST /api/v1/auth/login` - Giriş
- `GET /api/v1/auth/me` - Profil bilgisi

### Translation

- `POST /api/v1/translate/start` - Çeviri başlat
- `GET /api/v1/translate/status/{task_id}` - Durum sorgula
- `GET /api/v1/translate/result/{task_id}` - Sonuç al

### Series

- `GET /api/v1/public/series` - Serileri listele
- `GET /api/v1/series/{id}` - Seri detayı
- `POST /api/v1/series` - Seri oluştur
- `PUT /api/v1/series/{id}` - Seri güncelle

### Discovery

- `GET /api/v1/series/trending` - Trend seriler
- `GET /api/v1/series/featured` - Öne çıkanlar
- `GET /api/v1/series/popular` - Popüler seriler

**Tüm endpoint'ler için:** http://localhost:8000/docs

---

## 🧪 Testing

```bash
# Tüm testleri çalıştır
RUN_TESTS.bat

# Endpoint testleri
python test_all_endpoints.py

# Manuel test
pytest tests/
```

---

## 🐛 Sorun Giderme

### Python Bulunamadı

```bash
# Python'u PATH'e ekleyin veya yeniden kurun
python --version
```

### Docker Bağlantı Hatası

```bash
# Docker Desktop'ı açın ve Redis'i başlatın
docker start webtoon_redis
```

### Port Zaten Kullanımda

```bash
# Portu kullanan işlemi bulun ve sonlandırın
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Detaylı sorun giderme:** [KURULUM_DOKUMANI.md](KURULUM_DOKUMANI.md#sorun-giderme)

---

## 📝 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📞 İletişim

- **Proje:** https://github.com/KULLANICI_ADI/Webtoon
- **Issues:** https://github.com/KULLANICI_ADI/Webtoon/issues
- **Dokümantasyon:** http://localhost:8000/docs

---

## 🙏 Teşekkürler

Bu proje aşağıdaki harika açık kaynak projelerini kullanmaktadır:

- FastAPI
- SQLAlchemy
- OpenAI
- EasyOCR
- Celery
- Redis
- Docker

---

<div align="center">

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

Made with ❤️ by Webtoon AI Translator Team

</div>
