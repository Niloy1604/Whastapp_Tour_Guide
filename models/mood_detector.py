import re
from textblob import TextBlob
import numpy as np

class MoodDetector:
    def __init__(self):
        self.mood_keywords = {
            'curious': {
                'en': ['history', 'story', 'learn', 'discover', 'culture', 'heritage', 'ancient', 'traditional', 'why', 'how', 'when', 'what'],
                'hi': ['इतिहास', 'कहानी', 'सीखना', 'खोजना', 'संस्कृति', 'विरासत', 'पुराना', 'पारंपरिक', 'क्यों', 'कैसे', 'कब', 'क्या'],
                'bn': ['ইতিহাস', 'গল্প', 'শিখতে', 'আবিষ্কার', 'সংস্কৃতি', 'ঐতিহ্য', 'পুরাতন', 'ঐতিহ্যবাহী', 'কেন', 'কিভাবে', 'কখন', 'কি']
            },
            'adventurous': {
                'en': ['adventure', 'exciting', 'fun', 'thrill', 'explore', 'wild', 'active', 'sports', 'trek', 'climb', 'ride'],
                'hi': ['रोमांच', 'उत्साहजनक', 'मजेदार', 'रोमांचक', 'खोजना', 'जंगली', 'सक्रिय', 'खेल', 'ट्रेक', 'चढ़ाई', 'सवारी'],
                'bn': ['অ্যাডভেঞ্চার', 'উত্তেজনাপূর্ণ', 'মজার', 'রোমাঞ্চকর', 'অন্বেষণ', 'বন্য', 'সক্রিয়', 'খেলা', 'ট্রেক', 'আরোহণ', 'যাত্রা']
            },
            'relaxed': {
                'en': ['relax', 'peaceful', 'calm', 'quiet', 'serene', 'rest', 'meditate', 'spa', 'nature', 'garden', 'beach'],
                'hi': ['आराम', 'शांतिपूर्ण', 'शांत', 'चुप', 'निर्मल', 'विश्राम', 'ध्यान', 'स्पा', 'प्रकृति', 'बगीचा', 'समुद्र तट'],
                'bn': ['আরাম', 'শান্তিপূর্ণ', 'শান্ত', 'নিরব', 'নির্মল', 'বিশ্রাম', 'ধ্যান', 'স্পা', 'প্রকৃতি', 'বাগান', 'সমুদ্র সৈকত']
            },
            'cultural': {
                'en': ['temple', 'museum', 'art', 'festival', 'ceremony', 'tradition', 'local', 'authentic', 'food', 'craft', 'music'],
                'hi': ['मंदिर', 'संग्रहालय', 'कला', 'त्योहार', 'समारोह', 'परंपरा', 'स्थानीय', 'प्रामाणिक', 'भोजन', 'शिल्प', 'संगीत'],
                'bn': ['মন্দির', 'জাদুঘর', 'শিল্প', 'উৎসব', 'অনুষ্ঠান', 'ঐতিহ্য', 'স্থানীয়', 'প্রামাণিক', 'খাবার', 'কারুশিল্প', 'সঙ্গীত']
            }
        }
    
    def detect_mood(self, text, language='en'):
        """Detect mood from text based on keywords and sentiment"""
        if not text:
            return 'curious'
        
        text_lower = text.lower()
        mood_scores = {}
        
        # Keyword-based mood detection
        for mood, lang_keywords in self.mood_keywords.items():
            keywords = lang_keywords.get(language, lang_keywords['en'])
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            mood_scores[mood] = score
        
        # Sentiment analysis boost
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.3:
                mood_scores['adventurous'] += 2
            elif polarity < -0.3:
                mood_scores['relaxed'] += 2
            else:
                mood_scores['curious'] += 1
        except:
            pass
        
        # Return mood with highest score
        if max(mood_scores.values()) == 0:
            return 'curious'  # Default mood
        
        return max(mood_scores, key=mood_scores.get)
    
    def detect_from_voice_features(self, audio_features):
        """Detect mood from voice features (simplified implementation)"""
        if not audio_features:
            return 'curious'
        
        # This is a simplified version
        # In production, you would use proper audio analysis
        energy = audio_features.get('energy', 0.5)
        tempo = audio_features.get('tempo', 120)
        
        if energy > 0.7 and tempo > 140:
            return 'adventurous'
        elif energy < 0.3 and tempo < 100:
            return 'relaxed'
        elif energy > 0.4 and tempo > 100:
            return 'cultural'
        else:
            return 'curious'
