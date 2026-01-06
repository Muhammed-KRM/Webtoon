"""
AsuraComic.net Scraper
"""
import re
import asyncio
from typing import List, Dict
from bs4 import BeautifulSoup
from loguru import logger
from app.services.scrapers.base_scraper import BaseScraper


class AsuraScraper(BaseScraper):
    """Scraper for asuracomic.net"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://asurascans.com.tr"  # Updated to .com.tr domain
    
    async def fetch_chapter_images(self, chapter_url: str) -> List[bytes]:
        """
        Fetch images from AsuraScans.com.tr chapter
        
        AsuraScans uses a reader container with img tags, typically in a div with class "reading-content"
        """
        try:
            logger.info(f"Fetching AsuraScans chapter: {chapter_url}")
            
            # Get the chapter page
            response = await self.client.get(chapter_url)
            response.raise_for_status()
            html = response.text
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
            
            # Download images in parallel
            images = await self._download_images_parallel(unique_urls)
            
            return images
            
        except Exception as e:
            logger.error(f"Error fetching AsuraScans images: {e}")
            raise
    
    async def _download_images_parallel(self, image_urls: List[str]) -> List[bytes]:
        """Download multiple images in parallel"""
        tasks = [self.download_image(url) for url in image_urls]
        images = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_images = [img for img in images if isinstance(img, bytes)]
        logger.info(f"Downloaded {len(valid_images)}/{len(image_urls)} images")
        return valid_images
    
    async def analyze_url(self, url: str) -> Dict:
        """Analyze AsuraComic URL"""
        try:
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
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

