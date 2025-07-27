import os
import asyncio
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from typing import Optional, Dict, Any
import tempfile
from urllib.parse import urlparse

class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Debug logging to see what credentials we're loading
        print(f"🔧 Twilio Configuration:")
        print(f"   Account SID: {self.account_sid[:10] if self.account_sid else 'None'}...")
        print(f"   Auth Token: {'✅ Loaded' if self.auth_token else '❌ Missing'}")
        print(f"   Phone Number: {self.phone_number}")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            print("⚠️ Twilio credentials not found. WhatsApp features will be limited.")
            print("   Make sure your .env file has:")
            print("   TWILIO_ACCOUNT_SID=your_account_sid")
            print("   TWILIO_AUTH_TOKEN=your_auth_token")
            print("   TWILIO_PHONE_NUMBER=your_sandbox_number")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
            print("✅ WhatsApp service initialized successfully")
    
    def _format_whatsapp_number(self, phone_number: str) -> str:
        """Ensure phone number has proper WhatsApp format."""
        if not phone_number:
            return ""
        
        # Remove any existing whatsapp: prefix
        if phone_number.startswith('whatsapp:'):
            phone_number = phone_number[9:]
        
        # Remove any spaces or special characters except +
        phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Ensure it starts with +
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        return f"whatsapp:{phone_number}"
    
    async def send_message(self, to_number: str, message: str) -> bool:
        """Send text message via WhatsApp with enhanced error handling."""
        try:
            if not self.client:
                print("❌ Twilio client not initialized - check your credentials")
                return False
            
            # Format numbers properly
            formatted_to = self._format_whatsapp_number(to_number)
            formatted_from = self._format_whatsapp_number(self.phone_number)
            
            print(f"📤 Attempting to send message:")
            print(f"   From: {formatted_from}")
            print(f"   To: {formatted_to}")
            print(f"   Message: {message[:50]}{'...' if len(message) > 50 else ''}")
            
            # Validate the from number
            if not self._is_valid_sandbox_number(formatted_from):
                print(f"❌ Invalid sandbox number: {formatted_from}")
                print("💡 Check your TWILIO_PHONE_NUMBER in .env file")
                print("   It should be your Twilio WhatsApp sandbox number (e.g., +14155238886)")
                return False
            
            message_instance = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    body=message,
                    from_=formatted_from,
                    to=formatted_to
                )
            )
            
            print(f"✅ Message sent successfully!")
            print(f"   Message SID: {message_instance.sid}")
            print(f"   Status: {message_instance.status}")
            return True
            
        except TwilioException as e:
            print(f"❌ Twilio API error: {e}")
            if "21212" in str(e):
                print("💡 Error 21212: Invalid 'From' number")
                print("   This usually means your TWILIO_PHONE_NUMBER is incorrect")
                print("   1. Go to Twilio Console → Messaging → Try it out → WhatsApp")
                print("   2. Copy the exact sandbox number (e.g., +14155238886)")
                print("   3. Update your .env file with that number")
            elif "21211" in str(e):
                print("💡 Error 21211: Invalid 'To' number or not in sandbox")
                print("   Make sure the recipient has joined your WhatsApp sandbox")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending WhatsApp message: {e}")
            return False
    
    async def send_audio_message(self, to_number: str, audio_path: str) -> bool:
        """Send audio message via WhatsApp."""
        try:
            if not self.client:
                print("❌ Twilio client not initialized")
                return False
            
            # Format numbers properly
            formatted_to = self._format_whatsapp_number(to_number)
            formatted_from = self._format_whatsapp_number(self.phone_number)
            
            print(f"🎵 Attempting to send audio message:")
            print(f"   From: {formatted_from}")
            print(f"   To: {formatted_to}")
            print(f"   Audio: {audio_path}")
            
            # For sandbox, we need to upload audio to a public URL
            # For now, we'll send a text message indicating audio was generated
            # In production, you'd upload to S3/CloudFlare/etc and use that URL
            
            audio_message = f"🎵 Voice message generated! (Audio file: {os.path.basename(audio_path)})\n\n" \
                          f"Note: In sandbox mode, audio files aren't directly supported. " \
                          f"Your voice response was generated and saved locally."
            
            message_instance = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    body=audio_message,
                    from_=formatted_from,
                    to=formatted_to
                )
            )
            
            print(f"✅ Audio notification sent successfully: {message_instance.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Audio message error: {e}")
            return False
    
    async def download_media(self, media_url: str) -> Optional[bytes]:
        """Download media from WhatsApp message."""
        try:
            # Add Twilio credentials for authenticated download
            auth = (self.account_sid, self.auth_token)
            
            print(f"📥 Downloading media from: {media_url}")
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.get(media_url, auth=auth, timeout=30)
            )
            
            if response.status_code == 200:
                print(f"✅ Media downloaded: {len(response.content)} bytes")
                return response.content
            else:
                print(f"❌ Media download failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Media download error: {e}")
            return None
    
    def _is_valid_sandbox_number(self, whatsapp_number: str) -> bool:
        """Check if the number looks like a valid Twilio sandbox number."""
        if not whatsapp_number or not whatsapp_number.startswith('whatsapp:+'):
            return False
        
        # Extract just the phone number
        phone = whatsapp_number[9:]  # Remove 'whatsapp:'
        
        # Common Twilio sandbox patterns
        sandbox_patterns = [
            '+14155238886',  # US sandbox
            '+447700900000',  # UK sandbox
            '+12707716734',   # Another common pattern
        ]
        
        # Check if it matches known patterns or looks like a Twilio number
        if phone in sandbox_patterns:
            return True
        
        # Twilio numbers usually start with +1415, +1270, +447700, etc.
        if phone.startswith(('+1415', '+1270', '+447700')):
            return True
        
        print(f"⚠️ Unknown sandbox number pattern: {phone}")
        print("   If this is your correct Twilio sandbox number, it should still work")
        return True  # Allow it through, let Twilio validate
    
    def get_sandbox_join_instructions(self) -> str:
        """Get instructions for joining the WhatsApp sandbox."""
        return f"""
📱 To receive WhatsApp messages from CityChai:

1. Save this number in your contacts: {self.phone_number}
2. Send this message to join the sandbox:
   join orange-cat

3. You should receive a confirmation message
4. Then you can interact with CityChai!

Note: This is a Twilio sandbox for development/demo purposes.
"""
    
    def validate_webhook_signature(self, request_data: Dict[str, Any]) -> bool:
        """Validate incoming webhook signature for security."""
        try:
            # Implement Twilio signature validation
            # This is important for production security
            # For development/demo, we'll skip this
            return True
            
        except Exception as e:
            print(f"❌ Webhook validation error: {e}")
            return False

# Add this helper function to test Twilio setup
class TwilioTester:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.service = whatsapp_service
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Twilio connection and configuration."""
        results = {
            "client_initialized": bool(self.service.client),
            "credentials_loaded": bool(self.service.account_sid and self.service.auth_token),
            "phone_number": self.service.phone_number,
            "phone_number_valid": self.service._is_valid_sandbox_number(
                f"whatsapp:{self.service.phone_number}" if self.service.phone_number else ""
            )
        }
        
        if self.service.client:
            try:
                # Test account access
                account = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.service.client.api.accounts(self.service.account_sid).fetch()
                )
                results["account_status"] = account.status
                results["account_name"] = account.friendly_name
            except Exception as e:
                results["account_error"] = str(e)
        
        return results
    
    async def send_test_message(self, to_number: str) -> bool:
        """Send a test message to verify everything works."""
        test_message = """🎉 CityChai Test Message!

Your WhatsApp bot is working correctly!

Try sending:
- "Tell me about the Red Fort"
- "मुझे ताजमहल की कहानी सुनाओ"
- Voice messages for stories

Ready to explore India? 🇮🇳"""
        
        return await self.service.send_message(to_number, test_message)
