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
AlphaVox - Complete Conversation Handler
---------------------------------------
This module provides a comprehensive conversation handling system that integrates
various input modalities (text, speech, eye tracking, gestures) and maintains
context throughout a complete conversation.

The handler coordinates between:
- Speech recognition for audio input
- Text processing
- Nonverbal cue interpretation
- Response generation
- Conversation state management
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional, Callable, Tuple, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationContext:
    """
    Class to store and manage conversation context.
    
    Tracks:
    - Conversation history
    - Recent topics
    - User preferences
    - Emotional states
    - Active references
    """
    
    def __init__(self):
        """Initialize the conversation context"""
        self.history = []
        self.recent_topics = []
        self.user_preferences = {}
        self.current_emotion = "neutral"
        self.references = {}
        self.last_update_time = time.time()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender ('user', 'system', 'assistant')
            content: Text content of the message
            metadata: Optional metadata associated with the message
        """
        if metadata is None:
            metadata = {}
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata
        }
        
        self.history.append(message)
        self.last_update_time = time.time()
        
        # Update recent topics if applicable
        if 'topic' in metadata:
            self.add_topic(metadata['topic'])
    
    def add_topic(self, topic: str):
        """
        Add a topic to the recent topics list.
        
        Args:
            topic: Topic to add
        """
        # Add to front of list (most recent)
        self.recent_topics.insert(0, topic)
        
        # Keep only the 5 most recent topics
        self.recent_topics = self.recent_topics[:5]
    
    def set_emotion(self, emotion: str):
        """
        Set the current emotional context.
        
        Args:
            emotion: Current emotion ('happy', 'sad', 'neutral', etc.)
        """
        self.current_emotion = emotion
        self.last_update_time = time.time()
    
    def add_reference(self, key: str, value: Any):
        """
        Add a reference to the context.
        
        Args:
            key: Reference identifier
            value: Reference value
        """
        self.references[key] = value
        self.last_update_time = time.time()
    
    def get_recent_history(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent conversation history.
        
        Args:
            count: Number of recent messages to retrieve
        
        Returns:
            List of recent messages
        """
        return self.history[-count:] if len(self.history) >= count else self.history
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Get the entire context as a dictionary.
        
        Returns:
            Dictionary representation of the context
        """
        return {
            'history': self.history,
            'recent_topics': self.recent_topics,
            'user_preferences': self.user_preferences,
            'current_emotion': self.current_emotion,
            'references': self.references,
            'last_update_time': self.last_update_time
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """
        Load context from a dictionary.
        
        Args:
            data: Dictionary containing context data
        """
        self.history = data.get('history', [])
        self.recent_topics = data.get('recent_topics', [])
        self.user_preferences = data.get('user_preferences', {})
        self.current_emotion = data.get('current_emotion', 'neutral')
        self.references = data.get('references', {})
        self.last_update_time = data.get('last_update_time', time.time())


class CompleteConversationHandler:
    """
    Handler for managing complete conversations with integrated modalities.
    
    This class:
    - Coordinates between different input/output modalities
    - Maintains conversation context
    - Manages conversation state and flow
    - Handles interruptions and context switching
    - Provides a unified interface for all conversation functionalities
    """
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize the conversation handler.
        
        Args:
            user_id: Identifier for the current user
        """
        self.user_id = user_id
        self.context = ConversationContext()
        self.active = False
        self.input_callbacks = []
        self.output_callbacks = []
        self.on_conversation_end_callbacks = []
        
        # Initialize components as needed
        self._initialize_components()
        
        logger.info(f"Complete Conversation Handler initialized for user: {user_id}")
    
    def _initialize_components(self):
        """Initialize the required components"""
        try:
            # Import components lazily to avoid circular imports
            from speech_recognition_engine import get_speech_recognition_engine
            from conversation_engine import ConversationEngine
            from alphavox import alphavox
            
            # Store component references
            self.speech_engine = get_speech_recognition_engine()
            self.conversation_engine = alphavox.conversation_engine
            
            logger.info("All conversation components initialized successfully")
        except ImportError as e:
            logger.warning(f"Could not initialize all components: {e}")
            logger.warning("Some features may be limited")
    
    def start_conversation(self) -> bool:
        """
        Start a new conversation.
        
        Returns:
            True if conversation started successfully, False otherwise
        """
        if self.active:
            logger.warning("Conversation is already active")
            return False
        
        # Reset context for new conversation
        self.context = ConversationContext()
        
        # Start the speech recognition if available
        try:
            self.speech_engine.start_listening(callback=self._handle_speech_input)
        except Exception as e:
            logger.warning(f"Could not start speech recognition: {e}")
        
        # Mark conversation as active
        self.active = True
        
        # Add system message to history
        self.context.add_message(
            'system',
            'Conversation started',
            {'event': 'conversation_start'}
        )
        
        logger.info("Conversation started")
        return True
    
    def end_conversation(self) -> bool:
        """
        End the current conversation.
        
        Returns:
            True if conversation ended successfully, False otherwise
        """
        if not self.active:
            logger.warning("No active conversation to end")
            return False
        
        # Stop speech recognition if it was started
        try:
            self.speech_engine.stop_listening()
        except Exception as e:
            logger.warning(f"Error stopping speech recognition: {e}")
        
        # Mark conversation as inactive
        self.active = False
        
        # Add system message to history
        self.context.add_message(
            'system',
            'Conversation ended',
            {'event': 'conversation_end'}
        )
        
        # Notify all registered end callbacks
        for callback in self.on_conversation_end_callbacks:
            try:
                callback(self.context.as_dict())
            except Exception as e:
                logger.error(f"Error in conversation end callback: {e}")
        
        logger.info("Conversation ended")
        return True
    
    def add_text_input(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add text input to the conversation.
        
        Args:
            text: Text input from the user
            metadata: Optional metadata related to the input
        
        Returns:
            Response text
        """
        if not self.active:
            logger.warning("No active conversation for text input")
            return "No active conversation. Please start a conversation first."
        
        if metadata is None:
            metadata = {}
        
        # Add user message to history
        self.context.add_message('user', text, metadata)
        
        # Process the input
        response = self._process_input(text, metadata)
        
        return response
    
    def _handle_speech_input(self, text: str, confidence: float, metadata: Dict[str, Any]):
        """
        Handle speech input from the speech recognition engine.
        
        Args:
            text: Recognized text
            confidence: Confidence score
            metadata: Additional metadata from recognition
        """
        if not self.active or not text:
            return
        
        # Combine metadata with speech-specific info
        combined_metadata = {
            'source': 'speech',
            'confidence': confidence,
            **metadata
        }
        
        # Process like a text input
        response = self.add_text_input(text, combined_metadata)
        
        # Use text-to-speech for the response
        try:
            from app import text_to_speech
            text_to_speech(response)
        except Exception as e:
            logger.error(f"Could not generate speech response: {e}")
    
    def add_nonverbal_input(self, analysis: Dict[str, Any]) -> str:
        """
        Add nonverbal input to the conversation.
        
        Args:
            analysis: Analysis of nonverbal cues (eye tracking, gestures, etc.)
        
        Returns:
            Response text
        """
        if not self.active:
            logger.warning("No active conversation for nonverbal input")
            return "No active conversation. Please start a conversation first."
        
        # Update emotional context if available
        if 'emotion' in analysis:
            self.context.set_emotion(analysis['emotion'])
        
        # Add as system message to history
        self.context.add_message(
            'system',
            f"Nonverbal input detected: {analysis}",
            {'source': 'nonverbal', 'analysis': analysis}
        )
        
        # Process through conversation engine
        try:
            response = self.conversation_engine.get_response(analysis)
            
            # Add assistant message to history
            self.context.add_message('assistant', response, {'source': 'nonverbal_response'})
            
            return response
        except Exception as e:
            logger.error(f"Error processing nonverbal input: {e}")
            return "I'm having trouble understanding your nonverbal cues right now."
    
    def _process_input(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        Process text input and generate a response.
        
        Args:
            text: Input text
            metadata: Input metadata
        
        Returns:
            Response text
        """
        # Call input callbacks
        for callback in self.input_callbacks:
            try:
                # Allow callbacks to modify the input
                result = callback(text, metadata, self.context)
                if result:
                    text, metadata = result
            except Exception as e:
                logger.error(f"Error in input callback: {e}")
        
        # Generate a response
        response = ""
        
        try:
            # First check if we have a domain-specific query for academic response
            if any(keyword in text.lower() for keyword in [
                'explain', 'what is', 'how does', 'definition', 'describe', 'science',
                'mathematics', 'history', 'research', 'study', 'theory'
            ]):
                # This might be an academic query
                topic = text.lower().replace('what is', '').replace('explain', '').replace('how does', '').strip()
                response = self.conversation_engine.get_academic_response(topic)
            else:
                # General conversational response
                # Create an analysis object from the text
                analysis = {
                    'content': text,
                    'emotion': self.context.current_emotion,
                    'gaze_direction': 'center',  # Default
                    'blink_detected': False      # Default
                }
                
                # Add any additional metadata from input
                analysis.update(metadata)
                
                # Get response from conversation engine
                response = self.conversation_engine.get_response(analysis)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response = "I'm having trouble processing that right now. Can you rephrase?"
        
        # Add assistant message to history
        self.context.add_message('assistant', response, {'source': 'text_response'})
        
        # Call output callbacks
        for callback in self.output_callbacks:
            try:
                callback(response, self.context)
            except Exception as e:
                logger.error(f"Error in output callback: {e}")
        
        return response
    
    def register_input_callback(self, callback: Callable[[str, Dict[str, Any], ConversationContext], Optional[Tuple[str, Dict[str, Any]]]]):
        """
        Register a callback for processing input.
        
        Args:
            callback: Function to call when processing input
                     The function should accept (text, metadata, context) and optionally return (modified_text, modified_metadata)
        """
        self.input_callbacks.append(callback)
    
    def register_output_callback(self, callback: Callable[[str, ConversationContext], None]):
        """
        Register a callback for processing output.
        
        Args:
            callback: Function to call when generating output
                     The function should accept (response, context)
        """
        self.output_callbacks.append(callback)
    
    def register_conversation_end_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback for when a conversation ends.
        
        Args:
            callback: Function to call when conversation ends
                     The function should accept (context_dict)
        """
        self.on_conversation_end_callbacks.append(callback)
    
    def save_context(self) -> Dict[str, Any]:
        """
        Save the current conversation context.
        
        Returns:
            Dictionary containing the serialized context
        """
        return self.context.as_dict()
    
    def load_context(self, context_data: Dict[str, Any]) -> bool:
        """
        Load a previously saved conversation context.
        
        Args:
            context_data: Dictionary containing the context data
        
        Returns:
            True if context was loaded successfully, False otherwise
        """
        try:
            self.context.from_dict(context_data)
            return True
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            return False


# Singleton instance
_conversation_handler = None

def get_conversation_handler(user_id: str = "default_user") -> CompleteConversationHandler:
    """
    Get the singleton instance of the conversation handler.
    
    Args:
        user_id: User identifier
    
    Returns:
        CompleteConversationHandler instance
    """
    global _conversation_handler
    if _conversation_handler is None:
        _conversation_handler = CompleteConversationHandler(user_id)
    elif _conversation_handler.user_id != user_id:
        # If user ID is different, create a new handler
        _conversation_handler = CompleteConversationHandler(user_id)
    return _conversation_handler