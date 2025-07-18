from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests
from config import Config

class WhatsAppService:
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.from_number = Config.TWILIO_PHONE_NUMBER
    
    def send_message(self, to_number, message):
        """Send text message via WhatsApp"""
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return message_obj.sid
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def send_interactive_message(self, to_number, recommendations, language='en'):
        """Send interactive message with menu"""
        try:
            message_text = ""
            for rec in recommendations:
                message_text += f"{rec['full_text']}\n"
            
            menu_text = {
                'en': "\nReply 1/2/3 for more 📜",
                'hi': "\nऔर जानने के लिए 1/2/3 का जवाब दें 📜",
                'bn': "\nআরো জানতে 1/2/3 উত্তর দিন 📜"
            }
            
            message_text += menu_text.get(language, menu_text['en'])
            return self.send_message(to_number, message_text)
            
        except Exception as e:
            print(f"Error sending interactive message: {e}")
            return None
    
    def download_media(self, media_url):
        """Download media file from WhatsApp"""
        try:
            response = requests.get(media_url, auth=(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN))
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Error downloading media: {e}")
            return None
    
    def create_webhook_response(self, message_text):
        """Create TwiML response for webhook"""
        resp = MessagingResponse()
        resp.message(message_text)
        return str(resp)
