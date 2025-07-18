import redis
import json
import hashlib
from datetime import datetime, timedelta
from config import Config

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(Config.REDIS_URL, password=Config.REDIS_PASSWORD)
        self.cache_timeout = Config.CACHE_TIMEOUT
    
    def get_cache_key(self, city, mood, language):
        """Generate cache key for recommendations"""
        key_data = f"{city}_{mood}_{language}"
        return f"recommendations:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get_cached_recommendations(self, city, mood, language):
        """Get cached recommendations"""
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
        """Preload cache with popular city-mood-language combinations"""
        popular_cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Jaipur']
        moods = ['curious', 'adventurous', 'relaxed', 'cultural']
        languages = ['en', 'hi', 'bn']
        
        from models.story_generator import StoryGenerator
        story_generator = StoryGenerator()
        
        for city in popular_cities:
            for mood in moods:
                for language in languages:
                    try:
                        # Check if already cached
                        if self.get_cached_recommendations(city, mood, language):
                            continue
                        
                        # Generate and cache
                        recommendations = story_generator.generate_recommendations(city, mood, language)
                        self.cache_recommendations(city, mood, language, recommendations)
                        
                        print(f"Preloaded: {city}-{mood}-{language}")
                        
                    except Exception as e:
                        print(f"Preload error for {city}-{mood}-{language}: {e}")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {}
