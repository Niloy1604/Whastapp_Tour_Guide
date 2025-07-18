import re
from langdetect import detect
from textblob import TextBlob
from googletrans import Translator

class LanguageDetector:
    def __init__(self):
        self.translator = Translator()
        self.language_patterns = {
            'hi': [
                r'[\u0900-\u097F]+',  # Devanagari script
                r'\b(है|हैं|का|की|के|में|से|को|और|यह|वह|क्या|कैसे|कहाँ|कब)\b'
            ],
            'bn': [
                r'[\u0980-\u09FF]+',  # Bengali script
                r'\b(আছে|আমি|তুমি|সে|কি|কেমন|কোথায়|কখন|এবং|বা)\b'
            ],
            'en': [
                r'\b(the|is|are|was|were|have|has|will|would|could|should)\b'
            ]
        }
    
    def detect_language(self, text):
        """Detect language from text with fallback methods"""
        if not text or not text.strip():
            return 'en'
        
        # Method 1: Pattern matching for Indian languages
        for lang, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return lang
        
        # Method 2: langdetect library
        try:
            detected = detect(text)
            if detected in ['hi', 'bn', 'en']:
                return detected
        except:
            pass
        
        # Method 3: Google Translate detection
        try:
            result = self.translator.detect(text)
            if result.lang in ['hi', 'bn', 'en']:
                return result.lang
        except:
            pass
        
        # Default to English
        return 'en'
    
    def is_code_mixed(self, text):
        """Check if text contains multiple languages"""
        detected_langs = set()
        
        for lang, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected_langs.add(lang)
        
        return len(detected_langs) > 1
    
    def get_dominant_language(self, text):
        """Get dominant language in code-mixed text"""
        if not self.is_code_mixed(text):
            return self.detect_language(text)
        
        # Count script characters
        script_counts = {
            'hi': len(re.findall(r'[\u0900-\u097F]', text)),
            'bn': len(re.findall(r'[\u0980-\u09FF]', text)),
            'en': len(re.findall(r'[a-zA-Z]', text))
        }
        
        return max(script_counts, key=script_counts.get)
