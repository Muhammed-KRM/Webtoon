"""
Translation background tasks
"""
from app.core.celery_app import celery_app

@celery_app.task(name="translate_chapter")
def translate_chapter_task(chapter_id: int, target_lang: str):
    """Background task for chapter translation"""
    # This will be implemented later
    return {"status": "completed", "chapter_id": chapter_id}
