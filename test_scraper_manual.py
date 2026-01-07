"""
Manuel Scraper Test - AsuraScans URL test
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.scraper_service import ScraperService
from loguru import logger

async def test_scraper():
    """Test scraper with real URL"""
    url = "https://asurascans.com.tr/manga/martial-peak/bolum-20/"
    
    print("="*60)
    print("  SCRAPER MANUEL TEST")
    print("="*60)
    print(f"\nURL: {url}")
    print("\n[1/3] Scraper service initializing...")
    
    scraper = ScraperService()
    
    try:
        print("[2/3] Fetching images from URL...")
        logger.info(f"Starting scraper test for: {url}")
        
        images = await scraper.fetch_chapter_images(url)
        
        print(f"\n[OK] Successfully fetched {len(images)} images")
        print(f"[INFO] First image size: {len(images[0]) if images else 0} bytes")
        print(f"[INFO] Total data size: {sum(len(img) for img in images)} bytes")
        
        return True, images
        
    except Exception as e:
        print(f"\n[FAIL] Error fetching images: {str(e)}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        import traceback
        print(f"\n[TRACEBACK]:\n{traceback.format_exc()}")
        return False, None
        
    finally:
        print("\n[3/3] Closing scraper...")
        await scraper.close()
        print("[OK] Scraper closed")

if __name__ == "__main__":
    success, images = asyncio.run(test_scraper())
    
    print("\n" + "="*60)
    if success:
        print("[OK] TEST BASARILI")
    else:
        print("[FAIL] TEST BASARISIZ")
    print("="*60)

