import os
import logging
import json
import hashlib
from datetime import datetime
import openai
from openai import OpenAI
import threading
import time
import schedule

logger = logging.getLogger(__name__)

class CognitiveEnhancementModule:
    """
    Integrates and manages the cognitive enhancement components for AlphaWolf:
    - Self-learning and neural adaptation
    - Voice mimicry and personalization
    - Symbol-based communication
    - AR navigation and object recognition
    """
    
    def __init__(self, adaptive_learning=None, voice_mimicry=None, symbol_communication=None, ar_navigation=None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize or use provided components
        from services.adaptive_learning_system import AdaptiveLearningSystem
        from services.voice_mimicry import VoiceMimicryEngine
        from services.symbol_communication import SymbolCommunication
        from services.ar_navigation import ARNavigationSystem
        
        self.adaptive_learning = adaptive_learning or AdaptiveLearningSystem()
        self.voice_mimicry = voice_mimicry or VoiceMimicryEngine()
        self.symbol_communication = symbol_communication or SymbolCommunication()
        self.ar_navigation = ar_navigation or ARNavigationSystem()
        
        # Integration data storage
        self.data_dir = os.path.join('data', 'cognitive_enhancement')
        self.patient_models_dir = os.path.join(self.data_dir, 'patient_models')
        self.learning_logs_dir = os.path.join(self.data_dir, 'learning_logs')
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.patient_models_dir, exist_ok=True)
        os.makedirs(self.learning_logs_dir, exist_ok=True)
        
        # Load patient cognitive models
        self.patient_models = self._load_patient_models()
        
        # Set up OpenAI client
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Set up background learning thread
        self.learning_thread = None
        self.learning_active = False
        
        # Initialize background learning scheduler
        self._setup_learning_scheduler()
        
        self.logger.info("Cognitive Enhancement Module initialized")
    
    def _load_patient_models(self):
        """Load cognitive models for all patients."""
        try:
            models = {}
            
            # Load each JSON file in the patient models directory
            if os.path.exists(self.patient_models_dir):
                for filename in os.listdir(self.patient_models_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(self.patient_models_dir, filename), 'r') as f:
                                model_data = json.load(f)
                                
                                # Extract patient ID from filename (patient_id_model.json)
                                patient_id = filename.split('_')[0]
                                models[patient_id] = model_data
                        except Exception as e:
                            self.logger.error(f"Error loading patient model {filename}: {str(e)}")
            
            self.logger.info(f"Loaded {len(models)} patient cognitive models")
            return models
        
        except Exception as e:
            self.logger.error(f"Error loading patient models: {str(e)}")
            return {}
    
    def _save_patient_model(self, patient_id):
        """Save a patient's cognitive model to file."""
        try:
            if patient_id in self.patient_models:
                model_path = os.path.join(self.patient_models_dir, f"{patient_id}_model.json")
                with open(model_path, 'w') as f:
                    json.dump(self.patient_models[patient_id], f, indent=2)
                return True
            return False
        
        except Exception as e:
            self.logger.error(f"Error saving patient model: {str(e)}")
            return False
    
    def _setup_learning_scheduler(self):
        """Set up scheduled tasks for background neural learning."""
        try:
            # Schedule model enhancement at regular intervals
            schedule.every(3).hours.do(self._enhance_all_models)
            
            # Schedule research updates at specific times
            schedule.every().day.at("03:00").do(self._update_research_knowledge)
            
            # Start the background thread to run the scheduler
            self.learning_thread = threading.Thread(target=self._run_scheduler)
            self.learning_thread.daemon = True
            self.learning_active = True
            self.learning_thread.start()
            
            self.logger.info("Learning scheduler initialized")
        
        except Exception as e:
            self.logger.error(f"Error setting up learning scheduler: {str(e)}")
    
    def _run_scheduler(self):
        """Run the background learning scheduler."""
        while self.learning_active:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _enhance_all_models(self):
        """Enhance all patient models with latest learning."""
        try:
            self.logger.info("Starting scheduled model enhancement")
            
            # Enhance the base neural learning model
            self.adaptive_learning.enhance_neural_model()
            
            # Enhance each patient's cognitive model
            for patient_id in self.patient_models:
                self._enhance_patient_model(patient_id)
            
            self.logger.info("Completed scheduled model enhancement")
            return True
        
        except Exception as e:
            self.logger.error(f"Error in scheduled model enhancement: {str(e)}")
            return False
    
    def _update_research_knowledge(self):
        """Update research knowledge about dementia and Alzheimer's."""
        try:
            self.logger.info("Starting scheduled research knowledge update")
            
            # Gather new research on rotating topics
            topics = [
                "latest research on Alzheimer's treatment",
                "communication strategies for dementia care",
                "cognitive exercises for memory retention",
                "environmental adaptations for dementia patients",
                "technology innovations in dementia care"
            ]
            
            # Choose a topic based on day of month (rotate through them)
            day_of_month = datetime.utcnow().day
            topic_index = day_of_month % len(topics)
            selected_topic = topics[topic_index]
            
            # Gather research on the selected topic
            new_findings = self.adaptive_learning.gather_dementia_research(query=selected_topic, max_results=3)
            
            if new_findings:
                # Log the update
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'topic': selected_topic,
                    'findings_count': len(new_findings),
                    'findings': new_findings
                }
                
                # Save to research log
                log_path = os.path.join(self.learning_logs_dir, f"research_log_{datetime.utcnow().strftime('%Y%m%d')}.json")
                with open(log_path, 'w') as f:
                    json.dump(log_entry, f, indent=2)
            
            self.logger.info(f"Completed research update on: {selected_topic}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error in scheduled research update: {str(e)}")
            return False
    
    def initialize_patient_model(self, patient_id, patient_data=None):
        """
        Initialize or update a patient's cognitive model.
        
        Args:
            patient_id: ID of the patient
            patient_data: Optional initial patient data
            
        Returns:
            dict: The initialized cognitive model
        """
        try:
            # Check if patient already has a model
            if patient_id in self.patient_models:
                patient_model = self.patient_models[patient_id]
                
                # Update existing model with new data if provided
                if patient_data:
                    if 'demographics' in patient_data:
                        patient_model['demographics'] = patient_data['demographics']
                    if 'cognitive_status' in patient_data:
                        patient_model['cognitive_status'] = patient_data['cognitive_status']
                    if 'preferences' in patient_data:
                        patient_model['preferences'] = patient_data['preferences']
                
                patient_model['updated_at'] = datetime.utcnow().isoformat()
                
                # Save updated model
                self._save_patient_model(patient_id)
                
                self.logger.info(f"Updated cognitive model for patient {patient_id}")
                return patient_model
            
            # Create new model if not exists
            new_model = {
                'patient_id': patient_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'demographics': patient_data.get('demographics', {}),
                'cognitive_status': patient_data.get('cognitive_status', {
                    'stage': 'early',
                    'memory_score': 0.7,
                    'language_score': 0.8,
                    'orientation_score': 0.7,
                    'attention_score': 0.7
                }),
                'preferences': patient_data.get('preferences', {
                    'communication_mode': 'verbal',
                    'speech_rate': 'normal',
                    'voice_preference': 'female',
                    'favorite_topics': []
                }),
                'interaction_history': [],
                'learning_progress': {
                    'personalization_level': 0.1,
                    'voice_adaptation': 0.0,
                    'symbol_familiarity': 0.0,
                    'navigation_familiarity': 0.0
                },
                'active_components': {
                    'adaptive_learning': True,
                    'voice_mimicry': True,
                    'symbol_communication': True,
                    'ar_navigation': True
                }
            }
            
            # Store the new model
            self.patient_models[patient_id] = new_model
            
            # Save to file
            self._save_patient_model(patient_id)
            
            # Initialize related components
            self._initialize_components(patient_id, new_model)
            
            self.logger.info(f"Initialized new cognitive model for patient {patient_id}")
            return new_model
        
        except Exception as e:
            self.logger.error(f"Error initializing patient model: {str(e)}")
            return None
    
    def _initialize_components(self, patient_id, model):
        """Initialize all cognitive components for a new patient."""
        try:
            # Initialize adaptive learning
            if model['active_components']['adaptive_learning']:
                # Create voice model with demographic info
                self.adaptive_learning.adapt_to_patient(patient_id, {
                    'success_rate': 0.7,
                    'engagement': 0.8,
                    'comprehension': 0.7
                })
            
            # Initialize voice mimicry
            if model['active_components']['voice_mimicry']:
                # Create voice model with demographic info
                demographics = model['demographics']
                self.voice_mimicry.create_voice_model(
                    patient_id,
                    gender=demographics.get('gender'),
                    age=demographics.get('age')
                )
            
            # Initialize symbol communication
            if model['active_components']['symbol_communication']:
                # Create default symbol board
                self.symbol_communication.create_symbol_board(
                    patient_id,
                    name="Default Communication Board"
                )
            
            # No initialization needed for AR navigation yet
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error initializing components for patient {patient_id}: {str(e)}")
            return False
    
    def _enhance_patient_model(self, patient_id):
        """Enhance a patient's cognitive model with latest learning."""
        try:
            if patient_id not in self.patient_models:
                self.logger.error(f"Patient {patient_id} not found in models")
                return False
            
            model = self.patient_models[patient_id]
            
            # Update learning progress
            progress = model['learning_progress']
            
            # Check if each component is active
            if model['active_components']['adaptive_learning']:
                # Get adaptive learning progress
                adapt_model = self.adaptive_learning.get_patient_voice_tts_params(patient_id)
                if adapt_model:
                    # Update personalization level
                    progress['personalization_level'] = min(1.0, progress['personalization_level'] + 0.05)
            
            if model['active_components']['voice_mimicry']:
                # Get voice model progress
                voice_model = self.voice_mimicry.get_voice_model(patient_id)
                if voice_model:
                    # Update voice adaptation level
                    progress['voice_adaptation'] = voice_model.get('training_progress', 0.0)
            
            if model['active_components']['symbol_communication']:
                # Get symbol board
                symbol_board = self.symbol_communication.get_user_board(patient_id)
                if symbol_board and 'usage_stats' in symbol_board:
                    # Calculate symbol familiarity based on usage
                    total_uses = symbol_board['usage_stats'].get('total_uses', 0)
                    if total_uses > 0:
                        # Scale to [0, 1] range with diminishing returns
                        progress['symbol_familiarity'] = min(1.0, total_uses / (total_uses + 20))
            
            if model['active_components']['ar_navigation']:
                # Get navigation layouts
                layouts = self.ar_navigation.get_patient_layouts(patient_id)
                if layouts:
                    # Simple metric: familiarity increases with number of layouts
                    progress['navigation_familiarity'] = min(1.0, len(layouts) / 3)
            
            # Update timestamp
            model['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated model
            self._save_patient_model(patient_id)
            
            self.logger.info(f"Enhanced cognitive model for patient {patient_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error enhancing patient model: {str(e)}")
            return False
    
    def process_interaction(self, patient_id, interaction_data):
        """
        Process a patient interaction and update models accordingly.
        
        Args:
            patient_id: ID of the patient
            interaction_data: Dict with interaction details
            
        Returns:
            dict: Processing result
        """
        try:
            # Check if patient has a model
            if patient_id not in self.patient_models:
                self.logger.warning(f"No cognitive model found for patient {patient_id}. Initializing.")
                self.initialize_patient_model(patient_id)
            
            model = self.patient_models[patient_id]
            
            # Extract interaction details
            interaction_type = interaction_data.get('type', 'conversation')
            content = interaction_data.get('content', '')
            context = interaction_data.get('context', {})
            metrics = interaction_data.get('metrics', {})
            
            # Record interaction in history
            interaction_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': interaction_type,
                'summary': content[:100] + ('...' if len(content) > 100 else ''),
                'metrics': metrics
            }
            
            model['interaction_history'].append(interaction_record)
            
            # Keep history manageable (last 100 interactions)
            if len(model['interaction_history']) > 100:
                model['interaction_history'] = model['interaction_history'][-100:]
            
            # Process with appropriate component based on interaction type
            result = None
            
            if interaction_type == 'conversation':
                # Update adaptive learning model
                self.adaptive_learning.adapt_to_patient(patient_id, {
                    'success_rate': metrics.get('success_rate', 0.5),
                    'engagement': metrics.get('engagement', 0.5),
                    'comprehension': metrics.get('comprehension', 0.5),
                    'topic': context.get('topic'),
                    'approach': context.get('approach')
                })
                
                # Generate adaptive response if input provided
                if 'input' in interaction_data:
                    result = self.adaptive_learning.generate_adaptive_response(
                        patient_id,
                        interaction_data['input'],
                        context
                    )
            
            elif interaction_type == 'voice_sample':
                # Add voice sample to voice model
                if 'audio_data' in interaction_data:
                    result = self.voice_mimicry.add_voice_sample(
                        patient_id,
                        audio_data=interaction_data['audio_data'],
                        transcript=interaction_data.get('transcript')
                    )
            
            elif interaction_type == 'symbol_usage':
                # Record symbol usage
                if 'symbol_id' in interaction_data and 'category' in interaction_data:
                    result = self.symbol_communication.record_symbol_usage(
                        patient_id,
                        interaction_data['symbol_id'],
                        interaction_data['category']
                    )
            
            elif interaction_type == 'navigation':
                # No specific processing for navigation yet
                pass
            
            # Save updated model
            model['updated_at'] = datetime.utcnow().isoformat()
            self._save_patient_model(patient_id)
            
            self.logger.info(f"Processed {interaction_type} interaction for patient {patient_id}")
            return {
                'success': True,
                'interaction_recorded': True,
                'result': result
            }
        
        except Exception as e:
            self.logger.error(f"Error processing interaction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_personalized_content(self, patient_id, content_type, parameters=None):
        """
        Generate personalized content for a patient.
        
        Args:
            patient_id: ID of the patient
            content_type: Type of content to generate (response, speech, symbols, navigation)
            parameters: Optional parameters for content generation
            
        Returns:
            dict: Generated content
        """
        try:
            # Check if patient has a model
            if patient_id not in self.patient_models:
                self.logger.warning(f"No cognitive model found for patient {patient_id}.")
                return {
                    'success': False,
                    'error': f"No cognitive model found for patient {patient_id}"
                }
            
            model = self.patient_models[patient_id]
            
            # Default parameters if none provided
            if parameters is None:
                parameters = {}
            
            # Generate content based on type
            if content_type == 'response':
                # Generate adaptive text response
                result = self.adaptive_learning.generate_adaptive_response(
                    patient_id,
                    parameters.get('input', ''),
                    parameters.get('context')
                )
                
                # Convert to speech if needed
                if parameters.get('speech_output', False):
                    speech_result = self.voice_mimicry.generate_mimicked_speech(
                        patient_id,
                        result['text'],
                        parameters.get('context')
                    )
                    
                    if speech_result and speech_result['success']:
                        result['speech'] = speech_result
                
                return {
                    'success': True,
                    'content_type': 'response',
                    'response': result
                }
            
            elif content_type == 'speech':
                # Generate speech directly
                result = self.voice_mimicry.generate_mimicked_speech(
                    patient_id,
                    parameters.get('text', ''),
                    parameters.get('context')
                )
                
                return {
                    'success': True,
                    'content_type': 'speech',
                    'speech': result
                }
            
            elif content_type == 'symbols':
                # Get contextual symbol suggestions
                result = self.symbol_communication.get_contextual_suggestions(
                    patient_id,
                    parameters.get('time_of_day'),
                    parameters.get('location'),
                    parameters.get('recent_activities')
                )
                
                return {
                    'success': True,
                    'content_type': 'symbols',
                    'symbols': result
                }
            
            elif content_type == 'navigation':
                # Generate navigation instructions
                result = self.ar_navigation.generate_navigation_instructions(
                    patient_id,
                    parameters.get('layout_id'),
                    parameters.get('start_name', 'Start'),
                    parameters.get('end_name', 'End'),
                    parameters.get('complexity', 'simple')
                )
                
                return {
                    'success': True,
                    'content_type': 'navigation',
                    'navigation': result
                }
            
            else:
                return {
                    'success': False,
                    'error': f"Unknown content type: {content_type}"
                }
        
        except Exception as e:
            self.logger.error(f"Error generating personalized content: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_patient_cognitive_status(self, patient_id):
        """
        Get the current cognitive status and learning progress for a patient.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: Cognitive status information
        """
        try:
            # Check if patient has a model
            if patient_id not in self.patient_models:
                self.logger.warning(f"No cognitive model found for patient {patient_id}.")
                return {
                    'success': False,
                    'error': f"No cognitive model found for patient {patient_id}"
                }
            
            model = self.patient_models[patient_id]
            
            # Get component-specific statuses
            # Adaptive learning status
            adaptive_status = None
            if model['active_components']['adaptive_learning']:
                patient_adaptation = self.adaptive_learning.patient_adaptations.get(patient_id)
                if patient_adaptation:
                    adaptive_status = {
                        'adaptation_level': patient_adaptation.get('adaptation_level', 0.0),
                        'interaction_count': patient_adaptation.get('interaction_count', 0),
                        'preferred_topics': patient_adaptation.get('preferred_topics', []),
                        'effective_approaches': patient_adaptation.get('effective_approaches', [])
                    }
            
            # Voice mimicry status
            voice_status = None
            if model['active_components']['voice_mimicry']:
                voice_report = self.voice_mimicry.generate_voice_report(patient_id)
                if voice_report and voice_report['success']:
                    voice_status = voice_report['report']
            
            # Symbol communication status
            symbol_status = None
            if model['active_components']['symbol_communication']:
                symbol_board = self.symbol_communication.get_user_board(patient_id)
                if symbol_board:
                    symbol_status = {
                        'board_name': symbol_board.get('name', 'Default Board'),
                        'total_uses': symbol_board.get('usage_stats', {}).get('total_uses', 0),
                        'most_used_categories': sorted(
                            symbol_board.get('usage_stats', {}).get('category_uses', {}).items(),
                            key=lambda x: x[1],
                            reverse=True
                        )[:3]
                    }
            
            # AR navigation status
            navigation_status = None
            if model['active_components']['ar_navigation']:
                layouts = self.ar_navigation.get_patient_layouts(patient_id)
                if layouts:
                    navigation_status = {
                        'layout_count': len(layouts),
                        'layouts': [{'id': layout['id'], 'name': layout['name']} for layout in layouts]
                    }
            
            # Combine all statuses
            full_status = {
                'patient_id': patient_id,
                'demographics': model['demographics'],
                'cognitive_status': model['cognitive_status'],
                'preferences': model['preferences'],
                'learning_progress': model['learning_progress'],
                'active_components': model['active_components'],
                'component_statuses': {
                    'adaptive_learning': adaptive_status,
                    'voice_mimicry': voice_status,
                    'symbol_communication': symbol_status,
                    'ar_navigation': navigation_status
                },
                'recent_interactions': model['interaction_history'][-5:] if model['interaction_history'] else [],
                'last_updated': model['updated_at']
            }
            
            return {
                'success': True,
                'status': full_status
            }
        
        except Exception as e:
            self.logger.error(f"Error getting patient cognitive status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_patient_preferences(self, patient_id, preferences):
        """
        Update preferences for a patient.
        
        Args:
            patient_id: ID of the patient
            preferences: Dict with preference updates
            
        Returns:
            dict: Updated preferences
        """
        try:
            # Check if patient has a model
            if patient_id not in self.patient_models:
                self.logger.warning(f"No cognitive model found for patient {patient_id}. Initializing.")
                self.initialize_patient_model(patient_id, {'preferences': preferences})
                return {
                    'success': True,
                    'preferences': preferences
                }
            
            model = self.patient_models[patient_id]
            
            # Update preferences
            for key, value in preferences.items():
                model['preferences'][key] = value
            
            # Update timestamp
            model['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated model
            self._save_patient_model(patient_id)
            
            self.logger.info(f"Updated preferences for patient {patient_id}")
            return {
                'success': True,
                'preferences': model['preferences']
            }
        
        except Exception as e:
            self.logger.error(f"Error updating patient preferences: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def toggle_component(self, patient_id, component_name, active):
        """
        Enable or disable a cognitive component for a patient.
        
        Args:
            patient_id: ID of the patient
            component_name: Name of component to toggle
            active: Boolean indicating whether to enable or disable
            
        Returns:
            dict: Updated component status
        """
        try:
            # Check if patient has a model
            if patient_id not in self.patient_models:
                self.logger.warning(f"No cognitive model found for patient {patient_id}.")
                return {
                    'success': False,
                    'error': f"No cognitive model found for patient {patient_id}"
                }
            
            model = self.patient_models[patient_id]
            
            # Check if component exists
            if component_name not in model['active_components']:
                return {
                    'success': False,
                    'error': f"Unknown component: {component_name}"
                }
            
            # Toggle component
            model['active_components'][component_name] = active
            
            # Update timestamp
            model['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated model
            self._save_patient_model(patient_id)
            
            self.logger.info(f"{'Enabled' if active else 'Disabled'} {component_name} for patient {patient_id}")
            return {
                'success': True,
                'component': component_name,
                'active': active,
                'active_components': model['active_components']
            }
        
        except Exception as e:
            self.logger.error(f"Error toggling component: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }