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
import re

logger = logging.getLogger(__name__)

class ResearchModule:
    """Module for accessing and providing dementia-specific research and therapy content."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load knowledge base
        self.knowledge_base_path = os.path.join('data', 'knowledge_base.json')
        self.topics_path = os.path.join('data', 'topics.json')
        self.facts_path = os.path.join('data', 'facts.json')
        
        self.knowledge_base = {}
        self.topics = {}
        self.facts = []
        
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
            
            # Load knowledge base
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, 'r') as f:
                    self.knowledge_base = json.load(f)
                self.logger.info(f"Loaded knowledge base from {self.knowledge_base_path}")
            
            # Load topics
            if os.path.exists(self.topics_path):
                with open(self.topics_path, 'r') as f:
                    self.topics = json.load(f)
                self.logger.info(f"Loaded topics from {self.topics_path}")
            
            # Load facts
            if os.path.exists(self.facts_path):
                with open(self.facts_path, 'r') as f:
                    self.facts = json.load(f)
                self.logger.info(f"Loaded facts from {self.facts_path}")
        except Exception as e:
            self.logger.error(f"Error loading research data: {str(e)}")
        
        # Initialize with core dementia therapy topics if not loaded
        if not self.topics:
            self._initialize_default_topics()
        
        # Initialize with core facts if not loaded
        if not self.facts:
            self._initialize_default_facts()
        
        self.logger.info("Research Module initialized")
    
    def get_therapy_content(self, therapy_type, difficulty='medium', personalization=None):
        """
        Get content for specific dementia therapy approaches.
        
        Args:
            therapy_type: Type of therapy (reminiscence, reality_orientation, etc.)
            difficulty: Difficulty level (easy, medium, hard)
            personalization: Optional personalization data for the patient
            
        Returns:
            dict: Therapy content
        """
        try:
            # Check if therapy type exists
            if therapy_type not in self.topics:
                therapy_type = 'reminiscence'  # Default to reminiscence if not found
            
            # Get content for therapy type
            therapy_data = self.topics.get(therapy_type, {})
            
            # Filter content by difficulty
            content_items = []
            for item in therapy_data.get('content', []):
                item_difficulty = item.get('difficulty', 'medium')
                if item_difficulty == difficulty:
                    content_items.append(item)
            
            # If no items at requested difficulty, use any difficulty
            if not content_items:
                content_items = therapy_data.get('content', [])
            
            # Select a random content item
            content = random.choice(content_items) if content_items else {}
            
            # Apply personalization if available
            if personalization and content:
                content = self._personalize_content(content, personalization)
            
            return {
                'therapy_type': therapy_type,
                'difficulty': difficulty,
                'name': therapy_data.get('name', ''),
                'description': therapy_data.get('description', ''),
                'content': content
            }
        except Exception as e:
            self.logger.error(f"Error getting therapy content: {str(e)}")
            return {}
    
    def get_fact(self, category=None, personalization=None):
        """
        Get an informative fact, optionally from a specific category.
        
        Args:
            category: Optional category of fact
            personalization: Optional personalization data for the patient
            
        Returns:
            dict: Fact data
        """
        try:
            # Filter facts by category if provided
            filtered_facts = self.facts
            if category:
                filtered_facts = [fact for fact in self.facts if fact.get('category') == category]
            
            # If no facts in category, use all facts
            if not filtered_facts:
                filtered_facts = self.facts
            
            # Select a random fact
            fact = random.choice(filtered_facts) if filtered_facts else {}
            
            # Apply personalization if available
            if personalization and fact:
                fact_text = fact.get('text', '')
                
                # Replace placeholders with personalization data
                for key, value in personalization.items():
                    placeholder = f"[[{key}]]"
                    if placeholder in fact_text:
                        fact_text = fact_text.replace(placeholder, str(value))
                
                fact['text'] = fact_text
            
            return fact
        except Exception as e:
            self.logger.error(f"Error getting fact: {str(e)}")
            return {}
    
    def search_knowledge_base(self, query, limit=5):
        """
        Search the knowledge base for information.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            list: Matching knowledge items
        """
        try:
            results = []
            
            # Process query
            query = query.lower().strip()
            query_terms = set(re.findall(r'\w+', query))
            
            # Search in topics
            for topic_id, topic_data in self.topics.items():
                topic_name = topic_data.get('name', '').lower()
                topic_desc = topic_data.get('description', '').lower()
                topic_text = f"{topic_name} {topic_desc}"
                topic_terms = set(re.findall(r'\w+', topic_text))
                
                # Calculate term overlap
                overlap = len(query_terms.intersection(topic_terms))
                if overlap > 0:
                    results.append({
                        'type': 'topic',
                        'id': topic_id,
                        'name': topic_data.get('name', ''),
                        'description': topic_data.get('description', ''),
                        'relevance': overlap / len(query_terms) if query_terms else 0
                    })
            
            # Search in facts
            for fact in self.facts:
                fact_text = fact.get('text', '').lower()
                fact_terms = set(re.findall(r'\w+', fact_text))
                
                # Calculate term overlap
                overlap = len(query_terms.intersection(fact_terms))
                if overlap > 0:
                    results.append({
                        'type': 'fact',
                        'category': fact.get('category', ''),
                        'text': fact.get('text', ''),
                        'relevance': overlap / len(query_terms) if query_terms else 0
                    })
            
            # Sort by relevance
            results.sort(key=lambda x: x['relevance'], reverse=True)
            
            return results[:limit]
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def add_topic(self, topic_id, name, description, content=None):
        """
        Add a new therapy topic to the knowledge base.
        
        Args:
            topic_id: Unique identifier for the topic
            name: Name of the topic
            description: Description of the topic
            content: Optional list of content items
            
        Returns:
            bool: Success of operation
        """
        try:
            # Create new topic
            new_topic = {
                'name': name,
                'description': description,
                'content': content or [],
                'added_at': datetime.utcnow().isoformat()
            }
            
            # Add to topics
            self.topics[topic_id] = new_topic
            
            # Save topics
            self._save_topics()
            
            self.logger.info(f"Added new topic: {topic_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding topic: {str(e)}")
            return False
    
    def add_fact(self, text, category=None, source=None):
        """
        Add a new fact to the facts database.
        
        Args:
            text: The fact text
            category: Optional category
            source: Optional source information
            
        Returns:
            bool: Success of operation
        """
        try:
            # Create new fact
            new_fact = {
                'text': text,
                'category': category or 'general',
                'source': source,
                'added_at': datetime.utcnow().isoformat()
            }
            
            # Add to facts
            self.facts.append(new_fact)
            
            # Save facts
            self._save_facts()
            
            self.logger.info(f"Added new fact in category: {category}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding fact: {str(e)}")
            return False
    
    def get_topic_list(self):
        """
        Get a list of all therapy topics.
        
        Returns:
            list: Topic summaries
        """
        topic_list = []
        for topic_id, topic_data in self.topics.items():
            topic_list.append({
                'id': topic_id,
                'name': topic_data.get('name', ''),
                'description': topic_data.get('description', ''),
                'content_count': len(topic_data.get('content', []))
            })
        
        return topic_list
    
    def get_fact_categories(self):
        """
        Get a list of all fact categories with counts.
        
        Returns:
            dict: Categories with counts
        """
        categories = {}
        for fact in self.facts:
            category = fact.get('category', 'general')
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def _personalize_content(self, content, personalization):
        """Personalize content with patient-specific information."""
        # Deep copy content to avoid modifying original
        personalized_content = {k: v for k, v in content.items()}
        
        # Personalize text fields
        for field in ['text', 'question', 'description', 'prompt']:
            if field in personalized_content:
                text = personalized_content[field]
                
                # Replace placeholders with personalization data
                for key, value in personalization.items():
                    placeholder = f"[[{key}]]"
                    if placeholder in text:
                        text = text.replace(placeholder, str(value))
                
                personalized_content[field] = text
        
        # Personalize options if present
        if 'options' in personalized_content and isinstance(personalized_content['options'], list):
            personalized_options = []
            for option in personalized_content['options']:
                if isinstance(option, str):
                    # Replace placeholders in string options
                    option_text = option
                    for key, value in personalization.items():
                        placeholder = f"[[{key}]]"
                        if placeholder in option_text:
                            option_text = option_text.replace(placeholder, str(value))
                    personalized_options.append(option_text)
                elif isinstance(option, dict):
                    # Replace placeholders in dictionary options
                    option_dict = {k: v for k, v in option.items()}
                    for field, value in option_dict.items():
                        if isinstance(value, str):
                            for key, pvalue in personalization.items():
                                placeholder = f"[[{key}]]"
                                if placeholder in value:
                                    value = value.replace(placeholder, str(pvalue))
                            option_dict[field] = value
                    personalized_options.append(option_dict)
                else:
                    personalized_options.append(option)
            
            personalized_content['options'] = personalized_options
        
        return personalized_content
    
    def _initialize_default_topics(self):
        """Initialize default therapy topics."""
        self.topics = {
            'reminiscence': {
                'name': 'Reminiscence Therapy',
                'description': 'Therapy that involves discussing past experiences, often with photos or other memory triggers',
                'content': [
                    {
                        'type': 'photo_prompt',
                        'difficulty': 'easy',
                        'prompt': 'Look at this photo. What memories does it bring back?',
                        'follow_up': 'Can you tell me more about that time in your life?'
                    },
                    {
                        'type': 'question',
                        'difficulty': 'medium',
                        'question': 'What was your favorite holiday when you were younger?',
                        'follow_up': 'What did you enjoy most about it?'
                    },
                    {
                        'type': 'music',
                        'difficulty': 'easy',
                        'description': 'Listen to music from your youth and discuss memories associated with it',
                        'prompt': 'What memories does this song bring back?'
                    }
                ]
            },
            'reality_orientation': {
                'name': 'Reality Orientation',
                'description': 'Therapy focused on improving awareness of time, place, and person',
                'content': [
                    {
                        'type': 'calendar',
                        'difficulty': 'easy',
                        'prompt': 'Today is [[day_of_week]], [[month]] [[day]], [[year]]. What season are we in?',
                        'options': ['Spring', 'Summer', 'Fall', 'Winter']
                    },
                    {
                        'type': 'location',
                        'difficulty': 'medium',
                        'prompt': 'We are currently in [[location]]. What city are we in?',
                        'answer': '[[city]]'
                    },
                    {
                        'type': 'person',
                        'difficulty': 'hard',
                        'prompt': 'Who is the current president of the United States?',
                        'options': ['Joe Biden', 'Donald Trump', 'Barack Obama', 'George Bush']
                    }
                ]
            },
            'cognitive_stimulation': {
                'name': 'Cognitive Stimulation',
                'description': 'Activities designed to stimulate thinking, concentration, and memory',
                'content': [
                    {
                        'type': 'word_game',
                        'difficulty': 'easy',
                        'prompt': 'How many words can you think of that begin with the letter B?',
                        'target': 5,
                        'time_limit': 60
                    },
                    {
                        'type': 'calculation',
                        'difficulty': 'medium',
                        'prompt': 'If you buy an item for $3.45 and pay with $5, how much change should you receive?',
                        'answer': 1.55
                    },
                    {
                        'type': 'categorization',
                        'difficulty': 'hard',
                        'prompt': 'Sort these items into their correct categories: apple, car, dog, banana, truck, cat, orange, bus',
                        'categories': {
                            'Fruits': ['apple', 'banana', 'orange'],
                            'Vehicles': ['car', 'truck', 'bus'],
                            'Animals': ['dog', 'cat']
                        }
                    }
                ]
            },
            'validation_therapy': {
                'name': 'Validation Therapy',
                'description': 'Therapy that focuses on validating feelings rather than correcting factual misperceptions',
                'content': [
                    {
                        'type': 'emotional_prompt',
                        'difficulty': 'easy',
                        'prompt': 'You seem to be feeling [[emotion]]. Can you tell me more about what you\'re feeling?',
                        'follow_up': 'That sounds difficult. How can I help you feel more comfortable?'
                    },
                    {
                        'type': 'validation_statement',
                        'difficulty': 'medium',
                        'situation': 'Patient looking for deceased spouse',
                        'statement': 'I can see you miss your [[spouse_name]] very much. Tell me about the times you shared together.'
                    },
                    {
                        'type': 'empathy_exercise',
                        'difficulty': 'hard',
                        'prompt': 'You seem worried about something. What concerns are on your mind right now?',
                        'approach': 'Listen without correcting and validate emotions'
                    }
                ]
            },
            'multisensory_stimulation': {
                'name': 'Multisensory Stimulation',
                'description': 'Therapy using sensory experiences (touch, smell, sound, etc.) to stimulate responses',
                'content': [
                    {
                        'type': 'aromatherapy',
                        'difficulty': 'easy',
                        'prompt': 'What does this scent remind you of?',
                        'options': ['lavender', 'cinnamon', 'vanilla', 'coffee']
                    },
                    {
                        'type': 'tactile',
                        'difficulty': 'medium',
                        'prompt': 'Without looking, can you identify this object by touch?',
                        'objects': ['soft fabric', 'smooth stone', 'rough sandpaper', 'cool metal']
                    },
                    {
                        'type': 'sound',
                        'difficulty': 'hard',
                        'prompt': 'Listen to these sounds and tell me what they are.',
                        'sounds': ['rain', 'birds chirping', 'car engine', 'doorbell']
                    }
                ]
            }
        }
        
        # Save default topics
        self._save_topics()
    
    def _initialize_default_facts(self):
        """Initialize default facts."""
        self.facts = [
            {
                'text': 'Regular physical activity, even mild movement like walking, can help maintain cognitive function.',
                'category': 'health',
                'source': 'Alzheimer\'s Association'
            },
            {
                'text': 'The Mediterranean diet, rich in fruits, vegetables, and healthy fats, may help reduce the risk of cognitive decline.',
                'category': 'nutrition',
                'source': 'National Institute on Aging'
            },
            {
                'text': 'Social engagement and regular interaction with others can help maintain cognitive health.',
                'category': 'social',
                'source': 'Dementia Care Central'
            },
            {
                'text': 'Mental stimulation through puzzles, reading, and learning new skills can help maintain brain health.',
                'category': 'cognitive',
                'source': 'Alzheimer\'s Society'
            },
            {
                'text': 'Quality sleep is important for brain health and may help clear abnormal proteins associated with Alzheimer\'s disease.',
                'category': 'health',
                'source': 'Sleep Foundation'
            },
            {
                'text': 'Music therapy can improve mood and trigger positive memories in people with dementia.',
                'category': 'therapy',
                'source': 'American Music Therapy Association'
            },
            {
                'text': 'Reminiscence therapy using personal items, photos, and familiar songs can help maintain identity and improve mood.',
                'category': 'therapy',
                'source': 'Dementia UK'
            },
            {
                'text': 'Hydration is important for brain function. Dehydration can worsen confusion and cognitive symptoms.',
                'category': 'nutrition',
                'source': 'Mayo Clinic'
            },
            {
                'text': 'Creating a daily routine can help reduce anxiety and confusion for people with dementia.',
                'category': 'daily_living',
                'source': 'Alzheimer\'s Association'
            },
            {
                'text': 'Pet therapy can help reduce agitation and improve social interaction in people with dementia.',
                'category': 'therapy',
                'source': 'National Center for Biotechnology Information'
            }
        ]
        
        # Save default facts
        self._save_facts()
    
    def _save_topics(self):
        """Save topics to file."""
        try:
            with open(self.topics_path, 'w') as f:
                json.dump(self.topics, f, indent=2)
            
            self.logger.debug(f"Saved topics to {self.topics_path}")
        except Exception as e:
            self.logger.error(f"Error saving topics: {str(e)}")
    
    def _save_facts(self):
        """Save facts to file."""
        try:
            with open(self.facts_path, 'w') as f:
                json.dump(self.facts, f, indent=2)
            
            self.logger.debug(f"Saved facts to {self.facts_path}")
        except Exception as e:
            self.logger.error(f"Error saving facts: {str(e)}")
    
    def _save_knowledge_base(self):
        """Save knowledge base to file."""
        try:
            with open(self.knowledge_base_path, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
            
            self.logger.debug(f"Saved knowledge base to {self.knowledge_base_path}")
        except Exception as e:
            self.logger.error(f"Error saving knowledge base: {str(e)}")