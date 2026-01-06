# 📦 Yeni Bilgisayarda Kurulum - Adım Adım

## 🎯 Hızlı Kurulum (5 Dakika)

### Adım 1: Gerekli Programları Kurun

**1.1 Python 3.10+ Kurulumu**

```
1. https://www.python.org/downloads/ adresine gidin
2. "Download Python 3.10.x" butonuna tıklayın
3. İndirilen dosyayı çalıştırın
4. ⚠️ ÖNEMLİ: "Add Python to PATH" kutucuğunu işaretleyin!
5. "Install Now" tıklayın
6. Kurulum bitince terminali açıp test edin: python --version
```

**1.2 Git Kurulumu**

```
1. https://git-scm.com/download/win adresine gidin
2. İndirilen dosyayı çalıştırın
3. Tüm ayarları varsayılan bırakıp "Next" tıklayın
4. Kurulum bitince terminali açıp test edin: git --version
```

**1.3 Docker Desktop Kurulumu**

```
1. https://www.docker.com/products/docker-desktop/ adresine gidin
2. "Download for Windows" butonuna tıklayın
3. İndirilen dosyayı çalıştırın
4. Kurulum bitince BİLGİSAYARI YENİDEN BAŞLATIN
5. Docker Desktop uygulamasını açın
6. Terminalde test edin: docker --version
```

---

### Adım 2: Projeyi İndirin

**Terminal/PowerShell açın ve şu komutları çalıştırın:**

```bash
# Projeyi istediğiniz klasöre indirin
cd D:\
git clone https://github.com/KULLANICI_ADI/Webtoon.git
cd Webtoon
```

**VEYA ZIP dosyasından:**

```
1. Proje ZIP dosyasını indirin
2. D:\Webtoon klasörüne çıkartın
3. Terminal'i D:\Webtoon\Webtoon klasöründe açın
```

---

### Adım 3: Otomatik Kurulum

**Proje klasöründe şu dosyayı çalıştırın:**

```bash
SETUP_COMPLETE.bat
```

**Bu script şunları yapar:**

- ✅ Python'un kurulu olduğunu kontrol eder
- ✅ Docker'ın kurulu olduğunu kontrol eder
- ✅ Virtual environment oluşturur
- ✅ Tüm Python paketlerini kurar
- ✅ .env dosyasını oluşturur
- ✅ Veritabanını oluşturur
- ✅ Redis container'ını başlatır

**⏱️ Beklenen Süre:** 3-5 dakika

---

### Adım 4: Docker'ı Hazırlayın

**4.1 Docker Desktop'ı Açın**

```
1. Windows'ta "Docker Desktop" uygulamasını açın
2. Sol alt köşede "Engine running" yazısını bekleyin
3. Sol menüden "Containers" sekmesine tıklayın
```

**4.2 Redis Container'ını Kontrol Edin**

```
- "webtoon_redis" adında bir container göreceksiniz
- Yanında yeşil nokta olmalı (çalışıyor demek)
- Eğer kırmızı nokta varsa, container'a tıklayıp "Start" butonuna basın
```

**Eğer container yoksa, terminalde şunu çalıştırın:**

```bash
docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
```

---

### Adım 5: Sistemi Başlatın

**Proje klasöründe şu dosyayı çalıştırın:**

```bash
START_ALL.bat
```

**Bu script şunları yapar:**

- ✅ Redis'in çalıştığını kontrol eder
- ✅ 3 terminal penceresi açar:
  - Web Server (Port 8000)
  - Celery Worker
  - Sistem Monitörü
- ✅ Tarayıcıda API dokümantasyonunu açar

**⏱️ Beklenen Süre:** 10-15 saniye

---

### Adım 6: Sistemi Test Edin

**Tarayıcınızda şu adreslere gidin:**

1. **API Dokümantasyonu:** http://localhost:8000/docs
2. **Health Check:** http://localhost:8000/health
3. **Ana Sayfa:** http://localhost:8000

**Eğer sayfalar açılıyorsa, kurulum başarılı! 🎉**

---

## 🔄 Günlük Kullanım

### Sistemi Başlatmak

```bash
START_ALL.bat
```

### Sistemi Durdurmak

```bash
STOP_ALL.bat
```

---

## 🐛 Sorun Giderme

### "Python bulunamadı" Hatası

```bash
# Çözüm 1: Python'u PATH'e ekleyin
1. Windows Arama'da "Environment Variables" yazın
2. "Sistem Özellikleri" > "Gelişmiş" > "Ortam Değişkenleri"
3. "Path" değişkenini bulun ve düzenleyin
4. Python kurulum klasörünü ekleyin (örn: C:\Python310)

# Çözüm 2: Python'u yeniden kurun
- "Add Python to PATH" seçeneğini işaretlemeyi unutmayın!
```

### "Docker bulunamadı" Hatası

```bash
# Çözüm:
1. Docker Desktop'ı kurun
2. Bilgisayarı yeniden başlatın
3. Docker Desktop uygulamasını açın
4. "Engine running" yazısını bekleyin
```

### "Port 8000 zaten kullanımda" Hatası

```bash
# Portu kullanan işlemi bulun
netstat -ano | findstr :8000

# İşlemi sonlandırın (PID numarasını yukarıdaki komuttan alın)
taskkill /PID <PID_NUMARASI> /F
```

### Redis Bağlantı Hatası

```bash
# Docker Desktop'ın açık olduğundan emin olun
docker ps

# Redis container'ını başlatın
docker start webtoon_redis

# Eğer container yoksa, oluşturun
docker run -d --name webtoon_redis -p 6379:6379 redis:7-alpine
```

---

## 📋 Kurulum Kontrol Listesi

- [ ] Python 3.10+ kuruldu
- [ ] Git kuruldu
- [ ] Docker Desktop kuruldu
- [ ] Bilgisayar yeniden başlatıldı (Docker için)
- [ ] Proje indirildi
- [ ] `SETUP_COMPLETE.bat` çalıştırıldı
- [ ] Docker Desktop açıldı
- [ ] Redis container çalışıyor
- [ ] `START_ALL.bat` çalıştırıldı
- [ ] http://localhost:8000/docs açılıyor

---

## 🎓 Sonraki Adımlar

1. **Kullanıcı Kaydı:** `/api/v1/auth/register` endpoint'ini kullanın
2. **API'yi Keşfedin:** http://localhost:8000/docs
3. **Dokümantasyonu Okuyun:** `DOC/COMPLETE_DOCUMENTATION.md`
4. **Test Edin:** `test_all_endpoints.py` scriptini çalıştırın

---

## 📞 Yardım

Sorun yaşarsanız:

1. `STOP_ALL.bat` ile sistemi durdurun
2. `SETUP_COMPLETE.bat` ile yeniden kurun
3. Log dosyalarını kontrol edin
4. `KURULUM_DOKUMANI.md` dosyasına bakın
