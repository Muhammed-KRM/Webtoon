"""
AsuraComic.net Scraper
"""
import re
import asyncio
from typing import List, Dict
from bs4 import BeautifulSoup
from loguru import logger
import undetected_chromedriver as uc
import time
from app.services.scrapers.base_scraper import BaseScraper


class AsuraScraper(BaseScraper):
    """Scraper for asuracomic.net"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://asurascans.com.tr"  # Updated to .com.tr domain
        # Use undetected-chromedriver for Cloudflare bypass
        # Note: Non-headless mode required for Cloudflare bypass
        self.driver = None
    
    async def fetch_chapter_images(self, chapter_url: str) -> List[bytes]:
        """
        Fetch images from AsuraScans.com.tr chapter
        
        AsuraScans uses a reader container with img tags, typically in a div with class "reading-content"
        """
        try:
            logger.info(f"Fetching AsuraScans chapter: {chapter_url}")
            
            # Get the chapter page using undetected-chromedriver (Cloudflare bypass)
            def fetch_with_selenium(url):
                # Initialize driver if not already done
                if self.driver is None:
                    logger.info("[SCRAPER] Initializing Chrome driver...")
                    options = uc.ChromeOptions()
                    # Try headless mode first (works in Celery worker)
                    # If Cloudflare blocks, we'll need to use non-headless
                    try:
                        # For Celery worker, we need headless mode
                        import os
                        if os.getenv('CELERY_WORKER', '').lower() == 'true' or 'celery' in os.getenv('_', '').lower():
                            # Running in Celery worker - use headless
                            options.add_argument('--headless=new')
                            logger.info("[SCRAPER] Using headless mode (Celery worker detected)")
                        else:
                            # Running in main process - try non-headless for Cloudflare
                            logger.info("[SCRAPER] Using non-headless mode (main process)")
                    except:
                        # Default to headless for safety
                        options.add_argument('--headless=new')
                        logger.info("[SCRAPER] Using headless mode (default)")
                    
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--window-size=1920,1080')
                    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                    
                    try:
                        self.driver = uc.Chrome(options=options, version_main=None)
                        logger.info("[SCRAPER] Chrome driver initialized successfully")
                    except Exception as e:
                        logger.error(f"[SCRAPER] Failed to initialize Chrome driver: {e}")
                        raise
                
                logger.info(f"[SCRAPER] Fetching URL: {url}")
                self.driver.get(url)
                # Wait for Cloudflare challenge to complete
                logger.info("[SCRAPER] Waiting for page to load (10 seconds)...")
                time.sleep(10)  # Wait for page to load
                logger.info("[SCRAPER] Page loaded, getting HTML...")
                html = self.driver.page_source
                logger.info(f"[SCRAPER] HTML retrieved, length: {len(html)}")
                return html
            
            html = await asyncio.to_thread(fetch_with_selenium, chapter_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            image_urls = []
            
            # Method 1: Look for reading-content container (most common in AsuraScans)
            reading_content = soup.find('div', {'class': re.compile(r'.*reading-content.*', re.I)})
            if reading_content:
                imgs = reading_content.find_all('img')
                for img in imgs:
                    img_url = (
                        img.get('data-src') or 
                        img.get('data-lazy-src') or 
                        img.get('src') or
                        img.get('data-url') or
                        img.get('data-original')
                    )
                    
                    if img_url:
                        img_url = img_url.strip()
                        
                        # Handle relative URLs
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = self.base_url + img_url
                        elif not img_url.startswith('http'):
                            img_url = self.base_url + '/' + img_url
                        
                        # Filter out placeholder/loading images
                        if any(skip in img_url.lower() for skip in ['placeholder', 'loading', 'spinner', 'blank', 'logo', 'banner']):
                            continue
                        
                        # Only add if it looks like an image URL
                        if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                            if img_url not in image_urls:
                                image_urls.append(img_url)
            
            # Method 2: Look for reader/chapter containers
            if not image_urls:
                reader_divs = soup.find_all('div', {'class': re.compile(r'.*(reader|chapter|content|wp-manga).*', re.I)})
                for div in reader_divs:
                    imgs = div.find_all('img')
                    for img in imgs:
                        img_url = img.get('data-src') or img.get('src') or img.get('data-lazy-src')
                        if img_url:
                            img_url = img_url.strip()
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            elif img_url.startswith('/'):
                                img_url = self.base_url + img_url
                            elif not img_url.startswith('http'):
                                img_url = self.base_url + '/' + img_url
                            
                            if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                if img_url not in image_urls and 'logo' not in img_url.lower():
                                    image_urls.append(img_url)
            
            # Method 3: Look for all img tags (fallback)
            if not image_urls:
                all_imgs = soup.find_all('img')
                for img in all_imgs:
                    img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if img_url:
                        img_url = img_url.strip()
                        if not img_url.startswith('http'):
                            img_url = 'https:' + img_url if img_url.startswith('//') else self.base_url + img_url
                        
                        # Filter out non-chapter images
                        if any(skip in img_url.lower() for skip in ['logo', 'banner', 'avatar', 'icon', 'ad', 'ads']):
                            continue
                        
                        if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            if img_url not in image_urls:
                                image_urls.append(img_url)
            
            # Method 4: Look in JavaScript (for lazy-loaded images)
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Look for image URLs in JavaScript
                    urls = re.findall(r'["\'](https?://[^"\']*\.(?:jpg|jpeg|png|webp|gif))["\']', script.string, re.I)
                    for url in urls:
                        # Filter out non-chapter images
                        if any(skip in url.lower() for skip in ['logo', 'banner', 'avatar', 'icon', 'ad']):
                            continue
                        if url not in image_urls:
                            image_urls.append(url)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in image_urls:
                if url and url not in seen:
                    seen.add(url)
                    unique_urls.append(url)
            
            if not unique_urls:
                raise ValueError(f"No images found in chapter: {chapter_url}")
            
            logger.info(f"Found {len(unique_urls)} images, downloading...")
            
            # Download images in parallel with referer
            images = await self._download_images_parallel(unique_urls, chapter_url=chapter_url)
            
            return images
            
        except Exception as e:
            logger.error(f"Error fetching AsuraScans images: {e}")
            raise
    
    async def _download_images_parallel(self, image_urls: List[str], chapter_url: str = None) -> List[bytes]:
        """Download multiple images in parallel"""
        # Use httpx client for image downloads with referer header
        referer = chapter_url or self.base_url
        tasks = [self.download_image(url, referer=referer) for url in image_urls]
        images = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_images = [img for img in images if isinstance(img, bytes)]
        logger.info(f"Downloaded {len(valid_images)}/{len(image_urls)} images")
        return valid_images
    
    async def analyze_url(self, url: str) -> Dict:
        """Analyze AsuraComic URL"""
        try:
            # Use undetected-chromedriver for Cloudflare bypass
            def fetch_with_selenium(url):
                if self.driver is None:
                    options = uc.ChromeOptions()
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    self.driver = uc.Chrome(options=options, version_main=None)
                
                self.driver.get(url)
                time.sleep(10)
                return self.driver.page_source
            
            html = await asyncio.to_thread(fetch_with_selenium, url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_elem = (
                soup.find('h1', {'class': re.compile(r'.*(title|chapter).*', re.I)}) or
                soup.find('h1') or
                soup.find('title')
            )
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Chapter"
            
            # Count images
            reader_divs = soup.find_all('div', {'class': re.compile(r'.*(reader|chapter|content).*', re.I)})
            img_count = sum(len(div.find_all('img')) for div in reader_divs)
            
            return {
                "title": title,
                "page_count": img_count,
                "images": []
            }
        except Exception as e:
            logger.error(f"Error analyzing AsuraComic URL: {e}")
            return {
                "title": "Unknown",
                "page_count": 0,
                "images": []
            }
    
    async def close(self):
        """Close HTTP client and Selenium driver"""
        try:
            await self.client.aclose()
        except:
            pass
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except:
            pass

