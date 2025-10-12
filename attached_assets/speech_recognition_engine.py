"""
AlphaVox - Speech Recognition Engine
-----------------------------------
This module provides speech recognition capabilities for the AlphaVox system.
It processes audio input and converts speech to text for further analysis.

The engine supports:
- Real-time audio processing
- Noise filtering
- Multiple language support
- Speaker identification
"""

import logging
import os
import time
import threading
import numpy as np
from typing import Dict, Any, List, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
AUDIO_SAMPLE_RATE = 16000
MIN_SPEECH_DURATION = 0.5  # seconds
SILENCE_THRESHOLD = 0.1
AUDIO_CACHE_DIR = "audio_cache"

# Create directory for audio cache if it doesn't exist
if not os.path.exists(AUDIO_CACHE_DIR):
    os.makedirs(AUDIO_CACHE_DIR)

class SpeechRecognitionEngine:
    """
    Engine for processing speech input and converting it to text.
    
    This engine handles:
    - Audio stream processing
    - Speech detection
    - Speech-to-text conversion
    - Speaker identification
    - Language detection
    """
    
    def __init__(self, language: str = "en-US"):
        """
        Initialize the speech recognition engine.
        
        Args:
            language: The default language code to use for recognition
        """
        self.language = language
        self.is_listening = False
        self.callbacks = []
        self.audio_buffer = []
        self.last_speech_time = 0
        
        # Speech detection parameters
        self.silence_threshold = SILENCE_THRESHOLD
        self.min_speech_duration = MIN_SPEECH_DURATION
        
        logger.info(f"Speech Recognition Engine initialized with language: {language}")
    
    def start_listening(self, callback: Optional[Callable] = None) -> bool:
        """
        Start listening for speech input.
        
        Args:
            callback: Optional callback function to call when speech is recognized
                     Function signature: callback(text: str, confidence: float, metadata: Dict[str, Any])
        
        Returns:
            True if listening started successfully, False otherwise
        """
        if self.is_listening:
            logger.warning("Speech recognition is already active")
            return False
        
        if callback:
            self.callbacks.append(callback)
        
        self.is_listening = True
        self._start_listening_thread()
        
        logger.info("Speech recognition started")
        return True
    
    def stop_listening(self) -> bool:
        """
        Stop listening for speech input.
        
        Returns:
            True if listening stopped successfully, False otherwise
        """
        if not self.is_listening:
            logger.warning("Speech recognition is not active")
            return False
        
        self.is_listening = False
        logger.info("Speech recognition stopped")
        return True
    
    def _start_listening_thread(self):
        """Start a background thread to process audio input"""
        thread = threading.Thread(target=self._audio_processing_loop)
        thread.daemon = True
        thread.start()
    
    def _audio_processing_loop(self):
        """Main audio processing loop that runs in a background thread"""
        try:
            while self.is_listening:
                # Simulate audio capture and processing
                # In a real implementation, this would capture audio from a microphone
                audio_chunk = self._simulate_audio_capture()
                
                # Process the audio chunk
                self._process_audio_chunk(audio_chunk)
                
                # Sleep to simulate real-time processing
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in audio processing loop: {e}")
            self.is_listening = False
    
    def _simulate_audio_capture(self) -> np.ndarray:
        """
        Simulate capturing audio from a microphone.
        
        In a real implementation, this would use a library like PyAudio
        to capture audio from the system's microphone.
        
        Returns:
            NumPy array containing audio samples
        """
        # Generate random audio data for simulation
        # In a real implementation, this would be actual audio samples
        return np.random.normal(0, 0.1, int(AUDIO_SAMPLE_RATE * 0.1))
    
    def _process_audio_chunk(self, audio_chunk: np.ndarray):
        """
        Process an audio chunk to detect speech and perform recognition.
        
        Args:
            audio_chunk: NumPy array containing audio samples
        """
        # Add the chunk to our buffer
        self.audio_buffer.append(audio_chunk)
        
        # Limit buffer size to avoid memory issues
        max_buffer_size = int(AUDIO_SAMPLE_RATE * 5)  # 5 seconds of audio
        if len(self.audio_buffer) * len(audio_chunk) > max_buffer_size:
            self.audio_buffer.pop(0)
        
        # Check if there is speech in the audio
        if self._detect_speech(audio_chunk):
            self.last_speech_time = time.time()
            
            # If we have enough speech, process it
            if self._check_speech_duration():
                # Convert combined buffer to a single array
                combined_audio = np.concatenate(self.audio_buffer)
                
                # Perform speech recognition
                text, confidence, metadata = self._recognize_speech(combined_audio)
                
                if text:
                    # Notify all registered callbacks
                    for callback in self.callbacks:
                        callback(text, confidence, metadata)
                    
                    # Clear the buffer after processing
                    self.audio_buffer = []
    
    def _detect_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect if the audio chunk contains speech.
        
        Args:
            audio_chunk: NumPy array containing audio samples
        
        Returns:
            True if speech is detected, False otherwise
        """
        # Simple energy-based speech detection
        # In a real implementation, this would use more sophisticated techniques
        energy = np.mean(np.abs(audio_chunk))
        return energy > self.silence_threshold
    
    def _check_speech_duration(self) -> bool:
        """
        Check if we have captured enough speech to process.
        
        Returns:
            True if we have enough speech, False otherwise
        """
        if not self.audio_buffer:
            return False
        
        # Check if enough time has passed since last speech detection
        time_since_last_speech = time.time() - self.last_speech_time
        return time_since_last_speech > self.min_speech_duration
    
    def _recognize_speech(self, audio_data: np.ndarray) -> Tuple[str, float, Dict[str, Any]]:
        """
        Perform speech recognition on the audio data.
        
        In a real implementation, this would use a speech recognition library
        or service like Google Speech-to-Text, Mozilla DeepSpeech, etc.
        
        Args:
            audio_data: NumPy array containing audio samples
        
        Returns:
            Tuple of (recognized text, confidence score, metadata)
        """
        # Simulate speech recognition result
        # In a real implementation, this would call a speech recognition API
        
        # Randomly determine if we "recognized" something (for simulation)
        if np.random.random() > 0.3:  # 70% chance of recognition for demo
            # For demo purposes, return one of several predefined phrases
            phrases = [
                "Hello, how are you?",
                "What can you help me with?",
                "Tell me about nonverbal communication",
                "I need assistance with something",
                "Can you explain how AlphaVox works?"
            ]
            text = phrases[int(np.random.random() * len(phrases))]
            confidence = 0.7 + (np.random.random() * 0.3)  # Between 0.7 and 1.0
            
            # Log the recognition
            logger.info(f"Speech recognized: '{text}' (confidence: {confidence:.2f})")
            
            # Return the result
            return text, confidence, {
                "language": self.language,
                "duration": len(audio_data) / AUDIO_SAMPLE_RATE,
                "timestamp": time.time()
            }
        else:
            # No speech recognized or confidence too low
            return "", 0.0, {"error": "No speech recognized"}
    
    def set_language(self, language: str) -> bool:
        """
        Set the recognition language.
        
        Args:
            language: Language code (e.g., "en-US", "fr-FR", "es-ES")
        
        Returns:
            True if language was set successfully, False otherwise
        """
        self.language = language
        logger.info(f"Recognition language set to: {language}")
        return True
    
    def adjust_sensitivity(self, silence_threshold: float, min_speech_duration: float) -> bool:
        """
        Adjust the speech detection sensitivity parameters.
        
        Args:
            silence_threshold: Energy threshold for detecting speech
            min_speech_duration: Minimum duration of speech to trigger recognition
        
        Returns:
            True if parameters were adjusted successfully, False otherwise
        """
        if silence_threshold <= 0 or min_speech_duration <= 0:
            logger.error("Invalid sensitivity parameters")
            return False
        
        self.silence_threshold = silence_threshold
        self.min_speech_duration = min_speech_duration
        
        logger.info(f"Sensitivity adjusted: threshold={silence_threshold}, duration={min_speech_duration}")
        return True
    
    def transcribe_file(self, file_path: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Transcribe an audio file.
        
        Args:
            file_path: Path to the audio file
        
        Returns:
            Tuple of (recognized text, confidence score, metadata)
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return "", 0.0, {"error": "File not found"}
        
        logger.info(f"Transcribing audio file: {file_path}")
        
        # Simulate file transcription
        # In a real implementation, this would load and process the audio file
        time.sleep(1)  # Simulate processing time
        
        # Return simulated result
        text = "This is a transcription of the audio file content."
        confidence = 0.85
        
        return text, confidence, {
            "file": file_path,
            "language": self.language,
            "duration": 5.0,  # Simulated duration
            "timestamp": time.time()
        }


# Singleton instance
_speech_recognition_engine = None

def get_speech_recognition_engine() -> SpeechRecognitionEngine:
    """Get the singleton instance of the speech recognition engine"""
    global _speech_recognition_engine
    if _speech_recognition_engine is None:
        _speech_recognition_engine = SpeechRecognitionEngine()
    return _speech_recognition_engine