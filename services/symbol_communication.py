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

###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# SYMBOL COMMUNICATION MODULE
# Symbol-based communication system for non-verbal users with dementia.
# Enables expression through customizable symbol boards with images and icons.
#
# CodeName: Atlas
###############################################################################

import os
import logging
import json
import hashlib
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class SymbolCommunication:
    """
    Symbol-based communication system for non-verbal users with dementia.
    Enables expression through customizable symbol boards with images and icons.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Set up storage directories
        self.symbols_dir = os.path.join('data', 'symbols')
        self.boards_dir = os.path.join('data', 'symbol_boards')
        self.user_symbols_dir = os.path.join('data', 'user_symbols')
        
        # Ensure directories exist
        os.makedirs(self.symbols_dir, exist_ok=True)
        os.makedirs(self.boards_dir, exist_ok=True)
        os.makedirs(self.user_symbols_dir, exist_ok=True)
        
        # Symbol board categories
        self.categories = {
            'basic_needs': 'Basic Needs (Food, Water, Bathroom)',
            'emotions': 'Emotions and Feelings',
            'health': 'Health and Pain',
            'activities': 'Activities and Preferences',
            'people': 'People and Relationships',
            'locations': 'Places and Locations',
            'time': 'Time and Schedule',
            'help': 'Help and Assistance'
        }
        
        # Standard symbol collections
        self.standard_symbols = self._load_standard_symbols()
        
        # User symbol boards
        self.user_boards = {}
        self._load_user_boards()
        
        self.logger.info("Symbol Communication System initialized")
    
    def _load_standard_symbols(self):
        """Load the standard symbol collection."""
        symbols_path = os.path.join(self.symbols_dir, 'standard_symbols.json')
        
        # If standard symbols don't exist, create default set
        if not os.path.exists(symbols_path):
            standard_symbols = self._create_default_symbols()
            
            # Save the default set
            with open(symbols_path, 'w') as f:
                json.dump(standard_symbols, f, indent=2)
            
            return standard_symbols
        
        # Load existing standard symbols
        try:
            with open(symbols_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading standard symbols: {str(e)}")
            return self._create_default_symbols()
    
    def _create_default_symbols(self):
        """Create a default set of symbols organized by category."""
        # Basic needs category
        basic_needs = [
            {
                'id': 'food',
                'name': 'Food',
                'description': 'I am hungry',
                'path': 'food.png'
            },
            {
                'id': 'water',
                'name': 'Water',
                'description': 'I am thirsty',
                'path': 'water.png'
            },
            {
                'id': 'bathroom',
                'name': 'Bathroom',
                'description': 'I need to use the bathroom',
                'path': 'bathroom.png'
            },
            {
                'id': 'sleep',
                'name': 'Sleep',
                'description': 'I am tired/want to sleep',
                'path': 'sleep.png'
            }
        ]
        
        # Emotions category
        emotions = [
            {
                'id': 'happy',
                'name': 'Happy',
                'description': 'I feel happy',
                'path': 'happy.png'
            },
            {
                'id': 'sad',
                'name': 'Sad',
                'description': 'I feel sad',
                'path': 'sad.png'
            },
            {
                'id': 'afraid',
                'name': 'Afraid',
                'description': 'I feel scared',
                'path': 'afraid.png'
            },
            {
                'id': 'confused',
                'name': 'Confused',
                'description': 'I feel confused',
                'path': 'confused.png'
            }
        ]
        
        # Health category
        health = [
            {
                'id': 'pain',
                'name': 'Pain',
                'description': 'I am in pain',
                'path': 'pain.png'
            },
            {
                'id': 'medication',
                'name': 'Medication',
                'description': 'I need my medication',
                'path': 'medication.png'
            },
            {
                'id': 'cold',
                'name': 'Cold',
                'description': 'I feel cold',
                'path': 'cold.png'
            },
            {
                'id': 'hot',
                'name': 'Hot',
                'description': 'I feel hot',
                'path': 'hot.png'
            }
        ]
        
        # Activities category
        activities = [
            {
                'id': 'tv',
                'name': 'Television',
                'description': 'I want to watch TV',
                'path': 'tv.png'
            },
            {
                'id': 'music',
                'name': 'Music',
                'description': 'I want to listen to music',
                'path': 'music.png'
            },
            {
                'id': 'walk',
                'name': 'Walk',
                'description': 'I want to go for a walk',
                'path': 'walk.png'
            },
            {
                'id': 'read',
                'name': 'Read',
                'description': 'I want to read',
                'path': 'read.png'
            }
        ]
        
        # Organize all symbols by category
        return {
            'basic_needs': basic_needs,
            'emotions': emotions,
            'health': health,
            'activities': activities,
            'people': [],  # Empty by default, to be customized
            'locations': [],  # Empty by default, to be customized
            'time': [],  # Empty by default, to be customized
            'help': []  # Empty by default, to be customized
        }
    
    def _load_user_boards(self):
        """Load all user symbol boards from storage."""
        try:
            for filename in os.listdir(self.boards_dir):
                if filename.endswith('.json'):
                    patient_id = filename.split('_')[0]
                    with open(os.path.join(self.boards_dir, filename), 'r') as f:
                        self.user_boards[patient_id] = json.load(f)
            
            self.logger.info(f"Loaded {len(self.user_boards)} user symbol boards")
        except Exception as e:
            self.logger.error(f"Error loading user boards: {str(e)}")
    
    def _save_user_board(self, patient_id):
        """Save a user's symbol board to storage."""
        try:
            if patient_id in self.user_boards:
                board_path = os.path.join(self.boards_dir, f"{patient_id}_board.json")
                with open(board_path, 'w') as f:
                    json.dump(self.user_boards[patient_id], f, indent=2)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error saving user board: {str(e)}")
            return False
    
    def create_symbol_board(self, patient_id, name, categories=None):
        """
        Create a new symbol board for a patient.
        
        Args:
            patient_id: ID of the patient
            name: Name for the symbol board
            categories: Optional list of categories to include
            
        Returns:
            dict: The newly created symbol board
        """
        try:
            # Default to all categories if none specified
            if categories is None:
                categories = list(self.categories.keys())
            
            # Create new board structure
            new_board = {
                'id': f"board_{patient_id}_{int(datetime.utcnow().timestamp())}",
                'name': name,
                'patient_id': patient_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'categories': {},
                'usage_stats': {
                    'total_uses': 0,
                    'category_uses': {},
                    'symbol_uses': {}
                }
            }
            
            # Add selected categories with standard symbols
            for category in categories:
                if category in self.categories:
                    new_board['categories'][category] = {
                        'name': self.categories[category],
                        'symbols': self.standard_symbols.get(category, [])
                    }
                    new_board['usage_stats']['category_uses'][category] = 0
            
            # Store the new board
            self.user_boards[patient_id] = new_board
            self._save_user_board(patient_id)
            
            self.logger.info(f"Created new symbol board '{name}' for patient {patient_id}")
            return new_board
        
        except Exception as e:
            self.logger.error(f"Error creating symbol board: {str(e)}")
            return None
    
    def add_custom_symbol(self, patient_id, category, name, description, image_data=None, image_path=None):
        """
        Add a custom symbol to a patient's board.
        
        Args:
            patient_id: ID of the patient
            category: Category to add symbol to
            name: Name of the symbol
            description: Description of what the symbol represents
            image_data: Optional base64 encoded image data
            image_path: Optional path to image file
            
        Returns:
            dict: The added symbol or None if failed
        """
        try:
            # Check if patient has a board
            if patient_id not in self.user_boards:
                self.logger.error(f"No symbol board found for patient {patient_id}")
                return None
            
            board = self.user_boards[patient_id]
            
            # Check if category exists
            if category not in board['categories']:
                self.logger.error(f"Category '{category}' not found in patient {patient_id}'s board")
                return None
            
            # Generate symbol ID
            symbol_id = f"{category}_{name.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}"
            
            # Handle image data
            symbol_filename = f"{symbol_id}.png"
            symbol_path = os.path.join(self.user_symbols_dir, symbol_filename)
            
            if image_data:
                # Save base64 encoded image
                try:
                    # Remove data URL prefix if present
                    if ',' in image_data:
                        image_data = image_data.split(',')[1]
                    
                    # Decode base64 and save image
                    img_data = base64.b64decode(image_data)
                    img = Image.open(BytesIO(img_data))
                    img.save(symbol_path)
                except Exception as e:
                    self.logger.error(f"Error saving image data: {str(e)}")
                    return None
            
            elif image_path:
                # Copy image from provided path
                try:
                    img = Image.open(image_path)
                    img.save(symbol_path)
                except Exception as e:
                    self.logger.error(f"Error copying image from path: {str(e)}")
                    return None
            
            else:
                # No image provided
                symbol_path = None
            
            # Create symbol object
            new_symbol = {
                'id': symbol_id,
                'name': name,
                'description': description,
                'path': symbol_filename if symbol_path else None,
                'custom': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Add to board
            board['categories'][category]['symbols'].append(new_symbol)
            board['usage_stats']['symbol_uses'][symbol_id] = 0
            board['updated_at'] = datetime.utcnow().isoformat()
            
            # Save board
            self._save_user_board(patient_id)
            
            self.logger.info(f"Added custom symbol '{name}' for patient {patient_id}")
            return new_symbol
        
        except Exception as e:
            self.logger.error(f"Error adding custom symbol: {str(e)}")
            return None
    
    def record_symbol_usage(self, patient_id, symbol_id, category):
        """
        Record usage of a symbol for analytics and suggestion improvements.
        
        Args:
            patient_id: ID of the patient
            symbol_id: ID of the used symbol
            category: Category of the symbol
            
        Returns:
            bool: Success of recording operation
        """
        try:
            # Check if patient has a board
            if patient_id not in self.user_boards:
                self.logger.error(f"No symbol board found for patient {patient_id}")
                return False
            
            board = self.user_boards[patient_id]
            
            # Update usage stats
            board['usage_stats']['total_uses'] += 1
            
            if category in board['usage_stats']['category_uses']:
                board['usage_stats']['category_uses'][category] += 1
            else:
                board['usage_stats']['category_uses'][category] = 1
            
            if symbol_id in board['usage_stats']['symbol_uses']:
                board['usage_stats']['symbol_uses'][symbol_id] += 1
            else:
                board['usage_stats']['symbol_uses'][symbol_id] = 1
            
            # Update timestamp
            board['updated_at'] = datetime.utcnow().isoformat()
            
            # Add usage record with context
            if 'usage_history' not in board:
                board['usage_history'] = []
            
            board['usage_history'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'symbol_id': symbol_id,
                'category': category,
                'time_of_day': self._get_time_of_day()
            })
            
            # Keep history manageable (last 100 uses)
            if len(board['usage_history']) > 100:
                board['usage_history'] = board['usage_history'][-100:]
            
            # Save board
            self._save_user_board(patient_id)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error recording symbol usage: {str(e)}")
            return False
    
    def get_contextual_suggestions(self, patient_id, time_of_day=None, location=None, recent_activities=None):
        """
        Get contextual symbol suggestions based on usage patterns and time of day.
        
        Args:
            patient_id: ID of the patient
            time_of_day: Optional time of day (morning, afternoon, evening, night)
            location: Optional current location
            recent_activities: Optional list of recent activities
            
        Returns:
            dict: Suggested symbols organized by category
        """
        try:
            # Check if patient has a board
            if patient_id not in self.user_boards:
                self.logger.error(f"No symbol board found for patient {patient_id}")
                return {}
            
            board = self.user_boards[patient_id]
            
            # Determine time of day if not provided
            if time_of_day is None:
                time_of_day = self._get_time_of_day()
            
            # Get usage history
            usage_history = board.get('usage_history', [])
            
            # Filter by time of day
            time_filtered_usage = [
                u for u in usage_history 
                if 'time_of_day' in u and u['time_of_day'] == time_of_day
            ]
            
            # Count symbol usage by time of day
            symbol_counts = {}
            for usage in time_filtered_usage:
                symbol_id = usage['symbol_id']
                symbol_counts[symbol_id] = symbol_counts.get(symbol_id, 0) + 1
            
            # Get top symbols by category
            suggestions = {}
            
            for category, cat_data in board['categories'].items():
                category_symbols = []
                
                for symbol in cat_data['symbols']:
                    symbol_id = symbol['id']
                    
                    # Calculate relevance score based on usage and time of day
                    relevance = symbol_counts.get(symbol_id, 0)
                    
                    # Increase relevance based on context
                    if time_of_day == 'morning' and category == 'basic_needs':
                        relevance += 2  # Boost food/water in morning
                    elif time_of_day == 'night' and symbol_id == 'sleep':
                        relevance += 3  # Boost sleep at night
                    
                    if location and category == 'locations':
                        if location.lower() in symbol['name'].lower():
                            relevance += 2  # Boost current location
                    
                    if recent_activities and category == 'activities':
                        for activity in recent_activities:
                            if activity.lower() in symbol['name'].lower():
                                relevance += 1  # Boost recent activities
                    
                    # Add to category list with relevance score
                    category_symbols.append({
                        'symbol': symbol,
                        'relevance': relevance
                    })
                
                # Sort by relevance (highest first)
                category_symbols.sort(key=lambda x: x['relevance'], reverse=True)
                
                # Keep top 5 symbols per category
                suggestions[category] = [s['symbol'] for s in category_symbols[:5]]
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"Error getting contextual suggestions: {str(e)}")
            return {}
    
    def _get_time_of_day(self):
        """Helper to determine current time of day."""
        hour = datetime.utcnow().hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def get_user_board(self, patient_id):
        """
        Get a patient's symbol board.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: The patient's symbol board or None if not found
        """
        return self.user_boards.get(patient_id)
    
    def update_board_layout(self, patient_id, layout_updates):
        """
        Update the layout or organization of a patient's symbol board.
        
        Args:
            patient_id: ID of the patient
            layout_updates: Dict with layout changes
            
        Returns:
            bool: Success of update operation
        """
        try:
            # Check if patient has a board
            if patient_id not in self.user_boards:
                self.logger.error(f"No symbol board found for patient {patient_id}")
                return False
            
            board = self.user_boards[patient_id]
            
            # Apply layout updates
            if 'category_order' in layout_updates:
                board['category_order'] = layout_updates['category_order']
            
            if 'symbol_size' in layout_updates:
                board['symbol_size'] = layout_updates['symbol_size']
            
            if 'background_color' in layout_updates:
                board['background_color'] = layout_updates['background_color']
            
            if 'text_size' in layout_updates:
                board['text_size'] = layout_updates['text_size']
            
            # Update timestamp
            board['updated_at'] = datetime.utcnow().isoformat()
            
            # Save board
            self._save_user_board(patient_id)
            
            self.logger.info(f"Updated board layout for patient {patient_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error updating board layout: {str(e)}")
            return False