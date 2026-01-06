# 📚 Seri Ekleme ve Otomatik Çeviri Akışı

## 🎯 Genel Bakış

Sistemde seri ekleme **iki farklı yöntemle** yapılabilir:

1. **Manuel Seri Oluşturma** (Admin)
2. **Otomatik Seri Oluşturma** (Çeviri sırasında)

---

## 1️⃣ Manuel Seri Oluşturma (Admin)

### Endpoint
```
POST /api/v1/series
```

### Akış
1. Admin, seri bilgilerini (title, description, tags, category) gönderir
2. `SeriesManager.create_or_get_series()` çağrılır
3. Sistem aynı isimde seri var mı kontrol eder:
   - **Varsa**: Mevcut seriyi döner, metadata güncellenir (yeni seri oluşturulmaz)
   - **Yoksa**: Yeni seri oluşturulur
4. Tag'ler eklenir (enum'dan validate edilir)
5. Seri veritabanına kaydedilir

### Örnek Request
```json
{
  "title": "My Webtoon",
  "description": "A great webtoon series",
  "category_id": 1,
  "tags": ["comedy", "action", "system", "return"]
}
```

### Önemli Notlar
- ✅ Aynı isimde seri varsa **yeni seri oluşturulmaz**
- ✅ Mevcut serinin metadata'sı güncellenir (boş alanlar doldurulur)
- ✅ Tag'ler enum'dan validate edilir
- ✅ Description **zorunludur**

---

## 2️⃣ Otomatik Seri Oluşturma (Çeviri Sırasında)

### Endpoint
```
POST /api/v1/translate/start
```

### Akış

#### Adım 1: Çeviri İsteği
```json
{
  "chapter_url": "https://webtoons.com/...",
  "target_lang": "tr",
  "source_lang": "en",
  "series_name": "My Webtoon",  // ← ÖNEMLİ: Seri adı burada verilir
  "translate_type": 1
}
```

#### Adım 2: Çeviri İşlemi
1. Celery task başlatılır (`process_chapter_task`)
2. Resimler indirilir, OCR yapılır, çeviri yapılır
3. Çeviri tamamlandığında `publish_translation_on_completion()` çağrılır

#### Adım 3: Otomatik Yayınlama
`publish_translation_on_completion()` fonksiyonu:

1. **Seri Kontrolü**:
   ```python
   series, is_new_series = SeriesManager.create_or_get_series(
       title=series_name,
       description="Translated series: {series_name}",  # Default description
       ...
   )
   ```
   - Aynı isimde seri **varsa**: Mevcut seriyi kullanır
   - Aynı isimde seri **yoksa**: Yeni seri oluşturur

2. **Chapter Kontrolü**:
   ```python
   chapter, is_new_chapter = SeriesManager.create_or_update_chapter(
       series_id=series.id,
       chapter_number=extracted_from_url,  # URL'den otomatik çıkarılır
       replace_existing=True  # Aynı chapter number varsa yenisiyle değiştir
   )
   ```
   - Chapter number URL'den otomatik çıkarılır (episode-123, chapter-123, vb.)
   - Aynı chapter number **varsa**: `replace_existing=True` ise yenisiyle değiştirilir
   - Aynı chapter number **yoksa**: Yeni chapter oluşturulur

3. **Translation Kontrolü**:
   ```python
   translation = SeriesManager.handle_chapter_conflict(
       chapter=chapter,
       source_lang="en",
       target_lang="tr",
       replace_existing=True  # Aynı translation varsa yenisiyle değiştir
   )
   ```
   - Aynı dil çifti (en->tr) **varsa**: Eski translation dosyaları silinir, yenisiyle değiştirilir
   - Aynı dil çifti **yoksa**: Yeni translation oluşturulur

4. **Hata Yönetimi**:
   - Herhangi bir hata olursa: **Transaction rollback**
   - Kaydedilen dosyalar **otomatik silinir**
   - Veri kaybı **önlenir**

---

## 🔄 Senaryolar ve Çözümler

### Senaryo 1: İlk Kez Seri Ekleme
**Durum**: "My Webtoon" adında seri yok
**Sonuç**: 
- ✅ Yeni seri oluşturulur
- ✅ Chapter 1 eklenir
- ✅ Translation oluşturulur

### Senaryo 2: Aynı Seriye Devam Etme
**Durum**: "My Webtoon" serisi var, Chapter 1-10 mevcut
**İşlem**: Chapter 11-20 çevirisi yapılıyor
**Sonuç**:
- ✅ Mevcut seri kullanılır (yeni seri oluşturulmaz)
- ✅ Chapter 11-20 eklenir
- ✅ Translation'lar oluşturulur

### Senaryo 3: Chapter Çakışması
**Durum**: "My Webtoon" serisinde Chapter 1-10 var
**İşlem**: Chapter 5-15 çevirisi yapılıyor
**Sonuç**:
- ✅ Mevcut seri kullanılır
- ✅ Chapter 5-10: **Yenisiyle değiştirilir** (`replace_existing=True`)
- ✅ Chapter 11-15: **Yeni eklenir**

### Senaryo 4: Translation Çakışması
**Durum**: Chapter 5'in en->tr translation'ı var
**İşlem**: Aynı chapter'ın tekrar çevirisi yapılıyor
**Sonuç**:
- ✅ Eski translation dosyaları **silinir**
- ✅ Yeni translation **kaydedilir**
- ✅ Database'de translation **güncellenir**

---

## 📋 Özet

### Seri Oluşturma Mantığı
```
series_name verildi mi?
├─ EVET
│  ├─ Aynı isimde seri var mı?
│  │  ├─ VAR → Mevcut seriyi kullan
│  │  └─ YOK → Yeni seri oluştur
│  └─ Çeviri tamamlandığında otomatik yayınla
└─ HAYIR
   └─ Sadece çeviri yap, yayınlama
```

### Chapter Çakışma Çözümü
```
Chapter number çıkar
├─ Aynı chapter number var mı?
│  ├─ VAR
│  │  ├─ replace_existing=True → Yenisiyle değiştir
│  │  └─ replace_existing=False → Atla (eski korunur)
│  └─ YOK → Yeni chapter oluştur
```

### Translation Çakışma Çözümü
```
Translation oluştur
├─ Aynı dil çifti var mı?
│  ├─ VAR
│  │  ├─ replace_existing=True → Eski dosyaları sil, yenisiyle değiştir
│  │  └─ replace_existing=False → Eski korunur
│  └─ YOK → Yeni translation oluştur
```

---

## ⚙️ Ayarlar

### `replace_existing_chapters` Parametresi
- **True** (Varsayılan): Aynı chapter/translation varsa yenisiyle değiştir
- **False**: Aynı chapter/translation varsa eski korunur, yeni atlanır

### Otomatik Yayınlama
- `series_name` verilirse: Çeviri tamamlandığında **otomatik yayınlanır**
- `series_name` verilmezse: Çeviri yapılır ama **yayınlanmaz** (manuel yayınlama gerekir)

---

## 🔒 Güvenlik ve Veri Bütünlüğü

1. ✅ **Transaction Rollback**: Herhangi bir hata durumunda tüm değişiklikler geri alınır
2. ✅ **Dosya Temizleme**: Hata durumunda kaydedilen dosyalar otomatik silinir
3. ✅ **Veri Kaybı Önleme**: Chapter/translation çakışmalarında eski veriler korunur veya güvenli şekilde değiştirilir
4. ✅ **Validation**: Tag'ler enum'dan validate edilir, geçersiz tag'ler atlanır

