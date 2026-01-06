"""
Web Scraper Service - Fetches images from webtoon sites
Uses adapter pattern to support multiple sites
"""
import re
from typing import List
from loguru import logger
from app.services.scrapers.base_scraper import BaseScraper
from app.services.scrapers.webtoons_scraper import WebtoonsScraper
from app.services.scrapers.asura_scraper import AsuraScraper


class ScraperService:
    """Service for scraping webtoon images with multi-site support"""
    
    def __init__(self):
        self.scrapers = {
            'webtoons.com': WebtoonsScraper(),
            'asurascans.com.tr': AsuraScraper(),
            'asuracomic.net': AsuraScraper(),
            'asuracomic.com': AsuraScraper(),
        }
    
    def _detect_site(self, url: str) -> str:
        """Detect which site the URL belongs to"""
        url_lower = url.lower()
        
        if 'webtoons.com' in url_lower or 'webtoon.com' in url_lower:
            return 'webtoons.com'
        elif 'asurascans.com.tr' in url_lower:
            return 'asurascans.com.tr'
        elif 'asuracomic.net' in url_lower or 'asuracomic.com' in url_lower:
            return 'asuracomic.net'
        else:
            # Default to AsuraScans for unknown sites (most similar structure)
            logger.warning(f"Unknown site for URL: {url}, using AsuraScans scraper")
            return 'asurascans.com.tr'
    
    def _get_scraper(self, url: str) -> BaseScraper:
        """Get appropriate scraper for the URL"""
        site = self._detect_site(url)
        return self.scrapers.get(site, self.scrapers['asuracomic.net'])
    
    async def fetch_chapter_images(self, chapter_url: str) -> List[bytes]:
        """
        Fetch all images from a chapter URL
        
        Automatically detects the site and uses appropriate scraper
        
        Args:
            chapter_url: URL of the webtoon chapter
            
        Returns:
            List of image bytes
        """
        try:
            logger.info(f"Fetching images from: {chapter_url}")
            
            scraper = self._get_scraper(chapter_url)
            images = await scraper.fetch_chapter_images(chapter_url)
            
            if not images:
                raise ValueError(f"No images found for URL: {chapter_url}")
            
            logger.info(f"Successfully fetched {len(images)} images")
            return images
            
        except Exception as e:
            logger.error(f"Error fetching images: {e}")
            raise
    
    async def analyze_url(self, url: str) -> dict:
        """
        Analyze a URL to extract chapter information
        
        Args:
            url: Webtoon chapter URL
            
        Returns:
            Dictionary with chapter info (title, page_count, etc.)
        """
        try:
            scraper = self._get_scraper(url)
            return await scraper.analyze_url(url)
        except Exception as e:
            logger.error(f"Error analyzing URL: {e}")
            return {
                "title": "Unknown Chapter",
                "page_count": 0,
                "images": []
            }
    
    async def close(self):
        """Close all scraper HTTP clients"""
        for scraper in self.scrapers.values():
            try:
                await scraper.close()
            except:
                pass
