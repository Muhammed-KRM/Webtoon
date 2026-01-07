# 📦 Yeni Bilgisayarda Kurulum - Adım Adım Detaylı Rehber

## 🎯 Hızlı Kurulum Özeti

1. **Gerekli Programları Kur** (Python, Git, Docker)
2. **Projeyi İndir**
3. **Otomatik Kurulum Çalıştır** (`SETUP_COMPLETE.bat`)
4. **Docker'ı Hazırla** (Redis container)
5. **Sistemi Başlat** (`START_ALL.bat`)
6. **Test Et** (http://localhost:8000/docs)

**Toplam Süre:** 10-15 dakika

---

## 📋 Adım 1: Gerekli Programları Kurun

### 1.1 Python 3.10+ Kurulumu

**⚠️ ÖNEMLİ:** Python 3.14 kullanıyorsanız bazı paketlerde uyumluluk sorunları olabilir. Python 3.10-3.12 önerilir.

```
1. https://www.python.org/downloads/ adresine gidin
2. "Download Python 3.10.x" veya "Download Python 3.12.x" butonuna tıklayın
3. İndirilen dosyayı çalıştırın
4. ⚠️ ÇOK ÖNEMLİ: "Add Python to PATH" kutucuğunu MUTLAKA işaretleyin!
5. "Install Now" tıklayın
6. Kurulum bitince terminali açıp test edin: python --version
```

**Kurulum Kontrolü:**
```bash
python --version
# Çıktı: Python 3.10.x veya Python 3.12.x olmalı
```

### 1.2 Git Kurulumu

```
1. https://git-scm.com/download/win adresine gidin
2. "Download for Windows" butonuna tıklayın
3. İndirilen dosyayı çalıştırın
4. Tüm ayarları varsayılan bırakıp "Next" tıklayın
5. Kurulum bitince terminali açıp test edin: git --version
```

**Kurulum Kontrolü:**
```bash
git --version
# Çıktı: git version 2.x.x olmalı
```

### 1.3 Docker Desktop Kurulumu

```
1. https://www.docker.com/products/docker-desktop/ adresine gidin
2. "Download for Windows" butonuna tıklayın
3. İndirilen dosyayı çalıştırın
4. Kurulum bitince BİLGİSAYARI MUTLAKA YENİDEN BAŞLATIN
5. Docker Desktop uygulamasını açın
6. Sol alt köşede "Engine running" yazısını bekleyin (1-2 dakika sürebilir)
7. Terminalde test edin: docker --version
```

**Kurulum Kontrolü:**
```bash
docker --version
# Çıktı: Docker version 24.x.x olmalı
```

---

## 📥 Adım 2: Projeyi İndirin

### Seçenek A: GitHub'dan İndirme

**Terminal/PowerShell açın ve şu komutları çalıştırın:**

```bash
# Projeyi istediğiniz klasöre indirin (örn: C:\ veya D:\)
cd C:\
git clone https://github.com/KULLANICI_ADI/Webtoon.git
cd Webtoon
```

### Seçenek B: ZIP Dosyasından İndirme

```
1. Proje ZIP dosyasını indirin
2. C:\Webtoon veya D:\Webtoon klasörüne çıkartın
3. Terminal'i C:\Webtoon\Webtoon klasöründe açın
```

**Kontrol:**
```bash
# Proje klasöründe olmalısınız
dir
# Şu dosyaları görmelisiniz: main.py, requirements.txt, SETUP_COMPLETE.bat
```

---

## 🔧 Adım 3: Otomatik Kurulum

### 3.1 SETUP_COMPLETE.bat Çalıştırma

**Proje klasöründe (C:\Webtoon) şu dosyayı çift tıklayın veya terminalden çalıştırın:**

```bash
SETUP_COMPLETE.bat
```

**VEYA PowerShell'den:**
```powershell
cd C:\Webtoon
.\SETUP_COMPLETE.bat
```

**Bu script şunları yapar:**

1. ✅ Python'un kurulu olduğunu kontrol eder
2. ✅ Docker'ın kurulu olduğunu kontrol eder
3. ✅ Virtual environment oluşturur (`venv` klasörü)
4. ✅ pip'i günceller
5. ✅ Tüm Python paketlerini kurar (`requirements.txt`'den)
6. ✅ `.env` dosyasını oluşturur (yoksa)
7. ✅ Veritabanını oluşturur (`webtoon.db`)
8. ✅ Redis container'ını oluşturur ve başlatır

**⏱️ Beklenen Süre:** 5-10 dakika (internet hızına bağlı)

**⚠️ ÖNEMLİ NOTLAR:**

- Kurulum sırasında bazı paketlerde hata alabilirsiniz (özellikle Python 3.14 kullanıyorsanız)
- Eğer `SETUP_COMPLETE.bat` hata verirse, aşağıdaki "Manuel Kurulum" bölümüne bakın

### 3.2 Kurulum Sonrası Kontroller

**Virtual Environment Kontrolü:**
```bash
# venv klasörünün oluştuğunu kontrol edin
dir venv
# Scripts klasörü görünmeli
```

**Paket Kurulumu Kontrolü:**
```bash
venv\Scripts\python.exe -m pip list | findstr "fastapi"
# Çıktı: fastapi görünmeli
```

**Veritabanı Kontrolü:**
```bash
dir webtoon.db
# webtoon.db dosyası görünmeli
```

**Redis Container Kontrolü:**
```bash
docker ps | findstr "webtoon_redis"
# webtoon_redis container görünmeli ve STATUS "Up" olmalı
```

---

## 🐳 Adım 4: Docker ve Redis Hazırlığı

### 4.1 Docker Desktop'ı Açın

```
1. Windows'ta "Docker Desktop" uygulamasını açın
2. Sol alt köşede "Engine running" yazısını bekleyin (1-2 dakika)
3. Sol menüden "Containers" sekmesine tıklayın
```

### 4.2 Redis Container'ını Kontrol Edin

**Docker Desktop'ta:**
```
- "webtoon_redis" adında bir container göreceksiniz
- Yanında yeşil nokta olmalı (çalışıyor demek)
- Eğer kırmızı nokta varsa, container'a tıklayıp "Start" butonuna basın
```

**Terminal'den Kontrol:**
```bash
docker ps
# webtoon_redis container'ı listede görünmeli
```

**Eğer container yoksa veya çalışmıyorsa:**

```bash
# Container'ı oluştur ve başlat
docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine

# Kontrol et
docker ps | findstr "webtoon_redis"
```

---

## 🚀 Adım 5: Sistemi Başlatın

### 5.1 START_ALL.bat ile Başlatma (Önerilen)

**⚠️ ÖNEMLİ:** `START_ALL.bat` dosyasını **çift tıklayarak** veya **terminalden direkt çalıştırarak** başlatın. PowerShell'den `Start-Process` ile çalıştırmayın!

**Proje klasöründe (C:\Webtoon):**

```bash
START_ALL.bat
```

**VEYA çift tıklayarak başlatın.**

**Bu script şunları yapar:**

1. ✅ Redis container'ının çalıştığını kontrol eder (yoksa başlatır)
2. ✅ Veritabanının mevcut olduğunu kontrol eder (yoksa oluşturur)
3. ✅ **3 yeni terminal penceresi açar:**
   - **Terminal 1:** Web Server (FastAPI) - Port 8000
   - **Terminal 2:** Celery Worker (Arka plan işleri)
   - **Terminal 3:** Sistem Monitörü (Durum bilgisi)
4. ✅ Tarayıcıda API dokümantasyonunu açar (http://localhost:8000/docs)

**⏱️ Beklenen Süre:** 10-15 saniye

**⚠️ UYARI:** 
- Script çalışırken "Press any key to continue" mesajı çıkacak
- Enter'a basın, 3 terminal penceresi açılacak
- Bu pencereleri **KAPATMAYIN**! Sistem çalışırken açık kalmalılar

### 5.2 Sistem Başlatma Adımları (Detaylı)

**Adım 1: START_ALL.bat'ı Çalıştırın**
```
1. C:\Webtoon klasörüne gidin
2. START_ALL.bat dosyasına çift tıklayın
3. Açılan terminal penceresinde "Press any key to continue" mesajını görün
4. Enter'a basın
```

**Adım 2: Terminal Pencerelerini Kontrol Edin**

Açılan 3 terminal penceresi:

**Terminal 1 - Web Server:**
```
Webtoon - Web Server
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
```

**Terminal 2 - Celery Worker:**
```
Webtoon - Celery Worker
celery@HOSTNAME v5.3.4 (emerald-rush)
[INFO] Connected to redis://localhost:6379/0
```

**Terminal 3 - System Monitor:**
```
WEBTOON AI TRANSLATOR - SYSTEM STATUS
[OK] Web Server: http://localhost:8000
[OK] API Docs: http://localhost:8000/docs
[OK] Redis: localhost:6379
[OK] Celery Worker: Active
```

**Adım 3: Tarayıcı Kontrolü**

Otomatik olarak tarayıcı açılacak ve şu sayfayı göreceksiniz:
- **URL:** http://localhost:8000/docs
- **İçerik:** Swagger UI - API Dokümantasyonu

### 5.3 Manuel Başlatma (Alternatif)

Eğer `START_ALL.bat` çalışmazsa, manuel olarak başlatabilirsiniz:

**Terminal 1 - Web Server:**
```bash
cd C:\Webtoon
venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
cd C:\Webtoon
venv\Scripts\celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

**Terminal 3 - Tarayıcı:**
```
http://localhost:8000/docs adresine gidin
```

---

## ✅ Adım 6: Sistemi Test Edin

### 6.1 Web Arayüzü Testleri

**Tarayıcınızda şu adreslere gidin:**

1. **API Dokümantasyonu:**
   - URL: http://localhost:8000/docs
   - Beklenen: Swagger UI sayfası açılmalı
   - Endpoint'ler görünmeli (Authentication, Translation, vb.)

2. **Health Check:**
   - URL: http://localhost:8000/health
   - Beklenen: JSON response
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "redis": "connected",
     "version": "1.0.0"
   }
   ```

3. **Ana Sayfa:**
   - URL: http://localhost:8000
   - Beklenen: JSON response
   ```json
   {
     "message": "Webtoon AI Translator API",
     "version": "1.0.0",
     "status": "running"
   }
   ```

### 6.2 Terminal Log Kontrolleri

**Web Server Terminal'inde şunları görmelisiniz:**
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
INFO: 127.0.0.1:xxxxx "GET /docs HTTP/1.1" 200 OK
```

**Celery Worker Terminal'inde şunları görmelisiniz:**
```
celery@HOSTNAME v5.3.4 (emerald-rush)
[INFO] Connected to redis://localhost:6379/0
```

**⚠️ UYARI MESAJLARI (Normal):**

Aşağıdaki uyarılar **normaldir** ve sistemi etkilemez:
```
WARNING: Argos Translate not available: unable to infer type for attribute "REGEX"
WARNING: spaCy not available: unable to infer type for attribute "REGEX". Using regex-based NER fallback.
```

Bu uyarılar, bazı opsiyonel paketlerin (spaCy, Argos Translate) Python 3.14 ile uyumlu olmaması nedeniyle görünür. Sistem regex fallback kullanarak çalışmaya devam eder.

---

## 🔄 Günlük Kullanım

### Sistemi Başlatmak

```bash
# Proje klasörüne gidin
cd C:\Webtoon

# START_ALL.bat'ı çalıştırın
START_ALL.bat
```

**VEYA çift tıklayarak başlatın.**

### Sistemi Durdurmak

```bash
# Proje klasöründe
STOP_ALL.bat
```

**VEYA terminal pencerelerini kapatın (Ctrl+C ile durdurun).**

---

## 🛠️ Manuel Kurulum (Sorun Giderme)

Eğer `SETUP_COMPLETE.bat` hata verirse, aşağıdaki adımları manuel olarak takip edin:

### 1. Virtual Environment Oluştur

```bash
cd C:\Webtoon
python -m venv venv
```

### 2. Virtual Environment'ı Aktif Et

```bash
venv\Scripts\activate
```

### 3. pip'i Güncelle

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Temel Paketleri Kur

```bash
# Önce temel paketleri kurun
venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy celery redis pydantic pydantic-settings python-dotenv alembic slowapi python-jose passlib python-multipart email-validator
```

### 5. Diğer Paketleri Kur

```bash
# HTTP ve Web Scraping
venv\Scripts\python.exe -m pip install httpx beautifulsoup4 selenium lxml

# Image Processing
venv\Scripts\python.exe -m pip install opencv-python Pillow numpy

# Translation
venv\Scripts\python.exe -m pip install openai deep-translator

# OCR
venv\Scripts\python.exe -m pip install easyocr

# Utilities
venv\Scripts\python.exe -m pip install loguru stripe

# Testing
venv\Scripts\python.exe -m pip install pytest pytest-asyncio
```

**⚠️ NOT:** Python 3.14 kullanıyorsanız:
- `Pillow>=11.3.0` kullanın (10.2.0 çalışmaz)
- `torch>=2.9.0` kullanın (2.1.2 çalışmaz)
- `numpy>=1.26.0` kullanın
- `spacy` ve `argostranslate` opsiyoneldir (uyumluluk sorunları var)

### 6. .env Dosyası Oluştur

`.env` dosyasını `C:\Webtoon` klasöründe oluşturun:

```env
SECRET_KEY=development_secret_key_change_in_production_32chars
DATABASE_URL=sqlite:///./webtoon.db
OPENAI_API_KEY=sk-your-openai-api-key-here
REDIS_URL=redis://localhost:6379/0
CDN_ENABLED=False
STRIPE_SECRET_KEY=sk_test_your-stripe-key-here
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 7. Veritabanını Oluştur

```bash
venv\Scripts\python.exe init_db.py
```

### 8. Redis Container'ını Başlat

```bash
docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
```

---

## 🐛 Sorun Giderme

### "Python bulunamadı" Hatası

**Çözüm 1: Python'u PATH'e ekleyin**
```
1. Windows Arama'da "Environment Variables" yazın
2. "Sistem Özellikleri" > "Gelişmiş" > "Ortam Değişkenleri"
3. "Path" değişkenini bulun ve düzenleyin
4. Python kurulum klasörünü ekleyin:
   - C:\Python310\ (veya kurulum klasörünüz)
   - C:\Python310\Scripts\
5. "Tamam" tıklayın ve terminali yeniden başlatın
```

**Çözüm 2: Python'u yeniden kurun**
```
- Kurulum sırasında "Add Python to PATH" seçeneğini MUTLAKA işaretleyin!
```

### "Docker bulunamadı" Hatası

**Çözüm:**
```
1. Docker Desktop'ı kurun
2. Bilgisayarı yeniden başlatın
3. Docker Desktop uygulamasını açın
4. "Engine running" yazısını bekleyin (1-2 dakika)
5. Terminali yeniden başlatın
```

### "Port 8000 zaten kullanımda" Hatası

**Çözüm:**
```bash
# Portu kullanan işlemi bulun
netstat -ano | findstr :8000

# İşlemi sonlandırın (PID numarasını yukarıdaki komuttan alın)
taskkill /PID <PID_NUMARASI> /F

# Örnek:
# taskkill /PID 1234 /F
```

### "ModuleNotFoundError" Hatası

**Çözüm:**
```bash
# Eksik paketi kurun
venv\Scripts\python.exe -m pip install <paket_adi>

# Örnekler:
venv\Scripts\python.exe -m pip install email-validator
venv\Scripts\python.exe -m pip install stripe
venv\Scripts\python.exe -m pip install loguru
```

### Redis Bağlantı Hatası

**Çözüm:**
```bash
# Docker Desktop'ın açık olduğundan emin olun
docker ps

# Redis container'ını başlatın
docker start webtoon_redis

# Eğer container yoksa, oluşturun
docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine

# Kontrol edin
docker ps | findstr "webtoon_redis"
```

### "spaCy" veya "Argos Translate" Uyarıları

**Bu uyarılar normaldir ve sistemi etkilemez:**
```
WARNING: Argos Translate not available: unable to infer type for attribute "REGEX"
WARNING: spaCy not available: unable to infer type for attribute "REGEX"
```

**Açıklama:**
- Python 3.14 kullanıyorsanız, bu paketler pydantic v1/v2 uyumsuzluğu nedeniyle çalışmayabilir
- Sistem otomatik olarak regex fallback kullanır
- Çeviri ve NER işlevleri çalışmaya devam eder

### START_ALL.bat Sadece 1 Terminal Açıyor

**Sorun:** PowerShell'den `Start-Process` ile çalıştırıldığında sadece 1 terminal açılır.

**Çözüm:**
```bash
# START_ALL.bat'ı çift tıklayarak başlatın
# VEYA terminalden direkt çalıştırın:
cd C:\Webtoon
START_ALL.bat
```

**Kontrol:**
- 3 terminal penceresi açılmalı (Web Server, Celery Worker, Monitor)
- Her terminal farklı bir başlıkla açılmalı

---

## 📋 Kurulum Kontrol Listesi

Kurulumun başarılı olduğunu kontrol etmek için:

- [ ] Python 3.10+ kuruldu (`python --version`)
- [ ] Git kuruldu (`git --version`)
- [ ] Docker Desktop kuruldu (`docker --version`)
- [ ] Bilgisayar yeniden başlatıldı (Docker için)
- [ ] Proje indirildi (`C:\Webtoon` klasörü mevcut)
- [ ] `SETUP_COMPLETE.bat` çalıştırıldı
- [ ] `venv` klasörü oluşturuldu
- [ ] `webtoon.db` dosyası oluşturuldu
- [ ] `.env` dosyası oluşturuldu
- [ ] Docker Desktop açıldı
- [ ] Redis container çalışıyor (`docker ps`)
- [ ] `START_ALL.bat` çalıştırıldı
- [ ] 3 terminal penceresi açıldı
- [ ] http://localhost:8000/docs açılıyor
- [ ] http://localhost:8000/health çalışıyor

---

## 🎓 Sonraki Adımlar

Kurulum tamamlandıktan sonra:

1. **Kullanıcı Kaydı:**
   - http://localhost:8000/docs adresine gidin
   - `POST /api/v1/auth/register` endpoint'ini kullanın
   - Yeni kullanıcı oluşturun

2. **API'yi Keşfedin:**
   - Swagger UI'da tüm endpoint'leri görüntüleyin
   - "Try it out" butonlarıyla test edin

3. **Dokümantasyonu Okuyun:**
   - `DOC/COMPLETE_DOCUMENTATION.md` - Tam dokümantasyon
   - `DOC/COMPLETE_ENDPOINTS.md` - Tüm endpoint'ler
   - `DOC/USAGE_GUIDE.md` - Kullanım rehberi

4. **Test Edin:**
   ```bash
   venv\Scripts\python.exe test_all_endpoints.py
   ```

---

## 📞 Yardım ve Destek

Sorun yaşarsanız:

1. **Sistemi Durdurun:**
   ```bash
   STOP_ALL.bat
   ```

2. **Yeniden Kurun:**
   ```bash
   SETUP_COMPLETE.bat
   ```

3. **Log Dosyalarını Kontrol Edin:**
   - Terminal çıktılarını inceleyin
   - Hata mesajlarını not edin

4. **Dokümantasyonu İnceleyin:**
   - `KURULUM_DOKUMANI.md` - Detaylı kurulum
   - `DOC/` klasöründeki diğer dokümanlar

5. **Sorun Giderme Bölümüne Bakın:**
   - Yukarıdaki "Sorun Giderme" bölümüne göz atın

---

## 📝 Önemli Notlar

### Python Versiyonu

- **Önerilen:** Python 3.10, 3.11 veya 3.12
- **Python 3.14:** Bazı paketlerde uyumluluk sorunları olabilir
  - Pillow, torch, numpy versiyonları güncellenmelidir
  - spaCy ve Argos Translate opsiyonel hale getirilmiştir

### Paket Versiyonları

Python 3.14 için güncellenmiş versiyonlar:
- `Pillow>=11.3.0` (10.2.0 çalışmaz)
- `torch>=2.9.0` (2.1.2 çalışmaz)
- `numpy>=1.26.0` (1.26.3 çalışmaz)

### Opsiyonel Paketler

Aşağıdaki paketler opsiyoneldir ve kurulmasa da sistem çalışır:
- `spacy` - NER için (regex fallback kullanılır)
- `argostranslate` - Offline çeviri için (Google Translate fallback kullanılır)
- `transformers` - Hugging Face modelleri için

### Sistem Gereksinimleri

- **RAM:** En az 4GB (8GB önerilir)
- **Disk:** En az 5GB boş alan
- **İnternet:** İlk kurulum için gerekli (paket indirme)
- **İşletim Sistemi:** Windows 10/11

---

## 🎉 Başarılı Kurulum!

Kurulum tamamlandıysa:

✅ Sistem çalışıyor  
✅ API dokümantasyonu erişilebilir  
✅ Tüm servisler aktif  

**Sonraki adım:** http://localhost:8000/docs adresine gidip API'yi keşfedin!

---

*Son Güncelleme: 2026-01-07*  
*Python 3.14 uyumluluk güncellemeleri eklendi*
