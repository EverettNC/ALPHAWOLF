import logging
import os
import hashlib
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class TTSEngine:
    """Text-to-Speech engine for generating voice responses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = os.path.join('static', 'audio', 'tts_cache')
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Voice configuration
        self.voices = {
            'female_default': {
                'language': 'en',
                'gender': 'female',
                'rate': 1.0,
                'pitch': 1.0
            },
            'male_default': {
                'language': 'en',
                'gender': 'male',
                'rate': 1.0,
                'pitch': 1.0
            },
            'female_slow': {
                'language': 'en',
                'gender': 'female',
                'rate': 0.8,
                'pitch': 1.0
            },
            'male_slow': {
                'language': 'en',
                'gender': 'male',
                'rate': 0.8,
                'pitch': 1.0
            }
        }
        
        # Try to import required libraries
        self.gtts_available = False
        try:
            from gtts import gTTS
            self.gtts_available = True
            self.logger.info("gTTS library available for TTS generation")
        except ImportError:
            self.logger.warning("gTTS library not available, TTS generation will be limited")
        
        self.logger.info("TTS Engine initialized")
    
    def generate_speech(self, text, voice_id='female_default', cache=True):
        """
        Generate speech audio from text.
        
        Args:
            text: Text to convert to speech
            voice_id: ID of voice to use
            cache: Whether to cache the result
            
        Returns:
            dict: Result with file path or error
        """
        try:
            # Check if text is empty
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Get voice configuration
            voice = self.voices.get(voice_id, self.voices['female_default'])
            
            # Generate cache key based on text and voice
            cache_key = hashlib.md5((text + str(voice)).encode()).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.mp3")
            
            # Check cache if enabled
            if cache and os.path.exists(cache_path):
                return {
                    'success': True,
                    'path': cache_path,
                    'cached': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Generate speech
            if self.gtts_available:
                from gtts import gTTS
                
                # Create gTTS object with the text and desired parameters
                tts = gTTS(text=text, lang=voice['language'], slow=(voice['rate'] < 0.9))
                
                # Save to file
                tts.save(cache_path)
                
                return {
                    'success': True,
                    'path': cache_path,
                    'cached': False,
                    'voice': voice_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                # Fallback if gTTS is not available
                return {
                    'success': False,
                    'error': 'TTS library not available',
                    'text': text,  # Return text for display
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error generating speech: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text,  # Return text for display
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def speak_text(self, text, voice_id='female_default', context=None):
        """
        Generate speech and prepare for playback.
        
        Args:
            text: Text to speak
            voice_id: ID of voice to use
            context: Optional context information for adapting speech
            
        Returns:
            dict: Result with audio information
        """
        try:
            # Adapt text based on context if provided
            if context:
                text = self._adapt_text(text, context)
            
            # Generate speech
            result = self.generate_speech(text, voice_id)
            
            # If successful, add additional playback information
            if result['success']:
                result['text'] = text
                result['url'] = '/static/audio/tts_cache/' + os.path.basename(result['path'])
                
                # Add SSML markup for web audio API (not actually used by gTTS but included for client)
                ssml = f'<speak>{text}</speak>'
                result['ssml'] = ssml
            
            return result
        except Exception as e:
            self.logger.error(f"Error preparing speech: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _adapt_text(self, text, context):
        """Adapt text based on context for better TTS."""
        adapted_text = text
        
        # Extract context information
        audience = context.get('audience', 'patient')
        cognitive_level = context.get('cognitive_level', 'moderate')
        urgency = context.get('urgency', 'normal')
        
        # Add pauses for easier comprehension
        if cognitive_level == 'low':
            # Add pauses after sentences and commas
            adapted_text = adapted_text.replace('. ', '. <break time="1s"/> ')
            adapted_text = adapted_text.replace(', ', ', <break time="0.5s"/> ')
        
        # Emphasize important words for urgent messages
        if urgency == 'high':
            # Simple approach: add emphasis to first sentence
            sentences = adapted_text.split('. ')
            if sentences:
                sentences[0] = f"<emphasis level='strong'>{sentences[0]}</emphasis>"
                adapted_text = '. '.join(sentences)
        
        return adapted_text
    
    def get_available_voices(self):
        """Get list of available voices."""
        return [
            {
                'id': voice_id,
                'name': voice_id.replace('_', ' ').title(),
                'language': voice['language'],
                'gender': voice['gender'],
                'rate': voice['rate'],
                'pitch': voice['pitch']
            }
            for voice_id, voice in self.voices.items()
        ]
    
    def add_custom_voice(self, voice_id, language, gender, rate, pitch):
        """Add a custom voice configuration."""
        try:
            if voice_id in self.voices:
                return {
                    'success': False,
                    'error': f"Voice ID '{voice_id}' already exists"
                }
            
            # Validate parameters
            if rate < 0.5 or rate > 1.5:
                return {
                    'success': False,
                    'error': "Rate must be between 0.5 and 1.5"
                }
                
            if pitch < 0.5 or pitch > 1.5:
                return {
                    'success': False,
                    'error': "Pitch must be between 0.5 and 1.5"
                }
            
            # Add voice
            self.voices[voice_id] = {
                'language': language,
                'gender': gender,
                'rate': rate,
                'pitch': pitch
            }
            
            return {
                'success': True,
                'voice_id': voice_id
            }
        except Exception as e:
            self.logger.error(f"Error adding custom voice: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_cache(self, max_age_days=30):
        """Clean up old cache files."""
        try:
            now = time.time()
            count = 0
            
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                
                # Check if file is old enough to delete
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > (max_age_days * 86400):  # Convert days to seconds
                        os.remove(file_path)
                        count += 1
            
            self.logger.info(f"Cleaned up {count} old cache files")
            return {
                'success': True,
                'files_removed': count
            }
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }