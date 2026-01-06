# 🚀 Webtoon AI Translator - Geliştirme Planı ve Yol Haritası

## 📋 İçindekiler
1. [Proje Durumu](#proje-durumu)
2. [Eksik Kodlar ve Özellikler](#eksik-kodlar-ve-özellikler)
3. [Kurulum Gereksinimleri](#kurulum-gereksinimleri)
4. [Adım Adım Geliştirme Planı](#adım-adım-geliştirme-planı)
5. [Test Stratejisi](#test-stratejisi)
6. [Deployment Planı](#deployment-planı)
7. [Sık Sorulan Sorular](#sık-sorulan-sorular)

---

## 📊 Proje Durumu

### ✅ Hazır Olanlar (Mevcut Kodlar)

#### 1. **Mimari Yapı (Layered Architecture)**
- ✅ FastAPI temel kurulumu
- ✅ Katmanlı mimari (API → Operations → Services)
- ✅ BaseResponse yapısı (Ranker tarzı)
- ✅ Database modelleri (User, TranslationJob)
- ✅ Dependency Injection yapısı

#### 2. **Core Modüller**
- ✅ `app/core/config.py` - Ayarlar yönetimi
- ✅ `app/db/session.py` - Database bağlantısı
- ✅ `app/db/base.py` - SQLAlchemy Base

#### 3. **Servisler (Temel İskelet)**
- ✅ `app/services/ocr_service.py` - OCR servisi (EasyOCR entegrasyonu)
- ✅ `app/services/ai_translator.py` - Context-aware çeviri servisi
- ✅ `app/services/image_processor.py` - Görüntü işleme servisi
- ⚠️ `app/services/scraper_service.py` - **MOCK (Gerçek implementasyon eksik)**

#### 4. **Operations**
- ✅ `app/operations/translation_manager.py` - Celery task yapısı

#### 5. **API Endpoints**
- ⚠️ `app/api/v1/endpoints/auth.py` - **Kısaltılmış (Tam implementasyon eksik)**
- ✅ `app/api/v1/endpoints/translate.py` - Çeviri endpoint'leri

---

## ❌ Eksik Kodlar ve Özellikler

### 🔴 Kritik Eksikler (Projenin Çalışması İçin Zorunlu)

#### 1. **Gerçek Web Scraper Implementasyonu**
**Dosya:** `app/services/scraper_service.py`

**Mevcut Durum:** Sadece mock/boş fonksiyonlar var.

**Yapılması Gerekenler:**
- Hedef webtoon sitesinin HTML yapısını analiz etme
- BeautifulSoup veya Selenium ile sayfa parsing
- Bölüm listesini çıkarma
- Her sayfadaki resim URL'lerini bulma
- Resimleri indirme ve byte formatına çevirme
- Rate limiting ve retry mekanizması
- Farklı webtoon siteleri için adapter pattern

**Örnek Yapı:**
```python
class ScraperService:
    async def analyze_url(self, url: str) -> ChapterInfo:
        """URL'yi analiz eder, bölüm bilgilerini döner"""
        pass
    
    async def fetch_chapter_pages(self, chapter_url: str) -> List[bytes]:
        """Bölümdeki tüm sayfaları indirir"""
        pass
    
    async def download_image(self, img_url: str) -> bytes:
        """Tek bir resmi indirir"""
        pass
```

#### 2. **Akıllı Metin Sığdırma (Text Wrapping)**
**Dosya:** `app/services/image_processor.py`

**Mevcut Durum:** Metin dümdüz yazılıyor, balon dışına taşabilir.

**Yapılması Gerekenler:**
- Metin uzunluğunu balon genişliğiyle karşılaştırma
- Otomatik font boyutu küçültme algoritması
- Çok satırlı metin desteği (textwrap)
- Metni balonun ortasına hizalama (center alignment)
- Minimum font boyutu sınırı
- Türkçe karakter desteği

**Algoritma Özeti:**
1. Başlangıç font boyutu: 20px
2. Metin genişliği > Balon genişliği ise font'u küçült
3. Hala sığmıyorsa çok satıra böl (textwrap)
4. Her satırı ortala ve dikey olarak dağıt

#### 3. **Türkçe Font Desteği**
**Dosya:** `app/services/image_processor.py`

**Mevcut Durum:** Sistem fontu kullanılıyor (Türkçe karakterlerde sorun olabilir).

**Yapılması Gerekenler:**
- Proje klasörüne uygun font dosyası ekleme (`fonts/` klasörü)
- Font dosyası yolu yapılandırması
- Fallback mekanizması (font bulunamazsa sistem fontu)

**Önerilen Fontlar:**
- Komika Axis (Çizgi roman tarzı)
- Lalezar (Türkçe karakter desteği güçlü)
- Roboto (Modern, okunabilir)

#### 4. **Tam Auth Implementasyonu**
**Dosya:** `app/api/v1/endpoints/auth.py`

**Mevcut Durum:** Sadece iskelet var.

**Yapılması Gerekenler:**
- Kullanıcı kayıt (register) endpoint'i
- Şifre hash'leme (bcrypt)
- JWT token üretme
- Token doğrulama middleware'i
- Kullanıcı bilgisi getirme (GET /auth/me)
- Şifre sıfırlama (opsiyonel)

#### 5. **Security Middleware**
**Dosya:** `app/core/security.py`

**Mevcut Durum:** Dosya eksik.

**Yapılması Gerekenler:**
- JWT token oluşturma fonksiyonu
- Token doğrulama fonksiyonu
- Password hash'leme fonksiyonları
- `get_current_user` dependency
- Role-based access control (RBAC)

### 🟡 Önemli Eksikler (Performans ve Kullanıcı Deneyimi)

#### 6. **Gelişmiş In-painting**
**Dosya:** `app/services/image_processor.py`

**Mevcut Durum:** Basit OpenCV inpaint kullanılıyor.

**İyileştirmeler:**
- Karmaşık arka planlar için Lama Cleaner entegrasyonu
- Mask genişletme algoritması (padding)
- Çoklu deneme (farklı algoritmalar)

#### 7. **Caching Mekanizması**
**Dosya:** Yeni dosya: `app/services/cache_service.py`

**Yapılması Gerekenler:**
- Redis ile işlenmiş resimleri cache'leme
- Cache key stratejisi (chapter_url + hash)
- Cache invalidation
- Disk cache (S3/CDN entegrasyonu için hazırlık)

#### 8. **Error Handling ve Logging**
**Dosya:** `app/core/logging.py` (yeni)

**Yapılması Gerekenler:**
- Structured logging (Loguru)
- Error tracking (Sentry entegrasyonu hazırlığı)
- Retry mekanizmaları
- Graceful degradation

#### 9. **Rate Limiting**
**Dosya:** `app/core/rate_limit.py` (yeni)

**Yapılması Gerekenler:**
- Kullanıcı başına istek limiti
- API key bazlı limitler
- Redis ile distributed rate limiting

#### 10. **Webtoon Site Adapter Pattern**
**Dosya:** `app/services/scrapers/` (yeni klasör)

**Yapılması Gerekenler:**
- Base scraper interface
- Her site için ayrı adapter (Webtoons.com, AsuraScans, vb.)
- Factory pattern ile adapter seçimi

### 🟢 İyileştirmeler (Nice-to-Have)

#### 11. **Admin Panel Endpoints**
**Dosya:** `app/api/v1/endpoints/admin.py` (yeni)

**Yapılması Gerekenler:**
- Cache temizleme endpoint'i
- Sistem logları görüntüleme
- Kullanıcı yönetimi
- İstatistikler

#### 12. **Webtoon Metadata**
**Dosya:** `app/models/webtoon.py` (yeni)

**Yapılması Gerekenler:**
- Webtoon serisi bilgileri
- Bölüm metadata
- Favoriler/Bookmark sistemi

#### 13. **Quality Settings**
**Dosya:** `app/schemas/translation_dto.py` (güncelleme)

**Yapılması Gerekenler:**
- High/Fast quality seçenekleri
- Overlay/Clean mode seçenekleri
- Custom font boyutu

---

## 🛠️ Kurulum Gereksinimleri

### 1. **Python Ortamı**
```bash
# Python 3.10+ gereklidir
python --version

# Virtual environment oluştur
python -m venv venv

# Aktif et (Windows)
venv\Scripts\activate

# Aktif et (Linux/Mac)
source venv/bin/activate
```

### 2. **PostgreSQL Kurulumu**
```bash
# Windows: PostgreSQL installer indir ve kur
# https://www.postgresql.org/download/windows/

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Database oluştur
createdb webtoon_db

# Veya psql ile:
psql -U postgres
CREATE DATABASE webtoon_db;
```

### 3. **Redis Kurulumu**

**Windows:**
- **Seçenek 1:** Memurai (Redis Windows portu) - https://www.memurai.com/
- **Seçenek 2:** Docker Desktop ile Redis container
```bash
docker run -d -p 6379:6379 redis:latest
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Mac (Homebrew)
brew install redis

# Başlat
redis-server
```

### 4. **Python Paketleri**
```bash
pip install -r requirements.txt
```

### 5. **OCR Model Dosyaları**
EasyOCR ilk çalıştırmada otomatik indirir, ancak manuel indirmek için:
```python
import easyocr
reader = easyocr.Reader(['en', 'tr'], gpu=False)  # İlk çalıştırmada indirir
```

### 6. **Font Dosyaları**
```bash
# fonts/ klasörü oluştur
mkdir fonts

# Font dosyalarını indir ve koy:
# - KomikaAxis.ttf
# - Lalezar-Regular.ttf
# - Roboto-Regular.ttf
```

### 7. **Environment Variables**
`.env` dosyasını oluştur ve doldur:
```env
PROJECT_NAME="Webtoon AI Translator"
SECRET_KEY="güvenli-bir-secret-key-buraya"
DATABASE_URL="postgresql://user:password@localhost/webtoon_db"
REDIS_URL="redis://localhost:6379/0"
OPENAI_API_KEY="sk-..."
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 📅 Adım Adım Geliştirme Planı

### **Faz 1: Temel Altyapı (1-2 Hafta)**

#### Hafta 1: Core ve Security
- [ ] `app/core/security.py` - JWT ve password hash implementasyonu
- [ ] `app/api/v1/endpoints/auth.py` - Tam auth endpoint'leri
- [ ] `app/core/logging.py` - Logging yapılandırması
- [ ] Database migration sistemi (Alembic)
- [ ] Unit testler (pytest)

#### Hafta 2: Scraper Temeli
- [ ] Hedef webtoon sitesini belirleme
- [ ] Site HTML yapısını analiz etme
- [ ] `app/services/scraper_service.py` - Temel scraper implementasyonu
- [ ] Test verileri ile çalıştırma

### **Faz 2: Çeviri Pipeline (2-3 Hafta)**

#### Hafta 3: OCR ve Çeviri İyileştirmeleri
- [ ] OCR servisini test etme ve optimize etme
- [ ] Context-aware çeviri prompt'larını iyileştirme
- [ ] Çeviri kalitesi testleri
- [ ] Karakter isim tutarlılığı testleri

#### Hafta 4: Görüntü İşleme
- [ ] Text wrapping algoritması implementasyonu
- [ ] Font yönetimi ve Türkçe karakter desteği
- [ ] In-painting iyileştirmeleri
- [ ] Görüntü kalitesi testleri

### **Faz 3: Production Hazırlığı (2 Hafta)**

#### Hafta 5: Optimizasyon
- [ ] Caching mekanizması
- [ ] Rate limiting
- [ ] Error handling iyileştirmeleri
- [ ] Performance profiling

#### Hafta 6: Testing ve Dokümantasyon
- [ ] Integration testler
- [ ] End-to-end testler
- [ ] API dokümantasyonu (Swagger)
- [ ] Kullanıcı kılavuzu

### **Faz 4: İleri Özellikler (Opsiyonel)**

- [ ] Multi-site scraper adapter pattern
- [ ] Admin panel
- [ ] Webhook desteği
- [ ] Batch processing (çoklu bölüm)

---

## 🧪 Test Stratejisi

### 1. **Unit Testler**
**Dosya:** `tests/unit/`

**Test Edilecekler:**
- Service fonksiyonları (OCR, Translation, Image Processing)
- Utility fonksiyonları
- Model validasyonları

**Örnek:**
```python
# tests/unit/test_ocr_service.py
def test_ocr_detects_text():
    service = OCRService()
    result = service.detect_text(test_image_bytes)
    assert len(result) > 0
    assert result[0]['text'] == "Hello"
```

### 2. **Integration Testler**
**Dosya:** `tests/integration/`

**Test Edilecekler:**
- API endpoint'leri
- Database işlemleri
- Celery task'ları

### 3. **End-to-End Testler**
**Dosya:** `tests/e2e/`

**Test Senaryoları:**
1. Kullanıcı kaydı → Giriş → Çeviri başlatma → Sonuç alma
2. Çoklu kullanıcı senaryosu
3. Hata durumları (network error, API limit, vb.)

### 4. **Performance Testleri**
- OCR hızı (sayfa başına süre)
- Çeviri API response time
- Görüntü işleme süresi
- Toplam pipeline süresi

---

## 🚀 Deployment Planı

### **Development Ortamı**
```bash
# 1. Redis başlat
redis-server

# 2. Celery worker başlat
celery -A app.operations.translation_manager.celery_app worker --loglevel=info --pool=solo

# 3. FastAPI başlat
uvicorn main:app --reload
```

### **Production Ortamı**

#### 1. **Server Gereksinimleri**
- Ubuntu 20.04+ veya Windows Server
- Minimum 4GB RAM (8GB önerilir)
- GPU (opsiyonel, OCR hızlandırır)

#### 2. **Docker Deployment (Önerilen)**
```dockerfile
# Dockerfile örneği
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. **Process Manager (PM2 veya Supervisor)**
```bash
# PM2 ile
pm2 start "uvicorn main:app --host 0.0.0.0" --name webtoon-api
pm2 start "celery -A app.operations.translation_manager.celery_app worker" --name webtoon-worker
```

#### 4. **Reverse Proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name api.webtoontranslator.com;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

#### 5. **Monitoring**
- Application logs (Loguru → File/CloudWatch)
- Error tracking (Sentry)
- Performance monitoring (New Relic / Datadog)

---

## ❓ Sık Sorulan Sorular

### **1. Kendi AI Modelimi Eğitmem Gerekiyor mu?**
**Hayır.** Proje hazır modelleri kullanıyor:
- **OCR:** EasyOCR (önceden eğitilmiş)
- **Çeviri:** OpenAI GPT-4o-mini (API)
- **In-painting:** OpenCV algoritması (AI değil, matematiksel)

### **2. Çeviri Tutarlılığı Nasıl Sağlanıyor?**
**Batch Processing** tekniği ile:
1. Tüm bölüm metinleri tek seferde toplanır
2. Tek bir prompt ile GPT'ye gönderilir
3. System prompt'ta "tutarlılık" vurgulanır
4. GPT tüm bağlamı görür, tutarlı çeviri yapar

**Kod Yeri:** `app/services/ai_translator.py` → `translate_batch_context_aware()`

### **3. Görüntü Editlenmesi Nasıl Çalışıyor?**
**In-painting Algoritması:**
1. OCR metin koordinatlarını verir
2. Bu koordinatlar "mask" olarak işaretlenir
3. `cv2.inpaint()` algoritması mask'in etrafındaki pikselleri analiz eder
4. Arka plan dokusunu kopyalayarak mask'i doldurur
5. Temizlenmiş alana Türkçe metin yazılır

**Kod Yeri:** `app/services/image_processor.py` → `process_image()`

### **4. Hangi Webtoon Siteleri Destekleniyor?**
Şu an **hiçbiri** (scraper mock). Hedef site belirlendikten sonra:
- Site HTML yapısı analiz edilir
- Siteye özel scraper adapter yazılır
- Factory pattern ile adapter seçilir

### **5. Windows'ta Celery Nasıl Çalıştırılır?**
Windows'ta Celery için `--pool=solo` parametresi gerekir:
```bash
celery -A app.operations.translation_manager.celery_app worker --loglevel=info --pool=solo
```

Alternatif: Docker container içinde çalıştır.

### **6. Maliyet Tahmini (OpenAI API)**
- GPT-4o-mini: ~$0.15 / 1M input tokens, ~$0.60 / 1M output tokens
- Ortalama bölüm (50 sayfa, 100 balon): ~$0.01-0.05
- Aylık 1000 bölüm: ~$10-50

**Öneri:** Rate limiting ve kullanıcı limitleri koy.

### **7. OCR Hızı Ne Kadar?**
- EasyOCR (CPU): ~2-5 saniye/sayfa
- EasyOCR (GPU): ~0.5-1 saniye/sayfa
- 50 sayfalık bölüm: ~2-4 dakika (CPU), ~30 saniye (GPU)

### **8. Proje Ne Zaman Tamamlanır?**
**Minimum Viable Product (MVP):** 4-6 hafta
- Temel scraper
- OCR + Çeviri + Görüntü işleme
- Basit API

**Production Ready:** 8-10 hafta
- Tüm özellikler
- Testler
- Dokümantasyon
- Deployment

---

## 📝 Sonraki Adımlar

### **Hemen Yapılacaklar:**
1. ✅ Bu dokümanı oku ve anla
2. ⬜ Kurulum gereksinimlerini tamamla (PostgreSQL, Redis, .env)
3. ⬜ Hedef webtoon sitesini belirle
4. ⬜ Test için örnek bir bölüm URL'i hazırla

### **İlk Kod Yazımı:**
1. `app/core/security.py` - JWT implementasyonu
2. `app/api/v1/endpoints/auth.py` - Auth endpoint'leri
3. `app/services/scraper_service.py` - Gerçek scraper (hedef site için)

### **Test ve İyileştirme:**
1. Scraper'ı test et (gerçek URL ile)
2. OCR kalitesini kontrol et
3. Çeviri tutarlılığını test et
4. Görüntü kalitesini değerlendir

---

## 📞 Destek ve Kaynaklar

### **Dokümantasyon:**
- FastAPI: https://fastapi.tiangolo.com/
- Celery: https://docs.celeryproject.org/
- EasyOCR: https://github.com/JaidedAI/EasyOCR
- OpenAI API: https://platform.openai.com/docs/

### **Yardımcı Kütüphaneler:**
- BeautifulSoup4: HTML parsing
- Selenium: JavaScript render gereken siteler için
- Pillow: Görüntü işleme
- OpenCV: Görüntü temizleme

---

**Son Güncelleme:** 2024
**Versiyon:** 1.0.0
**Durum:** Geliştirme Aşamasında

