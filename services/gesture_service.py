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

import os
import joblib
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class GestureService:
    """Service for processing and recognizing gestures from patients."""
    
    def __init__(self, model_path=None):
        self.model = None
        self.gesture_types = ['HandUp', 'HandWave', 'PointingLeft', 'PointingRight', 'Clapping', 'None']
        
        try:
            # Try to load gesture model - first check if it exists in shared models directory
            if model_path:
                self.model_path = model_path
            else:
                # Try different potential locations for the model
                potential_paths = [
                    'models/gesture_model.pkl',
                    'shared/models/gesture_model.pkl',
                    'christman-ai/shared/models/gesture_model.pkl'
                ]
                
                for path in potential_paths:
                    if os.path.exists(path):
                        self.model_path = path
                        break
                else:
                    # If no model found, use placeholder logic
                    logger.warning("Gesture model not found. Using placeholder recognition logic.")
                    self.model_path = None
                    
            if self.model_path:
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded gesture model from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading gesture model: {str(e)}")
            self.model = None
    
    def process_gesture(self, gesture_data):
        """
        Process gesture data and return recognized gesture.
        
        Args:
            gesture_data: Raw gesture data from input device
            
        Returns:
            String representation of recognized gesture or None if not recognized
        """
        try:
            if self.model:
                # Preprocess gesture data for model input
                processed_data = self._preprocess_gesture_data(gesture_data)
                
                # Make prediction using model
                gesture_index = self.model.predict([processed_data])[0]
                confidence = np.max(self.model.predict_proba([processed_data])[0])
                
                if confidence > 0.6:  # Confidence threshold
                    gesture = self.gesture_types[gesture_index]
                    logger.info(f"Recognized gesture: {gesture} with confidence {confidence:.2f}")
                    return gesture
                else:
                    logger.info(f"Low confidence gesture detection: {confidence:.2f}")
                    return None
            else:
                # Placeholder logic for testing when model is not available
                if isinstance(gesture_data, dict) and 'type' in gesture_data:
                    # If client sends pre-classified gesture for testing
                    return gesture_data['type'] if gesture_data['type'] in self.gesture_types else None
                elif isinstance(gesture_data, list) and len(gesture_data) > 0:
                    # Simple heuristic-based recognition for testing
                    if self._is_hand_up(gesture_data):
                        return 'HandUp'
                    elif self._is_hand_wave(gesture_data):
                        return 'HandWave'
                    # Add more simple gesture detection heuristics as needed
                
                logger.warning("Using placeholder gesture recognition - no model available")
                return None
                
        except Exception as e:
            logger.error(f"Error processing gesture: {str(e)}")
            return None
    
    def _preprocess_gesture_data(self, raw_data):
        """Preprocess raw gesture data for model input."""
        # In a real implementation, this would transform raw sensor/camera data
        # into the format expected by the model
        
        if isinstance(raw_data, list) and len(raw_data) >= 15:
            # Assuming the raw_data is a list of joint positions or similar
            # Convert to numpy array and normalize if needed
            return np.array(raw_data[:15], dtype=float)
        else:
            # If data format is unexpected, try to convert to a compatible format
            # or return a zero vector
            logger.warning(f"Unexpected gesture data format: {type(raw_data)}")
            return np.zeros(15, dtype=float)
    
    def _is_hand_up(self, gesture_data):
        """Simple heuristic to detect 'hand up' gesture."""
        # This is a simplified placeholder implementation
        try:
            if len(gesture_data) < 4:
                return False
                
            # Assuming format where y values increase upward
            # Check if hand is significantly above shoulder
            hand_y = gesture_data[0]
            shoulder_y = gesture_data[2]
            return hand_y > shoulder_y + 0.2
        except:
            return False
    
    def _is_hand_wave(self, gesture_data):
        """Simple heuristic to detect 'hand wave' gesture."""
        # This is a simplified placeholder implementation
        try:
            if len(gesture_data) < 8:
                return False
                
            # Assuming gesture_data contains hand position over time
            # Check for side-to-side movement
            hand_x_positions = [p[0] for p in gesture_data[:5]]
            max_diff = max(hand_x_positions) - min(hand_x_positions)
            return max_diff > 0.15  # Threshold for detecting side-to-side movement
        except:
            return False
