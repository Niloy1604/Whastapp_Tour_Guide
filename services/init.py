"""
Services package for WhatsApp AI City Guide
Contains external service integrations and core business logic
"""

from .whatsapp_service import WhatsAppService
from .speech_service import SpeechService
from .cache_service import CacheService

__all__ = [
    'WhatsAppService',
    'SpeechService',
    'CacheService'
]

__version__ = '1.0.0'
__author__ = 'CityChai Team'
__description__ = 'External service integrations for WhatsApp bot'

# Initialize service instances
whatsapp_service = WhatsAppService()
speech_service = SpeechService()
cache_service = CacheService()

# Service health check functions
def check_services_health():
    """Check health of all services"""
    return {
        'whatsapp': whatsapp_service.is_healthy() if hasattr(whatsapp_service, 'is_healthy') else True,
        'speech': speech_service.is_healthy() if hasattr(speech_service, 'is_healthy') else True,
        'cache': cache_service.is_healthy() if hasattr(cache_service, 'is_healthy') else True
    }

def initialize_services():
    """Initialize all services"""
    try:
        # Initialize cache service
        if hasattr(cache_service, 'initialize'):
            cache_service.initialize()
        
        # Load speech models if needed
        if hasattr(speech_service, 'load_models'):
            speech_service.load_models()
        
        return True
    except Exception as e:
        print(f"Error initializing services: {e}")
        return False

# Cleanup function
def cleanup_services():
    """Cleanup all services"""
    try:
        if hasattr(cache_service, 'cleanup'):
            cache_service.cleanup()
        
        if hasattr(speech_service, 'cleanup'):
            speech_service.cleanup()
        
        return True
    except Exception as e:
        print(f"Error cleaning up services: {e}")
        return False
