"""
Comprehensive API Endpoint Testing Suite
Tests all endpoints with multiple scenarios
"""
import requests
import json
from typing import Dict, Any
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class APITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.passed = 0
        self.failed = 0
        self.total = 0
        
    def log(self, message: str, status: str = "INFO"):
        colors = {
            "PASS": Colors.GREEN,
            "FAIL": Colors.RED,
            "INFO": Colors.BLUE,
            "WARN": Colors.YELLOW
        }
        color = colors.get(status, Colors.RESET)
        print(f"{color}[{status}]{Colors.RESET} {message}")
    
    def test_endpoint(self, name: str, method: str, url: str, **kwargs):
        """Test a single endpoint"""
        self.total += 1
        try:
            if method == "GET":
                response = requests.get(url, **kwargs)
            elif method == "POST":
                response = requests.post(url, **kwargs)
            elif method == "PUT":
                response = requests.put(url, **kwargs)
            elif method == "DELETE":
                response = requests.delete(url, **kwargs)
            
            if response.status_code in [200, 201]:
                self.passed += 1
                self.log(f"{name} - Status: {response.status_code}", "PASS")
                return response.json()
            else:
                self.failed += 1
                self.log(f"{name} - Status: {response.status_code} - {response.text[:100]}", "FAIL")
                return None
        except Exception as e:
            self.failed += 1
            self.log(f"{name} - Error: {str(e)}", "FAIL")
            return None
    
    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "="*60)
        print("  WEBTOON AI TRANSLATOR - API TEST SUITE")
        print("="*60 + "\n")
        
        # 1. Health Check Tests
        self.log("\n[1] HEALTH CHECK TESTS", "INFO")
        self.test_endpoint("Root Endpoint", "GET", BASE_URL)
        self.test_endpoint("Health Check", "GET", f"{BASE_URL}/health")
        
        # 2. Authentication Tests
        self.log("\n[2] AUTHENTICATION TESTS", "INFO")
        
        # Register new user
        register_data = {
            "username": f"testuser_{datetime.now().timestamp()}",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "TestPass123!"
        }
        result = self.test_endpoint(
            "User Registration",
            "POST",
            f"{API_V1}/auth/register",
            json=register_data
        )
        
        if result:
            # Login
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            result = self.test_endpoint(
                "User Login",
                "POST",
                f"{API_V1}/auth/login",
                data=login_data
            )
            
            if result and "access_token" in result:
                self.token = result["access_token"]
                self.log(f"Token obtained: {self.token[:20]}...", "INFO")
                
                # Get current user
                headers = {"Authorization": f"Bearer {self.token}"}
                user_data = self.test_endpoint(
                    "Get Current User",
                    "GET",
                    f"{API_V1}/auth/me",
                    headers=headers
                )
                
                if user_data:
                    self.user_id = user_data.get("data", {}).get("id")
        
        # 3. Public Endpoints Tests
        self.log("\n[3] PUBLIC ENDPOINTS TESTS", "INFO")
        self.test_endpoint("List Public Series", "GET", f"{API_V1}/public/series")
        self.test_endpoint("Search Series", "GET", f"{API_V1}/public/series?search=test")
        self.test_endpoint("Filter by Genre", "GET", f"{API_V1}/public/series?genre=action")
        self.test_endpoint("Sort by Popular", "GET", f"{API_V1}/public/series?sort=popular")
        
        # 4. Discovery Endpoints Tests
        self.log("\n[4] DISCOVERY ENDPOINTS TESTS", "INFO")
        self.test_endpoint("Trending Series (Day)", "GET", f"{API_V1}/series/trending?period=day")
        self.test_endpoint("Trending Series (Week)", "GET", f"{API_V1}/series/trending?period=week")
        self.test_endpoint("Featured Series", "GET", f"{API_V1}/series/featured")
        self.test_endpoint("Popular Series", "GET", f"{API_V1}/series/popular")
        self.test_endpoint("Newest Series", "GET", f"{API_V1}/series/newest")
        self.test_endpoint("List Tags", "GET", f"{API_V1}/tags")
        
        # 5. Translation Tests (Authenticated)
        if self.token:
            self.log("\n[5] TRANSLATION ENDPOINTS TESTS", "INFO")
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Start translation (will fail without valid URL, but tests endpoint)
            translation_data = {
                "url": "https://example.com/webtoon/test",
                "target_language": "tr",
                "source_language": "en"
            }
            self.test_endpoint(
                "Start Translation",
                "POST",
                f"{API_V1}/translate/start",
                json=translation_data,
                headers=headers
            )
        
        # 6. Series Management Tests (Authenticated)
        if self.token:
            self.log("\n[6] SERIES MANAGEMENT TESTS", "INFO")
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create series
            series_data = {
                "title": f"Test Series {datetime.now().timestamp()}",
                "description": "Test series description",
                "source_language": "en",
                "status": "ongoing"
            }
            series_result = self.test_endpoint(
                "Create Series",
                "POST",
                f"{API_V1}/series",
                json=series_data,
                headers=headers
            )
            
            if series_result:
                series_id = series_result.get("data", {}).get("id")
                if series_id:
                    # Get series details
                    self.test_endpoint(
                        "Get Series Details",
                        "GET",
                        f"{API_V1}/series/{series_id}",
                        headers=headers
                    )
                    
                    # Update series
                    update_data = {"description": "Updated description"}
                    self.test_endpoint(
                        "Update Series",
                        "PUT",
                        f"{API_V1}/series/{series_id}",
                        json=update_data,
                        headers=headers
                    )
        
        # 7. User Profile Tests (Authenticated)
        if self.token and self.user_id:
            self.log("\n[7] USER PROFILE TESTS", "INFO")
            headers = {"Authorization": f"Bearer {self.token}"}
            
            self.test_endpoint(
                "Get User Profile",
                "GET",
                f"{API_V1}/users/{self.user_id}",
                headers=headers
            )
            
            # Update profile
            profile_data = {
                "bio": "Test user bio",
                "preferences": {"theme": "dark"}
            }
            self.test_endpoint(
                "Update User Profile",
                "PUT",
                f"{API_V1}/users/{self.user_id}",
                json=profile_data,
                headers=headers
            )
        
        # 8. Reading History Tests (Authenticated)
        if self.token:
            self.log("\n[8] READING HISTORY TESTS", "INFO")
            headers = {"Authorization": f"Bearer {self.token}"}
            
            self.test_endpoint(
                "Get Reading History",
                "GET",
                f"{API_V1}/reading/history",
                headers=headers
            )
            
            self.test_endpoint(
                "Get Bookmarks",
                "GET",
                f"{API_V1}/reading/bookmarks",
                headers=headers
            )
        
        # 9. Site Settings Tests
        self.log("\n[9] SITE SETTINGS TESTS", "INFO")
        self.test_endpoint("Get Site Settings", "GET", f"{API_V1}/settings")
        
        # 10. Metrics Tests (Authenticated)
        if self.token:
            self.log("\n[10] METRICS TESTS", "INFO")
            headers = {"Authorization": f"Bearer {self.token}"}
            
            self.test_endpoint(
                "Get Translation Stats",
                "GET",
                f"{API_V1}/metrics/translation-stats",
                headers=headers
            )
            
            self.test_endpoint(
                "Get User Stats",
                "GET",
                f"{API_V1}/metrics/user-stats",
                headers=headers
            )
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("  TEST SUMMARY")
        print("="*60)
        print(f"Total Tests:  {self.total}")
        print(f"{Colors.GREEN}Passed:       {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed:       {self.failed}{Colors.RESET}")
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print("="*60 + "\n")
        
        if success_rate >= 80:
            print(f"{Colors.GREEN}✓ SYSTEM IS HEALTHY!{Colors.RESET}\n")
        elif success_rate >= 50:
            print(f"{Colors.YELLOW}⚠ SYSTEM HAS SOME ISSUES{Colors.RESET}\n")
        else:
            print(f"{Colors.RED}✗ SYSTEM NEEDS ATTENTION{Colors.RESET}\n")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
