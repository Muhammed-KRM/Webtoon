"""
Test Celery task directly
"""
from app.core.celery_app import celery_app
from app.operations.translation_manager import process_chapter_task
import time

print("="*60)
print("  CELERY TASK DIRECT TEST")
print("="*60)

# Test task
chapter_url = "https://asurascans.com.tr/manga/martial-peak/bolum-20/"
print(f"\n[INFO] Starting task for: {chapter_url}")
print("[INFO] This will test if the task can be called directly")

try:
    # Call task directly (not async)
    print("[INFO] Calling task directly (synchronous)...")
    result = process_chapter_task(
        chapter_url=chapter_url,
        target_lang="tr",
        source_lang="en",
        mode="clean",
        use_cache=False,
        series_name="martial-peak",
        translate_type=2  # FREE
    )
    print(f"[OK] Task completed!")
    print(f"[OK] Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
except Exception as e:
    print(f"[FAIL] Task failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)

