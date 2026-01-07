"""
Test Batch Translation for Martial Peak chapters 20-30
"""
import requests
import json
import time
import sys

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
                print(f"[OK] Login successful. Token: {token[:20]}...")
                return token
            else:
                print("[FAIL] Token not found in response")
                return None
        else:
            print(f"[FAIL] Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        return None

def start_batch_translation(token):
    """Start batch translation for chapters 20-30"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Batch translation request
    request_data = {
        "base_url": "https://asurascans.com.tr/manga/martial-peak/bolum-20/",
        "start_chapter": 20,
        "end_chapter": 30,
        "source_lang": "en",  # veya otomatik tespit
        "target_lang": "tr",
        "mode": "clean",
        "series_name": "martial-peak",
        "translate_type": 2  # Free translation (daha hızlı test için)
    }
    
    print("\n" + "="*60)
    print("  BATCH TRANSLATION REQUEST")
    print("="*60)
    print(f"Base URL: {request_data['base_url']}")
    print(f"Chapters: {request_data['start_chapter']} - {request_data['end_chapter']}")
    print(f"Series: {request_data['series_name']}")
    print(f"Translate Type: {'FREE' if request_data['translate_type'] == 2 else 'AI'}")
    print("="*60 + "\n")
    
    try:
        print("[INFO] Sending batch translation request...")
        response = requests.post(
            f"{API_V1}/translate/batch/start",
            json=request_data,
            headers=headers,
            timeout=30
        )
        
        print(f"[INFO] Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"[OK] Batch translation started!")
            print(f"\nResponse:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
            
            task_id = result.get("data", {}).get("task_id")
            if task_id:
                print(f"\n[INFO] Task ID: {task_id}")
                print(f"[INFO] You can check status at: {API_V1}/translate/status/{task_id}")
                return task_id
            else:
                print("[WARN] Task ID not found in response")
                return None
        else:
            print(f"[FAIL] Batch translation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error starting batch translation: {str(e)}")
        import traceback
        traceback.print_exc()
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
            status = status_data.get("status", "UNKNOWN")
            progress = status_data.get("progress", 0)
            message = status_data.get("message", "")
            
            print(f"\n[STATUS] Status: {status}, Progress: {progress}%, Message: {message}")
            return status, progress
        else:
            print(f"[FAIL] Status check failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"[ERROR] Status check error: {str(e)}")
        return None, None

if __name__ == "__main__":
    print("="*60)
    print("  BATCH TRANSLATION TEST - MARTIAL PEAK 20-30")
    print("="*60)
    print()
    
    # Login
    token = login()
    if not token:
        print("\n[FAIL] Cannot proceed without authentication token")
        sys.exit(1)
    
    # Start batch translation
    task_id = start_batch_translation(token)
    if not task_id:
        print("\n[FAIL] Cannot proceed without task ID")
        sys.exit(1)
    
    # Check status a few times
    print("\n[INFO] Checking status (will check 5 times, 10 seconds apart)...")
    for i in range(5):
        time.sleep(10)
        status, progress = check_status(task_id, token)
        if status in ["COMPLETED", "FAILED"]:
            print(f"\n[INFO] Task finished with status: {status}")
            break
    
    print("\n" + "="*60)
    print("  TEST COMPLETED")
    print("="*60)
    print(f"\n[INFO] Check logs for detailed debug information")
    print(f"[INFO] Files should be saved in: storage/martial-peak/en_to_tr/")

