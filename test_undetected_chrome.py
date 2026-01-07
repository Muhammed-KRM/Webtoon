"""
Undetected ChromeDriver test for Cloudflare bypass
"""
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

url = "https://asurascans.com.tr/manga/martial-peak/bolum-20/"

print("="*60)
print("  UNDETECTED CHROMEDRIVER TEST")
print("="*60)
print(f"\nURL: {url}")

driver = None
try:
    print("\n[1/3] Starting undetected Chrome driver...")
    options = uc.ChromeOptions()
    options.add_argument('--headless')  # Try headless first
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = uc.Chrome(options=options, version_main=None)
    
    print("[2/3] Loading page...")
    driver.get(url)
    
    # Wait for page to load
    print("[INFO] Waiting for page to load (10 seconds)...")
    time.sleep(10)
    
    print("[3/3] Extracting HTML...")
    html = driver.page_source
    
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else "No title"
    print(f"\n[OK] Page loaded!")
    print(f"[INFO] Page title: {title}")
    
    # Check for Cloudflare challenge
    if "Bir dakika" in html or "Just a moment" in html or "cloudflare" in html.lower():
        print("\n[WARN] Still on Cloudflare challenge page")
        print("[INFO] Trying without headless mode...")
        
        # Close and retry without headless
        driver.quit()
        time.sleep(2)
        
        options = uc.ChromeOptions()
        # Don't add headless this time
        driver = uc.Chrome(options=options, version_main=None)
        driver.get(url)
        print("[INFO] Waiting for page to load (15 seconds)...")
        time.sleep(15)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "No title"
        print(f"[INFO] Page title (non-headless): {title}")
        
        if "Bir dakika" not in html and "Just a moment" not in html:
            print("[OK] Successfully bypassed Cloudflare!")
        else:
            print("[FAIL] Still on Cloudflare challenge")
    else:
        print("\n[OK] Successfully bypassed Cloudflare!")
    
    # Check for images
    reading_content = soup.find('div', class_=lambda x: x and 'reading-content' in x.lower())
    if reading_content:
        imgs = reading_content.find_all('img')
        print(f"\n[INFO] Found {len(imgs)} images in reading-content")
        for i, img in enumerate(imgs[:5]):  # Show first 5
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                print(f"  Image {i+1}: {src[:100]}...")
    else:
        print("\n[WARN] No reading-content div found")
        # Try to find any images
        all_imgs = soup.find_all('img')
        print(f"[INFO] Found {len(all_imgs)} total images on page")
        
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

