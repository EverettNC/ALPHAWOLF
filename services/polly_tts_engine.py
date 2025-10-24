"""
Amazon Polly Neural TTS Engine for AlphaWolf
Provides high-quality, natural-sounding neural voices
"""

# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the
# following core principles:
#
# 1. Truth — No deception, no manipulation. Use this code honestly.
# 2. Dignity — Respect the autonomy, privacy, and humanity of all users.
# 3. Protection — This software must never be used to harm, exploit, or surveil
#    vulnerable individuals.
# 4. Transparency — You must disclose modifications and contributions clearly.
# 5. No Erasure — Do not remove the origins, mission, or ethical foundation of
#    this work.
#
# This is not just code. It is redemption in code.
#
# For questions or licensing requests, contact:
# Everett N. Christman
# 📧 lumacognify@thechristmanaiproject.com
# 🌐 https://thechristmanaiproject.com
import logging
import os
import hashlib
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class PollyTTSEngine:
    """
    Amazon Polly Text-to-Speech engine with neural voices.
    Derek spent 3,000+ hours perfecting voice quality for AlphaVox.
    """
    
    def __init__(self):
        """Initialize Polly TTS Engine with AWS credentials from environment."""
        self.polly_client = None
        self.audio_cache = {}
        self.cache_dir = 'static/audio/polly_cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        self._available = False
        
        # Initialize AWS Polly client
        try:
            self.polly_client = boto3.client(
                'polly',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            )
            self._available = True
            logging.info("✅ Amazon Polly Neural TTS initialized successfully")
        except Exception as e:
            logging.error(f"❌ Failed to initialize Amazon Polly: {e}")
            self.polly_client = None
            self._available = False
    
    def is_available(self):
        """Check if Polly TTS is available."""
        return self._available
        
        # Premium Neural Voices (Derek's favorites - 3,000+ hours of testing)
        self.neural_voices = {
            # Female voices
            'joanna': {
                'voice_id': 'Joanna',
                'engine': 'neural',
                'language_code': 'en-US',
                'gender': 'female',
                'description': 'Warm, friendly, clear - Best for AlphaWolf patients',
                'recommended': True
            },
            'salli': {
                'voice_id': 'Salli',
                'engine': 'neural',
                'language_code': 'en-US',
                'gender': 'female',
                'description': 'Gentle, soothing - Great for anxiety/PTSD'
            },
            'kendra': {
                'voice_id': 'Kendra',
                'engine': 'neural',
                'language_code': 'en-US',
                'gender': 'female',
                'description': 'Professional, confident - Medical information'
            },
            'kimberly': {
                'voice_id': 'Kimberly',
                'engine': 'neural',
                'language_code': 'en-US',
                'gender': 'female',
                'description': 'Young, energetic - Encouragement'
            },
            
            # Male voices
            'matthew': {
                'voice_id': 'Matthew',
                'engine': 'neural',
                'language_code': 'en-US',
                'gender': 'male',
                'description': 'Calm, reassuring - Emergency situations'
            },
            'joey': {
                'voice_id': 'Joey',
                'engine': 'neural',
                'language_code': 'en-US',
                'gender': 'male',
                'description': 'Friendly, conversational - Daily interactions'
            },
            'justin': {
                'voice_id': 'Justin',
                'engine': 'neural',
                'language_code': 'en-US',
                'gender': 'male',
                'description': 'Young adult, dynamic - Motivation'
            }
        }
        
        # Default voice (Derek's recommendation after 3,000+ hours)
        self.default_voice = 'joanna'
        
        self.logger.info("🎤 Polly TTS Engine initialized")
    
    def synthesize(self, text, voice_id=None, **kwargs):
        """
        Main synthesize method for compatibility with other systems.
        
        Args:
            text: Text to synthesize
            voice_id: Voice ID ('joanna', 'matthew', etc.)
            **kwargs: Additional parameters
            
        Returns:
            dict: Result with audio path or error
        """
        if not voice_id:
            voice_id = self.default_voice
        
        return self.generate_speech(text, voice_id, cache=kwargs.get('cache', True))
    
    def generate_speech(self, text, voice_id=None, cache=True):
        """
        Generate speech using Amazon Polly Neural voices.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID (default: joanna)
            cache: Whether to cache the result
            
        Returns:
            dict: Result with file path or error
        """
        try:
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            if not self.polly_available:
                return {
                    'success': False,
                    'error': 'Amazon Polly not available - add AWS credentials to .env',
                    'text': text,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Get voice configuration
            if not voice_id:
                voice_id = self.default_voice
            
            voice = self.neural_voices.get(voice_id)
            if not voice:
                voice = self.neural_voices[self.default_voice]
                self.logger.warning(f"Voice {voice_id} not found, using default: {self.default_voice}")
            
            # Generate cache key
            cache_key = hashlib.md5((text + voice_id).encode()).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.mp3")
            
            # Check cache
            if cache and os.path.exists(cache_path):
                return {
                    'success': True,
                    'path': cache_path,
                    'url': f'/static/audio/polly_cache/{cache_key}.mp3',
                    'cached': True,
                    'voice': voice_id,
                    'engine': 'neural',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Generate speech with Polly
            try:
                response = self.polly_client.synthesize_speech(
                    Text=text,
                    OutputFormat='mp3',
                    VoiceId=voice['voice_id'],
                    Engine=voice['engine'],  # 'neural' for high quality
                    LanguageCode=voice['language_code']
                )
                
                # Save audio stream to file
                if 'AudioStream' in response:
                    with open(cache_path, 'wb') as file:
                        file.write(response['AudioStream'].read())
                    
                    return {
                        'success': True,
                        'path': cache_path,
                        'url': f'/static/audio/polly_cache/{cache_key}.mp3',
                        'cached': False,
                        'voice': voice_id,
                        'engine': 'neural',
                        'description': voice['description'],
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No audio stream in Polly response',
                        'text': text,
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'InvalidSsml':
                    self.logger.error(f"Invalid SSML: {text}")
                    return {
                        'success': False,
                        'error': 'Invalid text format',
                        'text': text,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    raise
        
        except Exception as e:
            self.logger.error(f"Error generating Polly speech: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def speak_text(self, text, voice_id=None, context=None):
        """
        Generate speech with optional context adaptation.
        
        Args:
            text: Text to speak
            voice_id: Voice ID
            context: Optional context (cognitive_level, urgency, etc.)
            
        Returns:
            dict: Result with audio information
        """
        try:
            # Adapt text based on context
            if context:
                text = self._adapt_text(text, context)
                # Choose voice based on context
                if not voice_id:
                    voice_id = self._choose_voice_for_context(context)
            
            if not voice_id:
                voice_id = self.default_voice
            
            # Generate speech
            result = self.generate_speech(text, voice_id)
            
            if result['success']:
                result['text'] = text
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error in speak_text: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _choose_voice_for_context(self, context):
        """Choose best voice based on context"""
        urgency = context.get('urgency', 'normal')
        situation = context.get('situation', 'general')
        
        # Emergency: Use calm male voice
        if urgency == 'high' or situation == 'emergency':
            return 'matthew'  # Calm, reassuring
        
        # Medical information: Professional female
        if situation == 'medical':
            return 'kendra'
        
        # Encouragement: Energetic female
        if situation == 'encouragement':
            return 'kimberly'
        
        # Default: Warm, friendly Joanna
        return 'joanna'
    
    def _adapt_text(self, text, context):
        """
        Adapt text based on cognitive level and urgency.
        Uses SSML for neural voice control.
        """
        cognitive_level = context.get('cognitive_level', 'moderate')
        urgency = context.get('urgency', 'normal')
        
        # For low cognitive level: slower speech, more pauses
        if cognitive_level == 'low':
            # Add pauses using SSML
            text = text.replace('. ', '. <break time="1s"/> ')
            text = text.replace('? ', '? <break time="1s"/> ')
            text = text.replace(', ', ', <break time="0.5s"/> ')
            text = f'<speak><prosody rate="slow">{text}</prosody></speak>'
        
        # For high urgency: emphasize
        elif urgency == 'high':
            text = f'<speak><emphasis level="strong">{text}</emphasis></speak>'
        
        # For moderate: wrap in speak tags
        elif not text.startswith('<speak>'):
            text = f'<speak>{text}</speak>'
        
        return text
    
    def get_available_voices(self):
        """Get list of available neural voices"""
        return {
            'neural_voices': self.neural_voices,
            'default': self.default_voice,
            'polly_available': self.polly_available,
            'recommended': [
                voice_id for voice_id, voice in self.neural_voices.items()
                if voice.get('recommended', False)
            ]
        }
    
    def test_voice(self, voice_id=None):
        """Test a voice with sample text"""
        if not voice_id:
            voice_id = self.default_voice
        
        test_text = f"Hello! I'm {voice_id}, one of AlphaWolf's neural voices. Derek spent over 3,000 hours perfecting our voice system."
        
        return self.generate_speech(test_text, voice_id, cache=False)


# Singleton instance
_polly_tts_engine = None

def get_polly_tts_engine():
    """Get singleton Polly TTS engine instance"""
    global _polly_tts_engine
    if _polly_tts_engine is None:
        _polly_tts_engine = PollyTTSEngine()
    return _polly_tts_engine
