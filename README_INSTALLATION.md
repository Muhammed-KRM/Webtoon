# 📦 Kurulum Rehberi

## Hızlı Kurulum

### 1. İlk Kurulum (Tüm Paketler)
```bash
SETUP.bat
```
Bu komut:
- ✅ Temel paketleri kurar
- ✅ Opsiyonel paketleri kurar (Hugging Face, Argos, spaCy)
- ✅ spaCy modellerini indirir
- ✅ Gerekli klasörleri oluşturur

### 2. Sadece Opsiyonel Paketler
Eğer temel kurulum yapıldıysa ve sadece opsiyonel paketleri eklemek istiyorsanız:
```bash
INSTALL_OPTIONAL.bat
```

### 3. Başlatma
```bash
START.bat
```

---

## Kurulu Paketler

### Zorunlu Paketler (Her Zaman)
- FastAPI, Celery, Redis
- OpenAI (çeviri için)
- Google Translate (ücretsiz çeviri için)
- OCR, Image Processing

### Opsiyonel Paketler (Daha İyi Performans İçin)

#### 1. Hugging Face Transformers + PyTorch
- **Ne işe yarar:** Offline AI çevirisi (ücretsiz, kaliteli)
- **Kurulum:** `pip install transformers torch`
- **Boyut:** ~2GB (ilk kullanımda model indirilir)
- **Avantaj:** OpenAI'ye yakın kalite, ücretsiz, offline

#### 2. Argos Translate
- **Ne işe yarar:** Offline ücretsiz çeviri
- **Kurulum:** `pip install argostranslate`
- **Boyut:** ~200-500MB (dil çiftine göre)
- **Avantaj:** Hızlı, offline, ücretsiz

#### 3. spaCy
- **Ne işe yarar:** Gelişmiş özel isim tespiti (NER)
- **Kurulum:** `pip install spacy` + `python -m spacy download en_core_web_sm`
- **Boyut:** ~50-100MB (model başına)
- **Avantaj:** Regex'den çok daha doğru özel isim tespiti

---

## Otomatik Fallback Sistemi

Sistem otomatik olarak en iyi çeviri servisini seçer:

### Çeviri Servisleri (Öncelik Sırası)
1. **Hugging Face** (varsa) → Offline, ücretsiz, kaliteli
2. **Argos Translate** (varsa) → Offline, ücretsiz, hızlı
3. **Google Translate** (her zaman) → Online, ücretsiz
4. **DeepL** (varsa) → Online, API key gerekebilir

### NER Servisleri (Öncelik Sırası)
1. **spaCy** (varsa) → %85-95 doğruluk
2. **Regex** (her zaman) → %60-70 doğruluk

---

## Manuel Kurulum

### Sadece Hugging Face
```bash
venv\Scripts\activate
pip install transformers torch
```

### Sadece Argos Translate
```bash
venv\Scripts\activate
pip install argostranslate
```

### Sadece spaCy
```bash
venv\Scripts\activate
pip install spacy
python -m spacy download en_core_web_sm
```

---

## Kontrol

Kurulumun başarılı olup olmadığını kontrol etmek için:

```python
# Python'da test edin
python -c "import transformers; print('Hugging Face: OK')"
python -c "import argostranslate; print('Argos: OK')"
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy: OK')"
```

---

## Sorun Giderme

### "spaCy model bulunamadı"
```bash
python -m spacy download en_core_web_sm
```

### "Argos Translate paketleri yok"
İlk kullanımda otomatik indirilir. Manuel:
```python
import argostranslate.package
argostranslate.package.update_package_index()
```

### "Hugging Face model yüklenemiyor"
İnternet bağlantısı gerekli (ilk kullanımda model indirilir).

---

## Notlar

- Tüm opsiyonel paketler **fallback** mekanizması ile çalışır
- Bir paket yoksa sistem otomatik olarak alternatifini kullanır
- Hiçbir paket zorunlu değil (Google Translate her zaman çalışır)

