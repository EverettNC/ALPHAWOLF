import logging
import numpy as np
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class EyeTrackingService:
    """Service for processing eye tracking data for cognitive engagement assessment."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gaze_history = {}  # Store recent gaze data by patient_id
        self.attention_thresholds = {
            'focused': 0.8,      # High attention
            'engaged': 0.6,      # Normal attention
            'wandering': 0.4,    # Low attention
            'disengaged': 0.2    # Very low attention
        }
        self.logger.info("Eye tracking service initialized")
    
    def process_gaze_data(self, patient_id, gaze_data):
        """
        Process raw gaze data to assess cognitive engagement.
        
        Args:
            patient_id: ID of the patient
            gaze_data: Dict containing gaze tracking data
                {
                    'timestamp': Timestamp of reading,
                    'x': x-coordinate in normalized (0-1) format,
                    'y': y-coordinate in normalized (0-1) format,
                    'duration': Fixation duration in seconds (optional),
                    'target_element': ID of UI element being gazed at (optional),
                    'target_type': Type of UI element (text, image, etc.) (optional)
                }
                
        Returns:
            dict: Processed gaze assessment
        """
        try:
            # Initialize patient's gaze history if needed
            if patient_id not in self.gaze_history:
                self.gaze_history[patient_id] = []
            
            # Add timestamp if not present
            if 'timestamp' not in gaze_data:
                gaze_data['timestamp'] = datetime.utcnow().isoformat()
            
            # Keep history limited to recent entries (last 100)
            self.gaze_history[patient_id].append(gaze_data)
            if len(self.gaze_history[patient_id]) > 100:
                self.gaze_history[patient_id].pop(0)
            
            # Calculate metrics based on gaze data
            metrics = self._calculate_gaze_metrics(patient_id)
            
            # Determine attention level based on metrics
            attention_level = self._determine_attention_level(metrics)
            
            # Create assessment
            assessment = {
                'patient_id': patient_id,
                'timestamp': datetime.utcnow().isoformat(),
                'attention_level': attention_level,
                'attention_score': metrics['attention_score'],
                'gaze_stability': metrics['gaze_stability'],
                'target_focus': metrics.get('target_focus', None),
                'saccade_frequency': metrics['saccade_frequency'],
                'recommended_actions': self._get_recommendations(attention_level, metrics)
            }
            
            return assessment
        except Exception as e:
            self.logger.error(f"Error processing gaze data: {str(e)}")
            return {
                'patient_id': patient_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_attention_history(self, patient_id, timeframe='recent'):
        """
        Get history of attention assessments for a patient.
        
        Args:
            patient_id: ID of the patient
            timeframe: 'recent' (last 10), 'session' (current session), 'day' (last 24 hours)
            
        Returns:
            list: Attention history data
        """
        try:
            if patient_id not in self.gaze_history:
                return []
            
            # Get gaze history for the patient
            history = self.gaze_history[patient_id]
            
            # Filter based on timeframe
            if timeframe == 'recent':
                history = history[-10:]  # Last 10 entries
            elif timeframe == 'session':
                # Assume sessions are separated by gaps of more than 5 minutes
                session_start = None
                session_data = []
                
                for i in range(len(history) - 1, -1, -1):
                    entry = history[i]
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    
                    if session_start is None:
                        session_start = entry_time
                        session_data.append(entry)
                    else:
                        time_diff = (session_start - entry_time).total_seconds()
                        if time_diff <= 300:  # Within 5 minutes
                            session_data.append(entry)
                        else:
                            break
                
                history = list(reversed(session_data))
            elif timeframe == 'day':
                # Filter to last 24 hours
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                history = [
                    entry for entry in history 
                    if datetime.fromisoformat(entry['timestamp']) >= cutoff_time
                ]
            
            # Process history to get attention assessments
            assessments = []
            for entry in history:
                metrics = self._calculate_entry_metrics(entry)
                attention_level = self._determine_attention_level(metrics)
                
                assessments.append({
                    'timestamp': entry['timestamp'],
                    'attention_level': attention_level,
                    'attention_score': metrics.get('attention_score', 0.0),
                    'target_element': entry.get('target_element', None),
                    'target_type': entry.get('target_type', None)
                })
            
            return assessments
        except Exception as e:
            self.logger.error(f"Error getting attention history: {str(e)}")
            return []
    
    def detect_cognitive_load(self, patient_id, context=None):
        """
        Detect cognitive load based on eye movement patterns.
        
        Args:
            patient_id: ID of the patient
            context: Optional context about current activity
            
        Returns:
            dict: Cognitive load assessment
        """
        try:
            if patient_id not in self.gaze_history or not self.gaze_history[patient_id]:
                return {
                    'patient_id': patient_id,
                    'cognitive_load': 'unknown',
                    'confidence': 0.0,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Get recent history (last 20 entries)
            recent_history = self.gaze_history[patient_id][-20:]
            
            # Calculate cognitive load indicators
            # 1. Pupil dilation (if available)
            pupil_sizes = [
                entry.get('pupil_size', None) 
                for entry in recent_history 
                if entry.get('pupil_size') is not None
            ]
            
            pupil_dilation = None
            if pupil_sizes and len(pupil_sizes) >= 3:
                # Check if pupil size is increasing (indicates higher cognitive load)
                pupil_dilation = np.mean(pupil_sizes[-3:]) - np.mean(pupil_sizes[:3])
            
            # 2. Saccade frequency
            saccade_count = 0
            for i in range(1, len(recent_history)):
                if 'x' in recent_history[i] and 'x' in recent_history[i-1]:
                    dx = recent_history[i]['x'] - recent_history[i-1]['x']
                    dy = recent_history[i]['y'] - recent_history[i-1]['y']
                    distance = np.sqrt(dx**2 + dy**2)
                    if distance > 0.1:  # Threshold for saccade
                        saccade_count += 1
            
            saccade_frequency = saccade_count / len(recent_history) if recent_history else 0
            
            # 3. Fixation duration
            fixation_durations = [
                entry.get('duration', 0.0) 
                for entry in recent_history 
                if entry.get('duration') is not None
            ]
            
            avg_fixation = np.mean(fixation_durations) if fixation_durations else 0.0
            
            # Determine cognitive load based on indicators
            cognitive_load = 'medium'  # Default
            confidence = 0.5  # Default
            
            if pupil_dilation is not None:
                if pupil_dilation > 0.2:
                    cognitive_load = 'high'
                    confidence = 0.7 + (pupil_dilation - 0.2) / 2  # Scale up with dilation
                elif pupil_dilation < -0.1:
                    cognitive_load = 'low'
                    confidence = 0.6 + abs(pupil_dilation + 0.1) / 2  # Scale up with contraction
            
            # Adjust based on saccade frequency
            if saccade_frequency > 0.5:  # High saccade frequency often indicates high load or distraction
                if cognitive_load != 'high':
                    cognitive_load = 'high'
                    confidence = float(max(confidence, 0.6 + saccade_frequency / 5))
            elif saccade_frequency < 0.2:  # Low saccade may indicate focused attention or disengagement
                # Use fixation duration to disambiguate
                if avg_fixation > 0.5:  # Longer fixations with low saccades suggests focus
                    cognitive_load = 'medium-low'
                    confidence = float(max(confidence, 0.6 + avg_fixation / 4))
                else:  # Short fixations with low saccades may indicate disengagement
                    cognitive_load = 'low'
                    confidence = float(max(confidence, 0.5))
            
            # Consider context if provided
            if context:
                task_difficulty = context.get('task_difficulty', 'medium')
                if task_difficulty == 'hard' and cognitive_load == 'high':
                    confidence += 0.1  # More confident if difficult task shows high load
                elif task_difficulty == 'easy' and cognitive_load == 'low':
                    confidence += 0.1  # More confident if easy task shows low load
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
            return {
                'patient_id': patient_id,
                'cognitive_load': cognitive_load,
                'confidence': confidence,
                'indicators': {
                    'pupil_dilation': pupil_dilation,
                    'saccade_frequency': saccade_frequency,
                    'avg_fixation_duration': avg_fixation
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error detecting cognitive load: {str(e)}")
            return {
                'patient_id': patient_id,
                'cognitive_load': 'unknown',
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def detect_confusion(self, patient_id, ui_context=None):
        """
        Detect confusion based on eye tracking patterns.
        
        Args:
            patient_id: ID of the patient
            ui_context: Optional context about UI elements being viewed
            
        Returns:
            dict: Confusion assessment
        """
        try:
            if patient_id not in self.gaze_history or not self.gaze_history[patient_id]:
                return {
                    'patient_id': patient_id,
                    'confused': False,
                    'confidence': 0.0,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Get recent history (last 30 entries)
            recent_history = self.gaze_history[patient_id][-30:]
            
            # Signs of confusion:
            # 1. Rapid back-and-forth scanning
            back_forth_count = 0
            for i in range(2, len(recent_history)):
                if 'x' in recent_history[i] and 'x' in recent_history[i-1] and 'x' in recent_history[i-2]:
                    x1, x2, x3 = recent_history[i-2]['x'], recent_history[i-1]['x'], recent_history[i]['x']
                    # Check for direction change
                    if (x2 > x1 and x3 < x2) or (x2 < x1 and x3 > x2):
                        back_forth_count += 1
            
            # Normalize by number of possible transitions
            back_forth_ratio = back_forth_count / (len(recent_history) - 2) if len(recent_history) > 2 else 0
            
            # 2. Fixations on UI elements marked as instructions/help
            help_fixations = 0
            if ui_context and 'elements' in ui_context:
                for entry in recent_history:
                    element_id = entry.get('target_element')
                    if element_id and element_id in ui_context['elements']:
                        element_type = ui_context['elements'][element_id].get('type')
                        if element_type in ['instruction', 'help', 'error_message']:
                            help_fixations += 1
            
            help_fixation_ratio = help_fixations / len(recent_history) if recent_history else 0
            
            # 3. Erratic gaze patterns (high variance in movements)
            gaze_points = [(entry.get('x', 0.5), entry.get('y', 0.5)) for entry in recent_history]
            
            # Calculate variance if we have enough points
            pattern_variance = 0
            if len(gaze_points) >= 3:
                # Calculate distances between consecutive points
                distances = []
                for i in range(1, len(gaze_points)):
                    dx = gaze_points[i][0] - gaze_points[i-1][0]
                    dy = gaze_points[i][1] - gaze_points[i-1][1]
                    distances.append(np.sqrt(dx**2 + dy**2))
                
                # Calculate variance of distances (high variance = erratic movement)
                pattern_variance = np.var(distances) if distances else 0
            
            # Determine confusion likelihood based on indicators
            confusion_indicators = {
                'back_forth_scanning': back_forth_ratio > 0.3,
                'help_element_focus': help_fixation_ratio > 0.2,
                'erratic_gaze': pattern_variance > 0.02
            }
            
            # Count positive indicators
            positive_indicators = sum(1 for v in confusion_indicators.values() if v)
            
            # Determine confusion state
            is_confused = positive_indicators >= 2
            
            # Calculate confidence
            if positive_indicators == 0:
                confidence = 0.8  # Confident not confused
            elif positive_indicators == 1:
                confidence = 0.5  # Uncertain
            elif positive_indicators == 2:
                confidence = 0.7  # Moderately confident confused
            else:
                confidence = 0.9  # Very confident confused
            
            return {
                'patient_id': patient_id,
                'confused': is_confused,
                'confidence': confidence,
                'indicators': confusion_indicators,
                'metrics': {
                    'back_forth_ratio': back_forth_ratio,
                    'help_fixation_ratio': help_fixation_ratio,
                    'pattern_variance': pattern_variance
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error detecting confusion: {str(e)}")
            return {
                'patient_id': patient_id,
                'confused': False,
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_gaze_metrics(self, patient_id):
        """Calculate metrics from gaze history for a patient."""
        if not self.gaze_history.get(patient_id):
            return {
                'attention_score': 0.5,  # Default mid-level
                'gaze_stability': 0.5,
                'saccade_frequency': 0.0
            }
        
        # Get recent history (last 20 entries or fewer)
        recent = self.gaze_history[patient_id][-20:]
        
        # Calculate gaze stability (inversely related to variance)
        gaze_points = [(entry.get('x', 0.5), entry.get('y', 0.5)) for entry in recent]
        
        # Calculate variance if we have enough points
        if len(gaze_points) >= 3:
            # Calculate distances between consecutive points
            distances = []
            for i in range(1, len(gaze_points)):
                dx = gaze_points[i][0] - gaze_points[i-1][0]
                dy = gaze_points[i][1] - gaze_points[i-1][1]
                distances.append(np.sqrt(dx**2 + dy**2))
            
            # High variance = low stability
            variance = np.var(distances) if distances else 0
            gaze_stability = 1.0 / (1.0 + 10.0 * variance)  # Scale and invert
        else:
            gaze_stability = 0.5  # Default if not enough data
        
        # Calculate saccade frequency (rapid eye movements)
        saccade_count = 0
        for i in range(1, len(recent)):
            if 'x' in recent[i] and 'x' in recent[i-1]:
                dx = recent[i]['x'] - recent[i-1]['x']
                dy = recent[i]['y'] - recent[i-1]['y']
                distance = np.sqrt(dx**2 + dy**2)
                if distance > 0.1:  # Threshold for saccade
                    saccade_count += 1
        
        saccade_frequency = saccade_count / len(recent) if recent else 0
        
        # Calculate target focus if target information is available
        target_counts = {}
        for entry in recent:
            if 'target_element' in entry:
                target = entry['target_element']
                target_counts[target] = target_counts.get(target, 0) + 1
        
        if target_counts:
            # Calculate percentage of time spent on most viewed target
            max_target = max(target_counts.items(), key=lambda x: x[1])
            target_focus = max_target[1] / len(recent)
        else:
            target_focus = None
        
        # Calculate overall attention score
        # Higher stability, moderate saccades, and higher target focus = higher attention
        stability_weight = 0.5
        saccade_weight = -0.3  # Too many saccades reduce attention, but zero is also bad
        focus_weight = 0.4
        
        attention_score = (stability_weight * gaze_stability) + \
                          (saccade_weight * abs(saccade_frequency - 0.2)) + \
                          (focus_weight * target_focus if target_focus is not None else 0)
        
        # Normalize to 0-1 range
        attention_score = float(max(0.0, min(1.0, attention_score + 0.3)))  # Shift score to reasonable range
        
        return {
            'attention_score': attention_score,
            'gaze_stability': gaze_stability,
            'target_focus': target_focus,
            'saccade_frequency': saccade_frequency
        }
    
    def _calculate_entry_metrics(self, entry):
        """Calculate metrics for a single gaze entry."""
        # For single entries, we have limited metrics
        metrics = {
            'attention_score': 0.5,  # Default
            'gaze_stability': None,
            'saccade_frequency': None
        }
        
        # If duration is available, use it as a signal
        if 'duration' in entry:
            duration = entry['duration']
            if duration > 1.0:  # Long fixation suggests higher attention
                metrics['attention_score'] = min(0.8, 0.5 + duration / 10.0)
            elif duration < 0.2:  # Very short fixation suggests lower attention
                metrics['attention_score'] = max(0.2, 0.5 - (0.2 - duration) / 0.2)
        
        return metrics
    
    def _determine_attention_level(self, metrics):
        """Map attention score to categorical level."""
        score = metrics['attention_score']
        
        if score >= self.attention_thresholds['focused']:
            return 'focused'
        elif score >= self.attention_thresholds['engaged']:
            return 'engaged'
        elif score >= self.attention_thresholds['wandering']:
            return 'wandering'
        else:
            return 'disengaged'
    
    def _get_recommendations(self, attention_level, metrics):
        """Generate recommendations based on attention assessment."""
        recommendations = []
        
        if attention_level == 'disengaged':
            recommendations.append("Provide visual prompts to re-engage attention")
            recommendations.append("Simplify the current content or task")
            recommendations.append("Consider taking a short break")
            
        elif attention_level == 'wandering':
            recommendations.append("Reduce distractions in the environment")
            recommendations.append("Use more engaging visual elements")
            recommendations.append("Break task into smaller steps")
            
        elif attention_level == 'engaged':
            if metrics.get('saccade_frequency', 0) > 0.4:
                recommendations.append("Content may be too complex, consider simplifying")
            else:
                recommendations.append("Current engagement level is appropriate")
                
        elif attention_level == 'focused':
            recommendations.append("Maintain current content complexity")
            recommendations.append("Good time for learning new information")
        
        return recommendations