# Task Timeout Sorunu ve Çözümü

## 🔴 SORUN

**Belirtiler:**
- `process_chapter_task` 20 dakika (1200 saniye) timeout alıyor
- Celery worker log'larında `process_chapter_task` için hiçbir log yok
- Task başlamıyor veya bir yerde takılıyor

**Neden:**
1. `undetected-chromedriver` non-headless modda çalışıyor
2. Celery worker GUI açamaz (headless ortam)
3. Chrome driver başlatılamıyor veya takılıyor
4. Task başlamadan önce takılıyor

## ✅ ÇÖZÜM

### 1. Task Başlangıç Log'ları Eklendi
**Dosya:** `app/operations/translation_manager.py`

```python
logger.info(f"[TASK START] process_chapter_task started for: {chapter_url}")
logger.info(f"[TASK START] Parameters: target_lang={target_lang}, source_lang={source_lang}, mode={mode}, translate_type={translate_type}")
logger.info("[TASK START] Initializing services...")
```

**Amaç:** Task'ın başlayıp başlamadığını görmek için

### 2. Chrome Driver Headless Mod Kontrolü
**Dosya:** `app/services/scrapers/asura_scraper.py`

**Değişiklik:**
- Celery worker ortamında headless mod kullanılıyor
- Ana process'te non-headless mod kullanılıyor (Cloudflare bypass için)
- Ortam değişkeni kontrolü eklendi

```python
# For Celery worker, we need headless mode
import os
if os.getenv('CELERY_WORKER', '').lower() == 'true' or 'celery' in os.getenv('_', '').lower():
    # Running in Celery worker - use headless
    options.add_argument('--headless=new')
    logger.info("[SCRAPER] Using headless mode (Celery worker detected)")
else:
    # Running in main process - try non-headless for Cloudflare
    logger.info("[SCRAPER] Using non-headless mode (main process)")
```

### 3. Daha Fazla Log Eklendi
**Dosya:** `app/services/scrapers/asura_scraper.py`

**Eklenen log'lar:**
- Chrome driver başlatma
- URL fetch
- Sayfa yükleme bekleme
- HTML alma

**Amaç:** Task'ın nerede takıldığını görmek için

## 🧪 TEST

**Yapılacaklar:**
1. Celery worker'ı yeniden başlat
2. Yeni bir batch translation testi yap
3. Log'ları kontrol et:
   - `[TASK START]` log'ları görünüyor mu?
   - `[SCRAPER]` log'ları görünüyor mu?
   - Task nerede takılıyor?

## 📝 BEKLENEN SONUÇ

**Başarılı durumda:**
- `[TASK START]` log'ları görünecek
- `[SCRAPER]` log'ları görünecek
- Task 20 dakika içinde tamamlanacak
- Dosyalar storage'a kaydedilecek

**Hala sorun varsa:**
- Log'lara bakarak nerede takıldığını bul
- Gerekirse timeout'u artır
- Veya alternatif scraper kullan

## 🔧 EK DÜZELTMELER

### Timeout Artırma
Eğer hala timeout alınıyorsa, `batch_translation_manager.py` içindeki timeout'u artırabiliriz:

```python
# Şu an: 1200 saniye (20 dakika)
# Artırılabilir: 1800 saniye (30 dakika)
```

### Alternatif Scraper
Eğer headless mod Cloudflare'i bypass edemezse, alternatif scraper kullanılabilir:
- `cloudscraper` (tekrar denenebilir)
- `requests-html`
- `playwright`

## 📊 DURUM

**Şu an:**
- ✅ Log'lar eklendi
- ✅ Headless mod kontrolü eklendi
- ⏳ Test edilmeli

**Sonraki adım:**
- Celery worker'ı yeniden başlat
- Test yap
- Log'ları kontrol et

