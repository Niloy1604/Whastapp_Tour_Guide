import redis
import json
import hashlib
from datetime import datetime
from config import Config

class CacheService:
    def __init__(self):
        try:
            # Use rediss:// for SSL connection required by Upstash
            self.redis_client = redis.from_url(
                Config.REDIS_URL, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test the connection
            self.redis_client.ping()
            print("✅ Redis connected successfully")
            self.cache_timeout = Config.CACHE_TIMEOUT
        except Exception as e:
            print(f"❌ Redis connection error: {e}")
            print("⚠️ Using in-memory fallback storage")
            self.redis_client = None
            self.cache_timeout = Config.CACHE_TIMEOUT
    
    # ... rest of your methods remain the same

    
    def get_cache_key(self, city, mood, language):
        """Generate cache key for recommendations"""
        key_data = f"{city}_{mood}_{language}"
        return f"recommendations:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get_cached_recommendations(self, city, mood, language):
        """Get cached recommendations"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self.get_cache_key(city, mood, language)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None
    
    def cache_recommendations(self, city, mood, language, recommendations):
        """Cache recommendations"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self.get_cache_key(city, mood, language)
            cache_data = {
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat(),
                'city': city,
                'mood': mood,
                'language': language
            }
            
            self.redis_client.setex(
                cache_key,
                self.cache_timeout,
                json.dumps(cache_data)
            )
            
            return True
            
        except Exception as e:
            print(f"Cache storage error: {e}")
            return False
    
    def preload_popular_combinations(self):
        """Preload cache with popular combinations"""
        if not self.redis_client:
            return
        print("Cache preloading skipped (Redis not available)")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        if not self.redis_client:
            return {'status': 'Redis not connected'}
            
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            return {'error': str(e)}
