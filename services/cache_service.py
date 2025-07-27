import os
import json
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class CacheService:
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_password = os.getenv('REDIS_PASSWORD', '')
        
        try:
            if self.redis_password:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    password=self.redis_password,
                    decode_responses=True
                )
            else:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connected successfully")
            
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            # Fallback to in-memory cache
            self.redis_client = None
            self.memory_cache = {}
            print("⚠️ Using in-memory cache fallback")
    
    def cache_user_context(self, user_id: str, context: Dict[str, Any], ttl: int = 7200) -> bool:
        """Cache user context with TTL."""
        try:
            key = f"user_context:{user_id}"
            value = json.dumps(context, default=str)
            
            if self.redis_client:
                self.redis_client.setex(key, ttl, value)
            else:
                # Memory cache with timestamp
                self.memory_cache[key] = {
                    'value': value,
                    'expires': datetime.now() + timedelta(seconds=ttl)
                }
            
            return True
            
        except Exception as e:
            print(f"❌ Cache context error: {e}")
            return False
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieve cached user context."""
        try:
            key = f"user_context:{user_id}"
            
            if self.redis_client:
                cached_data = self.redis_client.get(key)
            else:
                # Check memory cache
                cached_entry = self.memory_cache.get(key)
                if cached_entry and cached_entry['expires'] > datetime.now():
                    cached_data = cached_entry['value']
                else:
                    cached_data = None
            
            if cached_data:
                return json.loads(cached_data)
            
            # Return default context
            return {
                "conversation_turns": 0,
                "last_topics": [],
                "preferred_language": "en",
                "mood_history": [],
                "locations_mentioned": []
            }
            
        except Exception as e:
            print(f"❌ Get context error: {e}")
            return {}
    
    def update_conversation(self, user_id: str, role: str, content: str) -> bool:
        """Update conversation history."""
        try:
            key = f"conversation:{user_id}"
            
            # Get existing conversation
            if self.redis_client:
                existing = self.redis_client.lrange(key, 0, -1)
            else:
                existing = self.memory_cache.get(key, [])
            
            # Add new message
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.redis_client:
                self.redis_client.lpush(key, json.dumps(message, default=str))
                # Keep only last 20 messages
                self.redis_client.ltrim(key, 0, 19)
                # Set expiry
                self.redis_client.expire(key, 7200)
            else:
                if key not in self.memory_cache:
                    self.memory_cache[key] = []
                self.memory_cache[key].insert(0, json.dumps(message, default=str))
                # Keep only last 20 messages
                self.memory_cache[key] = self.memory_cache[key][:20]
            
            return True
            
        except Exception as e:
            print(f"❌ Update conversation error: {e}")
            return False
    
    def get_conversation(self, user_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        try:
            key = f"conversation:{user_id}"
            
            if self.redis_client:
                messages = self.redis_client.lrange(key, 0, 9)  # Last 10 messages
            else:
                messages = self.memory_cache.get(key, [])[:10]
            
            conversation = []
            for msg in reversed(messages):  # Reverse to get chronological order
                try:
                    conversation.append(json.loads(msg))
                except json.JSONDecodeError:
                    continue
            
            return conversation
            
        except Exception as e:
            print(f"❌ Get conversation error: {e}")
            return []
    
    def cache_location_data(self, location: str, data: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache location-specific data."""
        try:
            key = f"location:{location.lower()}"
            value = json.dumps(data, default=str)
            
            if self.redis_client:
                self.redis_client.setex(key, ttl, value)
            else:
                self.memory_cache[key] = {
                    'value': value,
                    'expires': datetime.now() + timedelta(seconds=ttl)
                }
            
            return True
            
        except Exception as e:
            print(f"❌ Cache location error: {e}")
            return False
    
    def get_location_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Get cached location data."""
        try:
            key = f"location:{location.lower()}"
            
            if self.redis_client:
                cached_data = self.redis_client.get(key)
            else:
                cached_entry = self.memory_cache.get(key)
                if cached_entry and cached_entry['expires'] > datetime.now():
                    cached_data = cached_entry['value']
                else:
                    cached_data = None
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            print(f"❌ Get location data error: {e}")
            return None
    
    def cleanup_expired_data(self):
        """Clean up expired data from memory cache."""
        if not self.redis_client and hasattr(self, 'memory_cache'):
            current_time = datetime.now()
            expired_keys = [
                key for key, value in self.memory_cache.items()
                if isinstance(value, dict) and 
                value.get('expires') and 
                value['expires'] < current_time
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            if expired_keys:
                print(f"🗑️ Cleaned up {len(expired_keys)} expired cache entries")
