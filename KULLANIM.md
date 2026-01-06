# 📖 Kullanım Rehberi

## 🚀 Hızlı Başlangıç

### İlk Kurulum (Sadece Bir Kez)

1. **SETUP.bat çalıştırın**
   ```bash
   SETUP.bat
   ```
   Bu script tüm bağımlılıkları yükler ve klasörleri oluşturur.

2. **.env dosyasını düzenleyin**
   - `ENV_OLUSTUR.md` dosyasına bakın
   - OpenAI API key'inizi ekleyin (`DOC/API_KEY_REHBERI.md`)

### Projeyi Başlatma

**Tek komutla her şeyi başlatın:**
```bash
START.bat
```

Bu komut:
- ✅ Redis'i başlatır (Docker ile)
- ✅ Celery Worker'ı başlatır (ayrı pencere)
- ✅ FastAPI'yi başlatır (ana pencere)

**Açılan pencereler:**
- **Celery Worker penceresi:** Arka planda çalışır (kapatmayın!)
- **FastAPI penceresi:** Ana pencere (Ctrl+C ile durdurabilirsiniz)

### Projeyi Durdurma

**Tüm servisleri durdurmak için:**
```bash
STOP.bat
```

Bu komut:
- ✅ Celery Worker'ı durdurur
- ✅ FastAPI'yi durdurur
- ✅ Redis'i durdurur (Docker)

### Durum Kontrolü

**Servislerin durumunu kontrol etmek için:**
```bash
CHECK.bat
```

Bu komut:
- ✅ Sanal ortam kontrolü
- ✅ .env dosyası kontrolü
- ✅ Redis durumu
- ✅ Process durumları

### Yeniden Başlatma

**Tüm servisleri yeniden başlatmak için:**
```bash
RESTART.bat
```

## 📋 Komut Listesi

| Dosya | Açıklama | Ne Zaman Kullanılır |
|-------|----------|---------------------|
| `SETUP.bat` | İlk kurulum | Sadece bir kez, projeyi ilk kurarken |
| `START.bat` | Projeyi başlat | Her kullanımda |
| `STOP.bat` | Projeyi durdur | İşiniz bittiğinde |
| `RESTART.bat` | Yeniden başlat | Hata aldığınızda veya ayar değişikliğinden sonra |
| `CHECK.bat` | Durum kontrolü | Sorun yaşadığınızda |

## 🌐 API Kullanımı

### 1. API Dokümantasyonu

Proje başladıktan sonra tarayıcıda açın:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 2. İş Akışı

#### Adım 1: Kullanıcı Kaydı
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

#### Adım 2: Giriş Yap
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

#### Adım 3: Çeviri Başlat
```http
POST /api/v1/translate/start
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "chapter_url": "https://example.com/webtoon/chapter/1",
  "target_lang": "tr",
  "mode": "clean"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Çeviri işlemi başlatıldı. Task ID ile takip edebilirsiniz.",
  "data": {
    "task_id": "abc123-def456-ghi789"
  }
}
```

#### Adım 4: Durum Kontrolü (Polling)
```http
GET /api/v1/translate/status/{task_id}
Authorization: Bearer {access_token}
```

**Response (İşlem devam ederken):**
```json
{
  "success": true,
  "data": {
    "task_id": "abc123-def456-ghi789",
    "status": "PROCESSING",
    "progress": 45,
    "message": "OCR yapılıyor...",
    "result": null
  }
}
```

**Response (Tamamlandığında):**
```json
{
  "success": true,
  "data": {
    "task_id": "abc123-def456-ghi789",
    "status": "SUCCESS",
    "progress": 100,
    "message": "Completed",
    "result": {
      "pages": ["base64_image_1", "base64_image_2", ...],
      "total": 50
    }
  }
}
```

#### Adım 5: Sonuçları Al
```http
GET /api/v1/translate/result/{task_id}
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "chapter_title": "Chapter abc123",
    "pages": [
      {
        "index": 0,
        "processed_url": "data:image/jpeg;base64,/9j/4AAQ...",
        "original_text": ["Hello", "World"],
        "translated_text": ["Merhaba", "Dünya"],
        "bubbles": [
          {"x": 100, "y": 200, "w": 150, "h": 30}
        ]
      },
      ...
    ],
    "total_pages": 50
  }
}
```

## 🔄 Frontend Entegrasyonu

### Angular/React Örneği

```typescript
// 1. Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'user', password: 'pass' })
});
const { data } = await loginResponse.json();
const token = data.access_token;

// 2. Çeviri Başlat
const startResponse = await fetch('http://localhost:8000/api/v1/translate/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    chapter_url: 'https://example.com/chapter/1',
    target_lang: 'tr'
  })
});
const { data: startData } = await startResponse.json();
const taskId = startData.task_id;

// 3. Durum Kontrolü (Polling)
const checkStatus = async () => {
  const statusResponse = await fetch(
    `http://localhost:8000/api/v1/translate/status/${taskId}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  const { data } = await statusResponse.json();
  
  if (data.status === 'SUCCESS') {
    // Sonuçları al
    const resultResponse = await fetch(
      `http://localhost:8000/api/v1/translate/result/${taskId}`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    const { data: result } = await resultResponse.json();
    return result;
  } else if (data.status === 'FAILURE') {
    throw new Error(data.error);
  }
  
  // Hala işleniyor, tekrar kontrol et
  setTimeout(checkStatus, 2000);
};

// 4. Resimleri Göster
result.pages.forEach(page => {
  const img = document.createElement('img');
  img.src = page.processed_url; // Base64 data URL
  document.body.appendChild(img);
});
```

## ⚠️ Önemli Notlar

1. **Scraper Service:** `app/services/scraper_service.py` dosyasında hedef webtoon sitesine özel scraping mantığını implemente etmeniz gerekiyor.

2. **Polling:** Durum kontrolü için 2-3 saniyede bir istek gönderin.

3. **Token:** Access token'ı güvenli saklayın ve her istekte gönderin.

4. **Cache:** Aynı bölümü tekrar çevirmek isterseniz, cache'den anında döner (maliyet yok).

## 🐛 Sorun Giderme

### Servisler başlamıyor
```bash
CHECK.bat
```

### Redis hatası
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### Port zaten kullanılıyor
- FastAPI: `main.py` dosyasında port değiştirin
- Redis: Docker container'ı durdurun

---

**Detaylı dokümantasyon:** `DOC/` klasörüne bakın.

