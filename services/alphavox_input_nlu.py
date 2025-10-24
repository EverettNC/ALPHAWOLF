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
import logging
import json
import re
import numpy as np
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class AlphaVoxInputProcessor:
    """Service for processing multimodal inputs including gestures, voice, and eye tracking."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gesture_types = ['HandUp', 'HandWave', 'PointingLeft', 'PointingRight', 'Clapping', 'None']
        self.intents = {
            'request_help': {
                'patterns': [
                    r'help( me)?',
                    r'need (some )?assistance',
                    r'can(| yo)u help( me)?',
                    r'i(| a)m (confused|lost)',
                    r'don\'t understand'
                ],
                'gestures': ['HandUp', 'Clapping'],
                'priority': 'high'
            },
            'set_reminder': {
                'patterns': [
                    r'remind me (to|about) (.+)',
                    r'set( a)? reminder (for|to) (.+)',
                    r'don\'t (let me )?forget to (.+)'
                ],
                'gestures': [],
                'priority': 'medium'
            },
            'current_location': {
                'patterns': [
                    r'where am i',
                    r'(what|which) (place|location) (is this|am i in)',
                    r'(i\'m|i am) lost',
                    r'(help me )?find (my way|the way) (home|back)'
                ],
                'gestures': ['PointingLeft', 'PointingRight'],
                'priority': 'high'
            },
            'cognitive_exercise': {
                'patterns': [
                    r'(start|play|do)( a)? (game|exercise)',
                    r'(show|give) me (a |an |some )?(exercise|game|puzzle)',
                    r'i want to (play|practice)',
                    r'(help|train) (my )?brain'
                ],
                'gestures': [],
                'priority': 'low'
            },
            'call_caregiver': {
                'patterns': [
                    r'call (my )?(caregiver|family|son|daughter|wife|husband)',
                    r'contact (my )?(caregiver|family|son|daughter|wife|husband)',
                    r'i need (my )?(caregiver|family|son|daughter|wife|husband)',
                    r'help me (call|reach) (my )?(caregiver|family)'
                ],
                'gestures': ['HandWave'],
                'priority': 'high'
            },
            'daily_schedule': {
                'patterns': [
                    r'what(.+)on (my )?schedule',
                    r'what(.+)(planned|happening) today',
                    r'(show|tell) me my (appointments|schedule)',
                    r'do i have any (appointments|plans) today'
                ],
                'gestures': [],
                'priority': 'medium'
            },
            'medication_reminder': {
                'patterns': [
                    r'(did i|have i) (take|taken) (my )?medication',
                    r'remind me (about|to take) (my )?medication',
                    r'when (is|was) (my )?medication (scheduled|due)',
                    r'(which|what) medication (do i|should i) take'
                ],
                'gestures': [],
                'priority': 'high'
            }
        }
        
        # Load context data if available
        self.context_path = os.path.join('data', 'input_context.pkl')
        self.context_data = {}
        
        try:
            if os.path.exists(self.context_path):
                import joblib
                self.context_data = joblib.load(self.context_path)
                self.logger.info(f"Loaded input context data from {self.context_path}")
        except Exception as e:
            self.logger.error(f"Error loading input context data: {str(e)}")
        
        self.logger.info("AlphaVox Input Processor initialized")
    
    def process_input(self, input_data):
        """
        Process multimodal input from various sources.
        
        Args:
            input_data: Dict containing input data from different modalities
                {
                    'text': Optional text input,
                    'gesture': Optional gesture data,
                    'gaze': Optional eye tracking data,
                    'location': Optional location data,
                    'context': Optional contextual information
                }
            
        Returns:
            dict: Processed input with intent and parameters
        """
        try:
            # Extract data from input
            text = input_data.get('text', '')
            gesture = input_data.get('gesture', None)
            gaze = input_data.get('gaze', None)
            location = input_data.get('location', None)
            context = input_data.get('context', {})
            
            # Process text input
            text_analysis = self._process_text(text) if text else None
            
            # Process gesture input
            gesture_analysis = self._process_gesture(gesture) if gesture else None
            
            # Process eye tracking data
            gaze_analysis = self._process_gaze(gaze) if gaze else None
            
            # Merge all analyses to determine overall intent
            overall_intent = self._determine_intent(text_analysis, gesture_analysis, gaze_analysis, context)
            
            # Extract parameters for the intent
            parameters = self._extract_parameters(overall_intent, text, context)
            
            # Update interaction context
            self._update_context(overall_intent, parameters, location, context)
            
            return {
                'intent': overall_intent.get('intent', 'unknown'),
                'confidence': overall_intent.get('confidence', 0.0),
                'parameters': parameters,
                'text_analysis': text_analysis,
                'gesture_analysis': gesture_analysis,
                'gaze_analysis': gaze_analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error processing input: {str(e)}")
            return {
                'intent': 'error',
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _process_text(self, text):
        """Process and analyze text input."""
        text = text.lower().strip()
        intents_matched = {}
        
        # Check text against patterns for each intent
        for intent, config in self.intents.items():
            confidence = 0.0
            
            for pattern in config['patterns']:
                match = re.search(pattern, text)
                if match:
                    # Calculate confidence based on how much of the text matches the pattern
                    match_length = match.end() - match.start()
                    text_coverage = match_length / len(text) if len(text) > 0 else 0
                    pattern_confidence = 0.6 + (0.4 * text_coverage)
                    
                    # Take the highest confidence among pattern matches
                    confidence = max(confidence, pattern_confidence)
            
            if confidence > 0:
                intents_matched[intent] = confidence
        
        # Get the intent with highest confidence
        if intents_matched:
            best_intent = max(intents_matched.items(), key=lambda x: x[1])
            return {
                'intent': best_intent[0],
                'confidence': best_intent[1],
                'all_intents': intents_matched
            }
        else:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'all_intents': {}
            }
    
    def _process_gesture(self, gesture_data):
        """Process and analyze gesture input."""
        # If gesture_data is already classified, use it directly
        if isinstance(gesture_data, str) and gesture_data in self.gesture_types:
            gesture_type = gesture_data
            confidence = 1.0
        elif isinstance(gesture_data, dict) and 'type' in gesture_data:
            gesture_type = gesture_data['type']
            confidence = gesture_data.get('confidence', 1.0)
        else:
            # For unclassified gestures, we'd need a model
            # Here we'll just use a simple placeholder
            gesture_type = 'None'
            confidence = 0.0
        
        # Map gesture to potential intents
        potential_intents = {}
        for intent, config in self.intents.items():
            if gesture_type in config['gestures']:
                # Calculate intent confidence based on gesture confidence and priority
                priority_weight = 0.8 if config['priority'] == 'high' else 0.6 if config['priority'] == 'medium' else 0.4
                intent_confidence = confidence * priority_weight
                potential_intents[intent] = intent_confidence
        
        # Get the intent with highest confidence
        if potential_intents:
            best_intent = max(potential_intents.items(), key=lambda x: x[1])
            return {
                'gesture': gesture_type,
                'confidence': confidence,
                'intent': best_intent[0],
                'intent_confidence': best_intent[1],
                'all_intents': potential_intents
            }
        else:
            return {
                'gesture': gesture_type,
                'confidence': confidence,
                'intent': 'unknown',
                'intent_confidence': 0.0,
                'all_intents': {}
            }
    
    def _process_gaze(self, gaze_data):
        """Process and analyze eye tracking data."""
        # For now, this is a placeholder
        # Real implementation would analyze gaze patterns for attention, confusion, etc.
        
        if isinstance(gaze_data, dict):
            focus_point = gaze_data.get('focus_point', [0.5, 0.5])
            duration = gaze_data.get('duration', 0.0)
            intensity = gaze_data.get('intensity', 0.5)
            
            # Simple analysis of gaze data
            if duration > 2.0:  # Staring at something for more than 2 seconds
                attention = 'focused'
                confidence = min(1.0, duration / 5.0)  # Normalize to 0-1 range
            elif duration < 0.5:  # Very short gaze
                attention = 'distracted'
                confidence = min(1.0, (0.5 - duration) * 2)
            else:
                attention = 'normal'
                confidence = 0.5
            
            return {
                'attention': attention,
                'confidence': confidence,
                'focus_point': focus_point,
                'duration': duration,
                'intensity': intensity
            }
        else:
            return {
                'attention': 'unknown',
                'confidence': 0.0
            }
    
    def _determine_intent(self, text_analysis, gesture_analysis, gaze_analysis, context):
        """Determine overall intent by combining multimodal inputs."""
        intents = {}
        
        # Add intents from text analysis
        if text_analysis:
            for intent, confidence in text_analysis.get('all_intents', {}).items():
                intents[intent] = intents.get(intent, 0.0) + (confidence * 0.6)  # Text has 60% weight
        
        # Add intents from gesture analysis
        if gesture_analysis:
            for intent, confidence in gesture_analysis.get('all_intents', {}).items():
                intents[intent] = intents.get(intent, 0.0) + (confidence * 0.3)  # Gesture has 30% weight
        
        # Use gaze analysis to modify confidence
        if gaze_analysis:
            attention = gaze_analysis.get('attention', 'normal')
            attention_confidence = gaze_analysis.get('confidence', 0.5)
            
            # Adjust confidences based on attention
            if attention == 'focused':
                # Increase confidence for all intents
                for intent in intents:
                    intents[intent] *= (1.0 + (0.2 * attention_confidence))
            elif attention == 'distracted':
                # Decrease confidence for all intents
                for intent in intents:
                    intents[intent] *= (1.0 - (0.3 * attention_confidence))
        
        # Adjust based on context
        if context:
            current_activity = context.get('current_activity', '')
            
            # If user is in a cognitive exercise, boost that intent
            if current_activity == 'cognitive_exercise' and 'cognitive_exercise' in intents:
                intents['cognitive_exercise'] *= 1.2
            
            # If user has a medication due soon, boost that intent
            if context.get('medication_due_soon', False) and 'medication_reminder' in intents:
                intents['medication_reminder'] *= 1.3
        
        # Get the intent with highest confidence
        if intents:
            best_intent = max(intents.items(), key=lambda x: x[1])
            return {
                'intent': best_intent[0],
                'confidence': min(1.0, best_intent[1]),  # Cap at 1.0
                'all_intents': intents
            }
        else:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'all_intents': {}
            }
    
    def _extract_parameters(self, intent_data, text, context):
        """Extract parameters for the detected intent from text."""
        intent = intent_data.get('intent', 'unknown')
        parameters = {}
        
        if intent == 'set_reminder':
            # Extract what to remind about and when
            for pattern in self.intents['set_reminder']['patterns']:
                match = re.search(pattern, text.lower())
                if match and len(match.groups()) >= 2:
                    parameters['reminder_text'] = match.group(2)
                    
                    # Try to extract time information
                    time_match = re.search(r'at (\d{1,2})(:\d{2})? ?(am|pm)?', text.lower())
                    if time_match:
                        hour = int(time_match.group(1))
                        minute = int(time_match.group(2)[1:]) if time_match.group(2) else 0
                        period = time_match.group(3)
                        
                        if period == 'pm' and hour < 12:
                            hour += 12
                        elif period == 'am' and hour == 12:
                            hour = 0
                            
                        parameters['reminder_time'] = f"{hour:02d}:{minute:02d}"
                    break
        
        elif intent == 'medication_reminder':
            # Extract medication name if mentioned
            med_match = re.search(r'(my )?(\w+) (medication|pills|medicine)', text.lower())
            if med_match:
                parameters['medication_name'] = med_match.group(2)
            
            # Check if asking about taken status
            if re.search(r'(did i|have i) (take|taken)', text.lower()):
                parameters['query_type'] = 'status_check'
            elif re.search(r'remind me', text.lower()):
                parameters['query_type'] = 'set_reminder'
            elif re.search(r'when (is|was)', text.lower()):
                parameters['query_type'] = 'time_check'
        
        elif intent == 'call_caregiver':
            # Extract which caregiver to call
            for relation in ['caregiver', 'family', 'son', 'daughter', 'wife', 'husband']:
                if relation in text.lower():
                    parameters['relation'] = relation
                    break
        
        elif intent == 'current_location':
            # Add current location from context if available
            if 'location' in context:
                parameters['current_location'] = context['location']
            
            # Check if asking for directions home
            if re.search(r'(find|way) (home|back)', text.lower()):
                parameters['destination'] = 'home'
        
        return parameters
    
    def _update_context(self, intent_data, parameters, location, context):
        """Update interaction context based on current processing."""
        # This would update a context database or memory for continuing conversations
        # Here we'll just update our local context_data
        
        patient_id = context.get('patient_id', 'unknown')
        if patient_id not in self.context_data:
            self.context_data[patient_id] = {}
        
        # Update patient's context
        patient_context = self.context_data[patient_id]
        patient_context['last_intent'] = intent_data.get('intent', 'unknown')
        patient_context['last_interaction_time'] = datetime.utcnow().isoformat()
        
        if parameters:
            if 'parameters' not in patient_context:
                patient_context['parameters'] = {}
            patient_context['parameters'].update(parameters)
        
        if location:
            patient_context['last_location'] = location
        
        # Save context data periodically (in a real app, this would be in a database)
        try:
            if os.path.exists(os.path.dirname(self.context_path)):
                import joblib
                joblib.dump(self.context_data, self.context_path)
                self.logger.debug(f"Updated context data for patient {patient_id}")
        except Exception as e:
            self.logger.error(f"Error saving context data: {str(e)}")
    
    def get_context(self, patient_id):
        """
        Get the current interaction context for a patient.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: Current interaction context
        """
        return self.context_data.get(patient_id, {})