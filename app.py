from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging

# Import our modules
from config import Config
from utils.session_manager import SessionManager
from utils.helpers import MessageHelper, ValidationHelper
from models.language_detector import LanguageDetector
from models.mood_detector import MoodDetector
from models.story_generator import StoryGenerator
from services.whatsapp_service import WhatsAppService
from services.speech_service import SpeechService
from services.cache_service import CacheService

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
session_manager = SessionManager()
language_detector = LanguageDetector()
mood_detector = MoodDetector()
story_generator = StoryGenerator()
whatsapp_service = WhatsAppService()
speech_service = SpeechService()
cache_service = CacheService()

class CityChatBot:
    def __init__(self):
        self.session_manager = session_manager
        self.language_detector = language_detector
        self.mood_detector = mood_detector
        self.story_generator = story_generator
        self.whatsapp_service = whatsapp_service
        self.speech_service = speech_service
        self.cache_service = cache_service
        
        # Load cultural content
        self.load_cultural_content()
    
    def load_cultural_content(self):
        """Load cultural content data"""
        try:
            with open('data/cultural_content.json', 'r', encoding='utf-8') as f:
                self.cultural_content = json.load(f)
        except FileNotFoundError:
            logger.warning("Cultural content file not found, using defaults")
            self.cultural_content = {}
    
    def process_message(self, user_id, message_body=None, media_url=None):
        """Process incoming message"""
        try:
            # Get user session
            session = self.session_manager.get_session(user_id)
            
            # Process voice message
            if media_url:
                return self.process_voice_message(user_id, media_url, session)
            
            # Process text message
            if message_body:
                return self.process_text_message(user_id, message_body, session)
            
            return self.get_error_response(session['language'])
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self.get_error_response('en')
    
    def process_voice_message(self, user_id, media_url, session):
        """Process voice message"""
        try:
            # Download audio
            audio_data = self.whatsapp_service.download_media(media_url)
            if not audio_data:
                return self.get_error_response(session['language'])
            
            # Transcribe audio
            transcription = self.speech_service.transcribe_audio(audio_data, session['language'])
            if not transcription:
                return self.get_error_response(session['language'])
            
            # Extract audio features for mood detection
            audio_features = self.speech_service.extract_audio_features(audio_data)
            
            # Process as text message
            return self.process_text_message(user_id, transcription, session, audio_features)
            
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            return self.get_error_response(session['language'])
    
    def process_text_message(self, user_id, message_body, session, audio_features=None):
        """Process text message"""
        try:
            # Clean message
            message_body = MessageHelper.clean_text(message_body)
            
            # Check if it's a menu selection
            if session['conversation_stage'] == 'menu_displayed':
                return self.handle_menu_selection(user_id, message_body, session)
            
            # Detect language
            language = self.language_detector.detect_language(message_body)
            
            # Detect mood
            mood = self.mood_detector.detect_mood(message_body, language)
            if audio_features:
                voice_mood = self.mood_detector.detect_from_voice_features(audio_features)
                # Combine text and voice mood
                mood = voice_mood if voice_mood != 'curious' else mood
            
            # Extract city
            city = MessageHelper.extract_city_from_text(message_body)
            
            # Handle greeting
            if MessageHelper.is_greeting(message_body):
                return self.handle_greeting(user_id, language)
            
            # Check if city is found
            if not city:
                return self.handle_no_city(user_id, language)
            
            # Update session
            self.session_manager.update_session(user_id, {
                'language': language,
                'mood': mood,
                'current_city': city,
                'conversation_stage': 'processing',
                'message_count': session['message_count'] + 1
            })
            
            # Generate recommendations
            return self.generate_recommendations(user_id, city, mood, language)
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            return self.get_error_response(session['language'])
    
    def handle_greeting(self, user_id, language):
        """Handle greeting message"""
        greetings = {
            'en': "Hello! I'm CityChai, your AI city guide 🇮🇳\n\nTell me which city you're exploring and I'll share amazing local stories!\n\nExample: 'I'm in Delhi and feeling curious about history'",
            'hi': "नमस्ते! मैं CityChai हूँ, आपका AI शहर गाइड 🇮🇳\n\nबताएं कि आप कौन से शहर की खोज कर रहे हैं और मैं आपको शानदार स्थानीय कहानियां बताऊंगा!\n\nउदाहरण: 'मैं दिल्ली में हूँ और इतिहास के बारे में जिज्ञासु हूँ'",
            'bn': "নমস্কার! আমি CityChai, আপনার AI শহর গাইড 🇮🇳\n\nবলুন আপনি কোন শহর অন্বেষণ করছেন এবং আমি আপনাকে অসাধারণ স্থানীয় গল্প বলব!\n\nউদাহরণ: 'আমি দিল্লিতে আছি এবং ইতিহাস সম্পর্কে কৌতূহলী'"
        }
        
        # Update session
        self.session_manager.update_session(user_id, {
            'language': language,
            'conversation_stage': 'greeting_sent'
        })
        
        return greetings.get(language, greetings['en'])
    
    def handle_no_city(self, user_id, language):
        """Handle when city is not found"""
        return MessageHelper.get_error_message(language, 'city_not_found')
    
    def generate_recommendations(self, user_id, city, mood, language):
        """Generate recommendations for city, mood, and language"""
        try:
            # Check cache first
            cached_recommendations = self.cache_service.get_cached_recommendations(city, mood, language)
            if cached_recommendations:
                recommendations = cached_recommendations['recommendations']
            else:
                # Generate new recommendations
                recommendations = self.story_generator.generate_recommendations(city, mood, language)
                
                # Cache the recommendations
                self.cache_service.cache_recommendations(city, mood, language, recommendations)
            
            if not recommendations:
                return self.get_error_response(language)
            
            # Update session with recommendations
            self.session_manager.update_session(user_id, {
                'last_recommendations': recommendations,
                'conversation_stage': 'menu_displayed'
            })
            
            # Format response
            response = self.format_recommendations_response(recommendations, language)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self.get_error_response(language)
    
    def format_recommendations_response(self, recommendations, language):
        """Format recommendations as response"""
        response = ""
        
        for rec in recommendations:
            response += f"{rec['full_text']}\n"
        
        menu_text = {
            'en': "\nReply 1/2/3 for more 📜",
            'hi': "\nऔर जानने के लिए 1/2/3 का जवाब दें 📜",
            'bn': "\nআরো জানতে 1/2/3 উত্তর দিন 📜"
        }
        
        response += menu_text.get(language, menu_text['en'])
        
        return response
    
    def handle_menu_selection(self, user_id, message_body, session):
        """Handle menu selection"""
        try:
            # Extract selection number
            selection = MessageHelper.extract_selection_number(message_body)
            
            if not selection or selection < 1 or selection > 3:
                return MessageHelper.get_error_message(session['language'], 'invalid_selection')
            
            # Get selected recommendation
            if len(session['last_recommendations']) < selection:
                return MessageHelper.get_error_message(session['language'], 'invalid_selection')
            
            selected_rec = session['last_recommendations'][selection - 1]
            
            # Generate detailed story
            detailed_story = self.story_generator.generate_detailed_story(selected_rec, session['language'])
            
            # Update session
            self.session_manager.update_session(user_id, {
                'conversation_stage': 'story_detailed',
                'last_selected': selected_rec
            })
            
            # Format response with next actions
            next_actions = self.get_next_actions(session['language'])
            response = f"{detailed_story}\n\n{next_actions}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling menu selection: {e}")
            return MessageHelper.get_error_message(session['language'])
    
    def get_next_actions(self, language):
        """Get next action options"""
        next_actions = {
            'en': "What next?\n🗺️ Type 'more' for other places\n🏠 Type 'new' for different city",
            'hi': "आगे क्या?\n🗺️ अन्य स्थानों के लिए 'more' टाइप करें\n🏠 दूसरे शहर के लिए 'new' टाइप करें",
            'bn': "পরবর্তী কি?\n🗺️ অন্য স্থানের জন্য 'more' টাইপ করুন\n🏠 ভিন্ন শহরের জন্য 'new' টাইপ করুন"
        }
        
        return next_actions.get(language, next_actions['en'])
    
    def get_error_response(self, language):
        """Get error response"""
        return MessageHelper.get_error_message(language, 'general')

# Initialize bot
city_bot = CityChatBot()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Get form data
        message_data = request.form.to_dict()
        
        # Extract relevant information
        user_id = message_data.get('From', '')
        message_body = message_data.get('Body', '')
        media_url = message_data.get('MediaUrl0', '')
        
        # Validate phone number
        if not ValidationHelper.validate_phone_number(user_id):
            logger.warning(f"Invalid phone number: {user_id}")
            return jsonify({'error': 'Invalid phone number'}), 400
        
        # Process message
        if media_url:
            # Voice message
            response_text = city_bot.process_message(user_id, media_url=media_url)
        else:
            # Text message
            response_text = city_bot.process_message(user_id, message_body=message_body)
        
        # Send response
        message_sid = whatsapp_service.send_message(user_id, response_text)
        
        # Return TwiML response
        return whatsapp_service.create_webhook_response(response_text)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': session_manager.get_active_sessions(),
        'cache_stats': cache_service.get_cache_stats()
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        stats = {
            'active_sessions': session_manager.get_active_sessions(),
            'cache_stats': cache_service.get_cache_stats(),
            'uptime': datetime.now().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': 'Unable to get stats'}), 500

if __name__ == '__main__':
    # Run app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
