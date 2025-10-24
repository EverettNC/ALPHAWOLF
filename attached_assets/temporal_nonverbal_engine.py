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
Enhanced Temporal Nonverbal Engine for AlphaVox
-------------------------------------------
This module processes sequences of nonverbal inputs over time to provide 
enhanced understanding of temporal patterns in communication. It integrates
gesture, eye tracking, and emotional data to form comprehensive interpretations.

This version combines features from the original implementation with enhancements
from the LSTM-based approach, allowing for both simple pattern recognition and 
more advanced deep learning-based analysis when models are available.
"""

import os
import json
import logging
import numpy as np
import time
import pickle
from typing import List, Dict, Any, Tuple, Optional, Union

# Check if TensorFlow is available
tf_available = False
try:
    import tensorflow as tf
    tf_available = True
    logging.info("TensorFlow is available. Advanced LSTM features enabled.")
except ImportError:
    logging.info("TensorFlow not found. Using simple temporal analysis only.")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemporalNonverbalEngine:
    """
    Engine for analyzing temporal sequences of nonverbal communication data.
    
    This engine maintains a history of multimodal inputs (gesture, eye, emotion)
    and analyzes them for patterns over time, providing more contextually
    appropriate interpretations than single-frame analysis.
    """
    
    def __init__(self, max_history: int = 30, lstm_model_dir: str = 'lstm_models', 
                 language_map_path: str = 'language_map.json'):
        """
        Initialize the temporal nonverbal engine
        
        Args:
            max_history: Maximum number of frames to keep in history
            lstm_model_dir: Directory containing trained LSTM models (for advanced mode)
            language_map_path: Path to language mapping file (for advanced mode)
        """
        # Sequence history for each modality
        self.gesture_history = []
        self.eye_history = []
        self.emotion_history = []
        
        # Maximum history frames to keep
        self.max_history = max_history
        
        # Pattern recognition confidence thresholds
        self.confidence_thresholds = {
            'gesture': 0.6,
            'eye': 0.7,
            'emotion': 0.65,
            'combined': 0.75
        }
        
        # Recognized patterns storage
        self.recognized_patterns = {
            'gesture': {},
            'eye': {},
            'emotion': {},
            'combined': {}
        }
        
        # Gesture patterns (simplified for basic demo)
        self.gesture_patterns = {
            'wave': {
                'description': 'Side-to-side hand movement',
                'meaning': 'Greeting or seeking attention'
            },
            'point': {
                'description': 'Direct finger indication',
                'meaning': 'Directing attention to an object or location'
            },
            'nod': {
                'description': 'Head moving up and down',
                'meaning': 'Agreement or acknowledgement'
            },
            'shake': {
                'description': 'Head moving left to right',
                'meaning': 'Disagreement or negation'
            },
            'circle': {
                'description': 'Circular hand motion',
                'meaning': 'Continuation or processing'
            }
        }
        
        # Eye patterns
        self.eye_patterns = {
            'focused': {
                'description': 'Sustained gaze at a single point',
                'meaning': 'Attention or interest'
            },
            'scanning': {
                'description': 'Regular movement between multiple points',
                'meaning': 'Searching or information gathering'
            },
            'avoidance': {
                'description': 'Looking away from primary subject',
                'meaning': 'Discomfort or disinterest'
            },
            'rapid_blink': {
                'description': 'Increased blink frequency',
                'meaning': 'Stress, surprise, or processing'
            }
        }
        
        # Emotion patterns
        self.emotion_patterns = {
            'consistent_positive': {
                'description': 'Sustained positive emotional state',
                'meaning': 'Contentment or happiness'
            },
            'consistent_negative': {
                'description': 'Sustained negative emotional state',
                'meaning': 'Distress or discomfort'
            },
            'fluctuating': {
                'description': 'Rapidly changing emotional states',
                'meaning': 'Uncertainty or emotional processing'
            },
            'intensifying': {
                'description': 'Increasing emotional intensity',
                'meaning': 'Growing reaction to stimulus'
            },
            'diminishing': {
                'description': 'Decreasing emotional intensity',
                'meaning': 'Calming or adjustment'
            }
        }
        
        # Multimodal patterns
        self.multimodal_patterns = {
            'agreement': {
                'description': 'Nodding + positive emotion + focused gaze',
                'meaning': 'Strong confirmation or approval'
            },
            'disagreement': {
                'description': 'Head shake + negative emotion + avoidance gaze',
                'meaning': 'Strong rejection or disapproval'
            },
            'confusion': {
                'description': 'Rapid eye movement + neutral/negative emotion + variable gestures',
                'meaning': 'Processing difficulty or misunderstanding'
            },
            'interest': {
                'description': 'Leaning forward + focused gaze + positive/neutral emotion',
                'meaning': 'Engagement or curiosity'
            },
            'disengagement': {
                'description': 'Leaning back + avoidance gaze + neutral/negative emotion',
                'meaning': 'Withdrawal or disinterest'
            }
        }
        
        # Initialize advanced LSTM mode if TensorFlow is available
        self.advanced_mode = False
        self.lstm_model_dir = lstm_model_dir
        self.language_map_path = language_map_path
        
        if tf_available:
            self._load_language_map()
            self._load_lstm_models()
            # Set advanced mode if models were loaded successfully
            if hasattr(self, 'models') and any(self.models.values()):
                self.advanced_mode = True
                logger.info("Advanced LSTM-based temporal analysis enabled")
        
        logger.info("Temporal Nonverbal Engine initialized")
    
    def _load_language_map(self):
        """Load the language mapping for nonverbal cues"""
        try:
            if os.path.exists(self.language_map_path):
                with open(self.language_map_path, 'r') as f:
                    self.language_map = json.load(f)
                logger.info("Language map loaded successfully")
            else:
                # Default language map if file doesn't exist
                self.language_map = {
                    'Hand Up': {'intent': 'Request attention', 'message': 'I need help.'},
                    'Wave Left': {'intent': 'Previous mode', 'message': 'Go back.'},
                    'Wave Right': {'intent': 'Next mode', 'message': 'Move forward.'},
                    'Head Jerk': {'intent': 'Stress (tick)', 'message': 'I\'m overwhelmed.'},
                    'Looking Up': {'intent': 'Thinking', 'message': 'I\'m thinking.'},
                    'Rapid Blinking': {'intent': 'Discomfort', 'message': 'I\'m uneasy.'},
                    'Neutral': {'intent': 'Calm', 'message': 'I\'m fine.'},
                    'Happy': {'intent': 'Joy', 'message': 'I\'m happy.'},
                    'Sad': {'intent': 'Unhappy', 'message': 'I\'m sad.'},
                    'Angry': {'intent': 'Upset', 'message': 'I\'m angry.'},
                    'Fear': {'intent': 'Worried', 'message': 'I\'m scared.'},
                    'Surprise': {'intent': 'Shocked', 'message': 'I\'m surprised.'}
                }
                # Save default map to file
                os.makedirs(os.path.dirname(self.language_map_path), exist_ok=True)
                with open(self.language_map_path, 'w') as f:
                    json.dump(self.language_map, f, indent=4)
                logger.info("Default language map created")
        except Exception as e:
            logger.error(f"Error loading language map: {e}")
            self.language_map = {}
    
    def _load_lstm_models(self):
        """Load the trained LSTM models for temporal pattern recognition"""
        self.models = {}
        self.labels = {}
        
        # Check if LSTM model directory exists
        if not os.path.exists(self.lstm_model_dir):
            logger.warning(f"LSTM model directory not found at {self.lstm_model_dir}")
            self.models['gesture'] = None
            self.models['eye_movement'] = None
            self.models['emotion'] = None
            return
        
        # Load gesture model if available
        try:
            gesture_model_path = os.path.join(self.lstm_model_dir, 'gesture_lstm_model.keras')
            gesture_labels_path = os.path.join(self.lstm_model_dir, 'gesture_labels.pkl')
            if os.path.exists(gesture_model_path) and os.path.exists(gesture_labels_path):
                self.models['gesture'] = tf.keras.models.load_model(gesture_model_path)
                with open(gesture_labels_path, 'rb') as f:
                    self.labels['gesture'] = pickle.load(f)
                logger.info("Gesture LSTM model loaded successfully")
            else:
                self.models['gesture'] = None
        except Exception as e:
            logger.error(f"Failed to load gesture LSTM model: {e}")
            self.models['gesture'] = None
        
        # Load eye movement model if available
        try:
            eye_model_path = os.path.join(self.lstm_model_dir, 'eye_movement_lstm_model.keras')
            eye_labels_path = os.path.join(self.lstm_model_dir, 'eye_movement_labels.pkl')
            if os.path.exists(eye_model_path) and os.path.exists(eye_labels_path):
                self.models['eye_movement'] = tf.keras.models.load_model(eye_model_path)
                with open(eye_labels_path, 'rb') as f:
                    self.labels['eye_movement'] = pickle.load(f)
                logger.info("Eye movement LSTM model loaded successfully")
            else:
                self.models['eye_movement'] = None
        except Exception as e:
            logger.error(f"Failed to load eye movement LSTM model: {e}")
            self.models['eye_movement'] = None
        
        # Load emotion model if available
        try:
            emotion_model_path = os.path.join(self.lstm_model_dir, 'emotion_lstm_model.keras')
            emotion_labels_path = os.path.join(self.lstm_model_dir, 'emotion_labels.pkl')
            if os.path.exists(emotion_model_path) and os.path.exists(emotion_labels_path):
                self.models['emotion'] = tf.keras.models.load_model(emotion_model_path)
                with open(emotion_labels_path, 'rb') as f:
                    self.labels['emotion'] = pickle.load(f)
                logger.info("Emotion LSTM model loaded successfully")
            else:
                self.models['emotion'] = None
        except Exception as e:
            logger.error(f"Failed to load emotion LSTM model: {e}")
            self.models['emotion'] = None
    
    def process_multimodal_sequence(self, 
                                  gesture_features: List[float], 
                                  eye_features: List[float], 
                                  emotion_features: List[float]) -> Dict[str, Any]:
        """
        Process multimodal input features and update temporal analysis
        
        Args:
            gesture_features: Features from gesture recognition
            eye_features: Features from eye tracking
            emotion_features: Features from emotion recognition
            
        Returns:
            dict: Analysis results and response
        """
        # Add current features to history
        self.gesture_history.append(gesture_features)
        self.eye_history.append(eye_features)
        self.emotion_history.append(emotion_features)
        
        # Trim history to max length
        self._trim_history()
        
        # Check if we should use advanced LSTM mode
        if self.advanced_mode and tf_available:
            return self._process_with_lstm(gesture_features, eye_features, emotion_features)
        
        # Use basic pattern recognition mode
        gesture_analysis = self._analyze_gesture_sequence()
        eye_analysis = self._analyze_eye_sequence()
        emotion_analysis = self._analyze_emotion_sequence()
        
        # Combined multimodal analysis
        combined_analysis = self._perform_multimodal_analysis(
            gesture_analysis, eye_analysis, emotion_analysis)
        
        # Determine primary result based on highest confidence
        primary_type, primary_result = self._determine_primary_result(
            gesture_analysis, eye_analysis, emotion_analysis, combined_analysis)
        
        # Generate enhanced response
        enhanced_response = self._generate_enhanced_response(
            primary_type, primary_result, combined_analysis)
        
        # Return comprehensive results
        return {
            'timestamp': time.time(),
            'primary_type': primary_type,
            'primary_result': primary_result,
            'enhanced_response': enhanced_response,
            'gesture_analysis': gesture_analysis,
            'eye_analysis': eye_analysis,
            'emotion_analysis': emotion_analysis,
            'combined_analysis': combined_analysis
        }
    
    def _process_with_lstm(self, gesture_features, eye_features, emotion_features):
        """Process using LSTM-based temporal analysis"""
        results = []
        
        # Check if we have enough data in the buffers
        gesture_ready = len(self.gesture_history) >= 10
        eye_ready = len(self.eye_history) >= 10
        emotion_ready = len(self.emotion_history) >= 10
        
        # Use LSTM models for classification if available
        if gesture_ready and self.models.get('gesture'):
            gesture_result = self._classify_with_lstm('gesture')
            results.append(('gesture', gesture_result))
        else:
            # Fall back to basic analysis
            results.append(('gesture', self._analyze_gesture_sequence()))
        
        if eye_ready and self.models.get('eye_movement'):
            eye_result = self._classify_with_lstm('eye_movement')
            results.append(('eye', eye_result))
        else:
            results.append(('eye', self._analyze_eye_sequence()))
        
        if emotion_ready and self.models.get('emotion'):
            emotion_result = self._classify_with_lstm('emotion')
            results.append(('emotion', emotion_result))
        else:
            results.append(('emotion', self._analyze_emotion_sequence()))
        
        # Get the individual analyses
        gesture_analysis = dict(results)[0]
        eye_analysis = dict(results)[1]
        emotion_analysis = dict(results)[2]
        
        # Combined multimodal analysis
        combined_analysis = self._perform_multimodal_analysis(
            gesture_analysis, eye_analysis, emotion_analysis)
        
        # Sort results by confidence
        sorted_results = sorted(results, key=lambda x: x[1]['confidence'], reverse=True)
        primary_type, primary_result = sorted_results[0]
        
        # Generate enhanced response
        intent_to_emotion = self._map_intent_to_emotion(primary_result.get('intent', 'unknown'))
        intensity = self._confidence_to_intensity(primary_result.get('confidence', 0.0))
        
        # Enhanced response text
        enhanced_response = self._generate_enhanced_response(primary_type, primary_result, combined_analysis)
        
        return {
            'timestamp': time.time(),
            'primary_type': primary_type,
            'primary_result': primary_result,
            'enhanced_response': enhanced_response,
            'gesture_analysis': dict(results).get('gesture', {}),
            'eye_analysis': dict(results).get('eye', {}),
            'emotion_analysis': dict(results).get('emotion', {}),
            'combined_analysis': combined_analysis
        }
    
    def _classify_with_lstm(self, modality):
        """
        Use LSTM model to classify a sequence
        
        Args:
            modality: The modality to classify ('gesture', 'eye_movement', or 'emotion')
            
        Returns:
            dict: Classification result
        """
        # Map modality to history
        if modality == 'gesture':
            sequence = self.gesture_history
        elif modality == 'eye_movement':
            sequence = self.eye_history
        else:  # emotion
            sequence = self.emotion_history
        
        # Convert sequence to numpy array
        sequence_np = np.array(sequence[-10:])  # Use the last 10 frames
        sequence_np = np.expand_dims(sequence_np, axis=0)  # Add batch dimension
        
        # Make prediction
        prediction = self.models[modality].predict(sequence_np, verbose=0)
        class_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][class_idx])
        
        # Get class label
        if class_idx < len(self.labels[modality]):
            label = self.labels[modality][class_idx]
        else:
            label = 'Unknown'
        
        # Get intent and message from language map
        expression_data = self.language_map.get(label, 
                                              {'intent': 'Unknown', 
                                               'message': 'I don\'t understand.'})
        
        return {
            'pattern': label,
            'confidence': confidence,
            'intent': expression_data['intent'],
            'meaning': expression_data.get('meaning', expression_data['intent']),
            'message': expression_data['message'],
            'description': expression_data.get('description', label),
            'duration_frames': len(sequence)
        }
    
    def _map_intent_to_emotion(self, intent):
        """
        Map intent to an emotional state
        
        Args:
            intent: Intent string from classification result
            
        Returns:
            Emotion string
        """
        # Intent to emotion mapping
        intent_emotion_map = {
            'Request attention': 'curious',
            'Previous mode': 'neutral',
            'Next mode': 'neutral',
            'Stress (tick)': 'anxious',
            'Thinking': 'thoughtful',
            'Discomfort': 'uncomfortable',
            'Calm': 'neutral',
            'Joy': 'happy',
            'Unhappy': 'sad',
            'Upset': 'angry',
            'Worried': 'fearful',
            'Shocked': 'surprised'
        }
        
        return intent_emotion_map.get(intent, 'neutral')
    
    def _confidence_to_intensity(self, confidence):
        """
        Convert confidence score to intensity level
        
        Args:
            confidence: Confidence score from 0.0 to 1.0
            
        Returns:
            Intensity level (mild, moderate, strong)
        """
        if confidence < 0.4:
            return "mild"
        elif confidence < 0.7:
            return "moderate"
        else:
            return "strong"

    def _trim_history(self):
        """Trim history sequences to maximum length"""
        if len(self.gesture_history) > self.max_history:
            self.gesture_history = self.gesture_history[-self.max_history:]
        
        if len(self.eye_history) > self.max_history:
            self.eye_history = self.eye_history[-self.max_history:]
        
        if len(self.emotion_history) > self.max_history:
            self.emotion_history = self.emotion_history[-self.max_history:]
    
    def _analyze_gesture_sequence(self) -> Dict[str, Any]:
        """
        Analyze the temporal sequence of gesture features
        
        Returns:
            dict: Gesture analysis results
        """
        # With a real implementation, we would use more sophisticated pattern recognition
        # For this demo, we'll use a simplified approach
        
        # Sample features structure (for reference):
        # [x_position, y_position, angle, velocity] per frame
        
        if len(self.gesture_history) < 3:
            # Not enough history for meaningful temporal analysis
            return {
                'pattern': 'unknown',
                'confidence': 0.0,
                'meaning': 'Insufficient gesture data for analysis',
                'duration_frames': len(self.gesture_history)
            }
        
        # Simplified analysis: look for patterns in the sequence
        # In this demo, we'll just randomly select one for illustration
        gesture_patterns = list(self.gesture_patterns.keys())
        selected_pattern = gesture_patterns[hash(str(self.gesture_history[-1])) % len(gesture_patterns)]
        
        # Calculate a pseudo-confidence based on consistency
        # In a real implementation, this would use actual pattern matching algorithms
        consistency = self._calculate_sequence_consistency(self.gesture_history)
        confidence = min(0.5 + (consistency * 0.5), 0.95)
        
        pattern_info = self.gesture_patterns[selected_pattern]
        
        return {
            'pattern': selected_pattern,
            'confidence': confidence,
            'meaning': pattern_info['meaning'],
            'description': pattern_info['description'],
            'duration_frames': len(self.gesture_history)
        }
    
    def _analyze_eye_sequence(self) -> Dict[str, Any]:
        """
        Analyze the temporal sequence of eye tracking features
        
        Returns:
            dict: Eye tracking analysis results
        """
        # Sample features structure (for reference):
        # [gaze_x, gaze_y, blink_rate] per frame
        
        if len(self.eye_history) < 3:
            # Not enough history for meaningful temporal analysis
            return {
                'pattern': 'unknown',
                'confidence': 0.0,
                'meaning': 'Insufficient eye tracking data for analysis',
                'duration_frames': len(self.eye_history)
            }
        
        # Simplified analysis for demo
        eye_patterns = list(self.eye_patterns.keys())
        selected_pattern = eye_patterns[hash(str(self.eye_history[-1])) % len(eye_patterns)]
        
        # Calculate a pseudo-confidence
        consistency = self._calculate_sequence_consistency(self.eye_history)
        confidence = min(0.4 + (consistency * 0.6), 0.9)  # Eye tracking typically has lower confidence
        
        pattern_info = self.eye_patterns[selected_pattern]
        
        return {
            'pattern': selected_pattern,
            'confidence': confidence,
            'meaning': pattern_info['meaning'],
            'description': pattern_info['description'],
            'duration_frames': len(self.eye_history),
            'blink_rate': self._calculate_blink_rate()
        }
    
    def _analyze_emotion_sequence(self) -> Dict[str, Any]:
        """
        Analyze the temporal sequence of emotion features
        
        Returns:
            dict: Emotion analysis results
        """
        # Sample features structure (for reference):
        # [happy, sad, angry, surprised, neutral] per frame
        
        if len(self.emotion_history) < 3:
            # Not enough history for meaningful temporal analysis
            return {
                'pattern': 'unknown',
                'confidence': 0.0,
                'meaning': 'Insufficient emotion data for analysis',
                'duration_frames': len(self.emotion_history)
            }
        
        # Simplified analysis for demo
        emotion_patterns = list(self.emotion_patterns.keys())
        selected_pattern = emotion_patterns[hash(str(self.emotion_history[-1])) % len(emotion_patterns)]
        
        # Calculate a pseudo-confidence
        consistency = self._calculate_sequence_consistency(self.emotion_history)
        trend = self._calculate_emotion_trend()
        confidence = min(0.45 + (consistency * 0.3) + (abs(trend) * 0.25), 0.95)
        
        pattern_info = self.emotion_patterns[selected_pattern]
        
        # Calculate dominant emotion
        dominant_emotion = "neutral"
        if len(self.emotion_history) > 0 and len(self.emotion_history[-1]) >= 5:
            emotions = ["happy", "sad", "angry", "surprised", "neutral"]
            dominant_idx = np.argmax(self.emotion_history[-1])
            if dominant_idx < len(emotions):
                dominant_emotion = emotions[dominant_idx]
        
        return {
            'pattern': selected_pattern,
            'confidence': confidence,
            'meaning': pattern_info['meaning'],
            'description': pattern_info['description'],
            'duration_frames': len(self.emotion_history),
            'dominant_emotion': dominant_emotion,
            'trend': trend
        }
    
    def _perform_multimodal_analysis(self, 
                                   gesture_analysis: Dict[str, Any],
                                   eye_analysis: Dict[str, Any],
                                   emotion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform integrated multimodal analysis combining all modalities
        
        Args:
            gesture_analysis: Results from gesture sequence analysis
            eye_analysis: Results from eye tracking sequence analysis
            emotion_analysis: Results from emotion sequence analysis
            
        Returns:
            dict: Combined multimodal analysis
        """
        # Check if we have enough data from all modalities
        if (gesture_analysis['confidence'] < 0.2 or 
            eye_analysis['confidence'] < 0.2 or 
            emotion_analysis['confidence'] < 0.2):
            
            return {
                'pattern': 'unclear',
                'confidence': 0.0,
                'meaning': 'Insufficient data for multimodal analysis',
                'contributing_patterns': []
            }
        
        # Simplified multimodal analysis for demo
        # In a real implementation, we would use more sophisticated pattern matching
        
        # Determine multimodal pattern based on individual analyses
        multimodal_patterns = list(self.multimodal_patterns.keys())
        
        # Simple heuristic: use all the individual patterns to select a multimodal pattern
        combined_hash = hash(gesture_analysis['pattern'] + 
                           eye_analysis['pattern'] + 
                           emotion_analysis['pattern'])
        
        selected_pattern = multimodal_patterns[combined_hash % len(multimodal_patterns)]
        pattern_info = self.multimodal_patterns[selected_pattern]
        
        # Calculate combined confidence
        # Weight each modality based on typical reliability
        combined_confidence = (
            gesture_analysis['confidence'] * 0.35 +
            eye_analysis['confidence'] * 0.25 +
            emotion_analysis['confidence'] * 0.4
        )
        
        # Boost confidence if individual confidences are all high
        if (gesture_analysis['confidence'] > 0.7 and
            eye_analysis['confidence'] > 0.6 and
            emotion_analysis['confidence'] > 0.7):
            combined_confidence = min(combined_confidence + 0.1, 0.98)
        
        return {
            'pattern': selected_pattern,
            'confidence': combined_confidence,
            'meaning': pattern_info['meaning'],
            'description': pattern_info['description'],
            'contributing_patterns': [
                {'type': 'gesture', 'pattern': gesture_analysis['pattern']},
                {'type': 'eye', 'pattern': eye_analysis['pattern']},
                {'type': 'emotion', 'pattern': emotion_analysis['pattern']}
            ]
        }
    
    def _determine_primary_result(self,
                               gesture_analysis: Dict[str, Any],
                               eye_analysis: Dict[str, Any],
                               emotion_analysis: Dict[str, Any],
                               combined_analysis: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Determine the primary result to report based on confidences
        
        Args:
            gesture_analysis: Results from gesture sequence analysis
            eye_analysis: Results from eye tracking sequence analysis
            emotion_analysis: Results from emotion sequence analysis
            combined_analysis: Results from multimodal analysis
            
        Returns:
            tuple: (primary_type, primary_result)
        """
        # Compare confidences to determine primary result
        confidences = {
            'gesture': gesture_analysis['confidence'],
            'eye': eye_analysis['confidence'],
            'emotion': emotion_analysis['confidence'],
            'combined': combined_analysis['confidence']
        }
        
        # Find the key with the highest confidence
        max_confidence = 0.0
        primary_type = 'combined'  # default
        
        for modality, confidence in confidences.items():
            if confidence > max_confidence:
                max_confidence = confidence
                primary_type = modality
        
        # Get the corresponding analysis
        if primary_type == 'gesture':
            primary_result = gesture_analysis
        elif primary_type == 'eye':
            primary_result = eye_analysis
        elif primary_type == 'emotion':
            primary_result = emotion_analysis
        else:  # combined
            primary_result = combined_analysis
        
        return primary_type, primary_result
    
    def _generate_enhanced_response(self,
                                 primary_type: str,
                                 primary_result: Dict[str, Any],
                                 combined_analysis: Dict[str, Any]) -> str:
        """
        Generate an enhanced textual response based on the analyses
        
        Args:
            primary_type: Type of primary result (gesture, eye, emotion, combined)
            primary_result: Primary analysis result
            combined_analysis: Combined multimodal analysis
            
        Returns:
            str: Enhanced response text
        """
        if primary_result['confidence'] < 0.3:
            return "I'm not detecting a clear pattern in your nonverbal communication."
        
        confidence_level = "possibly"
        if primary_result['confidence'] > 0.8:
            confidence_level = "clearly"
        elif primary_result['confidence'] > 0.6:
            confidence_level = "likely"
        
        # Base response on primary result
        response = f"I {confidence_level} observe {primary_result['description']}. "
        
        # Add meaning interpretation
        response += f"This suggests {primary_result['meaning']}. "
        
        # If primary is not combined but combined has high confidence, add it
        if primary_type != 'combined' and combined_analysis['confidence'] > 0.6:
            response += f"Overall, your nonverbal communication indicates {combined_analysis['meaning']}."
        
        return response
    
    def _calculate_sequence_consistency(self, sequence: List[List[float]]) -> float:
        """
        Calculate the consistency of a feature sequence
        
        Args:
            sequence: Sequence of feature vectors
            
        Returns:
            float: Consistency score (0-1)
        """
        if len(sequence) < 2:
            return 0.0
        
        # Simple consistency measure: mean pairwise similarity
        total_similarity = 0.0
        comparisons = 0
        
        # Compare adjacent frames
        for i in range(len(sequence) - 1):
            similarity = self._calculate_vector_similarity(sequence[i], sequence[i+1])
            total_similarity += similarity
            comparisons += 1
        
        return total_similarity / max(1, comparisons)
    
    def _calculate_vector_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate similarity between two feature vectors
        
        Args:
            vec1: First feature vector
            vec2: Second feature vector
            
        Returns:
            float: Similarity score (0-1)
        """
        # Ensure same length
        min_len = min(len(vec1), len(vec2))
        vec1 = vec1[:min_len]
        vec2 = vec2[:min_len]
        
        if min_len == 0:
            return 0.0
        
        # Simplified similarity: 1 - normalized Euclidean distance
        try:
            distance = np.sqrt(sum((np.array(vec1) - np.array(vec2))**2))
            max_possible_distance = np.sqrt(min_len * 4)  # Assuming values in range [0,2]
            normalized_distance = min(distance / max_possible_distance, 1.0)
            return 1.0 - normalized_distance
        except:
            # Fallback if numpy operations fail
            diffs = [abs(a - b) for a, b in zip(vec1, vec2)]
            avg_diff = sum(diffs) / min_len
            return 1.0 - min(avg_diff / 2.0, 1.0)  # Assuming values in range [0,2]
    
    def _calculate_blink_rate(self) -> float:
        """
        Calculate blink rate from eye history
        
        Returns:
            float: Estimated blinks per minute
        """
        # In a real implementation, this would analyze actual blink data
        # For the demo, we'll return a randomized but consistent value
        if not self.eye_history:
            return 0.0
        
        # Use the third value of eye features as a proxy for blink rate
        # In a real implementation, this would be actual blink detection
        try:
            blink_values = [frame[2] if len(frame) > 2 else 0.0 for frame in self.eye_history]
            return np.mean(blink_values) * 60.0  # Convert to per minute
        except:
            # Fallback
            return 12.0  # Average human blink rate
    
    def _calculate_emotion_trend(self) -> float:
        """
        Calculate the trend in emotion intensity
        
        Returns:
            float: Trend value (negative = decreasing, positive = increasing)
        """
        if len(self.emotion_history) < 3:
            return 0.0
        
        try:
            # Use average of all emotion values as a proxy for intensity
            intensities = [np.mean(frame) for frame in self.emotion_history]
            
            # Calculate linear regression slope
            x = np.arange(len(intensities))
            y = np.array(intensities)
            A = np.vstack([x, np.ones(len(x))]).T
            
            # Use least squares to find slope
            slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
            
            # Normalize to range [-1, 1]
            return np.clip(slope * len(intensities), -1.0, 1.0)
        except:
            # Fallback if numpy operations fail
            if len(self.emotion_history) >= 3:
                first = sum(self.emotion_history[0]) / len(self.emotion_history[0])
                last = sum(self.emotion_history[-1]) / len(self.emotion_history[-1])
                return (last - first) / max(1, len(self.emotion_history))
            return 0.0
    
    def set_learning_journey(self, learning_journey):
        """
        Inject a LearningJourney instance into the engine.
        
        Args:
            learning_journey: LearningJourney instance for tracking progress
        """
        self.learning_journey = learning_journey
        logger.info("Learning journey integration enabled")
    
    def set_conversation_persona(self, persona):
        """
        Set the conversation persona for response generation
        
        Args:
            persona: Personality profile to use
            
        Returns:
            bool: Success of persona change
        """
        # This would typically interact with a conversation engine
        # For now, just log the change
        logger.info(f"Setting conversation persona to: {persona}")
        return True
    
    def get_academic_response(self, topic, depth="advanced"):
        """
        Generate a PhD-level academic response on a given topic
        
        Args:
            topic: Academic topic to discuss
            depth: Depth of response (basic, intermediate, advanced)
            
        Returns:
            str: Academic response text
        """
        # This would typically interact with an NLP module
        # For now, return a placeholder response
        domains = ["science", "humanities", "philosophy", "technology", "medicine"]
        domain = domains[hash(topic) % len(domains)]
        
        if depth == "advanced":
            return f"Regarding your inquiry in {domain}: Recent advances in this field have leveraged computational approaches to model complex systems with emergent properties that were previously intractable."
        elif depth == "intermediate":
            return f"From a {domain} perspective, this topic involves the interplay of multiple factors that create a dynamic system with feedback loops and emergent behaviors."
        else:
            return f"This {domain} topic explores how different elements work together to create interesting patterns we can observe in the world around us."
    
    def clear_buffers(self):
        """Clear all sequence buffers"""
        self.gesture_history = []
        self.eye_history = []
        self.emotion_history = []
        logger.info("All sequence buffers cleared")

# Create singleton accessor
_temporal_nonverbal_engine = None

def get_temporal_nonverbal_engine():
    """Get or create the temporal nonverbal engine singleton"""
    global _temporal_nonverbal_engine
    if _temporal_nonverbal_engine is None:
        _temporal_nonverbal_engine = TemporalNonverbalEngine()
    return _temporal_nonverbal_engine