import speech_recognition as sr
import whisper
import requests
import tempfile
import os
from pydub import AudioSegment
import librosa
import numpy as np
from config import Config

class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        self.assembly_ai_key = Config.ASSEMBLY_AI_API_KEY
    
    def load_whisper_model(self):
        """Load Whisper model for offline transcription"""
        if self.whisper_model is None:
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model
    
    def transcribe_audio(self, audio_data, language='en'):
        """Transcribe audio using multiple methods"""
        # Save audio data to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name
        
        try:
            # Method 1: Try Whisper first (offline)
            transcription = self.transcribe_with_whisper(tmp_file_path, language)
            if transcription:
                return transcription
            
            # Method 2: Try Google Speech Recognition
            transcription = self.transcribe_with_google(tmp_file_path, language)
            if transcription:
                return transcription
            
            # Method 3: Try Assembly AI
            transcription = self.transcribe_with_assembly_ai(tmp_file_path, language)
            if transcription:
                return transcription
            
            return None
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def transcribe_with_whisper(self, audio_path, language='en'):
        """Transcribe using Whisper (offline)"""
        try:
            model = self.load_whisper_model()
            
            # Convert language codes
            whisper_lang = {
                'en': 'english',
                'hi': 'hindi',
                'bn': 'bengali'
            }.get(language, 'english')
            
            result = model.transcribe(audio_path, language=whisper_lang)
            return result['text'].strip()
            
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return None
    
    def transcribe_with_google(self, audio_path, language='en'):
        """Transcribe using Google Speech Recognition"""
        try:
            # Convert audio to wav format
            audio = AudioSegment.from_file(audio_path)
            wav_path = audio_path.replace('.wav', '_converted.wav')
            audio.export(wav_path, format='wav')
            
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
            
            # Google language codes
            google_lang = {
                'en': 'en-IN',
                'hi': 'hi-IN',
                'bn': 'bn-IN'
            }.get(language, 'en-IN')
            
            text = self.recognizer.recognize_google(audio_data, language=google_lang)
            
            # Clean up
            if os.path.exists(wav_path):
                os.unlink(wav_path)
            
            return text
            
        except Exception as e:
            print(f"Google transcription error: {e}")
            return None
    
    def transcribe_with_assembly_ai(self, audio_path, language='en'):
        """Transcribe using Assembly AI"""
        try:
            if not self.assembly_ai_key:
                return None
            
            # Upload audio file
            upload_response = requests.post(
                'https://api.assemblyai.com/v2/upload',
                files={'file': open(audio_path, 'rb')},
                headers={'authorization': self.assembly_ai_key}
            )
            
            if upload_response.status_code != 200:
                return None
            
            audio_url = upload_response.json()['upload_url']
            
            # Request transcription
            transcript_request = {
                'audio_url': audio_url,
                'language_code': language
            }
            
            response = requests.post(
                'https://api.assemblyai.com/v2/transcript',
                json=transcript_request,
                headers={'authorization': self.assembly_ai_key}
            )
            
            if response.status_code != 200:
                return None
            
            transcript_id = response.json()['id']
            
            # Poll for completion
            while True:
                response = requests.get(
                    f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
                    headers={'authorization': self.assembly_ai_key}
                )
                
                if response.status_code != 200:
                    return None
                
                result = response.json()
                if result['status'] == 'completed':
                    return result['text']
                elif result['status'] == 'error':
                    return None
                
                import time
                time.sleep(3)
                
        except Exception as e:
            print(f"Assembly AI transcription error: {e}")
            return None
    
    def extract_audio_features(self, audio_data):
        """Extract audio features for mood detection"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # Load audio
            y, sr = librosa.load(tmp_file_path)
            
            # Extract features
            features = {
                'energy': float(np.mean(librosa.feature.rms(y=y))),
                'tempo': float(librosa.beat.tempo(y=y, sr=sr)[0]),
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y)))
            }
            
            # Clean up
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            
            return features
            
        except Exception as e:
            print(f"Audio feature extraction error: {e}")
            return {}
    
    def synthesize_speech(self, text, language='en'):
        """Synthesize speech from text (placeholder)"""
        # This is a placeholder - in production you would use:
        # - Google Cloud TTS
        # - ElevenLabs
        # - Indic-TTS
        # - Azure Cognitive Services
        
        try:
            # For demo purposes, return a placeholder audio URL
            return f"https://your-tts-service.com/synthesize?text={text}&lang={language}"
        except Exception as e:
            print(f"TTS error: {e}")
            return None
