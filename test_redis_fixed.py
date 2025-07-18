import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv('REDIS_URL')
redis_password = os.getenv('REDIS_PASSWORD')

print(f"Redis URL: {redis_url}")
print(f"Redis Password: {redis_password}")

try:
    # Test connection with proper SSL settings
    r = redis.from_url(redis_url, decode_responses=True)
    r.ping()
    print("✅ Redis connection successful!")
    
    # Test basic operations
    r.set("test_key", "test_value")
    result = r.get("test_key")
    print(f"✅ Redis operations working: {result}")
    
    # Test with expiration
    r.setex("temp_key", 60, "temp_value")
    temp_result = r.get("temp_key")
    print(f"✅ Redis expiration working: {temp_result}")
    
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    print("❌ Make sure your REDIS_URL starts with 'rediss://' (with SSL)")
