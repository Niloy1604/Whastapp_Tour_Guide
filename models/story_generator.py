import openai
import json
import re
from config import Config

class StoryGenerator:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.system_prompts = {
            'en': """You are "CityChai", a friendly Indian local guide. Generate 3 numbered recommendations for {city} matching {mood} mood. Each recommendation should be:
- One place name
- One sentence cultural story/fact
- Under 50 words each
- Format: "1. [Place] - [Story]"
End with "Reply 1/2/3 for more 📜" """,
            
            'hi': """आप "CityChai" हैं, एक मित्रवत भारतीय स्थानीय गाइड। {city} के लिए {mood} मूड के अनुसार 3 संख्याबद्ध सुझाव दें। प्रत्येक सुझाव में हो:
- एक स्थान का नाम
- एक वाक्य सांस्कृतिक कहानी/तथ्य
- 50 शब्दों से कम
- प्रारूप: "1. [स्थान] - [कहानी]"
अंत में "Reply 1/2/3 for more 📜" लिखें""",
            
            'bn': """আপনি "CityChai", একজন বন্ধুত্বপূর্ণ ভারতীয় স্থানীয় গাইড। {city} এর জন্য {mood} মেজাজ অনুযায়ী 3টি সংখ্যাযুক্ত সুপারিশ দিন। প্রতিটি সুপারিশে থাকবে:
- একটি স্থানের নাম
- একটি বাক্য সাংস্কৃতিক গল্প/তথ্য
- 50 শব্দের কম
- ফরম্যাট: "1. [স্থান] - [গল্প]"
শেষে "Reply 1/2/3 for more 📜" লিখুন"""
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
                    {"role": "user", "content": f"Suggest places in {city} for {mood} mood"}
                ],
                max_tokens=300,
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
            match = re.match(r'(\d+)\.\s*(.+?)\s*[-–]\s*(.+)', line)
            if match:
                number, place, story = match.groups()
                recommendations.append({
                    'number': int(number),
                    'place': place.strip(),
                    'story': story.strip(),
                    'full_text': line
                })
        
        return recommendations[:3]
    
    def generate_detailed_story(self, recommendation, language='en'):
        """Generate detailed story for selected recommendation"""
        try:
            prompts = {
                'en': f"Tell a detailed story about {recommendation['place']} in 3-4 sentences. Include history, legends, and tips. Keep under 200 words.",
                'hi': f"{recommendation['place']} के बारे में 3-4 वाक्यों में विस्तृत कहानी बताएं। इतिहास, किंवदंतियां और सुझाव शामिल करें। 200 शब्दों से कम रखें।",
                'bn': f"{recommendation['place']} সম্পর্কে 3-4 বাক্যে বিস्तृত গল্প বলুন। ইতিহাস, কিংবদন্তি এবং পরামর্শ অন্তর্ভুক্ত করুন। 200 শব্দের কম রাখুন।"
            }
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompts.get(language, prompts['en'])}
                ],
                max_tokens=250,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating detailed story: {e}")
            return self.get_fallback_detailed_story(recommendation, language)
    
    def get_fallback_recommendations(self, city, mood, language='en'):
        """Fallback recommendations when API fails"""
        fallback_data = {
            'Delhi': [
                {'number': 1, 'place': 'Red Fort', 'story': 'Mughal emperors ruled from these red sandstone walls', 'full_text': '1. Red Fort - Mughal emperors ruled from these red sandstone walls'},
                {'number': 2, 'place': 'India Gate', 'story': 'Memorial arch honoring 70,000 Indian soldiers', 'full_text': '2. India Gate - Memorial arch honoring 70,000 Indian soldiers'},
                {'number': 3, 'place': 'Lotus Temple', 'story': 'Bahai house of worship shaped like a blooming lotus', 'full_text': '3. Lotus Temple - Bahai house of worship shaped like a blooming lotus'}
            ]
        }
        
        return fallback_data.get(city, fallback_data['Delhi'])
    
    def get_fallback_detailed_story(self, recommendation, language='en'):
        """Fallback detailed story when API fails"""
        stories = {
            'en': f"The {recommendation['place']} is a magnificent destination with rich history and cultural significance. Visitors often describe it as a place where past and present beautifully blend together. It's definitely worth exploring!",
            'hi': f"{recommendation['place']} एक शानदार गंतव्य है जो समृद्ध इतिहास और सांस्कृतिक महत्व से भरा है। यह निश्चित रूप से देखने लायक है!",
            'bn': f"{recommendation['place']} একটি দুর্দান্ত গন্তব্য যা সমৃদ্ধ ইতিহাস এবং সাংস্কৃতিক তাৎপর্য নিয়ে ভরপুর। এটি অবশ্যই দেখার মতো!"
        }
        
        return stories.get(language, stories['en'])
