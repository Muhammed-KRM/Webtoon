# 📝 .env Dosyası Oluşturma

## Hızlı Yöntem

Proje kök dizininde (C:\Webtoon) `.env` adında bir dosya oluşturun ve aşağıdaki içeriği yapıştırın:

```env
# ============================================
# Webtoon AI Translator - Environment Variables
# ============================================

# Application Settings
PROJECT_NAME="Webtoon AI Translator"
SECRET_KEY="your-super-secret-key-minimum-32-characters-long-change-this-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database Configuration
# SQLite (Kolay başlangıç için)
DATABASE_URL="sqlite:///./webtoon.db"

# PostgreSQL (Production için - yukarıdakini yorum satırı yapın)
# DATABASE_URL="postgresql://postgres:your_password@localhost:5432/webtoon_db"

# Redis Configuration
REDIS_URL="redis://localhost:6379/0"

# OpenAI API Configuration
# ⚠️ ÖNEMLİ: Buraya gerçek API key'inizi koyun!
# Format: sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# OpenAI Model
OPENAI_MODEL="gpt-4o-mini"

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# File Storage Paths
STORAGE_PATH=./storage
CACHE_PATH=./cache
FONTS_PATH=./fonts
```

## 🔑 API Key Nasıl Alınır?

**Detaylı rehber:** `DOC/API_KEY_REHBERI.md` dosyasına bakın.

**Kısa özet:**
1. https://platform.openai.com/ adresine gidin
2. Hesap oluşturun / Giriş yapın
3. Sağ üst köşede profil → "API keys"
4. "Create new secret key" butonuna tıklayın
5. Key'i kopyalayın (sadece bir kez gösterilir!)
6. Yukarıdaki `OPENAI_API_KEY` değerine yapıştırın

**Örnek API Key formatı:**
```
sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

## ⚠️ Önemli Notlar

1. **SECRET_KEY:** En az 32 karakter olmalı. Rastgele bir string oluşturun.
   - Örnek: `my-super-secret-key-12345678901234567890`

2. **OPENAI_API_KEY:** Tırnak işaretlerini koruyun!
   - ✅ Doğru: `OPENAI_API_KEY="sk-proj-..."`
   - ❌ Yanlış: `OPENAI_API_KEY=sk-proj-...` (tırnak yok)

3. **DATABASE_URL:** İlk başlangıç için SQLite kullanın (daha kolay)
   - SQLite: `DATABASE_URL="sqlite:///./webtoon.db"`
   - PostgreSQL: `DATABASE_URL="postgresql://user:pass@localhost:5432/webtoon_db"`

## ✅ Kontrol Listesi

- [ ] `.env` dosyası oluşturuldu
- [ ] `SECRET_KEY` en az 32 karakter
- [ ] `OPENAI_API_KEY` eklendi (sk-proj- ile başlamalı)
- [ ] `DATABASE_URL` ayarlandı (SQLite veya PostgreSQL)
- [ ] Dosya kaydedildi

## 🚀 Sonraki Adım

`.env` dosyasını oluşturduktan sonra:
1. `SETUP.bat` çalıştırın (veya manuel kurulum)
2. Redis başlatın
3. Celery worker başlatın
4. FastAPI başlatın

Detaylar: `KURULUM.md` veya `DOC/HIZLI_BASLANGIC.md`

