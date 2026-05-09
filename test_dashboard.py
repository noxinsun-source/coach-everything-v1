#!/usr/bin/env python3
"""
Test script for Coach Everything Dashboard
Verifies backend API and frontend connectivity
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

class DashboardTester:
    def __init__(self):
        self.results = []
        self.project_id = None
        self.task_id = None

    def log(self, test_name, status, message=""):
        """Log test result"""
        symbol = "✅" if status == "PASS" else "❌"
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message
        })
        print(f"{symbol} {test_name}: {message}")

    def test_backend_connection(self):
        """Test if backend is running"""
        try:
            response = requests.get(f"{BASE_URL}/api/projects", timeout=TIMEOUT)
            if response.status_code == 200:
                self.log("Backend Connection", "PASS", "API responding")
                return True
            else:
                self.log("Backend Connection", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log("Backend Connection", "FAIL", str(e))
            return False

    def test_frontend_files(self):
        """Test if frontend files are served"""
        files_to_check = [
            ("/", "HTML"),
            ("/index.html", "HTML"),
            ("/css/styles.css", "CSS"),
            ("/js/app.js", "JavaScript"),
            ("/js/api.js", "JavaScript"),
            ("/js/ui.js", "JavaScript"),
        ]

        for path, file_type in files_to_check:
            try:
                response = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
                if response.status_code == 200:
                    self.log(f"Frontend {file_type} ({path})", "PASS", f"{len(response.content)} bytes")
                else:
                    self.log(f"Frontend {file_type} ({path})", "FAIL", f"Status {response.status_code}")
            except Exception as e:
                self.log(f"Frontend {file_type} ({path})", "FAIL", str(e))

    def test_create_project(self):
        """Test project creation"""
        project_data = {
            "name": f"Test Project {int(time.time())}",
            "description": "Auto-generated test project",
            "domain": "learning",
            "vault_path": str(Path.home() / "Documents" / "Obsidian Vault")
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/projects",
                json=project_data,
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.project_id = data.get("id")
                self.log("Create Project", "PASS", f"Project ID: {self.project_id[:8]}...")
                return True
            else:
                self.log("Create Project", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log("Create Project", "FAIL", str(e))
            return False

    def test_get_projects(self):
        """Test fetching projects"""
        try:
            response = requests.get(
                f"{BASE_URL}/api/projects",
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                projects = response.json()
                self.log("Get Projects", "PASS", f"Retrieved {len(projects)} projects")
                return True
            else:
                self.log("Get Projects", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log("Get Projects", "FAIL", str(e))
            return False

    def test_get_dashboard(self):
        """Test fetching dashboard data"""
        if not self.project_id:
            self.log("Get Dashboard", "SKIP", "No project ID available")
            return False

        try:
            response = requests.get(
                f"{BASE_URL}/api/projects/{self.project_id}/dashboard",
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.log("Get Dashboard", "PASS",
                    f"Project: {data['project']['name']}, Tasks: {len(data['tasks'])}")
                return True
            else:
                self.log("Get Dashboard", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log("Get Dashboard", "FAIL", str(e))
            return False

    def test_create_task(self):
        """Test task creation"""
        if not self.project_id:
            self.log("Create Task", "SKIP", "No project ID available")
            return False

        task_data = {
            "title": "Test Task",
            "description": "Auto-generated test task",
            "phase": "Planning",
            "estimated_minutes": 120,
            "verification_criteria": {
                "description": "Task completed",
                "commands": ["echo 'done'"]
            }
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/projects/{self.project_id}/tasks",
                json=task_data,
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.task_id = data.get("id")
                self.log("Create Task", "PASS", f"Task ID: {self.task_id}")
                return True
            else:
                self.log("Create Task", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log("Create Task", "FAIL", str(e))
            return False

    def test_log_time(self):
        """Test time logging"""
        if not self.project_id:
            self.log("Log Time", "SKIP", "No project ID available")
            return False

        time_data = {
            "task_id": self.task_id or "",
            "project_id": self.project_id,
            "duration_minutes": 25,
            "pomodoros": 1,
            "start_time": "2026-05-09T10:00:00",
            "end_time": "2026-05-09T10:25:00",
            "completed": False
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/time-logs",
                json=time_data,
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                self.log("Log Time", "PASS", "Time logged successfully")
                return True
            else:
                self.log("Log Time", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log("Log Time", "FAIL", str(e))
            return False

    def test_settings(self):
        """Test settings endpoints"""
        try:
            # Get settings
            response = requests.get(
                f"{BASE_URL}/api/settings",
                timeout=TIMEOUT
            )
            if response.status_code != 200:
                self.log("Get Settings", "FAIL", f"Status {response.status_code}")
                return False

            settings = response.json()
            self.log("Get Settings", "PASS", f"Theme: {settings.get('theme')}")

            # Update settings
            update_data = {
                "theme": "dark",
                "font_size": 14,
                "language": "zh"
            }
            response = requests.post(
                f"{BASE_URL}/api/settings",
                json=update_data,
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                self.log("Update Settings", "PASS", "Settings updated")
                return True
            else:
                self.log("Update Settings", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log("Settings Endpoints", "FAIL", str(e))
            return False

    def test_database_integrity(self):
        """Test database integrity"""
        db_path = Path.home() / ".coach" / "coach_dashboard.db"
        if db_path.exists():
            size = db_path.stat().st_size
            self.log("Database Integrity", "PASS", f"Database found ({size} bytes)")
            return True
        else:
            self.log("Database Integrity", "WARN", "Database file not found (will be created)")
            return True

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Coach Everything Dashboard Test Suite")
        print("=" * 50)

        # Core tests
        if not self.test_backend_connection():
            print("\n❌ Backend not running. Start it with:")
            print("   python coach/dashboard_backend.py")
            return False

        self.test_database_integrity()
        self.test_frontend_files()

        # API tests
        self.test_get_projects()
        self.test_create_project()

        if self.project_id:
            self.test_get_dashboard()
            self.test_create_task()
            self.test_log_time()

        self.test_settings()

        # Summary
        print("\n" + "=" * 50)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")

        print(f"\n📊 Test Results:")
        print(f"   ✅ Passed:  {passed}")
        print(f"   ❌ Failed:  {failed}")
        print(f"   ⏭️  Skipped: {skipped}")
        print(f"   📈 Total:   {len(self.results)}")

        if failed == 0:
            print("\n🎉 All tests passed! Dashboard is ready to use.")
            print("\nOpen your browser to: http://127.0.0.1:8000")
            return True
        else:
            print(f"\n⚠️  {failed} test(s) failed. Check logs above.")
            return False

if __name__ == "__main__":
    tester = DashboardTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
