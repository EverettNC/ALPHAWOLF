import logging
import json
from datetime import datetime, timedelta
import os
import random

logger = logging.getLogger(__name__)

class LearningJourney:
    """Service for tracking patient progress in cognitive exercises and reminders."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.learning_logs = {}
        
        # Load existing logs if available
        self.log_path = os.path.join('data', 'learning_log.json')
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path, 'r') as f:
                    self.learning_logs = json.load(f)
                self.logger.info(f"Loaded learning logs from {self.log_path}")
        except Exception as e:
            self.logger.error(f"Error loading learning logs: {str(e)}")
        
        # Define skill domains and cognitive areas
        self.skill_domains = {
            'memory': {
                'description': 'Ability to recall and recognize information',
                'exercises': ['memory_match', 'sequence_recall', 'word_recall', 'picture_recall', 'story_recall'],
                'metrics': ['accuracy', 'recall_speed', 'retention_duration']
            },
            'attention': {
                'description': 'Ability to focus and maintain concentration',
                'exercises': ['visual_search', 'sustained_attention', 'divided_attention', 'selective_attention'],
                'metrics': ['focus_duration', 'distraction_resistance', 'task_completion']
            },
            'language': {
                'description': 'Verbal communication and comprehension skills',
                'exercises': ['word_association', 'verbal_fluency', 'reading_comprehension', 'naming'],
                'metrics': ['vocabulary_range', 'comprehension_accuracy', 'expression_clarity']
            },
            'executive_function': {
                'description': 'Planning, decision-making, and problem-solving',
                'exercises': ['problem_solving', 'planning', 'inhibition_control', 'task_switching'],
                'metrics': ['strategy_use', 'problem_completion', 'adaptation_speed']
            },
            'orientation': {
                'description': 'Awareness of time, place, and situation',
                'exercises': ['time_orientation', 'place_recognition', 'personal_orientation', 'situational_awareness'],
                'metrics': ['context_recognition', 'navigation_ability', 'temporal_awareness']
            }
        }
        
        # Define progression levels for each domain
        self.progression_levels = {
            'beginner': {
                'range': (0.0, 0.3),
                'adaptation': {
                    'complexity': 'low',
                    'assistance': 'high',
                    'pace': 'slow',
                    'feedback': 'immediate',
                    'repetition': 'high'
                }
            },
            'intermediate': {
                'range': (0.3, 0.6),
                'adaptation': {
                    'complexity': 'medium',
                    'assistance': 'medium',
                    'pace': 'moderate',
                    'feedback': 'periodic',
                    'repetition': 'medium'
                }
            },
            'advanced': {
                'range': (0.6, 0.8),
                'adaptation': {
                    'complexity': 'high',
                    'assistance': 'low',
                    'pace': 'normal',
                    'feedback': 'summary',
                    'repetition': 'low'
                }
            },
            'expert': {
                'range': (0.8, 1.0),
                'adaptation': {
                    'complexity': 'very high',
                    'assistance': 'minimal',
                    'pace': 'fast',
                    'feedback': 'end-only',
                    'repetition': 'very low'
                }
            }
        }
        
        self.logger.info("Learning Journey initialized")
    
    def log_exercise_result(self, patient_id, exercise_data, result_data):
        """
        Log a cognitive exercise result and update patient's learning journey.
        
        Args:
            patient_id: ID of the patient
            exercise_data: Data about the exercise (type, difficulty, etc.)
            result_data: Performance results (score, completion time, etc.)
            
        Returns:
            dict: Updated journey data
        """
        try:
            # Initialize patient's learning log if needed
            if patient_id not in self.learning_logs:
                self.learning_logs[patient_id] = {
                    'exercises': [],
                    'reminders': [],
                    'skill_levels': {
                        'memory': 0.2,
                        'attention': 0.2,
                        'language': 0.2,
                        'executive_function': 0.2,
                        'orientation': 0.2
                    },
                    'learning_patterns': {},
                    'last_update': datetime.utcnow().isoformat()
                }
            
            # Get exercise domain
            exercise_type = exercise_data.get('type', 'unknown')
            domain = self._get_exercise_domain(exercise_type)
            
            # Calculate metrics
            score = result_data.get('score', 0.0)
            completion_time = result_data.get('completion_time', 0.0)
            attempts = result_data.get('attempts', 1)
            
            # Normalize score to 0-1 range if needed
            if score > 1.0:
                score = score / 100.0
            
            # Create exercise log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'exercise_type': exercise_type,
                'difficulty': exercise_data.get('difficulty', 'medium'),
                'domain': domain,
                'score': score,
                'completion_time': completion_time,
                'attempts': attempts,
                'metrics': {
                    'accuracy': score,
                    'efficiency': 1.0 / (1.0 + completion_time / 60.0) if completion_time > 0 else 0.5,
                    'persistence': 1.0 / attempts if attempts > 0 else 0.5
                }
            }
            
            # Add to log
            self.learning_logs[patient_id]['exercises'].append(log_entry)
            
            # Update skill levels
            if domain in self.learning_logs[patient_id]['skill_levels']:
                # Calculate new skill level with weighted average
                # Recent performance has higher weight
                current_level = self.learning_logs[patient_id]['skill_levels'][domain]
                performance_weight = 0.3  # 30% weight for new performance
                new_level = (current_level * (1 - performance_weight)) + (score * performance_weight)
                
                # Apply constraints
                new_level = max(0.1, min(1.0, new_level))
                
                # Update level
                self.learning_logs[patient_id]['skill_levels'][domain] = new_level
            
            # Update learning patterns
            time_of_day = datetime.utcnow().strftime('%H')
            if 'performance_by_time' not in self.learning_logs[patient_id]['learning_patterns']:
                self.learning_logs[patient_id]['learning_patterns']['performance_by_time'] = {}
            
            if time_of_day not in self.learning_logs[patient_id]['learning_patterns']['performance_by_time']:
                self.learning_logs[patient_id]['learning_patterns']['performance_by_time'][time_of_day] = []
            
            self.learning_logs[patient_id]['learning_patterns']['performance_by_time'][time_of_day].append(score)
            
            # Update timestamp
            self.learning_logs[patient_id]['last_update'] = datetime.utcnow().isoformat()
            
            # Save logs
            self._save_logs()
            
            return self.learning_logs[patient_id]
        
        except Exception as e:
            self.logger.error(f"Error logging exercise result: {str(e)}")
            return None
    
    def log_reminder_result(self, patient_id, reminder_data, result_data):
        """
        Log a reminder result and update patient's adherence patterns.
        
        Args:
            patient_id: ID of the patient
            reminder_data: Data about the reminder (type, time, etc.)
            result_data: Result data (acknowledged, completed, etc.)
            
        Returns:
            dict: Updated journey data
        """
        try:
            # Initialize patient's learning log if needed
            if patient_id not in self.learning_logs:
                self.learning_logs[patient_id] = {
                    'exercises': [],
                    'reminders': [],
                    'skill_levels': {
                        'memory': 0.2,
                        'attention': 0.2,
                        'language': 0.2,
                        'executive_function': 0.2,
                        'orientation': 0.2
                    },
                    'learning_patterns': {},
                    'last_update': datetime.utcnow().isoformat()
                }
            
            # Create reminder log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'reminder_id': reminder_data.get('id', ''),
                'title': reminder_data.get('title', ''),
                'scheduled_time': reminder_data.get('time', ''),
                'acknowledged': result_data.get('acknowledged', False),
                'completed': result_data.get('completed', False),
                'response_time': result_data.get('response_time', 0.0),  # in seconds
                'metrics': {
                    'adherence': 1.0 if result_data.get('completed', False) else 0.0,
                    'promptness': 1.0 / (1.0 + result_data.get('response_time', 0.0) / 60.0)
                }
            }
            
            # Add to log
            self.learning_logs[patient_id]['reminders'].append(log_entry)
            
            # Update reminder patterns
            reminder_type = reminder_data.get('type', 'general')
            if 'adherence_by_type' not in self.learning_logs[patient_id]['learning_patterns']:
                self.learning_logs[patient_id]['learning_patterns']['adherence_by_type'] = {}
            
            if reminder_type not in self.learning_logs[patient_id]['learning_patterns']['adherence_by_type']:
                self.learning_logs[patient_id]['learning_patterns']['adherence_by_type'][reminder_type] = []
            
            adherence_score = 1.0 if result_data.get('completed', False) else 0.0
            self.learning_logs[patient_id]['learning_patterns']['adherence_by_type'][reminder_type].append(adherence_score)
            
            # Update orientation skill level based on reminder adherence
            if 'orientation' in self.learning_logs[patient_id]['skill_levels']:
                current_level = self.learning_logs[patient_id]['skill_levels']['orientation']
                adherence_weight = 0.1  # 10% weight for reminder adherence
                new_level = (current_level * (1 - adherence_weight)) + (adherence_score * adherence_weight)
                
                # Apply constraints
                new_level = max(0.1, min(1.0, new_level))
                
                # Update level
                self.learning_logs[patient_id]['skill_levels']['orientation'] = new_level
            
            # Update timestamp
            self.learning_logs[patient_id]['last_update'] = datetime.utcnow().isoformat()
            
            # Save logs
            self._save_logs()
            
            return self.learning_logs[patient_id]
        
        except Exception as e:
            self.logger.error(f"Error logging reminder result: {str(e)}")
            return None
    
    def get_learning_journey(self, patient_id):
        """
        Get a patient's complete learning journey.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: Learning journey data
        """
        return self.learning_logs.get(patient_id, {})
    
    def get_skill_levels(self, patient_id):
        """
        Get a patient's current skill levels in different domains.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: Skill levels by domain
        """
        journey = self.learning_logs.get(patient_id, {})
        return journey.get('skill_levels', {})
    
    def get_progression_level(self, patient_id, domain):
        """
        Get a patient's progression level in a specific domain.
        
        Args:
            patient_id: ID of the patient
            domain: Skill domain (memory, attention, etc.)
            
        Returns:
            tuple: (level_name, adaptation_parameters)
        """
        skill_levels = self.get_skill_levels(patient_id)
        skill_level = skill_levels.get(domain, 0.2)
        
        # Determine progression level based on skill level
        for level_name, level_data in self.progression_levels.items():
            level_range = level_data['range']
            if level_range[0] <= skill_level < level_range[1]:
                return (level_name, level_data['adaptation'])
        
        # Default to beginner if no match
        return ('beginner', self.progression_levels['beginner']['adaptation'])
    
    def recommend_exercises(self, patient_id, count=3):
        """
        Recommend cognitive exercises tailored to patient's needs.
        
        Args:
            patient_id: ID of the patient
            count: Number of exercises to recommend
            
        Returns:
            list: Recommended exercises
        """
        try:
            # Get patient's skill levels
            skill_levels = self.get_skill_levels(patient_id)
            
            # Find domains that need most improvement (lowest scores)
            sorted_domains = sorted(skill_levels.items(), key=lambda x: x[1])
            focus_domains = [domain for domain, _ in sorted_domains[:2]]
            
            # If we don't have enough domains, add some
            while len(focus_domains) < 2:
                focus_domains.append(random.choice(list(self.skill_domains.keys())))
            
            # Get exercises for focus domains
            exercises = []
            for domain in focus_domains:
                # Get progression level to determine appropriate difficulty
                level_name, adaptations = self.get_progression_level(patient_id, domain)
                
                # Map progression level to exercise difficulty
                difficulty_map = {
                    'beginner': 'easy',
                    'intermediate': 'medium',
                    'advanced': 'hard',
                    'expert': 'hard'
                }
                difficulty = difficulty_map.get(level_name, 'medium')
                
                # Get domain exercises
                domain_exercises = self.skill_domains.get(domain, {}).get('exercises', [])
                
                # Add exercises with appropriate difficulty
                for exercise_type in domain_exercises:
                    exercises.append({
                        'type': exercise_type,
                        'domain': domain,
                        'difficulty': difficulty,
                        'adaptations': adaptations
                    })
            
            # Get recently completed exercises to avoid repetition
            recent_exercises = set()
            journey = self.learning_logs.get(patient_id, {})
            
            for log in journey.get('exercises', [])[-10:]:
                recent_exercises.add(log.get('exercise_type'))
            
            # Filter out recently completed exercises when possible
            filtered_exercises = [ex for ex in exercises if ex['type'] not in recent_exercises]
            
            # If we filtered out too many, add some back in
            if len(filtered_exercises) < count:
                filtered_exercises = exercises
            
            # Shuffle and return requested count
            random.shuffle(filtered_exercises)
            return filtered_exercises[:count]
        
        except Exception as e:
            self.logger.error(f"Error recommending exercises: {str(e)}")
            return []
    
    def analyze_learning_patterns(self, patient_id):
        """
        Analyze a patient's learning patterns for insights.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: Learning pattern insights
        """
        try:
            journey = self.learning_logs.get(patient_id, {})
            patterns = journey.get('learning_patterns', {})
            
            insights = {
                'optimal_time': '',
                'domain_preferences': [],
                'reminder_adherence': 0.0,
                'consistency': '',
                'progression_rate': '',
                'recommendations': []
            }
            
            # Determine optimal time of day for exercises
            if 'performance_by_time' in patterns:
                time_scores = {}
                for time, scores in patterns['performance_by_time'].items():
                    if scores:
                        time_scores[time] = sum(scores) / len(scores)
                
                if time_scores:
                    optimal_time = max(time_scores.items(), key=lambda x: x[1])
                    insights['optimal_time'] = f"{optimal_time[0]}:00"
            
            # Determine domain preferences
            skill_levels = journey.get('skill_levels', {})
            sorted_domains = sorted(skill_levels.items(), key=lambda x: x[1], reverse=True)
            insights['domain_preferences'] = [domain for domain, _ in sorted_domains[:2]]
            
            # Calculate reminder adherence
            reminder_logs = journey.get('reminders', [])
            if reminder_logs:
                completed_count = sum(1 for log in reminder_logs if log.get('completed', False))
                insights['reminder_adherence'] = completed_count / len(reminder_logs) if len(reminder_logs) > 0 else 0.0
            
            # Analyze consistency of practice
            exercise_logs = journey.get('exercises', [])
            if exercise_logs:
                dates = {}
                for log in exercise_logs:
                    date = log.get('timestamp', '').split('T')[0]
                    dates[date] = dates.get(date, 0) + 1
                
                avg_per_day = sum(dates.values()) / len(dates) if dates else 0
                
                if avg_per_day >= 3:
                    insights['consistency'] = 'high'
                elif avg_per_day >= 1:
                    insights['consistency'] = 'medium'
                else:
                    insights['consistency'] = 'low'
            
            # Determine progression rate
            # This would compare skill levels over time
            insights['progression_rate'] = 'steady'  # Placeholder
            
            # Generate recommendations
            if insights['consistency'] == 'low':
                insights['recommendations'].append('Increase exercise frequency to at least once daily')
            
            if insights['reminder_adherence'] < 0.7:
                insights['recommendations'].append('Improve reminder adherence with additional prompts or caregiver support')
            
            lowest_domain = sorted_domains[-1][0] if sorted_domains else ''
            if lowest_domain:
                insights['recommendations'].append(f'Focus on improving {lowest_domain} skills with targeted exercises')
            
            return insights
        except Exception as e:
            self.logger.error(f"Error analyzing learning patterns: {str(e)}")
            return {}
    
    def _get_exercise_domain(self, exercise_type):
        """Map exercise type to cognitive domain."""
        for domain, data in self.skill_domains.items():
            if exercise_type in data['exercises']:
                return domain
        return 'memory'  # Default domain
    
    def _save_logs(self):
        """Save learning logs to file."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            
            with open(self.log_path, 'w') as f:
                json.dump(self.learning_logs, f, indent=2)
            
            self.logger.debug(f"Saved learning logs to {self.log_path}")
        except Exception as e:
            self.logger.error(f"Error saving learning logs: {str(e)}")
    
    def get_statistics(self, patient_id, timeframe='month'):
        """
        Get statistics about a patient's learning journey.
        
        Args:
            patient_id: ID of the patient
            timeframe: 'week', 'month', or 'all'
            
        Returns:
            dict: Statistics about the learning journey
        """
        try:
            journey = self.learning_logs.get(patient_id, {})
            
            # Determine start date based on timeframe
            start_date = None
            if timeframe == 'week':
                start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
            elif timeframe == 'month':
                start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
            
            # Filter exercises by timeframe
            exercises = journey.get('exercises', [])
            if start_date:
                exercises = [ex for ex in exercises if ex.get('timestamp', '') >= start_date]
            
            # Filter reminders by timeframe
            reminders = journey.get('reminders', [])
            if start_date:
                reminders = [rem for rem in reminders if rem.get('timestamp', '') >= start_date]
            
            # Calculate statistics
            stats = {
                'total_exercises': len(exercises),
                'average_score': 0.0,
                'domain_breakdown': {},
                'difficulty_breakdown': {
                    'easy': 0,
                    'medium': 0,
                    'hard': 0
                },
                'total_reminders': len(reminders),
                'reminder_adherence': 0.0,
                'skill_levels': journey.get('skill_levels', {})
            }
            
            # Process exercises
            scores = []
            domain_counts = {}
            for exercise in exercises:
                scores.append(exercise.get('score', 0.0))
                
                domain = exercise.get('domain', 'unknown')
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
                
                difficulty = exercise.get('difficulty', 'medium')
                stats['difficulty_breakdown'][difficulty] = stats['difficulty_breakdown'].get(difficulty, 0) + 1
            
            # Calculate average score
            stats['average_score'] = sum(scores) / len(scores) if scores else 0.0
            
            # Convert domain counts to percentages
            for domain, count in domain_counts.items():
                stats['domain_breakdown'][domain] = count / len(exercises) if exercises else 0.0
            
            # Calculate reminder adherence
            completed_reminders = [rem for rem in reminders if rem.get('completed', False)]
            stats['reminder_adherence'] = len(completed_reminders) / len(reminders) if reminders else 0.0
            
            return stats
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {str(e)}")
            return {}