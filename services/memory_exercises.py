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
import random
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class MemoryExercises:
    """Service for generating and evaluating memory-based cognitive exercises."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exercise_types = [
            'memory_match',
            'sequence_recall',
            'word_recall',
            'picture_recall',
            'story_recall'
        ]
        self.difficulty_levels = ['easy', 'medium', 'hard']
        self.logger.info("Memory exercises service initialized")
    
    def generate_exercise(self, exercise_type=None, difficulty='medium'):
        """
        Generate a memory exercise.
        
        Args:
            exercise_type: Optional specific exercise type
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            dict: Exercise data
        """
        try:
            # Select a random exercise type if not specified
            if not exercise_type or exercise_type not in self.exercise_types:
                exercise_type = random.choice(self.exercise_types)
            
            # Ensure difficulty is valid
            if difficulty not in self.difficulty_levels:
                difficulty = 'medium'
            
            # Generate exercise based on type
            if exercise_type == 'memory_match':
                return self._generate_memory_match(difficulty)
            elif exercise_type == 'sequence_recall':
                return self._generate_sequence_recall(difficulty)
            elif exercise_type == 'word_recall':
                return self._generate_word_recall(difficulty)
            elif exercise_type == 'picture_recall':
                return self._generate_picture_recall(difficulty)
            elif exercise_type == 'story_recall':
                return self._generate_story_recall(difficulty)
            else:
                return self._generate_memory_match(difficulty)  # Default
                
        except Exception as e:
            self.logger.error(f"Error generating memory exercise: {str(e)}")
            return {"error": "Could not generate exercise"}
    
    def evaluate_result(self, exercise_data, user_response):
        """
        Evaluate a user's response to a memory exercise.
        
        Args:
            exercise_data: The original exercise data
            user_response: The user's answers
            
        Returns:
            dict: Evaluation results with score and feedback
        """
        try:
            exercise_type = exercise_data.get('type', '')
            
            if exercise_type == 'memory_match':
                return self._evaluate_memory_match(exercise_data, user_response)
            elif exercise_type == 'sequence_recall':
                return self._evaluate_sequence_recall(exercise_data, user_response)
            elif exercise_type == 'word_recall':
                return self._evaluate_word_recall(exercise_data, user_response)
            elif exercise_type == 'picture_recall':
                return self._evaluate_picture_recall(exercise_data, user_response)
            elif exercise_type == 'story_recall':
                return self._evaluate_story_recall(exercise_data, user_response)
            else:
                return {
                    "error": "Unknown exercise type",
                    "score": 0,
                    "feedback": "Could not evaluate exercise"
                }
                
        except Exception as e:
            self.logger.error(f"Error evaluating exercise result: {str(e)}")
            return {
                "error": str(e),
                "score": 0,
                "feedback": "An error occurred during evaluation"
            }
    
    def _generate_memory_match(self, difficulty):
        """Generate a memory matching card game."""
        # Number of pairs based on difficulty
        pair_counts = {
            'easy': 4,     # 8 cards
            'medium': 6,   # 12 cards
            'hard': 10     # 20 cards
        }
        
        pairs_count = pair_counts.get(difficulty, 6)
        
        # Categories for matching (using simple text for now)
        categories = [
            'animals', 'fruits', 'colors', 'shapes', 
            'household', 'vehicles', 'clothing', 'nature'
        ]
        
        selected_category = random.choice(categories)
        
        # Generate items for the selected category
        items = []
        if selected_category == 'animals':
            all_items = ['dog', 'cat', 'horse', 'cow', 'sheep', 'pig', 'elephant', 'lion', 'tiger', 'bear', 'giraffe', 'monkey']
            items = random.sample(all_items, pairs_count)
        elif selected_category == 'fruits':
            all_items = ['apple', 'banana', 'orange', 'grape', 'pear', 'cherry', 'watermelon', 'strawberry', 'kiwi', 'mango']
            items = random.sample(all_items, pairs_count)
        elif selected_category == 'colors':
            all_items = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown', 'black', 'white']
            items = random.sample(all_items, pairs_count)
        elif selected_category == 'shapes':
            all_items = ['circle', 'square', 'triangle', 'rectangle', 'diamond', 'oval', 'star', 'heart', 'pentagon', 'hexagon']
            items = random.sample(all_items, pairs_count)
        else:
            # Generate generic items if category not specifically handled
            for i in range(pairs_count):
                items.append(f"{selected_category}_{i+1}")
        
        # Double the items to create pairs
        cards = []
        for item in items:
            cards.append({'id': len(cards), 'value': item})
            cards.append({'id': len(cards), 'value': item})
        
        # Shuffle the cards
        random.shuffle(cards)
        
        return {
            'type': 'memory_match',
            'difficulty': difficulty,
            'instructions': 'Match pairs of identical cards',
            'cards': cards,
            'category': selected_category,
            'pairs_count': pairs_count
        }
    
    def _generate_sequence_recall(self, difficulty):
        """Generate a sequence recall exercise."""
        # Sequence length based on difficulty
        sequence_lengths = {
            'easy': 4,
            'medium': 6,
            'hard': 8
        }
        
        length = sequence_lengths.get(difficulty, 6)
        
        # Types of sequences
        sequence_types = ['digits', 'colors', 'shapes', 'letters']
        sequence_type = random.choice(sequence_types)
        
        sequence = []
        if sequence_type == 'digits':
            sequence = [str(random.randint(0, 9)) for _ in range(length)]
        elif sequence_type == 'colors':
            all_colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown']
            sequence = random.choices(all_colors, k=length)
        elif sequence_type == 'shapes':
            all_shapes = ['circle', 'square', 'triangle', 'rectangle', 'diamond', 'star']
            sequence = random.choices(all_shapes, k=length)
        elif sequence_type == 'letters':
            all_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            sequence = random.choices(all_letters, k=length)
        
        return {
            'type': 'sequence_recall',
            'difficulty': difficulty,
            'instructions': f'Remember the sequence of {sequence_type} and recall them in order',
            'sequence': sequence,
            'sequence_type': sequence_type,
            'display_time': 5000 - (difficulty == 'hard') * 2000  # ms to display (shorter for harder)
        }
    
    def _generate_word_recall(self, difficulty):
        """Generate a word recall exercise."""
        # Word counts based on difficulty
        word_counts = {
            'easy': 5,
            'medium': 8,
            'hard': 12
        }
        
        count = word_counts.get(difficulty, 8)
        
        # Word categories (for semantic grouping)
        categories = [
            'animals', 'food', 'household', 'nature', 'city'
        ]
        
        selected_category = random.choice(categories)
        
        # Generate words for the selected category
        words = []
        if selected_category == 'animals':
            all_words = ['dog', 'cat', 'horse', 'cow', 'sheep', 'pig', 'lion', 'tiger', 'bear', 'fox', 'wolf', 'deer']
            words = random.sample(all_words, min(count, len(all_words)))
        elif selected_category == 'food':
            all_words = ['apple', 'bread', 'cheese', 'milk', 'pasta', 'rice', 'chicken', 'beef', 'carrot', 'potato', 'tomato', 'banana']
            words = random.sample(all_words, min(count, len(all_words)))
        elif selected_category == 'household':
            all_words = ['chair', 'table', 'lamp', 'sofa', 'bed', 'pillow', 'blanket', 'mirror', 'clock', 'vase', 'picture', 'carpet']
            words = random.sample(all_words, min(count, len(all_words)))
        elif selected_category == 'nature':
            all_words = ['tree', 'flower', 'river', 'mountain', 'lake', 'forest', 'beach', 'sky', 'cloud', 'rain', 'snow', 'wind']
            words = random.sample(all_words, min(count, len(all_words)))
        elif selected_category == 'city':
            all_words = ['building', 'street', 'car', 'bus', 'park', 'store', 'school', 'house', 'office', 'bridge', 'road', 'sidewalk']
            words = random.sample(all_words, min(count, len(all_words)))
        
        # Create options for recall (original words + distractors)
        all_options = words.copy()
        
        # Add distractors (words from same category but not in original list)
        if selected_category == 'animals':
            distractors = ['rabbit', 'hamster', 'elephant', 'giraffe', 'zebra', 'monkey']
        elif selected_category == 'food':
            distractors = ['orange', 'egg', 'pizza', 'fish', 'cake', 'cookie']
        elif selected_category == 'household':
            distractors = ['desk', 'drawer', 'shelf', 'plate', 'fork', 'knife']
        elif selected_category == 'nature':
            distractors = ['hill', 'ocean', 'star', 'moon', 'grass', 'leaf']
        elif selected_category == 'city':
            distractors = ['train', 'station', 'hospital', 'restaurant', 'cinema', 'mall']
        else:
            distractors = []
        
        for distractor in distractors:
            if distractor not in all_options and len(all_options) < count + 5:
                all_options.append(distractor)
        
        random.shuffle(all_options)
        
        return {
            'type': 'word_recall',
            'difficulty': difficulty,
            'instructions': f'Remember the {selected_category} words and select them later',
            'words': words,
            'options': all_options,
            'category': selected_category,
            'display_time': 10000 - (difficulty == 'hard') * 4000  # ms to display (shorter for harder)
        }
    
    def _generate_picture_recall(self, difficulty):
        """Generate a picture recall exercise using ASCII art for simplicity."""
        # Number of pictures based on difficulty
        picture_counts = {
            'easy': 3,
            'medium': 5,
            'hard': 7
        }
        
        count = picture_counts.get(difficulty, 5)
        
        # Simple ASCII art for objects
        pictures = {
            'house': [
                "  /\\  ",
                " /  \\ ",
                "/____\\",
                "|    |",
                "|____|"
            ],
            'tree': [
                "  ^  ",
                " / \\ ",
                "/   \\",
                "  |  ",
                "  |  "
            ],
            'car': [
                "  ____  ",
                " /|__|\\",
                "(_)  (_)"
            ],
            'apple': [
                "  __  ",
                " /  \\ ",
                "|    |",
                " \\__/ "
            ],
            'fish': [
                "  /\\  ",
                " /  \\_",
                " \\   /",
                "  \\_/ "
            ],
            'flower': [
                " @@ ",
                "@  @",
                " @@ ",
                "  | ",
                "  | "
            ],
            'sun': [
                "\\   /",
                " \\_/ ",
                "  O  ",
                " / \\ ",
                "/   \\"
            ],
            'cup': [
                " ___ ",
                "|   |",
                "|   |",
                " \\__/"
            ],
            'heart': [
                " / \\ ",
                "/   \\",
                "\\   /",
                " \\_/ "
            ]
        }
        
        # Select random pictures
        picture_names = list(pictures.keys())
        selected_names = random.sample(picture_names, min(count, len(picture_names)))
        
        # Create pictures list
        selected_pictures = [
            {
                'name': name,
                'ascii': pictures[name]
            }
            for name in selected_names
        ]
        
        # Create options for recall (all names)
        options = picture_names.copy()
        random.shuffle(options)
        
        return {
            'type': 'picture_recall',
            'difficulty': difficulty,
            'instructions': 'Remember each picture and identify it later',
            'pictures': selected_pictures,
            'options': options,
            'correct_answers': selected_names,
            'display_time': 6000 - (difficulty == 'hard') * 3000  # ms per picture
        }
    
    def _generate_story_recall(self, difficulty):
        """Generate a story recall exercise."""
        # Stories with questions based on difficulty
        stories = {
            'easy': [
                {
                    'text': "Mary went to the store. She bought milk and bread. Then she went home.",
                    'questions': [
                        {'question': "What is the name of the person in the story?", 'options': ['Mary', 'John', 'Susan', 'David'], 'answer': 'Mary'},
                        {'question': "Where did Mary go?", 'options': ['Store', 'Park', 'School', 'Beach'], 'answer': 'Store'},
                        {'question': "What did Mary buy?", 'options': ['Milk and bread', 'Eggs and cheese', 'Apples and bananas', 'Meat and vegetables'], 'answer': 'Milk and bread'}
                    ]
                },
                {
                    'text': "Tom has a pet dog. The dog's name is Spot. Spot likes to play fetch.",
                    'questions': [
                        {'question': "Who is Tom's pet?", 'options': ['Dog', 'Cat', 'Bird', 'Fish'], 'answer': 'Dog'},
                        {'question': "What is the dog's name?", 'options': ['Spot', 'Rex', 'Buddy', 'Max'], 'answer': 'Spot'},
                        {'question': "What game does Spot like to play?", 'options': ['Fetch', 'Hide and seek', 'Tag', 'Ball'], 'answer': 'Fetch'}
                    ]
                }
            ],
            'medium': [
                {
                    'text': "Sarah went on vacation to the beach. She stayed for five days. While there, she swam in the ocean and collected seashells. The weather was sunny every day except Tuesday, when it rained.",
                    'questions': [
                        {'question': "Where did Sarah go on vacation?", 'options': ['Beach', 'Mountains', 'City', 'Desert'], 'answer': 'Beach'},
                        {'question': "How long did Sarah stay?", 'options': ['Three days', 'Four days', 'Five days', 'One week'], 'answer': 'Five days'},
                        {'question': "What did Sarah do at the beach?", 'options': ['Swam and collected seashells', 'Built sandcastles', 'Read books', 'Took photos'], 'answer': 'Swam and collected seashells'},
                        {'question': "When did it rain?", 'options': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'], 'answer': 'Tuesday'}
                    ]
                }
            ],
            'hard': [
                {
                    'text': "Michael Johnson is a retired teacher who lives in a small house on Maple Street. He has two children, Emily and Robert, and five grandchildren. Every Sunday, he visits the local bakery to buy fresh bread and pastries. His favorite is the cinnamon roll. Michael also volunteers at the community garden on Wednesdays and Fridays, where he grows tomatoes, carrots, and peppers. Last summer, his tomatoes won first prize at the county fair.",
                    'questions': [
                        {'question': "What is Michael's last name?", 'options': ['Smith', 'Johnson', 'Williams', 'Brown'], 'answer': 'Johnson'},
                        {'question': "What was Michael's profession?", 'options': ['Doctor', 'Lawyer', 'Teacher', 'Engineer'], 'answer': 'Teacher'},
                        {'question': "How many grandchildren does Michael have?", 'options': ['Three', 'Four', 'Five', 'Six'], 'answer': 'Five'},
                        {'question': "What is Michael's favorite bakery item?", 'options': ['Croissant', 'Cinnamon roll', 'Bread', 'Donut'], 'answer': 'Cinnamon roll'},
                        {'question': "Which days does Michael volunteer at the garden?", 'options': ['Monday and Wednesday', 'Tuesday and Thursday', 'Wednesday and Friday', 'Saturday and Sunday'], 'answer': 'Wednesday and Friday'},
                        {'question': "What vegetable won a prize at the county fair?", 'options': ['Carrots', 'Tomatoes', 'Peppers', 'Cucumbers'], 'answer': 'Tomatoes'}
                    ]
                }
            ]
        }
        
        # Select a random story based on difficulty
        available_stories = stories.get(difficulty, stories['medium'])
        selected_story = random.choice(available_stories)
        
        return {
            'type': 'story_recall',
            'difficulty': difficulty,
            'instructions': 'Read the story carefully and answer the questions that follow',
            'story': selected_story['text'],
            'questions': selected_story['questions'],
            'reading_time': 20000 - (difficulty == 'easy') * 5000 + (difficulty == 'hard') * 10000  # ms to read
        }
    
    def _evaluate_memory_match(self, exercise_data, user_response):
        """Evaluate memory match exercise results."""
        # User response should be a list of matched pairs (card IDs)
        matches = user_response.get('matches', [])
        cards = exercise_data.get('cards', [])
        pairs_count = exercise_data.get('pairs_count', 0)
        
        # Check if each pair is a valid match
        correct_pairs = 0
        incorrect_pairs = 0
        
        for pair in matches:
            if len(pair) != 2:
                continue
                
            # Get cards for the pair
            card1 = next((card for card in cards if card['id'] == pair[0]), None)
            card2 = next((card for card in cards if card['id'] == pair[1]), None)
            
            if card1 and card2 and card1['value'] == card2['value']:
                correct_pairs += 1
            else:
                incorrect_pairs += 1
        
        # Calculate score (percentage of correct pairs)
        score = (correct_pairs / pairs_count) * 100 if pairs_count > 0 else 0
        
        # Generate feedback
        if score >= 90:
            feedback = "Excellent! You have a great memory for matching."
        elif score >= 70:
            feedback = "Good job! You matched most pairs correctly."
        elif score >= 50:
            feedback = "Not bad. With a bit more practice, your matching skills will improve."
        else:
            feedback = "Keep practicing. Memory games can help improve your recall abilities."
        
        return {
            'score': score,
            'correct_pairs': correct_pairs,
            'incorrect_pairs': incorrect_pairs,
            'total_pairs': pairs_count,
            'feedback': feedback
        }
    
    def _evaluate_sequence_recall(self, exercise_data, user_response):
        """Evaluate sequence recall exercise results."""
        original_sequence = exercise_data.get('sequence', [])
        user_sequence = user_response.get('sequence', [])
        
        # Check for correctness
        correct_items = 0
        for i in range(min(len(original_sequence), len(user_sequence))):
            if original_sequence[i] == user_sequence[i]:
                correct_items += 1
        
        # Calculate score
        score = (correct_items / len(original_sequence)) * 100 if original_sequence else 0
        
        # Check for order errors (correct items in wrong positions)
        order_errors = 0
        for item in user_sequence:
            if item in original_sequence and item != original_sequence[user_sequence.index(item)]:
                order_errors += 1
        
        # Generate feedback
        if score >= 90:
            feedback = "Excellent! Your sequence recall is very strong."
        elif score >= 70:
            feedback = "Good job! You remembered most of the sequence correctly."
        elif score >= 50:
            feedback = "Not bad. Try focusing on the order of items in the sequence."
        else:
            feedback = "Keep practicing. Sequential memory can improve with regular exercise."
        
        return {
            'score': score,
            'correct_items': correct_items,
            'total_items': len(original_sequence),
            'order_errors': order_errors,
            'feedback': feedback
        }
    
    def _evaluate_word_recall(self, exercise_data, user_response):
        """Evaluate word recall exercise results."""
        original_words = exercise_data.get('words', [])
        selected_words = user_response.get('selected_words', [])
        
        # Count correct and incorrect selections
        correct_selections = 0
        incorrect_selections = 0
        
        for word in selected_words:
            if word in original_words:
                correct_selections += 1
            else:
                incorrect_selections += 1
        
        # Calculate missed words
        missed_words = [word for word in original_words if word not in selected_words]
        
        # Calculate score
        # Formula: (correct - incorrect) / total * 100, with minimum of 0
        score = max(0, (correct_selections - incorrect_selections) / len(original_words)) * 100
        
        # Generate feedback
        if score >= 90:
            feedback = "Excellent! Your word recall is very strong."
        elif score >= 70:
            feedback = "Good job! You remembered most words correctly."
        elif score >= 50:
            feedback = "Not bad. Try to focus more on each word during the presentation."
        else:
            feedback = "Keep practicing. Word recall can improve with regular exercise."
        
        return {
            'score': score,
            'correct_selections': correct_selections,
            'incorrect_selections': incorrect_selections,
            'missed_words': missed_words,
            'total_words': len(original_words),
            'feedback': feedback
        }
    
    def _evaluate_picture_recall(self, exercise_data, user_response):
        """Evaluate picture recall exercise results."""
        correct_answers = exercise_data.get('correct_answers', [])
        user_answers = user_response.get('selected_pictures', [])
        
        # Count correct and incorrect identifications
        correct_ids = 0
        incorrect_ids = 0
        
        for answer in user_answers:
            if answer in correct_answers:
                correct_ids += 1
            else:
                incorrect_ids += 1
        
        # Calculate missed pictures
        missed_pictures = [pic for pic in correct_answers if pic not in user_answers]
        
        # Calculate score
        # Formula: (correct - incorrect) / total * 100, with minimum of 0
        score = max(0, (correct_ids - incorrect_ids) / len(correct_answers)) * 100
        
        # Generate feedback
        if score >= 90:
            feedback = "Excellent! Your visual recall is very strong."
        elif score >= 70:
            feedback = "Good job! You remembered most pictures correctly."
        elif score >= 50:
            feedback = "Not bad. Try spending more time studying each picture."
        else:
            feedback = "Keep practicing. Visual memory can improve with regular exercise."
        
        return {
            'score': score,
            'correct_identifications': correct_ids,
            'incorrect_identifications': incorrect_ids,
            'missed_pictures': missed_pictures,
            'total_pictures': len(correct_answers),
            'feedback': feedback
        }
    
    def _evaluate_story_recall(self, exercise_data, user_response):
        """Evaluate story recall exercise results."""
        questions = exercise_data.get('questions', [])
        user_answers = user_response.get('answers', {})
        
        # Count correct answers
        correct_answers = 0
        incorrect_answers = 0
        
        for question in questions:
            question_text = question['question']
            correct_answer = question['answer']
            
            if user_answers.get(question_text) == correct_answer:
                correct_answers += 1
            else:
                incorrect_answers += 1
        
        # Calculate score
        score = (correct_answers / len(questions)) * 100 if questions else 0
        
        # Generate feedback
        if score >= 90:
            feedback = "Excellent! Your story comprehension and recall is very strong."
        elif score >= 70:
            feedback = "Good job! You remembered most details from the story."
        elif score >= 50:
            feedback = "Not bad. Try to focus on key details while reading the story."
        else:
            feedback = "Keep practicing. Reading comprehension can improve with regular exercise."
        
        return {
            'score': score,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'total_questions': len(questions),
            'feedback': feedback
        }
