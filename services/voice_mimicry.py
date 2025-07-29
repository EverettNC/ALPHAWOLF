###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# VOICE MIMICRY ENGINE MODULE
# Enhanced voice system that analyzes, learns from, and mimics individual
# patient voices for more personalized and effective communication.
#
# CodeName: Echo
###############################################################################

import os
import logging
import json
import hashlib
import numpy as np
from datetime import datetime
import tempfile
import base64
from io import BytesIO

from openai import OpenAI
from gtts import gTTS
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ...existing imports...
logger = logging.getLogger(__name__)

class VoiceMimicryEngine:
    """
    Enhanced voice system that can analyze, learn from, and mimic individual
    patient voices for more personalized and effective communication.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Set up OpenAI client
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Set up storage directories
        self.voice_models_dir = os.path.join('data', 'voice_models')
        self.voice_samples_dir = os.path.join('data', 'voice_samples')
        self.voice_outputs_dir = os.path.join('static', 'audio', 'generated')
        
        # Ensure directories exist
        os.makedirs(self.voice_models_dir, exist_ok=True)
        os.makedirs(self.voice_samples_dir, exist_ok=True)
        os.makedirs(self.voice_outputs_dir, exist_ok=True)
        
        # Voice model parameters
        self.voice_models = self._load_voice_models()
        
        # Default voice presets for different demographics
        self.default_presets = {
            'elderly_female': {
                'rate': 0.85,
                'pitch': 1.05,
                'volume': 0.8,
                'clarity': 1.2,
                'dialect': 'standard',
                'age_factor': 1.3,
                'expressiveness': 0.9
            },
            'elderly_male': {
                'rate': 0.8,
                'pitch': 0.95,
                'volume': 0.85,
                'clarity': 1.1,
                'dialect': 'standard',
                'age_factor': 1.3,
                'expressiveness': 0.8
            },
            'adult_female': {
                'rate': 1.0,
                'pitch': 1.1,
                'volume': 0.9,
                'clarity': 1.0,
                'dialect': 'standard',
                'age_factor': 1.0,
                'expressiveness': 1.0
            },
            'adult_male': {
                'rate': 1.0,
                'pitch': 0.9,
                'volume': 1.0,
                'clarity': 1.0,
                'dialect': 'standard',
                'age_factor': 1.0,
                'expressiveness': 1.0
            }
        }
        
        self.logger.info("Voice Mimicry Engine initialized")
    
    def _load_voice_models(self):
        """Load existing voice models."""
        try:
            models = {}
            
            # Load each JSON file in the voice models directory
            if os.path.exists(self.voice_models_dir):
                for filename in os.listdir(self.voice_models_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(self.voice_models_dir, filename), 'r') as f:
                                model_data = json.load(f)
                                
                                # Extract patient ID from filename (patient_id_voice_model.json)
                                patient_id = filename.split('_')[0]
                                models[patient_id] = model_data
                        except Exception as e:
                            self.logger.error(f"Error loading voice model {filename}: {str(e)}")
            
            self.logger.info(f"Loaded {len(models)} voice models")
            return models
        
        except Exception as e:
            self.logger.error(f"Error loading voice models: {str(e)}")
            return {}
    
    def _save_voice_model(self, patient_id, model_data):
        """Save a voice model to file."""
        try:
            filepath = os.path.join(self.voice_models_dir, f"{patient_id}_voice_model.json")
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving voice model: {str(e)}")
            return False
    
    def create_voice_model(self, patient_id, gender=None, age=None, initial_samples=None):
        """
        Initialize a new voice model for a patient.
        
        Args:
            patient_id: ID of the patient
            gender: Optional gender ('female', 'male', 'other')
            age: Optional age in years
            initial_samples: Optional list of audio sample paths
            
        Returns:
            dict: The created voice model
        """
        try:
            # Determine default preset based on age and gender
            preset_key = None
            if gender and age:
                if gender.lower() in ['female', 'f']:
                    preset_key = 'elderly_female' if age > 65 else 'adult_female'
                elif gender.lower() in ['male', 'm']:
                    preset_key = 'elderly_male' if age > 65 else 'adult_male'
            
            # Use adult default if no match
            if not preset_key:
                preset_key = 'adult_female'
            
            # Create base voice model
            voice_model = {
                'patient_id': patient_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'sample_count': 0,
                'training_progress': 0.0,
                'parameters': self.default_presets[preset_key].copy(),
                'voice_samples': [],
                'voice_attributes': {
                    'gender': gender,
                    'age': age,
                    'dialect': 'standard',
                    'speech_patterns': [],
                    'phrase_emphasis': {},
                    'word_pronunciation': {}
                },
                'version': '1.0'
            }
            
            # Process initial samples if provided
            if initial_samples:
                for sample_path in initial_samples:
                    self.add_voice_sample(patient_id, sample_path)
            
            # Save the new model
            self.voice_models[patient_id] = voice_model
            self._save_voice_model(patient_id, voice_model)
            
            self.logger.info(f"Created new voice model for patient {patient_id}")
            return voice_model
        
        except Exception as e:
            self.logger.error(f"Error creating voice model: {str(e)}")
            return None
    
    def add_voice_sample(self, patient_id, audio_data=None, audio_path=None, transcript=None):
        """
        Add a voice sample to the patient's voice model.
        
        Args:
            patient_id: ID of the patient
            audio_data: Optional base64 encoded audio data
            audio_path: Optional path to audio file
            transcript: Optional transcript of the speech
            
        Returns:
            dict: Updated voice model or None if failed
        """
        try:
            # Check if patient has a voice model
            if patient_id not in self.voice_models:
                self.logger.warning(f"No voice model found for patient {patient_id}. Creating new model.")
                self.create_voice_model(patient_id)
            
            voice_model = self.voice_models[patient_id]
            
            # Generate sample ID
            sample_id = f"sample_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Save audio sample
            sample_filename = f"{patient_id}_{sample_id}.mp3"
            sample_path = os.path.join(self.voice_samples_dir, sample_filename)
            
            if audio_data:
                # Save base64 encoded audio
                try:
                    # Remove data URL prefix if present
                    if ',' in audio_data:
                        audio_data = audio_data.split(',')[1]
                    
                    # Decode base64 and save audio
                    with open(sample_path, 'wb') as f:
                        f.write(base64.b64decode(audio_data))
                except Exception as e:
                    self.logger.error(f"Error saving audio data: {str(e)}")
                    return None
            
            elif audio_path:
                # Copy audio from provided path
                try:
                    import shutil
                    shutil.copy(audio_path, sample_path)
                except Exception as e:
                    self.logger.error(f"Error copying audio from path: {str(e)}")
                    return None
            
            else:
                # No audio provided
                self.logger.error("No audio data or path provided")
                return None
            
            # Analyze the voice sample
            analysis = self._analyze_voice_sample(sample_path, transcript)
            
            if not analysis:
                self.logger.error("Voice analysis failed")
                return None
            
            # Add sample to voice model
            sample_data = {
                'id': sample_id,
                'path': sample_filename,
                'added_at': datetime.utcnow().isoformat(),
                'transcript': transcript,
                'analysis': analysis
            }
            
            voice_model['voice_samples'].append(sample_data)
            voice_model['sample_count'] += 1
            
            # Update voice model parameters based on new sample
            self._update_model_from_sample(voice_model, analysis)
            
            # Update timestamp
            voice_model['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated model
            self._save_voice_model(patient_id, voice_model)
            
            self.logger.info(f"Added voice sample for patient {patient_id}")
            return voice_model
        
        except Exception as e:
            self.logger.error(f"Error adding voice sample: {str(e)}")
            return None
    
    def _analyze_voice_sample(self, sample_path, transcript=None):
        """
        Analyze a voice sample to extract voice characteristics.
        In a real implementation, this would use audio processing libraries.
        For this prototype, we'll simulate analysis using OpenAI for transcript
        analysis if available.
        
        Args:
            sample_path: Path to the audio sample
            transcript: Optional transcript of the speech
            
        Returns:
            dict: Voice analysis data
        """
        try:
            # Basic analysis results with placeholder values
            analysis = {
                'rate': np.random.uniform(0.8, 1.2),  # Speech rate
                'pitch': np.random.uniform(0.8, 1.2),  # Pitch
                'volume': np.random.uniform(0.7, 1.0),  # Volume
                'clarity': np.random.uniform(0.8, 1.2),  # Clarity
                'confidence': 0.7  # Confidence in analysis
            }
            
            # If transcript is available, analyze it for speech patterns
            if transcript:
                # Use OpenAI to analyze the transcript for speech patterns
                analysis_prompt = f"""
                Analyze this speech transcript and extract speech pattern characteristics:
                "{transcript}"
                
                Provide your analysis as a JSON object with the following structure:
                {{
                    "speech_rate": 0.1-2.0 (0.1 is very slow, 1.0 is average, 2.0 is very fast),
                    "pitch_estimate": 0.1-2.0 (0.1 is very low, 1.0 is average, 2.0 is very high),
                    "pause_frequency": 0.1-2.0 (frequency of pauses, 1.0 is average),
                    "emphasized_words": ["word1", "word2"],
                    "speech_patterns": ["pattern1", "pattern2"],
                    "dialect_markers": ["marker1", "marker2"],
                    "repetition_patterns": ["pattern1", "pattern2"],
                    "filler_words": ["um", "like", etc]
                }}
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. Do not change this unless explicitly requested by the user
                    messages=[{"role": "system", "content": "You are a speech pattern analysis specialist."},
                             {"role": "user", "content": analysis_prompt}],
                    response_format={"type": "json_object"}
                )
                
                # Parse response
                text_analysis = json.loads(response.choices[0].message.content)
                
                # Update analysis with text-based insights
                analysis['rate'] = text_analysis.get('speech_rate', analysis['rate'])
                analysis['pitch'] = text_analysis.get('pitch_estimate', analysis['pitch'])
                analysis['pause_frequency'] = text_analysis.get('pause_frequency', 1.0)
                analysis['speech_patterns'] = text_analysis.get('speech_patterns', [])
                analysis['emphasized_words'] = text_analysis.get('emphasized_words', [])
                analysis['dialect_markers'] = text_analysis.get('dialect_markers', [])
                analysis['repetition_patterns'] = text_analysis.get('repetition_patterns', [])
                analysis['filler_words'] = text_analysis.get('filler_words', [])
                analysis['confidence'] = 0.9  # Higher confidence with transcript
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Error analyzing voice sample: {str(e)}")
            return None
    
    def _update_model_from_sample(self, voice_model, sample_analysis):
        """
        Update voice model parameters based on a new sample analysis.
        
        Args:
            voice_model: The voice model to update
            sample_analysis: Analysis data from a new sample
            
        Returns:
            None (updates voice_model in place)
        """
        try:
            # Extract current parameters
            params = voice_model['parameters']
            
            # Determine weight of new sample (depends on number of samples)
            sample_count = voice_model['sample_count']
            
            # Higher weights for early samples, lower as we get more data
            if sample_count <= 3:
                weight = 0.3  # First few samples have more weight
            elif sample_count <= 10:
                weight = 0.2
            else:
                weight = 0.1
            
            # Update numeric parameters with weighted average
            for param in ['rate', 'pitch', 'volume', 'clarity']:
                if param in sample_analysis:
                    params[param] = (1 - weight) * params[param] + weight * sample_analysis[param]
            
            # Update speech patterns
            if 'speech_patterns' in sample_analysis:
                existing_patterns = set(voice_model['voice_attributes'].get('speech_patterns', []))
                new_patterns = set(sample_analysis['speech_patterns'])
                
                # Add new patterns
                voice_model['voice_attributes']['speech_patterns'] = list(existing_patterns.union(new_patterns))
            
            # Update emphasized words dictionary
            if 'emphasized_words' in sample_analysis:
                word_emphasis = voice_model['voice_attributes'].get('phrase_emphasis', {})
                
                for word in sample_analysis['emphasized_words']:
                    word_emphasis[word] = word_emphasis.get(word, 0) + 1
                
                voice_model['voice_attributes']['phrase_emphasis'] = word_emphasis
            
            # Update dialect markers
            if 'dialect_markers' in sample_analysis:
                if len(sample_analysis['dialect_markers']) > 0:
                    # Simple approach: use most frequent dialect
                    voice_model['voice_attributes']['dialect'] = sample_analysis['dialect_markers'][0]
            
            # Update training progress
            voice_model['training_progress'] = min(1.0, 0.1 + 0.1 * sample_count)
        
        except Exception as e:
            self.logger.error(f"Error updating model from sample: {str(e)}")
    
    def generate_mimicked_speech(self, patient_id, text, context=None):
        """
        Generate speech that mimics the patient's voice.
        
        Args:
            patient_id: ID of the patient
            text: Text to convert to speech
            context: Optional context for speech generation
            
        Returns:
            dict: Result with audio file path and metadata
        """
        try:
            # Check if patient has a voice model
            use_mimicry = patient_id in self.voice_models
            
            if use_mimicry:
                voice_model = self.voice_models[patient_id]
                
                # Check if model has enough training
                if voice_model['sample_count'] < 3 or voice_model['training_progress'] < 0.3:
                    use_mimicry = False
                    self.logger.info(f"Voice model for patient {patient_id} has insufficient training, using default TTS")
            
            # Apply emphasis based on voice attributes if available
            emphasized_text = self._apply_emphasis(text, patient_id) if use_mimicry else text
            
            # Generate a unique filename
            timestamp = int(datetime.utcnow().timestamp())
            output_filename = f"{patient_id}_speech_{timestamp}.mp3"
            output_path = os.path.join(self.voice_outputs_dir, output_filename)
            
            # Get TTS parameters
            tts_params = self._get_tts_params(patient_id, context) if use_mimicry else {
                'lang': 'en',
                'slow': False,
                'tld': 'com'
            }
            
            # Generate speech using gTTS
            tts = gTTS(
                text=emphasized_text,
                lang=tts_params.get('lang', 'en'),
                slow=tts_params.get('slow', False),
                tld=tts_params.get('tld', 'com')
            )
            
            # Save the file
            tts.save(output_path)
            
            result = {
                'success': True,
                'patient_id': patient_id,
                'text': text,
                'file_path': output_path,
                'url': f'/static/audio/generated/{output_filename}',
                'mimicry_used': use_mimicry,
                'generated_at': datetime.utcnow().isoformat(),
                'emphasis_applied': emphasized_text != text
            }
            
            self.logger.info(f"Generated speech for patient {patient_id}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error generating mimicked speech: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text,
                'patient_id': patient_id
            }
    
    def _apply_emphasis(self, text, patient_id):
        """
        Apply word emphasis and speech patterns to text.
        
        Args:
            text: Text to process
            patient_id: ID of the patient
            
        Returns:
            str: Processed text with emphasis markers
        """
        try:
            if patient_id not in self.voice_models:
                return text
            
            voice_model = self.voice_models[patient_id]
            voice_attrs = voice_model['voice_attributes']
            
            # Get word emphasis dictionary
            emphasis = voice_attrs.get('phrase_emphasis', {})
            
            # No emphasis to apply
            if not emphasis:
                return text
            
            # Simple approach: add emphasis markers (SSML-like) for emphasized words
            words = text.split()
            emphasized_words = []
            
            for word in words:
                # Strip punctuation for matching
                clean_word = ''.join(c for c in word.lower() if c.isalnum())
                
                # Check if this word should be emphasized
                if clean_word in emphasis and emphasis[clean_word] > 1:
                    # Add emphasis markers
                    emphasized_words.append(f"<emphasis>{word}</emphasis>")
                else:
                    emphasized_words.append(word)
            
            # Combine back into text
            emphasized_text = ' '.join(emphasized_words)
            
            return emphasized_text
        
        except Exception as e:
            self.logger.error(f"Error applying emphasis: {str(e)}")
            return text
    
    def _get_tts_params(self, patient_id, context=None):
        """
        Get TTS parameters based on voice model and context.
        
        Args:
            patient_id: ID of the patient
            context: Optional context for parameter adjustment
            
        Returns:
            dict: TTS parameters
        """
        try:
            if patient_id not in self.voice_models:
                return {
                    'lang': 'en',
                    'slow': False,
                    'tld': 'com'
                }
            
            voice_model = self.voice_models[patient_id]
            params = voice_model['parameters']
            
            # Base parameters
            tts_params = {
                'lang': 'en',
                'slow': params['rate'] < 0.9,
                'tld': 'com'
            }
            
            # Adjust based on context if provided
            if context:
                # Example: slow down for important information
                if context.get('importance') == 'high':
                    tts_params['slow'] = True
                
                # Example: adjust language based on dialect
                dialect = voice_model['voice_attributes'].get('dialect', 'standard')
                if dialect == 'british':
                    tts_params['tld'] = 'co.uk'
                elif dialect == 'australian':
                    tts_params['tld'] = 'com.au'
            
            return tts_params
        
        except Exception as e:
            self.logger.error(f"Error getting TTS parameters: {str(e)}")
            return {
                'lang': 'en',
                'slow': False,
                'tld': 'com'
            }
    
    def get_voice_model(self, patient_id):
        """
        Get a patient's voice model.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: Voice model or None if not found
        """
        return self.voice_models.get(patient_id)
    
    def generate_voice_report(self, patient_id):
        """
        Generate a report about a patient's voice characteristics and changes over time.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            dict: Voice analysis report
        """
        try:
            if patient_id not in self.voice_models:
                return {
                    'success': False,
                    'error': f"No voice model found for patient {patient_id}"
                }
            
            voice_model = self.voice_models[patient_id]
            
            # Basic voice report
            report = {
                'patient_id': patient_id,
                'sample_count': voice_model['sample_count'],
                'training_progress': voice_model['training_progress'],
                'created_at': voice_model['created_at'],
                'updated_at': voice_model['updated_at'],
                'voice_characteristics': {
                    'rate': voice_model['parameters']['rate'],
                    'pitch': voice_model['parameters']['pitch'],
                    'clarity': voice_model['parameters'].get('clarity', 1.0),
                    'speech_patterns': voice_model['voice_attributes'].get('speech_patterns', []),
                    'dialect': voice_model['voice_attributes'].get('dialect', 'standard')
                },
                'common_emphasized_words': [],
                'sample_history': []
            }
            
            # Get top emphasized words
            emphasis = voice_model['voice_attributes'].get('phrase_emphasis', {})
            top_words = sorted(emphasis.items(), key=lambda x: x[1], reverse=True)[:10]
            report['common_emphasized_words'] = [word for word, count in top_words]
            
            # Add sample history (timestamps only)
            for sample in voice_model['voice_samples']:
                report['sample_history'].append({
                    'id': sample['id'],
                    'added_at': sample['added_at'],
                    'has_transcript': 'transcript' in sample and sample['transcript'] is not None
                })
            
            return {
                'success': True,
                'report': report
            }
        
        except Exception as e:
            self.logger.error(f"Error generating voice report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }