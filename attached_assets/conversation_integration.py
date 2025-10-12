"""
AlphaVox - Conversation Integration
---------------------------------
This module integrates all conversation components into a seamless system:
- Speech recognition for hearing the user
- Nonverbal cue detection (gestures, eye movements, emotions)
- LSTM-based temporal pattern recognition
- Comprehensive conversation handling
- Response generation with context awareness

This provides the AI with the ability to hold complete conversations while processing
multimodal inputs including speech and nonverbal cues.
"""

import logging
import time
import os
import json
from typing import Dict, Any, List, Optional, Tuple
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationIntegration:
    """
    Main integration class that brings together all conversation components
    to provide a unified conversational AI system.
    
    This class:
    - Coordinates between different input modalities
    - Manages the conversation flow
    - Integrates temporal pattern recognition
    - Handles speech and nonverbal inputs
    - Provides comprehensive responses
    """
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize the conversation integration.
        
        Args:
            user_id: Identifier for the current user
        """
        self.user_id = user_id
        self.components = {}
        self.is_active = False
        self.conversations = {}
        
        # Load components
        self._load_components()
        
        logger.info(f"Conversation Integration initialized for user: {user_id}")
    
    def _load_components(self):
        """Load all required components"""
        try:
            # Import lazily to avoid circular imports
            from alphavox import alphavox
            from conversation_engine import ConversationEngine
            from enhanced_speech_recognition import get_enhanced_speech_recognition
            from complete_conversation_handler import get_conversation_handler
            import sound_recognition_service
            
            # Store components
            self.components['alphavox'] = alphavox
            self.components['conversation_engine'] = alphavox.conversation_engine
            self.components['speech_recognition'] = get_enhanced_speech_recognition()
            self.components['conversation_handler'] = get_conversation_handler(self.user_id)
            
            # Try to load LSTM components if available
            try:
                import os
                if os.path.exists('lstm_models'):
                    from lstm_interpreter import LSTMInterpreter
                    self.components['lstm_interpreter'] = LSTMInterpreter()
                    logger.info("LSTM interpreter loaded successfully")
            except ImportError as e:
                logger.warning(f"Could not load LSTM interpreter: {e}")
            
            logger.info("All conversation components loaded successfully")
        except ImportError as e:
            logger.error(f"Failed to load required components: {e}")
            logger.warning("Some functionality may be limited")
    
    def start(self) -> bool:
        """
        Start the integrated conversation system.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_active:
            logger.warning("Conversation integration is already active")
            return False
        
        # Tag AlphaVox as active
        self.components['alphavox'].tag()
        
        # Start speech recognition
        speech_recognition = self.components.get('speech_recognition')
        if speech_recognition:
            speech_recognition.start_listening(callback=self._handle_speech_input)
        
        # Start conversation handler
        conversation_handler = self.components.get('conversation_handler')
        if conversation_handler:
            conversation_handler.start_conversation()
            
            # Register callbacks
            conversation_handler.register_output_callback(self._handle_conversation_output)
        
        # Mark as active
        self.is_active = True
        
        logger.info("Conversation integration started")
        return True
    
    def stop(self) -> bool:
        """
        Stop the integrated conversation system.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.is_active:
            logger.warning("Conversation integration is not active")
            return False
        
        # Stop speech recognition
        speech_recognition = self.components.get('speech_recognition')
        if speech_recognition:
            speech_recognition.stop_listening()
        
        # Stop conversation handler
        conversation_handler = self.components.get('conversation_handler')
        if conversation_handler:
            conversation_handler.end_conversation()
        
        # Mark as inactive
        self.is_active = False
        
        logger.info("Conversation integration stopped")
        return True
    
    def _handle_speech_input(self, text: str, confidence: float, metadata: Dict[str, Any]):
        """
        Handle speech input from the speech recognition component.
        
        Args:
            text: Recognized text
            confidence: Confidence score for the recognition
            metadata: Additional metadata about the recognition
        """
        if not self.is_active or not text:
            return
        
        logger.info(f"Speech input: '{text}' (confidence: {confidence:.2f})")
        
        # Process through conversation handler
        conversation_handler = self.components.get('conversation_handler')
        if conversation_handler:
            # Create enhanced metadata
            enhanced_metadata = {
                'source': 'speech',
                'confidence': confidence,
                'modality': 'verbal',
                **metadata
            }
            
            # Add to conversation
            response = conversation_handler.add_text_input(text, enhanced_metadata)
            
            # Log the response
            logger.info(f"Response to speech: '{response}'")
            
            # Generate speech response
            try:
                from app import text_to_speech
                audio_path = text_to_speech(response)
                logger.info(f"Generated speech response: {audio_path}")
            except Exception as e:
                logger.error(f"Error generating speech response: {e}")
    
    def _handle_nonverbal_input(self, analysis: Dict[str, Any]):
        """
        Handle nonverbal input from various sources.
        
        Args:
            analysis: Analysis of nonverbal cues
        """
        if not self.is_active:
            return
        
        # Process through LSTM interpreter if available
        lstm_interpreter = self.components.get('lstm_interpreter')
        if lstm_interpreter and 'sequence' in analysis:
            # This is a temporal sequence, process with LSTM
            lstm_result = lstm_interpreter.interpret_sequence(
                analysis['sequence'],
                analysis.get('sequence_type', 'gesture')
            )
            
            # Enhance the analysis with LSTM results
            analysis.update(lstm_result)
        
        # Process through conversation handler
        conversation_handler = self.components.get('conversation_handler')
        if conversation_handler:
            response = conversation_handler.add_nonverbal_input(analysis)
            
            # Log the response
            logger.info(f"Response to nonverbal input: '{response}'")
            
            # Generate speech response
            try:
                from app import text_to_speech
                audio_path = text_to_speech(response)
                logger.info(f"Generated speech response: {audio_path}")
            except Exception as e:
                logger.error(f"Error generating speech response: {e}")
    
    def _handle_conversation_output(self, response: str, context: Any):
        """
        Handle output from the conversation handler.
        
        Args:
            response: Text response
            context: Conversation context
        """
        # Log the response
        logger.debug(f"Conversation output: '{response}'")
        
        # Here you could integrate with other systems or interfaces
        # For example, updating UI elements, triggering animations, etc.
    
    def process_text_input(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process text input from external sources.
        
        Args:
            text: Text input
            metadata: Optional metadata
            
        Returns:
            Response text
        """
        if not self.is_active:
            logger.warning("Cannot process input: Conversation integration is not active")
            return "Conversation system is not active. Please start the system first."
        
        if metadata is None:
            metadata = {}
        
        # Process through conversation handler
        conversation_handler = self.components.get('conversation_handler')
        if conversation_handler:
            enhanced_metadata = {
                'source': 'external',
                'modality': 'text',
                **metadata
            }
            
            response = conversation_handler.add_text_input(text, enhanced_metadata)
            return response
        else:
            return "Conversation handler is not available"
    
    def process_audio_data(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Process raw audio data for speech recognition.
        
        Args:
            audio_data: Raw audio data
            sample_rate: Sample rate of the audio
            
        Returns:
            Dictionary with recognition results
        """
        if not self.is_active:
            logger.warning("Cannot process audio: Conversation integration is not active")
            return {"error": "Conversation system is not active"}
        
        # Process through speech recognition
        speech_recognition = self.components.get('speech_recognition')
        if speech_recognition:
            result = speech_recognition.process_audio_data(audio_data, sample_rate)
            
            # If speech was recognized, also process through conversation handler
            if 'text' in result and result['text']:
                conversation_handler = self.components.get('conversation_handler')
                if conversation_handler:
                    response = conversation_handler.add_text_input(result['text'], {
                        'source': 'audio_upload',
                        'confidence': result.get('confidence', 0.0),
                        'audio_length': result.get('audio_length', 0.0)
                    })
                    
                    result['response'] = response
            
            return result
        else:
            return {"error": "Speech recognition is not available"}
    
    def process_eye_tracking(self, gaze_x: float, gaze_y: float, 
                           blink_detected: bool = False,
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process eye tracking data.
        
        Args:
            gaze_x: X-coordinate of gaze (0.0-1.0, 0.5 is center)
            gaze_y: Y-coordinate of gaze (0.0-1.0, 0.5 is center)
            blink_detected: Whether a blink was detected
            metadata: Additional metadata
            
        Returns:
            Dictionary with processing results
        """
        if not self.is_active:
            logger.warning("Cannot process eye tracking: Conversation integration is not active")
            return {"error": "Conversation system is not active"}
        
        if metadata is None:
            metadata = {}
        
        # Create analysis dictionary
        analysis = {
            'gaze_x': gaze_x,
            'gaze_y': gaze_y,
            'blink_detected': blink_detected,
            **metadata
        }
        
        # Add derived information
        if gaze_x < 0.35:
            analysis['gaze_direction'] = 'left'
        elif gaze_x > 0.65:
            analysis['gaze_direction'] = 'right'
        else:
            analysis['gaze_direction'] = 'center'
        
        if gaze_y < 0.35:
            analysis['gaze_vertical'] = 'up'
        elif gaze_y > 0.65:
            analysis['gaze_vertical'] = 'down'
        else:
            analysis['gaze_vertical'] = 'middle'
        
        # Process through nonverbal input handler
        self._handle_nonverbal_input(analysis)
        
        return {"status": "processed", "analysis": analysis}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the conversation integration.
        
        Returns:
            Dictionary with status information
        """
        speech_recognition = self.components.get('speech_recognition')
        conversation_handler = self.components.get('conversation_handler')
        
        status = {
            "is_active": self.is_active,
            "components": {
                "alphavox": "loaded" if 'alphavox' in self.components else "not_loaded",
                "conversation_engine": "loaded" if 'conversation_engine' in self.components else "not_loaded",
                "speech_recognition": "loaded" if speech_recognition else "not_loaded",
                "conversation_handler": "loaded" if conversation_handler else "not_loaded",
                "lstm_interpreter": "loaded" if 'lstm_interpreter' in self.components else "not_loaded"
            }
        }
        
        # Add component-specific status
        if speech_recognition:
            status["speech_recognition"] = speech_recognition.get_recognition_status()
        
        return status


# Create singleton instance
_conversation_integration = None

def get_conversation_integration(user_id: str = "default_user"):
    """Get the singleton instance of the conversation integration"""
    global _conversation_integration
    if _conversation_integration is None:
        _conversation_integration = ConversationIntegration(user_id)
    return _conversation_integration


# If running directly, start the integration
if __name__ == "__main__":
    integration = get_conversation_integration()
    integration.start()
    
    # Keep running until interrupted
    try:
        logger.info("Conversation integration running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping conversation integration...")
        integration.stop()
        logger.info("Conversation integration stopped")