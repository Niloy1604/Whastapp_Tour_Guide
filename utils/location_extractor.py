import re
from typing import Optional, List

class LocationExtractor:
    def __init__(self):
        # Comprehensive Indian locations with multilingual support
        self.indian_cities = {
            # Major Metro Cities
            'delhi': 'Delhi', 'new delhi': 'Delhi', 'ncr': 'Delhi',
            'mumbai': 'Mumbai', 'bombay': 'Mumbai',
            'bangalore': 'Bangalore', 'bengaluru': 'Bangalore',
            'chennai': 'Chennai', 'madras': 'Chennai',
            'kolkata': 'Kolkata', 'calcutta': 'Kolkata',
            'hyderabad': 'Hyderabad',
            'pune': 'Pune', 'poona': 'Pune',
            
            # Kerala (God's Own Country)
            'kerala': 'Kerala', 'keralam': 'Kerala',
            'kochi': 'Kochi', 'cochin': 'Kochi', 'ernakulam': 'Kochi',
            'alleppey': 'Alleppey', 'alappuzha': 'Alleppey',
            'munnar': 'Munnar',
            'kumarakom': 'Kumarakom',
            'thekkady': 'Thekkady', 'periyar': 'Thekkady',
            'kovalam': 'Kovalam',
            'varkala': 'Varkala',
            'wayanad': 'Wayanad',
            'thrissur': 'Thrissur',
            'palakkad': 'Palakkad',
            'kozhikode': 'Kozhikode', 'calicut': 'Kozhikode',
            'kannur': 'Kannur',
            'kollam': 'Kollam',
            'fort kochi': 'Fort Kochi', 'fort cochin': 'Fort Kochi',
            'backwaters': 'Kerala Backwaters',
            
            # Rajasthan (Land of Kings)
            'rajasthan': 'Rajasthan',
            'jaipur': 'Jaipur', 'pink city': 'Jaipur',
            'udaipur': 'Udaipur', 'city of lakes': 'Udaipur',
            'jodhpur': 'Jodhpur', 'blue city': 'Jodhpur',
            'jaisalmer': 'Jaisalmer', 'golden city': 'Jaisalmer',
            'pushkar': 'Pushkar',
            'mount abu': 'Mount Abu',
            'bikaner': 'Bikaner',
            'ajmer': 'Ajmer',
            'ranthambore': 'Ranthambore',
            'chittorgarh': 'Chittorgarh',
            
            # Himachal Pradesh (Hill Stations)
            'himachal pradesh': 'Himachal Pradesh', 'himachal': 'Himachal Pradesh',
            'shimla': 'Shimla',
            'manali': 'Manali',
            'dharamshala': 'Dharamshala', 'dharamsala': 'Dharamshala',
            'mcleod ganj': 'McLeod Ganj',
            'kasol': 'Kasol',
            'spiti': 'Spiti Valley',
            'kullu': 'Kullu',
            'dalhousie': 'Dalhousie',
            'kasauli': 'Kasauli',
            
            # Uttarakhand (Dev Bhoomi)
            'uttarakhand': 'Uttarakhand',
            'dehradun': 'Dehradun',
            'mussoorie': 'Mussoorie',
            'nainital': 'Nainital',
            'rishikesh': 'Rishikesh',
            'haridwar': 'Haridwar',
            'jim corbett': 'Jim Corbett',
            'auli': 'Auli',
            'kedarnath': 'Kedarnath',
            'badrinath': 'Badrinath',
            'valley of flowers': 'Valley of Flowers',
            
            # Goa (Beach Paradise)
            'goa': 'Goa',
            'panaji': 'Panaji', 'panjim': 'Panaji',
            'calangute': 'Calangute',
            'baga': 'Baga Beach',
            'anjuna': 'Anjuna',
            'arambol': 'Arambol',
            'palolem': 'Palolem',
            'old goa': 'Old Goa',
            'margao': 'Margao',
            
            # Tamil Nadu
            'tamil nadu': 'Tamil Nadu', 'tamilnadu': 'Tamil Nadu',
            'madurai': 'Madurai',
            'coimbatore': 'Coimbatore',
            'ooty': 'Ooty', 'ootacamund': 'Ooty',
            'kodaikanal': 'Kodaikanal',
            'rameswaram': 'Rameswaram',
            'kanyakumari': 'Kanyakumari', 'cape comorin': 'Kanyakumari',
            'pondicherry': 'Pondicherry', 'puducherry': 'Pondicherry',
            'mahabalipuram': 'Mahabalipuram', 'mamallapuram': 'Mahabalipuram',
            'thanjavur': 'Thanjavur', 'tanjore': 'Thanjavur',
            'tiruchirappalli': 'Tiruchirappalli', 'trichy': 'Tiruchirappalli',
            
            # Karnataka
            'karnataka': 'Karnataka',
            'mysore': 'Mysore', 'mysuru': 'Mysore',
            'hampi': 'Hampi',
            'coorg': 'Coorg', 'kodagu': 'Coorg',
            'chikmagalur': 'Chikmagalur',
            'mangalore': 'Mangalore', 'mangaluru': 'Mangalore',
            'udupi': 'Udupi',
            'badami': 'Badami',
            'belur': 'Belur',
            'halebidu': 'Halebidu',
            'gokarna': 'Gokarna',
            
            # Andhra Pradesh & Telangana
            'andhra pradesh': 'Andhra Pradesh',
            'telangana': 'Telangana',
            'vijayawada': 'Vijayawada',
            'visakhapatnam': 'Visakhapatnam', 'vizag': 'Visakhapatnam',
            'tirupati': 'Tirupati',
            'amaravati': 'Amaravati',
            'warangal': 'Warangal',
            
            # West Bengal
            'west bengal': 'West Bengal',
            'darjeeling': 'Darjeeling',
            'kalimpong': 'Kalimpong',
            'siliguri': 'Siliguri',
            'digha': 'Digha',
            'sundarbans': 'Sundarbans',
            'shantiniketan': 'Shantiniketan',
            
            # Gujarat
            'gujarat': 'Gujarat',
            'ahmedabad': 'Ahmedabad',
            'surat': 'Surat',
            'vadodara': 'Vadodara', 'baroda': 'Vadodara',
            'rajkot': 'Rajkot',
            'dwarka': 'Dwarka',
            'somnath': 'Somnath',
            'kutch': 'Kutch', 'kachchh': 'Kutch',
            'rann of kutch': 'Rann of Kutch',
            'gir': 'Gir National Park',
            
            # Maharashtra
            'maharashtra': 'Maharashtra',
            'nashik': 'Nashik',
            'aurangabad': 'Aurangabad',
            'lonavala': 'Lonavala',
            'mahabaleshwar': 'Mahabaleshwar',
            'ajanta': 'Ajanta Caves',
            'ellora': 'Ellora Caves',
            'shirdi': 'Shirdi',
            'nagpur': 'Nagpur',
            
            # Madhya Pradesh
            'madhya pradesh': 'Madhya Pradesh', 'mp': 'Madhya Pradesh',
            'bhopal': 'Bhopal',
            'indore': 'Indore',
            'gwalior': 'Gwalior',
            'khajuraho': 'Khajuraho',
            'ujjain': 'Ujjain',
            'jabalpur': 'Jabalpur',
            'sanchi': 'Sanchi',
            'pachmarhi': 'Pachmarhi',
            'kanha': 'Kanha National Park',
            'bandhavgarh': 'Bandhavgarh',
            
            # Uttar Pradesh
            'uttar pradesh': 'Uttar Pradesh', 'up': 'Uttar Pradesh',
            'lucknow': 'Lucknow',
            'agra': 'Agra',
            'varanasi': 'Varanasi', 'banaras': 'Varanasi', 'kashi': 'Varanasi',
            'allahabad': 'Prayagraj', 'prayagraj': 'Prayagraj',
            'mathura': 'Mathura',
            'vrindavan': 'Vrindavan',
            'ayodhya': 'Ayodhya',
            'kanpur': 'Kanpur',
            'meerut': 'Meerut',
            
            # Punjab & Haryana
            'punjab': 'Punjab',
            'chandigarh': 'Chandigarh',
            'amritsar': 'Amritsar',
            'ludhiana': 'Ludhiana',
            'patiala': 'Patiala',
            'haryana': 'Haryana',
            'gurgaon': 'Gurgaon', 'gurugram': 'Gurgaon',
            'faridabad': 'Faridabad',
            
            # Bihar & Jharkhand
            'bihar': 'Bihar',
            'patna': 'Patna',
            'gaya': 'Gaya',
            'bodh gaya': 'Bodh Gaya',
            'nalanda': 'Nalanda',
            'jharkhand': 'Jharkhand',
            'ranchi': 'Ranchi',
            'jamshedpur': 'Jamshedpur',
            'dhanbad': 'Dhanbad',
            
            # Odisha
            'odisha': 'Odisha', 'orissa': 'Odisha',
            'bhubaneswar': 'Bhubaneswar',
            'puri': 'Puri',
            'cuttack': 'Cuttack',
            'konark': 'Konark',
            'chilika': 'Chilika Lake',
            
            # Northeast States
            'assam': 'Assam',
            'guwahati': 'Guwahati',
            'kaziranga': 'Kaziranga',
            'majuli': 'Majuli',
            'meghalaya': 'Meghalaya',
            'shillong': 'Shillong',
            'cherrapunji': 'Cherrapunji',
            'manipur': 'Manipur',
            'imphal': 'Imphal',
            'nagaland': 'Nagaland',
            'kohima': 'Kohima',
            'tripura': 'Tripura',
            'agartala': 'Agartala',
            'mizoram': 'Mizoram',
            'aizawl': 'Aizawl',
            'arunachal pradesh': 'Arunachal Pradesh',
            'itanagar': 'Itanagar',
            'sikkim': 'Sikkim',
            'gangtok': 'Gangtok',
            
            # Jammu & Kashmir / Ladakh
            'jammu and kashmir': 'Jammu and Kashmir', 'j&k': 'Jammu and Kashmir',
            'srinagar': 'Srinagar',
            'jammu': 'Jammu',
            'gulmarg': 'Gulmarg',
            'pahalgam': 'Pahalgam',
            'sonamarg': 'Sonamarg',
            'ladakh': 'Ladakh',
            'leh': 'Leh',
            'kargil': 'Kargil',
            'nubra valley': 'Nubra Valley',
            'pangong tso': 'Pangong Tso',
            
            # Union Territories
            'andaman and nicobar': 'Andaman and Nicobar',
            'port blair': 'Port Blair',
            'havelock': 'Havelock Island',
            'neil island': 'Neil Island',
            'lakshadweep': 'Lakshadweep',
            'daman and diu': 'Daman and Diu',
            'dadra and nagar haveli': 'Dadra and Nagar Haveli',
            
            # Hindi Names
            'दिल्ली': 'Delhi', 'मुंबई': 'Mumbai', 'बंगलौर': 'Bangalore',
            'चेन्नई': 'Chennai', 'कोलकाता': 'Kolkata', 'हैदराबाद': 'Hyderabad',
            'जयपुर': 'Jaipur', 'आगरा': 'Agra', 'वाराणसी': 'Varanasi',
            'ऋषिकेश': 'Rishikesh', 'हरिद्वार': 'Haridwar', 'शिमला': 'Shimla',
            'मनाली': 'Manali', 'गोवा': 'Goa', 'केरल': 'Kerala',
            'राजस्थान': 'Rajasthan', 'हिमाचल प्रदेश': 'Himachal Pradesh',
            'उत्तराखंड': 'Uttarakhand', 'मध्य प्रदेश': 'Madhya Pradesh',
            'उत्तर प्रदेश': 'Uttar Pradesh', 'गुजरात': 'Gujarat',
            'महाराष्ट्र': 'Maharashtra', 'तमिलनाडु': 'Tamil Nadu',
            'कर्नाटक': 'Karnataka', 'आंध्र प्रदेश': 'Andhra Pradesh',
            'पश्चिम बंगाल': 'West Bengal', 'पंजाब': 'Punjab',
            'हरियाणा': 'Haryana', 'बिहार': 'Bihar',
            
            # Bengali Names
            'দিল্লি': 'Delhi', 'মুম্বাই': 'Mumbai', 'কলকাতা': 'Kolkata',
            'চেন্নাই': 'Chennai', 'ব্যাঙ্গালোর': 'Bangalore',
            'দার্জিলিং': 'Darjeeling', 'শান্তিনিকেতন': 'Shantiniketan',
            'সুন্দরবন': 'Sundarbans', 'কেরল': 'Kerala', 'কেরালা': 'Kerala',
            'গোয়া': 'Goa', 'রাজস্থান': 'Rajasthan',
            'পশ্চিমবঙ্গ': 'West Bengal', 'বিহার': 'Bihar',
            
            # Malayalam Names
            'കേരളം': 'Kerala', 'കൊച്ചി': 'Kochi', 'എറണാകുളം': 'Kochi',
            'ആലപ്പുഴ': 'Alleppey', 'മുന്നാർ': 'Munnar',
            'തിരുവനന്തപുരം': 'Thiruvananthapuram',
            'കോഴിക്കോട്': 'Kozhikode', 'കണ്ണൂർ': 'Kannur',
            'കൊല്ലം': 'Kollam', 'തൃശൂർ': 'Thrissur',
            'വയനാട്': 'Wayanad', 'ഇടുക്കി': 'Idukki',
            
            # Tamil Names
            'தமிழ்நாடு': 'Tamil Nadu', 'சென்னை': 'Chennai',
            'மதுரை': 'Madurai', 'கோயம்புத்தூர்': 'Coimbatore',
            'ஊட்டி': 'Ooty', 'கொடைக்கானல்': 'Kodaikanal',
            'ராமேஸ்வரம்': 'Rameswaram', 'கன்னியாகுமரி': 'Kanyakumari',
            'பாண்டிச்சேரி': 'Pondicherry', 'மகாபலிபுரம்': 'Mahabalipuram',
            
            # Telugu Names
            'తెలంగాణ': 'Telangana', 'ఆంధ్రప్రదేశ్': 'Andhra Pradesh',
            'హైదరాబాద్': 'Hyderabad', 'విజయవాడ': 'Vijayawada',
            'విశాఖపట్నం': 'Visakhapatnam', 'తిరుపతి': 'Tirupati',
            
            # Kannada Names
            'ಕರ್ನಾಟಕ': 'Karnataka', 'ಬೆಂಗಳೂರು': 'Bangalore',
            'ಮೈಸೂರು': 'Mysore', 'ಹಂಪಿ': 'Hampi',
            'ಕೂರ್ಗ್': 'Coorg', 'ಮಂಗಳೂರು': 'Mangalore',
            
            # Gujarati Names
            'ગુજરાત': 'Gujarat', 'અમદાવાદ': 'Ahmedabad',
            'સુરત': 'Surat', 'રાજકોટ': 'Rajkot',
            'વડોદરા': 'Vadodara', 'દ્વારકા': 'Dwarka'
        }
        
        # Enhanced location extraction patterns
        self.location_patterns = [
            r'\b(?:in|at|visiting|going to|traveling to|exploring|from|to)\s+([A-Za-z\u0900-\u097F\u0980-\u09FF\u0B00-\u0B7F\u0C00-\u0C7F\u0D00-\u0D7F\s]+?)(?:\s|$|[,.])',
            r'\b([A-Za-z\u0900-\u097F\u0980-\u09FF\u0B00-\u0B7F\u0C00-\u0C7F\u0D00-\u0D7F\s]+?)\s+(?:city|place|state|mein|में|তে|এ|లో|ನಲ್ಲಿ|ൽ)\b',
            r'\b(?:I\'m|I am|मैं|আমি|నేను|ನಾನು|ഞാൻ)\s+(?:in|at|में|এ|তে|లో|ನಲ್ಲಿ|ൽ)\s+([A-Za-z\u0900-\u097F\u0980-\u09FF\u0B00-\u0B7F\u0C00-\u0C7F\u0D00-\u0D7F\s]+?)(?:\s|$|[,.])',
            r'\b(?:want to|planning to|going to)\s+(?:visit|explore|see|go to)\s+([A-Za-z\u0900-\u097F\u0980-\u09FF\u0B00-\u0B7F\u0C00-\u0C7F\u0D00-\u0D7F\s]+?)(?:\s|$|[,.])'
        ]
    
    def extract_location(self, text: str) -> Optional[str]:
        """Extract location from user message with comprehensive coverage."""
        
        print(f"🔍 Extracting location from: '{text}'")
        
        # Method 1: Direct city/state matching (most reliable)
        direct_match = self._match_known_cities(text)
        if direct_match:
            print(f"✅ Direct match found: {direct_match}")
            return direct_match
        
        # Method 2: Pattern-based extraction
        pattern_matches = self._extract_by_patterns(text)
        for match in pattern_matches:
            validated = self._match_known_cities(match)
            if validated:
                print(f"✅ Pattern match found: {validated}")
                return validated
        
        # Method 3: Fuzzy matching for misspellings
        fuzzy_match = self._fuzzy_match(text)
        if fuzzy_match:
            print(f"✅ Fuzzy match found: {fuzzy_match}")
            return fuzzy_match
        
        print(f"❌ No location found in text")
        return None
    
    def _match_known_cities(self, text: str) -> Optional[str]:
        """Match against comprehensive Indian locations."""
        text_lower = text.lower().strip()
        
        # Direct exact match
        if text_lower in self.indian_cities:
            return self.indian_cities[text_lower]
        
        # Partial match within text
        for city_key, city_name in self.indian_cities.items():
            if len(city_key) > 3:  # Avoid false positives with short names
                if city_key in text_lower or city_name.lower() in text_lower:
                    return city_name
        
        return None
    
    def _extract_by_patterns(self, text: str) -> List[str]:
        """Extract potential locations using regex patterns."""
        matches = []
        
        for pattern in self.location_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            for match in found:
                location = match.strip()
                if 2 < len(location) < 50:  # Reasonable length
                    matches.append(location)
        
        return matches
    
    def _fuzzy_match(self, text: str) -> Optional[str]:
        """Fuzzy matching for common misspellings."""
        text_lower = text.lower()
        
        # Common misspellings and variations
        fuzzy_mappings = {
            'kerrala': 'Kerala', 'kerela': 'Kerala', 'karela': 'Kerala',
            'kochi': 'Kochi', 'cochin': 'Kochi',
            'munaar': 'Munnar', 'munar': 'Munnar',
            'allepey': 'Alleppey', 'alappuzha': 'Alleppey',
            'bangalor': 'Bangalore', 'bengaluru': 'Bangalore',
            'chenai': 'Chennai', 'madras': 'Chennai',
            'kolkatta': 'Kolkata', 'calcutta': 'Kolkata',
            'hydrabad': 'Hyderabad', 'haidarabad': 'Hyderabad',
            'rajsthan': 'Rajasthan', 'rajasthhan': 'Rajasthan',
            'himachal': 'Himachal Pradesh', 'hp': 'Himachal Pradesh',
            'uttrakhand': 'Uttarakhand', 'uttaranchal': 'Uttarakhand',
            'up': 'Uttar Pradesh', 'mp': 'Madhya Pradesh'
        }
        
        for misspelling, correct in fuzzy_mappings.items():
            if misspelling in text_lower:
                return correct
        
        return None
    
    def get_location_type(self, location: str) -> str:
        """Classify location type for better recommendations."""
        
        states = [
            'Kerala', 'Rajasthan', 'Himachal Pradesh', 'Uttarakhand', 'Goa',
            'Tamil Nadu', 'Karnataka', 'Maharashtra', 'Gujarat', 'West Bengal',
            'Madhya Pradesh', 'Uttar Pradesh', 'Punjab', 'Haryana', 'Bihar',
            'Odisha', 'Assam', 'Meghalaya', 'Sikkim', 'Jammu and Kashmir',
            'Ladakh', 'Andhra Pradesh', 'Telangana'
        ]
        
        hill_stations = [
            'Shimla', 'Manali', 'Dharamshala', 'Mussoorie', 'Nainital',
            'Ooty', 'Kodaikanal', 'Munnar', 'Darjeeling', 'Gangtok',
            'Mount Abu', 'Coorg', 'Chikmagalur'
        ]
        
        beaches = [
            'Goa', 'Kovalam', 'Varkala', 'Gokarna', 'Pondicherry',
            'Kanyakumari', 'Digha', 'Puri', 'Calangute', 'Baga Beach'
        ]
        
        heritage = [
            'Agra', 'Jaipur', 'Udaipur', 'Varanasi', 'Hampi', 'Khajuraho',
            'Ajanta Caves', 'Ellora Caves', 'Mahabalipuram', 'Konark'
        ]
        
        if location in states:
            return 'state'
        elif location in hill_stations:
            return 'hill_station'
        elif location in beaches:
            return 'beach'
        elif location in heritage:
            return 'heritage'
        else:
            return 'city'
    
    def get_nearby_attractions(self, location: str) -> List[str]:
        """Get nearby attractions for a location."""
        
        attraction_map = {
            'Kerala': ['Backwaters', 'Hill Stations', 'Beaches', 'Ayurveda Centers', 'Spice Plantations'],
            'Kochi': ['Fort Kochi', 'Chinese Fishing Nets', 'Mattancherry Palace', 'Jewish Synagogue'],
            'Alleppey': ['Backwater Cruises', 'Houseboat Stays', 'Kumarakom Bird Sanctuary'],
            'Munnar': ['Tea Plantations', 'Eravikulam National Park', 'Mattupetty Dam'],
            'Rajasthan': ['Desert Safari', 'Palaces', 'Forts', 'Camel Rides', 'Folk Music'],
            'Jaipur': ['Hawa Mahal', 'Amber Fort', 'City Palace', 'Jantar Mantar'],
            'Udaipur': ['Lake Pichola', 'City Palace', 'Jag Mandir', 'Saheliyon ki Bari'],
            'Goa': ['Beaches', 'Portuguese Churches', 'Spice Plantations', 'Night Markets'],
            'Himachal Pradesh': ['Hill Stations', 'Adventure Sports', 'Monasteries', 'Apple Orchards'],
            'Tamil Nadu': ['Temples', 'Hill Stations', 'Beaches', 'Classical Arts'],
            'Karnataka': ['Palace Architecture', 'Wildlife Sanctuaries', 'Coffee Plantations', 'Ancient Ruins']
        }
        
        return attraction_map.get(location, [])
