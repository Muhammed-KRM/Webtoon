"""
Test URL generator
"""
from app.services.url_generator import URLGenerator

base_url = "https://asurascans.com.tr/manga/martial-peak/bolum-20/"
chapter_numbers = [20, 21, 22, 23, 24]

print("="*60)
print("  URL GENERATOR TEST")
print("="*60)
print(f"\nBase URL: {base_url}")
print(f"Chapter numbers: {chapter_numbers}")
print("\nGenerated URLs:")

urls = URLGenerator.generate_chapter_urls(base_url, chapter_numbers)

for i, url in enumerate(urls, 1):
    print(f"  {i}. {url}")
    
    # Check if URL is correct
    expected = base_url.replace("bolum-20", f"bolum-{chapter_numbers[i-1]}")
    if url == expected:
        print(f"      [OK] DOGRU")
    else:
        print(f"      [FAIL] YANLIS (Beklenen: {expected})")

print("\n" + "="*60)

