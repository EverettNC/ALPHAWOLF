"""
AlphaWolf Brain - Unified Cognitive Care System
Part of The Christman AI Project - Powered by LumaCognify AI

This module integrates:
- Derek C's advanced conversational intelligence
- AlphaWolf's dementia care specialization
- Memory and learning systems
- Self-improvement capabilities

Mission: "How can we help you love yourself more?"
Because no one should lose their memories—or their dignity.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Import core components
try:
    from core.memory_engine import MemoryEngine
    logger.info("✅ MemoryEngine imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import MemoryEngine: {e}")
    # Create fallback
    class MemoryEngine:
        def __init__(self, file_path):
            self.file_path = file_path
            self._memory = []
        def save(self, entry): pass
        def query(self, text, intent=None): return {"context": ""}

try:
    from core.conversation_engine import ConversationEngine
    logger.info("✅ ConversationEngine imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import ConversationEngine: {e}")
    ConversationEngine = None

try:
    from core.ai_learning_engine import (
        SelfImprovementEngine,
        get_self_improvement_engine,
        learn_from_text
    )
    logger.info("✅ AI Learning Engine imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import AI Learning Engine: {e}")
    SelfImprovementEngine = None
    learn_from_text = lambda x: None

try:
    from core.local_reasoning_engine import (
        LocalReasoningEngine,
        get_local_reasoning_engine
    )
    logger.info("✅ Local Reasoning Engine imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import Local Reasoning Engine: {e}")
    LocalReasoningEngine = None
    get_local_reasoning_engine = None


class AlphaWolfBrain:
    """
    The AlphaWolf Brain - A compassionate AI for cognitive care.
    
    Combines Derek C's intelligence with specialized dementia care features:
    - Memory support and reminiscence
    - Caregiver assistance
    - Patient safety monitoring
    - Adaptive learning from interactions
    - Self-improvement capabilities
    """
    
    def __init__(self, memory_path: str = "./memory/alphawolf_memory.json"):
        """Initialize the AlphaWolf brain system."""
        self.memory_path = memory_path
        os.makedirs(os.path.dirname(memory_path), exist_ok=True)
        
        # Core cognitive components
        self.memory_engine = MemoryEngine(file_path=memory_path)
        self.conversation_engine = ConversationEngine() if ConversationEngine else None
        self.learning_engine = None
        
        # LOCAL REASONING - The secret sauce for AI sovereignty
        self.local_reasoning = None
        if get_local_reasoning_engine:
            try:
                self.local_reasoning = get_local_reasoning_engine()
                logger.info("✅ Local reasoning engine initialized - AI sovereignty enabled")
            except Exception as e:
                logger.warning(f"⚠️ Local reasoning not available: {e}")
        
        # AlphaWolf-specific features
        self.patient_profiles = {}
        self.caregiver_mode = False
        self.safety_alerts = []
        
        # Emotional state tracking
        self.emotional_state = {
            "valence": 0.5,  # 0-1, negative to positive
            "arousal": 0.3,  # 0-1, calm to excited
            "empathy": 0.9,  # AlphaWolf is highly empathetic
        }
        
        # Initialize learning engine if available
        if SelfImprovementEngine:
            try:
                self.learning_engine = get_self_improvement_engine()
                logger.info("✅ AlphaWolf learning engine initialized")
            except Exception as e:
                logger.error(f"⚠️ Learning engine initialization failed: {e}")
        
        logger.info(f"🐺 AlphaWolf Brain initialized with memory at: {memory_path}")
        logger.info("💙 Mission active: Cognitive support with dignity and care")
    
    def generate_greeting(self) -> str:
        """Generate a warm, welcoming greeting."""
        greetings = [
            "Hello! I'm AlphaWolf, here to support you with care and understanding.",
            "Welcome! I'm here to help you maintain your independence and dignity.",
            "Hi there! Ready to support you on your journey today.",
        ]
        import random
        return random.choice(greetings)
    
    def think(self, input_text: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process input and generate a thoughtful, caring response.
        
        Args:
            input_text: User's input (text, voice transcript, etc.)
            user_context: Additional context (user_id, patient_info, location, etc.)
        
        Returns:
            dict: Response with message, intent, emotion, and actions
        """
        logger.info(f"🧠 AlphaWolf thinking: {input_text[:100]}...")
        
        context = user_context or {}
        
        # Check for emergency keywords (with context sensitivity)
        emergency_phrases = [
            'help me', "i've fallen", 'fallen and', 'emergency', 
            'call 911', 'call ambulance', 'cant breathe', "can't breathe",
            'chest pain', 'very scared', 'really scared', 'im lost', "i'm lost"
        ]
        is_emergency = any(phrase in input_text.lower() for phrase in emergency_phrases)
        
        if is_emergency:
            return self._handle_emergency(input_text, context)
        
        # STEP 1: LOCAL REASONING (Privacy-first, no cloud needed)
        local_thought = None
        if self.local_reasoning:
            try:
                # Get relevant memory context
                memory_context = memory_result.get('context', '')
                
                # Get emotional state if available
                emotion = context.get('emotion', '')
                
                # Get visual context if available  
                vision = context.get('vision', '')
                
                # Generate local reasoning (NO API CALL)
                local_thought = self.local_reasoning.analyze(
                    user_input=input_text,
                    memory=memory_context,
                    emotion=emotion,
                    vision=vision
                )
                
                logger.info(f"🧠 Local reasoning: {local_thought[:100]}...")
                
            except Exception as e:
                logger.warning(f"⚠️ Local reasoning failed: {e}")
        
        # STEP 2: OPTIONAL CLOUD ENHANCEMENT (if conversation engine available)
        cloud_response = None
        if self.conversation_engine:
            try:
                cloud_response = self.conversation_engine.process_text(
                    input_text,
                    user_id=context.get('user_id'),
                    context=context
                )
                
                # If we have both local and cloud reasoning, merge them
                if local_thought and cloud_response:
                    merged_message = self.local_reasoning.merge_thoughts(
                        internal=local_thought,
                        external=cloud_response.get('message', '')
                    )
                    cloud_response['message'] = merged_message
                    cloud_response['reasoning_mode'] = 'hybrid'
                
                response = cloud_response
                
                # Enhance response with AlphaWolf care features
                response = self._enhance_with_care(response, context)
                
                # Log interaction for learning
                if self.learning_engine:
                    self.learning_engine.register_interaction(
                        'text',
                        {
                            'input': input_text,
                            'output': response.get('message'),
                            'intent': response.get('intent'),
                            'success': True,
                            'confidence': response.get('confidence', 0.8)
                        }
                    )
                
                return response
                
            except Exception as e:
                logger.error(f"❌ Conversation processing error: {e}")
                # Fall through to local-only response
        
        # STEP 3: LOCAL-ONLY FALLBACK (if no cloud or cloud failed)
        if local_thought:
            response = {
                'status': 'success',
                'message': local_thought,
                'intent': 'local_reasoning',
                'confidence': 0.75,
                'expression': 'supportive',
                'reasoning_mode': 'local_only',
                'privacy_preserved': True
            }
            response = self._enhance_with_care(response, context)
            return response
        
        # STEP 4: ABSOLUTE FALLBACK (if everything failed)
        return self._fallback_response(input_text, context)
    
    def _handle_emergency(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency situations with immediate response."""
        logger.warning(f"🚨 EMERGENCY detected: {input_text}")
        
        # Create alert
        alert = {
            'timestamp': datetime.now().isoformat(),
            'message': input_text,
            'user_id': context.get('user_id'),
            'location': context.get('location'),
            'type': 'emergency'
        }
        self.safety_alerts.append(alert)
        
        return {
            'status': 'emergency',
            'message': "I understand this is urgent. I'm alerting your caregiver right now. Help is on the way. You're not alone.",
            'intent': 'emergency_response',
            'confidence': 1.0,
            'expression': 'urgent',
            'actions': [
                {'type': 'alert_caregiver', 'alert': alert},
                {'type': 'log_emergency', 'alert': alert}
            ]
        }
    
    def _enhance_with_care(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance response with AlphaWolf's caring touch."""
        # Add memory prompts for dementia patients
        if context.get('patient_type') == 'dementia':
            response['care_notes'] = [
                "Speaking slowly and clearly",
                "Maintaining eye contact",
                "Using simple, familiar words"
            ]
        
        # Add encouragement
        if response.get('intent') in ['help', 'request_info']:
            original_message = response.get('message', '')
            response['message'] = f"{original_message} I'm here to support you every step of the way."
        
        return response
    
    def _fallback_response(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a caring fallback response."""
        return {
            'status': 'success',
            'message': "I hear you. Could you tell me a bit more about what you need? I'm here to help.",
            'intent': 'clarification',
            'confidence': 0.6,
            'expression': 'supportive',
            'emotion_tier': 'mild'
        }
    
    def learn_from_interaction(self, interaction_data: Dict[str, Any]):
        """Learn from patient/caregiver interactions."""
        try:
            # Save to memory
            self.memory_engine.save(interaction_data)
            
            # Use learning engine if available
            if self.learning_engine:
                self.learning_engine.register_interaction(
                    interaction_data.get('type', 'general'),
                    interaction_data
                )
            
            logger.info(f"✅ AlphaWolf learned from interaction")
        except Exception as e:
            logger.error(f"❌ Learning failed: {e}")
    
    def learn_from_research(self, text: str) -> str:
        """Ingest research, best practices, and care guidelines."""
        try:
            result = learn_from_text(text)
            logger.info(f"📚 AlphaWolf ingested research: {len(text)} chars")
            return result
        except Exception as e:
            logger.error(f"❌ Research ingestion failed: {e}")
            return "Research ingestion failed"
    
    def start_learning_systems(self):
        """Activate autonomous learning and self-improvement."""
        if self.learning_engine:
            try:
                self.learning_engine.start_learning()
                logger.info("🎓 AlphaWolf learning systems activated")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to start learning: {e}")
                return False
        else:
            logger.warning("⚠️ Learning engine not available")
            return False
    
    def stop_learning_systems(self):
        """Deactivate learning systems."""
        if self.learning_engine:
            self.learning_engine.stop_learning()
            logger.info("🛑 AlphaWolf learning systems stopped")
    
    def get_emotional_state(self) -> Dict[str, float]:
        """Get current emotional state."""
        if self.conversation_engine:
            return self.conversation_engine.get_emotional_state()
        return self.emotional_state
    
    def get_safety_alerts(self) -> List[Dict[str, Any]]:
        """Get recent safety alerts."""
        return self.safety_alerts[-10:]  # Last 10 alerts
    
    def create_patient_profile(self, patient_id: str, profile_data: Dict[str, Any]):
        """Create or update a patient profile."""
        self.patient_profiles[patient_id] = {
            **profile_data,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        logger.info(f"👤 Patient profile created/updated: {patient_id}")
    
    def get_patient_profile(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient profile."""
        return self.patient_profiles.get(patient_id)
    
    def save_state(self):
        """Save current state to disk."""
        try:
            state_file = self.memory_path.replace('.json', '_state.json')
            state = {
                'patient_profiles': self.patient_profiles,
                'emotional_state': self.emotional_state,
                'safety_alerts': self.safety_alerts[-100:],  # Keep last 100
                'last_saved': datetime.now().isoformat()
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"💾 AlphaWolf state saved to {state_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")
    
    def load_state(self):
        """Load saved state from disk."""
        try:
            state_file = self.memory_path.replace('.json', '_state.json')
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                self.patient_profiles = state.get('patient_profiles', {})
                self.emotional_state = state.get('emotional_state', self.emotional_state)
                self.safety_alerts = state.get('safety_alerts', [])
                logger.info(f"📂 AlphaWolf state loaded from {state_file}")
        except Exception as e:
            logger.error(f"❌ Failed to load state: {e}")


# Global instance
_alphawolf_brain = None


def get_alphawolf_brain() -> AlphaWolfBrain:
    """Get or create the global AlphaWolf brain instance."""
    global _alphawolf_brain
    if _alphawolf_brain is None:
        _alphawolf_brain = AlphaWolfBrain()
        _alphawolf_brain.load_state()
    return _alphawolf_brain


def initialize_alphawolf(memory_path: Optional[str] = None) -> AlphaWolfBrain:
    """Initialize AlphaWolf brain system."""
    global _alphawolf_brain
    if memory_path:
        _alphawolf_brain = AlphaWolfBrain(memory_path)
    else:
        _alphawolf_brain = AlphaWolfBrain()
    _alphawolf_brain.load_state()
    logger.info("🐺 AlphaWolf system initialized and ready")
    return _alphawolf_brain


if __name__ == "__main__":
    # Test the brain
    print("="*60)
    print("🐺 AlphaWolf Brain - Self Test")
    print("Part of The Christman AI Project")
    print("="*60)
    
    brain = AlphaWolfBrain()
    
    print(f"\n💬 Greeting: {brain.generate_greeting()}")
    
    # Test thinking
    print("\n🧠 Testing cognitive response...")
    response = brain.think("Hello, can you help me remember to take my medication?")
    print(f"Response: {response.get('message')}")
    print(f"Intent: {response.get('intent')}")
    print(f"Confidence: {response.get('confidence')}")
    
    # Test emergency
    print("\n🚨 Testing emergency response...")
    emergency = brain.think("Help! I've fallen and I'm scared!")
    print(f"Emergency Response: {emergency.get('message')}")
    print(f"Status: {emergency.get('status')}")
    
    # Test learning
    print("\n📚 Testing learning from research...")
    research_text = "Dementia patients benefit from routine, familiar environments, and patient communication."
    result = brain.learn_from_research(research_text)
    print(f"Learning result: {result}")
    
    print("\n✅ AlphaWolf Brain self-test complete!")
    print("💙 System ready to provide cognitive care with dignity")
