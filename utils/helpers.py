import re
from datetime import datetime
from config import Config

class MessageHelper:
    @staticmethod
    def extract_city_from_text(text):
        """Extract city name from text"""
        indian_cities = [
            'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad',
            'Pune', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore',
            'Agra', 'Varanasi', 'Goa', 'Udaipur', 'Jodhpur', 'Amritsar'
        ]
        
        hindi_cities = {
            'दिल्ली': 'Delhi', 'मुंबई': 'Mumbai', 'बैंगलोर': 'Bangalore',
            'चेन्नई': 'Chennai', 'कोलकाता': 'Kolkata', 'जयपुर': 'Jaipur',
            'आगरा': 'Agra', 'गोवा': 'Goa'
        }
        
        bengali_cities = {
            'দিল্লি': 'Delhi', 'মুম্বাই': 'Mumbai', 'কলকাতা': 'Kolkata',
            'চেন্নাই': 'Chennai', 'ব্যাঙ্গালোর': 'Bangalore', 'জয়পুর': 'Jaipur',
            'আগরা': 'Agra', 'গোয়া': 'Goa'
        }
        
        text_lower = text.lower()
        
        # Check English cities
        for city in indian_cities:
            if city.lower() in text_lower:
                return city
        
        # Check Hindi cities
        for hindi_city, english_city in hindi_cities.items():
            if hindi_city in text:
                return english_city
        
        # Check Bengali cities
        for bengali_city, english_city in bengali_cities.items():
            if bengali_city in text:
                return english_city
        
        return None
    
    @staticmethod
    def extract_selection_number(text):
        """Extract selection number from user input"""
        text = text.strip().lower()
        
        patterns = [
            r'^(\d+)$',
            r'^(\d+)\.?$',
            r'reply\s*(\d+)',
            r'option\s*(\d+)',
            r'choice\s*(\d+)',
            r'select\s*(\d+)',
            r'(\d+)\s*please',
            r'number\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                number = int(match.group(1))
                if 1 <= number <= 3:
                    return number
        
        return None
    
    @staticmethod
    def clean_text(text):
        """Clean text for processing"""
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\u0900-\u097F\u0980-\u09FF.,!?-]', '', text)
        
        return text
    
    @staticmethod
    def is_greeting(text):
        """Check if text is a greeting"""
        greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'start', 'begin', 'help', 'guide',
            'नमस्ते', 'हैलो', 'हाय', 'प्रणाम', 'शुभ प्रभात', 'शुभ संध्या',
            'शुरू', 'आरंभ', 'मदद', 'गाइड',
            'নমস্কার', 'হ্যালো', 'হাই', 'প্রণাম', 'শুভ সকাল', 'শুভ সন্ধ্যা',
            'শুরু', 'আরম্ভ', 'সাহায্য', 'গাইড'
        ]
        
        text_lower = text.lower()
        return any(greeting in text_lower for greeting in greetings)
    
    @staticmethod
    def get_error_message(language, error_type='general'):
        """Get error message in appropriate language"""
        error_messages = {
            'general': {
                'en': "Sorry, I'm having trouble understanding. Please try again!",
                'hi': "माफ़ करें, मुझे समझने में परेशानी हो रही है। कृपया पुनः प्रयास करें!",
                'bn': "দুঃখিত, আমার বুঝতে সমস্যা হচ্ছে। অনুগ্রহ করে আবার চেষ্টা করুন!"
            },
            'city_not_found': {
                'en': "I couldn't find your city. Please mention the city name clearly.",
                'hi': "मुझे आपका शहर नहीं মিला। कृपया शहর का नाम स्पष्ट रूप से बताएं।",
                'bn': "আমি আপনার शहর खুঁজে পাইনি। অনুগ্রহ করে শহরের নাম স্পষ্টভাবে বলুন।"
            },
            'invalid_selection': {
                'en': "Please reply with 1, 2, or 3 to get more details.",
                'hi': "কৃপया अधिक विवरण के लिए 1, 2, या 3 का उत्तर दें।",
                'bn': "আরো বিस্তারিত জানতে অনুগ্রহ করে 1, 2, অথবা 3 उत्तर दिন।"
            }
        }
        
        return error_messages.get(error_type, error_messages['general']).get(language, error_messages['general']['en'])

class ValidationHelper:
    @staticmethod
    def validate_phone_number(phone_number):
        """Validate WhatsApp phone number format"""
        if phone_number.startswith('whatsapp:'):
            phone_number = phone_number[9:]
        
        pattern = r'^\+\d{10,15}$'
        return re.match(pattern, phone_number) is not None
    
    @staticmethod
    def validate_language(language):
        """Validate language code"""
        return language in Config.SUPPORTED_LANGUAGES
    
    @staticmethod
    def validate_mood(mood):
        """Validate mood value"""
        valid_moods = ['curious', 'adventurous', 'relaxed', 'cultural']
        return mood in valid_moods
