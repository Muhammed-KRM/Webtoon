"""
Base Scraper Interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import httpx
from bs4 import BeautifulSoup
from loguru import logger


class BaseScraper(ABC):
    """Base class for webtoon site scrapers"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        )
    
    @abstractmethod
    async def fetch_chapter_images(self, chapter_url: str) -> List[bytes]:
        """Fetch all images from a chapter URL"""
        pass
    
    @abstractmethod
    async def analyze_url(self, url: str) -> Dict:
        """Analyze URL and extract chapter info"""
        pass
    
    async def download_image(self, img_url: str) -> bytes:
        """Download a single image"""
        try:
            response = await self.client.get(img_url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading image {img_url}: {e}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

