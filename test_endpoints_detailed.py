"""
Detaylı Endpoint Test Scripti
Tüm endpoint'leri tek tek test eder ve detaylı rapor oluşturur
"""
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import sys

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class EndpointTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.admin_token = None
        self.adminadmin_token = None
        self.results: List[Dict[str, Any]] = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0
        
    def log(self, message: str, status: str = "INFO", file=None):
        """Log mesajı yazdır ve dosyaya kaydet"""
        colors = {
            "PASS": Colors.GREEN,
            "FAIL": Colors.RED,
            "INFO": Colors.BLUE,
            "WARN": Colors.YELLOW,
            "SKIP": Colors.CYAN
        }
        color = colors.get(status, Colors.RESET)
        msg = f"{color}[{status}]{Colors.RESET} {message}"
        print(msg)
        if file:
            file.write(f"[{status}] {message}\n")
    
    def test_endpoint(
        self,
        name: str,
        method: str,
        url: str,
        requires_auth: bool = False,
        requires_admin: bool = False,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        expected_status: List[int] = [200, 201],
        file=None
    ) -> Dict[str, Any]:
        """Tek bir endpoint'i test et"""
        self.total += 1
        result = {
            "name": name,
            "method": method,
            "url": url,
            "status": "UNKNOWN",
            "status_code": None,
            "response_time": None,
            "error": None,
            "response": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Auth kontrolü
            headers = {}
            if requires_auth or requires_admin:
                # AdminAdmin token'ı öncelikli kullan (hem admin hem adminadmin yetkileri için)
                token = self.adminadmin_token if requires_admin and self.adminadmin_token else (self.admin_token if requires_admin else self.token)
                if not token:
                    result["status"] = "SKIPPED"
                    result["error"] = "Authentication token not available"
                    self.skipped += 1
                    self.log(f"{name} - SKIPPED (No auth token)", "SKIP", file)
                    self.results.append(result)
                    return result
                headers["Authorization"] = f"Bearer {token}"
            
            # Request gönder
            start_time = datetime.now()
            
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                if files:
                    response = requests.post(url, headers=headers, json=json_data, files=files, timeout=30)
                else:
                    response = requests.post(url, headers=headers, json=json_data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=json_data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            result["status_code"] = response.status_code
            result["response_time"] = response_time
            
            # Response'u parse et
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text[:500]  # İlk 500 karakter
            
            # Status kontrolü
            if response.status_code in expected_status:
                result["status"] = "PASS"
                self.passed += 1
                self.log(f"{name} - PASS ({response.status_code}) - {response_time:.2f}s", "PASS", file)
            else:
                result["status"] = "FAIL"
                result["error"] = f"Expected {expected_status}, got {response.status_code}"
                self.failed += 1
                error_msg = response.text[:200] if response.text else "No error message"
                self.log(f"{name} - FAIL ({response.status_code}) - {error_msg}", "FAIL", file)
                
        except requests.exceptions.ConnectionError:
            result["status"] = "FAIL"
            result["error"] = "Connection refused - Server not running?"
            self.failed += 1
            self.log(f"{name} - FAIL (Connection Error)", "FAIL", file)
        except requests.exceptions.Timeout:
            result["status"] = "FAIL"
            result["error"] = "Request timeout"
            self.failed += 1
            self.log(f"{name} - FAIL (Timeout)", "FAIL", file)
        except Exception as e:
            result["status"] = "FAIL"
            result["error"] = str(e)
            self.failed += 1
            self.log(f"{name} - FAIL (Error: {str(e)})", "FAIL", file)
        
        self.results.append(result)
        return result
    
    def setup_authentication(self, file=None):
        """Authentication setup - test user oluştur ve login ol"""
        self.log("\n=== AUTHENTICATION SETUP ===", "INFO", file)
        
        # Test user register
        timestamp = int(datetime.now().timestamp())
        register_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPass123!"
        }
        
        result = self.test_endpoint(
            "User Registration",
            "POST",
            f"{API_V1}/auth/register",
            json_data=register_data,
            file=file
        )
        
        if result["status"] == "PASS":
            # Login
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            
            result = self.test_endpoint(
                "User Login",
                "POST",
                f"{API_V1}/auth/login",
                json_data=login_data,
                file=file
            )
            
            if result["status"] == "PASS" and result.get("response"):
                # BaseResponse format: {"success": true, "data": {...}, "message": "..."}
                response_data = result["response"]
                data = response_data.get("data", {})
                
                # Token extraction - try multiple formats
                if isinstance(data, dict):
                    self.token = data.get("access_token")
                elif isinstance(data, str):
                    # If data is string, check if it's JSON
                    try:
                        import json
                        parsed = json.loads(data)
                        if isinstance(parsed, dict):
                            self.token = parsed.get("access_token")
                    except:
                        pass
                
                # Also check direct in response
                if not self.token and isinstance(response_data, dict):
                    self.token = response_data.get("access_token")
                
                if self.token:
                    self.log(f"Token obtained: {self.token[:20]}...", "INFO", file)
                    
                    # Get current user
                    user_result = self.test_endpoint(
                        "Get Current User",
                        "GET",
                        f"{API_V1}/auth/me",
                        requires_auth=True,
                        file=file
                    )
                    
                    if user_result["status"] == "PASS" and user_result.get("response"):
                        user_response = user_result["response"]
                        user_data = user_response.get("data", {}) if isinstance(user_response, dict) else {}
                        if isinstance(user_data, dict):
                            self.user_id = user_data.get("id")
                        self.log(f"User ID: {self.user_id}", "INFO", file)
                else:
                    self.log("Failed to extract token from login response", "WARN", file)
                    self.log(f"Response structure: {str(result.get('response'))[:200]}", "WARN", file)
            else:
                self.log("Login failed, some tests will be skipped", "WARN", file)
        else:
            # Kullanıcı zaten var olabilir, login dene
            self.log("Registration failed, trying login with existing user", "WARN", file)
            login_data = {
                "username": "testuser_123",
                "password": "TestPass123!"
            }
            result = self.test_endpoint(
                "User Login (Existing)",
                "POST",
                f"{API_V1}/auth/login",
                json_data=login_data,
                file=file
            )
            if result["status"] == "PASS" and result.get("response"):
                data = result["response"].get("data", {})
                self.token = data.get("access_token") if isinstance(data, dict) else None
    
    def setup_admin_authentication(self, file=None):
        """Admin authentication setup - AdminAdmin ve Admin login"""
        self.log("\n=== ADMIN AUTHENTICATION SETUP ===", "INFO", file)
        
        # 1. AdminAdmin login (SystemAdmin)
        adminadmin_login = {
            "username": "SystemAdmin",
            "email": "Admin@Admin.com",
            "password": "hashhash"
        }
        
        result = self.test_endpoint(
            "AdminAdmin Login",
            "POST",
            f"{API_V1}/auth/login",
            json_data={"username": adminadmin_login["username"], "password": adminadmin_login["password"]},
            file=file
        )
        
        if result["status"] == "PASS" and result.get("response"):
            response_data = result["response"]
            data = response_data.get("data", {})
            if isinstance(data, dict):
                self.adminadmin_token = data.get("access_token")
            if not self.adminadmin_token and isinstance(response_data, dict):
                self.adminadmin_token = response_data.get("access_token")
            if self.adminadmin_token:
                self.log(f"AdminAdmin token obtained: {self.adminadmin_token[:20]}...", "INFO", file)
        
        # 2. Admin login (test)
        admin_login = {
            "username": "test",
            "email": "test@test.com",
            "password": "test123"
        }
        
        result = self.test_endpoint(
            "Admin Login",
            "POST",
            f"{API_V1}/auth/login",
            json_data={"username": admin_login["username"], "password": admin_login["password"]},
            file=file
        )
        
        if result["status"] == "PASS" and result.get("response"):
            response_data = result["response"]
            data = response_data.get("data", {})
            if isinstance(data, dict):
                self.admin_token = data.get("access_token")
            if not self.admin_token and isinstance(response_data, dict):
                self.admin_token = response_data.get("access_token")
            if self.admin_token:
                self.log(f"Admin token obtained: {self.admin_token[:20]}...", "INFO", file)
        
        # 3. AdminAdmin ile yeni admin oluştur (test)
        if self.adminadmin_token:
            timestamp = int(datetime.now().timestamp())
            new_admin_data = {
                "username": f"admin_{timestamp}",
                "email": f"admin_{timestamp}@example.com",
                "password": "AdminPass123!"
            }
            
            result = self.test_endpoint(
                "Create Admin User (by AdminAdmin)",
                "POST",
                f"{API_V1}/admin/users/create-admin",
                requires_admin=True,  # AdminAdmin token kullanılacak
                json_data=new_admin_data,
                file=file
            )
            
            if result["status"] == "PASS":
                self.log(f"New admin user created: {new_admin_data['username']}", "INFO", file)
    
    def check_database(self, file=None):
        """Veritabanına yazılan verileri kontrol et"""
        self.log("\n=== DATABASE CHECK ===", "INFO", file)
        
        try:
            import sqlite3
            import os
            from app.core.config import settings
            
            # Database path
            db_path = getattr(settings, 'DATABASE_URL', 'sqlite:///./webtoon.db')
            if db_path.startswith('sqlite:///'):
                db_path = db_path.replace('sqlite:///', '')
            
            if not os.path.exists(db_path):
                self.log(f"Database file not found: {db_path}", "WARN", file)
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Users tablosu
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            self.log(f"Users in database: {user_count}", "INFO", file)
            
            # Admin users
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            admin_count = cursor.fetchone()[0]
            self.log(f"Admin users: {admin_count}", "INFO", file)
            
            # Series
            cursor.execute("SELECT COUNT(*) FROM series")
            series_count = cursor.fetchone()[0]
            self.log(f"Series in database: {series_count}", "INFO", file)
            
            # Translation jobs
            cursor.execute("SELECT COUNT(*) FROM translation_jobs")
            job_count = cursor.fetchone()[0]
            self.log(f"Translation jobs: {job_count}", "INFO", file)
            
            # Comments
            cursor.execute("SELECT COUNT(*) FROM comments")
            comment_count = cursor.fetchone()[0]
            self.log(f"Comments: {comment_count}", "INFO", file)
            
            # Reading history
            cursor.execute("SELECT COUNT(*) FROM readings")
            reading_count = cursor.fetchone()[0]
            self.log(f"Reading history entries: {reading_count}", "INFO", file)
            
            conn.close()
            
            if file:
                file.write(f"\nDatabase Summary:\n")
                file.write(f"  Users: {user_count}\n")
                file.write(f"  Admins: {admin_count}\n")
                file.write(f"  Series: {series_count}\n")
                file.write(f"  Jobs: {job_count}\n")
                file.write(f"  Comments: {comment_count}\n")
                file.write(f"  Reading History: {reading_count}\n\n")
                
        except Exception as e:
            self.log(f"Database check error: {str(e)}", "WARN", file)
    
    def run_all_tests(self):
        """Tüm endpoint'leri test et"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"endpoint_test_report_{timestamp}.txt"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("  WEBTOON AI TRANSLATOR - DETAYLI ENDPOINT TEST RAPORU\n")
            f.write("="*80 + "\n")
            f.write(f"Test Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Base URL: {BASE_URL}\n")
            f.write("="*80 + "\n\n")
            
            print("\n" + "="*80)
            print("  WEBTOON AI TRANSLATOR - DETAYLI ENDPOINT TEST SUITE")
            print("="*80 + "\n")
            
            # 1. Health Check & Root
            self.log("\n[1] HEALTH CHECK & ROOT ENDPOINTS", "INFO", f)
            self.test_endpoint("Root Endpoint", "GET", BASE_URL, file=f)
            self.test_endpoint("Health Check", "GET", f"{BASE_URL}/health", file=f)
            self.test_endpoint("OpenAPI JSON", "GET", f"{BASE_URL}/openapi.json", file=f)
            self.test_endpoint("API Docs", "GET", f"{BASE_URL}/docs", expected_status=[200, 307], file=f)
            
            # 2. Authentication
            self.log("\n[2] AUTHENTICATION ENDPOINTS", "INFO", f)
            self.setup_authentication(f)
            
            # 2.5. Admin Authentication
            self.setup_admin_authentication(f)
            
            # 3. Public Endpoints
            self.log("\n[3] PUBLIC ENDPOINTS", "INFO", f)
            self.test_endpoint("List Public Series", "GET", f"{API_V1}/public/series", file=f)
            self.test_endpoint("Search Series", "GET", f"{API_V1}/public/series", params={"search": "test"}, file=f)
            self.test_endpoint("Filter by Genre", "GET", f"{API_V1}/public/series", params={"genre": "action"}, file=f)
            self.test_endpoint("Sort by Popular", "GET", f"{API_V1}/public/series", params={"sort": "popular"}, file=f)
            
            # 4. Discovery Endpoints
            self.log("\n[4] DISCOVERY ENDPOINTS", "INFO", f)
            self.test_endpoint("Trending Series (Day)", "GET", f"{API_V1}/series/trending", params={"period": "day"}, file=f)
            self.test_endpoint("Trending Series (Week)", "GET", f"{API_V1}/series/trending", params={"period": "week"}, file=f)
            self.test_endpoint("Featured Series", "GET", f"{API_V1}/series/featured", file=f)
            self.test_endpoint("Popular Series", "GET", f"{API_V1}/series/popular", file=f)
            self.test_endpoint("Newest Series", "GET", f"{API_V1}/series/newest", file=f)
            self.test_endpoint("List Tags", "GET", f"{API_V1}/tags", file=f)
            self.test_endpoint("Validate Tags", "GET", f"{API_V1}/tags/validate", params={"tag_names": ["action", "comedy"]}, file=f)
            self.test_endpoint("Get Genres", "GET", f"{API_V1}/series/genres", file=f)
            
            # 5. Translation Endpoints (Authenticated)
            self.log("\n[5] TRANSLATION ENDPOINTS", "INFO", f)
            if self.token:
                translation_data = {
                    "chapter_url": "https://example.com/webtoon/test/chapter/1",
                    "target_lang": "tr",
                    "source_lang": "en",
                    "mode": "clean",
                    "translate_type": 2,  # Free translation
                    "series_name": "Test Series"
                }
                result = self.test_endpoint(
                    "Start Translation",
                    "POST",
                    f"{API_V1}/translate/start",
                    requires_auth=True,
                    json_data=translation_data,
                    expected_status=[200, 201, 400, 404, 409],  # Çeşitli durumlar olabilir
                    file=f
                )
                
                task_id = None
                if result.get("response") and isinstance(result["response"], dict):
                    data = result["response"].get("data", {})
                    if isinstance(data, dict):
                        task_id = data.get("task_id")
                
                if task_id:
                    self.test_endpoint(
                        "Get Translation Status",
                        "GET",
                        f"{API_V1}/translate/status/{task_id}",
                        requires_auth=True,
                        file=f
                    )
                    self.test_endpoint(
                        "Get Translation Result",
                        "GET",
                        f"{API_V1}/translate/result/{task_id}",
                        requires_auth=True,
                        expected_status=[200, 404],  # Henüz hazır olmayabilir
                        file=f
                    )
                
                # Batch Translation
                batch_data = {
                    "base_url": "https://example.com/webtoon/test/episode-{}/viewer",
                    "start_chapter": 1,
                    "end_chapter": 3,
                    "target_lang": "tr",
                    "source_lang": "en",
                    "mode": "clean",
                    "translate_type": 2
                }
                self.test_endpoint(
                    "Start Batch Translation",
                    "POST",
                    f"{API_V1}/translate/batch/start",
                    requires_auth=True,
                    json_data=batch_data,
                    expected_status=[200, 201, 400, 404],
                    file=f
                )
            
            # 6. Jobs Endpoints
            self.log("\n[6] JOBS ENDPOINTS", "INFO", f)
            if self.token:
                self.test_endpoint(
                    "Get Job History",
                    "GET",
                    f"{API_V1}/translate/jobs",
                    requires_auth=True,
                    file=f
                )
                # Get job status via translate endpoint
                self.test_endpoint(
                    "Get Job Status (via translate)",
                    "GET",
                    f"{API_V1}/translate/status/invalid-task-id",
                    requires_auth=True,
                    expected_status=[200, 404],
                    file=f
                )
            
            # 7. Series Management
            self.log("\n[7] SERIES MANAGEMENT ENDPOINTS", "INFO", f)
            if self.token:
                # Create Series requires admin
                series_data = {
                    "title": f"Test Series {int(datetime.now().timestamp())}",
                    "description": "Test series description",
                    "source_language": "en",
                    "status": "ongoing"
                }
                result = self.test_endpoint(
                    "Create Series (Admin)",
                    "POST",
                    f"{API_V1}/series",
                    requires_admin=True,
                    json_data=series_data,
                    file=f
                )
                
                series_id = None
                if result.get("response") and isinstance(result["response"], dict):
                    data = result["response"].get("data", {})
                    if isinstance(data, dict):
                        series_id = data.get("id")
                
                if series_id:
                    self.test_endpoint(
                        "Get Series Details",
                        "GET",
                        f"{API_V1}/series/{series_id}",
                        requires_auth=True,
                        file=f
                    )
                    self.test_endpoint(
                        "Update Series",
                        "PUT",
                        f"{API_V1}/series/{series_id}",
                        requires_admin=True,  # Admin veya AdminAdmin gerekli
                        json_data={"description": "Updated description"},
                        file=f
                    )
                else:
                    # Mevcut serileri listele
                    self.test_endpoint(
                        "List Series",
                        "GET",
                        f"{API_V1}/series",
                        requires_auth=True,
                        file=f
                    )
            
            # 8. User Profile
            self.log("\n[8] USER PROFILE ENDPOINTS", "INFO", f)
            if self.token:
                self.test_endpoint(
                    "Get User Profile",
                    "GET",
                    f"{API_V1}/users/profile",
                    requires_auth=True,
                    file=f
                )
                self.test_endpoint(
                    "Update User Profile",
                    "PUT",
                    f"{API_V1}/users/profile",
                    requires_auth=True,
                    json_data={"email": f"updated_{int(datetime.now().timestamp())}@example.com"},
                    file=f
                )
            
            # 9. Reading History
            self.log("\n[9] READING HISTORY ENDPOINTS", "INFO", f)
            if self.token:
                self.test_endpoint(
                    "Get Reading History",
                    "GET",
                    f"{API_V1}/reading/history",
                    requires_auth=True,
                    file=f
                )
            self.test_endpoint(
                "Get Bookmarks",
                "GET",
                f"{API_V1}/bookmarks",
                requires_auth=True,
                file=f
            )
            
            # 10. Comments
            self.log("\n[10] COMMENTS ENDPOINTS", "INFO", f)
            if self.token:
                self.test_endpoint(
                    "List Comments",
                    "GET",
                    f"{API_V1}/comments",
                    requires_auth=True,
                    file=f
                )
            
            # 11. Reactions
            self.log("\n[11] REACTIONS ENDPOINTS", "INFO", f)
            if self.token:
                # Reactions require series_id, chapter_id, or comment_id
                # We'll skip this as it requires existing data
                self.log("Reactions endpoint requires existing series/chapter/comment - SKIPPED", "SKIP", f)
            
            # 12. Site Settings
            self.log("\n[12] SITE SETTINGS ENDPOINTS", "INFO", f)
            self.test_endpoint("Get Site Settings", "GET", f"{API_V1}/settings", file=f)
            
            # 13. Metrics
            self.log("\n[13] METRICS ENDPOINTS", "INFO", f)
            if self.token:
                self.test_endpoint(
                    "Get Metrics Summary",
                    "GET",
                    f"{API_V1}/metrics/summary",
                    requires_auth=True,
                    file=f
                )
            
            # 14. Cache
            self.log("\n[14] CACHE ENDPOINTS", "INFO", f)
            if self.token:
                self.test_endpoint(
                    "Get Cache Status",
                    "GET",
                    f"{API_V1}/cache/status",
                    requires_auth=True,
                    file=f
                )
            
            # 15. Notifications
            self.log("\n[15] NOTIFICATIONS ENDPOINTS", "INFO", f)
            if self.token:
                self.test_endpoint(
                    "Get Notifications",
                    "GET",
                    f"{API_V1}/notifications",
                    requires_auth=True,
                    file=f
                )
            
            # 16. Subscription
            self.log("\n[16] SUBSCRIPTION ENDPOINTS", "INFO", f)
            if self.token:
                self.test_endpoint(
                    "Get Subscription Status",
                    "GET",
                    f"{API_V1}/subscription",
                    requires_auth=True,
                    file=f
                )
            
            # 17. Files
            self.log("\n[17] FILES ENDPOINTS", "INFO", f)
            if self.token:
                # Files endpoint requires query parameters
                self.test_endpoint(
                    "List Chapters (Files)",
                    "GET",
                    f"{API_V1}/files/test_series/chapters",
                    requires_auth=True,
                    params={"source_lang": "en", "target_lang": "tr"},
                    expected_status=[200, 404],  # 404 if series doesn't exist
                    file=f
                )
            
            # 18. Admin Endpoints
            self.log("\n[18] ADMIN ENDPOINTS", "INFO", f)
            if self.admin_token:
                self.test_endpoint(
                    "Get Admin Stats",
                    "GET",
                    f"{API_V1}/admin/stats",
                    requires_admin=True,
                    file=f
                )
                self.test_endpoint(
                    "Clear Cache (Admin)",
                    "DELETE",
                    f"{API_V1}/admin/cache/clear",
                    requires_admin=True,
                    file=f
                )
                self.test_endpoint(
                    "Get Admin Logs",
                    "GET",
                    f"{API_V1}/admin/logs",
                    requires_admin=True,
                    params={"limit": 10},
                    file=f
                )
                self.test_endpoint(
                    "Get Admin Logs Stats",
                    "GET",
                    f"{API_V1}/admin/logs/stats",
                    requires_admin=True,
                    file=f
                )
            else:
                self.log("Admin token not available, admin endpoints skipped", "SKIP", f)
            
            # 19. Site Settings (Admin Update)
            self.log("\n[19] SITE SETTINGS (ADMIN UPDATE)", "INFO", f)
            if self.admin_token:
                self.test_endpoint(
                    "Update Site Settings (Admin)",
                    "PUT",
                    f"{API_V1}/settings",
                    requires_admin=True,
                    json_data={"maintenance_mode": False},
                    file=f
                )
            
            # 20. Database Check
            self.check_database(f)
            
            # Rapor yazdır
            self.print_summary(f)
            f.write("\n" + "="*80 + "\n")
            f.write("  DETAYLI TEST SONUCLARI\n")
            f.write("="*80 + "\n\n")
            
            for result in self.results:
                f.write(f"\n[{result['status']}] {result['name']}\n")
                f.write(f"  Method: {result['method']}\n")
                f.write(f"  URL: {result['url']}\n")
                f.write(f"  Status Code: {result.get('status_code', 'N/A')}\n")
                f.write(f"  Response Time: {result.get('response_time', 'N/A')}s\n")
                if result.get('error'):
                    f.write(f"  Error: {result['error']}\n")
                if result.get('response'):
                    f.write(f"  Response: {json.dumps(result['response'], indent=2, ensure_ascii=False)[:500]}\n")
                f.write("\n")
        
        print(f"\n{Colors.CYAN}Rapor dosyasi: {report_file}{Colors.RESET}\n")
        return report_file
    
    def print_summary(self, file=None):
        """Test özetini yazdır"""
        print("\n" + "="*80)
        print("  TEST OZETI")
        print("="*80)
        
        summary = f"""
Toplam Test:  {self.total}
{Colors.GREEN}Gecen:        {self.passed}{Colors.RESET}
{Colors.RED}Basarisiz:    {self.failed}{Colors.RESET}
{Colors.CYAN}Atlanan:      {self.skipped}{Colors.RESET}
"""
        print(summary)
        if file:
            file.write(summary)
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"Basarı Oranı: {success_rate:.1f}%")
        print("="*80 + "\n")
        
        if file:
            file.write(f"Basarı Oranı: {success_rate:.1f}%\n")
            file.write("="*80 + "\n\n")
        
        if success_rate >= 80:
            print(f"{Colors.GREEN}[OK] SISTEM SAGLIKLI!{Colors.RESET}\n")
            if file:
                file.write("[OK] SISTEM SAGLIKLI!\n")
        elif success_rate >= 50:
            print(f"{Colors.YELLOW}[UYARI] SISTEMDE BAZI SORUNLAR VAR{Colors.RESET}\n")
            if file:
                file.write("[UYARI] SISTEMDE BAZI SORUNLAR VAR\n")
        else:
            print(f"{Colors.RED}[HATA] SISTEM DIKKAT GEREKTIRIYOR{Colors.RESET}\n")
            if file:
                file.write("[HATA] SISTEM DIKKAT GEREKTIRIYOR\n")
        
        # Başarısız testleri listele
        failed_tests = [r for r in self.results if r["status"] == "FAIL"]
        if failed_tests:
            print(f"{Colors.RED}BASARISIZ TESTLER:{Colors.RESET}")
            if file:
                file.write("BASARISIZ TESTLER:\n")
            for test in failed_tests:
                error_msg = test.get("error", "Unknown error")
                print(f"  - {test['name']}: {error_msg}")
                if file:
                    file.write(f"  - {test['name']}: {error_msg}\n")
            print()

if __name__ == "__main__":
    try:
        tester = EndpointTester()
        report_file = tester.run_all_tests()
        print(f"\n{Colors.CYAN}Test tamamlandi! Rapor: {report_file}{Colors.RESET}\n")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test kullanici tarafindan iptal edildi.{Colors.RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Kritik hata: {str(e)}{Colors.RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

