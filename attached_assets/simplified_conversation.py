"""
AlphaVox - Simplified Conversation Handler
----------------------------------------
This module provides a simplified conversation interface for AlphaVox.
It integrates speech recognition, text processing, and knowledge retrieval
to create a responsive and adaptive conversation experience.
"""

import os
import time
import json
import logging
import random
import datetime
from typing import Dict, Any, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import knowledge engine for self-education capabilities
from knowledge_engine import get_knowledge_engine, get_random_fact, process_expertise_query

# Constants
CONVERSATION_DIR = "data/conversations"
os.makedirs(CONVERSATION_DIR, exist_ok=True)

class SimplifiedConversation:
    """
    Simplified conversation handler that integrates knowledge retrieval
    and basic conversation capabilities.
    """
    
    def __init__(self, conversation_id: Optional[str] = None):
        """Initialize the conversation handler"""
        self.conversation_id = conversation_id or f"conversation_{int(time.time())}"
        self.history = []
        self.stats = {
            "total_interactions": 0,
            "text_interactions": 0,
            "speech_interactions": 0,
            "knowledge_queries": 0,
            "started_at": datetime.datetime.now().isoformat()
        }
        self._load_history()
    
    def _load_history(self):
        """Load conversation history if it exists"""
        history_file = os.path.join(CONVERSATION_DIR, f"{self.conversation_id}.json")
        stats_file = os.path.join(CONVERSATION_DIR, f"{self.conversation_id}_stats.json")
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading conversation history: {e}")
        
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    self.stats = json.load(f)
            except Exception as e:
                logger.error(f"Error loading conversation stats: {e}")
    
    def _save_history(self):
        """Save conversation history and stats"""
        history_file = os.path.join(CONVERSATION_DIR, f"{self.conversation_id}.json")
        stats_file = os.path.join(CONVERSATION_DIR, f"{self.conversation_id}_stats.json")
        
        try:
            with open(history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving conversation data: {e}")
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text input and generate a response
        
        Args:
            text: The user's input text
            
        Returns:
            Dictionary with response data
        """
        # Update stats
        self.stats["total_interactions"] += 1
        self.stats["text_interactions"] += 1
        
        # Record in history
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "type": "text",
            "input": text,
            "response": None  # Will be filled after processing
        }
        
        # Process the input
        if self._is_knowledge_query(text):
            self.stats["knowledge_queries"] += 1
            response = self._handle_knowledge_query(text)
            entry["response_type"] = "knowledge"
        else:
            response = self._handle_conversation(text)
            entry["response_type"] = "conversation"
        
        # Record the response
        entry["response"] = response
        self.history.append(entry)
        
        # Save the updated history
        self._save_history()
        
        return response
    
    def process_speech(self, transcript: str, confidence: float) -> Dict[str, Any]:
        """
        Process speech input and generate a response
        
        Args:
            transcript: The transcribed speech
            confidence: The confidence score (0-1)
            
        Returns:
            Dictionary with response data
        """
        # Update stats
        self.stats["total_interactions"] += 1
        self.stats["speech_interactions"] += 1
        
        # Record in history
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "type": "speech",
            "input": transcript,
            "confidence": confidence,
            "response": None  # Will be filled after processing
        }
        
        # Process the input
        if self._is_knowledge_query(transcript):
            self.stats["knowledge_queries"] += 1
            response = self._handle_knowledge_query(transcript)
            entry["response_type"] = "knowledge"
        else:
            response = self._handle_conversation(transcript)
            entry["response_type"] = "conversation"
        
        # Record the response
        entry["response"] = response
        self.history.append(entry)
        
        # Save the updated history
        self._save_history()
        
        return response
    
    def _is_knowledge_query(self, text: str) -> bool:
        """
        Determine if the input is a knowledge query
        
        Args:
            text: The input text to analyze
            
        Returns:
            True if it's a knowledge query, False otherwise
        """
        # For simplicity, we'll check for question-related patterns
        text_lower = text.lower()
        
        # Check for question words
        question_indicators = [
            "what", "how", "why", "when", "where", "who", "tell me about",
            "explain", "describe", "information on", "facts about"
        ]
        
        # Check for knowledge-related topics
        knowledge_topics = [
            "communication", "nonverbal", "eye contact", "body language",
            "facial expression", "gesture", "autism", "assistive", "therapy",
            "augmentative", "alternative", "speech", "learn", "know", "educate"
        ]
        
        # Check if it's a question about AlphaVox's knowledge
        alphavox_knowledge_indicators = [
            "what do you know", "tell me what you know", "what have you learned",
            "how much do you know", "what are you learning about", "your knowledge",
            "have you learned", "what topics", "educate yourself", "teach yourself"
        ]
        
        # Check for direct indicators
        for indicator in alphavox_knowledge_indicators:
            if indicator in text_lower:
                return True
        
        # Check for question pattern + knowledge topic
        for q_indicator in question_indicators:
            if q_indicator in text_lower:
                for topic in knowledge_topics:
                    if topic in text_lower:
                        return True
        
        # If it ends with a question mark and contains a knowledge topic
        if text.endswith("?"):
            for topic in knowledge_topics:
                if topic in text_lower:
                    return True
        
        return False
    
    def _handle_knowledge_query(self, query: str) -> Dict[str, Any]:
        """
        Handle a knowledge query by retrieving information
        
        Args:
            query: The knowledge query
            
        Returns:
            Response data
        """
        # Use the knowledge engine to process the query
        result = process_expertise_query(query)
        
        # Format the response
        text = result["response_text"]
        facts = result["facts"]
        learning_status = result["learning_status"]
        
        # Build the response with facts
        response_text = f"{text}\n\n"
        for i, fact in enumerate(facts, 1):
            response_text += f"{i}. {fact}\n"
        
        # Add information about learning progress
        response_text += f"\n{learning_status}"
        
        # Get knowledge metrics to show learning progress
        engine = get_knowledge_engine()
        metrics = engine.get_learning_metrics()
        
        return {
            "text": response_text,
            "type": "knowledge",
            "facts": facts,
            "learning_status": learning_status,
            "facts_learned": metrics["facts_learned"],
            "topics_explored": metrics["topics_explored"]
        }
    
    def _handle_conversation(self, text: str) -> Dict[str, Any]:
        """
        Handle a general conversation input
        
        Args:
            text: The user's input
            
        Returns:
            Response data
        """
        # Simple pattern matching for demo purposes
        text_lower = text.lower()
        
        # Greeting patterns
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        for greeting in greetings:
            if greeting in text_lower:
                return {
                    "text": f"{random.choice(greetings).capitalize()}! How can I help you today? I've been learning about communication topics. Feel free to ask me what I know!",
                    "type": "conversation"
                }
        
        # Questions about AlphaVox
        if any(q in text_lower for q in ["who are you", "what are you", "about you", "your name"]):
            return {
                "text": "I'm AlphaVox, an AI assistant that can educate itself about communication topics. I continuously learn new information and can share what I've learned with you. Ask me what I know about nonverbal communication or any related topic!",
                "type": "conversation"
            }
        
        # Learning-related questions
        if any(q in text_lower for q in ["do you learn", "are you learning", "can you learn", "self learning"]):
            engine = get_knowledge_engine()
            metrics = engine.get_learning_metrics()
            return {
                "text": f"Yes! I'm designed to educate myself. So far, I've learned {metrics['facts_learned']} facts across {metrics['topics_explored']} topics related to communication. I'm continuously gathering new information from various sources.",
                "type": "conversation",
                "metrics": metrics
            }
        
        # Default: share a random fact to demonstrate learning
        fact = get_random_fact()
        return {
            "text": f"That's interesting! Did you know? {fact}\n\nI'm always learning new things. Feel free to ask me about what I know regarding communication topics.",
            "type": "conversation",
            "random_fact": fact
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics and metrics"""
        # Update with latest data from knowledge engine
        engine = get_knowledge_engine()
        learning_metrics = engine.get_learning_metrics()
        
        # Combine with conversation stats
        stats = self.stats.copy()
        stats["learning_metrics"] = learning_metrics
        stats["last_updated"] = datetime.datetime.now().isoformat()
        
        return stats


# Singleton instance
_conversation = None

def get_simplified_conversation() -> SimplifiedConversation:
    """Get the singleton conversation instance"""
    global _conversation
    if _conversation is None:
        _conversation = SimplifiedConversation()
    return _conversation