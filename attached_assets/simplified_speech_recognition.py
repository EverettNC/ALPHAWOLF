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
AlphaVox - Simplified Speech Recognition
--------------------------------------
This module provides a simplified speech recognition implementation that can be
easily integrated with web browsers using JavaScript's Web Speech API.

It includes:
- Server-side speech processing
- Integration with conversation engine
- Error handling for various speech recognition scenarios
"""

import logging
import json
import time
import threading
from typing import Dict, Any, List, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplifiedSpeechRecognition:
    """
    Simplified speech recognition for AlphaVox that works with Web Speech API.
    
    This class handles:
    - Processing speech recognition results from browser
    - Confidence thresholds for transcription quality
    - Integration with conversation handlers
    - Maintaining speech context
    """
    
    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize the simplified speech recognition service.
        
        Args:
            min_confidence: Minimum confidence threshold for accepting transcription
        """
        self.min_confidence = min_confidence
        self.callbacks = []
        self.is_active = True
        self.processing_lock = threading.Lock()
        self.speech_context = {}
        
        logger.info("SimplifiedSpeechRecognition initialized")
    
    def process_speech_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a speech recognition result from the Web Speech API.
        
        Args:
            result: Dictionary containing the speech recognition result
                   (transcript, confidence, isFinal, etc.)
                   
        Returns:
            Dictionary with processed result and response information
        """
        with self.processing_lock:
            transcript = result.get('transcript', '')
            confidence = result.get('confidence', 0.0)
            is_final = result.get('isFinal', False)
            
            logger.info(f"Processing speech: '{transcript}' (confidence: {confidence}, final: {is_final})")
            
            if not is_final:
                return {
                    'status': 'interim',
                    'transcript': transcript,
                    'confidence': confidence
                }
            
            if confidence < self.min_confidence:
                logger.warning(f"Low confidence speech detection: {confidence}")
                return {
                    'status': 'low_confidence',
                    'transcript': transcript,
                    'confidence': confidence,
                    'message': 'Could not understand clearly. Please try again.'
                }
            
            # Update speech context
            self._update_context(transcript)
            
            # Process through callbacks
            responses = []
            for callback in self.callbacks:
                try:
                    response = callback(transcript, confidence, self.speech_context)
                    if response:
                        responses.append(response)
                except Exception as e:
                    logger.error(f"Error in speech callback: {e}")
            
            combined_response = self._combine_responses(responses)
            
            return {
                'status': 'success',
                'transcript': transcript,
                'confidence': confidence,
                'response': combined_response
            }
    
    def register_callback(self, callback: Callable):
        """
        Register a callback function to process recognized speech.
        
        Args:
            callback: Function that takes (transcript, confidence, context) and returns a response
        """
        self.callbacks.append(callback)
        logger.info(f"Speech callback registered: {callback.__name__}")
    
    def _update_context(self, transcript: str):
        """
        Update the speech context with the latest transcript.
        
        Args:
            transcript: The speech transcript to add to context
        """
        if 'recent_transcripts' not in self.speech_context:
            self.speech_context['recent_transcripts'] = []
        
        self.speech_context['recent_transcripts'].append({
            'text': transcript,
            'timestamp': time.time()
        })
        
        # Keep only the 5 most recent transcripts
        self.speech_context['recent_transcripts'] = self.speech_context['recent_transcripts'][-5:]
    
    def _combine_responses(self, responses: List[Any]) -> str:
        """
        Combine multiple callback responses into a single response.
        
        Args:
            responses: List of responses from callbacks
            
        Returns:
            Combined response text
        """
        if not responses:
            return "I heard you, but I'm not sure how to respond."
        
        # For now, just use the first non-empty response
        for response in responses:
            if response and isinstance(response, str) and response.strip():
                return response
        
        return "I heard you, but I'm not sure how to respond."
    
    def reset_context(self):
        """Reset the speech context."""
        self.speech_context = {}
        logger.info("Speech context reset")

# Singleton instance
_speech_recognition = None

def get_speech_recognition():
    """Get the singleton speech recognition instance."""
    global _speech_recognition
    if _speech_recognition is None:
        _speech_recognition = SimplifiedSpeechRecognition()
    return _speech_recognition

def process_speech_from_browser(result):
    """
    Process speech recognition results from the browser.
    
    Args:
        result: Speech recognition result from Web Speech API
        
    Returns:
        Processed result with response
    """
    speech_recognition = get_speech_recognition()
    return speech_recognition.process_speech_result(result)