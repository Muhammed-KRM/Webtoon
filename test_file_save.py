"""
Test file save functionality
"""
from app.services.file_manager import FileManager
from pathlib import Path

# Test data
series_name = "martial-peak"
chapter_number = 20
source_lang = "en"
target_lang = "tr"

# Create dummy image (1x1 pixel PNG)
import io
from PIL import Image

img = Image.new('RGB', (1, 1), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes = img_bytes.getvalue()

print("="*60)
print("  FILE SAVE TEST")
print("="*60)
print(f"\nSeries: {series_name}")
print(f"Chapter: {chapter_number}")
print(f"Language pair: {source_lang} -> {target_lang}")
print(f"Image size: {len(img_bytes)} bytes")

try:
    file_manager = FileManager()
    print(f"\n[INFO] Storage path: {file_manager.storage_path}")
    print(f"[INFO] Storage path exists: {file_manager.storage_path.exists()}")
    
    metadata = {
        "original_texts": ["Test text"],
        "translated_texts": ["Test metni"],
        "blocks": [{"text": "Test", "coords": [0, 0, 10, 10]}],
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    
    print("\n[INFO] Saving chapter...")
    storage_path = file_manager.save_chapter(
        series_name=series_name,
        chapter_number=chapter_number,
        pages=[img_bytes],
        metadata=metadata,
        source_lang=source_lang,
        target_lang=target_lang
    )
    
    print(f"[OK] Chapter saved to: {storage_path}")
    
    # Check if files exist
    expected_path = Path(storage_path)
    if expected_path.exists():
        files = list(expected_path.glob("page_*"))
        print(f"[OK] Found {len(files)} page files")
        for f in files[:3]:
            print(f"  - {f.name} ({f.stat().st_size} bytes)")
        
        metadata_file = expected_path / "metadata.json"
        if metadata_file.exists():
            print(f"[OK] Metadata file exists: {metadata_file}")
        else:
            print(f"[WARN] Metadata file not found")
    else:
        print(f"[FAIL] Storage path does not exist: {expected_path}")
    
except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)

