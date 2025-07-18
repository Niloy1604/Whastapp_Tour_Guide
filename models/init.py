"""
Models package for WhatsApp AI City Guide
Contains language detection, mood analysis, and story generation models
"""

from .language_detector import LanguageDetector
from .mood_detector import MoodDetector
from .story_generator import StoryGenerator

__all__ = [
    'LanguageDetector',
    'MoodDetector', 
    'StoryGenerator'
]

__version__ = '1.0.0'
__author__ = 'CityChai Team'
__description__ = 'AI models for multilingual city guide functionality'

# Initialize default instances for easy import
language_detector = LanguageDetector()
mood_detector = MoodDetector()
story_generator = StoryGenerator()

# Export convenience functions
def detect_language(text):
    """Convenience function for language detection"""
    return language_detector.detect_language(text)

def detect_mood(text, language='en'):
    """Convenience function for mood detection"""
    return mood_detector.detect_mood(text, language)

def generate_story(city, mood, language='en'):
    """Convenience function for story generation"""
    return story_generator.generate_recommendations(city, mood, language)
