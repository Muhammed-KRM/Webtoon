# 🔑 OpenAI API Key Nasıl Alınır?

Bu rehber, OpenAI API key'inizi nasıl alacağınızı adım adım açıklar.

## 📋 Adımlar

### 1. OpenAI Hesabı Oluştur

1. **OpenAI Platform'a gidin:**
   - https://platform.openai.com/
   - "Sign up" butonuna tıklayın

2. **Hesap oluşturun:**
   - Email adresinizle kayıt olun
   - Telefon numaranızı doğrulayın (SMS ile)

### 2. API Key Oluştur

1. **Giriş yaptıktan sonra:**
   - Sağ üst köşedeki profil ikonuna tıklayın
   - "API keys" seçeneğine tıklayın
   - Veya direkt: https://platform.openai.com/api-keys

2. **Yeni API Key oluşturun:**
   - "Create new secret key" butonuna tıklayın
   - Key'e bir isim verin (örn: "Webtoon Translator")
   - "Create secret key" butonuna tıklayın

3. **⚠️ ÖNEMLİ: Key'i kopyalayın!**
   - API key sadece bir kez gösterilir
   - Hemen kopyalayıp güvenli bir yere kaydedin
   - Format: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 3. API Key'i Projeye Ekleyin

1. **`.env` dosyasını açın:**
   ```bash
   # Proje kök dizininde
   .env
   ```

2. **OPENAI_API_KEY değerini güncelleyin:**
   ```env
   OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```
   
   ⚠️ **Tırnak işaretlerini koruyun!**

3. **Dosyayı kaydedin**

### 4. Kredi Yükleme (İlk Kullanım)

OpenAI API ücretlidir, ancak çok ucuzdur:

1. **Billing sayfasına gidin:**
   - https://platform.openai.com/account/billing
   - "Add payment method" butonuna tıklayın

2. **Kredi kartı ekleyin:**
   - Kredi kartı bilgilerinizi girin
   - Minimum $5 yükleme yapabilirsiniz

3. **Kullanım limiti ayarlayın (Önerilir):**
   - "Usage limits" bölümünden aylık limit belirleyin
   - Örnek: $10/ay limit (kontrolsüz kullanımı önler)

## 💰 Maliyet Bilgisi

- **GPT-4o-mini:** Çok ucuz
- **1 bölüm çevirisi:** ~$0.005 (0.5 cent)
- **100 bölüm:** ~$0.50
- **1000 bölüm:** ~$5

**Detaylı maliyet analizi için:** `DOC/MaliyetAnalizi.md`

## ✅ API Key'i Test Etme

API key'inizin çalışıp çalışmadığını test etmek için:

```bash
# Python ile test
python -c "from openai import OpenAI; client = OpenAI(api_key='sk-proj-...'); print('API Key çalışıyor!')"
```

Veya uygulamayı başlatıp bir çeviri işlemi deneyin.

## 🔒 Güvenlik İpuçları

1. **`.env` dosyasını asla Git'e commit etmeyin!**
   - `.gitignore` dosyasında `.env` olmalı

2. **API key'i kimseyle paylaşmayın**

3. **Key'i düzenli olarak yenileyin** (güvenlik için)

4. **Kullanım limitleri koyun** (kontrolsüz kullanımı önler)

## ❓ Sorun Giderme

### "Invalid API Key" Hatası
- API key'i doğru kopyaladığınızdan emin olun
- Tırnak işaretlerini kontrol edin
- `.env` dosyasının doğru konumda olduğundan emin olun

### "Insufficient Quota" Hatası
- Billing sayfasından kredi yükleyin
- Usage limits kontrol edin

### "Rate Limit" Hatası
- Çok fazla istek gönderiyorsunuz
- Biraz bekleyip tekrar deneyin

## 📞 Destek

- **OpenAI Dokümantasyon:** https://platform.openai.com/docs
- **OpenAI Support:** https://help.openai.com/

---

**Son Güncelleme:** 6 Ocak 2026

