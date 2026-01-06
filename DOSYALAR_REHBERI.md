# 📚 Kurulum Dosyaları Rehberi

## 🎯 Hangi Dosyayı Kullanmalıyım?

### Yeni Bilgisayarda İlk Kurulum

**1. KURULUM_SIHIRBAZI.bat** ⭐ (Önerilen - Başlangıç İçin)

```
Adım adım interaktif kurulum
Her adımda ne yapacağınızı gösterir
Yeni kullanıcılar için ideal
```

**2. SETUP_COMPLETE.bat** (Hızlı Otomatik Kurulum)

```
Tek tıkla otomatik kurulum
Deneyimli kullanıcılar için
Tüm adımları otomatik yapar
```

**3. ADIM_ADIM_KURULUM.md** (Detaylı Yazılı Rehber)

```
Ekran görüntülü detaylı anlatım
Manuel kurulum için
Sorun giderme ipuçları
```

---

### Günlük Kullanım

**START_ALL.bat** (Sistemi Başlat)

```
Tek tıkla tüm servisleri başlatır
Her gün kullanacağınız dosya
3 terminal penceresi açar
```

**STOP_ALL.bat** (Sistemi Durdur)

```
Tüm servisleri güvenle kapatır
Gün sonunda kullanın
Temiz kapatma sağlar
```

---

### Dokümantasyon

**KURULUM_DOKUMANI.md**

```
Kapsamlı kurulum rehberi
Tüm detaylar burada
Sorun giderme bölümü var
```

**HIZLI_BASLANGIC.md**

```
Hızlı başlangıç kılavuzu
Temel komutlar
Erişim adresleri
```

---

## 📋 Kurulum Sırası (Yeni Bilgisayar)

```
1. KURULUM_SIHIRBAZI.bat çalıştır
   ↓
2. Programları kur (Python, Git, Docker)
   ↓
3. Bilgisayarı yeniden başlat (Docker için)
   ↓
4. Docker Desktop'ı aç
   ↓
5. START_ALL.bat çalıştır
   ↓
6. http://localhost:8000/docs aç
   ↓
7. ✅ Hazır!
```

---

## 🔧 Dosya Açıklamaları

### Kurulum Dosyaları

| Dosya                   | Amaç               | Ne Zaman Kullanılır         |
| ----------------------- | ------------------ | --------------------------- |
| `KURULUM_SIHIRBAZI.bat` | İnteraktif kurulum | İlk kez kuruyorsanız        |
| `SETUP_COMPLETE.bat`    | Otomatik kurulum   | Hızlı kurulum istiyorsanız  |
| `ADIM_ADIM_KURULUM.md`  | Detaylı rehber     | Manuel kurulum yapacaksanız |
| `KURULUM_DOKUMANI.md`   | Tam dokümantasyon  | Sorun yaşarsanız            |

### Çalıştırma Dosyaları

| Dosya              | Amaç           | Ne Zaman Kullanılır           |
| ------------------ | -------------- | ----------------------------- |
| `START_ALL.bat`    | Sistemi başlat | Her gün, sistem başlatırken   |
| `STOP_ALL.bat`     | Sistemi durdur | Gün sonunda, kapatırken       |
| `START_CELERY.bat` | Sadece Celery  | Celery yeniden başlatmak için |
| `START_SIMPLE.bat` | Basit başlatma | Sadece web server için        |

### Test Dosyaları

| Dosya                   | Amaç               | Ne Zaman Kullanılır        |
| ----------------------- | ------------------ | -------------------------- |
| `test_all_endpoints.py` | API testi          | Sistem kontrolü için       |
| `RUN_TESTS.bat`         | Test çalıştır      | Geliştirme sonrası         |
| `init_db.py`            | Veritabanı oluştur | İlk kurulum veya sıfırlama |

---

## 🚀 Hızlı Başlangıç (Özet)

### İlk Kurulum (Bir Kez)

```bash
KURULUM_SIHIRBAZI.bat
```

### Günlük Kullanım

```bash
# Sabah
START_ALL.bat

# Akşam
STOP_ALL.bat
```

---

## 💡 İpuçları

**İlk Kez Kuruyorsanız:**

- `KURULUM_SIHIRBAZI.bat` kullanın
- Her adımı dikkatlice okuyun
- Docker kurulumundan sonra bilgisayarı yeniden başlatın

**Deneyimliyseniz:**

- `SETUP_COMPLETE.bat` ile hızlı kurun
- `START_ALL.bat` ile başlatın

**Sorun Yaşarsanız:**

- `KURULUM_DOKUMANI.md` dosyasına bakın
- "Sorun Giderme" bölümünü okuyun
- Sistemi `STOP_ALL.bat` ile durdurup yeniden başlatın

---

## 📞 Yardım

Hangi dosyayı kullanacağınızdan emin değilseniz:

1. **Yeni kullanıcı:** `KURULUM_SIHIRBAZI.bat`
2. **Deneyimli:** `SETUP_COMPLETE.bat`
3. **Sorun var:** `KURULUM_DOKUMANI.md`
