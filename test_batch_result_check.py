"""
Check batch translation result and files
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Test kullanıcı bilgileri
test_user = {
    "username": "test",
    "password": "test123"
}

def login():
    """Login and get token"""
    try:
        response = requests.post(
            f"{API_V1}/auth/login",
            json=test_user,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            token = data.get("access_token")
            if token:
                return token
        return None
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        return None

def check_task_result(task_id, token):
    """Check task result"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_V1}/translate/status/{task_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("data", {})
        return None
    except Exception as e:
        print(f"[ERROR] Status check error: {str(e)}")
        return None

def check_files():
    """Check if files were saved"""
    storage_path = Path("storage/martial-peak/en_to_tr")
    
    if not storage_path.exists():
        print("[WARN] Storage path does not exist")
        return []
    
    chapters = []
    for chapter_dir in sorted(storage_path.glob("chapter_*")):
        if chapter_dir.is_dir():
            pages = list(chapter_dir.glob("page_*.jpg")) + list(chapter_dir.glob("page_*.png"))
            chapters.append({
                "chapter": chapter_dir.name,
                "pages": len(pages),
                "path": str(chapter_dir)
            })
    
    return chapters

if __name__ == "__main__":
    print("="*60)
    print("  BATCH TRANSLATION RESULT CHECK")
    print("="*60)
    print()
    
    # Check files
    print("[1/2] Checking saved files...")
    chapters = check_files()
    
    if chapters:
        print(f"[OK] Found {len(chapters)} chapters:")
        for ch in chapters:
            print(f"  - {ch['chapter']}: {ch['pages']} pages")
            print(f"    Path: {ch['path']}")
    else:
        print("[WARN] No chapters found in storage")
    
    print()
    print("[2/2] Checking task status...")
    token = login()
    if token:
        # Son task ID'yi kontrol et (test scriptinden)
        # Burada manuel olarak son task ID'yi girebilirsiniz
        print("[INFO] To check specific task, use:")
        print("  GET /api/v1/translate/status/{task_id}")
    else:
        print("[FAIL] Cannot login to check task status")
    
    print()
    print("="*60)

