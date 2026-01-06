# 💰 Webtoon AI Translator - Detaylı Maliyet Analizi

**Son Güncelleme:** 6 Ocak 2026  
**Kaynak:** OpenAI Resmi Fiyatlandırma (2026), Oracle Cloud, VPS Sağlayıcıları

---

## 📊 Özet Tablo

| Bileşen | Teknoloji | Durum | Aylık Maliyet | Notlar |
|---------|-----------|-------|---------------|--------|
| **Backend & Kod** | Python, FastAPI, Celery | ✅ Ücretsiz | **$0** | Açık kaynak |
| **Veritabanı** | PostgreSQL | ✅ Ücretsiz | **$0** | Kendi sunucunda |
| **OCR** | EasyOCR | ✅ Ücretsiz | **$0** | CPU/GPU gücü kullanır |
| **Görüntü İşleme** | OpenCV | ✅ Ücretsiz | **$0** | Açık kaynak |
| **Çeviri AI** | OpenAI GPT-4o-mini | ⚠️ Ücretli | **~$5-20** | Kullanıma bağlı |
| **Sunucu** | VPS / Oracle Cloud | ⚠️ Ücretli/Ücretsiz | **$0-10** | Seçime bağlı |

**Toplam Aylık Maliyet:** **$5-30** (Kullanım ve seçimlere göre)

---

## 🔍 Detaylı Maliyet Analizi

### 1. OpenAI GPT-4o-mini - Çeviri Maliyeti

#### Güncel Fiyatlandırma (2026)
- **Input (Girdi) Token:** $0.15 / 1M tokens
- **Cached Input (Önbelleğe Alınmış Girdi):** $0.075 / 1M tokens ⭐ **%50 İndirim!**
- **Output (Çıktı) Token:** $0.60 / 1M tokens

**Önemli:** System prompt'ları cache'leyerek input maliyetini **%50 azaltabilirsiniz!**

**Batch API (Toplu İşleme) - Daha da ucuz:**
- **Input:** $0.075 / 1M tokens (%50 indirim)
- **Output:** $0.30 / 1M tokens (%50 indirim)
- **Not:** Batch API asenkron çalışır, daha yavaş ama çok daha ucuz

**Kaynak:** [OpenAI Resmi Fiyatlandırma](https://platform.openai.com/pricing)

#### Token Hesaplama

**Önemli Not:** Token ≠ Kelime

- **1 Token** ≈ **0.75 kelime** (İngilizce için)
- **1 Token** ≈ **1-1.5 karakter** (yaklaşık)
- **100 kelime** ≈ **~133 token**

#### Webtoon Bölüm Başına Maliyet Hesaplaması

**Varsayımlar:**
- Ortalama bölüm: **50 sayfa**
- Sayfa başına ortalama: **3-5 konuşma balonu**
- Balon başına ortalama: **10-15 kelime**
- **Toplam:** ~150-250 balon, ~2,000-3,000 kelime

**Token Hesaplaması:**
- Input tokens: ~2,500-4,000 token (orijinal metin + system prompt)
- Output tokens: ~2,500-4,000 token (çevrilmiş metin)
- **Toplam:** ~5,000-8,000 token/bölüm

**Maliyet Hesaplama (Ortalama 6,500 token/bölüm):**

**Standart API (Normal Kullanım):**
```
Input:  6,500 token × ($0.15 / 1,000,000) = $0.000975
Output: 6,500 token × ($0.60 / 1,000,000) = $0.0039
────────────────────────────────────────────────────
Toplam:                                    ≈ $0.005 (0.5 cent)
```

**Cached Input ile (System Prompt Cache'lenirse):**
```
Cached Input: 2,000 token × ($0.075 / 1,000,000) = $0.00015
Normal Input: 4,500 token × ($0.15 / 1,000,000)   = $0.000675
Output:       6,500 token × ($0.60 / 1,000,000)   = $0.0039
────────────────────────────────────────────────────
Toplam:                                            ≈ $0.0047 (0.47 cent)
Tasarruf:                                          ~%6
```

**Batch API ile (En Ucuz - Asenkron):**
```
Input:  6,500 token × ($0.075 / 1,000,000) = $0.0004875
Output: 6,500 token × ($0.30 / 1,000,000)  = $0.00195
────────────────────────────────────────────────────
Toplam:                                       ≈ $0.0024 (0.24 cent)
Tasarruf:                                     ~%52 (Yarı fiyat!)
```

**Türk Lirası Karşılığı (1 USD ≈ 35 TL):**

| Yöntem | 1 Bölüm | 10 Bölüm | 100 Bölüm | 1,000 Bölüm |
|--------|---------|----------|-----------|-------------|
| **Standart API** | ~0.18 TL | ~1.8 TL | ~18 TL | ~180 TL |
| **Cached Input** | ~0.16 TL | ~1.6 TL | ~16 TL | ~165 TL |
| **Batch API** | ~0.08 TL | ~0.8 TL | ~8 TL | ~84 TL ⭐ |

#### Aylık Kullanım Senaryoları

| Senaryo | Bölüm Sayısı | Token (Tahmini) | Standart API | Cached Input | Batch API |
|---------|-------------|-----------------|--------------|--------------|-----------|
| **Hafif Kullanım** | 50 bölüm/ay | ~325K token | **$2-3** (~70-105 TL) | **$1.9-2.8** (~67-98 TL) | **$1-1.5** (~35-53 TL) ⭐ |
| **Orta Kullanım** | 200 bölüm/ay | ~1.3M token | **$8-12** (~280-420 TL) | **$7.5-11** (~263-385 TL) | **$4-6** (~140-210 TL) ⭐ |
| **Yoğun Kullanım** | 500 bölüm/ay | ~3.25M token | **$20-30** (~700-1,050 TL) | **$19-28** (~665-980 TL) | **$10-15** (~350-525 TL) ⭐ |

**Not:** Batch API asenkron çalışır (daha yavaş), ama maliyet %50 daha düşük!

**Not:** Bu hesaplamalar ortalama değerlerdir. Gerçek maliyet metin uzunluğuna göre değişir.

---

### 2. Sunucu Maliyeti

#### Seçenek A: Oracle Cloud Free Tier (ÖNERİLEN)

**Özellikler:**
- **2x ARM64 Instance** (Ampere A1)
- **Her biri:** 4 OCPU, 24 GB RAM
- **Toplam:** 8 OCPU, 48 GB RAM
- **Depolama:** 200 GB
- **Bant Genişliği:** 10 TB/ay
- **Süre:** **Süresiz ücretsiz** (Always Free)

**Maliyet:** **$0/ay** ✅

**Avantajlar:**
- Güçlü ARM işlemciler (OCR için yeterli)
- Yeterli RAM (Celery worker'lar için)
- Ücretsiz ve süresiz

**Dezavantajlar:**
- Hesap doğrulama gerekebilir (kredi kartı)
- Bölge sınırlamaları olabilir
- İlk kurulum biraz karmaşık

**Kaynak:** [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)

#### Seçenek B: Ücretli VPS

| Sağlayıcı | Plan | CPU | RAM | Depolama | Fiyat/Ay | Notlar |
|-----------|------|-----|-----|-----------|-----------|--------|
| **Hetzner** | CX11 | 1 vCore | 2 GB | 20 GB | **€3.29 (~$3.5)** | En ucuz, Almanya |
| **DigitalOcean** | Basic | 1 vCPU | 1 GB | 25 GB | **$6** | Kolay kurulum |
| **Linode** | Nanode | 1 CPU | 1 GB | 25 GB | **$5** | İyi performans |
| **Vultr** | Regular | 1 vCPU | 1 GB | 25 GB | **$6** | Çok bölge seçeneği |
| **AWS Lightsail** | 1GB | 1 vCPU | 1 GB | 40 GB | **$3.50** | AWS ekosistemi |

**Öneri:** Oracle Cloud Free Tier kullan (ücretsiz). Yetersiz kalırsa Hetzner CX11'e geç.

---

### 3. Diğer Maliyetler

#### PostgreSQL
- **Maliyet:** $0 (kendi sunucunda çalıştırıyorsun)
- **Alternatif:** Supabase Free Tier (500 MB limit)

#### Redis
- **Maliyet:** $0 (kendi sunucunda çalıştırıyorsun)
- **Alternatif:** Redis Cloud Free Tier (30 MB limit)

#### Depolama (İşlenmiş Resimler)
- **Maliyet:** $0-5/ay (kullanıma bağlı)
- **Hesaplama:**
  - İşlenmiş resim: ~500 KB-2 MB
  - 1000 bölüm × 50 sayfa × 1 MB = 50 GB
  - Oracle Cloud Free: 200 GB yeterli
  - Ekstra gerekiyorsa: $0.025/GB (Oracle)

---

## 💡 Maliyet Optimizasyon Stratejileri

### 1. **OpenAI Cached Input (System Prompt Cache)**
- System prompt'ları cache'le (OpenAI özelliği)
- Aynı system prompt tekrar kullanıldığında %50 indirim
- **Tasarruf:** Input maliyetinde %50 azalma
- **Kod:** `cache_control={"type": "ephemeral"}` parametresi kullan

### 2. **Batch API (Toplu İşleme)**
- Birden fazla bölümü toplu halde işle
- Asenkron çalışır (daha yavaş ama çok ucuz)
- **Tasarruf:** %50 maliyet azalması
- **Kullanım:** Acil olmayan çeviriler için ideal

### 3. **Resim Cache (Kendi Cache'iniz)**
- Aynı bölümü tekrar çevirmeyi önle
- İşlenmiş resimleri cache'le
- **Tasarruf:** %50-80 maliyet azalması

### 4. **System Prompt Optimizasyonu**
- System prompt'u kısa ve öz tut
- Gereksiz talimatları kaldır
- **Tasarruf:** %10-20 token tasarrufu

### 3. **Rate Limiting**
- Kullanıcı başına günlük/aylık limit
- **Tasarruf:** Kontrolsüz kullanımı önler

### 4. **Quality Settings**
- "Fast" modu: Daha kısa prompt'lar
- "High" modu: Daha detaylı prompt'lar
- Kullanıcı seçimi yapabilir

---

## 📈 Gerçek Dünya Senaryoları

### Senaryo 1: Kişisel Kullanım (Hobi)
- **Kullanım:** Ayda 20-30 bölüm
- **OpenAI (Standart):** ~$1-2/ay
- **OpenAI (Batch API):** ~$0.5-1/ay ⭐
- **Sunucu:** Oracle Cloud Free ($0)
- **Toplam (Standart):** **~$1-2/ay (~35-70 TL)**
- **Toplam (Batch):** **~$0.5-1/ay (~18-35 TL)** ⭐

### Senaryo 2: Küçük Topluluk (10-50 kullanıcı)
- **Kullanım:** Ayda 200-500 bölüm
- **OpenAI (Standart):** ~$10-20/ay
- **OpenAI (Batch API):** ~$5-10/ay ⭐
- **Sunucu:** Oracle Cloud Free veya Hetzner ($3.5)
- **Toplam (Standart):** **~$13-23/ay (~455-805 TL)**
- **Toplam (Batch):** **~$8-13/ay (~280-455 TL)** ⭐

### Senaryo 3: Orta Ölçekli Platform (100+ kullanıcı)
- **Kullanım:** Ayda 1,000-2,000 bölüm
- **OpenAI (Standart):** ~$40-80/ay
- **OpenAI (Batch API):** ~$20-40/ay ⭐
- **Sunucu:** Hetzner veya daha güçlü ($10-20)
- **Depolama:** $5-10/ay
- **Toplam (Standart):** **~$55-110/ay (~1,925-3,850 TL)**
- **Toplam (Batch):** **~$35-70/ay (~1,225-2,450 TL)** ⭐

---

## ⚠️ Önemli Notlar

### 1. **Token Hesaplama Değişkenliği**
- Metin uzunluğu bölümden bölüme değişir
- Bazı webtoonlar çok metin içerir (diyalog ağırlıklı)
- Bazıları az metin içerir (aksiyon ağırlıklı)
- **Gerçek maliyet %50-200 arası değişebilir**

### 1.5. **Cached Input Kullanımı**
- System prompt'ları cache'leyerek input maliyetini %50 azalt
- Özellikle aynı seriyi çevirirken çok etkili
- **Önemli:** OpenAI'nin 2026'da eklediği yeni özellik!

### 2. **OpenAI Fiyat Değişiklikleri**
- OpenAI fiyatları zamanla değişebilir
- Düzenli olarak kontrol et: https://platform.openai.com/pricing
- 2026 itibarıyla fiyatlar sabit (2024'ten beri aynı)
- **Yeni Özellikler:** Cached Input ve Batch API ile maliyet optimizasyonu mümkün

### 3. **Sunucu Maliyeti Artışları**
- VPS fiyatları genelde sabit kalır
- Oracle Cloud Free Tier şartları değişebilir
- Yedek plan hazırla

### 4. **Gizli Maliyetler**
- **Bandwidth:** Genelde dahil, ama kontrol et
- **Backup:** Otomatik yedekleme maliyeti
- **Monitoring:** Ücretsiz araçlar kullan (Grafana, Prometheus)

---

## 🔄 Alternatif Çözümler ve Maliyetleri

### Alternatif 1: Google Translate API

**Fiyatlandırma:**
- İlk 500,000 karakter/ay: **Ücretsiz**
- Sonrası: $20 / 1M karakter

**Hesaplama:**
- 1 bölüm ≈ 10,000-15,000 karakter
- 50 bölüm/ay: ~500K-750K karakter
- **Maliyet:** İlk 500K ücretsiz, kalan ~$5-10/ay

**Avantajlar:**
- İlk 500K karakter ücretsiz
- Basit API

**Dezavantajlar:**
- ❌ **Context-aware çeviri yok** (tutarlılık sorunu)
- ❌ Karakter isimleri tutarsız çevrilebilir
- ❌ Webtoon dilini anlamakta zorlanır

**Sonuç:** Ücretsiz başlamak için iyi, ama kalite düşük.

---

### Alternatif 2: Local LLM (Kendi Sunucunda)

**Modeller:**
- Llama 3 8B
- Mistral 7B
- Qwen 2.5 7B

**Gereksinimler:**
- GPU: NVIDIA GPU (8GB+ VRAM) veya Apple Silicon
- CPU: En az 16 GB RAM (GPU yoksa)

**Maliyet:**
- **GPU Sunucu:** $50-100/ay (Vast.ai, RunPod)
- **Kendi GPU:** $0 (eğer varsa)

**Avantajlar:**
- Token başına ücret yok
- Veri gizliliği
- Sınırsız kullanım

**Dezavantajlar:**
- ❌ Kurulum karmaşık
- ❌ GPU gereksinimi (pahalı)
- ❌ Daha yavaş (CPU'da)
- ❌ Kalite OpenAI kadar iyi değil

**Sonuç:** Çok kullanım varsa mantıklı, ama başlangıç için değil.

---

### Alternatif 3: Hibrit Yaklaşım

**Strateji:**
- İlk 100 bölüm/ay: Google Translate (ücretsiz)
- Sonrası: OpenAI GPT-4o-mini

**Maliyet:**
- İlk 100 bölüm: $0
- Sonrası: OpenAI fiyatları
- **Tasarruf:** %20-30

**Sonuç:** Bütçe sınırlıysa iyi bir başlangıç.

---

## 📊 Maliyet Karşılaştırma Tablosu

| Çözüm | Aylık Maliyet (50 bölüm) | Aylık Maliyet (500 bölüm) | Kalite | Tutarlılık |
|-------|-------------------------|---------------------------|--------|------------|
| **OpenAI GPT-4o-mini (Standart)** | ~$2-3 | ~$20-30 | ⭐⭐⭐⭐⭐ | ✅ Mükemmel |
| **OpenAI GPT-4o-mini (Batch API)** | ~$1-1.5 | ~$10-15 | ⭐⭐⭐⭐⭐ | ✅ Mükemmel ⭐ |
| **OpenAI GPT-4o-mini (Cached)** | ~$1.9-2.8 | ~$19-28 | ⭐⭐⭐⭐⭐ | ✅ Mükemmel |
| **Google Translate** | $0-5 | ~$50-100 | ⭐⭐⭐ | ❌ Zayıf |
| **Local LLM (GPU)** | $50-100 | $50-100 | ⭐⭐⭐⭐ | ✅ İyi |
| **Hibrit** | $0-2 | ~$15-25 | ⭐⭐⭐⭐ | ⚠️ Orta |

---

## ✅ Önerilen Maliyet Planı

### Başlangıç (İlk 3 Ay)
- **Sunucu:** Oracle Cloud Free Tier ($0)
- **Çeviri:** OpenAI GPT-4o-mini
- **Bütçe:** $10-20/ay (~350-700 TL)
- **Hedef:** 100-200 bölüm/ay

### Büyüme (3-6 Ay)
- **Sunucu:** Oracle Cloud Free (yeterliyse) veya Hetzner ($3.5)
- **Çeviri:** OpenAI GPT-4o-mini + Caching
- **Bütçe:** $20-40/ay (~700-1,400 TL)
- **Hedef:** 300-500 bölüm/ay

### Ölçeklenme (6+ Ay)
- **Sunucu:** Hetzner veya daha güçlü ($10-20)
- **Çeviri:** OpenAI GPT-4o-mini + Optimizasyonlar
- **Depolama:** Gerekirse ek ($5-10)
- **Bütçe:** $50-100/ay (~1,750-3,500 TL)
- **Hedef:** 1,000+ bölüm/ay

---

## 🎯 Sonuç ve Tavsiyeler

### En Uygun Maliyetli Çözüm (2026):
1. **Sunucu:** Oracle Cloud Free Tier ($0)
2. **Çeviri:** OpenAI GPT-4o-mini Batch API (~$0.0024/bölüm) ⭐
3. **Cached Input:** System prompt'ları cache'le (%50 input tasarrufu)
4. **Resim Cache:** Aynı bölümü tekrar çevirmeyi önle
5. **Toplam Tasarruf:** %60-70 maliyet azalması mümkün!

### Gerçekçi Aylık Bütçe (2026 - Optimizasyonlu):
- **Kişisel (Batch API):** $0.5-1/ay (~18-35 TL) ⭐
- **Küçük Topluluk (Batch API):** $8-13/ay (~280-455 TL) ⭐
- **Platform (Batch API):** $35-70/ay (~1,225-2,450 TL) ⭐

**Standart API ile:**
- **Kişisel:** $1-2/ay (~35-70 TL)
- **Küçük Topluluk:** $13-23/ay (~455-805 TL)
- **Platform:** $55-110/ay (~1,925-3,850 TL)

### Önemli Hatırlatmalar (2026):
- ✅ OpenAI fiyatları güncel ($0.15/$0.60 per 1M tokens - 2026)
- ✅ **YENİ:** Cached Input özelliği ile %50 input tasarrufu
- ✅ **YENİ:** Batch API ile %50 genel tasarruf (asenkron)
- ✅ Oracle Cloud Free Tier gerçekten ücretsiz ve güçlü
- ✅ Caching + Batch API ile toplam %60-70 maliyet azalması mümkün
- ⚠️ Token sayısı metin uzunluğuna göre değişir
- ⚠️ Batch API asenkron çalışır (daha yavaş ama çok ucuz)
- ⚠️ Fiyatlar zamanla değişebilir, düzenli kontrol et

---

**Son Güncelleme:** 6 Ocak 2026  
**Bir Sonraki Kontrol:** OpenAI fiyatlarını 3 ayda bir kontrol et  
**Önemli Değişiklikler:** Cached Input ve Batch API özellikleri eklendi (2026)

