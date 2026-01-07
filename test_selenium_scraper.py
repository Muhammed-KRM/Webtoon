"""
Selenium scraper test for Cloudflare bypass
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

url = "https://asurascans.com.tr/manga/martial-peak/bolum-20/"

print("="*60)
print("  SELENIUM SCRAPER TEST")
print("="*60)
print(f"\nURL: {url}")

# Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in background
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = None
try:
    print("\n[1/3] Starting Chrome driver...")
    driver = webdriver.Chrome(options=chrome_options)
    
    print("[2/3] Loading page...")
    driver.get(url)
    
    # Wait for Cloudflare challenge to complete (max 30 seconds)
    print("[INFO] Waiting for Cloudflare challenge...")
    try:
        # Wait until page title changes from "Just a moment..." or "Bir dakika lütfen..."
        WebDriverWait(driver, 30).until(
            lambda d: "Bir dakika" not in d.title and "Just a moment" not in d.title
        )
        print("[OK] Cloudflare challenge passed!")
    except:
        print("[WARN] Cloudflare challenge timeout, continuing anyway...")
    
    # Additional wait for page to fully load
    time.sleep(3)
    
    print("[3/3] Extracting HTML...")
    html = driver.page_source
    
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else "No title"
    print(f"\n[OK] Page loaded successfully!")
    print(f"[INFO] Page title: {title}")
    
    # Check for images
    reading_content = soup.find('div', class_=lambda x: x and 'reading-content' in x.lower())
    if reading_content:
        imgs = reading_content.find_all('img')
        print(f"[INFO] Found {len(imgs)} images in reading-content")
        for i, img in enumerate(imgs[:3]):  # Show first 3
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            print(f"  Image {i+1}: {src[:80] if src else 'No src'}...")
    else:
        print("[WARN] No reading-content div found")
    
    # Check if we got past Cloudflare
    if "Bir dakika" in html or "Just a moment" in html:
        print("\n[WARN] Still on Cloudflare challenge page")
    else:
        print("\n[OK] Successfully bypassed Cloudflare!")
        
except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if driver:
        print("\n[INFO] Closing browser...")
        driver.quit()
        print("[OK] Browser closed")

print("\n" + "="*60)

