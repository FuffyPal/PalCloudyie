"""
PalCloudy - Core: Cache Manager
API yanıtlarını cache'lemek için TTL ile
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class CacheEntry:
    """Cache'te tutulacak bir entry"""
    
    def __init__(self, key: str, value: Any, ttl_seconds: int):
        self.key = key
        self.value = value
        self.ttl_seconds = ttl_seconds
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
    
    def is_expired(self) -> bool:
        """Veri expire oldu mu kontrol et"""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def update_access(self):
        """Son erişim zamanını güncelle"""
        self.last_accessed = datetime.now()


class CacheManager:
    """
    API yanıtlarını cache'leyerek performansı artır.
    
    Örnek Kullanım:
        >>> cache = CacheManager()
        >>> 
        >>> # Cache'e veri ekle
        >>> cache.set("servers_list", servers_data, ttl_seconds=300)
        >>> 
        >>> # Cache'den veri al
        >>> data = cache.get("servers_list")
        >>> if data:
        ...     print(f"Cache'ten: {data}")
    """
    
    def __init__(self):
        """Cache Manager'ı başlat"""
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0,
        }
        logger.info("✅ CacheManager başlatıldı")
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """
        Cache'e veri ekle.
        
        Args:
            key: Cache anahtarı
            value: Depolanacak veri
            ttl_seconds: Time-To-Live (varsayılan 5 dakika)
        """
        with self._lock:
            entry = CacheEntry(key, value, ttl_seconds)
            self._cache[key] = entry
            self._stats['sets'] += 1
        
        logger.debug(f"💾 Cache set: {key} (TTL: {ttl_seconds}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Cache'den veri al.
        
        Args:
            key: Cache anahtarı
        
        Returns:
            Cached veri veya None (expire ise)
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._stats['misses'] += 1
                logger.debug(f"⏰ Cache expired: {key}")
                return None
            
            entry.update_access()
            self._stats['hits'] += 1
            logger.debug(f"✅ Cache hit: {key}")
            return entry.value
    
    def delete(self, key: str) -> bool:
        """
        Cache'ten veri sil.
        
        Args:
            key: Silinecek cache anahtarı
        
        Returns:
            Başarılı ise True
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"🗑️  Cache deleted: {key}")
                return True
        return False
    
    def invalidate(self, pattern: str = None):
        """
        Cache'i geçersiz kıl.
        
        Args:
            pattern: Pattern varsa sadece matching entries sil
        """
        with self._lock:
            if pattern is None:
                self._cache.clear()
                logger.info("🗑️  Tüm cache temizlendi")
            else:
                keys_to_delete = [k for k in self._cache.keys() if pattern in k]
                for k in keys_to_delete:
                    del self._cache[k]
                logger.info(f"🗑️  {len(keys_to_delete)} cache entry silindi (pattern: {pattern})")
    
    def cleanup_expired(self):
        """Expire olan entries'i sil"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            logger.debug(f"⏰ {len(expired_keys)} expired entry temizlendi")
    
    def get_stats(self) -> Dict[str, Any]:
        """Cache istatistiklerini al"""
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            hit_rate = (
                (self._stats['hits'] / total * 100) if total > 0 else 0
            )
            
            return {
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': f"{hit_rate:.1f}%",
                'sets': self._stats['sets'],
                'evictions': self._stats['evictions'],
                'current_size': len(self._cache),
            }
    
    def print_stats(self):
        """Cache istatistiklerini yazdır"""
        stats = self.get_stats()
        logger.info(f"""
        📊 Cache İstatistikleri:
        ├─ Hits: {stats['hits']}
        ├─ Misses: {stats['misses']}
        ├─ Hit Rate: {stats['hit_rate']}
        ├─ Sets: {stats['sets']}
        ├─ Size: {stats['current_size']}
        └─ Evictions: {stats['evictions']}
        """)


# Singleton instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Global cache manager'ı al (singleton)"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Cache policy constants
class CachePolicy:
    """Cache TTL policies"""
    SHORT = 30  # 30 saniye
    MEDIUM = 300  # 5 dakika
    LONG = 1800  # 30 dakika
    VERY_LONG = 3600  # 1 saat
