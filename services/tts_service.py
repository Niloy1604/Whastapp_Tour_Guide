import asyncio
import tempfile
import os
import uuid
import json
import re
from gtts import gTTS
from typing import Optional, Dict
import logging

class TTSService:
    def __init__(self):
        # Load language data
        self.language_data = self._load_language_data()
        
        # Enhanced language support for TTS with voice settings
        self.gtts_languages = {}
        self.voice_settings = {}
        
        self._initialize_tts_config()
        
        self.temp_dir = tempfile.gettempdir()
        print(f"✅ TTS Service initialized with {len(self.gtts_languages)} languages")
    
    def _load_language_data(self) -> Dict:
        """Load language configuration from languages.json."""
        try:
            lang_file = os.path.join('data', 'languages.json')
            with open(lang_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load languages.json: {e}")
            return {}

    def _initialize_tts_config(self):
        """Initialize TTS configuration from language data."""
        supported_langs = self.language_data.get('supported_languages', {})
        
        for lang_code, lang_info in supported_langs.items():
            if lang_info.get('tts_supported', False):
                self.gtts_languages[lang_code] = lang_info.get('gtts_code', lang_code)
                self.voice_settings[lang_code] = lang_info.get('voice_settings', {
                    'speed': 'normal',
                    'pitch': 'medium',
                    'accent': 'indian'
                })
    
    async def text_to_speech(self, text: str, language: str = 'en') -> Optional[str]:
        """Generate high-quality speech from text with language-specific settings."""
        try:
            # Validate language support
            if not self._is_tts_supported(language):
                print(f"⚠️ TTS not supported for {language}, falling back to English")
                language = 'en'
            
            # Clean text for optimal TTS
            clean_text = self._clean_text_for_tts(text, language)
            
            if not clean_text.strip():
                print("⚠️ Empty text after cleaning, skipping TTS")
                return None
            
            # Get language-specific settings
            gtts_lang = self.gtts_languages.get(language, 'en')
            voice_settings = self.voice_settings.get(language, {})
            
            # Create unique audio file
            audio_filename = f"tts_{language}_{uuid.uuid4().hex}.mp3"
            audio_path = os.path.join(self.temp_dir, audio_filename)
            
            print(f"🔊 Generating TTS for {gtts_lang}: {clean_text[:50]}...")
            
            # Generate speech with enhanced settings
            tts = gTTS(
                text=clean_text,
                lang=gtts_lang,
                slow=voice_settings.get('speed') == 'slow',
                tld=self._get_tld_for_language(language)
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: tts.save(audio_path)
            )
            
            print(f"✅ TTS audio saved: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"❌ TTS generation error: {e}")
            return None

    def _is_tts_supported(self, language: str) -> bool:
        """Check if TTS is supported for the language."""
        lang_info = self.language_data.get('supported_languages', {}).get(language, {})
        return lang_info.get('tts_supported', False)

    def _get_tld_for_language(self, language: str) -> str:
        """Get appropriate TLD for better voice quality."""
        tld_map = {
            'en': 'com',
            'hi': 'co.in',
            'bn': 'co.in',
            'ta': 'co.in',
            'te': 'co.in',
            'ml': 'co.in',
            'kn': 'co.in',
            'gu': 'co.in',
            'mr': 'co.in',
            'pa': 'co.in',
            'or': 'co.in',
            'ur': 'com.pk'
        }
        return tld_map.get(language, 'com')
    
    def _clean_text_for_tts(self, text: str, language: str) -> str:
        """Advanced text cleaning for natural speech by language."""
        
        # Remove bot prefixes
        text = re.sub(r'^🤖\s*', '', text)
        text = re.sub(r'^💡\s*', '', text)
        
        # Language-specific cleaning
        if language in ['hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'mr', 'pa', 'or', 'ur']:
            # For Indian languages, preserve more emojis for natural pauses
            text = re.sub(r'[🏰🌊🏛️🎉🔥✨🌟💫⭐🌙☀️🌈🎭🎨🎪🎯🚀]', ' ', text)
            # Keep culturally relevant emojis
            text = re.sub(r'[😊😍🤔❤️💕🙏👑🇮🇳]', '.', text)
        else:
            # For English, standard emoji handling
            text = re.sub(r'[🏰🌊🏛️🇮🇳🎉🔥✨🌟💫⭐🌙☀️🌈🎭🎨🎪🎯🚀]', '', text)
            text = re.sub(r'[😊😍🤔❤️💕🙏👑]', '.', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Add natural pauses for better speech flow
        text = re.sub(r'([.!?])\s*', r'\1 ', text)
        
        # Handle numbers and abbreviations
        text = text.replace('&', 'and' if language == 'en' else 'और')
        text = text.replace('@', 'at' if language == 'en' else 'पर')
        
        # Language-specific improvements
        if language == 'hi':
            text = text.replace('vs', 'बनाम')
            text = text.replace('Dr', 'डॉक्टर')
        elif language == 'bn':
            text = text.replace('Dr', 'ডাক্তার')
        elif language == 'ta':
            text = text.replace('Dr', 'டாக்டர்')
        
        return text.strip()

    def get_voice_info(self, language: str) -> Dict:
        """Get voice information for a language."""
        return {
            'supported': self._is_tts_supported(language),
            'gtts_code': self.gtts_languages.get(language),
            'settings': self.voice_settings.get(language, {}),
            'language_name': self.language_data.get('supported_languages', {}).get(language, {}).get('name', 'Unknown')
        }

    def get_supported_languages(self) -> list:
        """Get list of TTS-supported languages."""
        return list(self.gtts_languages.keys())
    
    def cleanup_audio_file(self, file_path: str):
        """Clean up temporary audio files."""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                print(f"🗑️ Cleaned up audio file: {file_path}")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

    def batch_cleanup(self, max_age_hours: int = 24):
        """Clean up old audio files in temp directory."""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            cleaned_count = 0
            for filename in os.listdir(self.temp_dir):
                if filename.startswith('tts_') and filename.endswith('.mp3'):
                    file_path = os.path.join(self.temp_dir, filename)
                    file_age = current_time - os.path.getctime(file_path)
                    
                    if file_age > max_age_seconds:
                        self.cleanup_audio_file(file_path)
                        cleaned_count += 1
            
            if cleaned_count > 0:
                print(f"🧹 Cleaned up {cleaned_count} old audio files")
                
        except Exception as e:
            print(f"❌ Batch cleanup error: {e}")
