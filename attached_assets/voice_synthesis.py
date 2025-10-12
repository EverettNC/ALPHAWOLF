"""
AlphaVox - Voice Synthesis Module
--------------------------------
This module provides voice synthesis capabilities for AlphaVox using gTTS.
It supports multiple languages, regional accents, and speech rates.
"""

import logging
import os
import tempfile

import pygame
from gtts import gTTS
from gtts.lang import tts_langs

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize pygame mixer for audio playback
pygame.mixer.init()


class VoiceSynthesizer:
    """Voice synthesis engine for AlphaVox.

    Provides text-to-speech functionality with support for:
    - Multiple languages
    - Regional accent variations
    - Speech rate control
    """

    def __init__(self, cache_dir="voice_cache"):
        """Initialize the voice synthesizer.

        Args:
            cache_dir: Directory to cache generated audio files
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # Default settings
        self.default_language = "en"
        self.default_tld = "com"  # US English
        self.default_slow = False

        # Get available languages
        try:
            self.available_languages = tts_langs()
            logger.info(f"Loaded {len(self.available_languages)} available languages")
        except Exception as e:
            logger.error(f"Failed to load available languages: {e}")
            self.available_languages = {"en": "English"}

        # Define voice profiles for English regional accents
        self.english_accents = {
            "us": {"tld": "com"},  # US English
            "uk": {"tld": "co.uk"},  # UK English
            "au": {"tld": "com.au"},  # Australian English
            "ca": {"tld": "ca"},  # Canadian English
            "in": {"tld": "co.in"},  # Indian English
            "za": {"tld": "co.za"},  # South African English
            "ie": {"tld": "ie"},  # Irish English
        }

        # Flag to track if audio is currently playing
        self.is_playing = False

        logger.info("Voice synthesizer initialized")

    def get_available_languages(self):
        """Get list of available languages.

        Returns:
            dict: Available languages mapping ISO code to name
        """
        return self.available_languages

    def get_available_accents(self):
        """Get list of available English accents.

        Returns:
            list: Available accent codes
        """
        return list(self.english_accents.keys())

    def text_to_speech(
        self, text, language=None, accent=None, slow=None, play=True, save_path=None
    ):
        """Convert text to speech and optionally play it or save it to a file.

        Args:
            text: Text to convert to speech
            language: Language code (ISO 639-1), defaults to 'en'
            accent: Accent code for English (us, uk, au, etc.), ignored for non-English
            slow: Whether to use slower speech rate
            play: Whether to play the audio immediately
            save_path: Optional path to save the generated audio

        Returns:
            str: Path to the generated audio file
        """
        # Use default values if not specified
        language = language or self.default_language
        slow = slow if slow is not None else self.default_slow

        # Determine TLD for English regional accents
        tld = self.default_tld
        if language == "en" and accent in self.english_accents:
            tld = self.english_accents[accent]["tld"]

        # Log the request
        logger.info(f"Generating speech: lang={language}, tld={tld}, slow={slow}")
        logger.info(f"Text: {text[:50]}..." if len(text) > 50 else f"Text: {text}")

        try:
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=language,
                slow=slow,
                tld=tld if language == "en" else None,
            )

            # Determine output path
            if save_path:
                output_path = save_path
            else:
                # Create temporary file in cache directory
                with tempfile.NamedTemporaryFile(
                    suffix=".mp3", dir=self.cache_dir, delete=False
                ) as temp_file:
                    output_path = temp_file.name

            # Save the audio file
            tts.save(output_path)
            logger.info(f"Audio saved to {output_path}")

            # Play the audio if requested
            if play:
                self.play_audio(output_path)

            return output_path

        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return None

    def play_audio(self, audio_path):
        """Play an audio file.

        Args:
            audio_path: Path to the audio file to play

        Returns:
            bool: Whether playback started successfully
        """
        try:
            # Stop any currently playing audio
            pygame.mixer.music.stop()

            # Load and play the audio
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            self.is_playing = True

            # Set up callback for when playback ends
            pygame.mixer.music.set_endevent(pygame.USEREVENT)

            logger.info(f"Playing audio: {audio_path}")
            return True

        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            self.is_playing = False
            return False

    def stop_audio(self):
        """Stop any currently playing audio.

        Returns:
            bool: Whether audio was stopped
        """
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            logger.info("Audio playback stopped")
            return True
        return False

    def is_audio_playing(self):
        """Check if audio is currently playing.

        Returns:
            bool: Whether audio is playing
        """
        return pygame.mixer.music.get_busy()

    def set_defaults(self, language=None, accent=None, slow=None):
        """Set default values for synthesis parameters.

        Args:
            language: Default language code
            accent: Default accent code for English
            slow: Default speech rate (slow/normal)

        Returns:
            dict: Updated default settings
        """
        if language:
            if language in self.available_languages:
                self.default_language = language
            else:
                logger.warning(
                    f"Language '{language}' not available, using current default: {self.default_language}"
                )

        if accent:
            if accent in self.english_accents:
                self.default_tld = self.english_accents[accent]["tld"]
            else:
                logger.warning(
                    f"Accent '{accent}' not available, using current default"
                )

        if slow is not None:
            self.default_slow = bool(slow)

        logger.info(
            f"Default settings updated: language={self.default_language}, "
            + f"tld={self.default_tld}, slow={self.default_slow}"
        )

        return {
            "language": self.default_language,
            "tld": self.default_tld,
            "slow": self.default_slow,
        }

    def speak_with_emotion(
        self, text, emotion=None, emotion_intensity=None, language=None, accent=None
    ):
        """Generate speech with emotional context.

        This method adjusts speech parameters based on the specified emotion and intensity.

        Args:
            text: Text to speak
            emotion: Emotional context (happy, sad, angry, etc.)
            emotion_intensity: Intensity of emotion (mild, moderate, strong)
            language: Language code
            accent: Accent code for English

        Returns:
            str: Path to the generated audio file
        """
        # Default values
        language = language or self.default_language

        # Determine speech parameters based on emotion
        slow = self.default_slow

        # Adjust speech parameters based on emotion
        if emotion:
            logger.info(
                f"Applying emotional context: {emotion}, intensity: {emotion_intensity}"
            )

            # Simple emotion-based adjustments
            if emotion.lower() in ["sad", "unhappy", "depressed"]:
                slow = True

            # Prepend emotion indicator for demonstration purposes
            # In a real implementation, this would use more sophisticated voice modulation
            if emotion_intensity == "strong":
                text = f"[With strong {emotion}] {text}"
            elif emotion_intensity == "moderate":
                text = f"[With moderate {emotion}] {text}"
            elif emotion_intensity:
                text = f"[With mild {emotion}] {text}"

        # Generate speech with adjusted parameters
        return self.text_to_speech(text, language=language, accent=accent, slow=slow)


# Create a singleton instance
_voice_synthesizer = None


def get_voice_synthesizer():
    """Get or create the voice synthesizer singleton."""
    global _voice_synthesizer
    if _voice_synthesizer is None:
        _voice_synthesizer = VoiceSynthesizer()
    return _voice_synthesizer
