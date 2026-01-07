"""
Test single chapter translation
"""
import requests
import json
import time

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
            return token
        return None
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        return None

def translate_single_chapter(token):
    """Translate a single chapter"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Single chapter translation
    data = {
        "chapter_url": "https://asurascans.com.tr/manga/martial-peak/bolum-20/",
        "target_lang": "tr",
        "source_lang": "en",
        "mode": "clean",
        "translate_type": 2  # FREE
    }
    
    try:
        print("[INFO] Sending single chapter translation request...")
        response = requests.post(
            f"{API_V1}/translate/start",
            json=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("data", {}).get("task_id")
            print(f"[OK] Translation started! Task ID: {task_id}")
            return task_id
        else:
            print(f"[FAIL] Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return None

def check_status(task_id, token):
    """Check translation status"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_V1}/translate/status/{task_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            status_data = result.get("data", {})
            return status_data
        return None
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("  SINGLE CHAPTER TRANSLATION TEST")
    print("="*60)
    print()
    
    token = login()
    if not token:
        print("[FAIL] Cannot login")
        exit(1)
    
    task_id = translate_single_chapter(token)
    if not task_id:
        print("[FAIL] Cannot start translation")
        exit(1)
    
    print(f"\n[INFO] Checking status (will check 20 times, 15 seconds apart)...")
    for i in range(20):
        status_data = check_status(task_id, token)
        if status_data:
            status = status_data.get("status")
            progress = status_data.get("progress", 0)
            message = status_data.get("message", "")
            print(f"[{i+1}/20] Status: {status}, Progress: {progress}%, Message: {message}")
            
            if status == "SUCCESS":
                print("\n[OK] Translation completed!")
                break
            elif status == "FAILED":
                error = status_data.get("error", "Unknown error")
                print(f"\n[FAIL] Translation failed: {error}")
                break
        
        time.sleep(15)
    
    print("\n" + "="*60)

