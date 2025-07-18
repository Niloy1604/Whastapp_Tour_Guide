"""
Utilities package for WhatsApp AI City Guide
Contains helper functions, session management, and common utilities
"""

from .session_manager import SessionManager
from .helpers import MessageHelper, ValidationHelper

__all__ = [
    'SessionManager',
    'MessageHelper',
    'ValidationHelper'
]

__version__ = '1.0.0'
__author__ = 'CityChai Team'
__description__ = 'Utility functions and session management for WhatsApp bot'

# Initialize utility instances
session_manager = SessionManager()
message_helper = MessageHelper()
validation_helper = ValidationHelper()

# Common utility functions
def format_phone_number(phone_number):
    """Format phone number for consistency"""
    return validation_helper.format_phone_number(phone_number)

def extract_city_from_text(text):
    """Extract city name from text"""
    return message_helper.extract_city_from_text(text)

def extract_selection_number(text):
    """Extract menu selection number from text"""
    return message_helper.extract_selection_number(text)

def is_valid_language(language):
    """Check if language is supported"""
    return validation_helper.validate_language(language)

def clean_text(text):
    """Clean and normalize text"""
    return message_helper.clean_text(text)

def get_error_message(language, error_type='general'):
    """Get localized error message"""
    return message_helper.get_error_message(language, error_type)

# Session management shortcuts
def get_user_session(user_id):
    """Get user session"""
    return session_manager.get_session(user_id)

def update_user_session(user_id, updates):
    """Update user session"""
    return session_manager.update_session(user_id, updates)

def create_user_session(user_id):
    """Create new user session"""
    return session_manager.create_session(user_id)

def delete_user_session(user_id):
    """Delete user session"""
    return session_manager.delete_session(user_id)

# Configuration helpers
def get_supported_languages():
    """Get list of supported languages"""
    from config import Config
    return getattr(Config, 'SUPPORTED_LANGUAGES', ['en', 'hi', 'bn'])

def get_supported_cities():
    """Get list of supported cities"""
    import json
    import os
    
    try:
        cities_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'cities.json')
        with open(cities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [city['name'] for city in data.get('cities', [])]
    except Exception as e:
        print(f"Error loading cities: {e}")
        return ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata']

def get_supported_moods():
    """Get list of supported moods"""
    return ['curious', 'adventurous', 'relaxed', 'cultural', 'foodie']

# Logging helpers
def setup_logging():
    """Setup logging configuration"""
    import logging
    from config import Config
    
    logging.basicConfig(
        level=getattr(Config, 'LOG_LEVEL', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

def get_logger(name):
    """Get logger instance"""
    import logging
    return logging.getLogger(name)

# Performance monitoring
def measure_time(func):
    """Decorator to measure function execution time"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

# Data validation
def validate_message_data(data):
    """Validate incoming message data"""
    required_fields = ['From', 'Body']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate phone number format
    if not validation_helper.validate_phone_number(data['From']):
        return False, "Invalid phone number format"
    
    return True, "Valid"

# Response formatting
def format_response(recommendations, language='en'):
    """Format recommendations response"""
    return message_helper.format_recommendations_response(recommendations, language)

def format_welcome_message(language='en'):
    """Format welcome message"""
    welcome_messages = {
        'en': """🙏 Welcome to CityChai! 🇮🇳

I'm your AI travel companion for exploring India!

🗣️ What I can do:
• Send me text or voice messages
• Tell me which city you're in
• Share your mood (curious, adventurous, relaxed, etc.)
• Get personalized recommendations with stories

📱 How to use:
Just say: "I'm in Delhi and feeling adventurous!"

🌐 Languages: English, Hindi, Bengali

Let's explore incredible India together! ✨""",
        
        'hi': """🙏 CityChai में आपका स्वागत है! 🇮🇳

मैं भारत के लिए आपका AI यात्रा साथी हूँ!

🗣️ मैं क्या कर सकता हूँ:
• मुझे टेक्स्ट या वॉइस मैसेज भेजें
• बताएं कि आप कौन से शहर में हैं
• अपना मूड शेयर करें (जिज्ञासु, साहसी, शांत, आदि)
• कहानियों के साथ व्यक्तिगत सुझाव पाएं

📱 उपयोग कैसे करें:
बस कहें: "मैं दिल्ली में हूँ और साहसी महसूस कर रहा हूँ!"

🌐 भाषाएं: English, Hindi, Bengali

चलिए मिलकर अविश्वसनीय भारत का अन्वेषण करते हैं! ✨""",
        
        'bn': """🙏 CityChai-এ আপনাকে স্বাগতম! 🇮🇳

আমি ভারত অন্বেষণের জন্য আপনার AI ভ্রমণ সাথী!

🗣️ আমি কী করতে পারি:
• আমাকে টেক্সট বা ভয়েস মেসেজ পাঠান
• বলুন আপনি কোন শহরে আছেন
• আপনার মুড শেয়ার করুন (কৌতূহলী, দুঃসাহসিক, শান্ত, ইত্যাদি)
• গল্প সহ ব্যক্তিগত সুপারিশ পান

📱 কিভাবে ব্যবহার করবেন:
শুধু বলুন: "আমি দিল্লিতে আছি এবং দুঃসাহসিক অনুভব করছি!"

🌐 ভাষা: English, Hindi, Bengali

চলুন একসাথে অবিশ্বাস্য ভারত অন্বেষণ করি! ✨"""
    }
    
    return welcome_messages.get(language, welcome_messages['en'])

# Statistics helpers
def get_usage_stats():
    """Get usage statistics"""
    try:
        active_sessions = session_manager.get_active_sessions()
        return {
            'active_sessions': active_sessions,
            'total_users': len(session_manager.get_all_sessions()) if hasattr(session_manager, 'get_all_sessions') else 0,
            'uptime': 'Available'
        }
    except Exception as e:
        print(f"Error getting usage stats: {e}")
        return {
            'active_sessions': 0,
            'total_users': 0,
            'uptime': 'Unknown'
        }

# Error handling
def handle_error(error, context="Unknown"):
    """Handle and log errors"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error in {context}: {str(error)}")
    
    # Return user-friendly error message
    return {
        'error': True,
        'message': 'Something went wrong. Please try again.',
        'context': context
    }

# Initialization function
def initialize_utils():
    """Initialize utilities"""
    try:
        setup_logging()
        
        # Initialize session manager
        if hasattr(session_manager, 'initialize'):
            session_manager.initialize()
        
        print("Utils initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing utils: {e}")
        return False

# Cleanup function
def cleanup_utils():
    """Cleanup utilities"""
    try:
        if hasattr(session_manager, 'cleanup'):
            session_manager.cleanup()
        
        print("Utils cleaned up successfully")
        return True
    except Exception as e:
        print(f"Error cleaning up utils: {e}")
        return False
