import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # LLM API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    # Session and Cache
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '7200'))  # 2 hours
    CACHE_DEFAULT_TTL = int(os.getenv('CACHE_DEFAULT_TTL', '3600'))  # 1 hour
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'groq')  # 'groq' or 'openai'
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '300'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.9'))
    
    # Voice and Audio
    VOICE_RESPONSES_ENABLED = os.getenv('VOICE_RESPONSES_ENABLED', 'True').lower() == 'true'
    DEFAULT_VOICE_LANGUAGE = os.getenv('DEFAULT_VOICE_LANGUAGE', 'en')
    AUDIO_UPLOAD_FOLDER = os.getenv('AUDIO_UPLOAD_FOLDER', './uploads/audio')
    
    # Supported Languages (ISO codes)
    SUPPORTED_LANGUAGES = [
        'en', 'hi', 'bn', 'ta', 'te', 
        'ml', 'kn', 'gu', 'mr', 'pa', 
        'or', 'as', 'ur'
    ]
    
    # Language Names for Display
    LANGUAGE_NAMES = {
        'en': 'English',
        'hi': 'Hindi', 
        'bn': 'Bengali',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'kn': 'Kannada',
        'gu': 'Gujarati',
        'mr': 'Marathi',
        'pa': 'Punjabi',
        'or': 'Odia',
        'as': 'Assamese',
        'ur': 'Urdu'
    }
    
    # Location Categories
    LOCATION_CATEGORIES = {
        'METROS': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune'],
        'STATES': ['Kerala', 'Rajasthan', 'Himachal Pradesh', 'Uttarakhand', 'Goa', 'Tamil Nadu', 'Karnataka'],
        'HILL_STATIONS': ['Shimla', 'Manali', 'Mussoorie', 'Nainital', 'Ooty', 'Kodaikanal', 'Munnar', 'Darjeeling'],
        'BEACHES': ['Goa', 'Kerala', 'Pondicherry', 'Gokarna', 'Kovalam', 'Varkala', 'Digha'],
        'HERITAGE': ['Agra', 'Jaipur', 'Udaipur', 'Varanasi', 'Hampi', 'Khajuraho', 'Ajanta', 'Ellora'],
        'SPIRITUAL': ['Varanasi', 'Rishikesh', 'Haridwar', 'Tirupati', 'Shirdi', 'Bodh Gaya', 'Amritsar']
    }
    
    # Feature Flags
    FEATURES = {
        'VOICE_FIRST_STORYTELLING': True,
        'DYNAMIC_LLM_RESPONSES': True,
        'ENHANCED_MULTILINGUAL': True,
        'SESSION_PERSISTENCE': True,
        'MOOD_AWARE_RECOMMENDATIONS': True,
        'LOCATION_INTELLIGENCE': True,
        'PROXY_BYPASS': True,
        'CULTURAL_CONTEXT_AWARENESS': True
    }
    
    # API Rate Limits
    GROQ_RATE_LIMIT = int(os.getenv('GROQ_RATE_LIMIT', '100'))  # requests per minute
    OPENAI_RATE_LIMIT = int(os.getenv('OPENAI_RATE_LIMIT', '60'))  # requests per minute
    
    # Cloud Storage (for audio files)
    CLOUD_STORAGE_PROVIDER = os.getenv('CLOUD_STORAGE_PROVIDER', 'local')  # 'aws', 'gcp', 'azure', 'local'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    @classmethod
    def validate_config(cls):
        """Validate essential configuration."""
        errors = []
        
        if not cls.GROQ_API_KEY and not cls.OPENAI_API_KEY:
            errors.append("At least one LLM API key (GROQ_API_KEY or OPENAI_API_KEY) is required")
        
        if cls.VOICE_RESPONSES_ENABLED and not cls.TWILIO_ACCOUNT_SID:
            errors.append("Twilio credentials required for voice responses")
        
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))
        
        return True
