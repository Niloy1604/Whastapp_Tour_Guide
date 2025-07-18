import openai
import json
import re
from config import Config

class StoryGenerator:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.system_prompts = {
            'en': """You are "CityChai", a friendly Indian local who replies on WhatsApp.
Always:
• speak in English
• keep responses ≤160 characters
• weave a 1-sentence cultural story for each place
• match mood: {mood} (curious/adventurous/relaxed/cultural)
• end with: "Reply 1/2/3 for more 📜"

User context:
City: {city}
Mood: {mood}
========================================================
Task:
1. Return exactly 3 numbered recommendations.
2. Each line: "{number}. {Place} – {1-sentence story}"
3. No extra text before or after the list.""",
            
            'hi': """आप "CityChai" हैं, एक मित्रवत भारतीय स्थानीय जो WhatsApp पर जवाब देते हैं।
हमेशा:
• हिंदी में बोलें
• जवाब ≤160 अक्षरों में रखें
• हर जगह के लिए 1-वाक्य की सांस्कृतिक कहानी बुनें
• मूड के अनुसार: {mood} (curious/adventurous/relaxed/cultural)
• अंत में: "Reply 1/2/3 for more 📜"

यूजर संदर्भ:
शहर: {city}
मूड: {mood}
========================================================
कार्य:
1. ठीक 3 संख्याबद्ध सुझाव दें।
2. हर लाइन: "{number}. {Place} – {1-sentence story}"
3. सूची से पहले या बाद में कोई अतिरिक्त टेक्स्ट नहीं।""",
            
            'bn': """আপনি "CityChai", একজন বন্ধুত্ব্যপূর্ণ ভারতীয় স্থানীয় যিনি WhatsApp এ উত্তর দেন।
সর্বদা:
• বাংলায় কথা বলুন
• উত্তর ≤160 অক্ষরে রাখুন
• প্রতিটি স্থানের জন্য 1-বাক্য সাংস্কৃতিক গল্প বুনুন
• মেজাজ অনুযায়ী: {mood} (curious/adventurous/relaxed/cultural)
• শেষে: "Reply 1/2/3 for more 📜"

ব্যবহারকারী প্রসঙ্গ:
শহর: {city}
মেজাজ: {mood}
========================================================
কাজ:
1. ঠিক 3টি সংখ্যাযুক্ত সুপারিশ দিন।
2. প্রতিটি লাইন: "{number}. {Place} – {1-sentence story}"
3. তালিকার আগে বা পরে কোনো অতিরিক্ত টেক্সট নেই।"""
        }
    
    def generate_recommendations(self, city, mood, language='en'):
        """Generate 3 story-driven recommendations"""
        try:
            system_prompt = self.system_prompts.get(language, self.system_prompts['en'])
            formatted_prompt = system_prompt.format(city=city, mood=mood)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": formatted_prompt},
                    {"role": "user", "content": f"Tell me about places to visit in {city} that match my {mood} mood"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            return self.parse_recommendations(content)
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self.get_fallback_recommendations(city, mood, language)
    
    def parse_recommendations(self, content):
        """Parse LLM response into structured recommendations"""
        lines = content.split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip()
            # Match numbered recommendations
            match = re.match(r'(\d+)\.\s*(.+?)\s*–\s*(.+)', line)
            if match:
                number, place, story = match.groups()
                recommendations.append({
                    'number': int(number),
                    'place': place.strip(),
                    'story': story.strip(),
                    'full_text': line
                })
        
        return recommendations[:3]  # Ensure only 3 recommendations
    
    def generate_detailed_story(self, recommendation, language='en'):
        """Generate detailed story for selected recommendation"""
        try:
            prompts = {
                'en': f"Tell a detailed, engaging story about {recommendation['place']} in 2-3 sentences. Include historical facts, local legends, and what makes it special. Keep it under 300 characters.",
                'hi': f"{recommendation['place']} के बारे में 2-3 वाक्यों में एक विस्तृत, दिलचस्प कहानी बताएं। ऐतिहासिक तथ्य, स्थानीय किंवदंतियां और इसकी विशेषता शामिल करें। 300 अक्षरों के अंदर रखें।",
                'bn': f"{recommendation['place']} সম্পর্কে 2-3 বাক্যে একটি বিস্তৃত, আকর্ষণীয় গল্প বলুন। ঐতিহাসিক তথ্য, স্থানীয় কিংবদন্তি এবং এটি কী বিশেষ করে তোলে তা অন্তর্ভুক্ত করুন। 300 অক্ষরের মধ্যে রাখুন।"
            }
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompts.get(language, prompts['en'])}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating detailed story: {e}")
            return self.get_fallback_detailed_story(recommendation, language)
    
    def get_fallback_recommendations(self, city, mood, language='en'):
        """Fallback recommendations when API fails"""
        fallback_data = {
            'Delhi': {
                'en': [
                    {'number': 1, 'place': 'Red Fort', 'story': 'Mughal emperors ruled from these red sandstone walls', 'full_text': '1. Red Fort – Mughal emperors ruled from these red sandstone walls'},
                    {'number': 2, 'place': 'India Gate', 'story': 'Memorial arch honoring 70,000 Indian soldiers', 'full_text': '2. India Gate – Memorial arch honoring 70,000 Indian soldiers'},
                    {'number': 3, 'place': 'Lotus Temple', 'story': 'Bahai house of worship shaped like a blooming lotus', 'full_text': '3. Lotus Temple – Bahai house of worship shaped like a blooming lotus'}
                ],
                'hi': [
                    {'number': 1, 'place': 'लाल किला', 'story': 'मुगल बादशाह यहां लाल पत्थर की दीवारों से राज करते थे', 'full_text': '1. लाल किला – मुगल बादशाह यहां लाल पत्थर की दीवारों से राज करते थे'},
                    {'number': 2, 'place': 'इंडिया गेट', 'story': '70,000 भारतीय सैनिकों को समर्पित स्मारक', 'full_text': '2. इंडिया गेट – 70,000 भारतीय सैनिकों को समर्पित स्मारक'},
                    {'number': 3, 'place': 'लोटस टेम्पल', 'story': 'कमल के फूल जैसा बहाई उपासना स्थल', 'full_text': '3. लोटस टेम्पल – कमल के फूल जैसा बहाई उपासना स्थल'}
                ]
            }
        }
        
        return fallback_data.get(city, fallback_data['Delhi']).get(language, fallback_data['Delhi']['en'])
    
    def get_fallback_detailed_story(self, recommendation, language='en'):
        """Fallback detailed story when API fails"""
        fallback_stories = {
            'en': f"The {recommendation['place']} is a magnificent destination with rich history and cultural significance. Visitors often describe it as a place where past and present beautifully blend together.",
            'hi': f"{recommendation['place']} एक शानदार गंतव्य है जो समृद्ध इतिहास और सांस्कृतिक महत्व से भरा है। पर्यटक अक्सर इसे एक ऐसी जगह बताते हैं जहां अतीत और वर्तमान खूबसूरती से मिल जाते हैं।",
            'bn': f"{recommendation['place']} একটি দুর্দান্ত গন্তব্য যা সমৃদ্ধ ইতিহাস এবং সাংস্কৃতিক তাৎপর্য নিয়ে ভরপুর। দর্শনার্থীরা প্রায়শই এটিকে এমন একটি স্থান হিসেবে বর্ণনা করেন যেখানে অতীত এবং বর্তমান সুন্দরভাবে মিশে যায়।"
        }
        
        return fallback_stories.get(language, fallback_stories['en'])
