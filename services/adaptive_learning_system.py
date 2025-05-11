import logging
import time
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random
import math

class AdaptiveLearningSystem:
    """
    Adaptive Learning System that personalizes cognitive exercises and learning content 
    based on patient performance and needs. It dynamically adjusts difficulty and 
    focus areas to optimize cognitive stimulation.
    """
    
    def __init__(self):
        """Initialize the adaptive learning system."""
        self.logger = logging.getLogger(__name__)
        
        # Patient learning models
        self.patient_models: Dict[str, Dict[str, Any]] = {}
        
        # History of patient interactions
        self.interaction_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Cognitive domain weights
        self.cognitive_domains = {
            'memory': {
                'weight': 1.0,
                'decay_rate': 0.05,  # How quickly skills deteriorate without practice
                'exercises': ['memory_match', 'sequence_recall', 'word_recall', 'picture_recall']
            },
            'attention': {
                'weight': 1.0,
                'decay_rate': 0.03,
                'exercises': ['focus_finder', 'attention_shift', 'sustained_attention']
            },
            'language': {
                'weight': 1.0,
                'decay_rate': 0.04,
                'exercises': ['word_association', 'naming_objects', 'sentence_completion']
            },
            'executive_function': {
                'weight': 1.0,
                'decay_rate': 0.06,
                'exercises': ['planning', 'problem_solving', 'task_switching']
            },
            'visual_spatial': {
                'weight': 1.0,
                'decay_rate': 0.03,
                'exercises': ['spatial_orientation', 'pattern_recognition', 'visual_memory']
            }
        }
        
        # Learning rate factors (how quickly patients improve)
        self.learning_rates = {
            'fast': 0.15,
            'medium': 0.1,
            'slow': 0.05
        }
        
        # Difficulty adjustment factors
        self.difficulty_levels = ['very_easy', 'easy', 'medium', 'hard', 'very_hard']
        self.difficulty_thresholds = {
            'very_easy': 0.3,
            'easy': 0.5,
            'medium': 0.7,
            'hard': 0.85,
            'very_hard': 0.95
        }
        
        self.logger.info("Adaptive Learning System initialized")
    
    def initialize_patient_model(self, patient_id: str, demographics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize a new patient learning model.
        
        Args:
            patient_id: Patient's unique identifier
            demographics: Optional demographic data to inform initial model
            
        Returns:
            New patient model
        """
        # Default initial model
        model = {
            'patient_id': patient_id,
            'created_at': time.time(),
            'last_updated': time.time(),
            'learning_rate': 'medium',  # Default to medium learning rate
            'cognitive_domains': {},
            'preferences': {
                'content_types': {
                    'visual': 0.5,
                    'auditory': 0.5,
                    'text': 0.5
                },
                'themes': {},
                'session_length': 15,  # Minutes
                'session_frequency': 1  # Times per day
            },
            'engagement_metrics': {
                'completion_rate': 0.0,
                'average_session_duration': 0.0,
                'last_session': None,
                'total_sessions': 0,
                'streak_days': 0
            },
            'next_exercises': [],
            'completed_exercises': []
        }
        
        # Initialize cognitive domains with default values
        for domain, data in self.cognitive_domains.items():
            model['cognitive_domains'][domain] = {
                'current_level': 0.4,  # Start at 40% of normal capacity
                'difficulty': 'medium',
                'improvement_rate': 0.0,
                'focus_score': 1.0,    # Default focus weight
                'last_practice': None,
                'exercises_completed': 0
            }
        
        # Adjust model based on demographics if provided
        if demographics:
            age = demographics.get('age')
            if age:
                # Adjust initial levels based on age
                if age > 85:
                    self._adjust_all_domains(model, -0.15)  # More significant impairment
                    model['learning_rate'] = 'slow'
                elif age > 75:
                    self._adjust_all_domains(model, -0.1)
                elif age > 65:
                    self._adjust_all_domains(model, -0.05)
            
            # Adjust based on diagnosis severity if available
            diagnosis = demographics.get('diagnosis')
            if diagnosis:
                severity = diagnosis.get('severity', 'mild')
                if severity == 'severe':
                    self._adjust_all_domains(model, -0.2)
                    model['learning_rate'] = 'slow'
                elif severity == 'moderate':
                    self._adjust_all_domains(model, -0.1)
                    model['learning_rate'] = 'medium'
                # mild is default
            
            # Adjust based on education level
            education = demographics.get('education_years')
            if education:
                if education > 16:  # Post-graduate
                    self._adjust_all_domains(model, 0.05)  # Cognitive reserve
                elif education > 12:  # College
                    self._adjust_all_domains(model, 0.03)
            
            # Initialize content preferences based on patient interests
            interests = demographics.get('interests', [])
            for interest in interests:
                model['preferences']['themes'][interest] = 0.8  # High preference for interests
        
        # Store the model
        self.patient_models[patient_id] = model
        self.interaction_history[patient_id] = []
        
        return model
    
    def _adjust_all_domains(self, model: Dict[str, Any], adjustment: float) -> None:
        """Helper to adjust all cognitive domains by a fixed amount."""
        for domain in model['cognitive_domains']:
            current = model['cognitive_domains'][domain]['current_level']
            # Ensure level stays between 0.1 and 1.0
            model['cognitive_domains'][domain]['current_level'] = max(0.1, min(1.0, current + adjustment))
    
    def get_patient_model(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a patient's learning model.
        
        Args:
            patient_id: Patient's unique identifier
            
        Returns:
            Patient model or None if not found
        """
        return self.patient_models.get(patient_id)
    
    def recommend_exercises(self, patient_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Recommend the next set of exercises for a patient.
        
        Args:
            patient_id: Patient's unique identifier
            count: Number of exercises to recommend
            
        Returns:
            List of recommended exercises
        """
        model = self.get_patient_model(patient_id)
        
        if not model:
            self.logger.warning(f"No model found for patient {patient_id}")
            return []
        
        # Get the current focus domains (sorted by focus score)
        domains = sorted(
            model['cognitive_domains'].items(),
            key=lambda x: x[1]['focus_score'],
            reverse=True
        )
        
        # Calculate time since last practice for each domain
        current_time = time.time()
        for domain, data in domains:
            last_practice = data.get('last_practice')
            if last_practice:
                days_since_practice = (current_time - last_practice) / (24 * 3600)
                # Increase focus score for domains not practiced recently
                decay_factor = min(days_since_practice * 0.1, 0.5)
                model['cognitive_domains'][domain]['focus_score'] += decay_factor
        
        # Apply cognitive domain weights to focus scores
        weighted_domains = []
        for domain, data in domains:
            domain_weight = self.cognitive_domains[domain]['weight']
            focus_score = data['focus_score'] * domain_weight
            weighted_domains.append((domain, data, focus_score))
        
        # Sort domains by weighted focus score
        weighted_domains.sort(key=lambda x: x[2], reverse=True)
        
        # Select exercises proportionally from top domains
        recommendations = []
        for i in range(count):
            if i < len(weighted_domains):
                domain, data, _ = weighted_domains[i]
                difficulty = data['difficulty']
                
                # Get eligible exercises for this domain
                eligible_exercises = self.cognitive_domains[domain]['exercises']
                
                # Filter out recently completed exercises
                completed = set(ex['exercise_id'] for ex in model['completed_exercises'][-5:])
                candidates = [ex for ex in eligible_exercises if ex not in completed]
                
                if not candidates:
                    candidates = eligible_exercises  # Fall back if all have been done recently
                
                # Select a random exercise from candidates
                exercise_id = random.choice(candidates)
                
                recommendations.append({
                    'exercise_id': exercise_id,
                    'domain': domain,
                    'difficulty': difficulty,
                    'parameters': self._generate_exercise_parameters(exercise_id, difficulty)
                })
            else:
                # If we need more exercises than domains, select from lower priority domains
                remaining_domains = weighted_domains[:]
                random.shuffle(remaining_domains)
                
                domain, data, _ = remaining_domains[0]
                difficulty = data['difficulty']
                exercise_id = random.choice(self.cognitive_domains[domain]['exercises'])
                
                recommendations.append({
                    'exercise_id': exercise_id,
                    'domain': domain,
                    'difficulty': difficulty,
                    'parameters': self._generate_exercise_parameters(exercise_id, difficulty)
                })
        
        # Store recommendations in the model
        model['next_exercises'] = recommendations
        model['last_updated'] = time.time()
        
        return recommendations
    
    def _generate_exercise_parameters(self, exercise_id: str, difficulty: str) -> Dict[str, Any]:
        """Generate parameters for an exercise based on difficulty."""
        params = {
            'difficulty': difficulty
        }
        
        # Common parameters by difficulty level
        if difficulty == 'very_easy':
            params.update({
                'time_limit': 300,  # 5 minutes
                'items_count': 3,
                'assistance_level': 'high'
            })
        elif difficulty == 'easy':
            params.update({
                'time_limit': 240,
                'items_count': 5,
                'assistance_level': 'medium'
            })
        elif difficulty == 'medium':
            params.update({
                'time_limit': 180,
                'items_count': 8,
                'assistance_level': 'low'
            })
        elif difficulty == 'hard':
            params.update({
                'time_limit': 150,
                'items_count': 12,
                'assistance_level': 'minimal'
            })
        elif difficulty == 'very_hard':
            params.update({
                'time_limit': 120,
                'items_count': 15,
                'assistance_level': 'none'
            })
        
        # Exercise-specific parameters
        if exercise_id == 'memory_match':
            # Set pairs count based on difficulty
            params['pairs_count'] = params.pop('items_count') // 2
        elif exercise_id == 'sequence_recall':
            # Set sequence length
            params['sequence_length'] = params.pop('items_count')
        elif exercise_id == 'word_recall':
            # Set word count
            params['word_count'] = params.pop('items_count')
            # Add distractor words
            params['distractor_count'] = int(params['word_count'] * 0.5)
        
        return params
    
    def process_exercise_result(self, patient_id: str, exercise_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process results from a completed exercise and update patient model.
        
        Args:
            patient_id: Patient's unique identifier
            exercise_result: Exercise result data including score, completion time, etc.
            
        Returns:
            Updated patient model with analysis and next recommendations
        """
        model = self.get_patient_model(patient_id)
        
        if not model:
            self.logger.warning(f"No model found for patient {patient_id}")
            return {}
        
        # Extract exercise data
        exercise_id = exercise_result.get('exercise_id')
        domain = exercise_result.get('domain')
        score = exercise_result.get('score', 0.0)
        completion_time = exercise_result.get('completion_time', 0)
        
        # Find the matching domain if not provided
        if not domain:
            for d, data in self.cognitive_domains.items():
                if exercise_id in data['exercises']:
                    domain = d
                    break
        
        if not domain:
            self.logger.warning(f"Could not identify domain for exercise {exercise_id}")
            return model
        
        # Record the exercise completion
        model['completed_exercises'].append({
            'exercise_id': exercise_id,
            'domain': domain,
            'score': score,
            'completion_time': completion_time,
            'timestamp': time.time()
        })
        
        # Trim completed exercises list if it gets too long
        if len(model['completed_exercises']) > 100:
            model['completed_exercises'] = model['completed_exercises'][-100:]
        
        # Update domain-specific metrics
        domain_data = model['cognitive_domains'][domain]
        domain_data['last_practice'] = time.time()
        domain_data['exercises_completed'] += 1
        
        # Determine learning rate factor
        learning_rate_factor = self.learning_rates[model['learning_rate']]
        
        # Update current level based on performance
        current_level = domain_data['current_level']
        expected_score = self._calculate_expected_score(domain_data['difficulty'])
        performance_delta = score - expected_score
        
        # Adjust level based on performance
        adjustment = performance_delta * learning_rate_factor
        new_level = max(0.1, min(1.0, current_level + adjustment))
        domain_data['current_level'] = new_level
        
        # Track improvement rate
        if domain_data['exercises_completed'] > 1:
            domain_data['improvement_rate'] = (new_level - current_level) / learning_rate_factor
        
        # Update difficulty based on new level
        new_difficulty = self._determine_difficulty(new_level)
        domain_data['difficulty'] = new_difficulty
        
        # Update focus score - reduce focus for just-practiced domain
        domain_data['focus_score'] = max(0.5, domain_data['focus_score'] - 0.2)
        
        # Update engagement metrics
        engagement = model['engagement_metrics']
        engagement['total_sessions'] += 1
        
        # Update completion rate
        total_assigned = len(model.get('next_exercises', []))
        if total_assigned > 0:
            completed = sum(1 for ex in model['completed_exercises'] 
                          if ex['timestamp'] > model['last_updated'])
            completion_rate = completed / total_assigned
            # Exponential moving average to smooth out changes
            engagement['completion_rate'] = 0.8 * engagement['completion_rate'] + 0.2 * completion_rate
        
        # Update session duration
        engagement['average_session_duration'] = (0.8 * engagement['average_session_duration'] 
                                              + 0.2 * completion_time)
        
        # Check for streak days
        last_session = engagement['last_session']
        now = time.time()
        today = datetime.fromtimestamp(now).date()
        
        if last_session:
            last_date = datetime.fromtimestamp(last_session).date()
            if today - last_date == timedelta(days=1):
                # Consecutive day
                engagement['streak_days'] += 1
            elif today > last_date + timedelta(days=1):
                # Streak broken
                engagement['streak_days'] = 1
        else:
            # First session
            engagement['streak_days'] = 1
        
        engagement['last_session'] = now
        
        # Record interaction
        self.interaction_history[patient_id].append({
            'type': 'exercise_completion',
            'exercise_id': exercise_id,
            'domain': domain,
            'score': score,
            'completion_time': completion_time,
            'difficulty': domain_data['difficulty'],
            'timestamp': time.time()
        })
        
        # Update model timestamp
        model['last_updated'] = time.time()
        
        # Generate new exercise recommendations
        self.recommend_exercises(patient_id)
        
        return model
    
    def _calculate_expected_score(self, difficulty: str) -> float:
        """Calculate expected score based on difficulty level."""
        difficulty_penalties = {
            'very_easy': 0.0,
            'easy': 0.1,
            'medium': 0.2,
            'hard': 0.3,
            'very_hard': 0.4
        }
        
        # Base expected score is 0.9 (90%) with penalties for higher difficulties
        return max(0.5, 0.9 - difficulty_penalties.get(difficulty, 0.2))
    
    def _determine_difficulty(self, level: float) -> str:
        """Determine appropriate difficulty based on cognitive level."""
        # Convert level to difficulty
        for difficulty, threshold in reversed(sorted(self.difficulty_thresholds.items(), key=lambda x: x[1])):
            if level >= threshold:
                return difficulty
        
        # Default to very easy
        return 'very_easy'
    
    def update_preferences(self, patient_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update a patient's preferences.
        
        Args:
            patient_id: Patient's unique identifier
            preferences: New preference settings
            
        Returns:
            Success status
        """
        model = self.get_patient_model(patient_id)
        
        if not model:
            self.logger.warning(f"No model found for patient {patient_id}")
            return False
        
        # Update content type preferences
        content_types = preferences.get('content_types')
        if content_types:
            for content_type, value in content_types.items():
                model['preferences']['content_types'][content_type] = value
        
        # Update theme preferences
        themes = preferences.get('themes')
        if themes:
            for theme, value in themes.items():
                model['preferences']['themes'][theme] = value
        
        # Update session preferences
        session_length = preferences.get('session_length')
        if session_length:
            model['preferences']['session_length'] = session_length
        
        session_frequency = preferences.get('session_frequency')
        if session_frequency:
            model['preferences']['session_frequency'] = session_frequency
        
        # Record interaction
        self.interaction_history[patient_id].append({
            'type': 'preference_update',
            'preferences': preferences,
            'timestamp': time.time()
        })
        
        # Update model timestamp
        model['last_updated'] = time.time()
        
        return True
    
    def generate_progress_report(self, patient_id: str, period: str = 'week') -> Dict[str, Any]:
        """
        Generate a progress report for a patient.
        
        Args:
            patient_id: Patient's unique identifier
            period: Time period ('day', 'week', 'month')
            
        Returns:
            Progress report data
        """
        model = self.get_patient_model(patient_id)
        
        if not model:
            self.logger.warning(f"No model found for patient {patient_id}")
            return {}
        
        # Determine time range
        now = time.time()
        if period == 'day':
            start_time = now - (24 * 3600)
        elif period == 'week':
            start_time = now - (7 * 24 * 3600)
        elif period == 'month':
            start_time = now - (30 * 24 * 3600)
        else:
            start_time = now - (7 * 24 * 3600)  # Default to week
        
        # Get recent exercise completions
        recent_exercises = [
            ex for ex in model['completed_exercises']
            if ex.get('timestamp', 0) >= start_time
        ]
        
        # Skip if no recent exercises
        if not recent_exercises:
            return {
                'patient_id': patient_id,
                'period': period,
                'exercises_completed': 0,
                'average_score': 0,
                'domains': {},
                'recommendations': []
            }
        
        # Calculate overall metrics
        total_exercises = len(recent_exercises)
        average_score = sum(ex.get('score', 0) for ex in recent_exercises) / total_exercises
        
        # Calculate domain-specific metrics
        domains = {}
        for domain in self.cognitive_domains:
            domain_exercises = [ex for ex in recent_exercises if ex.get('domain') == domain]
            
            if domain_exercises:
                domain_count = len(domain_exercises)
                domain_score = sum(ex.get('score', 0) for ex in domain_exercises) / domain_count
                
                # Get current level and comparison to previous
                current_level = model['cognitive_domains'][domain]['current_level']
                
                # Find the first exercise before the period to get the old level
                old_level = 0.4  # Default starting level
                history = self.interaction_history.get(patient_id, [])
                filtered_history = [
                    h for h in history
                    if h.get('type') == 'exercise_completion' and
                    h.get('domain') == domain and
                    h.get('timestamp', 0) < start_time
                ]
                
                if filtered_history:
                    # Get the most recent exercise before the period
                    filtered_history.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
                    prev_exercise = filtered_history[0]
                    # Estimate the level after this exercise
                    exercise_count = sum(1 for h in history 
                                    if h.get('type') == 'exercise_completion' and 
                                    h.get('domain') == domain and
                                    h.get('timestamp', 0) <= prev_exercise.get('timestamp', 0))
                    # Simple heuristic to estimate old level
                    old_level = min(0.9, 0.4 + 0.05 * exercise_count)
                
                domains[domain] = {
                    'exercises_completed': domain_count,
                    'average_score': domain_score,
                    'current_level': current_level,
                    'level_change': current_level - old_level,
                    'level_change_percent': (current_level - old_level) / old_level * 100 if old_level > 0 else 0
                }
        
        # Generate personalized recommendations
        recommendations = []
        
        # Find domains with lower performance
        weak_domains = sorted(
            [(domain, data) for domain, data in domains.items()],
            key=lambda x: (x[1]['average_score'], x[1]['current_level'])
        )
        
        if weak_domains:
            weak_domain, weak_data = weak_domains[0]
            recommendations.append({
                'type': 'focus_area',
                'domain': weak_domain,
                'message': f"Focus on {weak_domain.replace('_', ' ')} exercises to improve cognitive balance."
            })
        
        # Check for streak recommendations
        streak_days = model['engagement_metrics']['streak_days']
        if streak_days > 0:
            if streak_days >= 7:
                recommendations.append({
                    'type': 'engagement',
                    'message': f"Great job maintaining a {streak_days}-day streak! Consistency is key for cognitive health."
                })
            else:
                recommendations.append({
                    'type': 'engagement',
                    'message': f"You're on a {streak_days}-day streak. Keep it going!"
                })
        else:
            recommendations.append({
                'type': 'engagement',
                'message': "Try to practice daily for the best results in maintaining cognitive abilities."
            })
        
        # Check completion rate
        completion_rate = model['engagement_metrics']['completion_rate']
        if completion_rate < 0.7:
            recommendations.append({
                'type': 'adherence',
                'message': "Try to complete all recommended exercises for maximum benefit."
            })
        
        # Return the report
        return {
            'patient_id': patient_id,
            'period': period,
            'exercises_completed': total_exercises,
            'average_score': average_score,
            'domains': domains,
            'recommendations': recommendations
        }
    
    def apply_cognitive_decay(self, patient_id: str) -> bool:
        """
        Apply natural cognitive decay for time periods without practice.
        This simulates the deterioration of cognitive abilities without regular exercise.
        
        Args:
            patient_id: Patient's unique identifier
            
        Returns:
            Success status
        """
        model = self.get_patient_model(patient_id)
        
        if not model:
            self.logger.warning(f"No model found for patient {patient_id}")
            return False
        
        # Current time
        now = time.time()
        
        # Check each domain for decay
        for domain, domain_data in model['cognitive_domains'].items():
            last_practice = domain_data.get('last_practice')
            
            if last_practice:
                # Calculate days since last practice
                days_since_practice = (now - last_practice) / (24 * 3600)
                
                # Only apply decay if more than 1 day since practice
                if days_since_practice > 1:
                    # Get domain decay rate
                    decay_rate = self.cognitive_domains[domain]['decay_rate']
                    
                    # Calculate decay amount (more days = more decay, but with diminishing effect)
                    decay_amount = decay_rate * math.log(days_since_practice + 1, 10)
                    
                    # Apply decay to current level (limited to prevent dropping below minimum)
                    current_level = domain_data['current_level']
                    new_level = max(0.1, current_level - decay_amount)
                    domain_data['current_level'] = new_level
                    
                    # Update focus score to emphasize domains that haven't been practiced
                    domain_data['focus_score'] = min(2.0, domain_data['focus_score'] + (0.1 * days_since_practice))
        
        # Update model timestamp
        model['last_updated'] = now
        
        return True
    
    def save_models(self, file_path: str) -> bool:
        """
        Save all patient models to a file.
        
        Args:
            file_path: Path to save the models
            
        Returns:
            Success status
        """
        try:
            # Create directory if doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save models
            with open(file_path, 'w') as f:
                json.dump({
                    'models': self.patient_models,
                    'timestamp': time.time()
                }, f)
            
            self.logger.info(f"Saved {len(self.patient_models)} patient models to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving patient models: {str(e)}")
            return False
    
    def load_models(self, file_path: str) -> bool:
        """
        Load patient models from a file.
        
        Args:
            file_path: Path to load the models from
            
        Returns:
            Success status
        """
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"Model file {file_path} does not exist")
                return False
                
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.patient_models = data.get('models', {})
                
            # Initialize interaction history for loaded models
            for patient_id in self.patient_models:
                if patient_id not in self.interaction_history:
                    self.interaction_history[patient_id] = []
            
            self.logger.info(f"Loaded {len(self.patient_models)} patient models from {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading patient models: {str(e)}")
            return False