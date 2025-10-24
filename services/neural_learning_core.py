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
import numpy as np
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class NeuralLearningCore:
    """Core for inferring cognitive needs and adapting learning approaches for dementia patients."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.root_causes = {
            'cognitive_load': {
                'description': 'Level of mental effort currently experienced by the patient',
                'factors': ['task_complexity', 'fatigue', 'time_of_day', 'distractions']
            },
            'emotional_state': {
                'description': 'Current emotional condition affecting cognitive performance',
                'factors': ['anxiety', 'frustration', 'engagement', 'comfort']
            },
            'memory_degradation': {
                'description': 'Specific memory functions showing impairment',
                'factors': ['working_memory', 'long_term_recall', 'procedural_memory', 'recognition']
            },
            'communication_barrier': {
                'description': 'Obstacles in understanding or expressing information',
                'factors': ['language_processing', 'word_finding', 'comprehension', 'attention']
            }
        }
        
        # Factor weights initialized with defaults, would be personalized with learning
        self.factor_weights = {
            'task_complexity': 0.7,
            'fatigue': 0.8,
            'time_of_day': 0.5,
            'distractions': 0.6,
            'anxiety': 0.7,
            'frustration': 0.8,
            'engagement': 0.9,
            'comfort': 0.5,
            'working_memory': 0.9,
            'long_term_recall': 0.8,
            'procedural_memory': 0.6,
            'recognition': 0.7,
            'language_processing': 0.7,
            'word_finding': 0.8,
            'comprehension': 0.9,
            'attention': 0.8
        }
        
        # Load model if available
        self.model_path = os.path.join('models', 'root_cause_model.pkl')
        self.model = None
        
        try:
            if os.path.exists(self.model_path):
                import joblib
                self.model = joblib.load(self.model_path)
                self.logger.info(f"Loaded root cause model from {self.model_path}")
            else:
                self.logger.warning(f"Root cause model not found at {self.model_path}, using heuristic inference")
        except Exception as e:
            self.logger.error(f"Error loading root cause model: {str(e)}")
        
        self.logger.info("Neural Learning Core initialized")
    
    def infer_root_cause(self, observation_data):
        """
        Infer the root cause of cognitive difficulties from observation data.
        
        Args:
            observation_data: Dict with observed factors like task performance, reaction times, etc.
            
        Returns:
            dict: Root cause assessment with probabilities
        """
        try:
            if self.model:
                # Using trained model for inference
                features = self._extract_features(observation_data)
                root_cause_probs = self.model.predict_proba([features])[0]
                root_cause_indexes = self.model.classes_
                
                # Find index of max probability
                max_index = int(np.argmax(root_cause_probs))
                max_prob = float(np.max(root_cause_probs))
                
                return {
                    'primary_cause': root_cause_indexes[max_index],
                    'confidence': max_prob,
                    'all_causes': {cause: float(prob) for cause, prob in zip(root_cause_indexes, root_cause_probs)}
                }
            else:
                # Using heuristic approach 
                return self._heuristic_inference(observation_data)
        except Exception as e:
            self.logger.error(f"Error inferring root cause: {str(e)}")
            return {
                'primary_cause': 'unknown',
                'confidence': 0.0,
                'all_causes': {}
            }
    
    def _extract_features(self, observation_data):
        """Extract features from observation data for model input."""
        # This would extract relevant features from the observation data
        # based on the model's expected input format
        features = []
        
        # Example feature extraction
        if 'task_performance' in observation_data:
            features.append(observation_data['task_performance'])
        else:
            features.append(0.5)  # Default value
            
        if 'reaction_time' in observation_data:
            features.append(observation_data['reaction_time'])
        else:
            features.append(0.5)  # Default value
        
        # Add more feature extraction logic here
        
        return features
    
    def _heuristic_inference(self, observation_data):
        """Use heuristics to infer root cause when model is unavailable."""
        scores = {
            'cognitive_load': 0.0,
            'emotional_state': 0.0,
            'memory_degradation': 0.0,
            'communication_barrier': 0.0
        }
        
        # Calculate scores based on observation data and factor weights
        if 'task_complexity' in observation_data:
            scores['cognitive_load'] += observation_data['task_complexity'] * self.factor_weights['task_complexity']
            
        if 'fatigue' in observation_data:
            scores['cognitive_load'] += observation_data['fatigue'] * self.factor_weights['fatigue']
            
        if 'anxiety' in observation_data:
            scores['emotional_state'] += observation_data['anxiety'] * self.factor_weights['anxiety']
            
        if 'frustration' in observation_data:
            scores['emotional_state'] += observation_data['frustration'] * self.factor_weights['frustration']
            
        if 'working_memory' in observation_data:
            scores['memory_degradation'] += observation_data['working_memory'] * self.factor_weights['working_memory']
            
        if 'long_term_recall' in observation_data:
            scores['memory_degradation'] += observation_data['long_term_recall'] * self.factor_weights['long_term_recall']
            
        if 'language_processing' in observation_data:
            scores['communication_barrier'] += observation_data['language_processing'] * self.factor_weights['language_processing']
            
        if 'word_finding' in observation_data:
            scores['communication_barrier'] += observation_data['word_finding'] * self.factor_weights['word_finding']
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            for key in scores:
                scores[key] /= total
        
        # Find primary cause
        primary_cause = max(scores.items(), key=lambda x: x[1])[0]
        
        return {
            'primary_cause': primary_cause,
            'confidence': scores[primary_cause],
            'all_causes': scores
        }
    
    def adapt_interaction(self, patient_profile, root_cause_assessment, interaction_context):
        """
        Adapt interaction approach based on root cause assessment.
        
        Args:
            patient_profile: Patient's cognitive profile and preferences
            root_cause_assessment: Result from infer_root_cause
            interaction_context: Current context (exercise, reminder, etc.)
            
        Returns:
            dict: Adapted interaction parameters
        """
        primary_cause = root_cause_assessment['primary_cause']
        confidence = root_cause_assessment['confidence']
        
        # Default adaptations
        adaptations = {
            'complexity_level': 'medium',
            'pace': 'normal',
            'modality': 'visual_and_audio',
            'repetition': 1,
            'guidance_level': 'medium',
            'emotional_tone': 'neutral'
        }
        
        # Adapt based on primary cause
        if primary_cause == 'cognitive_load' and confidence > 0.5:
            adaptations['complexity_level'] = 'low'
            adaptations['pace'] = 'slow'
            adaptations['repetition'] = 2
            adaptations['guidance_level'] = 'high'
            
        elif primary_cause == 'emotional_state' and confidence > 0.5:
            adaptations['emotional_tone'] = 'soothing'
            adaptations['pace'] = 'slow'
            adaptations['guidance_level'] = 'high'
            
        elif primary_cause == 'memory_degradation' and confidence > 0.5:
            adaptations['repetition'] = 3
            adaptations['modality'] = 'visual_and_audio'
            adaptations['guidance_level'] = 'high'
            
        elif primary_cause == 'communication_barrier' and confidence > 0.5:
            adaptations['modality'] = 'visual_primary'
            adaptations['pace'] = 'slow'
            adaptations['complexity_level'] = 'low'
        
        # Factor in patient preferences from profile
        if patient_profile:
            if 'preferred_pace' in patient_profile:
                adaptations['pace'] = patient_profile['preferred_pace']
                
            if 'preferred_modality' in patient_profile:
                adaptations['modality'] = patient_profile['preferred_modality']
        
        # Consider interaction context
        if interaction_context:
            if interaction_context.get('type') == 'reminder' and interaction_context.get('urgency') == 'high':
                adaptations['repetition'] += 1
                adaptations['emotional_tone'] = 'firm'
                
            if interaction_context.get('type') == 'exercise' and interaction_context.get('difficulty') == 'hard':
                adaptations['guidance_level'] = 'high'
                adaptations['pace'] = 'slower'
        
        # Log the adaptation process
        self.logger.info(f"Adapted interaction for root cause '{primary_cause}' (confidence: {confidence:.2f})")
        
        return adaptations
    
    def update_weights(self, observation_data, actual_cause, success_rate):
        """
        Update factor weights based on success of interventions.
        
        Args:
            observation_data: The observed factors
            actual_cause: The verified root cause (from caregiver/patient feedback)
            success_rate: How effective the intervention was (0.0-1.0)
            
        Returns:
            bool: Success of update
        """
        try:
            # Get factors relevant to the actual cause
            relevant_factors = self.root_causes.get(actual_cause, {}).get('factors', [])
            
            # Update weights for relevant factors
            for factor in relevant_factors:
                if factor in observation_data and factor in self.factor_weights:
                    # Adjust weight based on success rate and observation
                    adjustment = (success_rate - 0.5) * 0.1  # Small adjustment
                    self.factor_weights[factor] += adjustment
                    
                    # Ensure weight stays in reasonable range
                    self.factor_weights[factor] = max(0.1, min(1.0, self.factor_weights[factor]))
            
            self.logger.info(f"Updated weights for root cause '{actual_cause}' based on success rate {success_rate:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating weights: {str(e)}")
            return False
    
    def get_cognitive_insights(self, patient_id, timeframe='week'):
        """
        Analyze cognitive patterns over time for a patient.
        
        Args:
            patient_id: ID of the patient
            timeframe: 'day', 'week', 'month'
            
        Returns:
            dict: Insights about cognitive patterns
        """
        # This would analyze stored data about a patient's cognitive performance over time
        # In a real implementation, this would query a database of observations
        
        # For now, we'll return placeholder insights
        insights = {
            'patient_id': patient_id,
            'timeframe': timeframe,
            'analysis_date': datetime.utcnow().isoformat(),
            'patterns': {
                'memory': {
                    'trend': 'stable',
                    'strength': 0.65,
                    'notes': 'Short-term memory retention appears stable'
                },
                'attention': {
                    'trend': 'declining',
                    'strength': 0.48,
                    'notes': 'Attention span showing gradual decrease'
                },
                'language': {
                    'trend': 'stable',
                    'strength': 0.72,
                    'notes': 'Language comprehension remains consistent'
                },
                'problem_solving': {
                    'trend': 'improving',
                    'strength': 0.58,
                    'notes': 'Showing improvement in sequential reasoning tasks'
                }
            },
            'recommendations': [
                'Focus on attention-building exercises',
                'Maintain current language activities',
                'Continue with puzzle-based problem solving tasks'
            ]
        }
        
        return insights