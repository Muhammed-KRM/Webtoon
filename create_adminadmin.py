"""
Create first AdminAdmin user
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# İlk AdminAdmin kullanıcısı
adminadmin_data = {
    "username": "SystemAdmin",
    "email": "Admin@Admin.com",
    "password": "hashhash"
}

# Mevcut test admin kullanıcısı
test_admin_data = {
    "username": "test",
    "email": "test@test.com",
    "password": "test123"
}

def create_adminadmin():
    """Create first AdminAdmin user"""
    try:
        response = requests.post(
            f"{API_V1}/admin/users/create-adminadmin",
            json=adminadmin_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"[OK] AdminAdmin user created: {adminadmin_data['username']}")
            result = response.json()
            print(f"  Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"[FAIL] Failed to create AdminAdmin: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error creating AdminAdmin: {str(e)}")
        return False

def create_test_admin():
    """Create test admin user (requires AdminAdmin token)"""
    try:
        # First login as AdminAdmin
        login_data = {
            "username": adminadmin_data["username"],
            "password": adminadmin_data["password"]
        }
        
        login_response = requests.post(
            f"{API_V1}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"[FAIL] Failed to login as AdminAdmin: {login_response.status_code}")
            print(f"  Response: {login_response.text}")
            return False
        
        token_data = login_response.json()
        token = token_data.get("data", {}).get("access_token")
        
        if not token:
            print("[FAIL] Failed to extract token from login response")
            return False
        
        # Create admin user
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_V1}/admin/users/create-admin",
            json=test_admin_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"[OK] Test admin user created: {test_admin_data['username']}")
            result = response.json()
            print(f"  Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"[FAIL] Failed to create test admin: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error creating test admin: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  CREATING ADMINADMIN AND TEST ADMIN USERS")
    print("="*60)
    print()
    
    print("[1/2] Creating AdminAdmin user...")
    if create_adminadmin():
        print()
        print("[2/2] Creating test admin user...")
        create_test_admin()
    else:
        print("\n[FAIL] Cannot proceed without AdminAdmin user")
    
    print()
    print("="*60)

