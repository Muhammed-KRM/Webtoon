"""
Webtoons.com Scraper
"""
import re
import json
import asyncio
from typing import List, Dict
from bs4 import BeautifulSoup
from loguru import logger
from app.services.scrapers.base_scraper import BaseScraper


class WebtoonsScraper(BaseScraper):
    """Scraper for webtoons.com"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.webtoons.com"
    
    async def fetch_chapter_images(self, chapter_url: str) -> List[bytes]:
        """
        Fetch images from webtoons.com chapter
        
        Webtoons.com uses API endpoints to load images. We extract title_no and episode_no
        from URL and call the API endpoint.
        """
        try:
            logger.info(f"Fetching Webtoons.com chapter: {chapter_url}")
            
            # Extract title_no and episode_no from URL
            # Format: https://www.webtoons.com/en/genre/title/episode/viewer?title_no=1571&episode_no=364
            title_no = self._extract_title_no(chapter_url)
            episode_no = self._extract_episode_no(chapter_url)
            
            if not title_no or not episode_no:
                raise ValueError(f"Could not extract title_no or episode_no from URL: {chapter_url}")
            
            # Webtoons.com loads images via JavaScript
            # Method 1: Try to extract from HTML page (viewer container)
            # Method 2: Look for JavaScript variables with image URLs
            # Method 3: Try API endpoint if available
            
            # First, get the HTML page
            response = await self.client.get(chapter_url)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            image_urls = []
            
            # Method 1: Look for viewer container with images
            viewer = soup.find('div', {'id': 'viewer'}) or soup.find('div', {'class': re.compile(r'.*viewer.*', re.I)})
            if viewer:
                imgs = viewer.find_all('img')
                for img in imgs:
                    img_url = img.get('data-url') or img.get('src') or img.get('data-src')
                    if img_url:
                        if not img_url.startswith('http'):
                            img_url = 'https:' + img_url if img_url.startswith('//') else self.base_url + img_url
                        if img_url not in image_urls and 'webtoon' in img_url.lower():
                            image_urls.append(img_url)
            
            # Method 2: Extract from JavaScript variables
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Look for image URLs in various JavaScript patterns
                    # Pattern 1: "imageUrl": "https://..."
                    urls = re.findall(r'["\'](https?://[^"\']*webtoon[^"\']*\.(?:jpg|jpeg|png|webp))["\']', script.string, re.I)
                    image_urls.extend(urls)
                    
                    # Pattern 2: imageUrl: "https://..."
                    urls = re.findall(r'imageUrl["\']?\s*[:=]\s*["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp))["\']', script.string, re.I)
                    image_urls.extend(urls)
                    
                    # Pattern 3: Array of image URLs
                    urls = re.findall(r'["\'](https?://[^"\']*webtoon[^"\']*\.(?:jpg|jpeg|png|webp))["\']', script.string, re.I)
                    image_urls.extend(urls)
            
            # Method 3: Try API endpoint (if available)
            if not image_urls:
                try:
                    api_url = f"https://www.webtoons.com/episodeViewer?titleNo={title_no}&episodeNo={episode_no}"
                    api_response = await self.client.get(api_url, headers={
                        "Referer": chapter_url,
                        "Accept": "application/json"
                    })
                    if api_response.status_code == 200:
                        try:
                            data = api_response.json()
                            # Extract image URLs from API response
                            def find_urls(obj, urls_list):
                                if isinstance(obj, dict):
                                    for key, value in obj.items():
                                        if 'image' in key.lower() and 'url' in key.lower():
                                            if isinstance(value, str) and value.startswith('http'):
                                                urls_list.append(value)
                                        else:
                                            find_urls(value, urls_list)
                                elif isinstance(obj, list):
                                    for item in obj:
                                        find_urls(item, urls_list)
                            
                            find_urls(data, image_urls)
                        except:
                            pass
                except:
                    pass
            
            # If still no images, try HTML parsing fallback
            if not image_urls:
                logger.warning("All methods failed, trying HTML parsing fallback...")
                # This will raise an error if no images found
                return await self._fetch_from_html(chapter_url)
            
            # Clean and validate URLs
            unique_urls = []
            for url in image_urls:
                if url and isinstance(url, str):
                    url = url.strip()
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif not url.startswith('http'):
                        continue
                    if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        if url not in unique_urls:
                            unique_urls.append(url)
            
            if not unique_urls:
                raise ValueError(f"No images found in API response for: {chapter_url}")
            
            logger.info(f"Found {len(unique_urls)} images from API, downloading...")
            
            # Download images in parallel
            images = await self._download_images_parallel(unique_urls)
            
            return images
            
        except Exception as e:
            logger.error(f"Error fetching Webtoons.com images: {e}")
            # Fallback to HTML parsing
            try:
                return await self._fetch_from_html(chapter_url)
            except:
                raise
    
    async def _fetch_from_html(self, chapter_url: str) -> List[bytes]:
        """Fallback method: Parse HTML to find images"""
        response = await self.client.get(chapter_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        image_urls = []
        
        # Look for viewer container
        viewer = soup.find('div', {'id': 'viewer'}) or soup.find('div', {'class': re.compile(r'.*viewer.*', re.I)})
        if viewer:
            imgs = viewer.find_all('img')
            for img in imgs:
                img_url = img.get('data-url') or img.get('src') or img.get('data-src')
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = 'https:' + img_url if img_url.startswith('//') else self.base_url + img_url
                    if img_url not in image_urls:
                        image_urls.append(img_url)
        
        # Look in JavaScript
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                urls = re.findall(r'["\'](https?://[^"\']*webtoon[^"\']*\.(?:jpg|jpeg|png|webp))["\']', script.string, re.I)
                image_urls.extend(urls)
        
        if not image_urls:
            raise ValueError(f"No images found in HTML for: {chapter_url}")
        
        return await self._download_images_parallel(list(set(image_urls)))
    
    def _extract_title_no(self, url: str) -> str:
        """Extract title_no from URL"""
        match = re.search(r'title_no=(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    def _extract_episode_no(self, url: str) -> str:
        """Extract episode_no from URL"""
        match = re.search(r'episode_no=(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    
    async def _download_images_parallel(self, image_urls: List[str]) -> List[bytes]:
        """Download multiple images in parallel"""
        tasks = [self.download_image(url) for url in image_urls]
        images = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_images = [img for img in images if isinstance(img, bytes)]
        logger.info(f"Downloaded {len(valid_images)}/{len(image_urls)} images")
        return valid_images
    
    async def analyze_url(self, url: str) -> Dict:
        """Analyze Webtoons.com URL"""
        try:
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Chapter"
            
            # Extract page count (count images)
            img_count = len(soup.find_all('img', {'class': re.compile(r'.*viewer.*', re.I)}))
            
            return {
                "title": title,
                "page_count": img_count,
                "images": []
            }
        except Exception as e:
            logger.error(f"Error analyzing Webtoons.com URL: {e}")
            return {
                "title": "Unknown",
                "page_count": 0,
                "images": []
            }

