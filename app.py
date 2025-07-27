import os
import asyncio
import json
from flask import Flask, request, jsonify
from datetime import datetime
from typing import Optional, Dict, Any

# Import all services
from models.llm_agent import LocalGuideAgent
from models.language_detector import QuickLanguageDetector
from models.mood_analyzer import MoodAnalyzer
from utils.location_extractor import LocationExtractor
from services.whatsapp_service import WhatsAppService, TwilioTester
from services.speech_service import SpeechService
from services.tts_service import TTSService
from services.cache_service import CacheService
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


class VoiceFirstConversationBot:
    def __init__(self):
        # Load language data first
        self.language_data = self._load_language_data()
        self.supported_languages = list(self.language_data.get('supported_languages', {}).keys())

        # Initialize all services
        self.llm_agent = LocalGuideAgent()
        self.language_detector = QuickLanguageDetector()
        self.mood_analyzer = MoodAnalyzer()
        self.location_extractor = LocationExtractor()
        self.whatsapp_service = WhatsAppService()
        self.speech_service = SpeechService()
        self.tts_service = TTSService()
        self.cache_service = CacheService()

        # Load response templates
        self.response_templates = self._load_response_templates()

        print(f"✅ VoiceFirstConversationBot initialized with {len(self.supported_languages)} languages")
        print(f"🎯 Supported languages: {', '.join(self.supported_languages)}")

    def _load_language_data(self) -> Dict:
        """Load language data from languages.json."""
        try:
            with open('data/languages.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load languages.json: {e}")
            return {'supported_languages': {'en': {'name': 'English'}}}

    def _load_response_templates(self) -> Dict:
        """Load response templates from data/responses/ folder."""
        templates = {}

        for lang_code in self.supported_languages:
            try:
                template_file = f'data/responses/{lang_code}_responses.json'
                if os.path.exists(template_file):
                    with open(template_file, 'r', encoding='utf-8') as f:
                        templates[lang_code] = json.load(f)
                        print(f"✅ Loaded {lang_code} response templates")
            except Exception as e:
                print(f"⚠️ Failed to load {lang_code} templates: {e}")

        return templates

    async def process_message(self, user_id: str, message_body: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """Process user message - ALWAYS generative, voice-first when appropriate."""

        print(f"🎯 Processing message for {user_id}: '{message_body[:50]}...'")

        # Handle voice input first
        if media_url:
            print("🎤 Voice message detected - processing with STT")
            text_from_voice = await self._process_voice_message(media_url, {"user_id": user_id})
            if text_from_voice:
                message_body = text_from_voice
                print(f"🎤 STT Result: {message_body}")

        # Build comprehensive user context
        user_context = await self._build_user_context(user_id, message_body)
        print(f"🔍 User context: {user_context}")

        # Get conversation history
        conversation_history = self.cache_service.get_conversation(user_id)

        # **ALWAYS CALL LLM - NO FALLBACKS**
        llm_response = await self.llm_agent.get_response(
            user_message=message_body,
            conversation_history=conversation_history,
            user_context=user_context
        )

        # Determine if this should be voice-only response
        wants_voice = self._should_respond_with_voice(message_body, user_context)

        response_data = {
            "input": message_body,
            "response": llm_response,
            "timestamp": datetime.now().isoformat(),
            "user_context": user_context,
            "voice_response": wants_voice,
            "language_info": self._get_language_response_info(user_context.get('detected_language', 'en'))
        }

        # Generate voice response if requested
        if wants_voice:
            print("🔊 Generating voice response")
            audio_path = await self._generate_voice_response(llm_response, user_context)
            if audio_path:
                response_data["audio_url"] = audio_path

        # Update conversation history and cache
        self.cache_service.update_conversation(user_id, "user", message_body)
        self.cache_service.update_conversation(user_id, "assistant", llm_response)
        self.cache_service.cache_user_context(user_id, user_context)

        return response_data

    async def _build_user_context(self, user_id: str, message: str) -> Dict[str, Any]:
        """Build comprehensive user context for LLM."""

        cached_context = self.cache_service.get_user_context(user_id)
        detected_language, confidence = self.language_detector.detect_language(message)
        print(f"🌐 Language detection: {detected_language} (confidence: {confidence:.2f})")

        lang_support = self.validate_language_support(detected_language)
        if not lang_support['supported']:
            print(f"⚠️ Language {detected_language} not fully supported, falling back to English")
            detected_language = 'en'

        mood_analysis = self.mood_analyzer.analyze_mood(message, detected_language)
        print(f"😊 Mood analysis: {mood_analysis}")

        location = self.location_extractor.extract_location(message)
        if location:
            print(f"📍 Location extracted: {location}")

        wants_voice = self._should_respond_with_voice(message, cached_context)

        return {
            "user_id": user_id,
            "detected_language": detected_language,
            "language_confidence": confidence,
            "language_support": lang_support,
            "current_location": location or cached_context.get("current_location"),
            "mood": mood_analysis.get("mood", "curious"),
            "energy_level": mood_analysis.get("energy_level", "medium"),
            "emotional_state": mood_analysis.get("emotional_state", "neutral"),
            "wants_voice_response": wants_voice,
            "conversation_turns": cached_context.get("conversation_turns", 0) + 1,
            "last_topics": cached_context.get("last_topics", []),
            "cultural_context": self._get_cultural_context(detected_language, location)
        }

    def _get_cultural_context(self, language: str, location: Optional[str]) -> Dict:
        lang_info = self.language_data.get('supported_languages', {}).get(language, {})

        context = {
            'language_name': lang_info.get('name', 'English'),
            'native_name': lang_info.get('native_name', 'English'),
            'script': lang_info.get('script', 'Latin'),
            'region': lang_info.get('region', 'International'),
            'cultural_usage': lang_info.get('cultural_context', {})
        }

        if location:
            context['location_context'] = self._get_location_cultural_context(location)

        return context

    def _get_location_cultural_context(self, location: str) -> Dict:
        location_contexts = {
            'Delhi': {'heritage': 'Mughal', 'language_preference': 'hi', 'specialties': ['monuments', 'street_food']},
            'Mumbai': {'heritage': 'Colonial', 'language_preference': 'mr', 'specialties': ['bollywood', 'finance']},
            'Kerala': {'heritage': 'Coastal', 'language_preference': 'ml', 'specialties': ['backwaters', 'spices']},
            'Rajasthan': {'heritage': 'Royal', 'language_preference': 'hi', 'specialties': ['palaces', 'desert']},
            'Tamil Nadu': {'heritage': 'Dravidian', 'language_preference': 'ta', 'specialties': ['temples', 'classical_arts']}
        }

        return location_contexts.get(location, {'heritage': 'Diverse', 'specialties': ['culture', 'history']})

    def validate_language_support(self, lang_code: str) -> Dict:
        lang_info = self.language_data.get('supported_languages', {}).get(lang_code, {})

        return {
            'supported': bool(lang_info),
            'voice_available': lang_info.get('tts_supported', False) and lang_info.get('stt_supported', False),
            'name': lang_info.get('name', 'Unknown'),
            'native_name': lang_info.get('native_name', 'Unknown'),
            'script': lang_info.get('script', 'Unknown')
        }

    def _get_language_response_info(self, lang_code: str) -> Dict:
        lang_info = self.language_data.get('supported_languages', {}).get(lang_code, {})

        return {
            'code': lang_code,
            'name': lang_info.get('name', 'English'),
            'native_name': lang_info.get('native_name', 'English'),
            'script': lang_info.get('script', 'Latin'),
            'voice_supported': lang_info.get('tts_supported', False),
            'greeting': self.language_detector.get_greeting(lang_code, 'casual')
        }

    def _should_respond_with_voice(self, message: str, context: Dict) -> bool:
        voice_triggers = [
            "tell me a story", "story about", "कहानी सुनाओ", "গল্প বলুন",
            "கதை சொல்லுங்கள்", "కథ చెప్పండి", "കഥ പറയൂ", "voice", "audio",
            "sing", "recite", "narrate", "describe in detail", "सुनाओ", "বলুন"
        ]

        message_lower = message.lower()
        return any(trigger in message_lower for trigger in voice_triggers)

    async def _process_voice_message(self, media_url: str, context: dict) -> Optional[str]:
        try:
            audio_data = await self.whatsapp_service.download_media(media_url)
            if not audio_data:
                return None

            detected_lang = context.get("detected_language", "en")
            transcribed_text = await self.speech_service.transcribe_audio(audio_data, detected_lang)

            return transcribed_text
        except Exception as e:
            print(f"❌ Voice processing error: {e}")
            return None

    async def _generate_voice_response(self, text_response: str, user_context: Dict) -> Optional[str]:
        try:
            language = user_context.get("detected_language", "en")
            if not self.tts_service._is_tts_supported(language):
                print(f"⚠️ TTS not supported for {language}, using English")
                language = "en"

            audio_path = await self.tts_service.text_to_speech(text_response, language)
            return audio_path
        except Exception as e:
            print(f"❌ TTS generation error: {e}")
            return None


bot = VoiceFirstConversationBot()


@app.route('/webhook', methods=['POST'])
async def whatsapp_webhook():
    try:
        from_number = request.form.get('From', '').replace('whatsapp:', '')
        message_body = request.form.get('Body', '')
        media_url = request.form.get('MediaUrl0')  # Voice message URL

        if not from_number:
            return "OK", 200

        if not message_body and not media_url:
            cached_context = bot.cache_service.get_user_context(from_number)
            preferred_lang = cached_context.get('detected_language', 'en')
            greeting = bot.language_detector.get_greeting(preferred_lang, 'casual')
            await bot.whatsapp_service.send_message(f"whatsapp:{from_number}", greeting)
            return "OK", 200

        response_data = await bot.process_message(from_number, message_body or "", media_url)

        if response_data.get("voice_response") and response_data.get("audio_url"):
            await bot.whatsapp_service.send_audio_message(f"whatsapp:{from_number}", response_data["audio_url"])
        else:
            await bot.whatsapp_service.send_message(f"whatsapp:{from_number}", response_data["response"])

        return "OK", 200

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return "Error", 500


@app.route('/test', methods=['POST'])
async def test_endpoint():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')

        if not user_id or not message:
            return jsonify({"error": "Missing user_id or message"}), 400

        response_data = await bot.process_message(user_id, message)
        return jsonify(response_data)

    except Exception as e:
        print(f"❌ Test endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/languages', methods=['GET'])
def get_supported_languages():
    return jsonify({
        "supported_languages": bot.supported_languages,
        "language_details": bot.language_data.get('supported_languages', {}),
        "total_count": len(bot.supported_languages),
        "voice_enabled": [lang for lang in bot.supported_languages if bot.validate_language_support(lang)['voice_available']]
    })


@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "llm_provider": bot.llm_agent.working_provider,
        "voice_enabled": True,
        "total_languages": len(bot.supported_languages),
        "supported_languages": bot.supported_languages,
        "services": {
            "llm_agent": bool(bot.llm_agent.working_provider),
            "language_detector": True,
            "tts_service": len(bot.tts_service.get_supported_languages()),
            "redis": bool(bot.cache_service.redis_client),
            "whisper": True
        },
        "features": {
            "voice_first_storytelling": True,
            "dynamic_llm_responses": True,
            "enhanced_multilingual": True,
            "session_persistence": True,
            "mood_aware_recommendations": True,
            "location_intelligence": True,
            "cultural_context_awareness": True,
            "proxy_bypass": True
        }
    })


@app.route('/test-twilio-setup', methods=['GET'])
async def test_twilio_setup():
    tester = TwilioTester(bot.whatsapp_service)
    results = await tester.test_connection()
    return jsonify(results)


@app.route('/send-test-message/<phone>', methods=['GET'])
async def send_test_message(phone):
    tester = TwilioTester(bot.whatsapp_service)
    success = await tester.send_test_message(f"+{phone}")

    if success:
        return jsonify({"status": "success", "message": f"Test message sent to +{phone}"})
    else:
        return jsonify({"status": "failed", "message": "Failed to send test message"})


if __name__ == '__main__':
    try:
        Config.validate_config()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)

    app.run(debug=True, host='0.0.0.0', port=5000)
