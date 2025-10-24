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
import random
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class CognitiveService:
    """Service for managing cognitive exercises and patient cognitive profiles."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exercise_types = {
            'memory': {
                'name': 'Memory Exercises',
                'description': 'Exercises to improve memory recall and retention',
                'impact_factors': {
                    'memory_score': 1.0,
                    'attention_score': 0.3,
                    'language_score': 0.1,
                    'pattern_recognition_score': 0.2,
                    'problem_solving_score': 0.1
                }
            },
            'attention': {
                'name': 'Attention Exercises',
                'description': 'Exercises to improve focus and attention span',
                'impact_factors': {
                    'memory_score': 0.2,
                    'attention_score': 1.0,
                    'language_score': 0.1,
                    'pattern_recognition_score': 0.3,
                    'problem_solving_score': 0.2
                }
            },
            'language': {
                'name': 'Language Exercises',
                'description': 'Exercises to maintain verbal ability and comprehension',
                'impact_factors': {
                    'memory_score': 0.2,
                    'attention_score': 0.1,
                    'language_score': 1.0,
                    'pattern_recognition_score': 0.1,
                    'problem_solving_score': 0.2
                }
            },
            'pattern': {
                'name': 'Pattern Recognition',
                'description': 'Exercises to identify and complete patterns',
                'impact_factors': {
                    'memory_score': 0.3,
                    'attention_score': 0.3,
                    'language_score': 0.1,
                    'pattern_recognition_score': 1.0,
                    'problem_solving_score': 0.4
                }
            },
            'problem': {
                'name': 'Problem Solving',
                'description': 'Exercises to maintain reasoning and problem-solving skills',
                'impact_factors': {
                    'memory_score': 0.2,
                    'attention_score': 0.3,
                    'language_score': 0.2,
                    'pattern_recognition_score': 0.4,
                    'problem_solving_score': 1.0
                }
            }
        }
        self.logger.info("Cognitive service initialized")
    
    def get_exercise_by_id(self, exercise_id, db_session):
        """
        Retrieve exercise details by ID from database.
        
        Args:
            exercise_id: ID of the exercise
            db_session: Database session
            
        Returns:
            Exercise object or None
        """
        try:
            from models import CognitiveExercise
            return db_session.query(CognitiveExercise).get(exercise_id)
        except Exception as e:
            self.logger.error(f"Error retrieving exercise {exercise_id}: {str(e)}")
            return None
    
    def get_recommended_exercises(self, patient, db_session, count=3):
        """
        Get personalized exercise recommendations for a patient.
        
        Args:
            patient: Patient object
            db_session: Database session
            count: Number of exercises to recommend
            
        Returns:
            list: Recommended cognitive exercises
        """
        try:
            from models import CognitiveExercise, CognitiveProfile, ExerciseResult
            
            # Get patient's cognitive profile
            profile = db_session.query(CognitiveProfile).filter_by(patient_id=patient.id).first()
            
            if not profile:
                # If no profile exists, create one with default values
                profile = CognitiveProfile()
                profile.patient_id = patient.id
                db_session.add(profile)
                db_session.commit()
            
            # Get recent exercise results to avoid repetition
            recent_exercises = db_session.query(ExerciseResult.exercise_id)\
                .filter_by(patient_id=patient.id)\
                .order_by(ExerciseResult.timestamp.desc())\
                .limit(5)\
                .all()
            recent_ids = [r[0] for r in recent_exercises]
            
            # Find weakest cognitive areas (lowest scores)
            scores = {
                'memory': profile.memory_score,
                'attention': profile.attention_score,
                'language': profile.language_score,
                'pattern': profile.pattern_recognition_score,
                'problem': profile.problem_solving_score
            }
            
            # Sort cognitive areas by score (ascending)
            sorted_areas = sorted(scores.items(), key=lambda x: x[1])
            focus_areas = [area for area, _ in sorted_areas[:2]]
            
            # Get exercises that target these areas
            all_exercises = db_session.query(CognitiveExercise).all()
            
            # Filter and score exercises based on cognitive needs
            scored_exercises = []
            for exercise in all_exercises:
                # Skip recently performed exercises
                if exercise.id in recent_ids:
                    continue
                
                # Calculate relevance score based on exercise type and patient needs
                relevance = 0
                if exercise.type in focus_areas:
                    relevance += 3
                
                # Adjust based on difficulty, using float conversion for profile scores
                max_score = max(float(score) for score in scores.values())
                if exercise.difficulty == 'easy' and max_score < 0.3:
                    relevance += 2
                elif exercise.difficulty == 'medium' and 0.3 <= max_score < 0.7:
                    relevance += 2
                elif exercise.difficulty == 'hard' and max_score >= 0.7:
                    relevance += 2
                scored_exercises.append((exercise, relevance))
            
            # Sort by relevance (descending)
            scored_exercises.sort(key=lambda x: x[1], reverse=True)
            
            # Return top recommendations
            recommendations = [exercise for exercise, _ in scored_exercises[:count]]
            
            # If not enough relevant exercises, add random ones to fill the count
            if len(recommendations) < count:
                additional_needed = count - len(recommendations)
                available_exercises = [e for e in all_exercises if e not in recommendations and e.id not in recent_ids]
                
                if available_exercises:
                    recommendations.extend(random.sample(available_exercises, min(additional_needed, len(available_exercises))))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting recommended exercises: {str(e)}")
            return []
    
    def update_cognitive_profile(self, exercise_result, db_session=None):
        """
        Update a patient's cognitive profile based on exercise results.
        
        Args:
            exercise_result: ExerciseResult object
            db_session: Optional database session
            
        Returns:
            bool: Success of update
        """
        try:
            if db_session is None:
                # If no session provided, assume we're in app context
                from app import db
                db_session = db.session
            
            from models import CognitiveProfile, CognitiveExercise
            
            patient_id = exercise_result.patient_id
            exercise = db_session.query(CognitiveExercise).get(exercise_result.exercise_id)
            
            if not exercise:
                self.logger.error(f"Exercise {exercise_result.exercise_id} not found")
                return False
            
            # Get patient's cognitive profile
            profile = db_session.query(CognitiveProfile).filter_by(patient_id=patient_id).first()
            if not profile:
                # Create new profile if one doesn't exist
                profile = CognitiveProfile()
                profile.patient_id = patient_id
                db_session.add(profile)
                db_session.add(profile)
            
            # Normalize score to 0-1 range
            normalized_score = min(max(exercise_result.score / 100.0, 0), 1)
            
            # Get impact factors for this exercise type
            exercise_type = exercise.type
            if exercise_type not in self.exercise_types:
                exercise_type = 'memory'  # Default if type not recognized
            
            impact_factors = self.exercise_types[exercise_type]['impact_factors']
            
            # Update each cognitive area based on impact factors
            # Using weighted average: new_score = (old_score * weight + new_score * impact) / (weight + impact)
            # where weight decreases the influence of a single exercise on the overall profile
            weight = 5  # Determines how quickly profile changes
            
            profile.memory_score = (profile.memory_score * weight + normalized_score * impact_factors['memory_score']) / (weight + impact_factors['memory_score'])
            profile.attention_score = (profile.attention_score * weight + normalized_score * impact_factors['attention_score']) / (weight + impact_factors['attention_score'])
            profile.language_score = (profile.language_score * weight + normalized_score * impact_factors['language_score']) / (weight + impact_factors['language_score'])
            profile.pattern_recognition_score = (profile.pattern_recognition_score * weight + normalized_score * impact_factors['pattern_recognition_score']) / (weight + impact_factors['pattern_recognition_score'])
            profile.problem_solving_score = (profile.problem_solving_score * weight + normalized_score * impact_factors['problem_solving_score']) / (weight + impact_factors['problem_solving_score'])
            
            profile.last_updated = datetime.utcnow()
            
            db_session.commit()
            self.logger.info(f"Updated cognitive profile for patient {patient_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating cognitive profile: {str(e)}")
            return False
    
    def get_exercise_data(self, exercise_type, difficulty='medium'):
        """
        Get data for a specific exercise type and difficulty.
        
        Args:
            exercise_type: Type of exercise (memory, pattern, etc.)
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            dict: Exercise data
        """
        try:
            # In a production system, this would load from a database
            # Here we generate simple exercise data based on type and difficulty
            
            if exercise_type == 'memory':
                return self._generate_memory_exercise(difficulty)
            elif exercise_type == 'pattern':
                return self._generate_pattern_exercise(difficulty)
            elif exercise_type == 'language':
                return self._generate_language_exercise(difficulty)
            else:
                return self._generate_memory_exercise(difficulty)  # Default
                
        except Exception as e:
            self.logger.error(f"Error generating exercise data: {str(e)}")
            return {"error": "Could not generate exercise data"}
    
    def _generate_memory_exercise(self, difficulty):
        """Generate a memory matching exercise."""
        item_counts = {
            'easy': 6,     # 3 pairs
            'medium': 12,  # 6 pairs
            'hard': 20     # 10 pairs
        }
        
        count = item_counts.get(difficulty, 12)
        
        # Categories of items that could be matched
        categories = [
            'animals', 'fruits', 'colors', 'shapes', 
            'household', 'vehicles', 'clothing', 'nature'
        ]
        
        # For simple implementation, just use the category name as the item
        selected_category = random.choice(categories)
        
        items = []
        for i in range(count // 2):
            item = f"{selected_category}_{i+1}"
            # Add each item twice for matching
            items.append(item)
            items.append(item)
        
        # Shuffle the items
        random.shuffle(items)
        
        return {
            'type': 'memory',
            'subtype': 'matching',
            'difficulty': difficulty,
            'instructions': 'Match the pairs of identical items',
            'items': items,
            'category': selected_category
        }
    
    def _generate_pattern_exercise(self, difficulty):
        """Generate a pattern completion exercise."""
        pattern_lengths = {
            'easy': 4,
            'medium': 6,
            'hard': 8
        }
        
        length = pattern_lengths.get(difficulty, 6)
        
        # Generate a simple pattern (for a real app, this would be more sophisticated)
        pattern_types = ['ascending', 'descending', 'alternating', 'fibonacci']
        pattern_type = random.choice(pattern_types)
        
        pattern = []
        if pattern_type == 'ascending':
            start = random.randint(1, 5)
            step = random.randint(1, 3)
            pattern = [start + i*step for i in range(length)]
        elif pattern_type == 'descending':
            start = random.randint(10, 20)
            step = random.randint(1, 3)
            pattern = [start - i*step for i in range(length)]
        elif pattern_type == 'alternating':
            first = random.randint(1, 5)
            second = random.randint(6, 10)
            pattern = [first if i % 2 == 0 else second for i in range(length)]
        elif pattern_type == 'fibonacci':
            a, b = 1, 1
            pattern = [a]
            for i in range(length-1):
                a, b = b, a + b
                pattern.append(a)
        
        # Hide the last element as the answer
        answer = pattern[-1]
        pattern[-1] = None
        
        # Generate options
        options = [answer]
        while len(options) < 4:
            option = answer + random.randint(-5, 5)
            if option != answer and option not in options:
                options.append(option)
        
        random.shuffle(options)
        
        return {
            'type': 'pattern',
            'difficulty': difficulty,
            'instructions': 'Complete the pattern by selecting the missing number',
            'pattern': pattern,
            'options': options,
            'answer_index': options.index(answer)
        }
    
    def _generate_language_exercise(self, difficulty):
        """Generate a word association exercise."""
        # Word pair complexity by difficulty
        difficulties = {
            'easy': ['dog-cat', 'day-night', 'hot-cold', 'happy-sad', 'big-small', 'old-new'],
            'medium': ['knife-fork', 'doctor-nurse', 'book-read', 'flower-garden', 'rain-umbrella'],
            'hard': ['astronomy-telescope', 'democracy-vote', 'symphony-orchestra', 'prescription-pharmacy']
        }
        
        # Select word pairs based on difficulty
        word_pairs = difficulties.get(difficulty, difficulties['medium'])
        
        # Randomly select pairs for the exercise
        num_pairs = 5
        selected_pairs = random.sample(word_pairs, min(num_pairs, len(word_pairs)))
        
        # Create exercise items
        items = []
        for pair in selected_pairs:
            words = pair.split('-')
            
            # For some items, flip the word order for variety
            if random.choice([True, False]):
                items.append({
                    'prompt': words[0],
                    'answer': words[1],
                    'options': self._generate_word_options(words[1])
                })
            else:
                items.append({
                    'prompt': words[1],
                    'answer': words[0],
                    'options': self._generate_word_options(words[0])
                })
        
        return {
            'type': 'language',
            'subtype': 'word_association',
            'difficulty': difficulty,
            'instructions': 'Select the word that is most associated with the given word',
            'items': items
        }
    
    def _generate_word_options(self, answer):
        """Generate plausible options for a word association exercise."""
        # In a real application, this would use a semantic database or word embeddings
        
        # Some simple distractors for demonstration
        common_distractors = {
            'cat': ['mouse', 'tiger', 'lion'],
            'dog': ['puppy', 'wolf', 'fox'],
            'night': ['evening', 'dark', 'moon'],
            'day': ['sun', 'light', 'morning'],
            'cold': ['ice', 'winter', 'freeze'],
            'hot': ['warm', 'summer', 'heat'],
            # Add more as needed
        }
        
        options = [answer]
        
        # Add specific distractors if available
        if answer in common_distractors:
            distractors = random.sample(common_distractors[answer], min(2, len(common_distractors[answer])))
            options.extend(distractors)
        
        # Fill remaining options with general words
        general_words = ['time', 'place', 'person', 'thing', 'idea', 'water', 'food', 'home', 'work', 'play']
        while len(options) < 4:
            word = random.choice(general_words)
            if word not in options:
                options.append(word)
        
        random.shuffle(options)
        return options
