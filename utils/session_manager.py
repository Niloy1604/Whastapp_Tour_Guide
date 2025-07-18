import redis
import json
from datetime import datetime, timedelta
from config import Config

class SessionManager:
    def __init__(self):
        try:
            self.redis_client = redis.from_url(Config.REDIS_URL)
            self.session_timeout = Config.SESSION_TIMEOUT
        except Exception as e:
            print(f"Redis connection error: {e}")
            self.redis_client = None
            self.memory_sessions = {}
    
    def get_session_key(self, user_id):
        """Generate session key"""
        return f"session:{user_id}"
    
    def get_session(self, user_id):
        """Get user session"""
        if self.redis_client:
            return self._get_redis_session(user_id)
        else:
            return self._get_memory_session(user_id)
    
    def _get_redis_session(self, user_id):
        """Get session from Redis"""
        try:
            session_key = self.get_session_key(user_id)
            session_data = self.redis_client.get(session_key)
            
            if session_data:
                session = json.loads(session_data)
                return session
            else:
                return self.create_session(user_id)
                
        except Exception as e:
            print(f"Session retrieval error: {e}")
            return self.create_session(user_id)
    
    def _get_memory_session(self, user_id):
        """Get session from memory (fallback)"""
        if user_id in self.memory_sessions:
            return self.memory_sessions[user_id]
        else:
            return self.create_session(user_id)
    
    def create_session(self, user_id):
        """Create new session"""
        session = {
            'user_id': user_id,
            'language': 'en',
            'current_city': None,
            'mood': 'curious',
            'conversation_stage': 'initial',
            'last_recommendations': [],
            'message_count': 0,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        self.update_session(user_id, session)
        return session
    
    def update_session(self, user_id, updates):
        """Update session with new data"""
        try:
            session = self.get_session(user_id)
            session.update(updates)
            session['last_activity'] = datetime.now().isoformat()
            
            if self.redis_client:
                session_key = self.get_session_key(user_id)
                self.redis_client.setex(
                    session_key,
                    self.session_timeout,
                    json.dumps(session)
                )
            else:
                self.memory_sessions[user_id] = session
            
            return session
            
        except Exception as e:
            print(f"Session update error: {e}")
            return None
    
    def delete_session(self, user_id):
        """Delete user session"""
        try:
            if self.redis_client:
                session_key = self.get_session_key(user_id)
                self.redis_client.delete(session_key)
            else:
                if user_id in self.memory_sessions:
                    del self.memory_sessions[user_id]
            return True
        except Exception as e:
            print(f"Session deletion error: {e}")
            return False
    
    def get_active_sessions(self):
        """Get count of active sessions"""
        try:
            if self.redis_client:
                pattern = "session:*"
                keys = self.redis_client.keys(pattern)
                return len(keys)
            else:
                return len(self.memory_sessions)
        except Exception as e:
            print(f"Active sessions error: {e}")
            return 0
