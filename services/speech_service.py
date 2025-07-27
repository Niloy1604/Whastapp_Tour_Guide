import asyncio
import tempfile
import os
import whisper
import speech_recognition as sr
from pydub import AudioSegment
from typing import Optional

class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        self.supported_languages = {
            'en': 'english', 'hi': 'hindi', 'bn': 'bengali',
            'ta': 'tamil', 'te': 'telugu', 'mr': 'marathi',
            'gu': 'gujarati', 'kn': 'kannada', 'ml': 'malayalam'
        }
    
    def load_whisper_model(self) -> Optional[whisper.Whisper]:
        """Load Whisper model for accurate transcription."""
        if self.whisper_model is None:
            try:
                self.whisper_model = whisper.load_model("base")
                print("✅ Whisper model loaded successfully")
            except Exception as e:
                print(f"❌ Whisper load error: {e}")
                self.whisper_model = None
        return self.whisper_model
    
    async def transcribe_audio(self, audio_data: bytes, language: str = 'auto') -> Optional[str]:
        """Advanced audio transcription with language detection."""
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name
        
        try:
            # Try Whisper first (most accurate for multilingual)
            result = await self._transcribe_with_whisper(tmp_file_path, language)
            if result and len(result.strip()) > 2:  # Valid transcription
                print(f"✅ Whisper transcription: {result}")
                return result
            
            # Fallback to Google Speech Recognition
            result = await self._transcribe_with_google(tmp_file_path, language)
            if result:
                print(f"✅ Google transcription: {result}")
                return result
                
            return None
            
        finally:
            # Cleanup
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    async def _transcribe_with_whisper(self, audio_path: str, language: str) -> Optional[str]:
        """Whisper transcription with language support."""
        try:
            model = self.load_whisper_model()
            if not model:
                return None
            
            # Map to Whisper language
            whisper_lang = self.supported_languages.get(language, 'english')
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.transcribe(
                    audio_path, 
                    language=whisper_lang,
                    task="transcribe"
                )
            )
            
            return result['text'].strip()
            
        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            return None
    
    async def _transcribe_with_google(self, audio_path: str, language: str) -> Optional[str]:
        """Google Speech Recognition fallback."""
        try:
            # Convert to proper format
            audio = AudioSegment.from_file(audio_path)
            wav_path = audio_path.replace('.wav', '_converted.wav')
            audio.export(wav_path, format='wav')
            
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                audio_data = self.recognizer.record(source)
            
            # Google language mapping
            google_languages = {
                'en': 'en-IN', 'hi': 'hi-IN', 'bn': 'bn-IN',
                'ta': 'ta-IN', 'te': 'te-IN', 'mr': 'mr-IN',
                'gu': 'gu-IN', 'kn': 'kn-IN', 'ml': 'ml-IN'
            }
            
            google_lang = google_languages.get(language, 'en-IN')
            
            text = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.recognizer.recognize_google(
                    audio_data, 
                    language=google_lang
                )
            )
            
            # Cleanup
            if os.path.exists(wav_path):
                os.unlink(wav_path)
            
            return text
            
        except Exception as e:
            print(f"❌ Google transcription error: {e}")
            return None
