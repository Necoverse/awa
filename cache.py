from typing import Any, Dict, Optional, Callable
from functools import wraps
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SimpleCache:
    """Basit in-memory cache implementasyonu"""
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if item["expires_at"] < datetime.now():
            del self._cache[key]
            return None
            
        return item["value"]
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Cache'e veri kaydet"""
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl)
        }
    
    def delete(self, key: str) -> None:
        """Cache'den veri sil"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Tüm cache'i temizle"""
        self._cache.clear()

# Singleton cache instance
cache = SimpleCache()

def cache_decorator(ttl: int = 3600) -> Callable:
    """Cache decorator'ı"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Cache anahtarını oluştur
            key = f"{func.__name__}:{':'.join(str(arg) for arg in args)}:{':'.join(f'{k}:{v}' for k, v in sorted(kwargs.items()))}"
            
            # Cache'den veriyi al
            cached_data = cache.get(key)
            if cached_data is not None:
                logger.debug(f"Cache hit for key: {key}")
                return cached_data
            
            # Fonksiyonu çalıştır ve sonucu cache'le
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.debug(f"Cache miss for key: {key}, duration: {duration:.2f}s")
            cache.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator 