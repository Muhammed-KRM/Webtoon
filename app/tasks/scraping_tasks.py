"""
Scraping background tasks
"""
from app.core.celery_app import celery_app

@celery_app.task(name="scrape_webtoon")
def scrape_webtoon_task(url: str):
    """Background task for webtoon scraping"""
    return {"status": "completed", "url": url}
