import re
import json
import os
from langdetect import detect
from typing import Tuple, Dict, List, Optional

class QuickLanguageDetector:
    def __init__(self):
        # Load comprehensive language data
        self.language_data = self._load_language_data()
        self.supported_languages = list(self.language_data.get('supported_languages', {}).keys())
        
        # Enhanced Unicode patterns from languages.json
        self.script_patterns = {}
        self.keyword_patterns = {}
        self.strong_indicators = {}
        
        self._initialize_detection_patterns()
        print(f"✅ Language detector initialized with {len(self.supported_languages)} languages")

    def _load_language_data(self) -> Dict:
        """Load comprehensive language data from JSON."""
        try:
            lang_file = os.path.join('data', 'languages.json')
            with open(lang_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load languages.json: {e}")
            return self._get_fallback_language_data()

    def _get_fallback_language_data(self) -> Dict:
        """Fallback language data if JSON fails to load."""
        return {
            'supported_languages': {
                'en': {'name': 'English', 'tts_supported': True, 'stt_supported': True},
                'hi': {'name': 'Hindi', 'tts_supported': True, 'stt_supported': True},
                'bn': {'name': 'Bengali', 'tts_supported': True, 'stt_supported': True}
            }
        }

    def _initialize_detection_patterns(self):
        """Initialize detection patterns from language data."""
        
        # Unicode script patterns
        self.script_patterns = {
            'hi': r'[\u0900-\u097F]+',   # Devanagari (Hindi, Marathi)
            'bn': r'[\u0980-\u09FF]+',   # Bengali script  
            'ta': r'[\u0B80-\u0BFF]+',   # Tamil script
            'te': r'[\u0C00-\u0C7F]+',   # Telugu script
            'gu': r'[\u0A80-\u0AFF]+',   # Gujarati script
            'kn': r'[\u0C80-\u0CFF]+',   # Kannada script
            'ml': r'[\u0D00-\u0D7F]+',   # Malayalam script
            'mr': r'[\u0900-\u097F]+',   # Marathi (shares Devanagari)
            'pa': r'[\u0A00-\u0A7F]+',   # Punjabi (Gurmukhi)
            'or': r'[\u0B00-\u0B7F]+',   # Odia script
            'as': r'[\u0980-\u09FF]+',   # Assamese (similar to Bengali)
            'ur': r'[\u0600-\u06FF]+',   # Arabic/Urdu script
        }

        # Enhanced keyword patterns with sample phrases from languages.json
        for lang_code, lang_info in self.language_data.get('supported_languages', {}).items():
            sample_phrases = lang_info.get('sample_phrases', {})
            
            # Extract keywords from sample phrases
            keywords = []
            for phrase in sample_phrases.values():
                if isinstance(phrase, str):
                    # Split into words and add to keywords
                    words = phrase.split()
                    keywords.extend([word.strip('.,!?') for word in words if len(word.strip('.,!?')) > 2])
            
            if keywords:
                self.keyword_patterns[lang_code] = keywords

        # Strong indicators for high-confidence detection
        self.strong_indicators = {
            'hi': ['राजस्थान', 'जयपुर', 'किले', 'बताओ', 'दिल्ली', 'मुंबई', 'भारत', 'कहानी', 'सुनाओ'],
            'bn': ['কোথায়', 'কেল্লা', 'লাল', 'বলুন', 'সম্পর্কে', 'বাংলাদেশ', 'কলকাতা', 'কহানী'],
            'ta': ['சொல்லுங்கள்', 'கோட்டை', 'சிவப்பு', 'பற்றி', 'தமிழ்நாடு', 'சென்னை', 'கதை'],
            'te': ['చెప్పండి', 'గురించి', 'కోట', 'ఎర్ర', 'తెలంగాణ', 'హైదరాబాద్', 'కథ'],
            'ml': ['പറയൂ', 'കുറിച്ച്', 'കോട്ട', 'ചുവന്ന', 'കേരളം', 'കൊച്ചി', 'കഥ'],
            'kn': ['ಹೇಳಿ', 'ಬಗ್ಗೆ', 'ಕೋಟೆ', 'ಕೆಂಪು', 'ಕರ್ನಾಟಕ', 'ಬೆಂಗಳೂರು', 'ಕಥೆ'],
            'gu': ['કહો', 'વિશે', 'કિલ્લો', 'લાલ', 'ગુજરાત', 'અમદાવાદ', 'વાર્તા'],
            'mr': ['सांगा', 'बद्दल', 'किल्ला', 'लाल', 'महाराष्ट्र', 'मुंबई', 'गोष्ट'],
            'pa': ['ਕਹਿੰਦੇ', 'ਬਾਰੇ', 'ਕਿਲ੍ਹਾ', 'ਲਾਲ', 'ਪੰਜਾਬ', 'ਚੰਡੀਗੜ੍ਹ'],
            'or': ['କୁହନ୍ତୁ', 'ବିଷୟରେ', 'ଦୁର୍ଗ', 'ଲାଲ୍', 'ଓଡ଼ିଶା'],
            'as': ['কওক', 'বিষয়ে', 'দুৰ্গ', 'ৰঙা', 'অসম'],
            'ur': ['بتائیں', 'کے بارے', 'قلعہ', 'لال', 'اردو'],
            'en': ['tell', 'about', 'fort', 'red', 'story', 'india', 'explore', 'visit']
        }

    def detect_language(self, text: str) -> Tuple[str, float]:
        """Enhanced language detection with priority-based approach."""
        if not text or not text.strip():
            return ('en', 0.0)

        print(f"🔍 Detecting language for: '{text}'")

        # Method 1: Strong indicators check (highest priority)
        strong_result = self._check_strong_indicators(text)
        if strong_result[1] > 0.0:
            print(f"🎯 Strong indicator detection: {strong_result}")
            return strong_result

        # Method 2: Script detection (high priority)
        script_result = self._detect_by_script(text)
        print(f"📝 Script detection: {script_result}")
        if script_result[1] > 0.2:
            return script_result

        # Method 3: Keyword matching from sample phrases (medium priority)
        keyword_result = self._detect_by_keywords(text)
        print(f"🔑 Keyword detection: {keyword_result}")
        if keyword_result[1] > 0.15:
            return keyword_result

        # Method 4: langdetect with corrections (lowest priority)
        try:
            detected = detect(text)
            print(f"🌐 Langdetect result: {detected}")
            
            # Fix common misdetections
            if detected in ['nl', 'no', 'da', 'sv', 'de']:
                # Check if it might be Bengali
                if re.search(self.script_patterns.get('bn', ''), text):
                    print(f"🔄 Correcting {detected} -> bn")
                    return ('bn', 0.8)
            
            # Return langdetect result if it's a supported language
            if detected in self.supported_languages:
                return (detected, 0.7)
            
        except Exception as e:
            print(f"❌ Langdetect error: {e}")

        # Default to English
        print("🔄 Defaulting to English")
        return ('en', 0.0)

    def _check_strong_indicators(self, text: str) -> Tuple[str, float]:
        """Check for strong language-specific indicators."""
        text_lower = text.lower()
        
        for lang, indicators in self.strong_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text)
            if matches > 0:
                confidence = min(matches * 0.5, 1.0)
                return (lang, confidence)
        
        return ('en', 0.0)

    def _detect_by_script(self, text: str) -> Tuple[str, float]:
        """Detect language by Unicode script patterns."""
        total_chars = len(text)
        if total_chars == 0:
            return ('en', 0.0)

        best_lang = 'en'
        highest_confidence = 0.0

        for lang, pattern in self.script_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                char_count = sum(len(match) for match in matches)
                confidence = char_count / total_chars
                
                if confidence > highest_confidence:
                    best_lang = lang
                    highest_confidence = confidence

        return (best_lang, highest_confidence)

    def _detect_by_keywords(self, text: str) -> Tuple[str, float]:
        """Detect language by keywords from sample phrases."""
        words = text.split()
        if not words:
            return ('en', 0.0)

        best_lang = 'en'
        best_score = 0.0

        for lang, keywords in self.keyword_patterns.items():
            matches = 0
            for word in words:
                for keyword in keywords:
                    if keyword in word:
                        matches += 1
                        break
            
            if matches > 0:
                score = matches / len(words)
                if score > best_score:
                    best_lang = lang
                    best_score = score

        return (best_lang, best_score)

    def get_language_info(self, lang_code: str) -> Dict:
        """Get comprehensive language information."""
        return self.language_data.get('supported_languages', {}).get(lang_code, {})

    def is_voice_supported(self, lang_code: str) -> bool:
        """Check if voice (TTS/STT) is supported for language."""
        lang_info = self.get_language_info(lang_code)
        return lang_info.get('tts_supported', False) and lang_info.get('stt_supported', False)

    def get_language_name(self, code: str) -> str:
        """Get full language name from code."""
        lang_info = self.get_language_info(code)
        return lang_info.get('name', 'English')

    def get_native_name(self, code: str) -> str:
        """Get native language name."""
        lang_info = self.get_language_info(code)
        return lang_info.get('native_name', 'English')

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return self.supported_languages

    def get_greeting(self, lang_code: str, style: str = 'formal') -> str:
        """Get culturally appropriate greeting."""
        greetings = self.language_data.get('cultural_greetings', {}).get(style, {})
        return greetings.get(lang_code, greetings.get('en', 'Welcome!'))
