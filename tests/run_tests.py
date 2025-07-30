#!/usr/bin/env python3
"""
Test Runner for Analytics Integration
Runs all tests and provides comprehensive reporting
"""

import subprocess
import sys
import os
from datetime import datetime


def run_command(command, description):
    """Run a command and capture output"""
    print(f"\n🔄 {description}")
    print("=" * 60)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False


def check_prerequisites():
    """Check if prerequisites are met"""
    print("🔍 Checking Prerequisites")
    print("=" * 60)

    # Check if Docker is running
    try:
        result = subprocess.run("docker ps", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not running")
            return False
        print("✅ Docker is running")
    except:
        print("❌ Docker command failed")
        return False

    # Check if services are running
    try:
        result = subprocess.run(
            "docker-compose ps", shell=True, capture_output=True, text=True
        )
        if "analytics" not in result.stdout or "backend" not in result.stdout:
            print("❌ Required services not running")
            print("💡 Please run: docker-compose up -d")
            return False
        print("✅ Required services are running")
    except:
        print("❌ Docker-compose command failed")
        return False

    # Check Python dependencies
    try:
        import requests

        print("✅ Python requests library available")
    except ImportError:
        print("❌ Requests library not found")
        print("💡 Please run: pip install requests")
        return False

    return True


def main():
    """Main test runner"""
    print("🚀 Analytics Integration Test Runner")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Change to tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(tests_dir)

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)

    # Test commands to run
    python_cmd = (
        "python3"
        if subprocess.run("which python3", shell=True, capture_output=True).returncode
        == 0
        else "python"
    )
    tests = [
        {
            "command": f"{python_cmd} validate_integration.py",
            "description": "Quick Validation Test",
        },
        {
            "command": f"{python_cmd} simple_test.py",
            "description": "Basic Integration Test",
        },
        {
            "command": f"{python_cmd} test_analytics_integration.py",
            "description": "Comprehensive Analytics Integration Test",
        },
    ]

    # Run tests
    passed = 0
    failed = 0

    for test in tests:
        success = run_command(test["command"], test["description"])
        if success:
            passed += 1
        else:
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(
        f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%"
        if (passed + failed) > 0
        else "No tests run"
    )
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Analytics integration is working correctly")
        print("✅ Data collection is comprehensive")
        print("✅ User tracking is functional")
        print("✅ Portfolio analytics is active")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("💡 Check the output above for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
