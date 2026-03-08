"""
PalCloudy - Test: Cache Manager
CacheManager sınıfını test et
"""

import unittest
import time
import sys
import os

# Proje kökünü path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.cache_manager import CacheManager, CachePolicy, get_cache_manager


class TestCacheManager(unittest.TestCase):
    """CacheManager sınıfını test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.cache = CacheManager()
    
    def test_set_and_get(self):
        """✅ Cache'e veri ekle ve al"""
        data = {"server": "ns123456", "ip": "1.2.3.4"}
        
        self.cache.set("server_1", data, ttl_seconds=300)
        retrieved = self.cache.get("server_1")
        
        self.assertEqual(retrieved, data)
    
    def test_cache_miss(self):
        """✅ Cache miss (veri yok)"""
        result = self.cache.get("nonexistent_key")
        
        self.assertIsNone(result)
    
    def test_cache_expiration(self):
        """✅ Cache TTL expire"""
        data = {"test": "data"}
        
        # 1 saniye TTL ile ekle
        self.cache.set("expiring_key", data, ttl_seconds=1)
        
        # Hemen al (still valid)
        result = self.cache.get("expiring_key")
        self.assertEqual(result, data)
        
        # 2 saniye bekle
        time.sleep(2)
        
        # Artık expire olmuş
        result = self.cache.get("expiring_key")
        self.assertIsNone(result)
    
    def test_delete(self):
        """✅ Cache'ten veri sil"""
        self.cache.set("key_to_delete", "data", ttl_seconds=300)
        
        # Silmeden önce kontrol
        self.assertIsNotNone(self.cache.get("key_to_delete"))
        
        # Sil
        success = self.cache.delete("key_to_delete")
        self.assertTrue(success)
        
        # Artık yok
        self.assertIsNone(self.cache.get("key_to_delete"))
    
    def test_delete_nonexistent(self):
        """✅ Olmayan key'i silmeye çalış"""
        success = self.cache.delete("nonexistent_key")
        
        self.assertFalse(success)
    
    def test_invalidate_all(self):
        """✅ Tüm cache'i temizle"""
        self.cache.set("key1", "data1", ttl_seconds=300)
        self.cache.set("key2", "data2", ttl_seconds=300)
        self.cache.set("key3", "data3", ttl_seconds=300)
        
        self.assertEqual(len(self.cache._cache), 3)
        
        # Tümünü temizle
        self.cache.invalidate()
        
        self.assertEqual(len(self.cache._cache), 0)
    
    def test_invalidate_with_pattern(self):
        """✅ Pattern ile cache temizle"""
        self.cache.set("server_1", "data1", ttl_seconds=300)
        self.cache.set("server_2", "data2", ttl_seconds=300)
        self.cache.set("user_1", "data3", ttl_seconds=300)
        
        # Sadece "server_" içeren key'leri sil
        self.cache.invalidate(pattern="server_")
        
        self.assertIsNone(self.cache.get("server_1"))
        self.assertIsNone(self.cache.get("server_2"))
        self.assertIsNotNone(self.cache.get("user_1"))  # Bu kalmalı
    
    def test_cleanup_expired(self):
        """✅ Expire olan entries'i temizle"""
        # Farklı TTL'lerle entries ekle
        self.cache.set("fast_expiring", "data", ttl_seconds=1)
        self.cache.set("slow_expiring", "data", ttl_seconds=300)
        
        time.sleep(2)
        
        # Cleanup çalıştır
        self.cache.cleanup_expired()
        
        # Fast expiring gitti, slow expiring var
        self.assertIsNone(self.cache.get("fast_expiring"))
        self.assertIsNotNone(self.cache.get("slow_expiring"))
    
    def test_cache_statistics(self):
        """✅ Cache istatistikleri"""
        # Birkaç operation yap
        self.cache.set("key1", "data1", ttl_seconds=300)
        self.cache.get("key1")  # Hit
        self.cache.get("key1")  # Hit
        self.cache.get("nonexistent")  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['sets'], 1)
        self.assertIn('%', stats['hit_rate'])
    
    def test_cache_policies(self):
        """✅ Cache policy constants"""
        self.assertEqual(CachePolicy.SHORT, 30)
        self.assertEqual(CachePolicy.MEDIUM, 300)
        self.assertEqual(CachePolicy.LONG, 1800)
        self.assertEqual(CachePolicy.VERY_LONG, 3600)
    
    def test_concurrent_access(self):
        """✅ Eşzamanlı erişim (thread-safe)"""
        import threading
        
        def add_data(key, value):
            self.cache.set(key, value, ttl_seconds=300)
        
        # Birden fazla thread'de cache'e ekle
        threads = []
        for i in range(10):
            t = threading.Thread(target=add_data, args=(f"key_{i}", f"data_{i}"))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Tümü eklenmeli
        self.assertEqual(len(self.cache._cache), 10)


class TestGetCacheManager(unittest.TestCase):
    """Singleton get_cache_manager() fonksiyonunu test et"""
    
    def test_singleton_instance(self):
        """✅ Singleton instance döner"""
        cache1 = get_cache_manager()
        cache2 = get_cache_manager()
        
        self.assertIs(cache1, cache2)  # Aynı nesne
    
    def test_data_persists(self):
        """✅ Veri singleton'da kalır"""
        cache = get_cache_manager()
        cache.set("persistent_key", "persistent_data", ttl_seconds=300)
        
        # Başka bir call ile al
        cache2 = get_cache_manager()
        data = cache2.get("persistent_key")
        
        self.assertEqual(data, "persistent_data")


class TestCacheIntegration(unittest.TestCase):
    """Cache Manager entegrasyonu test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.cache = CacheManager()
    
    def test_cache_server_data(self):
        """✅ Sunucu verilerini cache'le"""
        servers = [
            {'name': 'ns123456', 'ip': '1.2.3.4', 'state': 'ok'},
            {'name': 'ns654321', 'ip': '5.6.7.8', 'state': 'ok'},
        ]
        
        # Cache'e ekle (5 dakika)
        self.cache.set("servers_list", servers, ttl_seconds=CachePolicy.MEDIUM)
        
        # Al
        cached_servers = self.cache.get("servers_list")
        self.assertEqual(len(cached_servers), 2)
        self.assertEqual(cached_servers[0]['name'], 'ns123456')
    
    def test_cache_invalidate_on_update(self):
        """✅ Güncelleme sırasında cache invalidation"""
        # Sunucuları cache'le
        servers = [{'name': 'ns123456', 'state': 'ok'}]
        self.cache.set("servers_list", servers, ttl_seconds=300)
        
        # Yeni veri al (mock API çağrısı)
        new_servers = [
            {'name': 'ns123456', 'state': 'ok'},
            {'name': 'ns654321', 'state': 'ok'},
        ]
        
        # Cache'i invalidate et
        self.cache.invalidate(pattern="servers_")
        
        # Yeni veri ekle
        self.cache.set("servers_list", new_servers, ttl_seconds=300)
        
        # Al
        cached = self.cache.get("servers_list")
        self.assertEqual(len(cached), 2)


# Test runner
if __name__ == '__main__':
    unittest.main(verbosity=2)
