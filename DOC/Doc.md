Bu proje, sadece bir "çeviri aracı" değil, içinde görüntü işleme (Computer Vision), doğal dil işleme (NLP) ve asenkron iş akışları barındıran kompleks bir mühendislik ürünü olacak. **Ranker** projenindeki kurumsal mimariyi (Layered Architecture) temel alarak, Python ekosisteminin en profesyonel araçlarıyla bir "Geliştirme Dokümanı" hazırladım.

---

## 🚀 Webtoon AI Translator - Teknik Spesifikasyon Dokümanı

### 1. Teknoloji Yığını (Tech Stack)

| Katman | Teknoloji | .NET Karşılığı / Neden? |
| --- | --- | --- |
| **Backend Framework** | **FastAPI** | ASP.NET Core API (Asenkron ve çok hızlı) |
| **Task Queue (Kritik)** | **Celery + Redis** | Hangfire / RabbitMQ (Resim işleme uzun sürer, request'i bloklamamak için şart) |
| **Database (RDBMS)** | **PostgreSQL** | MS SQL Server |
| **Caching** | **Redis** | IDistributedCache (Sık sorulan bölümleri cache'lemek için) |
| **ORM** | **SQLAlchemy** | Entity Framework Core |
| **OCR Engine** | **EasyOCR / PaddleOCR** | Görüntüden metin okuma |
| **Translation Engine** | **OpenAI GPT-4o-mini** | Bağlam (Context) korumalı çeviri için |
| **Image Processing** | **OpenCV + Pillow** | Görüntü temizleme ve metin basma |
| **Auth** | **JWT (OAuth2)** | Identity Server / JWT Bearer |

---

### 2. Mimari ve Katman Yapısı

Proje, senin Ranker projesinde kullandığın **Operations/Services** ayrımını takip edecek:

* **API (Controllers):** Request karşılar, validasyon yapar.
* **Operations (Managers):** İş akışını yönetir (Örn: Önce indir, sonra çevir, sonra temizle).
* **Services:** Atomik teknik işleri yapar (Örn: Sadece OCR yap, sadece DB'ye yaz).

---

### 3. Endpoint Tanımları (API Design)

Tüm yanıtlar Ranker'daki gibi bir `BaseResponse<T>` içinde dönecek: `{ "data": T, "success": bool, "message": string }`

#### A. Auth & User (Ranker AuthController Muadili)

* `POST /auth/register`: Yeni kullanıcı kaydı.
* `POST /auth/login`: Token üretimi.
* `GET /auth/me`: Giriş yapan kullanıcı bilgisi.

#### B. Webtoon Scraper & Management

* `GET /webtoon/search?url=...`: Hedef siteyi analiz eder, bölüm listesini getirir.
* `GET /webtoon/chapter/{id}/pages`: Bölümdeki orijinal resim URL'lerini getirir.

#### C. Translation Pipeline (Asenkron İşlemler)

* `POST /translate/start`: Çeviri işlemini başlatır. (Hemen `TaskID` döner, kullanıcıyı bekletmez).
* **Request:** `{ chapter_id: int, target_lang: string }`


* `GET /translate/status/{taskId}`: İşlemin % kaçta olduğunu döner (Redis üzerinden).
* `GET /translate/result/{chapter_id}`: Tamamlanmış resimlerin listesini döner.

#### D. Admin Panel

* `DELETE /admin/clear-cache`: Redis ve diskteki geçici dosyaları temizler.
* `GET /admin/logs`: Sistem hatalarını listeler (Serilog/NLog muadili).

---

### 4. Fonksiyonel Gereksinimler & Mantıksal Akış

#### 1. Tutarlı Çeviri Algoritması (Context-Aware)

* **Fonksiyon:** `get_chapter_context_translation(texts: List[str])`
* **Mantık:** Bölümdeki tüm metinler tek bir prompt ile AI'ya gönderilir. AI'ya "Karakterlerin isim listesi budur, konuşma tonu şudur" bilgisi (System Prompt) verilir.

#### 2. Akıllı Görüntü Temizleme (In-painting)

* **Fonksiyon:** `clean_and_fill_bubble(image, mask)`
* **Mantık:** OCR'dan gelen koordinatlar kullanılarak metin silinir. `cv2.inpaint` ile arka plan dokusu (gradient veya doku) boşluğa kopyalanır.

#### 3. Dinamik Font ve Yerleştirme

* **Fonksiyon:** `fit_text_to_bubble(text, bubble_area)`
* **Mantık:** Metin uzunluğuna göre font boyutu (`FontSize`) otomatik küçültülür. Metin, balonun tam ortasına (Center-align) yerleştirilir.

---

### 5. Profesyonel Optimizasyonlar (Speed & Efficiency)

1. **Distributed Task Processing:** Resim işleme (OCR + Edit) çok CPU tüketir. Celery kullanarak bu işi 4-5 farklı "Worker"a dağıtabiliriz. Sen 1. sayfayı okurken Worker arka planda 10. sayfayı hazırlıyor olur.
2. **Image Caching:** Aynı bölümü başka bir kullanıcı istediğinde her şeyi baştan yapmamak için işlenmiş resimler S3 veya CDN üzerinde cache'lenir.
3. **Lazy Loading (Angular):** UI tarafında tüm bölümü bir kerede yüklemek yerine, kullanıcı aşağı kaydırdıkça resimleri çeken bir mekanizma (Intersection Observer) kurulur.

---

### 6. UI İçin Veri Modelleri (DTOs)

**Request (UI -> API):**

```typescript
interface TranslationRequest {
  targetUrl: string;
  quality: 'high' | 'fast'; // Hızlı ama az kaliteli veya yavaş ama mükemmel
  mode: 'overlay' | 'clean'; // Metni üstüne mi yazsın yoksa balonları temizlesin mi?
}

```

**Response (API -> UI):**

```typescript
interface ChapterResponse {
  chapterTitle: string;
  pages: {
    index: number;
    processedUrl: string; // İşlenmiş resmin URL'si
    originalText: string;
    translatedText: string;
    bubbles: { x: number, y: number, w: number, h: number }[]; // UI'da metin üzerine gelince orijinali göstermek için
  }[];
}

```

---

### 7. Güvenlik & Yetkilendirme (Permissions)

* **Guest:** Sadece önizleme (ilk 3 sayfa) görebilir.
* **User:** Kendi çeviri taleplerini oluşturabilir ve geçmişini görebilir.
* **Admin:** Tüm sistem cache'ini yönetebilir, API anahtarlarını güncelleyebilir ve limitleri (Rate Limit) belirleyebilir.

### Bir Sonraki Adım:

Bu döküman üzerinden mutabık kalırsak, ilk olarak **"Base Project Setup"** (FastAPI + Dependency Injection + BaseResponse) kurulumunu yapıp, ardından **Scraper Service** ile resimleri hedef siteden yakalamaya başlayabiliriz.

Bu dökümanda eklememi veya değiştirmemi istediğin bir "Pro Özellik" var mı? (Örn: Resimlerin kalitesini artırmak için AI Upscaling ekleyebiliriz). Would you like me to start with the Project Skeleton?