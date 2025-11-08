#!/usr/bin/env python3
"""
Test script for CI-NDA Flask Backend
Run this to verify everything is working correctly
"""

import requests
import json
import time

# Configuration
BASE_URL = 'http://localhost:5000/api'
TEST_USER = {
    'name': 'Test User',
    'email': 'test@example.com',
    'password': 'testpassword123',
    'userType': 'filmmaker',
    'bio': 'Test filmmaker for API testing',
    'location': 'Test City'
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
    
    def test_health_check(self):
        """Test server health"""
        print("🔍 Testing server health...")
        try:
            response = self.session.get(f'{BASE_URL}/health')
            if response.status_code == 200:
                print("✅ Server is healthy")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure the Flask server is running on port 5000")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n📝 Testing user registration...")
        try:
            response = self.session.post(
                f'{BASE_URL}/auth/register',
                json=TEST_USER,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token')
                    print("✅ User registration successful")
                    return True
                else:
                    print(f"❌ Registration failed: {data.get('message')}")
                    return False
            elif response.status_code == 409:
                print("⚠️  User already exists, trying login instead...")
                return self.test_user_login()
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def test_user_login(self):
        """Test user login"""
        print("\n🔐 Testing user login...")
        try:
            login_data = {
                'email': TEST_USER['email'],
                'password': TEST_USER['password']
            }
            
            response = self.session.post(
                f'{BASE_URL}/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token')
                    print("✅ User login successful")
                    return True
                else:
                    print(f"❌ Login failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_authenticated_request(self):
        """Test authenticated request"""
        print("\n👤 Testing authenticated request (get profile)...")
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f'{BASE_URL}/users/profile',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Authenticated request successful")
                    user_data = data.get('user', {})
                    print(f"   User: {user_data.get('name')} ({user_data.get('email')})")
                    return True
                else:
                    print(f"❌ Profile request failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Profile request failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Profile request error: {e}")
            return False
    
    def test_courses_endpoint(self):
        """Test courses endpoint"""
        print("\n📚 Testing courses endpoint...")
        try:
            response = self.session.get(f'{BASE_URL}/courses')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    courses = data.get('courses', [])
                    print(f"✅ Courses endpoint working - found {len(courses)} courses")
                    return True
                else:
                    print(f"❌ Courses request failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Courses request failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Courses request error: {e}")
            return False
    
    def test_opportunities_endpoint(self):
        """Test opportunities endpoint"""
        print("\n💼 Testing opportunities endpoint...")
        try:
            response = self.session.get(f'{BASE_URL}/opportunities')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    opportunities = data.get('opportunities', [])
                    print(f"✅ Opportunities endpoint working - found {len(opportunities)} opportunities")
                    return True
                else:
                    print(f"❌ Opportunities request failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Opportunities request failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Opportunities request error: {e}")
            return False
    
    def test_search_endpoint(self):
        """Test search endpoint"""
        print("\n🔍 Testing search endpoint...")
        try:
            response = self.session.get(f'{BASE_URL}/search?q=film')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    total_results = data.get('totalResults', 0)
                    print(f"✅ Search endpoint working - found {total_results} results")
                    return True
                else:
                    print(f"❌ Search request failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Search request failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Search request error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting CI-NDA API Tests...\n")
        
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_authenticated_request,
            self.test_courses_endpoint,
            self.test_opportunities_endpoint,
            self.test_search_endpoint
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your CI-NDA backend is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the error messages above.")
        
        return passed == total

def main():
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎬 Ready to start using CI-NDA!")
        print("📁 Open any HTML file in your browser to access the frontend")
        print("🌐 Backend API available at: http://localhost:5000/api")
    else:
        print("\n🔧 Please fix the issues above before proceeding")
        print("💡 Make sure:")
        print("   - Flask server is running (python server.py)")
        print("   - Database is set up and accessible")
        print("   - All dependencies are installed")

if __name__ == '__main__':
    main()