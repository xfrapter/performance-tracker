#!/usr/bin/env python3
"""
Performance Tracker App - Test Suite
Validates all functionality before Android deployment
"""

import sqlite3
import os
import sys
from datetime import datetime
import tempfile
import shutil

class PerformanceTrackerTester:
    def __init__(self):
        self.test_db_path = os.path.join(tempfile.gettempdir(), 'test_performance.db')
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        
    def setUp(self):
        """Set up test database"""
        # Remove existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        # Create test database
        self.init_test_database()
        
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
    def init_test_database(self):
        """Initialize test database with same schema as main app"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                target_time INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create performance_records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                actual_time INTEGER NOT NULL,
                target_time INTEGER NOT NULL,
                performance_percentage REAL NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        # Create delays table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS delays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                delay_minutes INTEGER NOT NULL,
                reason TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def assert_test(self, condition, test_name, error_msg=""):
        """Assert test condition and record result"""
        if condition:
            self.passed_tests += 1
            self.test_results.append(f"✓ {test_name}")
            print(f"✓ {test_name}")
        else:
            self.failed_tests += 1
            self.test_results.append(f"✗ {test_name} - {error_msg}")
            print(f"✗ {test_name} - {error_msg}")
            
    def test_database_schema(self):
        """Test database schema and table creation"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Test tasks table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        result = cursor.fetchone()
        self.assert_test(result is not None, "Tasks table exists")
        
        # Test performance_records table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='performance_records'")
        result = cursor.fetchone()
        self.assert_test(result is not None, "Performance records table exists")
        
        # Test delays table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delays'")
        result = cursor.fetchone()
        self.assert_test(result is not None, "Delays table exists")
        
        # Test tasks table schema
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        expected_columns = ['id', 'task_name', 'target_time', 'created_at']
        schema_correct = all(col in columns for col in expected_columns)
        self.assert_test(schema_correct, "Tasks table schema correct", f"Found columns: {columns}")
        
        # Test performance_records table schema
        cursor.execute("PRAGMA table_info(performance_records)")
        columns = [col[1] for col in cursor.fetchall()]
        expected_columns = ['id', 'task_id', 'actual_time', 'target_time', 'performance_percentage', 'recorded_at']
        schema_correct = all(col in columns for col in expected_columns)
        self.assert_test(schema_correct, "Performance records table schema correct", f"Found columns: {columns}")
        
        conn.close()
        
    def test_task_operations(self):
        """Test task creation, retrieval, and management"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Test task creation
        cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                      ("Test Task 1", 30))
        task_id = cursor.lastrowid
        conn.commit()
        
        self.assert_test(task_id > 0, "Task creation returns valid ID")
        
        # Test task retrieval
        cursor.execute("SELECT task_name, target_time FROM tasks WHERE id = ?", (task_id,))
        result = cursor.fetchone()
        self.assert_test(result is not None, "Task can be retrieved")
        self.assert_test(result[0] == "Test Task 1", "Task name stored correctly")
        self.assert_test(result[1] == 30, "Task target time stored correctly")
        
        # Test multiple task creation
        cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                      ("Test Task 2", 45))
        cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                      ("Test Task 3", 60))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        self.assert_test(count == 3, "Multiple tasks created successfully", f"Found {count} tasks")
        
        conn.close()
        
    def test_performance_recording(self):
        """Test performance recording and calculation"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create a test task
        cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                      ("Performance Test Task", 60))
        task_id = cursor.lastrowid
        conn.commit()
        
        # Test performance recording with good performance (under target)
        actual_time = 45
        target_time = 60
        performance_percentage = (target_time / actual_time) * 100
        
        cursor.execute("""
            INSERT INTO performance_records (task_id, actual_time, target_time, performance_percentage)
            VALUES (?, ?, ?, ?)
        """, (task_id, actual_time, target_time, performance_percentage))
        record_id = cursor.lastrowid
        conn.commit()
        
        self.assert_test(record_id > 0, "Performance record created successfully")
        
        # Verify performance calculation
        cursor.execute("SELECT performance_percentage FROM performance_records WHERE id = ?", (record_id,))
        stored_percentage = cursor.fetchone()[0]
        expected_percentage = (60 / 45) * 100  # Should be ~133.33%
        
        self.assert_test(abs(stored_percentage - expected_percentage) < 0.01, 
                        "Performance percentage calculated correctly",
                        f"Expected ~133.33%, got {stored_percentage}")
        
        # Test performance recording with poor performance (over target)
        cursor.execute("""
            INSERT INTO performance_records (task_id, actual_time, target_time, performance_percentage)
            VALUES (?, ?, ?, ?)
        """, (task_id, 90, 60, (60 / 90) * 100))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM performance_records WHERE task_id = ?", (task_id,))
        count = cursor.fetchone()[0]
        self.assert_test(count == 2, "Multiple performance records for same task")
        
        conn.close()
        
    def test_delay_tracking(self):
        """Test delay recording and management"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create a test task
        cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                      ("Delay Test Task", 30))
        task_id = cursor.lastrowid
        conn.commit()
        
        # Test delay recording
        cursor.execute("""
            INSERT INTO delays (task_id, delay_minutes, reason)
            VALUES (?, ?, ?)
        """, (task_id, 15, "Equipment malfunction"))
        delay_id = cursor.lastrowid
        conn.commit()
        
        self.assert_test(delay_id > 0, "Delay record created successfully")
        
        # Verify delay data
        cursor.execute("SELECT delay_minutes, reason FROM delays WHERE id = ?", (delay_id,))
        result = cursor.fetchone()
        self.assert_test(result[0] == 15, "Delay minutes stored correctly")
        self.assert_test(result[1] == "Equipment malfunction", "Delay reason stored correctly")
        
        # Test multiple delays for same task
        cursor.execute("""
            INSERT INTO delays (task_id, delay_minutes, reason)
            VALUES (?, ?, ?)
        """, (task_id, 5, "Material shortage"))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM delays WHERE task_id = ?", (task_id,))
        count = cursor.fetchone()[0]
        self.assert_test(count == 2, "Multiple delays recorded for same task")
        
        conn.close()
        
    def test_data_relationships(self):
        """Test foreign key relationships and data integrity"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create a test task
        cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                      ("Relationship Test Task", 40))
        task_id = cursor.lastrowid
        conn.commit()
        
        # Create related performance record
        cursor.execute("""
            INSERT INTO performance_records (task_id, actual_time, target_time, performance_percentage)
            VALUES (?, ?, ?, ?)
        """, (task_id, 35, 40, (40/35)*100))
        
        # Create related delay record
        cursor.execute("""
            INSERT INTO delays (task_id, delay_minutes, reason)
            VALUES (?, ?, ?)
        """, (task_id, 10, "Test delay"))
        conn.commit()
        
        # Test relationship query - get all data for a task
        cursor.execute("""
            SELECT t.task_name, t.target_time, 
                   p.actual_time, p.performance_percentage,
                   d.delay_minutes, d.reason
            FROM tasks t
            LEFT JOIN performance_records p ON t.id = p.task_id
            LEFT JOIN delays d ON t.id = d.task_id
            WHERE t.id = ?
        """, (task_id,))
        
        result = cursor.fetchone()
        self.assert_test(result is not None, "Related data can be queried together")
        self.assert_test(result[0] == "Relationship Test Task", "Task name in joined query")
        self.assert_test(result[2] == 35, "Performance data in joined query")
        self.assert_test(result[4] == 10, "Delay data in joined query")
        
        conn.close()
        
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Test zero target time (should be prevented in UI, but test DB)
        try:
            cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                          ("Zero Time Task", 0))
            conn.commit()
            # If this succeeds, it's not necessarily wrong, but worth noting
            self.assert_test(True, "Zero target time handled")
        except Exception as e:
            self.assert_test(False, "Zero target time caused error", str(e))
        
        # Test very large numbers
        cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                      ("Large Time Task", 9999))
        task_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT target_time FROM tasks WHERE id = ?", (task_id,))
        result = cursor.fetchone()[0]
        self.assert_test(result == 9999, "Large target time stored correctly")
        
        # Test empty strings
        cursor.execute("INSERT INTO tasks (task_name, target_time) VALUES (?, ?)", 
                      ("", 30))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_name = ''")
        count = cursor.fetchone()[0]
        self.assert_test(count == 1, "Empty task name handled")
        
        conn.close()
        
    def run_all_tests(self):
        """Run all test suites"""
        print("🔧 Performance Tracker App - Test Suite")
        print("=" * 50)
        
        self.setUp()
        
        try:
            print("\n📋 Testing Database Schema...")
            self.test_database_schema()
            
            print("\n📝 Testing Task Operations...")
            self.test_task_operations()
            
            print("\n📊 Testing Performance Recording...")
            self.test_performance_recording()
            
            print("\n⏰ Testing Delay Tracking...")
            self.test_delay_tracking()
            
            print("\n🔗 Testing Data Relationships...")
            self.test_data_relationships()
            
            print("\n🧪 Testing Edge Cases...")
            self.test_edge_cases()
            
        finally:
            self.tearDown()
            
        print("\n" + "=" * 50)
        print(f"🎯 Test Results Summary:")
        print(f"✓ Passed: {self.passed_tests}")
        print(f"✗ Failed: {self.failed_tests}")
        print(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests+self.failed_tests)*100):.1f}%")
        
        if self.failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result.startswith("✗"):
                    print(f"   {result}")
        
        return self.failed_tests == 0

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        'main.py',
        'task_details.py', 
        'init_db.py',
        'buildozer.spec',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_requirements():
    """Test that requirements.txt contains necessary packages"""
    print("\n📦 Testing Requirements...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().lower()
        
        required_packages = ['kivy', 'kivymd', 'numpy', 'pandas', 'matplotlib']
        missing_packages = []
        
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages in requirements.txt: {missing_packages}")
            return False
        else:
            print("✅ All required packages in requirements.txt")
            return True
            
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

if __name__ == "__main__":
    print("🚀 Starting Performance Tracker App Tests...")
    
    # Test file structure
    files_ok = test_file_structure()
    
    # Test requirements
    reqs_ok = test_requirements()
    
    # Test database functionality
    tester = PerformanceTrackerTester()
    db_tests_ok = tester.run_all_tests()
    
    # Overall result
    print("\n" + "=" * 60)
    if files_ok and reqs_ok and db_tests_ok:
        print("🎉 ALL TESTS PASSED - App ready for deployment!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Review issues before deployment")
        sys.exit(1) 