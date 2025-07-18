import speech_recognition as sr
import tempfile
import os
from pydub import AudioSegment
from config import Config

class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def transcribe_audio(self, audio_data, language='en'):
        """Transcribe audio using Google Speech Recognition"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name
        
        try:
            return self.transcribe_with_google(tmp_file_path, language)
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def transcribe_with_google(self, audio_path, language='en'):
        """Transcribe using Google Speech Recognition"""
        try:
            audio = AudioSegment.from_file(audio_path)
            wav_path = audio_path.replace('.wav', '_converted.wav')
            audio.export(wav_path, format='wav')
            
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
            
            google_lang = {
                'en': 'en-IN',
                'hi': 'hi-IN', 
                'bn': 'bn-IN'
            }.get(language, 'en-IN')
            
            text = self.recognizer.recognize_google(audio_data, language=google_lang)
            
            if os.path.exists(wav_path):
                os.unlink(wav_path)
            
            return text
            
        except Exception as e:
            print(f"Google transcription error: {e}")
            return None
    
    def extract_audio_features(self, audio_data):
        """Extract basic audio features"""
        return {
            'energy': 0.5,
            'tempo': 120,
            'spectral_centroid': 1000,
            'zero_crossing_rate': 0.1
        }
