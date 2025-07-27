import re
from typing import Dict, List, Tuple
from textblob import TextBlob
import json

class MoodAnalyzer:
    def __init__(self):
        # Multilingual mood keywords
        self.mood_keywords = {
            'excited': {
                'en': ['excited', 'thrilled', 'amazing', 'awesome', 'fantastic', 'incredible', 'wow'],
                'hi': ['उत्साहित', 'रोमांचित', 'शानदार', 'अद्भुत', 'बेहतरीन', 'वाह'],
                'bn': ['উত্তেজিত', 'রোমাঞ্চিত', 'দুর্দান্ত', 'অসাধারণ', 'চমৎকার', 'বাহ'],
                'ta': ['உற்சாகம்', 'அருமையான', 'அற்புதம்', 'சூப்பர்', 'வாவ்'],
                'te': ['ఉత్సాహం', 'అద్భుతం', 'అచ్చం', 'సూపర్', 'వావ్'],
                'ml': ['ആവേശം', 'അത്ഭുതം', 'സൂപ്പർ', 'വാവ്', 'കൊള്ളാം']
            },
            'tired': {
                'en': ['tired', 'exhausted', 'weary', 'drained', 'fatigue', 'sleepy', 'rest'],
                'hi': ['थका', 'थकान', 'आराम', 'सुस्त', 'नींद', 'विश्राम'],
                'bn': ['ক্লান্ত', 'ক্লান্তি', 'বিশ্রাম', 'ঘুম', 'আরাম'],
                'ta': ['சோர்வு', 'களைப்பு', 'ஓய்வு', 'தூக்கம்', 'அமைதி'],
                'te': ['అలసట', 'విశ్రాంతి', 'నిద్ర', 'శాంతి'],
                'ml': ['ക്ഷീണം', 'വിശ്രമം', 'ഉറക്കം', 'സമാധാനം']
            },
            'curious': {
                'en': ['curious', 'interested', 'explore', 'discover', 'learn', 'know', 'tell me'],
                'hi': ['जिज्ञासु', 'रुचि', 'खोज', 'जानना', 'बताओ', 'सीखना'],
                'bn': ['কৌতূহলী', 'আগ্রহী', 'অন্বেষণ', 'জানতে', 'বলুন', 'শিখতে'],
                'ta': ['ஆர்வம்', 'அறிய', 'கற்க', 'சொல்லுங்கள்', 'தெரிந்து'],
                'te': ['ఆసక్తి', 'తెలుసుకోవాలి', 'నేర్చుకోవాలి', 'చెప్పండి'],
                'ml': ['ആകാംക്ഷ', 'അറിയാൻ', 'പഠിക്കാൻ', 'പറയൂ', 'കണ്ടെത്താൻ']
            },
            'peaceful': {
                'en': ['peaceful', 'calm', 'serene', 'quiet', 'tranquil', 'relax', 'meditation'],
                'hi': ['शांत', 'आराम', 'स्थिर', 'मन', 'ध्यान', 'सुकून'],
                'bn': ['শান্ত', 'শান্তি', 'আরাম', 'স্থির', 'ধ্যান'],
                'ta': ['அமைதி', 'அமைதியான', 'அசைவற்ற', 'தியானம்'],
                'te': ['శాంతి', 'ప్రశాంతత', 'ధ్యానం', 'నిశ్చలత'],
                'ml': ['സമാധാനം', 'ശാന്തത', 'ധ്യാനം', 'സ്ഥിരത']
            },
            'adventurous': {
                'en': ['adventure', 'explore', 'exciting', 'thrill', 'journey', 'travel', 'experience'],
                'hi': ['साहसिक', 'यात्रा', 'अनुभव', 'रोमांच', 'खोज'],
                'bn': ['অ্যাডভেঞ্চার', 'ভ্রমণ', 'অভিজ্ঞতা', 'রোমাঞ্চ'],
                'ta': ['சாகசம்', 'பயணம்', 'அனுபவம்', 'ரோமாஞ்சம்'],
                'te': ['సాహసం', 'యాత్র', 'అనుభవం', 'థ్రిల్'],
                'ml': ['സാഹസം', 'യാത്ര', 'അനുഭവം', 'ത്രിൽ']
            }
        }
        
        # Energy level indicators
        self.energy_indicators = {
            'high': ['energetic', 'active', 'pumped', 'ready', 'go', 'let\'s', 'excited'],
            'medium': ['interested', 'curious', 'want', 'like', 'tell'],
            'low': ['tired', 'slow', 'calm', 'peaceful', 'rest', 'quiet']
        }
        
        print("✅ Mood analyzer initialized with multilingual support")
    
    def analyze_mood(self, text: str, language: str = 'en') -> Dict[str, str]:
        """Analyze user mood from text with language awareness."""
        
        text_lower = text.lower()
        detected_moods = []
        confidence_scores = {}
        
        # Check each mood category
        for mood, lang_keywords in self.mood_keywords.items():
            keywords = lang_keywords.get(language, lang_keywords['en'])
            
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                confidence = matches / len(keywords)
                detected_moods.append((mood, confidence))
                confidence_scores[mood] = confidence
        
        # Determine primary mood
        if detected_moods:
            primary_mood = max(detected_moods, key=lambda x: x[1])[0]
        else:
            # Fallback sentiment analysis
            primary_mood = self._sentiment_analysis_fallback(text)
        
        # Determine energy level
        energy_level = self._analyze_energy_level(text_lower)
        
        # Determine emotional state
        emotional_state = self._analyze_emotional_state(text, language)
        
        return {
            'mood': primary_mood,
            'energy_level': energy_level,
            'emotional_state': emotional_state,
            'confidence_scores': confidence_scores,
            'detected_moods': [mood for mood, _ in detected_moods]
        }
    
    def _sentiment_analysis_fallback(self, text: str) -> str:
        """Fallback sentiment analysis using TextBlob."""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.3:
                return 'excited'
            elif polarity < -0.3:
                return 'tired'
            else:
                return 'curious'
                
        except Exception:
            return 'curious'
    
    def _analyze_energy_level(self, text_lower: str) -> str:
        """Analyze energy level from text."""
        
        high_score = sum(1 for indicator in self.energy_indicators['high'] if indicator in text_lower)
        medium_score = sum(1 for indicator in self.energy_indicators['medium'] if indicator in text_lower)
        low_score = sum(1 for indicator in self.energy_indicators['low'] if indicator in text_lower)
        
        scores = {'high': high_score, 'medium': medium_score, 'low': low_score}
        
        if max(scores.values()) == 0:
            return 'medium'  # Default
        
        return max(scores, key=scores.get)
    
    def _analyze_emotional_state(self, text: str, language: str) -> str:
        """Analyze deeper emotional state."""
        
        text_lower = text.lower()
        
        # Positive emotions
        positive_indicators = {
            'en': ['happy', 'joy', 'love', 'wonderful', 'beautiful', 'amazing'],
            'hi': ['खुश', 'प्रसन्न', 'खुशी', 'सुंदर', 'प्यार'],
            'bn': ['খুশি', 'আনন্দ', 'ভালোবাসা', 'সুন্দর'],
            'ta': ['மகிழ்ச்சி', 'அன்பு', 'அழகு', 'இனிமை'],
            'te': ['సంతోషం', 'ప్రేమ', 'అందం', 'మధురం'],
            'ml': ['സന്തോഷം', 'സ്നേഹം', 'സുന്ദരം', 'മധുരം']
        }
        
        # Negative emotions
        negative_indicators = {
            'en': ['sad', 'worried', 'confused', 'frustrated', 'anxious'],
            'hi': ['उदास', 'चिंतित', 'परेशान', 'घबराहट'],
            'bn': ['দুঃখিত', 'চিন্তিত', 'বিভ্রান্ত'],
            'ta': ['சோகம்', 'கவலை', 'குழப்பம்'],
            'te': ['దుఃఖం', 'ఆందోళన', 'గందరగోళం'],
            'ml': ['ദുഃഖം', 'ആകുലത', 'ആശയക്കുഴപ്പം']
        }
        
        pos_keywords = positive_indicators.get(language, positive_indicators['en'])
        neg_keywords = negative_indicators.get(language, negative_indicators['en'])
        
        pos_score = sum(1 for keyword in pos_keywords if keyword in text_lower)
        neg_score = sum(1 for keyword in neg_keywords if keyword in text_lower)
        
        if pos_score > neg_score:
            return 'positive'
        elif neg_score > pos_score:
            return 'negative'
        else:
            return 'neutral'
    
    def get_mood_recommendations(self, mood: str, location: str = None) -> List[str]:
        """Get location recommendations based on mood."""
        
        recommendations = {
            'excited': [
                "bustling markets and vibrant street life",
                "adventure sports and activities",
                "festivals and cultural events",
                "nightlife and entertainment"
            ],
            'tired': [
                "peaceful gardens and parks",
                "quiet temples and spiritual places",
                "spa and wellness centers",
                "serene lakes and nature spots"
            ],
            'curious': [
                "museums and historical sites",
                "cultural tours and heritage walks",
                "local workshops and demonstrations",
                "architectural marvels"
            ],
            'peaceful': [
                "meditation centers and ashrams",
                "quiet beaches and hillstations",
                "botanical gardens",
                "sunrise/sunset viewpoints"
            ],
            'adventurous': [
                "trekking and hiking trails",
                "water sports and activities",
                "off-beat destinations",
                "local food adventures"
            ]
        }
        
        return recommendations.get(mood, recommendations['curious'])
