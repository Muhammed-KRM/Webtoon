# 📖 Webtoon AI Translator - Usage Guide

## 🌍 Multi-Language Support

The system now supports translation between **any language pair** (30+ languages).

### Supported Languages

- **en** - English
- **tr** - Turkish
- **es** - Spanish
- **fr** - French
- **de** - German
- **it** - Italian
- **pt** - Portuguese
- **ru** - Russian
- **ja** - Japanese
- **ko** - Korean
- **zh** - Chinese
- And 20+ more languages...

**Full list:** See `app/services/language_detector.py`

## 🔗 How to Use - Single Chapter

### Step 1: Start Translation

**Endpoint:** `POST /api/v1/translate/start`

**Request:**
```json
{
  "chapter_url": "https://www.webtoons.com/en/action/eleceed/episode-364/viewer?title_no=1571&episode_no=364",
  "source_lang": "en",
  "target_lang": "tr",
  "mode": "clean",
  "series_name": "Eleceed"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Translation started",
  "data": {
    "task_id": "abc123-def456-ghi789"
  }
}
```

### Step 2: Check Status

**Endpoint:** `GET /api/v1/translate/status/{task_id}`

Poll every 2-3 seconds until status is "SUCCESS".

### Step 3: Get Result

**Endpoint:** `GET /api/v1/translate/result/{task_id}`

Returns processed images as base64.

## 📚 How to Use - Batch Translation (Chapter Range)

### Method 1: Chapter Range

**Endpoint:** `POST /api/v1/translate/batch/range`

**Request:**
```json
{
  "series_url": "https://www.webtoons.com/en/action/eleceed/episode-{}/viewer?title_no=1571&episode_no={}",
  "chapter_range": "1-10",
  "source_lang": "en",
  "target_lang": "tr",
  "mode": "clean",
  "series_name": "Eleceed"
}
```

**Chapter Range Formats:**
- `"1-10"` - Chapters 1 to 10
- `"5,7,9"` - Chapters 5, 7, and 9
- `"1-5,10-15"` - Chapters 1-5 and 10-15

### Method 2: Start-End Range

**Endpoint:** `POST /api/v1/translate/batch/start`

**Request:**
```json
{
  "base_url": "https://www.webtoons.com/en/action/eleceed/episode-{}/viewer?title_no=1571&episode_no={}",
  "start_chapter": 1,
  "end_chapter": 10,
  "source_lang": "en",
  "target_lang": "tr",
  "mode": "clean",
  "series_name": "Eleceed"
}
```

## 📁 File Organization

When `series_name` is provided, chapters are automatically saved to:

```
storage/
  {series_name}/
    {source_lang}_to_{target_lang}/
      chapter_0001/
        page_001.jpg
        page_002.jpg
        ...
        metadata.json
      chapter_0002/
        ...
```

**Example:**
```
storage/
  Eleceed/
    en_to_tr/
      chapter_0001/
        page_001.jpg
        page_002.jpg
        metadata.json
      chapter_0002/
        ...
```

## 🌐 Language Examples

### English to Turkish
```json
{
  "source_lang": "en",
  "target_lang": "tr"
}
```

### Korean to English
```json
{
  "source_lang": "ko",
  "target_lang": "en"
}
```

### Japanese to Spanish
```json
{
  "source_lang": "ja",
  "target_lang": "es"
}
```

## 🔍 Supported Sites

### ✅ Webtoons.com
- **URL Format:** `https://www.webtoons.com/en/genre/title/episode/viewer?title_no=XXX&episode_no=YYY`
- **Example:** https://www.webtoons.com/en/action/eleceed/episode-364/viewer?title_no=1571&episode_no=364

### ✅ AsuraScans.com.tr
- **URL Format:** `https://asurascans.com.tr/manga/title/chapter-XXX/`
- **Example:** https://asurascans.com.tr/manga/martial-peak/bolum-3851/

## 📝 Notes

1. **Automatic Language Detection:** If `source_lang` is not provided, the system tries to detect it from the URL.

2. **File Saving:** Chapters are only saved to disk if `series_name` is provided in the request.

3. **Batch Processing:** Batch translations process chapters sequentially. Large ranges may take time.

4. **Cache:** Same chapter translations are cached (no cost for repeated translations).

---

**For detailed API documentation:** http://localhost:8000/docs

