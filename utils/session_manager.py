import redis
import json
from datetime import datetime, timedelta
from config import Config

class SessionManager:
    def __init__(self):
        self.redis_client = redis.from_url(Config.REDIS_URL, password=Config.REDIS_PASSWORD)
        self.session_timeout = Config.SESSION_TIMEOUT
    
    def get_session_key(self, user_id):
        """Generate session key"""
        return f"session:{user_id}"
    
    def get_session(self, user_id):
        """Get user session"""
        try:
            session_key = self.get_session_key(user_id)
            session_data = self.redis_client.get(session_key)
            
            if session_data:
                session = json.loads(session_data)
                # Check if session is expired
                last_activity = datetime.fromisoformat(session['last_activity'])
                if datetime.now() - last_activity > timedelta(seconds=self.session_timeout):
                    self.delete_session(user_id)
                    return self.create_session(user_id)
                return session
            else:
                return self.create_session(user_id)
                
        except Exception as e:
            print(f"Session retrieval error: {e}")
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
            session_key = self.get_session_key(user_id)
            session = self.get_session(user_id)
            
            # Update with new data
            session.update(updates)
            session['last_activity'] = datetime.now().isoformat()
            
            # Save to Redis
            self.redis_client.setex(
                session_key,
                self.session_timeout,
                json.dumps(session)
            )
            
            return session
            
        except Exception as e:
            print(f"Session update error: {e}")
            return None
    
    def delete_session(self, user_id):
        """Delete user session"""
        try:
            session_key = self.get_session_key(user_id)
            self.redis_client.delete(session_key)
            return True
        except Exception as e:
            print(f"Session deletion error: {e}")
            return False
    
    def get_active_sessions(self):
        """Get count of active sessions"""
        try:
            pattern = "session:*"
            keys = self.redis_client.keys(pattern)
            return len(keys)
        except Exception as e:
            print(f"Active sessions error: {e}")
            return 0
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            pattern = "session:*"
            keys = self.redis_client.keys(pattern)
            
            expired_count = 0
            for key in keys:
                try:
                    session_data = self.redis_client.get(key)
                    if session_data:
                        session = json.loads(session_data)
                        last_activity = datetime.fromisoformat(session['last_activity'])
                        if datetime.now() - last_activity > timedelta(seconds=self.session_timeout):
                            self.redis_client.delete(key)
                            expired_count += 1
                except:
                    continue
            
            return expired_count
            
        except Exception as e:
            print(f"Session cleanup error: {e}")
            return 0
