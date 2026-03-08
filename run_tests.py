#!/usr/bin/env python3
"""
PalCloudy - Test Runner (FIXED VERSION)
Sprint 2: Tüm testleri çalıştır (API + Core + UI)
FIX: UI tests Gtk unavailable olduğunda safely handle et
"""

import os
import sys
import time
import unittest
from io import StringIO

# Proje kökünü path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Test modüllerini import et

# Sprint 1: API Tests
from tests.test_api.test_get_dedicated_servers import (
    TestExampleData,
    TestGetDedicatedServers,
    TestParseServerResponse,
)
from tests.test_core.test_cache_manager import (
    TestCacheIntegration,
    TestCacheManager,
    TestGetCacheManager,
)

# Sprint 1: Core Tests
from tests.test_core.test_task_manager import TestGetTaskManager, TestTaskManager

# Sprint 2: UI Tests - FIXED: try-except ile sarmalayı
UI_TESTS_AVAILABLE = False
try:
    import gi

    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")

    from tests.test_ui.test_ui_components import (
        TestGetToastManager,
        TestHealthIndicator,
        TestServerListView,
        TestStatusBadge,
        TestTaskProgressBar,
        TestToastManager,
    )

    UI_TESTS_AVAILABLE = True
except (ImportError, ValueError) as e:
    print(f"⚠️  UI tests geçileniyor (Gtk unavailable)")
    UI_TESTS_AVAILABLE = False


def run_tests(verbose=True):
    """Tüm testleri çalıştır"""

    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🧪 PalCloudy - Faz 3 Sprint 2 Test Suite (FIXED)           ║
║                                                                ║
║   Sprint 1 (API + Core) + Sprint 2 (UI Components)            ║
║   FIX: Gtk unavailable handling                               ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)

    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test case'leri ekle
    print("📋 Test Case'leri yükleniyor...\n")

    # ============ SPRINT 1: API TESTS ============
    print("📍 SPRINT 1: API Tests")
    suite.addTests(loader.loadTestsFromTestCase(TestGetDedicatedServers))
    suite.addTests(loader.loadTestsFromTestCase(TestParseServerResponse))
    suite.addTests(loader.loadTestsFromTestCase(TestExampleData))
    print("   ✅ 11 API test yüklendi")

    # ============ SPRINT 1: CORE TESTS ============
    print("📍 SPRINT 1: Core Tests")
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestGetTaskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestGetCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheIntegration))
    print("   ✅ 31 Core test yüklendi")

    # ============ SPRINT 2: UI TESTS ============
    if UI_TESTS_AVAILABLE:
        print("📍 SPRINT 2: UI Components Tests")
        suite.addTests(loader.loadTestsFromTestCase(TestServerListView))
        suite.addTests(loader.loadTestsFromTestCase(TestStatusBadge))
        suite.addTests(loader.loadTestsFromTestCase(TestHealthIndicator))
        suite.addTests(loader.loadTestsFromTestCase(TestTaskProgressBar))
        suite.addTests(loader.loadTestsFromTestCase(TestToastManager))
        suite.addTests(loader.loadTestsFromTestCase(TestGetToastManager))
        print("   ✅ 26 UI test yüklendi")
    else:
        print("📍 SPRINT 2: UI Components Tests")
        print("   ⚠️  Gtk unavailable - UI tests skipped")

    total_tests = suite.countTestCases()
    print(f"\n🚀 {total_tests} test çalıştırılıyor...\n")
    print("-" * 70)

    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1, stream=sys.stdout)

    # Testleri çalıştır
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time

    # Sonuç raporu
    print("\n" + "=" * 70)
    print("📊 TEST SONUÇ RAPORU")
    print("=" * 70)

    passed = result.testsRun - len(result.failures) - len(result.errors)
    success_rate = (passed / result.testsRun * 100) if result.testsRun > 0 else 0

    print(f"""
Total Tests:    {result.testsRun}
Passed:         {passed} ✅
Failed:         {len(result.failures)} ❌
Errors:         {len(result.errors)} ⚠️
Success Rate:   {success_rate:.1f}%
Elapsed Time:   {elapsed_time:.2f}s

Breakdown:
  • Sprint 1 API:     11 tests
  • Sprint 1 Core:    31 tests
  • Sprint 2 UI:      {26 if UI_TESTS_AVAILABLE else 0} tests
    """)

    # Detaylı hata bilgileri
    if result.failures:
        print("\n❌ FAILED TESTS:")
        print("-" * 70)
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback[:500])  # İlk 500 char

    if result.errors:
        print("\n⚠️  ERROR TESTS:")
        print("-" * 70)
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback[:500])  # İlk 500 char

    # Özet
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ TÜM TESTLER BAŞARILI! 🎉")
        print(f"   {total_tests} test, {elapsed_time:.2f}s, %100 geçişti")
    else:
        print("❌ BAZI TESTLER BAŞARISIZ")
        print(f"   {passed}/{result.testsRun} test geçti")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PalCloudy Test Runner (FIXED)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet output")
    args = parser.parse_args()

    verbose = not args.quiet
    sys.exit(run_tests(verbose=verbose))
