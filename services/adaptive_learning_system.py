import os
import logging
import json
import hashlib
from datetime import datetime
import numpy as np
from collections import deque
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class AdaptiveLearningSystem:
    """
    Enhanced neural learning system that can improve itself over time,
    gather information about dementia/Alzheimer's, and adapt to individual patients.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Set up OpenAI client
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Learning parameters
        self.learning_rate = 0.05
        self.memory_retention = 0.8
        self.exploration_rate = 0.2
        self.max_context_length = 10
        
        # Internal state
        self.learning_history = []
        self.current_context = deque(maxlen=self.max_context_length)
        self.last_update = datetime.utcnow()
        
        # Knowledge base paths
        self.knowledge_dir = os.path.join('data', 'adaptive_knowledge')
        self.research_path = os.path.join(self.knowledge_dir, 'research_data.json')
        self.patient_adaptive_path = os.path.join(self.knowledge_dir, 'patient_adaptations.json')
        self.voice_patterns_path = os.path.join(self.knowledge_dir, 'voice_patterns.json')
        
        # Ensure directories exist
        os.makedirs(self.knowledge_dir, exist_ok=True)
        
        # Initialize knowledge bases
        self.research_data = self._load_json(self.research_path, default=[])
        self.patient_adaptations = self._load_json(self.patient_adaptive_path, default={})
        self.voice_patterns = self._load_json(self.voice_patterns_path, default={})
        
        self.logger.info("Adaptive Learning System initialized")
    
    def _load_json(self, path, default=None):
        """Helper to load JSON files with default fallback."""
        if default is None:
            default = {}
        
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            return default
        except Exception as e:
            self.logger.error(f"Error loading {path}: {str(e)}")
            return default
    
    def _save_json(self, data, path):
        """Helper to save data to JSON file."""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving to {path}: {str(e)}")
            return False
    
    def gather_dementia_research(self, query=None, max_results=5):
        """
        Dynamically gather and update information about dementia and Alzheimer's
        using OpenAI for research synthesis.
        
        Args:
            query: Optional specific topic to research
            max_results: Maximum number of results to gather
            
        Returns:
            list: Updated research findings
        """
        try:
            # Default research query if none provided
            if not query:
                # Rotate through different research areas
                research_areas = [
                    "latest treatments for Alzheimer's disease",
                    "effective communication strategies for dementia patients",
                    "cognitive exercises that help slow Alzheimer's progression",
                    "environmental adaptations for dementia safety",
                    "technological innovations for dementia care"
                ]
                
                # Choose a research area based on what we have the least information about
                topic_counts = {}
                for item in self.research_data:
                    category = item.get('category', 'general')
                    topic_counts[category] = topic_counts.get(category, 0) + 1
                
                # Select the least researched area
                least_researched = None
                min_count = float('inf')
                
                for area in research_areas:
                    key = area.split()[0].lower()  # Simple categorization
                    count = topic_counts.get(key, 0)
                    if count < min_count:
                        min_count = count
                        least_researched = area
                
                query = least_researched
            
            # Generate a research prompt
            research_prompt = f"""
            Provide {max_results} evidence-based facts about {query}.
            Format your response as a JSON list of objects with the following structure:
            [
                {{
                    "fact": "The specific research finding",
                    "explanation": "A brief explanation of the finding",
                    "source": "Source of the information (organization or journal)",
                    "relevance": "Why this is important for dementia care",
                    "category": "One-word category for this finding"
                }}
            ]
            Include only accurate, current, and evidence-based information from reputable sources.
            """
            
            # Query OpenAI for research
            response = self.client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. Do not change this unless explicitly requested by the user
                messages=[{"role": "system", "content": "You are a specialized AI research assistant focused on gathering authoritative information about dementia and Alzheimer's disease."},
                         {"role": "user", "content": research_prompt}],
                response_format={"type": "json_object"}
            )
            
            # Extract and parse the research findings
            research_text = response.choices[0].message.content
            new_findings = json.loads(research_text)
            
            # Add timestamp and query information
            for finding in new_findings:
                finding['timestamp'] = datetime.utcnow().isoformat()
                finding['query'] = query
                
                # Add to research data
                self.research_data.append(finding)
            
            # Save updated research data
            self._save_json(self.research_data, self.research_path)
            
            self.logger.info(f"Added {len(new_findings)} new research findings on {query}")
            return new_findings
            
        except Exception as e:
            self.logger.error(f"Error gathering research: {str(e)}")
            return []
    
    def train_voice_mimicry(self, patient_id, voice_sample=None, text=None, voice_characteristics=None):
        """
        Train the system to recognize and mimic a specific patient's voice patterns.
        
        Args:
            patient_id: ID of the patient
            voice_sample: Optional audio sample of the patient's voice
            text: Optional text transcription of the voice sample
            voice_characteristics: Optional manual characteristics of the voice
            
        Returns:
            dict: Updated voice pattern data
        """
        try:
            # Initialize patient's voice pattern if not exists
            if patient_id not in self.voice_patterns:
                self.voice_patterns[patient_id] = {
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'samples_count': 0,
                    'characteristics': {
                        'pitch': 1.0,
                        'rate': 1.0,
                        'volume': 0.8,
                        'gender': 'neutral',
                        'age_sound': 'adult',
                        'dialectal_features': [],
                        'speech_patterns': []
                    },
                    'phrase_patterns': {},
                    'word_emphasis': {}
                }
            
            # Get existing voice pattern
            voice_pattern = self.voice_patterns[patient_id]
            
            # Update with voice sample analysis if provided
            if voice_sample:
                # In a real implementation, this would use audio analysis
                # For now, we'll simulate voice analysis results
                self.logger.info(f"Would analyze voice sample for patient {patient_id}")
                voice_pattern['samples_count'] += 1
            
            # Update with text analysis if provided
            if text:
                # Analyze text for speech patterns
                analysis_prompt = f"""
                Analyze this text as a speech sample and extract voice pattern characteristics:
                "{text}"
                
                Provide your analysis as a JSON object with the following structure:
                {{
                    "pitch": 0.0-2.0 (normal is 1.0),
                    "rate": 0.0-2.0 (normal is 1.0),
                    "volume_suggestion": 0.0-1.0,
                    "gender_leaning": "male/female/neutral",
                    "age_sound": "child/young/adult/elderly",
                    "dialectal_features": ["feature1", "feature2"],
                    "speech_patterns": ["pattern1", "pattern2"],
                    "emphasized_words": ["word1", "word2"],
                    "filler_words": ["um", "like", etc],
                    "speech_formality": "casual/formal"
                }}
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. Do not change this unless explicitly requested by the user
                    messages=[{"role": "system", "content": "You are a voice analysis specialist."},
                             {"role": "user", "content": analysis_prompt}],
                    response_format={"type": "json_object"}
                )
                
                text_analysis = json.loads(response.choices[0].message.content)
                
                # Update voice pattern with weighted average of new analysis
                alpha = 0.3  # Weight for new samples (adjust based on confidence)
                
                voice_pattern['characteristics']['pitch'] = (1-alpha) * voice_pattern['characteristics']['pitch'] + alpha * text_analysis.get('pitch', 1.0)
                voice_pattern['characteristics']['rate'] = (1-alpha) * voice_pattern['characteristics']['rate'] + alpha * text_analysis.get('rate', 1.0)
                voice_pattern['characteristics']['volume'] = (1-alpha) * voice_pattern['characteristics']['volume'] + alpha * text_analysis.get('volume_suggestion', 0.8)
                
                # Update categorical features
                gender_leaning = text_analysis.get('gender_leaning', 'neutral')
                if gender_leaning != 'neutral':
                    voice_pattern['characteristics']['gender'] = gender_leaning
                
                voice_pattern['characteristics']['age_sound'] = text_analysis.get('age_sound', voice_pattern['characteristics']['age_sound'])
                
                # Add new dialectal features and speech patterns
                for feature in text_analysis.get('dialectal_features', []):
                    if feature not in voice_pattern['characteristics']['dialectal_features']:
                        voice_pattern['characteristics']['dialectal_features'].append(feature)
                
                for pattern in text_analysis.get('speech_patterns', []):
                    if pattern not in voice_pattern['characteristics']['speech_patterns']:
                        voice_pattern['characteristics']['speech_patterns'].append(pattern)
                
                # Update emphasized words dictionary
                for word in text_analysis.get('emphasized_words', []):
                    voice_pattern['word_emphasis'][word] = voice_pattern['word_emphasis'].get(word, 0) + 1
            
            # Update with manually provided characteristics if any
            if voice_characteristics:
                for key, value in voice_characteristics.items():
                    if key in voice_pattern['characteristics']:
                        voice_pattern['characteristics'][key] = value
            
            # Update timestamp
            voice_pattern['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated voice patterns
            self._save_json(self.voice_patterns, self.voice_patterns_path)
            
            self.logger.info(f"Updated voice pattern for patient {patient_id}")
            return voice_pattern
            
        except Exception as e:
            self.logger.error(f"Error training voice mimicry: {str(e)}")
            return None
    
    def adapt_to_patient(self, patient_id, interaction_data):
        """
        Adapt system behavior to specific patient based on interaction history.
        
        Args:
            patient_id: ID of the patient
            interaction_data: Dict with interaction metrics, responses, etc.
            
        Returns:
            dict: Updated patient adaptation profile
        """
        try:
            # Initialize patient adaptation if not exists
            if patient_id not in self.patient_adaptations:
                self.patient_adaptations[patient_id] = {
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'interaction_count': 0,
                    'adaptation_level': 0.0,  # 0.0 to 1.0 scale
                    'preferred_topics': [],
                    'effective_approaches': [],
                    'ineffective_approaches': [],
                    'communication_preferences': {
                        'verbosity': 0.5,  # 0.0 (terse) to 1.0 (verbose)
                        'formality': 0.5,  # 0.0 (casual) to 1.0 (formal)
                        'speech_speed': 0.5,  # 0.0 (slow) to 1.0 (fast)
                        'repetition_needed': 0.5,  # 0.0 (rarely) to 1.0 (often)
                    },
                    'time_of_day_performance': {
                        'morning': 0.5,
                        'afternoon': 0.5,
                        'evening': 0.5,
                        'night': 0.5
                    },
                    'recent_interactions': []
                }
            
            # Get current patient adaptation
            adaptation = self.patient_adaptations[patient_id]
            
            # Update interaction count
            adaptation['interaction_count'] += 1
            
            # Extract time of day
            current_hour = datetime.utcnow().hour
            time_of_day = 'morning' if 5 <= current_hour < 12 else 'afternoon' if 12 <= current_hour < 17 else 'evening' if 17 <= current_hour < 22 else 'night'
            
            # Get interaction success metrics
            success_rate = interaction_data.get('success_rate', 0.5)
            engagement = interaction_data.get('engagement', 0.5)
            comprehension = interaction_data.get('comprehension', 0.5)
            
            # Overall interaction quality
            interaction_quality = (success_rate + engagement + comprehension) / 3.0
            
            # Update time of day performance with exponential moving average
            alpha = 0.2  # Weight for new observation
            adaptation['time_of_day_performance'][time_of_day] = (1-alpha) * adaptation['time_of_day_performance'][time_of_day] + alpha * interaction_quality
            
            # Update communication preferences based on interaction data
            if 'communication_metrics' in interaction_data:
                metrics = interaction_data['communication_metrics']
                for key in adaptation['communication_preferences']:
                    if key in metrics:
                        # Apply exponential moving average update
                        adaptation['communication_preferences'][key] = (1-alpha) * adaptation['communication_preferences'][key] + alpha * metrics[key]
            
            # Update preferred topics
            if 'topic' in interaction_data and interaction_quality > 0.6:
                topic = interaction_data['topic']
                if topic not in adaptation['preferred_topics']:
                    adaptation['preferred_topics'].append(topic)
            
            # Update effective/ineffective approaches
            if 'approach' in interaction_data:
                approach = interaction_data['approach']
                if interaction_quality > 0.7 and approach not in adaptation['effective_approaches']:
                    adaptation['effective_approaches'].append(approach)
                elif interaction_quality < 0.3 and approach not in adaptation['ineffective_approaches']:
                    adaptation['ineffective_approaches'].append(approach)
            
            # Store recent interaction summary
            adaptation['recent_interactions'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'quality': interaction_quality,
                'time_of_day': time_of_day,
                'topic': interaction_data.get('topic', 'unknown'),
                'approach': interaction_data.get('approach', 'unknown')
            })
            
            # Keep only last 20 interactions
            if len(adaptation['recent_interactions']) > 20:
                adaptation['recent_interactions'] = adaptation['recent_interactions'][-20:]
            
            # Calculate overall adaptation level based on interaction history
            if adaptation['interaction_count'] >= 5:
                recent_qualities = [i['quality'] for i in adaptation['recent_interactions'][-5:]]
                adaptation['adaptation_level'] = sum(recent_qualities) / len(recent_qualities)
            
            # Update timestamp
            adaptation['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated adaptations
            self._save_json(self.patient_adaptations, self.patient_adaptive_path)
            
            self.logger.info(f"Updated patient adaptation for patient {patient_id}")
            return adaptation
            
        except Exception as e:
            self.logger.error(f"Error adapting to patient: {str(e)}")
            return None
    
    def generate_adaptive_response(self, patient_id, input_text, context=None):
        """
        Generate a personalized response adapted to the specific patient.
        
        Args:
            patient_id: ID of the patient
            input_text: Text input from the patient
            context: Optional interaction context
            
        Returns:
            dict: Adaptive response with multiple formats
        """
        try:
            # Get patient adaptation profile
            adaptation = self.patient_adaptations.get(patient_id, {})
            
            # Get voice pattern
            voice_pattern = self.voice_patterns.get(patient_id, {})
            
            # Default context if none provided
            if context is None:
                context = {}
            
            # Time of day context
            current_hour = datetime.utcnow().hour
            time_of_day = 'morning' if 5 <= current_hour < 12 else 'afternoon' if 12 <= current_hour < 17 else 'evening' if 17 <= current_hour < 22 else 'night'
            
            # Build the system context from adaptation profile
            system_context = {
                "patient_id": patient_id,
                "adaptation_level": adaptation.get('adaptation_level', 0.0),
                "communication_preferences": adaptation.get('communication_preferences', {}),
                "time_of_day": time_of_day,
                "time_performance": adaptation.get('time_of_day_performance', {}).get(time_of_day, 0.5),
                "preferred_topics": adaptation.get('preferred_topics', []),
                "effective_approaches": adaptation.get('effective_approaches', []),
                "voice_characteristics": voice_pattern.get('characteristics', {})
            }
            
            # Build prompt with adaptive instructions
            comm_prefs = adaptation.get('communication_preferences', {})
            verbosity = comm_prefs.get('verbosity', 0.5)
            formality = comm_prefs.get('formality', 0.5)
            speech_speed = comm_prefs.get('speech_speed', 0.5)
            repetition = comm_prefs.get('repetition_needed', 0.5)
            
            system_prompt = f"""
            You are AlphaWolf, an adaptive AI assistant for someone with dementia.
            
            ADAPTATION PROFILE:
            - Verbosity: {'Keep responses concise and direct' if verbosity < 0.4 else 'Use moderate detail in responses' if verbosity < 0.7 else 'Provide detailed, thorough responses'}
            - Formality: {'Use casual, friendly language' if formality < 0.4 else 'Use a balanced, natural tone' if formality < 0.7 else 'Use more formal, structured language'}
            - Pace: {'Speak slowly and deliberately' if speech_speed < 0.4 else 'Use a moderate pace' if speech_speed < 0.7 else 'Speak at a normal conversational pace'}
            - Repetition: {'Repeat key information' if repetition > 0.6 else 'Occasionally reinforce important points' if repetition > 0.3 else 'Minimal repetition needed'}
            
            EFFECTIVENESS GUIDANCE:
            - Current time is {time_of_day}, when this person is typically {'very receptive' if system_context['time_performance'] > 0.7 else 'somewhat receptive' if system_context['time_performance'] > 0.4 else 'less receptive'} to new information
            - Effective approaches: {', '.join(system_context['effective_approaches']) if system_context['effective_approaches'] else 'No specific approaches identified yet'}
            - Preferred topics: {', '.join(system_context['preferred_topics']) if system_context['preferred_topics'] else 'No specific topics identified yet'}
            
            RESPONSE FORMAT INSTRUCTIONS:
            Provide your response in JSON format with the following structure:
            {{
                "text": "The main response text",
                "key_points": ["Important point 1", "Important point 2"],
                "voice_guidance": {{
                    "emphasis_words": ["word1", "word2"],
                    "pauses": ["after phrase 1", "after phrase 2"],
                    "tone": "calm/encouraging/etc."
                }}
            }}
            """
            
            # Prepare recent conversation context
            conversation_context = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation turns if available
            if 'conversation_history' in context:
                for turn in context['conversation_history'][-5:]:  # Last 5 turns
                    conversation_context.append({
                        "role": turn['role'],
                        "content": turn['content']
                    })
            
            # Add current user input
            conversation_context.append({"role": "user", "content": input_text})
            
            # Generate response with OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. Do not change this unless explicitly requested by the user
                messages=conversation_context,
                response_format={"type": "json_object"}
            )
            
            # Extract and parse the response
            response_text = response.choices[0].message.content
            response_data = json.loads(response_text)
            
            # Prepare the full adaptive response
            adaptive_response = {
                'text': response_data['text'],
                'key_points': response_data.get('key_points', []),
                'voice_guidance': response_data.get('voice_guidance', {}),
                'adaptation_metrics': {
                    'patient_id': patient_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'adaptation_level': adaptation.get('adaptation_level', 0.0),
                    'time_of_day': time_of_day
                }
            }
            
            # Update context with this interaction
            self.current_context.append({
                'timestamp': datetime.utcnow().isoformat(),
                'patient_id': patient_id,
                'input': input_text,
                'response': adaptive_response['text']
            })
            
            self.logger.info(f"Generated adaptive response for patient {patient_id}")
            return adaptive_response
            
        except Exception as e:
            self.logger.error(f"Error generating adaptive response: {str(e)}")
            return {
                'text': "I'm having some trouble processing that right now. Could you please repeat that?",
                'key_points': ["System experienced an error", "Request for clarification"],
                'voice_guidance': {
                    'tone': 'apologetic',
                    'emphasis_words': ['trouble', 'please', 'repeat'],
                }
            }
    
    def enhance_neural_model(self):
        """
        Self-improve the neural learning model based on interaction history.
        
        Returns:
            bool: Success of enhancement operation
        """
        try:
            # This would train the model using the latest interaction data
            # For now, we'll simulate model improvement with parameter adjustments
            
            # Calculate time since last update
            time_diff = (datetime.utcnow() - self.last_update).total_seconds() / 3600  # Hours
            
            # Only enhance if sufficient time has passed (at least 1 hour)
            if time_diff < 1:
                self.logger.info("Skipping model enhancement, too soon since last update")
                return False
            
            # Simulated improvement: Adjust learning parameters
            self.learning_rate *= 0.99  # Gradually decrease learning rate
            self.memory_retention = min(0.95, self.memory_retention + 0.01)  # Gradually increase retention
            
            # Adjust exploration rate based on system maturity
            if len(self.learning_history) > 100:
                self.exploration_rate = max(0.05, self.exploration_rate - 0.01)  # Reduce exploration as system matures
            
            # Record this enhancement in history
            self.learning_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'learning_rate': self.learning_rate,
                'memory_retention': self.memory_retention,
                'exploration_rate': self.exploration_rate
            })
            
            # Update last enhancement timestamp
            self.last_update = datetime.utcnow()
            
            self.logger.info("Enhanced neural model parameters")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enhancing neural model: {str(e)}")
            return False
    
    def get_patient_voice_tts_params(self, patient_id):
        """
        Get Text-to-Speech parameters optimized for mimicking patient's voice.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: TTS parameters for voice mimicry
        """
        try:
            # Get voice pattern for patient
            voice_pattern = self.voice_patterns.get(patient_id, {})
            
            # Default TTS parameters
            tts_params = {
                'rate': 1.0,
                'pitch': 1.0,
                'volume': 0.8,
                'voice': 'female_default'
            }
            
            # If we have voice characteristics, apply them
            if 'characteristics' in voice_pattern:
                chars = voice_pattern['characteristics']
                
                # Map voice pattern characteristics to TTS parameters
                tts_params['rate'] = chars.get('rate', 1.0)
                tts_params['pitch'] = chars.get('pitch', 1.0)
                tts_params['volume'] = chars.get('volume', 0.8)
                
                # Select appropriate voice model based on gender and age
                gender = chars.get('gender', 'neutral')
                age = chars.get('age_sound', 'adult')
                
                if gender == 'female':
                    tts_params['voice'] = 'female_default'
                    if age == 'elderly':
                        tts_params['voice'] = 'female_slow'
                elif gender == 'male':
                    tts_params['voice'] = 'male_default'
                    if age == 'elderly':
                        tts_params['voice'] = 'male_slow'
            
            return tts_params
            
        except Exception as e:
            self.logger.error(f"Error getting TTS parameters: {str(e)}")
            return {
                'rate': 1.0,
                'pitch': 1.0,
                'volume': 0.8,
                'voice': 'female_default'
            }