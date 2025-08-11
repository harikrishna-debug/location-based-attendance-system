"""
Test Script for Location-Based Attendance System
Comprehensive testing for Flask server and database functionality
"""

import requests
import json
import time
import mysql.connector
from datetime import datetime, timedelta
import sys

# Configuration
SERVER_URL = "http://localhost:5000"
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'attendance_system',
    'user': 'root',
    'password': 'password',  # Update with your password
    'port': 3306
}

class AttendanceSystemTester:
    def __init__(self, server_url, mysql_config):
        self.server_url = server_url
        self.mysql_config = mysql_config
        self.test_results = []
    
    def log_test(self, test_name, success, message):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def test_server_health(self):
        """Test server health endpoint"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Health", True, f"Server is running - {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("Server Health", False, f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Server Health", False, f"Connection error: {e}")
            return False
    
    def test_database_connection(self):
        """Test direct database connection"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                connection.close()
                self.log_test("Database Connection", True, "Successfully connected to MySQL")
                return True
            else:
                self.log_test("Database Connection", False, "Failed to connect")
                return False
        except mysql.connector.Error as e:
            self.log_test("Database Connection", False, f"MySQL error: {e}")
            return False
        except Exception as e:
            self.log_test("Database Connection", False, f"Unexpected error: {e}")
            return False
    
    def test_attendance_recording(self):
        """Test attendance recording endpoint"""
        test_data = {
            "student_mac_address": "AA:BB:CC:DD:EE:99",
            "classroom_id": 999,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/attendance",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Attendance Recording", True, "Successfully recorded test attendance")
                    return True
                else:
                    self.log_test("Attendance Recording", False, f"Server returned success=false: {data.get('message')}")
                    return False
            else:
                self.log_test("Attendance Recording", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Attendance Recording", False, f"Request error: {e}")
            return False
    
    def test_data_validation(self):
        """Test server data validation"""
        # Test missing fields
        invalid_data = {
            "student_mac_address": "AA:BB:CC:DD:EE:88"
            # Missing classroom_id and timestamp
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/attendance",
                json=invalid_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Data Validation", True, "Server correctly rejected invalid data")
                return True
            else:
                self.log_test("Data Validation", False, f"Server should have returned 400, got {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Data Validation", False, f"Request error: {e}")
            return False
    
    def test_recent_records(self):
        """Test recent records endpoint"""
        try:
            response = requests.get(f"{self.server_url}/api/attendance/recent?limit=5", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    records = data.get('data', [])
                    self.log_test("Recent Records", True, f"Retrieved {len(records)} recent records")
                    return True
                else:
                    self.log_test("Recent Records", False, f"Server returned success=false: {data.get('message')}")
                    return False
            else:
                self.log_test("Recent Records", False, f"HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Recent Records", False, f"Request error: {e}")
            return False
    
    def test_database_records(self):
        """Test database records directly"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            cursor = connection.cursor(dictionary=True)
            
            # Check if test record exists
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM attendance 
                WHERE student_mac_address = 'AA:BB:CC:DD:EE:99' 
                AND classroom_id = 999
            """)
            
            result = cursor.fetchone()
            count = result['count']
            
            cursor.close()
            connection.close()
            
            if count > 0:
                self.log_test("Database Records", True, f"Found {count} test record(s) in database")
                return True
            else:
                self.log_test("Database Records", False, "Test record not found in database")
                return False
                
        except mysql.connector.Error as e:
            self.log_test("Database Records", False, f"MySQL error: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            cursor = connection.cursor()
            
            # Delete test records
            cursor.execute("""
                DELETE FROM attendance 
                WHERE student_mac_address IN ('AA:BB:CC:DD:EE:99', 'AA:BB:CC:DD:EE:88')
                AND classroom_id = 999
            """)
            
            deleted_count = cursor.rowcount
            connection.commit()
            cursor.close()
            connection.close()
            
            self.log_test("Cleanup", True, f"Deleted {deleted_count} test record(s)")
            return True
            
        except mysql.connector.Error as e:
            self.log_test("Cleanup", False, f"MySQL error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Starting Location-Based Attendance System Tests")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Server Health Check", self.test_server_health),
            ("Database Connection", self.test_database_connection),
            ("Attendance Recording", self.test_attendance_recording),
            ("Data Validation", self.test_data_validation),
            ("Recent Records", self.test_recent_records),
            ("Database Records", self.test_database_records),
            ("Cleanup Test Data", self.cleanup_test_data)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
            return False

def main():
    """Main test execution"""
    print("Location-Based Attendance System - Test Suite")
    print("=" * 60)
    
    # Check if server is likely running
    try:
        response = requests.get(f"{SERVER_URL}/api/health", timeout=2)
        print(f"✅ Server appears to be running at {SERVER_URL}")
    except:
        print(f"⚠️  Warning: Server may not be running at {SERVER_URL}")
        print("   Make sure to start the Flask server first:")
        print("   python python/attendance_server.py")
        print()
    
    # Initialize tester
    tester = AttendanceSystemTester(SERVER_URL, MYSQL_CONFIG)
    
    # Run tests
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
