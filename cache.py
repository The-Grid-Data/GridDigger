"""
Caching layer for GridDigger Telegram Bot
Supports both in-memory and Redis caching
"""
import json
import logging
import time
from typing import Optional, Any, Dict
from functools import wraps
import hashlib

from config import Config

logger = logging.getLogger(__name__)

# Try to import Redis, fall back to in-memory cache if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")


class InMemoryCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry['expires_at']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = Config.CACHE_TTL
        
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        self._cache.clear()
        return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        return self.get(key) is not None


class RedisCache:
    """Redis-based cache implementation"""
    
    def __init__(self, redis_url: str):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in Redis cache with TTL"""
        try:
            if ttl is None:
                ttl = Config.CACHE_TTL
            
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries (use with caution)"""
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False


class CacheManager:
    """Cache manager that handles both Redis and in-memory caching"""
    
    def __init__(self):
        self.cache = None
        self.enabled = Config.ENABLE_CACHING
        
        if not self.enabled:
            logger.info("Caching is disabled")
            return
        
        # Try to initialize Redis cache first
        if REDIS_AVAILABLE and Config.REDIS_URL:
            try:
                self.cache = RedisCache(Config.REDIS_URL)
                logger.info("Using Redis cache")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.cache = InMemoryCache()
                logger.info("Falling back to in-memory cache")
        else:
            self.cache = InMemoryCache()
            logger.info("Using in-memory cache")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        # Create a string representation of all arguments
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        # Hash the key to ensure consistent length and avoid special characters
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.cache:
            return None
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        if not self.enabled or not self.cache:
            return False
        return self.cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.cache:
            return False
        return self.cache.delete(key)
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        if not self.enabled or not self.cache:
            return False
        return self.cache.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.cache:
            return False
        return self.cache.exists(key)


# Global cache manager instance
cache_manager = CacheManager()


def cached(prefix: str = "default", ttl: int = None):
    """
    Decorator for caching function results
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (uses Config.CACHE_TTL if None)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_manager.enabled:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            
            # Only cache successful results (avoid caching errors)
            if result is not None:
                cache_manager.set(cache_key, result, ttl)
            
            return result
        
        # Add cache management methods to the wrapped function
        wrapper.cache_clear = lambda: cache_manager.clear()
        wrapper.cache_delete = lambda *args, **kwargs: cache_manager.delete(
            cache_manager._generate_key(prefix, *args, **kwargs)
        )
        
        return wrapper
    return decorator


def cache_profile_search(search_term: str, limit: int = 20):
    """Cache key generator for profile searches"""
    return f"search:{hashlib.md5(f'{search_term}:{limit}'.encode()).hexdigest()}"


def cache_profile_detail(profile_id: str):
    """Cache key generator for profile details"""
    return f"profile:{profile_id}"


def cache_filter_options(filter_type: str):
    """Cache key generator for filter options"""
    return f"filters:{filter_type}"


# Cache warming functions
def warm_cache():
    """Warm up the cache with frequently accessed data"""
    if not cache_manager.enabled:
        return
    
    logger.info("Starting cache warm-up...")
    
    # This could be expanded to pre-load popular searches, filter options, etc.
    # For now, we'll just log that warming is available
    
    logger.info("Cache warm-up completed")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    if not cache_manager.enabled:
        return {"enabled": False}
    
    stats = {
        "enabled": True,
        "type": "Redis" if isinstance(cache_manager.cache, RedisCache) else "InMemory"
    }
    
    # Add Redis-specific stats if available
    if isinstance(cache_manager.cache, RedisCache):
        try:
            info = cache_manager.cache.redis_client.info()
            stats.update({
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed")
            })
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
    
    return stats