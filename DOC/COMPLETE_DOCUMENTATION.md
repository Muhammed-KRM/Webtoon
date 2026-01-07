# 📚 Webtoon AI Translator - Kapsamlı Dokümantasyon

## 📦 **KURULUM REHBERİ**

### 🚀 Hızlı Başlangıç (Yeni Sistem - 2026)

#### Yeni Bilgisayarda İlk Kurulum

**Adım 1: Gerekli Programları Kurun**

1. **Python 3.10+**: https://www.python.org/downloads/

   - ⚠️ Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin!

2. **Docker Desktop**: https://www.docker.com/products/docker-desktop/

   - Kurulum sonrası bilgisayarı yeniden başlatın

3. **Git** (opsiyonel): https://git-scm.com/download/win

**Adım 2: Otomatik Kurulum**

```bash
# İnteraktif kurulum (Önerilen - Yeni kullanıcılar için)
KURULUM_SIHIRBAZI.bat

# VEYA

# Hızlı otomatik kurulum (Deneyimli kullanıcılar için)
SETUP_COMPLETE.bat
```

Bu script'ler otomatik olarak:

- ✅ Virtual environment oluşturur
- ✅ Tüm Python paketlerini kurar
- ✅ Veritabanını oluşturur
- ✅ .env dosyasını yapılandırır
- ✅ Redis container'ını başlatır

**Adım 3: Sistemi Başlatın**

```bash
START_ALL.bat
```

Bu komut:

- ✅ Redis'i kontrol eder ve başlatır
- ✅ Web Server'ı başlatır (Port 8000)
- ✅ Celery Worker'ı başlatır
- ✅ Tarayıcıda API dokümantasyonunu açar

**Adım 4: Sistemi Test Edin**

Tarayıcınızda: http://localhost:8000/docs

---

### 📋 Kurulum Dosyaları

| Dosya                   | Amaç               | Kullanım                   |
| ----------------------- | ------------------ | -------------------------- |
| `KURULUM_SIHIRBAZI.bat` | İnteraktif kurulum | İlk kez kuruyorsanız       |
| `SETUP_COMPLETE.bat`    | Otomatik kurulum   | Hızlı kurulum istiyorsanız |
| `START_ALL.bat`         | Sistemi başlat     | Günlük kullanım            |
| `STOP_ALL.bat`          | Sistemi durdur     | Sistemi kapatırken         |

**Detaylı kurulum için:**

- `ADIM_ADIM_KURULUM.md` - Görsel adım adım rehber
- `KURULUM_DOKUMANI.md` - Kapsamlı kurulum dokümantasyonu
- `DOSYALAR_REHBERI.md` - Dosyalar hakkında bilgi

---

### 🔧 Kurulacak Paketler

#### Zorunlu Paketler (Otomatik Kurulur)

- **FastAPI**: Modern web framework
- **Celery**: Arka plan görev kuyruğu
- **Redis**: Cache ve message broker
- **SQLAlchemy**: ORM (Object-Relational Mapping)
- **OpenAI**: AI destekli çeviri
- **EasyOCR**: Optik karakter tanıma
- **OpenCV + Pillow**: Görüntü işleme
- **httpx + BeautifulSoup**: Web scraping
- **Deep Translator**: Ücretsiz çeviri servisi

#### Opsiyonel Paketler (Manuel Kurulum)

```bash
# Argos Translate (Offline ücretsiz çeviri)
pip install argostranslate

# Hugging Face Transformers (Offline AI çeviri)
pip install transformers torch

# spaCy (Gelişmiş NER)
pip install spacy
python -m spacy download en_core_web_sm
```

---

### 💻 Sistem Gereksinimleri

- **Python**: 3.10 veya üzeri
- **RAM**: Minimum 4GB (8GB önerilir)
- **Disk**: Minimum 5GB boş alan
- **Docker**: Redis için gerekli
- **İşletim Sistemi**: Windows 10/11, Linux, macOS

---

### 🔐 .env Dosyası Yapılandırması

`SETUP_COMPLETE.bat` otomatik olarak `.env` dosyası oluşturur.

**Varsayılan Ayarlar (Geliştirme):**

```env
SECRET_KEY=development_secret_key_change_in_production_32chars
DATABASE_URL=sqlite:///./webtoon.db
OPENAI_API_KEY=sk-your-openai-api-key-here
REDIS_URL=redis://localhost:6379/0
CDN_ENABLED=False
STRIPE_SECRET_KEY=sk_test_your-stripe-key-here
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

```

Detaylı rehber: `DOC/API_KEY_REHBERI.md`

### Otomatik Fallback Sistemi

Sistem otomatik olarak en iyi çeviri servisini seçer:

**Çeviri Servisleri (Öncelik Sırası):**

1. **Hugging Face** (varsa) → Offline, ücretsiz, kaliteli
2. **Argos Translate** (varsa) → Offline, ücretsiz, hızlı
3. **Google Translate** (her zaman) → Online, ücretsiz
4. **DeepL** (varsa) → Online, API key gerekebilir

**NER Servisleri (Öncelik Sırası):**

1. **spaCy** (varsa) → %85-95 doğruluk
2. **Regex** (her zaman) → %60-70 doğruluk

### Sorun Giderme

- **"spaCy model bulunamadı"**: `python -m spacy download en_core_web_sm`
- **"Argos Translate paketleri yok"**: İlk kullanımda otomatik indirilir
- **"Hugging Face model yüklenemiyor"**: İnternet bağlantısı gerekli (ilk kullanımda model indirilir)
- **Redis bağlantı hatası**: Docker'ı başlatın veya Memurai kullanın

---

## 🎯 **UYGULAMANIN AMACI**

**Webtoon AI Translator**, webtoon serilerini otomatik olarak çeviren profesyonel bir makine çeviri platformudur. Uygulama, görüntü işleme (Computer Vision), doğal dil işleme (NLP) ve asenkron iş akışları kullanarak webtoon görsellerindeki metinleri algılar, çevirir ve orijinal görsel üzerine yerleştirir.

### Ana Hedefler:

1. **Otomatik Çeviri:** Webtoon bölümlerini otomatik olarak çevirme
2. **Çoklu Site Desteği:** Farklı webtoon sitelerinden içerik çekme
3. **Çoklu Dil Desteği:** 30+ dilde çeviri yapabilme
4. **Okuma Platformu:** Çevrilmiş içerikleri okuma sitesi olarak sunma
5. **Premium Sistem:** Kullanıcılara premium çeviri hizmeti sunma
6. **Topluluk Özellikleri:** Yorum, tepki, favori gibi sosyal özellikler

### İki Ayrı Site İçin:

- **Çeviri Sitesi:** Diğer kullanıcılara makine çeviri hizmeti sunma
- **Okuma Sitesi:** Çevrilmiş webtoon serilerini okuma platformu

---

## 🛠️ **KULLANILAN TEKNOLOJİLER VE KULLANIM YERLERİ**

### Backend Framework

**FastAPI**

- **Nerede:** `main.py`, tüm API endpoint'leri
- **Neden:** Asenkron, hızlı, modern Python framework
- **Kullanım:** RESTful API, request/response handling, middleware

### Task Queue

**Celery + Redis**

- **Nerede:** `app/operations/translation_manager.py`, `app/celery_app.py`
- **Neden:** Uzun süren çeviri işlemlerini arka planda çalıştırmak
- **Kullanım:** OCR, çeviri, görüntü işleme işlemleri

### Database

**SQLAlchemy (ORM) + PostgreSQL/SQLite**

- **Nerede:** `app/db/`, `app/models/`
- **Neden:** Veritabanı yönetimi, ORM ile kolay veri erişimi
- **Kullanım:** Tüm veri modelleri, ilişkiler, sorgular

### Caching

**Redis**

- **Nerede:** `app/services/cache_service.py`, `app/services/api_cache.py`
- **Neden:** Hızlı veri erişimi, performans optimizasyonu
- **Kullanım:**
  - API response caching
  - Translation result caching
  - Rate limiting
  - Metrics storage

### OCR Engine

**EasyOCR**

- **Nerede:** `app/services/ocr_service.py`
- **Neden:** Görüntülerden metin algılama
- **Kullanım:** Webtoon sayfalarındaki metinleri tespit etme
- **Event Loop Protection:** `run_in_executor` ile thread pool'da çalışır
- **GPU Support:** Config'den GPU kullanımı açılıp kapatılabilir

### Translation Engine

**OpenAI GPT-4o-mini**

- **Nerede:** `app/services/ai_translator.py`
- **Neden:** Context-aware, tutarlı çeviri
- **Kullanım:** Metin çevirisi, karakter isim tutarlılığı

### Image Processing

**OpenCV + Pillow**

- **Nerede:** `app/services/image_processor.py`
- **Neden:** Görüntü işleme, metin yerleştirme
- **Kullanım:**
  - In-painting (metin silme)
  - Metin yerleştirme
  - Font boyutlandırma
  - Text wrapping (textwrap)
  - WebP format support
- **Event Loop Protection:** `run_in_executor` ile thread pool'da çalışır

### Authentication

**JWT (OAuth2)**

- **Nerede:** `app/core/security.py`
- **Neden:** Güvenli kullanıcı kimlik doğrulama
- **Kullanım:** Token tabanlı authentication, role-based access

### Web Scraping

**httpx + BeautifulSoup + Selenium**

- **Nerede:** `app/services/scraper_service.py`, `app/services/scrapers/`
- **Cloudflare Bypass:** `undetected-chromedriver` kullanılarak Cloudflare koruması bypass edilir (2026 güncellemesi)
- **Neden:** Webtoon sitelerinden içerik çekme
- **Kullanım:**
  - Webtoons.com scraping
  - AsuraScans scraping
  - Dinamik içerik yükleme

### Payment Gateway

**Stripe**

- **Nerede:** `app/services/payment_service.py`, `app/api/v1/endpoints/payments.py`
- **Neden:** Premium ödemeleri işleme
- **Kullanım:** Payment intent, webhook handling

### Logging

**Loguru + Database Logging**

- **Nerede:** `app/services/db_logger.py`, `app/core/middleware.py`
- **Neden:** Hata takibi, performans izleme
- **Kullanım:** Request/response logging, error tracking

### Enum System

**Python Enum (IntEnum, Enum)**

- **Nerede:** `app/core/enums.py`, `app/core/tag_enum.py`
- **Neden:** Tip güvenliği, tutarlılık, hata önleme
- **Kullanım:**
  - `TranslateType`: AI (1) veya FREE (2) çeviri seçimi
  - `TranslationMode`: CLEAN (1) veya OVERLAY (2) işleme modu
  - `JobStatus`: PENDING, PROCESSING, COMPLETED, FAILED
  - `SeriesStatus`: ONGOING, COMPLETED, HIATUS
  - `TranslationStatus`: PENDING, PROCESSING, COMPLETED, FAILED
  - `PlanType`: FREE, BASIC, PREMIUM
  - `PaymentStatus`: PENDING, COMPLETED, FAILED
  - `ReactionType`: EMOJI, GIF, MEMOJI
  - `NotificationType`: TRANSLATION_COMPLETED, NEW_CHAPTER, COMMENT_REPLY, vb.
  - `ProperNounType`: AUTO, YES, NO
  - `UserRole`: ADMIN, USER, GUEST, PREMIUM
  - `Theme`: LIGHT, DARK, AUTO
  - `Quality`: HIGH, FAST
  - `WebtoonTag`: 200+ webtoon tag'i (action, comedy, system, return, vb.)

### Tag & Category System

**Tag Enum + Database Models**

- **Nerede:** `app/core/tag_enum.py`, `app/models/tag.py`, `app/services/series_manager.py`
- **Neden:** Serilere tag ve kategori ekleme, filtreleme, arama
- **Kullanım:**
  - `WebtoonTag` enum: 200+ tag (genre, webtoon-specific, character, relationship, vb.)
  - `Tag` model: Many-to-many relationship ile serilere tag ekleme
  - `Category` model: Ana kategori sistemi (Action, Romance, vb.)
  - Tag validation: Enum'dan validate edilir, geçersiz tag'ler atlanır
  - Otomatik tag oluşturma: Var olmayan tag'ler otomatik oluşturulur

### Series Management System

**SeriesManager Service**

- **Nerede:** `app/services/series_manager.py`, `app/operations/translation_publisher.py`
- **Neden:** Seri bulma/oluşturma, chapter çakışma çözümü, transaction yönetimi
- **Kullanım:**
  - `create_or_get_series()`: Seri bulma/oluşturma (aynı isimde seri varsa yeni oluşturmaz)
  - `create_or_update_chapter()`: Chapter oluşturma/güncelleme (çakışma yönetimi)
  - `handle_chapter_conflict()`: Translation çakışma çözümü
  - `normalize_series_name()`: Seri ismi normalizasyonu (büyük/küçük harf, özel karakterler)
  - Transaction rollback: Hata durumunda otomatik rollback ve dosya temizleme

### Database Migrations

**Alembic**

- **Nerede:** `alembic/`, `alembic.ini`
- **Neden:** Veritabanı şema yönetimi
- **Kullanım:** Schema değişiklikleri, version control

### Validation

**Pydantic**

- **Nerede:** `app/schemas/`
- **Neden:** Request/response validation
- **Kullanım:** Tüm API endpoint'lerinde data validation

### Compression

**Gzip Middleware**

- **Nerede:** `app/core/compression.py`
- **Neden:** Response boyutunu küçültme
- **Kullanım:** Tüm API response'larında otomatik compression

### Rate Limiting

**slowapi + Redis**

- **Nerede:** `app/core/rate_limit.py`
- **Neden:** API abuse önleme
- **Kullanım:** Endpoint rate limiting

### Metrics

**Custom Metrics Collector**

- **Nerede:** `app/core/metrics.py`
- **Neden:** Performans izleme
- **Kullanım:** Request counters, timing, error rates

### Retry & Circuit Breaker

**Custom Implementation**

- **Nerede:** `app/core/retry.py`, `app/core/circuit_breaker.py`
- **Neden:** Hata toleransı, sistem stabilitesi
- **Kullanım:** External API çağrılarında retry logic

---

## 📁 **NİHAİ TAM DOSYA YAPISI**

```

webtoon-ai-translator/
│
├── 📄 main.py # FastAPI uygulama giriş noktası
├── 📄 requirements.txt # Python bağımlılıkları
├── 📄 alembic.ini # Alembic konfigürasyonu
├── 📄 .env.example # Environment variables örneği
├── 📄 .gitignore # Git ignore kuralları
│
├── 📁 alembic/ # Database migrations
│ ├── env.py # Alembic environment
│ ├── script.py.mako # Migration template
│ └── versions/ # Migration dosyaları
│
├── 📁 app/ # Ana uygulama klasörü
│ │
│ ├── 📁 api/ # API katmanı
│ │ └── 📁 v1/ # API v1
│ │ ├── router.py # Tüm endpoint'leri toplayan router
│ │ └── 📁 endpoints/ # Endpoint dosyaları
│ │ ├── auth.py # Authentication endpoints
│ │ ├── translate.py # Çeviri endpoints
│ │ ├── jobs.py # Job history endpoints
│ │ ├── files.py # File serving endpoints
│ │ ├── admin.py # Admin endpoints
│ │ ├── admin*content.py # Admin content management (manual upload, page edit)
│ │ ├── metrics.py # Metrics endpoints
│ │ ├── users.py # User management endpoints
│ │ ├── series.py # Series management endpoints
│ │ ├── comments.py # Comment endpoints
│ │ ├── reactions.py # Reaction endpoints
│ │ ├── subscription.py # Subscription endpoints
│ │ ├── payments.py # Payment endpoints
│ │ ├── site_settings.py # Site settings endpoints
│ │ ├── reading.py # Reading history/bookmarks/ratings
│ │ ├── notifications.py # Notification endpoints
│ │ ├── public.py # Public (no auth) endpoints
│ │ ├── discovery.py # Discovery endpoints (trending, featured, recommendations)
│ │ ├── cache.py # Cache management endpoints
│ │ ├── logs.py # Log viewing endpoints
│ │ └── translation_editor.py # Human-in-the-Loop editor endpoints
│ │
│ ├── 📁 core/ # Çekirdek modüller (14 dosya)
│ │ ├── config.py # Uygulama ayarları
│ │ │ # - Settings class (Pydantic)
│ │ │ # - Environment variables
│ │ │ # - Default values
│ │ │
│ │ ├── database.py # Database connection
│ │ │ # - SQLAlchemy engine
│ │ │ # - SessionLocal factory
│ │ │ # - get_db() dependency
│ │ │
│ │ ├── security.py # JWT, password hashing
│ │ │ # - create_access_token()
│ │ │ # - verify_password()
│ │ │ # - get_current_user()
│ │ │ # - require_admin()
│ │ │ # - get_current_user_optional()
│ │ │
│ │ ├── exceptions.py # Custom exceptions
│ │ │ # - global_exception_handler
│ │ │ # - validation_exception_handler
│ │ │ # - database_exception_handler
│ │ │
│ │ ├── middleware.py # Request/response middleware
│ │ │ # - RequestIDMiddleware
│ │ │ # - LoggingMiddleware
│ │ │ # - SecurityHeadersMiddleware
│ │ │
│ │ ├── metrics.py # Metrics collection
│ │ │ # - MetricsCollector class
│ │ │ # - increment_counter()
│ │ │ # - record_timing()
│ │ │
│ │ ├── rate_limit.py # Rate limiting
│ │ │ # - @rate_limit decorator
│ │ │ # - Redis-based limiting
│ │ │
│ │ ├── retry.py # Retry decorators
│ │ │ # - @retry (async)
│ │ │ # - @retry_sync
│ │ │
│ │ ├── circuit_breaker.py # Circuit breaker pattern
│ │ │ # - CircuitBreaker class
│ │ │ # - Failure threshold
│ │ │
│ │ ├── compression.py # Gzip compression
│ │ │ # - CompressionMiddleware
│ │ │ # - Response compression
│ │ │
│ │ ├── query_optimizer.py # Query optimization
│ │ │ # - Eager loading utilities
│ │ │ # - N+1 query prevention
│ │ │
│ │ ├── cache_invalidation.py # Cache invalidation
│ │ │ # - CacheInvalidation class
│ │ │ # - Invalidate methods
│ │ │
│ │ ├── stale_while_revalidate.py # SWR pattern
│ │ │ # - Stale-while-revalidate cache
│ │ │
│ │ ├── cache_decorator.py # Cache decorator
│ │ │ # - @cache_response decorator
│ │ │
│ │ └── response.py # Base response model
│ │ # - BaseResponse<T> generic
│ │ # - success_response()
│ │ # - error_response()
│ │
│ ├── 📁 db/ # Database modülleri
│ │ ├── base.py # SQLAlchemy base
│ │ └── session.py # Database session factory
│ │
│ ├── 📁 models/ # Database modelleri
│ │ ├── user.py # User model
│ │ ├── job.py # TranslationJob model
│ │ ├── series.py # Series, Chapter, ChapterTranslation
│ │ ├── comment.py # Comment model
│ │ ├── comment_like.py # CommentLike model
│ │ ├── reaction.py # Reaction model
│ │ ├── subscription.py # Subscription, Payment models
│ │ ├── site_settings.py # SiteSettings model
│ │ ├── reading.py # ReadingHistory, Bookmark, Rating, Notification
│ │ ├── log.py # Log model
│ │ ├── scraper_config.py # ScraperConfig model (dynamic CSS selectors)
│ │ └── **init**.py # Model exports
│ │
│ ├── 📁 schemas/ # Pydantic schemas (9 dosya)
│ │ ├── base_response.py # BaseResponse model
│ │ │ # - Generic BaseResponse<T>
│ │ │ # - success/error helpers
│ │ │
│ │ ├── auth.py # Auth schemas
│ │ │ # - UserRegister
│ │ │ # - UserLogin
│ │ │ # - Token, UserResponse
│ │ │
│ │ ├── translation.py # Translation schemas
│ │ │ # - TranslationRequest
│ │ │ # - JobStatusResponse
│ │ │ # - ChapterResponse
│ │ │
│ │ ├── batch_translation.py # Batch translation schemas
│ │ │ # - BatchTranslationRequest
│ │ │ # - ChapterRangeRequest
│ │ │ # - BatchTranslationResponse
│ │ │
│ │ ├── series.py # Series schemas
│ │ │ # - SeriesCreate, SeriesUpdate
│ │ │ # - SeriesResponse
│ │ │ # - ChapterResponse
│ │ │ # - ChapterTranslationResponse
│ │ │
│ │ ├── comment.py # Comment schemas
│ │ │ # - CommentCreate, CommentUpdate
│ │ │ # - CommentResponse (with replies)
│ │ │
│ │ ├── reaction.py # Reaction schemas
│ │ │ # - ReactionCreate
│ │ │ # - ReactionResponse
│ │ │ # - ReactionSummary
│ │ │
│ │ ├── subscription.py # Subscription schemas
│ │ │ # - SubscriptionResponse
│ │ │ # - PaymentRequest, PaymentResponse
│ │ │
│ │ ├── site_settings.py # Site settings schemas
│ │ │ # - SiteSettingsResponse
│ │ │ # - SiteSettingsUpdate
│ │ │
│ │ └── **init**.py # Schema exports
│ │
│ ├── 📁 services/ # Servis katmanı (14 dosya)
│ │ ├── scraper_service.py # Web scraping orchestrator
│ │ │ # - Site detection
│ │ │ # - Scraper selection
│ │ │ # - fetch_chapter_images()
│ │ │
│ │ ├── scrapers/ # Site-specific scrapers (3 dosya)
│ │ │ ├── base_scraper.py # Base scraper interface
│ │ │ │ # - Abstract base class
│ │ │ │ # - Common HTTP client
│ │ │ │
│ │ │ ├── webtoons_scraper.py # Webtoons.com scraper
│ │ │ │ # - API endpoint detection
│ │ │ │ # - HTML parsing
│ │ │ │ # - JavaScript variable extraction
│ │ │ │
│ │ │ └── asura_scraper.py # AsuraScans scraper
│ │ │ # - Reader container detection
│ │ │ # - Image URL extraction
│ │ │
│ │ ├── scraper_config_service.py # Dynamic scraper configuration
│ │ │ # - CSS selector management
│ │ │ # - Database-based config
│ │ │ # - Default selector fallback
│ │ │ # - Admin config updates
│ │ │
│ │ ├── ocr_service.py # OCR (EasyOCR)
│ │ │ # - EasyOCR reader initialization
│ │ │ # - Text detection
│ │ │ # - Bounding box extraction
│ │ │ # - GPU support (optional)
│ │ │ # - Async wrapper (run_in_executor)
│ │ │ # - Event loop blocking prevention
│ │ │
│ │ ├── ai_translator.py # OpenAI translation
│ │ │ # - GPT-4o-mini integration
│ │ │ # - Context-aware translation
│ │ │ # - Cached Input support
│ │ │ # - Batch translation
│ │ │ # - Glossary system integration
│ │ │ # - Smart chunking (token limit management)
│ │ │
│ │ ├── image_processor.py # Image processing (OpenCV, Pillow)
│ │ │ # - In-painting (text removal)
│ │ │ # - Text rendering
│ │ │ # - Dynamic font sizing
│ │ │ # - Multi-line text support
│ │ │ # - Text wrapping (textwrap)
│ │ │ # - WebP format support (~50% smaller)
│ │ │ # - Async wrapper (run_in_executor)
│ │ │ # - Event loop blocking prevention
│ │ │
│ │ ├── file_manager.py # File organization
│ │ │ # - Folder structure creation
│ │ │ # - Chapter/page naming
│ │ │ # - Metadata saving
│ │ │ # - CDN integration (S3/MinIO)
│ │ │ # - Automatic CDN upload
│ │ │ # - Local fallback
│ │ │
│ │ ├── cache_service.py # Redis caching
│ │ │ # - Translation result caching
│ │ │ # - Cache key generation
│ │ │ # - TTL management
│ │ │ # - Translation lock mechanism
│ │ │ # - Duplicate prevention
│ │ │
│ │ ├── api_cache.py # API response caching
│ │ │ # - Endpoint response caching
│ │ │ # - Cache key hashing
│ │ │ # - Invalidation utilities
│ │ │
│ │ ├── db_logger.py # Database logging
│ │ │ # - Background log writer thread
│ │ │ # - Log queue management
│ │ │ # - Database log storage
│ │ │
│ │ ├── notification_service.py # Notification service
│ │ │ # - Create notifications
│ │ │ # - Translation completed
│ │ │ # - New chapter
│ │ │ # - Comment reply
│ │ │
│ │ ├── payment_service.py # Stripe payment service
│ │ │ # - Payment intent creation
│ │ │ # - Payment confirmation
│ │ │ # - Webhook handling
│ │ │
│ │ ├── language_detector.py # Language detection
│ │ │ # - URL-based detection
│ │ │ # - Language validation
│ │ │ # - ISO 639-1 support
│ │ │
│ │ └── url_generator.py # URL generation utilities
│ │ # - Chapter range parsing
│ │ # - URL pattern detection
│ │ # - Chapter URL generation
│ │
│ ├── 📁 operations/ # İş akışı yönetimi (3 dosya)
│ │ ├── translation_manager.py # Translation pipeline (Celery task)
│ │ │ # - @celery_app.task decorator
│ │ │ # - process_chapter_task()
│ │ │ # - Full pipeline orchestration
│ │ │ # - Progress tracking
│ │ │ # - Error handling
│ │ │
│ │ ├── batch_translation_manager.py # Batch translation
│ │ │ # - batch_translation_task()
│ │ │ # - Multiple chapter processing
│ │ │ # - Sequential execution
│ │ │
│ │ └── translation_publisher.py # Auto-publish translations (geliştirilmiş hata yönetimi)
│ │ # - publish_translation_on_completion()
│ │ # - ChapterTranslation creation
│ │ # - Automatic publishing
│ │ # - Transaction rollback ve dosya temizleme
│ │
│ └── 📁 **init**.py
│
├── 📁 DOC/ # Dokümantasyon
│ ├── COMPLETE_DOCUMENTATION.md # Bu dosya
│ ├── API_KEY_REHBERI.md # API key rehberi
│ ├── BACKEND_REVIEW.md # Backend inceleme
│ ├── CACHE_STRATEGY.md # Cache stratejisi
│ ├── COMPLETE_CACHE_INVALIDATION.md # Cache invalidation
│ ├── COMPLETE_ENDPOINTS.md # Endpoint listesi
│ ├── COMPLETE_IMPLEMENTATION.md # Implementation detayları
│ ├── PERFORMANCE_OPTIMIZATIONS.md # Performans optimizasyonları
│ ├── SPEED_OPTIMIZATIONS.md # Hız optimizasyonları
│ └── ... (diğer dokümantasyon dosyaları)
│
├── 📁 storage/ # Çevrilmiş görseller (gitignore)
│ └── {series_name}/ # Seri klasörleri
│ └── {source_lang}\_to*{target*lang}/
│ └── chapter*{number:04d}/
│ ├── page_001.jpg
│ ├── page_002.jpg
│ ├── cleaned/ # Temizlenmiş (yazısız) resimler (Editör için)
│ │ ├── page_001.jpg
│ │ └── ...
│ └── metadata.json
│
├── 📁 cache/ # Cache dosyaları (gitignore)
│
├── 📁 fonts/ # Font dosyaları
│ └── (Türkçe karakter desteği olan fontlar)
│
├── 📄 README.md # Ana README
│ # - Proje açıklaması
│ # - Hızlı başlangıç
│ # - Özellikler
│
├── 📄 START.bat # Proje başlatma script'i
│ # - Redis başlatma
│ # - Celery Worker başlatma
│ # - FastAPI başlatma
│ # - Tarayıcı otomatik açma
│
├── 📄 STOP.bat # Proje durdurma script'i
│ # - Tüm servisleri durdurma
│
├── 📄 RESTART.bat # Proje yeniden başlatma
│
├── 📄 CHECK.bat # Servis durumu kontrol
│ # - Redis durumu
│ # - Celery durumu
│ # - FastAPI durumu
│
├── 📄 SETUP.bat # İlk kurulum script'i
│ # - Virtual environment
│ # - Temel paket yükleme
│ # - Opsiyonel paket yükleme (Hugging Face, Argos, spaCy)
│ # - spaCy model indirme
│ # - .env oluşturma
│ # - Klasör oluşturma
│
├── 📄 INSTALL_OPTIONAL.bat # Sadece opsiyonel paketler
│ # - Hugging Face Transformers
│ # - Argos Translate
│ # - spaCy + modeller
│
├── 📄 INSTALL_ALL.bat # Tam kurulum script'i
│
├── 📄 START.bat # Proje başlatma script'i
│ # - Redis başlatma
│ # - Celery Worker başlatma
│ # - FastAPI başlatma
│ # - Tarayıcıda API docs açma
│
├── 📄 STOP.bat # Tüm servisleri durdurma
│
├── 📄 RESTART.bat # Servisleri yeniden başlatma
│
├── 📄 CHECK.bat # Servis durumu kontrolü
│
├── 📄 README_INSTALLATION.md # Detaylı kurulum rehberi
│
├── 📄 GITHUB_DEPLOY.bat # GitHub'a yükleme script'i
│
├── 📄 GITHUB_INSTRUCTIONS.md # GitHub talimatları
│
├── 📄 ENV_OLUSTUR.md # Environment variables rehberi
│
├── 📄 KURULUM.md # Kurulum rehberi
│
└── 📄 MIGRATIONS_GUIDE.md # Database migration rehberi

````

---

## ⚡ **KISA ÖZELLİK ÖZETİ**

### ✅ **Tag & Category Sistemi**

- **200+ Webtoon Tag**: Genre tags (action, comedy, drama, vb.), webtoon-specific tags (system, return, rebirth, vb.), character tags, relationship tags
- **Tag Enum**: `WebtoonTag` enum ile tüm tag'ler validate edilir
- **Category System**: Ana kategori sistemi (Action, Romance, vb.)
- **Tag Validation**: Geçersiz tag'ler otomatik atlanır, geçerli tag'ler normalize edilir
- **Many-to-Many Relationship**: Seriler birden fazla tag'e sahip olabilir

### ✅ **Seri Yönetimi ve Çakışma Çözümü**

- **Akıllı Seri Bulma**: Aynı isimde seri varsa yeni oluşturmaz, mevcut seriyi kullanır
- **Chapter Çakışma Yönetimi**: Aynı chapter number varsa yenisiyle değiştirilebilir veya korunabilir
- **Translation Çakışma Yönetimi**: Aynı dil çifti varsa eski translation dosyaları silinir, yenisiyle değiştirilir
- **Otomatik Seri Oluşturma**: Çeviri sırasında seri yoksa otomatik oluşturulur
- **Transaction Rollback**: Hata durumunda otomatik rollback ve dosya temizleme
- **Veri Bütünlüğü**: Veri kaybı önleme mekanizmaları

### ✅ **Discovery Özellikleri**

- **Trending Series**: Günlük/haftalık/aylık trending seriler
- **Featured Series**: Admin seçili öne çıkan seriler
- **Recommendations**: Kullanıcıya özel öneriler (okuma geçmişi, bookmark'lar, benzer türler)
- **Popular Series**: Popüler seriler (görüntülenme sayısına göre)
- **Newest Series**: En yeni seriler
- **Genre List**: Mevcut türler ve sayıları

### ✅ **Admin Content Management**

- **Manuel Chapter Upload**: Admin'ler çeviri yaptırmadan direkt bölüm yükleyebilir
- **Page Editing**: Spesifik sayfa düzenleme/yeniden yükleme
- **Page Deletion**: Spesifik sayfa silme
- **Page Reordering**: Sayfa sıralamasını yeniden düzenleme
- **Bulk Publish**: Toplu bölüm yayınlama/yayından kaldırma

### ✅ **Çeviri Özellikleri**

- ✅ Multi-site scraping (Webtoons.com, AsuraScans)
- ✅ Multi-language translation (30+ dil)
- ✅ Context-aware translation (tutarlı karakter isimleri)
- ✅ Batch translation (bölüm aralığı)
- ✅ Automatic translation publishing
- ✅ **Glossary System**: Seri bazlı sözlük (tutarlı çeviri)
- ✅ **Smart Chunking**: Token limiti yönetimi (büyük bölümler için)
- ✅ **Human-in-the-Loop Editor**: Manuel çeviri düzenleme
- ✅ **Event Loop Protection**: CPU-intensive işlemler thread pool'da

### ✅ **Okuma Platformu Özellikleri**

- ✅ Series management (seri yönetimi)
- ✅ Chapter management (bölüm yönetimi)
- ✅ Multi-language reading (çoklu dil okuma)
- ✅ Reading history (okuma geçmişi)
- ✅ Bookmarks (favoriler)
- ✅ Ratings (puanlar)

### ✅ **Infrastructure & Performance**

- ✅ **CDN Integration**: S3/MinIO desteği (disk tasarrufu, hız)
- ✅ **Dinamik Scraper Config**: CSS selector'lar DB'den yönetilir
- ✅ **Event Loop Protection**: CPU-intensive işlemler thread pool'da
- ✅ **WebP Format**: %50 daha küçük dosya boyutu
- ✅ **Cache/Lock Mechanism**: Duplicate translation prevention

### ✅ **Sosyal Özellikler**

- ✅ Comment system (yorum sistemi)
- ✅ Reply system (cevap sistemi)
- ✅ Like system (beğeni sistemi)
- ✅ Reaction system (emoji, gif, memoji tepkileri)

### ✅ **Premium & Payment**

- ✅ Subscription system (abonelik sistemi)
- ✅ Stripe payment integration
- ✅ Monthly chapter limits
- ✅ Extra chapter purchases

### ✅ **Performans & Optimizasyon**

- ✅ Redis caching (API responses, translations)
- ✅ Response compression (Gzip)
- ✅ Query optimization (eager loading)
- ✅ Database logging
- ✅ Cache invalidation (aggressive)
- ✅ **Offline çeviri desteği:** Hugging Face ve Argos Translate ile internet olmadan çeviri
- ✅ **Otomatik fallback:** En iyi çeviri servisini otomatik seçme

### ✅ **Güvenlik & Monitoring**

- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Rate limiting
- ✅ Request logging
- ✅ Error tracking
- ✅ Metrics collection

---

## 📋 **TÜM ENDPOINT'LER VE AÇIKLAMALARI**

> **Not:** Tüm endpoint'ler `BaseResponse<T>` formatında response döner:
>
> ```json
> {
>   "success": true,
>   "message": "Success message",
>   "data": { ... }
> }
> ```
>
> **Cache Notu:** Public ve read-heavy endpoint'ler Redis ile cache'lenir (TTL: 3-5 dakika). Write işlemlerinde otomatik cache invalidation yapılır.

### 🔐 **Authentication Endpoints** (`/api/v1/auth`)

#### `POST /api/v1/auth/register`

**Amaç:** Yeni kullanıcı kaydı
**Request:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
````

**Response:** JWT access token
**Kullanım:** Kullanıcı kayıt işlemi

#### `POST /api/v1/auth/login`

**Amaç:** Kullanıcı girişi
**Request:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response:** JWT access token
**Kullanım:** Kullanıcı giriş işlemi

#### `GET /api/v1/auth/me`

**Amaç:** Giriş yapan kullanıcı bilgisi
**Auth:** Required
**Response:** User profile
**Kullanım:** Kullanıcı profil bilgisi

---

### 🌐 **Translation Endpoints** (`/api/v1/translate`)

#### `POST /api/v1/translate/start`

**Amaç:** Çeviri işlemini başlatır
**Auth:** Required
**Request:**

```json
{
  "chapter_url": "string",
  "target_lang": "tr",
  "source_lang": "en",
  "mode": "clean",
  "quality": "high",
  "series_name": "Eleceed",
  "translate_type": 1
}
```

**Request Parametreleri:**

- `chapter_url`: Bölüm URL'si (zorunlu)
- `target_lang`: Hedef dil kodu (default: "tr")
- `source_lang`: Kaynak dil kodu (default: "en")
- `mode`: İşleme modu - `"clean"` (temizleme) veya `"overlay"` (üzerine yazma) (default: "clean")
- `quality`: Çeviri kalitesi - `"high"` (yüksek) veya `"fast"` (hızlı) (default: "high")
- `series_name`: Seri adı (opsiyonel, dosya organizasyonu için)
- `translate_type`: Çeviri tipi - `1` (AI/OpenAI GPT-4o-mini) veya `2` (Free/Google Translate) (default: 1)

**Response:** Task ID
**Kullanım:** Tek bölüm çevirisi başlatma
**Not:** `translate_type=1` (AI) ücretlidir ama yüksek kalite, `translate_type=2` (Free) ücretsizdir ama kalite düşüktür. Free çeviride özel isim sözlüğü otomatik kullanılır.

#### `GET /api/v1/translate/status/{task_id}`

**Amaç:** Çeviri işleminin durumunu kontrol eder
**Auth:** Required
**Response:** Status, progress (0-100)
**Kullanım:** İşlem ilerlemesini takip etme

#### `GET /api/v1/translate/result/{task_id}`

**Amaç:** Tamamlanmış çeviri sonuçlarını getirir
**Auth:** Required
**Response:** Processed images list
**Kullanım:** Çevrilmiş sayfaları görüntüleme

#### `POST /api/v1/translate/batch/start`

**Amaç:** Başlangıç ve bitiş bölüm numaraları ile toplu çeviri başlatır
**Auth:** Required
**Request:**

```json
{
  "base_url": "https://webtoons.com/en/series/episode-{}/viewer",
  "start_chapter": 1,
  "end_chapter": 10,
  "source_lang": "en",
  "target_lang": "tr",
  "mode": "clean",
  "series_name": "Eleceed",
  "translate_type": 1
}
```

**Request Parametreleri:**

- `base_url`: URL pattern (bölüm numarası için `{}` placeholder)
- `start_chapter`: Başlangıç bölüm numarası
- `end_chapter`: Bitiş bölüm numarası
- `source_lang`: Kaynak dil (default: "en")
- `target_lang`: Hedef dil (default: "tr")
- `mode`: İşleme modu (default: "clean")
- `series_name`: Seri adı (opsiyonel)
- `translate_type`: Çeviri tipi - `1` (AI) veya `2` (Free) (default: 1)

**Response:** BatchTranslationResponse (task_id, total_chapters, chapters list)
**Kullanım:** Ardışık bölüm aralığı çevirisi (1-10 gibi)

#### `POST /api/v1/translate/batch/range`

**Amaç:** Esnek bölüm aralığı çevirisi başlatır (örn: "1-10", "5,7,9", "1-5,10-15")
**Auth:** Required
**Request:**

```json
{
  "series_url": "https://webtoons.com/en/series/episode-{}/viewer",
  "chapter_range": "1-10,15,20-25",
  "source_lang": "en",
  "target_lang": "tr",
  "mode": "clean",
  "series_name": "Eleceed",
  "translate_type": 1
}
```

**Request Parametreleri:**

- `series_url`: URL pattern (bölüm numarası için `{}` placeholder)
- `chapter_range`: Bölüm aralığı (örn: "1-10", "5,7,9", "1-5,10-15")
- `source_lang`: Kaynak dil (default: "en")
- `target_lang`: Hedef dil (default: "tr")
- `mode`: İşleme modu (default: "clean")
- `series_name`: Seri adı (opsiyonel)
- `translate_type`: Çeviri tipi - `1` (AI) veya `2` (Free) (default: 1)

**Response:** BatchTranslationResponse
**Kullanım:** Esnek bölüm seçimi (aralık, tek tek, karışık)
**Özellik:** URL pattern otomatik algılama ve chapter numarası yerleştirme

---

### ✏️ **Translation Editor Endpoints** (`/api/v1/translation`)

#### `GET /api/v1/translation/{task_id}/review`

**Amaç:** Çeviri sonucunu manuel inceleme için getir (Human-in-the-Loop)
**Auth:** Required
**Query Params:** `page_index` (optional)
**Response:** Translation review data (original + translated texts side-by-side)
**Kullanım:** AI çevirisini inceleme, düzenleme öncesi görüntüleme

#### `POST /api/v1/translation/review`

**Amaç:** Çeviriyi onaylama/reddetme/düzenleme
**Auth:** Required
**Request:**

```json
{
  "task_id": "uuid",
  "page_index": 0,
  "block_index": 0,
  "action": "approve|reject|edit",
  "edited_text": "Düzenlenmiş metin" // action=edit için gerekli
}
```

**Response:** Review result
**Kullanım:** Çeviriyi onaylama, reddetme veya düzenleme

#### `POST /api/v1/translation/edit`

**Amaç:** Spesifik bir çeviri bloğunu manuel düzenleme
**Auth:** Required
**Request:**

```json
{
  "task_id": "uuid",
  "page_index": 0,
  "block_index": 0,
  "original_text": "Orijinal metin",
  "translated_text": "Düzenlenmiş çeviri"
}
```

**Response:** Edited translation
**Kullanım:** Manuel çeviri düzeltme

---

### 📚 **Series Endpoints** (`/api/v1/series`)

#### `GET /api/v1/series`

**Amaç:** Seri listesi (public, cached)
**Auth:** Optional
**Query Params:**

- `skip`: Pagination offset
- `limit`: Page size
- `search`: Arama terimi
- `genre`: Genre filtresi
- `status`: Status filtresi (ongoing, completed)
- `sort`: Sıralama (newest, popular, rating)
  **Response:** Series list
  **Kullanım:** Ana sayfa seri listesi

#### `GET /api/v1/series/{series_id}`

**Amaç:** Seri detay sayfası (public, cached)
**Auth:** Optional
**Response:** Series details, chapters, ratings, bookmarks
**Kullanım:** Seri detay sayfası

#### `POST /api/v1/series`

**Amaç:** Yeni seri oluşturur (Admin only)
**Auth:** Required (Admin)
**Request:** SeriesCreate schema
**Response:** Created series
**Kullanım:** Admin seri ekleme

#### `PUT /api/v1/series/{series_id}`

**Amaç:** Seri güncelleme (Admin only)
**Auth:** Required (Admin)
**Request:** SeriesUpdate schema (partial update)
**Response:** Updated series
**Kullanım:** Seri metadata güncelleme
**Özellikler:**

- ✅ Partial update (sadece gönderilen alanlar güncellenir)
- ✅ Cache otomatik invalidate edilir

#### `DELETE /api/v1/series/{series_id}`

**Amaç:** Seri silme (Admin only - Soft delete)
**Auth:** Required (Admin)
**Response:** Deletion confirmation
**Kullanım:** Seri silme (soft delete: is_active=False, is_published=False)
**Özellikler:**

- ✅ Soft delete (veriler silinmez, sadece pasif edilir)
- ✅ Cache otomatik invalidate edilir

#### `PUT /api/v1/chapters/{chapter_id}`

**Amaç:** Bölüm güncelleme (Admin only)
**Auth:** Required (Admin)
**Request:** ChapterCreate schema (partial update)
**Response:** Updated chapter
**Kullanım:** Bölüm metadata güncelleme
**Özellikler:**

- ✅ Partial update
- ✅ series_id değiştirilemez
- ✅ Cache otomatik invalidate edilir

#### `DELETE /api/v1/chapters/{chapter_id}`

**Amaç:** Bölüm silme (Admin only - Soft delete)
**Auth:** Required (Admin)
**Response:** Deletion confirmation
**Kullanım:** Bölüm silme (soft delete: is_published=False)
**Özellikler:**

- ✅ Soft delete
- ✅ Cache otomatik invalidate edilir

#### `POST /api/v1/chapters/{chapter_id}/publish`

**Amaç:** Bölüm yayınlama/yayından kaldırma (Admin only)
**Auth:** Required (Admin)
**Query Params:**

- `publish`: true (yayınla) veya false (yayından kaldır)
  **Response:** Publish status
  **Kullanım:** Bölüm yayın durumu kontrolü

#### `POST /api/v1/chapters/{chapter_id}/translations/{translation_id}/publish`

**Amaç:** Translation yayınlama/yayından kaldırma (Admin only)
**Auth:** Required (Admin)
**Query Params:**

- `publish`: true (yayınla) veya false (yayından kaldır)
  **Response:** Publish status
  **Kullanım:** Translation yayın durumu kontrolü

#### `GET /api/v1/series/{series_id}/chapters`

**Amaç:** Seriye ait bölüm listesi (public, cached)
**Auth:** Optional
**Query Params:** skip, limit
**Response:** Chapter list
**Kullanım:** Seri bölüm listesi

#### `GET /api/v1/chapters/{chapter_id}/translations`

**Amaç:** Bölümün mevcut çeviri versiyonları (public, cached)
**Auth:** Optional
**Query Params:**

- `source_lang`: Kaynak dil filtresi (optional)
- `target_lang`: Hedef dil filtresi (optional)
  **Response:**

```json
{
  "id": 1,
  "chapter_id": 5,
  "source_lang": "en",
  "target_lang": "tr",
  "storage_path": "/storage/Eleceed/en_to_tr/chapter_0005",
  "page_count": 20,
  "status": "completed",
  "is_published": true,
  "view_count": 150
}
```

**Kullanım:** Çeviri versiyonlarını görüntüleme, dil seçimi
**Cache:** 10 dakika (TTL: 600)

#### `POST /api/v1/chapters/{chapter_id}/translate`

**Amaç:** Premium kullanıcılar için bölüm çevirisi talep etme
**Auth:** Required (Premium)
**Query Params:**

- `source_lang`: Kaynak dil (default: "en")
- `target_lang`: Hedef dil (default: "tr")
- `translate_type`: Çeviri tipi - `1` (AI) veya `2` (Free) (default: 1)
  **Response:** Task ID
  **Kullanım:** Premium kullanıcılar bölüm çevirisi talep edebilir
  **Not:** Aylık bölüm limiti kontrol edilir, aşılırsa ödeme gerekir
  **Amaç:** Bölüm için çeviri isteği (Premium)
  **Auth:** Required (Premium)
  **Query Params:** `target_lang` (string, required)
  **Response:**

```json
{
  "chapter_id": 5,
  "target_lang": "tr",
  "task_id": "abc123-def456",
  "translation_id": 10
}
```

**Kullanım:** Premium kullanıcı çeviri isteği
**Özellikler:**

- Aylık limit kontrolü
- Limit aşılırsa ödeme gerektirme (402 Payment Required)
- Otomatik ChapterTranslation oluşturma
- Çeviri tamamlandığında otomatik yayınlama
  **Cache Invalidation:** Chapter ve series cache'i temizlenir

---

### 💬 **Comment Endpoints** (`/api/v1/comments`)

#### `GET /api/v1/comments`

**Amaç:** Yorum listesi (public, cached)
**Auth:** Optional
**Query Params:**

- `series_id`: Seri filtresi
- `chapter_id`: Bölüm filtresi
- `skip`, `limit`: Pagination
  **Response:** Comment list with nested replies
  **Kullanım:** Yorumları görüntüleme

#### `POST /api/v1/comments`

**Amaç:** Yeni yorum yazma
**Auth:** Required
**Request:**

```json
{
  "series_id": 1,
  "chapter_id": 5,
  "content": "string",
  "attachments": []
}
```

**Response:** Created comment
**Kullanım:** Yorum yazma

#### `POST /api/v1/comments/{comment_id}/reply`

**Amaç:** Yorum cevaplama
**Auth:** Required
**Request:** content (string)
**Response:** Created reply
**Kullanım:** Yorum cevaplama

#### `POST /api/v1/comments/{comment_id}/like`

**Amaç:** Yorum beğenme/unlike (toggle)
**Auth:** Required
**Response:**

```json
{
  "comment_id": 5,
  "like_count": 12,
  "liked": true
}
```

**Kullanım:** Yorum beğenme/beğenmeme (toggle)
**Özellik:** İlk çağrıda beğenir, ikinci çağrıda beğeniyi kaldırır
**Cache Invalidation:** Comment cache temizlenir

#### `PUT /api/v1/comments/{comment_id}`

**Amaç:** Yorum düzenleme
**Auth:** Required (own comment or admin)
**Request:** CommentUpdate schema
**Response:** Updated comment
**Kullanım:** Yorum düzenleme

#### `DELETE /api/v1/comments/{comment_id}`

**Amaç:** Yorum silme (soft delete)
**Auth:** Required (own comment or admin)
**Response:** Success message
**Kullanım:** Yorum silme

---

### ⚡ **Reaction Endpoints** (`/api/v1/reactions`)

#### `POST /api/v1/reactions`

**Amaç:** Tepki ekleme (emoji, gif, memoji)
**Auth:** Required
**Query Params:**

- `reaction_type`: emoji, gif, memoji
- `reaction_value`: Tepki değeri
- `series_id` OR `chapter_id` OR `comment_id`: Hedef entity
  **Response:** Reaction data
  **Kullanım:** Seri/bölüm/yoruma tepki verme

#### `DELETE /api/v1/reactions`

**Amaç:** Tepki kaldırma
**Auth:** Required
**Query Params:** series_id OR chapter_id OR comment_id
**Response:** Success message
**Kullanım:** Tepki kaldırma

#### `GET /api/v1/reactions`

**Amaç:** Tepkileri görüntüleme (public, cached)
**Auth:** Optional
**Query Params:** series_id OR chapter_id OR comment_id
**Response:** Reaction summary (grouped by value)
**Kullanım:** Tepki istatistikleri

---

### 📖 **Reading Endpoints** (`/api/v1/reading`)

#### `POST /api/v1/reading/history`

**Amaç:** Okuma geçmişi güncelleme
**Auth:** Required
**Query Params:**

- `chapter_id`: Bölüm ID
- `translation_id`: Çeviri ID (optional)
- `last_page`: Son okunan sayfa
  **Response:** Updated history
  **Kullanım:** Okuma ilerlemesini kaydetme

#### `GET /api/v1/reading/history`

**Amaç:** Okuma geçmişi listesi (cached)
**Auth:** Required
**Query Params:** skip, limit
**Response:** Reading history list
**Kullanım:** Okuma geçmişini görüntüleme

#### `POST /api/v1/bookmarks`

**Amaç:** Favori ekleme
**Auth:** Required
**Query Params:**

- `series_id`: Seri ID
- `notes`: Notlar (optional)
  **Response:** Bookmark data
  **Kullanım:** Seriyi favorilere ekleme

#### `DELETE /api/v1/bookmarks/{series_id}`

**Amaç:** Favori kaldırma
**Auth:** Required
**Response:** Success message
**Kullanım:** Favoriden çıkarma

#### `GET /api/v1/bookmarks`

**Amaç:** Favori listesi (cached)
**Auth:** Required
**Query Params:** skip, limit
**Response:** Bookmark list
**Kullanım:** Favorileri görüntüleme

#### `POST /api/v1/ratings`

**Amaç:** Seri veya bölüme puan verme
**Auth:** Required
**Query Params:**

- `series_id` OR `chapter_id`: Hedef entity (exactly one required)
- `rating`: 1-5 arası puan (required)
- `review`: İnceleme metni (optional)
  **Response:**

```json
{
  "rating": 5,
  "series_id": 1,
  "chapter_id": null
}
```

**Kullanım:** Seri/bölüme puan verme
**Özellik:**

- Mevcut puan varsa günceller
- Seri/chapter ortalama puanını otomatik günceller
- Rating count'u günceller
  **Cache Invalidation:** Series/chapter cache temizlenir

---

### 💳 **Subscription Endpoints** (`/api/v1/subscription`)

#### `GET /api/v1/subscription`

**Amaç:** Kullanıcının abonelik bilgisi
**Auth:** Required
**Response:** Subscription details
**Kullanım:** Abonelik durumu görüntüleme

#### `POST /api/v1/subscription/upgrade`

**Amaç:** Abonelik yükseltme
**Auth:** Required
**Query Params:** plan_type (free, basic, premium)
**Response:** Updated subscription
**Kullanım:** Premium'a geçiş

#### `POST /api/v1/subscription/payment`

**Amaç:** Extra bölüm ödemesi (basit ödeme kaydı)
**Auth:** Required
**Request:**

```json
{
  "chapter_count": 5,
  "payment_method": "stripe"
}
```

**Response:** PaymentResponse (payment record)
**Kullanım:** Ekstra bölüm satın alma (basit kayıt)
**Not:** Gerçek ödeme için `/api/v1/payments/create-intent` kullanın

#### `POST /api/v1/payments/create-intent`

**Amaç:** Stripe payment intent oluşturma (gerçek ödeme)
**Auth:** Required
**Request:** PaymentRequest schema
**Response:**

```json
{
  "payment_id": 1,
  "client_secret": "pi_xxx_secret_yyy",
  "payment_intent_id": "pi_xxx",
  "amount": 2.5,
  "chapter_count": 5
}
```

**Kullanım:** Stripe ile gerçek ödeme başlatma
**Özellik:** Frontend'de Stripe Elements ile ödeme tamamlama için client_secret döner

---

### 💰 **Payment Endpoints** (`/api/v1/payments`)

#### `POST /api/v1/payments/create-intent`

**Amaç:** Stripe payment intent oluşturma
**Auth:** Required
**Request:** PaymentRequest schema
**Response:** Payment intent (client_secret)
**Kullanım:** Ödeme başlatma

#### `POST /api/v1/payments/confirm`

**Amaç:** Ödeme onaylama
**Auth:** Required
**Query Params:** payment_intent_id
**Response:** Confirmed payment
**Kullanım:** Ödeme tamamlama

#### `POST /api/v1/payments/webhook`

**Amaç:** Stripe webhook handler
**Auth:** None (Stripe signature)
**Request:** Stripe webhook event
**Response:** Success
**Kullanım:** Stripe event handling

---

### 🔔 **Notification Endpoints** (`/api/v1/notifications`)

#### `GET /api/v1/notifications`

**Amaç:** Bildirim listesi
**Auth:** Required
**Query Params:**

- `skip`, `limit`: Pagination
- `unread_only`: Sadece okunmamışlar
  **Response:** Notification list
  **Kullanım:** Bildirimleri görüntüleme

#### `PUT /api/v1/notifications/{notification_id}/read`

**Amaç:** Bildirimi okundu işaretleme
**Auth:** Required
**Response:** Success message
**Kullanım:** Bildirim okundu

#### `PUT /api/v1/notifications/read-all`

**Amaç:** Tüm bildirimleri okundu işaretleme
**Auth:** Required
**Response:** Success message
**Kullanım:** Toplu okundu işaretleme

#### `GET /api/v1/notifications/unread-count`

**Amaç:** Okunmamış bildirim sayısı
**Auth:** Required
**Response:** Unread count
**Kullanım:** Badge sayısı

---

### 👤 **User Endpoints** (`/api/v1/users`)

#### `GET /api/v1/profile`

**Amaç:** Kullanıcı profil bilgisi
**Auth:** Required
**Response:** User profile
**Kullanım:** Profil görüntüleme

#### `PUT /api/v1/profile`

**Amaç:** Profil güncelleme
**Auth:** Required
**Request:** UpdateUserRequest schema
**Response:** Updated profile
**Kullanım:** Profil düzenleme

#### `POST /api/v1/change-password`

**Amaç:** Şifre değiştirme
**Auth:** Required
**Request:** ChangePasswordRequest schema
**Response:** Success message
**Kullanım:** Şifre değiştirme

---

### 🌍 **Public Endpoints** (`/api/v1/public`)

#### `GET /api/v1/public/series`

**Amaç:** Seri listesi (no auth required, cached)
**Auth:** None
**Query Params:** skip, limit, search, genre, status, sort
**Response:** Series list
**Kullanım:** Guest kullanıcı seri listesi

#### `GET /api/v1/public/series/{series_id}`

**Amaç:** Seri detay sayfası (no auth required)
**Auth:** None
**Response:** Series details with chapters, ratings
**Kullanım:** Guest kullanıcı seri detayı

#### `GET /api/v1/public/chapters/{chapter_id}`

**Amaç:** Bölüm detay (no auth required)
**Auth:** None
**Response:** Chapter details, available translations
**Kullanım:** Guest kullanıcı bölüm detayı

#### `GET /api/v1/public/chapters/{chapter_id}/read/{translation_id}`

**Amaç:** Bölüm okuma - sayfa listesi ve URL'leri (no auth required)
**Auth:** None
**Query Params:**

- `page`: Mevcut sayfa numarası (optional, default: 1)
  **Response:**

```json
{
  "chapter_id": 5,
  "translation_id": 10,
  "current_page": 1,
  "total_pages": 20,
  "pages": [
    {
      "page_number": 1,
      "url": "/api/v1/files/Eleceed/en_to_tr/chapter_0005/page_001.jpg"
    },
    ...
  ],
  "source_lang": "en",
  "target_lang": "tr"
}
```

**Kullanım:** Guest kullanıcı bölüm okuma
**Özellik:** View count otomatik artırılır

#### `GET /api/v1/public/comments`

**Amaç:** Yorum listesi (no auth required, cached)
**Auth:** None
**Query Params:** series_id, chapter_id, skip, limit
**Response:** Comment list
**Kullanım:** Guest kullanıcı yorum görüntüleme

---

### 📁 **File Endpoints** (`/api/v1/files`)

#### `GET /api/v1/files/{series_name}/{source_lang}_to_{target_lang}/chapter_{chapter_number:04d}/page_{page_number:03d}.jpg`

**Amaç:** Çevrilmiş sayfa görseli servisi (public, auth optional)
**Auth:** Optional
**Path Params:**

- `series_name`: Seri adı (URL-safe)
- `source_lang`: Kaynak dil kodu (en, ko, ja, vb.)
- `target_lang`: Hedef dil kodu (tr, es, fr, vb.)
- `chapter_number`: Bölüm numarası (4 haneli, zero-padded: 0001, 0002, ...)
- `page_number`: Sayfa numarası (3 haneli, zero-padded: 001, 002, ...)
  **Response:** JPEG image file (binary)
  **Content-Type:** `image/jpeg`
  **Kullanım:** Sayfa görseli görüntüleme
  **Örnek URL:** `/api/v1/files/Eleceed/en_to_tr/chapter_0005/page_001.jpg`

#### `GET /api/v1/files/{series_name}/chapters`

**Amaç:** Seriye ait bölüm listesi (public, auth optional)
**Auth:** Optional
**Query Params:** source_lang, target_lang
**Response:** Chapter list
**Kullanım:** Bölüm listesi

---

### 📊 **Job Endpoints** (`/api/v1/jobs`)

#### `GET /api/v1/jobs`

**Amaç:** Çeviri iş geçmişi
**Auth:** Required
**Query Params:**

- `skip`, `limit`: Pagination
- `status_filter`: Status filtresi
  **Response:** Job history list
  **Kullanım:** İş geçmişini görüntüleme

#### `DELETE /api/v1/jobs/{task_id}`

**Amaç:** İş kaydını silme
**Auth:** Required
**Response:** Success message
**Kullanım:** İş kaydı silme

---

### ⚙️ **Admin Endpoints** (`/api/v1/admin`)

#### `DELETE /api/v1/admin/cache/clear`

**Amaç:** Tüm cache'i temizleme (Admin only)
**Auth:** Required (Admin)
**Response:** Success message
**Kullanım:** Cache temizleme

#### `GET /api/v1/admin/stats`

**Amaç:** Sistem istatistikleri (Admin only)
**Auth:** Required (Admin)
**Response:** System statistics
**Kullanım:** Sistem durumu

---

### 📝 **Log Endpoints** (`/api/v1/admin/logs`)

#### `GET /api/v1/admin/logs`

**Amaç:** Uygulama loglarını görüntüleme (Admin only)
**Auth:** Required (Admin)
**Query Params:**

- `level`: Log level (INFO, WARNING, ERROR, DEBUG) - optional
- `module`: Module filtresi (partial match) - optional
- `request_id`: Request ID filtresi (exact match) - optional
- `user_id`: User ID filtresi - optional
- `start_date`: Başlangıç tarihi (ISO format) - optional
- `end_date`: Bitiş tarihi (ISO format) - optional
- `skip`: Pagination offset (default: 0)
- `limit`: Page size (default: 100, max: 1000)
  **Response:**

```json
{
  "logs": [
    {
      "id": 1,
      "level": "ERROR",
      "message": "Translation failed",
      "module": "TranslationManager",
      "request_id": "abc123",
      "user_id": 5,
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "extra_data": { "error": "Connection timeout" },
      "created_at": "2026-01-06T10:30:00Z"
    }
  ],
  "total": 1500,
  "skip": 0,
  "limit": 100
}
```

**Kullanım:** Log görüntüleme, hata takibi, debugging
**Özellik:** Tüm loglar veritabanında saklanır (Log model)

#### `GET /api/v1/admin/logs/stats`

**Amaç:** Log istatistikleri (Admin only)
**Auth:** Required (Admin)
**Query Params:**

- `start_date`: Başlangıç tarihi (ISO format) - optional
- `end_date`: Bitiş tarihi (ISO format) - optional
  **Response:**

```json
{
  "total": 1500,
  "by_level": {
    "INFO": 1200,
    "WARNING": 200,
    "ERROR": 100,
    "DEBUG": 0
  },
  "top_modules": {
    "TranslationManager": 500,
    "LoggingMiddleware": 300,
    "OCRService": 200
  },
  "error_rate": 6.67,
  "errors": 100
}
```

**Kullanım:** Log analizi, sistem sağlığı izleme, hata oranı takibi

---

### 🔄 **Cache Endpoints** (`/api/v1/cache`)

#### `POST /api/v1/cache/refresh`

**Amaç:** Manuel cache yenileme (belirli entity'ler için)
**Auth:** Required
**Query Params:**

- `series_id`: Seri cache'ini temizle (optional)
- `chapter_id`: Bölüm cache'ini temizle (optional)
- `comment_id`: Yorum cache'ini temizle (optional)
  **Response:**

```json
{
  "invalidated": ["series_1", "chapter_5", "comments"]
}
```

**Kullanım:** Cache manuel yenileme (yeni içerik görünmüyorsa)
**Not:** Hiçbir parametre verilmezse tüm cache temizlenir

#### `GET /api/v1/cache/status`

**Amaç:** Cache durumu ve istatistikleri
**Auth:** Required
**Response:**

```json
{
  "status": "enabled",
  "total_keys": 1250,
  "memory_used": "45.2MB",
  "memory_peak": "50.1MB"
}
```

**Kullanım:** Cache durumu kontrolü, Redis memory kullanımı
**Not:** Redis bağlantısı yoksa `"status": "disabled"` döner

---

### 🔍 **Discovery Endpoints** (`/api/v1/`)

#### `GET /api/v1/series/trending`

**Amaç:** Trending seriler (günlük/haftalık/aylık)
**Auth:** None
**Query Params:**

- `skip`: Pagination offset
- `limit`: Page size (max 50)
- `period`: "day", "week", "month"
  **Response:** Trending series list
  **Kullanım:** Ana sayfa trending bölümü
  **Cache:** 1 saat

#### `GET /api/v1/series/featured`

**Amaç:** Öne çıkan seriler (admin-selected)
**Auth:** None
**Query Params:**

- `skip`: Pagination offset
- `limit`: Page size (max 50)
  **Response:** Featured series list
  **Kullanım:** Ana sayfa featured bölümü
  **Cache:** 30 dakika

#### `GET /api/v1/series/recommendations`

**Amaç:** Kullanıcıya özel öneriler
**Auth:** Optional (guest için popüler seriler)
**Query Params:**

- `skip`: Pagination offset
- `limit`: Page size (max 50)
  **Response:** Recommended series list
  **Kullanım:** Kişiselleştirilmiş öneriler
  **Özellikler:**
- ✅ Authenticated users: Okuma geçmişi ve bookmark'lara göre öneriler
- ✅ Guest users: Popüler seriler
  **Cache:** 30 dakika (kullanıcı bazlı)

#### `GET /api/v1/series/popular`

**Amaç:** Popüler seriler (görüntülenme sayısına göre)
**Auth:** None
**Query Params:**

- `skip`: Pagination offset
- `limit`: Page size (max 50)
- `period`: "day", "week", "month", "all"
  **Response:** Popular series list
  **Kullanım:** Popüler seriler sayfası
  **Cache:** 1 saat

#### `GET /api/v1/series/newest`

**Amaç:** En yeni seriler
**Auth:** None
**Query Params:**

- `skip`: Pagination offset
- `limit`: Page size (max 50)
  **Response:** Newest series list
  **Kullanım:** Yeni seriler sayfası
  **Cache:** 10 dakika

#### `GET /api/v1/tags`

**Amaç:** Tüm mevcut tag'leri listele
**Auth:** None
**Response:**

```json
{
  "all_tags": ["action", "comedy", "system", "return", ...],
  "genre_tags": ["action", "comedy", "drama", ...],
  "webtoon_specific_tags": ["system", "return", "rebirth", ...],
  "total_count": 200
}
```

**Kullanım:** Tag seçimi için dropdown/liste
**Cache:** 24 saat

#### `GET /api/v1/tags/validate`

**Amaç:** Tag isimlerini validate et
**Auth:** None
**Query Params:**

- `tag_names`: List of tag names (comma-separated veya query array)
  **Response:**

```json
{
  "valid_tags": [
    { "original": "comedy", "normalized": "comedy", "valid": true },
    { "original": "aksiyon", "normalized": "action", "valid": true }
  ],
  "invalid_tags": [{ "original": "invalid-tag", "valid": false }],
  "total_valid": 2,
  "total_invalid": 1
}
```

**Kullanım:** Tag validation, frontend'de tag seçimi

---

### ⚙️ **Site Settings Endpoints** (`/api/v1/settings`)

#### `GET /api/v1/settings`

**Amaç:** Site ayarları (public)
**Auth:** None
**Response:** Site settings
**Kullanım:** Site konfigürasyonu görüntüleme

#### `PUT /api/v1/settings`

**Amaç:** Site ayarları güncelleme (Admin only)
**Auth:** Required (Admin)
**Request:** SiteSettingsUpdate schema
**Response:** Updated settings
**Kullanım:** Site ayarları düzenleme

---

### 📈 **Metrics Endpoints** (`/api/v1/metrics`)

#### `GET /api/v1/metrics/summary`

**Amaç:** Uygulama metrikleri özeti
**Auth:** Required
**Response:**

```json
{
  "api": {
    "requests": 1234,
    "errors": 5,
    "timing": { "avg": 0.15, "p95": 0.5 }
  },
  "translation": {
    "started": 100,
    "completed": 95,
    "failed": 5,
    "timing": { "avg": 45.2, "p95": 120.0 }
  }
}
```

**Kullanım:** Performans izleme, sistem sağlığı kontrolü
**Cache:** Yok (real-time data)

---

## 🎯 **ENDPOINT ÖZETİ**

### Public Endpoints (No Auth)

- ✅ Series list/detail
- ✅ Chapter list/detail
- ✅ Chapter reading
- ✅ Comments viewing
- ✅ Reactions viewing
- ✅ File serving
- ✅ Site settings

### Authenticated Endpoints (Auth Required)

- ✅ Translation requests
- ✅ Comment create/update/delete
- ✅ Reaction add/remove
- ✅ Reading history
- ✅ Bookmarks
- ✅ Ratings
- ✅ Notifications
- ✅ User profile
- ✅ Subscription management

### Admin Endpoints (Admin Required)

- ✅ Cache management
- ✅ System statistics
- ✅ Log viewing
- ✅ Site settings update
- ✅ Manual chapter upload
- ✅ Page editing/deletion/reordering
- ✅ Bulk chapter publish/unpublish
- ✅ Series/Chapter/Translation management (CRUD)

**TOPLAM: 75+ endpoint** 🎉

### 📊 **Endpoint İstatistikleri**

| Kategori       | Endpoint Sayısı | Auth Gereksinimi          |
| -------------- | --------------- | ------------------------- |
| Authentication | 3               | Mixed                     |
| Translation    | 5               | Required                  |
| Series         | 6               | Mixed (Public + Admin)    |
| Comments       | 6               | Mixed (Public + Required) |
| Reactions      | 3               | Mixed (Public + Required) |
| Reading        | 6               | Required                  |
| Subscription   | 3               | Required                  |
| Payments       | 3               | Required                  |
| Notifications  | 4               | Required                  |
| Users          | 3               | Required                  |
| Public         | 5               | None                      |
| Files          | 2               | Optional                  |
| Jobs           | 2               | Required                  |
| Admin          | 2               | Admin                     |
| Logs           | 2               | Admin                     |
| Cache          | 2               | Required                  |
| Site Settings  | 2               | Mixed (Public + Admin)    |
| Metrics        | 1               | Required                  |
| **TOPLAM**     | **60+**         | -                         |

---

## ✅ **SONUÇ**

Bu dokümantasyon, Webtoon AI Translator projesinin tüm teknik detaylarını, kullanılan teknolojileri, dosya yapısını ve tüm endpoint'lerin açıklamalarını içermektedir.

**Proje %100 tamamlanmış ve production-ready durumda!** 🚀

---

**Son Güncelleme:** January 6, 2026

---

## 🆕 **YENİ EKLENEN ÖZELLİKLER (Son Güncelleme)**

### 🏷️ **Tag & Category Sistemi**

#### WebtoonTag Enum

- **200+ Tag**: Tüm webtoon tag'leri enum olarak tanımlanmış
- **Kategoriler:**
  - **Genre Tags** (14): action, adventure, comedy, drama, fantasy, horror, mystery, romance, sci-fi, slice-of-life, sports, supernatural, thriller, western
  - **Webtoon-Specific Tags**: system, return, rebirth, regression, transmigration-novel, villainess, duke-of-the-north, magic, mana, cultivation, martial-arts, leveling, game-elements, status-window, skills, evolution, dungeon, tower, gate, portal, isekai, alternate-world, parallel-world
  - **Character Tags**: strong-female-lead, op-main-character, weak-to-strong, reincarnation, transmigration, time-travel
  - **Relationship Tags**: harem, reverse-harem, love-triangle, yaoi, yuri, bl, gl, shoujo, shounen, seinen, josei
  - **Story Tags**: revenge, redemption, betrayal, academy, guild, adventurer, merchant, noble, royalty
  - **Modern Tags**: ceo, contract-marriage, arranged-marriage, enemies-to-lovers, secret-identity
  - **Power Tags**: overpowered, cheat, unique-skill, legendary
  - Ve daha fazlası...

#### Tag Validation

- Tag'ler enum'dan validate edilir
- Geçersiz tag'ler otomatik atlanır
- Tag isimleri normalize edilir (büyük/küçük harf, özel karakterler)

#### Endpoint'ler

- `GET /api/v1/tags` - Tüm tag'leri listele
- `GET /api/v1/tags/validate?tag_names=comedy,action` - Tag'leri validate et

---

### 📚 **Seri Yönetimi ve Otomatik Çeviri Akışı**

#### SeriesManager Service

**Lokasyon:** `app/services/series_manager.py`

**Özellikler:**

- `create_or_get_series()`: Seri bulma/oluşturma
  - Aynı isimde seri varsa: Mevcut seriyi kullanır (yeni oluşturmaz)
  - Aynı isimde seri yoksa: Yeni seri oluşturulur
  - Normalize edilmiş isim eşleştirme (büyük/küçük harf, özel karakterler)
- `create_or_update_chapter()`: Chapter oluşturma/güncelleme
  - Chapter number çakışması yönetimi
  - `replace_existing=True`: Aynı chapter number varsa yenisiyle değiştir
  - `replace_existing=False`: Aynı chapter number varsa eski korunur
- `handle_chapter_conflict()`: Translation çakışma çözümü
  - Aynı dil çifti varsa: Eski translation dosyaları silinir, yenisiyle değiştirilir
  - Aynı dil çifti yoksa: Yeni translation oluşturulur

#### Otomatik Seri Oluşturma

**Lokasyon:** `app/operations/translation_publisher.py`

**Akış:**

1. Çeviri tamamlandığında `publish_translation_on_completion()` çağrılır
2. Seri kontrolü: Aynı isimde seri varsa kullanılır, yoksa oluşturulur
3. Chapter kontrolü: Chapter number URL'den otomatik çıkarılır, çakışma yönetilir
4. Translation kontrolü: Aynı translation varsa yenisiyle değiştirilir
5. Hata yönetimi: Transaction rollback ve dosya temizleme

**Detaylı akış:** `DOC/SERIES_CREATION_FLOW.md` dosyasına bakın.

---

### 🔍 **Discovery Özellikleri**

#### Yeni Endpoint'ler

- `GET /api/v1/series/trending` - Trending seriler (günlük/haftalık/aylık)
- `GET /api/v1/series/featured` - Öne çıkan seriler (admin-selected)
- `GET /api/v1/series/recommendations` - Kullanıcıya özel öneriler
- `GET /api/v1/series/popular` - Popüler seriler
- `GET /api/v1/series/newest` - En yeni seriler
- `GET /api/v1/tags` - Tüm tag'leri listele
- `GET /api/v1/tags/validate` - Tag validation

**Özellikler:**

- ✅ Redis cache desteği (TTL: 600-3600 saniye)
- ✅ Kullanıcı bazlı öneriler (okuma geçmişi ve bookmark'lara göre)
- ✅ Guest kullanıcılar için popüler seriler

---

### 🔧 **Admin Content Management**

#### Yeni Endpoint'ler

- `POST /api/v1/admin/chapters/upload` - Manuel bölüm yükleme
- `PUT /api/v1/admin/chapters/{chapter_id}/pages/{page_number}` - Sayfa düzenleme
- `DELETE /api/v1/admin/chapters/{chapter_id}/pages/{page_number}` - Sayfa silme
- `POST /api/v1/admin/chapters/{chapter_id}/pages/reorder` - Sayfa sıralama
- `POST /api/v1/admin/series/{series_id}/chapters/bulk-publish` - Toplu yayınlama

**Özellikler:**

- ✅ Çeviri yaptırmadan direkt dosya yükleme
- ✅ Sayfa seviyesinde düzenleme
- ✅ Toplu işlemler
- ✅ Otomatik cache invalidation

---

### 🔒 **Güvenlik ve Veri Bütünlüğü İyileştirmeleri**

1. ✅ **Transaction Rollback**: Herhangi bir hata durumunda tüm değişiklikler geri alınır
2. ✅ **Dosya Temizleme**: Hata durumunda kaydedilen dosyalar otomatik silinir
3. ✅ **Veri Kaybı Önleme**: Chapter/translation çakışmalarında eski veriler korunur veya güvenli şekilde değiştirilir
4. ✅ **Validation**: Tag'ler enum'dan validate edilir, geçersiz tag'ler atlanır
5. ✅ **Seri Description Zorunluluğu**: Seri oluştururken description zorunludur

---

### 📖 **Glossary System (Sözlük Sistemi)**

#### Genel Bakış

Her seri için özel bir sözlük (glossary) tutulur. Bu sözlük, karakter isimleri, özel terimler ve tutarlı çeviri gerektiren kelimeleri içerir.

#### Modeller

**Lokasyon:** `app/models/dictionary.py`

- **SeriesDictionary**: Seri bazlı sözlük (her dil çifti için ayrı)

  - `series_id`: Seri ID
  - `source_lang`: Kaynak dil
  - `target_lang`: Hedef dil
  - `max_entries`: Maksimum entry sayısı (default: 1000)

- **DictionaryEntry**: Sözlük girişi
  - `original_name`: Orijinal isim/terim
  - `translated_name`: Çevrilmiş isim/terim
  - `usage_count`: Kullanım sayısı
  - `is_proper_noun`: Özel isim mi? (auto/yes/no)
  - `last_used_at`: Son kullanım tarihi

#### DictionaryService

**Lokasyon:** `app/services/dictionary_service.py`

**Metodlar:**

- `get_or_create_dictionary()`: Sözlük bul/oluştur
- `lookup_name()`: İsim arama
- `add_or_update_entry()`: Entry ekle/güncelle
- `apply_dictionary()`: Sözlüğü metinlere uygula (FREE translation için)
- `cleanup_dictionary()`: En az kullanılan entry'leri temizle

#### AI Translation Entegrasyonu

**Lokasyon:** `app/services/ai_translator.py`

- Glossary, AI translation'ın **system prompt'una** eklenir
- AI'ya "Bu kelimeleri görürsen kesinlikle karşılığındaki gibi çevir" talimatı verilir
- Örnek prompt:
  ```
  CRITICAL GLOSSARY RULES (MANDATORY):
  The following terms MUST be translated EXACTLY as specified:
    - "Hyung" → "Abi"
    - "Dungeon" → "Zindan"
    - "Hunter" → "Avcı"
  ```

#### Otomatik Özel İsim Tespiti

- NER (Named Entity Recognition) servisi ile otomatik tespit
- Yeni özel isimler sözlüğe eklenir
- Kullanım sayısına göre otomatik temizleme

---

### 🧩 **Smart Chunking (Akıllı Bölümleme)**

#### Genel Bakış

Büyük metinler için token limitini aşmamak için akıllı bölümleme algoritması.

**Lokasyon:** `app/services/ai_translator.py` → `_translate_with_chunking()`

#### Algoritma

1. **Token Tahmini**: ~4 karakter = 1 token
2. **Güvenli Limit**: 100,000 token (GPT-4o-mini için 128k max, ama 100k güvenli)
3. **Chunk Boyutu**: ~80,000 karakter (~20,000 token)
4. **Context Preservation**: Her chunk'a önceki chunk'ın özeti eklenir

#### Özellikler

- ✅ Otomatik chunk boyutu hesaplama
- ✅ Context koruma (önceki chunk'ın özeti)
- ✅ Hata toleransı (bir chunk başarısız olsa bile diğerleri devam eder)
- ✅ Otomatik padding/truncation (uzunluk uyumsuzluğu durumunda)

#### Kullanım

Otomatik olarak devreye girer. Metin boyutu 100k token'ı aşarsa smart chunking kullanılır.

---

### 🖼️ **WebP Format Support**

#### Genel Bakış

Resimler WebP formatında kaydedilir, boyut %50 azalır.

**Lokasyon:** `app/services/image_processor.py`, `app/services/file_manager.py`

#### Özellikler

- ✅ **WebP Format**: Varsayılan format (quality: 90, method: 6)
- ✅ **JPEG Fallback**: WebP desteklenmiyorsa otomatik JPEG'e geçer
- ✅ **Format Detection**: Magic bytes ile otomatik format algılama
- ✅ **Configurable**: `USE_WEBP` ve `IMAGE_QUALITY` config'den ayarlanabilir

#### Config

```python
# app/core/config.py
USE_WEBP: bool = True  # WebP kullan
IMAGE_QUALITY: int = 90  # 0-100 arası kalite
```

#### Dosya Yapısı

- WebP: `page_001.webp`
- JPEG: `page_001.jpg` (fallback)
- PNG: `page_001.png` (eğer PNG kaydedilirse)

---

### 🔐 **Cache/Lock Mechanism**

#### Genel Bakış

Aynı bölüm için aynı anda 2 çeviri başlatılmasını engeller.

**Lokasyon:** `app/services/cache_service.py`

#### Özellikler

- ✅ **Redis Lock**: SET NX EX ile atomic lock
- ✅ **Lock Timeout**: 1 saat (3600 saniye)
- ✅ **Otomatik Release**: Task tamamlandığında veya hata olduğunda
- ✅ **Duplicate Prevention**: Aynı chapter_url + target_lang + translate_type için lock

#### Metodlar

- `acquire_translation_lock()`: Lock al
- `release_translation_lock()`: Lock bırak
- `is_translation_locked()`: Lock durumunu kontrol et

#### Kullanım

**Lokasyon:** `app/api/v1/endpoints/translate.py`

1. Translation başlatılmadan önce lock kontrolü
2. Lock alınamazsa: 409 Conflict döner veya mevcut task ID döner
3. Task tamamlandığında: Lock otomatik release edilir
4. Hata durumunda: Lock otomatik release edilir

---

### 📝 **Text Wrapping Improvements**

#### Genel Bakış

Metinlerin balonlara düzgün sığması için geliştirilmiş text wrapping.

**Lokasyon:** `app/services/image_processor.py` → `_wrap_text()`

#### Özellikler

- ✅ **textwrap Kütüphanesi**: Python'un textwrap modülü kullanılır
- ✅ **Doğru Genişlik Hesaplama**: Font metrikleri ile gerçek genişlik hesaplanır
- ✅ **Uzun Kelime Desteği**: `break_long_words=True` ile uzun kelimeler bölünür
- ✅ **Hiphen Desteği**: `break_on_hyphens=True` ile tire işaretlerinde bölünür
- ✅ **Karakter Bazlı Bölme**: Gerekirse karakter bazlı bölme yapılır

#### Algoritma

1. `textwrap.wrap()` ile metin satırlara bölünür
2. Her satırın genişliği font metrikleri ile kontrol edilir
3. Satır çok genişse karakter bazlı bölme yapılır
4. Sonuç: Balona sığan, okunabilir metin

---

### ⚡ **Event Loop Blocking Düzeltmesi**

#### Genel Bakış

CPU-intensive işlemler (OCR, Image Processing) event loop'u bloklamaması için `run_in_executor` ile thread pool'a taşındı.

**Lokasyon:** `app/services/image_processor.py`, `app/services/ocr_service.py`

#### Özellikler

- ✅ **Async Wrappers**: `process_image_async()`, `detect_text_blocks_async()` eklendi
- ✅ **Thread Pool**: `ThreadPoolExecutor` ile ayrı thread'lerde çalışır
- ✅ **Event Loop Protection**: FastAPI event loop bloklanmaz
- ✅ **Celery Compatibility**: Celery task'lar zaten ayrı process'lerde, ama best practice için eklendi

#### Kullanım

```python
# Async context'te kullanım
processed_image = await image_processor.process_image_async(
    image_bytes, blocks, translations
)

# Sync context'te (Celery) kullanım
processed_image = image_processor.process_image(
    image_bytes, blocks, translations
)
```

---

### 🔧 **Dinamik Scraper Configuration**

#### Genel Bakış

CSS selector'lar artık veritabanından yönetilebilir. Site yapısı değiştiğinde kod değiştirmeden admin panelinden güncellenebilir.

**Lokasyon:** `app/models/scraper_config.py`, `app/services/scraper_config_service.py`

#### ScraperConfig Modeli

- `site_name`: Site adı (webtoons.com, asuracomic.net)
- `selectors`: CSS selector'lar (JSON formatında)
  ```json
  {
    "container": "div.reading-content",
    "image": "img",
    "image_attr": "data-src",
    "title": "h1.chapter-title",
    "next_chapter": "a.next-chapter"
  }
  ```
- `fallback_selectors`: Yedek selector'lar
- `config`: Ekstra config (user-agent, headers, timeout, vb.)
- `is_active`: Aktif/pasif durumu
- `last_updated`: Son güncelleme tarihi
- `updated_by`: Güncelleyen admin

#### ScraperConfigService

**Metodlar:**

- `get_config()`: Site için config getir
- `get_default_selectors()`: Default selector'lar (fallback)
- `get_selectors()`: DB'den veya default'tan selector'ları getir
- `update_config()`: Config güncelle (admin tarafından)

#### Kullanım

```python
# Scraper içinde kullanım
selectors = ScraperConfigService.get_selectors(db, "webtoons.com")
container = soup.select_one(selectors["container"])
images = container.find_all(selectors["image"])
```

#### Avantajlar

- ✅ **Kod Değiştirmeden Güncelleme**: Site yapısı değiştiğinde sadece DB'den güncelle
- ✅ **Fallback Sistemi**: DB'de yoksa default selector'lar kullanılır
- ✅ **Admin Yönetimi**: Admin panelinden kolayca güncellenebilir
- ✅ **Version Control**: `last_updated` ve `updated_by` ile takip

---

### ✏️ **Human-in-the-Loop Editor**

#### Genel Bakış

AI çevirilerini manuel olarak inceleyip düzenleyebilme özelliği.

**Lokasyon:** `app/api/v1/endpoints/translation_editor.py`

#### Endpoint'ler

**1. Çeviri İnceleme**

```
GET /api/v1/translation/{task_id}/review?page_index={page}
```

- Orijinal metin ve AI çevirisini yan yana gösterir
- Sayfa ve blok bazında inceleme
- Onaylama/reddetme/düzenleme seçenekleri

**2. Çeviri Onaylama/Reddetme/Düzenleme**

```
POST /api/v1/translation/review
```

Request Body:

```json
{
  "task_id": "uuid",
  "page_index": 0,
  "block_index": 0,
  "action": "approve|reject|edit",
  "edited_text": "Düzenlenmiş metin" // action=edit için gerekli
}
```

**3. Manuel Düzenleme**

```
POST /api/v1/translation/edit
```

Request Body:

```json
{
  "task_id": "uuid",
  "page_index": 0,
  "block_index": 0,
  "original_text": "Orijinal metin",
  "translated_text": "Düzenlenmiş çeviri"
}
```

#### Özellikler

- ✅ **Yan Yana Görüntüleme**: Orijinal ve çeviri yan yana
- ✅ **Blok Bazında Düzenleme**: Her metin bloğu ayrı ayrı düzenlenebilir
- ✅ **Onaylama Sistemi**: Onaylanan çeviriler finalize edilir
- ✅ **Re-processing**: Düzenlenen metinlerle resim yeniden işlenir

#### Kullanım Senaryosu

1. Kullanıcı çeviri başlatır
2. Çeviri tamamlandığında review endpoint'ine gider
3. Orijinal ve çeviriyi yan yana görür
4. Hatalı çevirileri düzenler
5. Onaylar ve finalize eder

---

### ☁️ **CDN Integration (S3/MinIO)**

#### Genel Bakış

İşlenmiş resimler CDN'e (S3/MinIO) yüklenir, disk kullanımı azalır ve hız artar.

**Lokasyon:** `app/services/cdn_service.py`, `app/services/file_manager.py`

#### CDNService

**Desteklenen CDN'ler:**

- **AWS S3**: Tam S3 desteği
- **MinIO**: Self-hosted S3-compatible storage

#### Özellikler

- ✅ **Otomatik Upload**: Resimler CDN'e otomatik yüklenir
- ✅ **Local Fallback**: CDN başarısız olursa local'e kaydedilir
- ✅ **URL Generation**: CDN URL'leri otomatik oluşturulur
- ✅ **Image Deletion**: CDN'den resim silme desteği
- ✅ **Configurable**: `.env`'den açılıp kapatılabilir

#### Config Ayarları

```env
# CDN Settings
CDN_ENABLED=true
CDN_TYPE=s3  # or "minio"

# AWS S3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=webtoon-images

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET_NAME=webtoon-images
```

#### Kullanım

**FileManager** otomatik olarak CDN'e yükler:

```python
# FileManager.save_chapter() içinde otomatik
if self.cdn_service.cdn_enabled:
    cdn_url = self.cdn_service.upload_image(
        image_bytes=page_bytes,
        object_key=object_key,
        content_type="image/webp"
    )
```

#### Avantajlar

- ✅ **Disk Tasarrufu**: Sunucu diskinde yer kaplamaz
- ✅ **Hız**: CDN'den daha hızlı servis edilir
- ✅ **Ölçeklenebilirlik**: Trafik artışında sorun olmaz
- ✅ **Yedekleme**: CDN'de otomatik yedekleme

---

## 🆕 **YENİ EKLENEN ÖZELLİKLER (Son Güncelleme)**

### 🏷️ **Tag & Category Sistemi**

#### WebtoonTag Enum

- **200+ Tag**: Tüm webtoon tag'leri enum olarak tanımlanmış
- **Kategoriler:**
  - **Genre Tags** (14): action, adventure, comedy, drama, fantasy, horror, mystery, romance, sci-fi, slice-of-life, sports, supernatural, thriller, western
  - **Webtoon-Specific Tags**: system, return, rebirth, regression, transmigration-novel, villainess, duke-of-the-north, magic, mana, cultivation, martial-arts, leveling, game-elements, status-window, skills, evolution, dungeon, tower, gate, portal, isekai, alternate-world, parallel-world
  - **Character Tags**: strong-female-lead, op-main-character, weak-to-strong, reincarnation, transmigration, time-travel
  - **Relationship Tags**: harem, reverse-harem, love-triangle, yaoi, yuri, bl, gl, shoujo, shounen, seinen, josei
  - **Story Tags**: revenge, redemption, betrayal, academy, guild, adventurer, merchant, noble, royalty
  - **Modern Tags**: ceo, contract-marriage, arranged-marriage, enemies-to-lovers, secret-identity
  - **Power Tags**: overpowered, cheat, unique-skill, legendary
  - Ve daha fazlası...

#### Tag Validation

- Tag'ler enum'dan validate edilir
- Geçersiz tag'ler otomatik atlanır
- Tag isimleri normalize edilir (büyük/küçük harf, özel karakterler)

#### Endpoint'ler

- `GET /api/v1/tags` - Tüm tag'leri listele
- `GET /api/v1/tags/validate?tag_names=comedy,action` - Tag'leri validate et

---

### 📚 **Seri Yönetimi ve Otomatik Çeviri Akışı**

#### SeriesManager Service

**Lokasyon:** `app/services/series_manager.py`

**Özellikler:**

- `create_or_get_series()`: Seri bulma/oluşturma
  - Aynı isimde seri varsa: Mevcut seriyi kullanır (yeni oluşturmaz)
  - Aynı isimde seri yoksa: Yeni seri oluşturulur
  - Normalize edilmiş isim eşleştirme (büyük/küçük harf, özel karakterler)
- `create_or_update_chapter()`: Chapter oluşturma/güncelleme
  - Chapter number çakışması yönetimi
  - `replace_existing=True`: Aynı chapter number varsa yenisiyle değiştir
  - `replace_existing=False`: Aynı chapter number varsa eski korunur
- `handle_chapter_conflict()`: Translation çakışma çözümü
  - Aynı dil çifti varsa: Eski translation dosyaları silinir, yenisiyle değiştirilir
  - Aynı dil çifti yoksa: Yeni translation oluşturulur

#### Otomatik Seri Oluşturma

**Lokasyon:** `app/operations/translation_publisher.py`

**Akış:**

1. Çeviri tamamlandığında `publish_translation_on_completion()` çağrılır
2. Seri kontrolü: Aynı isimde seri varsa kullanılır, yoksa oluşturulur
3. Chapter kontrolü: Chapter number URL'den otomatik çıkarılır, çakışma yönetilir
4. Translation kontrolü: Aynı translation varsa yenisiyle değiştirilir
5. Hata yönetimi: Transaction rollback ve dosya temizleme

**Detaylı akış:** `DOC/SERIES_CREATION_FLOW.md` dosyasına bakın.

---

### 🔍 **Discovery Özellikleri**

#### Yeni Endpoint'ler

- `GET /api/v1/series/trending` - Trending seriler (günlük/haftalık/aylık)
- `GET /api/v1/series/featured` - Öne çıkan seriler (admin-selected)
- `GET /api/v1/series/recommendations` - Kullanıcıya özel öneriler
- `GET /api/v1/series/popular` - Popüler seriler
- `GET /api/v1/series/newest` - En yeni seriler
- `GET /api/v1/tags` - Tüm tag'leri listele
- `GET /api/v1/tags/validate` - Tag validation

**Özellikler:**

- ✅ Redis cache desteği (TTL: 600-3600 saniye)
- ✅ Kullanıcı bazlı öneriler (okuma geçmişi ve bookmark'lara göre)
- ✅ Guest kullanıcılar için popüler seriler

---

### 🔧 **Admin Content Management**

#### Yeni Endpoint'ler

- `POST /api/v1/admin/chapters/upload` - Manuel bölüm yükleme
- `PUT /api/v1/admin/chapters/{chapter_id}/pages/{page_number}` - Sayfa düzenleme
- `DELETE /api/v1/admin/chapters/{chapter_id}/pages/{page_number}` - Sayfa silme
- `POST /api/v1/admin/chapters/{chapter_id}/pages/reorder` - Sayfa sıralama
- `POST /api/v1/admin/series/{series_id}/chapters/bulk-publish` - Toplu yayınlama

**Özellikler:**

- ✅ Çeviri yaptırmadan direkt dosya yükleme
- ✅ Sayfa seviyesinde düzenleme
- ✅ Toplu işlemler
- ✅ Otomatik cache invalidation

---

### 🔒 **Güvenlik ve Veri Bütünlüğü İyileştirmeleri**

1. ✅ **Transaction Rollback**: Herhangi bir hata durumunda tüm değişiklikler geri alınır
2. ✅ **Dosya Temizleme**: Hata durumunda kaydedilen dosyalar otomatik silinir
3. ✅ **Veri Kaybı Önleme**: Chapter/translation çakışmalarında eski veriler korunur veya güvenli şekilde değiştirilir
4. ✅ **Validation**: Tag'ler enum'dan validate edilir, geçersiz tag'ler atlanır
5. ✅ **Seri Description Zorunluluğu**: Seri oluştururken description zorunludur

---

## 🔐 **Cloudflare Bypass ve Scraper İyileştirmeleri (2026 Güncellemesi)**

### Cloudflare Koruması Sorunu

**Sorun:** AsuraScans.com.tr ve benzeri siteler Cloudflare koruması kullanıyor, bu da normal HTTP isteklerinde 403 Forbidden hatasına neden oluyor.

**Çözüm:** undetected-chromedriver kütüphanesi kullanılarak Cloudflare challenge'ı bypass edildi.

### Uygulanan Değişiklikler

#### 1. AsuraScraper Güncellemesi

**Lokasyon:** pp/services/scrapers/asura_scraper.py

**Değişiklikler:**
- ✅ undetected-chromedriver import edildi
- ✅ Selenium driver ile sayfa yükleme eklendi
- ✅ Cloudflare challenge için 10 saniye bekleme eklendi
- ✅ Referer header eklendi (görüntü indirmeleri için)
- ✅ close() metodu eklendi (driver kapatma)

**Önemli Notlar:**
- ⚠️ **Non-headless mod gerekli:** Cloudflare bypass için non-headless mod kullanılmalı (headless modda Cloudflare challenge geçilemiyor)
- ⚠️ **Bekleme süresi:** Her sayfa yüklemesi için 10 saniye bekleme var (Cloudflare challenge'ın tamamlanması için)
- ⚠️ **Driver yönetimi:** Driver her scraper instance'ı için bir kez oluşturuluyor, close() metodunda kapatılıyor

#### 2. BaseScraper Güncellemesi

**Lokasyon:** pp/services/scrapers/base_scraper.py

**Değişiklikler:**
- ✅ download_image metoduna 
eferer parametresi eklendi
- ✅ Görüntü indirmelerinde referer header gönderiliyor (CDN koruması için)

#### 3. Batch Translation Manager Güncellemesi

**Lokasyon:** pp/operations/batch_translation_manager.py

**Değişiklikler:**
- ✅ 	ask.get() yerine AsyncResult polling kullanıldı
- ✅ Celery best practices'e uygun hale getirildi
- ✅ "Never call result.get() within a task!" hatası çözüldü

**Neden:** Celery task içinde başka bir task'ın result'unu .get() ile almak yasak. Bunun yerine AsyncResult ile polling yapılmalı.

### Yeni Bağımlılıklar

**requirements.txt:**
`python
undetected-chromedriver>=3.5.5  # Cloudflare bypass için
`

### Test Sonuçları

- ✅ Manuel scraper testi başarılı (4 görüntü indirildi)
- ✅ Cloudflare challenge geçildi
- ✅ Batch translation task PROCESSING durumuna geçti
- ⏳ Task tamamlanması bekleniyor (uzun sürebilir - her bölüm için ~10 saniye Cloudflare bekleme)

### Kullanım

**Normal kullanım:** Değişiklik yok, scraper otomatik olarak Cloudflare bypass yapar.

**Manuel test:**
`python
from app.services.scraper_service import ScraperService
import asyncio

async def test():
    scraper = ScraperService()
    images = await scraper.fetch_chapter_images("https://asurascans.com.tr/manga/martial-peak/bolum-20/")
    print(f"Found {len(images)} images")
    await scraper.close()

asyncio.run(test())
`

### Bilinen Sınırlamalar

1. **Non-headless mod:** Production ortamında GUI gerektirir (headless modda çalışmaz)
2. **Bekleme süresi:** Her sayfa yüklemesi için 10 saniye bekleme var (optimize edilebilir)
3. **Memory kullanımı:** Selenium driver memory kullanır, close() ile kapatılmalı

### Gelecek İyileştirmeler

- [ ] Headless mod desteği (Cloudflare bypass için alternatif yöntemler)
- [ ] Bekleme süresi optimizasyonu (dinamik bekleme)
- [ ] Driver pool yönetimi (birden fazla scraper instance için)

