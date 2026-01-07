# URL ve Timeout Düzeltmeleri

## 🔍 TESPİT EDİLEN SORUNLAR

### 1. URL Yanlış Oluşturuluyor ❌

**Sorun:**
- Base URL: `https://asurascans.com.tr/manga/martial-peak/bolum-20/`
- Oluşturulan URL: `https://asurascans.com.tr/manga/martial-peak/20/` ❌
- Doğru olmalı: `https://asurascans.com.tr/manga/martial-peak/bolum-21/` ✅

**Neden:**
- `_detect_pattern` fonksiyonu `bolum-20` pattern'ini buluyor
- Ama `replace` kullanırken sadece pattern'i değiştiriyor, sayıyı doğru replace etmiyor

**Çözüm:**
- Regex kullanarak pattern içindeki sayıyı doğru şekilde replace ediyoruz
- `bolum-20` → `bolum-21` şeklinde doğru replace yapılıyor

### 2. Timeout Çok Kısa ❌

**Sorun:**
- Mevcut timeout: 600 saniye (10 dakika)
- Her bölüm için:
  - ~10 saniye Cloudflare bekleme
  - ~30-60 saniye çeviri süresi
  - Toplam: ~40-70 saniye per bölüm
- 11 bölüm için minimum: 440-770 saniye (7-13 dakika)
- Ama bazı bölümler daha uzun sürebilir

**Çözüm:**
- Timeout 1200 saniyeye (20 dakika) çıkarıldı
- Her 60 saniyede bir progress log eklendi

## 🔧 UYGULANAN DEĞİŞİKLİKLER

### 1. `app/services/url_generator.py`

**Değişiklik:**
```python
# Önceki kod (yanlış):
url = base_url.replace(url_pattern, str(chapter_num))

# Yeni kod (doğru):
pattern_with_number = re.sub(r'\d+', str(chapter_num), url_pattern)
url = base_url.replace(url_pattern, pattern_with_number)
```

**Sonuç:**
- `bolum-20` → `bolum-21` ✅
- `episode-364` → `episode-365` ✅
- `chapter-10` → `chapter-11` ✅

### 2. `app/operations/batch_translation_manager.py`

**Değişiklik:**
```python
# Önceki kod:
max_wait = 600  # 10 minutes

# Yeni kod:
max_wait = 1200  # 20 minutes
# + Progress logging every 60 seconds
```

**Sonuç:**
- Her bölüm için 20 dakika timeout
- Her 60 saniyede bir progress log
- Daha uzun çeviriler için yeterli süre

## 🧪 TEST

**Test URL:**
```
Base: https://asurascans.com.tr/manga/martial-peak/bolum-20/
Chapters: [20, 21, 22]
```

**Beklenen URL'ler:**
```
https://asurascans.com.tr/manga/martial-peak/bolum-20/
https://asurascans.com.tr/manga/martial-peak/bolum-21/
https://asurascans.com.tr/manga/martial-peak/bolum-22/
```

## 📝 SONUÇ

- ✅ URL generator düzeltildi
- ✅ Timeout süresi artırıldı
- ✅ Progress logging eklendi
- ⏳ Test edilmeli

