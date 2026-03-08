#!/usr/bin/env python3
"""
PalCloudy - Test Runner
Tüm testleri çalıştır ve rapor oluştur
"""

import unittest
import sys
import os
from io import StringIO
import time

# Proje kökünü path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Test modüllerini import et
from tests.test_api.test_get_dedicated_servers import (
    TestGetDedicatedServers,
    TestParseServerResponse,
    TestExampleData
)
from tests.test_core.test_task_manager import (
    TestTaskManager,
    TestGetTaskManager
)
from tests.test_core.test_cache_manager import (
    TestCacheManager,
    TestGetCacheManager,
    TestCacheIntegration
)


class ColoredTextTestResult(unittest.TextTestResult):
    """Renkli test sonuçları"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_start_time = None
    
    def startTest(self, test):
        super().startTest(test)
        self.test_start_time = time.time()
    
    def addSuccess(self, test):
        super().addSuccess(test)
        elapsed = time.time() - self.test_start_time
        print(f"✅ {test._testMethodName} ({elapsed:.3f}s)")
    
    def addError(self, test, err):
        super().addError(test, err)
        print(f"❌ {test._testMethodName} - ERROR")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"❌ {test._testMethodName} - FAILED")


def run_tests():
    """Tüm testleri çalıştır"""
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║            🧪 PalCloudy - Faz 3 Test Suite                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test case'leri ekle
    print("📋 Test Case'leri yükleniyor...\n")
    
    # API Tests
    print("📍 API Tests:")
    suite.addTests(loader.loadTestsFromTestCase(TestGetDedicatedServers))
    suite.addTests(loader.loadTestsFromTestCase(TestParseServerResponse))
    suite.addTests(loader.loadTestsFromTestCase(TestExampleData))
    
    # Core Tests
    print("📍 Core Tests:")
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestGetTaskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestGetCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheIntegration))
    
    print(f"\n🚀 {suite.countTestCases()} test çalıştırılıyor...\n")
    print("-" * 70)
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    
    # Testleri çalıştır
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time
    
    # Sonuç raporu
    print("\n" + "=" * 70)
    print("📊 TEST SONUÇ RAPORU")
    print("=" * 70)
    
    print(f"""
Total Tests:    {result.testsRun}
Passed:         {result.testsRun - len(result.failures) - len(result.errors)} ✅
Failed:         {len(result.failures)} ❌
Errors:         {len(result.errors)} ⚠️
Success Rate:   {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%
Elapsed Time:   {elapsed_time:.2f}s
    """)
    
    # Detaylı hata bilgileri
    if result.failures:
        print("\n❌ FAILED TESTS:")
        print("-" * 70)
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print("\n⚠️  ERROR TESTS:")
        print("-" * 70)
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    # Özet
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ TÜM TESTLER BAŞARILI! 🎉")
    else:
        print("❌ BAZI TESTLER BAŞARISIZ")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
