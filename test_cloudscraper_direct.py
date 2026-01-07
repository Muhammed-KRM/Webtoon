"""
Direct cloudscraper test
"""
import cloudscraper
from bs4 import BeautifulSoup

url = "https://asurascans.com.tr/manga/martial-peak/bolum-20/"

print("Testing cloudscraper with different configurations...")

# Test 1: Default cloudscraper
print("\n[1] Testing default cloudscraper...")
try:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS!")
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
    else:
        print(f"FAILED: {response.status_code}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Chrome browser emulation
print("\n[2] Testing Chrome browser emulation...")
try:
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    response = scraper.get(url, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS!")
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
    else:
        print(f"FAILED: {response.status_code}")
        print(f"Response text (first 500 chars): {response.text[:500]}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 3: Firefox browser emulation
print("\n[3] Testing Firefox browser emulation...")
try:
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'desktop': True
        }
    )
    response = scraper.get(url, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS!")
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
    else:
        print(f"FAILED: {response.status_code}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 4: With delay
print("\n[4] Testing with delay...")
import time
try:
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    time.sleep(2)  # Delay before request
    response = scraper.get(url, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS!")
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
    else:
        print(f"FAILED: {response.status_code}")
except Exception as e:
    print(f"ERROR: {e}")

