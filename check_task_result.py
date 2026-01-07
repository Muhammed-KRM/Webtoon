"""
Check batch translation task result details
"""
import requests
import json

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

def get_task_result(task_id, token):
    """Get task result"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get status first
        response = requests.get(
            f"{API_V1}/translate/status/{task_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            status_data = result.get("data", {})
            print(f"\n[STATUS] Status: {status_data.get('status')}")
            print(f"[STATUS] Progress: {status_data.get('progress')}%")
            print(f"[STATUS] Message: {status_data.get('message')}")
            
            # Get result if available
            result_data = status_data.get("result")
            if result_data:
                print(f"\n[RESULT] Result type: {type(result_data)}")
                if isinstance(result_data, dict):
                    print(f"[RESULT] Keys: {list(result_data.keys())}")
                    print(f"[RESULT] Total chapters: {result_data.get('total_chapters', 'N/A')}")
                    print(f"[RESULT] Completed: {result_data.get('completed', 'N/A')}")
                    print(f"[RESULT] Failed: {result_data.get('failed', 'N/A')}")
                    print(f"[RESULT] Series name: {result_data.get('series_name', 'N/A')}")
                    
                    results = result_data.get("results", {})
                    if results:
                        print(f"\n[RESULTS] Chapter results:")
                        for ch_num, ch_result in list(results.items())[:3]:  # İlk 3 bölüm
                            print(f"  Chapter {ch_num}: {ch_result.get('status')}")
                            if ch_result.get('warning'):
                                print(f"    Warning: {ch_result.get('warning')}")
                else:
                    print(f"[RESULT] Result: {str(result_data)[:200]}")
            else:
                print("[RESULT] No result data available")
            
            return status_data
        else:
            print(f"[FAIL] Status check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("="*60)
    print("  TASK RESULT CHECK")
    print("="*60)
    print()
    
    # Son task ID (test scriptinden)
    task_id = input("Enter task ID (or press Enter to use last test task): ").strip()
    if not task_id:
        task_id = "d5f2d3bc-5539-4549-a80b-eb3e564d8974"  # Son test task ID
    
    token = login()
    if not token:
        print("[FAIL] Cannot login")
        exit(1)
    
    get_task_result(task_id, token)
    
    print("\n" + "="*60)

