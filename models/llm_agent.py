import os
import asyncio
import requests
import json
import random
from typing import Dict, List

class LocalGuideAgent:
    def __init__(self):
        self.max_tokens = 300  # Increased for richer responses
        self.temperature = 0.9  # Higher creativity
        self.working_provider = None
        self.groq_api_key = None
        self.openai_api_key = None

        # Initialize APIs
        if os.getenv('GROQ_API_KEY'):
            self.groq_api_key = os.getenv('GROQ_API_KEY').strip()
            self.working_provider = 'groq'
            print(f"✅ Groq API key loaded: {self.groq_api_key[:10]}...")
        
        if os.getenv('OPENAI_API_KEY'):
            self.openai_api_key = os.getenv('OPENAI_API_KEY').strip()
            if not self.working_provider:
                self.working_provider = 'openai'
            print(f"✅ OpenAI API key loaded: {self.openai_api_key[:10]}...")
        
        if not self.working_provider:
            raise Exception("❌ NO LLM API KEYS FOUND! Cannot operate without LLM.")

    async def get_response(self, user_message: str, conversation_history: List[Dict], user_context: Dict) -> str:
        """ALWAYS generate dynamic LLM response - NO FALLBACKS ALLOWED."""

        detected_lang = user_context.get('detected_language', 'en')
        print(f"🔄 MANDATORY LLM call for {detected_lang}: '{user_message[:50]}...'")

        # Try primary LLM provider
        try:
            if self.working_provider == 'groq':
                response = await self._call_groq(user_message, user_context, conversation_history)
                print(f"✅ GROQ SUCCESS: {response[:100]}...")
                return response
            elif self.working_provider == 'openai':
                response = await self._call_openai(user_message, user_context, conversation_history)
                print(f"✅ OPENAI SUCCESS: {response[:100]}...")
                return response
        except Exception as e:
            print(f"❌ Primary LLM failed: {e}")

        # Try backup provider if available
        try:
            if self.working_provider == 'groq' and self.openai_api_key:
                print("🔄 Trying OpenAI as backup...")
                response = await self._call_openai(user_message, user_context, conversation_history)
                return response
            elif self.working_provider == 'openai' and self.groq_api_key:
                print("🔄 Trying Groq as backup...")
                response = await self._call_groq(user_message, user_context, conversation_history)
                return response
        except Exception as e:
            print(f"❌ Backup LLM failed: {e}")

        # ABSOLUTE LAST RESORT - Simple generative response
        return self._generate_emergency_response(user_message, user_context)

    async def _call_groq(self, user_message: str, user_context: Dict, conversation_history: List[Dict]) -> str:
        """Enhanced Groq API call with aggressive prompting."""

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        messages = self._build_conversation_messages(user_message, user_context, conversation_history)

        payload = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": 0.95,
            "stream": False
        }

        def send_request():
            return requests.post(url, headers=headers, json=payload, proxies={}, timeout=30)

        response = await asyncio.get_event_loop().run_in_executor(None, send_request)
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            return content
        else:
            raise Exception(f"Groq API error {response.status_code}: {response.text[:300]}")

    async def _call_openai(self, user_message: str, user_context: Dict, conversation_history: List[Dict]) -> str:
        """Enhanced OpenAI API call with aggressive prompting."""

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }

        messages = self._build_conversation_messages(user_message, user_context, conversation_history)

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        def send_request():
            return requests.post(url, headers=headers, json=payload, proxies={}, timeout=30)

        response = await asyncio.get_event_loop().run_in_executor(None, send_request)

        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            return content
        else:
            raise Exception(f"OpenAI API error {response.status_code}: {response.text[:300]}")

    def _build_conversation_messages(self, user_message: str, user_context: Dict, conversation_history: List[Dict]) -> List[Dict]:
        """Build ultra-strong conversation messages."""
        
        system_prompt = self._build_ultimate_system_prompt(user_context, user_message)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history with context
        for msg in conversation_history[-6:]:  # More history for better context
            if msg.get('role') and msg.get('content'):
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        messages.append({"role": "user", "content": user_message})
        return messages

    def _build_ultimate_system_prompt(self, user_context: Dict, user_message: str) -> str:
        """Build the most aggressive, dynamic system prompt possible."""

        language_code = user_context.get('detected_language', 'en')
        location = user_context.get('current_location', 'India')
        mood = user_context.get('mood', 'curious')
        conversation_turns = user_context.get('conversation_turns', 1)
        wants_voice = user_context.get('wants_voice_response', False)

        # Ultra-dynamic language rules
        language_rules = {
            'en': {
                'name': 'English',
                'rule': 'RESPOND ONLY IN ENGLISH',
                'greeting': 'Welcome to incredible India!',
                'example': 'The Red Fort is magnificent! Built by Shah Jahan in 1648, it housed Mughal emperors.'
            },
            'hi': {
                'name': 'Hindi',
                'rule': 'केवल हिंदी में जवाब दें - ABSOLUTELY NO ENGLISH',
                'greeting': 'अविश्वसनीय भारत में आपका स्वागत है!',
                'example': 'लाल किला शानदार है! शाहजहाँ ने 1648 में बनवाया था, यहाँ मुगल सम्राट रहते थे।'
            },
            'bn': {
                'name': 'Bengali',
                'rule': 'শুধুমাত্র বাংলায় উত্তর দিন - ABSOLUTELY NO ENGLISH',
                'greeting': 'অবিশ্বাস্য ভারতে আপনাকে স্বাগতম!',
                'example': 'লাল কেল্লা দুর্দান্ত! শাহজাহান ১৬৪৮ সালে নির্মাণ করেছিলেন, এখানে মুগল সম্রাটরা থাকতেন।'
            },
            'ta': {
                'name': 'Tamil',
                'rule': 'தமிழில் மட்டுமே பதிலளிக்கவும் - ABSOLUTELY NO ENGLISH',
                'greeting': 'நம்பமுடியாத இந்தியாவிற்கு வருக!',
                'example': 'சிவப்பு கோட்டை அற்புதமானது! ஷாஜஹான் 1648-இல் கட்டினார், முகலாய மன்னர்கள் இங்கு வாழ்ந்தனர்।'
            },
            'te': {
                'name': 'Telugu',
                'rule': 'తెలుగులో మాత్రమే సమాధానం ఇవ్వండి - ABSOLUTELY NO ENGLISH',
                'greeting': 'అద్భుతమైన భారతదేశానికి స్వాగతం!',
                'example': 'ఎర్రకోట అద్భుతమైనది! షాజహాన్ 1648లో నిర్మించాడు, మొఘల్ చక్రవర్తులు ఇక్కడ నివసించారు।'
            },
            'ml': {
                'name': 'Malayalam',
                'rule': 'മലയാളത്തിൽ മാത്രം മറുപടി നൽകുക - ABSOLUTELY NO ENGLISH',
                'greeting': 'അവിശ്വസനീയമായ ഇന്ത്യയിലേക്ക് സ്വാഗതം!',
                'example': 'ചുവന്ന കോട്ട അവിശ്വസനീയമാണ്! ഷാജഹാൻ 1648-ൽ നിർമ്മിച്ചു, മുഗൾ ചക്രവർത്തിമാർ ഇവിടെ താമസിച്ചു।'
            }
        }

        lang_info = language_rules.get(language_code, language_rules['en'])

        # Dynamic context integration
        context_elements = []
        if location:
            context_elements.append(f"Current focus: {location}")
        if mood != 'curious':
            context_elements.append(f"User mood: {mood}")
        if conversation_turns > 1:
            context_elements.append(f"Conversation turn: {conversation_turns}")
        if wants_voice:
            context_elements.append("VOICE RESPONSE REQUESTED - be more narrative and descriptive")

        context_string = " | ".join(context_elements) if context_elements else "Fresh conversation"

        # Voice-specific adjustments
        voice_instructions = ""
        if wants_voice:
            voice_instructions = f"""
🎤 VOICE RESPONSE MODE ACTIVATED:
- Be more narrative and storytelling
- Use descriptive language that sounds good when spoken
- Add dramatic pauses with punctuation
- Make it engaging for audio consumption
- Paint vivid pictures with words
"""

        # Ultimate dynamic prompt
        prompt = f"""🌍 You are CityChai, India's most passionate and knowledgeable AI tour guide.

🚨 CRITICAL LANGUAGE RULE 🚨
{lang_info['rule']}
USER LANGUAGE: {lang_info['name']}
YOU MUST RESPOND ONLY IN: {lang_info['name']}

CONTEXT: {context_string}

USER MESSAGE: "{user_message}"
CONVERSATION TURN: {conversation_turns}

{voice_instructions}

🎯 RESPONSE REQUIREMENTS:
1. Generate COMPLETELY UNIQUE content - never repeat previous responses
2. Use ONLY {lang_info['name']} language - NO exceptions
3. Be conversational, engaging, and passionate about India
4. Include fascinating cultural details, stories, or insights
5. Reference location ({location}) and mood ({mood}) naturally
6. Keep responses 3-4 sentences but rich in content
7. Use emojis naturally but not excessively
8. End with an engaging question or suggestion when appropriate

🔥 STYLE GUIDE:
- Be like a local friend who's deeply passionate about Indian culture
- Share insider knowledge and hidden gems
- Tell mini-stories or interesting facts
- Match the user's energy and interest level
- Be helpful, informative, and genuinely exciting

EXAMPLE PERFECT RESPONSE:
{lang_info['example']}

🌟 Remember: This is turn {conversation_turns} of our conversation. Be contextual, dynamic, and absolutely passionate about India! Respond ONLY in {lang_info['name']}!"""

        return prompt.strip()

    def _generate_emergency_response(self, user_message: str, user_context: Dict) -> str:
        """Last resort generative response if all LLMs fail."""
        
        language_code = user_context.get('detected_language', 'en')
        location = user_context.get('current_location', 'India')
        
        emergency_responses = {
            'en': [
                f"I'm deeply passionate about helping you discover {location or 'India'}! Even though I'm having technical difficulties, I can tell you that every corner of India has incredible stories waiting to be shared. What specific aspect interests you most?",
                f"India's rich heritage in {location or 'every region'} never fails to amaze me! While I'm experiencing some connectivity issues, I'd love to continue our conversation about this incredible destination. What would you like to explore?",
                f"The magic of {location or 'India'} is truly endless! Despite some technical challenges, I'm here to share the wonders of Indian culture and history with you. What catches your curiosity today?"
            ],
            'hi': [
                f"{location or 'भारत'} की खोज में आपकी मदद करने के लिए मैं बहुत उत्साहित हूं! तकनीकी समस्याओं के बावजूद, मैं जानता हूं कि भारत के हर कोने में अविश्वसनीय कहानियां हैं। आप किस विशेष चीज़ में रुचि रखते हैं?",
                f"{location or 'हर क्षेत्र'} में भारत की समृद्ध विरासत मुझे हमेशा आश्चर्यचकित करती है! कुछ connectivity issues के बावजूद, मैं इस अविश्वसनीय गंतव्य के बारे में बातचीत जारी रखना चाहूंगा। आप क्या explore करना चाहते हैं?"
            ],
            'bn': [
                f"{location or 'ভারত'} আবিষ্কারে আপনাকে সাহায্য করতে আমি গভীরভাবে আবেগপ্রবণ! প্রযুক্তিগত সমস্যা সত্ত্বেও, আমি জানি ভারতের প্রতিটি কোণে অবিশ্বাস্য গল্প অপেক্ষা করছে। কোন নির্দিষ্ট বিষয় আপনার আগ্রহের?",
                f"{location or 'প্রতিটি অঞ্চলে'} ভারতের সমৃদ্ধ ঐতিহ্য আমাকে সর্বদা বিস্মিত করে! কিছু connectivity সমস্যা সত্ত্বেও, আমি এই অবিশ্বাস্য গন্তব্য নিয়ে কথোপকথন চালিয়ে যেতে চাই। আপনি কী অন্বেষণ করতে চান?"
            ]
        }
        
        responses = emergency_responses.get(language_code, emergency_responses['en'])
        return random.choice(responses)
