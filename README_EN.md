# 🚀 Webtoon AI Translator

Professional webtoon machine translation application. Enterprise-level translation platform supported by image processing (Computer Vision), natural language processing (NLP), and asynchronous workflows.

## ✨ Features

- **Automatic Web Scraping** - Downloads images from webtoon sites automatically
- **Smart OCR** - Detects and reads text in images using EasyOCR
- **Context-Aware Translation** - OpenAI GPT-4o-mini with character name and tone consistency
- **Cached Input** - 50% cost savings on system prompts
- **Image Processing** - Text bubble cleaning (in-painting) and target language text placement
- **Smart Text Fitting** - Automatic font size adjustment and multi-line support
- **Asynchronous Processing** - Celery + Redis background processing
- **Multi-Language Support** - 30+ languages, any language pair
- **Batch Translation** - Process chapter ranges automatically
- **File Organization** - Automatic folder structure by series and language pair
- **Layered Architecture** - Ranker project style Operations/Services separation

## 🏗️ Architecture

```
app/
├── api/v1/endpoints/  # Controllers (Request handling, validation)
├── operations/        # Managers (Workflow orchestration - Celery tasks)
├── services/          # Atomic technical tasks (OCR, Translation, Image Processing)
│   └── scrapers/     # Site-specific scrapers (Webtoons, AsuraScans)
├── models/            # Database models
├── schemas/           # DTOs (Pydantic models)
├── core/              # Config, DI, BaseResponse, Security
└── db/                # Database session management
```

## 🚀 Quick Start

### 1. First Time Setup

```bash
SETUP.bat
```

### 2. Configure Environment

Edit `.env` file:
- `SECRET_KEY`: At least 32 characters
- `OPENAI_API_KEY`: Your API key
- `DATABASE_URL`: SQLite or PostgreSQL

**Details:** `ENV_OLUSTUR.md` and `DOC/API_KEY_REHBERI.md`

### 3. Start Project

```bash
START.bat
```

This will:
- ✅ Start Redis (Docker)
- ✅ Start Celery Worker (separate window)
- ✅ Start FastAPI (separate window)
- ✅ Open browser automatically (http://localhost:8000/docs)

## 📚 API Usage

### Single Chapter Translation

**Endpoint:** `POST /api/v1/translate/start`

```json
{
  "chapter_url": "https://www.webtoons.com/en/action/eleceed/episode-364/viewer?title_no=1571&episode_no=364",
  "source_lang": "en",
  "target_lang": "tr",
  "mode": "clean",
  "series_name": "Eleceed"
}
```

### Batch Translation (Chapter Range)

**Endpoint:** `POST /api/v1/translate/batch/range`

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

## 🌐 Supported Sites

### ✅ Webtoons.com
- **URL:** `https://www.webtoons.com/en/genre/title/episode/viewer?title_no=XXX&episode_no=YYY`
- **Status:** Implemented (needs testing)

### ✅ AsuraScans.com.tr
- **URL:** `https://asurascans.com.tr/manga/title/chapter-XXX/`
- **Status:** Implemented (needs testing)

## 🌍 Multi-Language Support

**30+ languages supported!** Any language pair:
- English → Turkish
- Korean → English
- Japanese → Spanish
- And many more...

**Full list:** `app/services/language_detector.py`

## 📁 File Organization

When `series_name` is provided, chapters are saved to:

```
storage/
  {series_name}/
    {source_lang}_to_{target_lang}/
      chapter_0001/
        page_001.jpg
        page_002.jpg
        ...
        metadata.json
```

## 🔧 Management Commands

| Command | Description |
|---------|-------------|
| `SETUP.bat` | First-time setup |
| `START.bat` | Start all services |
| `STOP.bat` | Stop all services |
| `RESTART.bat` | Restart all services |
| `CHECK.bat` | Check service status |

## 📖 Documentation

- **Project Status:** `PROJECT_STATUS.md`
- **Usage Guide:** `DOC/USAGE_GUIDE.md`
- **Complete Features:** `DOC/COMPLETE_FEATURES.md`
- **API Key Guide:** `DOC/API_KEY_REHBERI.md`
- **Setup Guide:** `KURULUM.md`

## 🛠️ Technology Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL / SQLite
- **Task Queue:** Celery + Redis
- **OCR:** EasyOCR
- **Translation:** OpenAI GPT-4o-mini (Cached Input)
- **Image Processing:** OpenCV + Pillow

## ⚠️ Important Notes

1. **Scraper Testing:** Scrapers are implemented but need real-world testing with actual links.

2. **API Key:** Add your OpenAI API key to `.env` file and load credits.

3. **Font Files:** Add Turkish character support fonts to `fonts/` folder (optional).

## 📝 License

This project is for educational purposes.

---

**Status:** ✅ Complete and Ready to Use!

**Last Updated:** January 6, 2026

