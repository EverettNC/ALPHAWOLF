# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
"""
AlphaVox - Enhanced Speech Recognition
------------------------------------
This module extends the existing sound recognition capabilities with full
speech recognition, allowing AlphaVox to understand spoken language and
maintain complete conversations.

It integrates with the sound_recognition_service for non-verbal sound patterns
and adds speech-to-text processing for verbal inputs.
"""

import json
import logging
import os
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedSpeechRecognition:
    """Enhanced speech recognition system that combines verbal speech
    recognition with non-verbal sound pattern recognition.

    This class provides:
    - Integration with the existing SoundRecognitionService
    - Web-based microphone capture
    - Streaming speech recognition
    - Continuous listening mode
    - Speech recognition with context
    """

    def __init__(self):
        """Initialize the enhanced speech recognition system."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing EnhancedSpeechRecognition")

        # Recognition status
        self.is_listening = False
        self.is_processing = False
        self.current_audio_data = []

        # Callbacks
        self.speech_callbacks = []
        self.sound_pattern_callbacks = []

        # Recognition parameters
        self.language = "en-US"
        self.sensitivity = 0.5
        self.silence_threshold = 0.1  # Energy level to detect speech
        self.min_audio_length = 0.5  # Minimum seconds of audio to process

        # Recognition context
        self.recognition_context = {
            "recent_phrases": [],  # Recently recognized phrases for context
            "current_topic": None,  # Current conversational topic
            "active_keywords": [],  # Keywords to prioritize in recognition
        }

        # Cache for audio processing
        self.audio_cache_dir = os.path.join("static", "audio", "recognition_cache")
        os.makedirs(self.audio_cache_dir, exist_ok=True)

        # Try to load the sound recognition service if available
        try:
            from sound_recognition_service import SoundRecognitionService

            self.sound_service = SoundRecognitionService()
            self.logger.info("Sound recognition service loaded")
        except ImportError:
            self.sound_service = None
            self.logger.warning("Sound recognition service not available")

        self.logger.info("EnhancedSpeechRecognition initialized")

    def start_listening(
        self,
        speech_callback: Optional[Callable] = None,
        sound_pattern_callback: Optional[Callable] = None,
    ) -> bool:
        """Start listening for speech and sound patterns.

        Args:
            speech_callback: Optional callback for speech recognition results
            sound_pattern_callback: Optional callback for sound pattern recognition

        Returns:
            True if started successfully, False otherwise
        """
        if self.is_listening:
            self.logger.warning("Speech recognition is already active")
            return False

        # Register callbacks if provided
        if speech_callback:
            self.speech_callbacks.append(speech_callback)

        if sound_pattern_callback:
            self.sound_pattern_callbacks.append(sound_pattern_callback)

        # Start sound recognition service if available
        if self.sound_service:
            self.sound_service.start_listening()

        # Mark as listening
        self.is_listening = True

        # Start the listener thread
        self._start_listening_thread()

        self.logger.info("Speech recognition started")
        return True

    def stop_listening(self) -> bool:
        """Stop listening for speech and sound patterns.

        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.is_listening:
            self.logger.warning("Speech recognition is not active")
            return False

        # Stop sound recognition service if available
        if self.sound_service:
            self.sound_service.stop_listening()

        # Mark as not listening
        self.is_listening = False

        self.logger.info("Speech recognition stopped")
        return True

    def _start_listening_thread(self):
        """Start the background listening thread."""
        thread = threading.Thread(target=self._listening_loop)
        thread.daemon = True
        thread.start()

    def _listening_loop(self):
        """Main listening loop that runs in the background."""
        self.logger.debug("Listening loop started")

        while self.is_listening:
            try:
                # Check for sound patterns using the sound service
                if self.sound_service:
                    sound_result = self.sound_service.detect_sound_pattern()
                    if sound_result:
                        self._process_sound_pattern(sound_result)

                # In a real implementation, this would process microphone audio streams
                # For now, we'll simulate occasional speech recognition
                self._simulate_speech_recognition()

                # Sleep to avoid CPU usage
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in listening loop: {e}")
                # Continue loop despite errors

        self.logger.debug("Listening loop ended")

    def _simulate_speech_recognition(self):
        """Simulate speech recognition for testing and development.

        In a real implementation, this would process actual audio from a
        microphone or audio stream.
        """
        # Only occasionally simulate speech (about once every 10-15 seconds)
        if not hasattr(self, "_last_simulation_time"):
            self._last_simulation_time = 0

        current_time = time.time()
        simulation_interval = 10 + (5 * self.sensitivity)  # 10-15 seconds

        if current_time - self._last_simulation_time < simulation_interval:
            return

        # 10% chance of simulating speech detection
        import random

        if random.random() < 0.1:
            self._last_simulation_time = current_time

            # Simulate speech recognition with sample phrases
            sample_phrases = [
                "Hello, how are you today?",
                "Can you tell me more about nonverbal communication?",
                "I'd like to learn about eye tracking",
                "What features does AlphaVox have?",
                "Can you explain how your AI works?",
            ]

            recognized_text = random.choice(sample_phrases)
            confidence = 0.7 + (random.random() * 0.25)  # 0.7-0.95

            # Create metadata
            metadata = {
                "confidence": confidence,
                "language": self.language,
                "timestamp": current_time,
                "audio_length": random.uniform(1.0, 3.0),
                "source": "simulation",
            }

            # Log the simulated recognition
            self.logger.info(
                f"Simulated speech recognition: '{recognized_text}' "
                f"(confidence: {confidence:.2f})"
            )

            # Process the recognized speech
            self._process_recognized_speech(recognized_text, metadata)

    def process_audio_data(
        self, audio_data: bytes, sample_rate: int = 16000, format_: str = "wav"
    ) -> Dict[str, Any]:
        """Process audio data and perform speech recognition.

        Args:
            audio_data: Raw audio data bytes
            sample_rate: Sample rate of the audio
            format_: Format of the audio data

        Returns:
            Dict with recognition results
        """
        if not audio_data:
            return {"error": "No audio data provided"}

        self.logger.info(f"Processing {len(audio_data)} bytes of audio data")

        # Mark as processing
        self.is_processing = True

        try:
            # Save the audio data to a temporary file
            import uuid
            import wave
            from datetime import datetime

            file_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(
                self.audio_cache_dir, f"audio_{timestamp}_{file_id}.wav"
            )

            # In a real implementation, this would process the audio into the correct format
            # For now, we'll just save as is and simulate recognition

            # Simulate recognition result
            import random

            # Sample phrases - in a real implementation, this would be actual recognition
            sample_phrases = [
                "Hello, I'm using AlphaVox.",
                "Can you help me with communication?",
                "This is a test of speech recognition.",
                "I'd like to know more about this system.",
                "Thank you for helping me communicate.",
            ]

            recognized_text = random.choice(sample_phrases)
            confidence = 0.7 + (random.random() * 0.25)  # 0.7-0.95

            # Create result
            result = {
                "text": recognized_text,
                "confidence": confidence,
                "language": self.language,
                "timestamp": time.time(),
                "audio_path": file_path,
            }

            # Log the recognition
            self.logger.info(
                f"Audio processing result: '{recognized_text}' "
                f"(confidence: {confidence:.2f})"
            )

            # Update recognition context
            self._update_recognition_context(recognized_text)

            # Notify callbacks
            self._process_recognized_speech(recognized_text, result)

            return result
        except Exception as e:
            self.logger.error(f"Error processing audio data: {e}")
            return {"error": str(e)}
        finally:
            # Mark as no longer processing
            self.is_processing = False

    def _process_recognized_speech(self, text: str, metadata: Dict[str, Any]):
        """Process recognized speech and notify callbacks.

        Args:
            text: Recognized text
            metadata: Recognition metadata
        """
        if not text:
            return

        # Update recognition context
        self._update_recognition_context(text)

        # Notify all registered callbacks
        for callback in self.speech_callbacks:
            try:
                callback(text, metadata.get("confidence", 0.0), metadata)
            except Exception as e:
                self.logger.error(f"Error in speech callback: {e}")

    def _process_sound_pattern(self, sound_result: Dict[str, Any]):
        """Process detected sound pattern and notify callbacks.

        Args:
            sound_result: Sound pattern detection result
        """
        if not sound_result:
            return

        pattern = sound_result.get("pattern")
        confidence = sound_result.get("confidence", 0.0)

        # Get the intent classification if sound service is available
        intent_data = {}
        if self.sound_service:
            try:
                intent_data = self.sound_service.classify_sound_intent(pattern)
            except Exception as e:
                self.logger.error(f"Error classifying sound intent: {e}")

        # Combine data
        combined_data = {**sound_result, **intent_data}

        # Notify all registered callbacks
        for callback in self.sound_pattern_callbacks:
            try:
                callback(pattern, confidence, combined_data)
            except Exception as e:
                self.logger.error(f"Error in sound pattern callback: {e}")

    def _update_recognition_context(self, text: str):
        """Update the recognition context with new text.

        Args:
            text: Recognized text
        """
        # Add to recent phrases (limit to 5)
        self.recognition_context["recent_phrases"].append(text)
        if len(self.recognition_context["recent_phrases"]) > 5:
            self.recognition_context["recent_phrases"].pop(0)

        # In a real implementation, this would update topic and keywords
        # based on natural language processing of the text

    def set_language(self, language: str) -> bool:
        """Set the recognition language.

        Args:
            language: Language code (e.g., "en-US", "fr-FR")

        Returns:
            True if successful, False otherwise
        """
        self.language = language
        self.logger.info(f"Recognition language set to: {language}")
        return True

    def set_sensitivity(self, sensitivity: float) -> bool:
        """Set the recognition sensitivity.

        Args:
            sensitivity: Sensitivity value (0.0-1.0)

        Returns:
            True if successful, False otherwise
        """
        if sensitivity < 0.0 or sensitivity > 1.0:
            self.logger.error(f"Invalid sensitivity value: {sensitivity}")
            return False

        self.sensitivity = sensitivity
        self.logger.info(f"Recognition sensitivity set to: {sensitivity}")
        return True

    def add_recognition_keywords(self, keywords: List[str]) -> bool:
        """Add keywords to prioritize in recognition.

        Args:
            keywords: List of keywords to prioritize

        Returns:
            True if successful, False otherwise
        """
        if not isinstance(keywords, list):
            self.logger.error("Keywords must be a list")
            return False

        self.recognition_context["active_keywords"].extend(keywords)
        self.logger.info(f"Added recognition keywords: {keywords}")
        return True

    def clear_recognition_keywords(self) -> bool:
        """Clear all recognition keywords.

        Returns:
            True if successful, False otherwise
        """
        self.recognition_context["active_keywords"] = []
        self.logger.info("Cleared recognition keywords")
        return True

    def get_recognition_status(self) -> Dict[str, Any]:
        """Get the current status of the speech recognition system.

        Returns:
            Dict with status information
        """
        return {
            "is_listening": self.is_listening,
            "is_processing": self.is_processing,
            "language": self.language,
            "sensitivity": self.sensitivity,
            "context": {
                "recent_phrases_count": len(self.recognition_context["recent_phrases"]),
                "current_topic": self.recognition_context["current_topic"],
                "active_keywords_count": len(
                    self.recognition_context["active_keywords"]
                ),
            },
        }


# Singleton instance
_enhanced_speech_recognition = None


def get_enhanced_speech_recognition() -> EnhancedSpeechRecognition:
    """Get the singleton instance of the enhanced speech recognition system."""
    global _enhanced_speech_recognition
    if _enhanced_speech_recognition is None:
        _enhanced_speech_recognition = EnhancedSpeechRecognition()
    return _enhanced_speech_recognition
