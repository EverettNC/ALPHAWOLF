import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import json
import schedule
import time
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///alphawolf.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Import services
from services.gesture_service import GestureService
from services.geolocation_service import GeolocationService
from services.reminder_service import ReminderService
from services.cognitive_service import CognitiveService
from services.caregiver_service import CaregiverService
from services.memory_exercises import MemoryExercises
from services.wandering_prevention import WanderingPrevention
from services.eye_tracking_service import EyeTrackingService
from services.neural_learning_core import NeuralLearningCore
from services.alphavox_input_nlu import AlphaVoxInputProcessor
from services.learning_journey import LearningJourney
from services.research_module import ResearchModule
from services.tts_engine import TTSEngine

# Initialize services
gesture_service = GestureService()
geolocation_service = GeolocationService()
reminder_service = ReminderService()
cognitive_service = CognitiveService()
caregiver_service = CaregiverService()
memory_exercises = MemoryExercises()
wandering_prevention = WanderingPrevention()
eye_tracking_service = EyeTrackingService()
neural_learning_core = NeuralLearningCore()
alphavox_input = AlphaVoxInputProcessor()
learning_journey = LearningJourney()
research_module = ResearchModule()
tts_engine = TTSEngine()

# Initialize AlphaVox-specific cognitive enhancement services
from services.adaptive_learning_system import AdaptiveLearningSystem
from services.voice_mimicry import VoiceMimicryEngine
from services.symbol_communication import SymbolCommunication
from services.ar_navigation import ARNavigationSystem
from services.cognitive_enhancement_module import CognitiveEnhancementModule

adaptive_learning = AdaptiveLearningSystem()
voice_mimicry = VoiceMimicryEngine()
symbol_communication = SymbolCommunication()
ar_navigation = ARNavigationSystem()
cognitive_enhancement = CognitiveEnhancementModule(
    adaptive_learning=adaptive_learning,
    voice_mimicry=voice_mimicry,
    symbol_communication=symbol_communication,
    ar_navigation=ar_navigation
)

with app.app_context():
    # Import models
    import models
    # Create tables
    db.create_all()
    
    # Initialize database with default safe zones if empty
    if not models.SafeZone.query.first():
        default_zones = [
            {"name": "Home", "latitude": 40.7128, "longitude": -74.0060, "radius": 100},
            {"name": "Park", "latitude": 40.7135, "longitude": -74.0046, "radius": 200}
        ]
        for zone in default_zones:
            db.session.add(models.SafeZone(**zone))
        db.session.commit()
        logger.info("Initialized default safe zones")
    
    # Initialize database with default cognitive exercises if empty
    if not models.CognitiveExercise.query.first():
        default_exercises = [
            {"name": "Memory Match", "description": "Match pairs of cards", "difficulty": "easy", "type": "memory"},
            {"name": "Pattern Recognition", "description": "Identify patterns in sequences", "difficulty": "medium", "type": "pattern"},
            {"name": "Word Association", "description": "Connect related words", "difficulty": "medium", "type": "language"},
            {"name": "Picture Recall", "description": "Remember and identify images", "difficulty": "hard", "type": "memory"}
        ]
        for exercise in default_exercises:
            db.session.add(models.CognitiveExercise(**exercise))
        db.session.commit()
        logger.info("Initialized default cognitive exercises")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_schedule)
scheduler_thread.daemon = True
scheduler_thread.start()

# Routes
@app.route('/')
def index():
    """Minimal landing page for AlphaWolf"""
    # If user is already logged in, redirect to their dashboard
    if session.get('user_id'):
        if session.get('user_type') == 'patient':
            return redirect(url_for('patient_dashboard'))
        else:
            return redirect(url_for('caregiver_dashboard'))
    return render_template('landing.html')

@app.route('/home')
def home():
    """Homepage with features, how it works, and sign in options"""
    # If user is already logged in, redirect to their dashboard
    if session.get('user_id'):
        if session.get('user_type') == 'patient':
            return redirect(url_for('patient_dashboard'))
        else:
            return redirect(url_for('caregiver_dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for patients and caregivers"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        if user_type == 'patient':
            user = models.Patient.query.filter_by(email=email).first()
        else:
            user = models.Caregiver.query.filter_by(email=email).first()
            
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_type'] = user_type
            flash('Login successful!', 'success')
            if user_type == 'patient':
                return redirect(url_for('patient_dashboard'))
            else:
                return redirect(url_for('caregiver_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page for patients and caregivers"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        # Check if email already exists
        if user_type == 'patient':
            existing_user = models.Patient.query.filter_by(email=email).first()
        else:
            existing_user = models.Caregiver.query.filter_by(email=email).first()
            
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        password_hash = generate_password_hash(password)
        
        if user_type == 'patient':
            new_user = models.Patient(name=name, email=email, password_hash=password_hash)
        else:
            new_user = models.Caregiver(name=name, email=email, password_hash=password_hash)
            
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/patient/dashboard')
def patient_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'patient':
        flash('Please log in as a patient to access the dashboard', 'error')
        return redirect(url_for('index'))
    
    patient = models.Patient.query.get(session['user_id'])
    exercises = models.CognitiveExercise.query.all()
    reminders = models.Reminder.query.filter_by(patient_id=session['user_id']).all()
    
    # Get the current date for display
    today_date = datetime.now().strftime("%A, %B %d, %Y")
    
    return render_template('patient_dashboard.html', 
                          patient=patient, 
                          exercises=exercises, 
                          reminders=reminders,
                          today_date=today_date)

@app.route('/caregiver/dashboard')
def caregiver_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'caregiver':
        flash('Please log in as a caregiver to access the dashboard', 'error')
        return redirect(url_for('index'))
    
    caregiver = models.Caregiver.query.get(session['user_id'])
    patients = models.Patient.query.all()  # In a real app, filter by caregiver-patient relationship
    safe_zones = models.SafeZone.query.all()
    
    return render_template('caregiver_dashboard.html', caregiver=caregiver, patients=patients, safe_zones=safe_zones)

@app.route('/cognitive/exercises')
def cognitive_exercises():
    if 'user_id' not in session:
        flash('Please log in to access exercises', 'error')
        return redirect(url_for('index'))
    
    exercises = models.CognitiveExercise.query.all()
    return render_template('cognitive_exercises.html', exercises=exercises)

@app.route('/exercise/<int:exercise_id>')
def exercise_detail(exercise_id):
    if 'user_id' not in session:
        flash('Please log in to access exercises', 'error')
        return redirect(url_for('index'))
    
    exercise = models.CognitiveExercise.query.get_or_404(exercise_id)
    return render_template('exercise_detail.html', exercise=exercise)

@app.route('/reminders')
def reminders():
    if 'user_id' not in session:
        flash('Please log in to access reminders', 'error')
        return redirect(url_for('index'))
    
    if session.get('user_type') == 'patient':
        reminders = models.Reminder.query.filter_by(patient_id=session['user_id']).all()
    else:
        # Caregivers can see reminders for all associated patients
        reminders = models.Reminder.query.all()  # In a real app, filter by caregiver-patient relationship
    
    return render_template('reminders.html', reminders=reminders)

@app.route('/reminders/add', methods=['POST'])
def add_reminder():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    patient_id = data.get('patient_id', session['user_id'] if session.get('user_type') == 'patient' else None)
    title = data.get('title')
    description = data.get('description')
    time = data.get('time')
    recurring = data.get('recurring', False)
    
    if not all([patient_id, title, time]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    new_reminder = models.Reminder(
        patient_id=patient_id,
        title=title,
        description=description,
        time=time,
        recurring=recurring
    )
    
    db.session.add(new_reminder)
    db.session.commit()
    
    # Update the scheduler
    reminder_service.schedule_reminder(new_reminder)
    
    return jsonify({'success': True, 'message': 'Reminder added successfully'})

@app.route('/safety/zones')
def safety_zones():
    if 'user_id' not in session:
        flash('Please log in to access safety zones', 'error')
        return redirect(url_for('index'))
    
    safe_zones = models.SafeZone.query.all()
    patients = models.Patient.query.all()  # In production, filter by caregiver-patient relationship
    
    # Check if each patient is in a safe zone
    for patient in patients:
        if patient.last_latitude and patient.last_longitude:
            safety_status = geolocation_service.check_safe_zones(
                patient.id, patient.last_latitude, patient.last_longitude
            )
            patient.is_in_safe_zone = safety_status.get('is_safe', False)
        else:
            patient.is_in_safe_zone = None  # No location data
    
    # Prepare JSON data for the map
    safe_zones_json = []
    for zone in safe_zones:
        safe_zones_json.append({
            'id': zone.id,
            'name': zone.name,
            'latitude': zone.latitude,
            'longitude': zone.longitude,
            'radius': zone.radius
        })
    
    patients_json = []
    for patient in patients:
        if patient.last_latitude and patient.last_longitude:
            patients_json.append({
                'id': patient.id,
                'name': patient.name,
                'last_latitude': patient.last_latitude,
                'last_longitude': patient.last_longitude,
                'last_location_update': patient.last_location_update.isoformat() if patient.last_location_update else None,
                'is_in_safe_zone': patient.is_in_safe_zone
            })
    
    return render_template(
        'safety_zones.html', 
        safe_zones=safe_zones, 
        patients=patients,
        safe_zones_json=json.dumps(safe_zones_json),
        patients_json=json.dumps(patients_json)
    )

@app.route('/safety/zones/add', methods=['POST'])
def add_safety_zone():
    if 'user_id' not in session or session.get('user_type') != 'caregiver':
        flash('Please log in as a caregiver to add safety zones', 'error')
        return redirect(url_for('safety_zones'))
    
    # If it's a form submission (not JSON)
    name = request.form.get('name')
    latitude = float(request.form.get('latitude'))
    longitude = float(request.form.get('longitude'))
    radius = float(request.form.get('radius', 100))  # Default radius of 100 meters
    
    if not all([name, latitude, longitude]):
        flash('Missing required fields', 'error')
        return redirect(url_for('safety_zones'))
    
    # Use the geolocation service to add the zone
    result = geolocation_service.add_safe_zone(name, latitude, longitude, radius)
    
    if result.get('success'):
        flash(f'Safety zone "{name}" added successfully', 'success')
    else:
        flash(f'Error adding safety zone: {result.get("error")}', 'error')
    
    return redirect(url_for('safety_zones'))

@app.route('/safety/zones/update', methods=['POST'])
def update_safety_zone():
    if 'user_id' not in session or session.get('user_type') != 'caregiver':
        flash('Please log in as a caregiver to update safety zones', 'error')
        return redirect(url_for('safety_zones'))
    
    zone_id = int(request.form.get('zone_id'))
    name = request.form.get('name')
    latitude = float(request.form.get('latitude'))
    longitude = float(request.form.get('longitude'))
    radius = float(request.form.get('radius'))
    
    # Use the geolocation service to update the zone
    result = geolocation_service.update_safe_zone(zone_id, name, latitude, longitude, radius)
    
    if result.get('success'):
        flash(f'Safety zone "{name}" updated successfully', 'success')
    else:
        flash(f'Error updating safety zone: {result.get("error")}', 'error')
    
    return redirect(url_for('safety_zones'))

@app.route('/safety/zones/delete', methods=['POST'])
def delete_safety_zone():
    if 'user_id' not in session or session.get('user_type') != 'caregiver':
        flash('Please log in as a caregiver to delete safety zones', 'error')
        return redirect(url_for('safety_zones'))
    
    zone_id = int(request.form.get('zone_id'))
    
    # Use the geolocation service to delete the zone
    result = geolocation_service.delete_safe_zone(zone_id)
    
    if result.get('success'):
        flash('Safety zone deleted successfully', 'success')
    else:
        flash(f'Error deleting safety zone: {result.get("error")}', 'error')
    
    return redirect(url_for('safety_zones'))

@app.route('/location/update', methods=['POST'])
def update_location():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not all([latitude, longitude]):
        return jsonify({'success': False, 'message': 'Missing location data'}), 400
    
    # Update patient location
    patient = models.Patient.query.get(session['user_id'])
    if patient:
        patient.last_latitude = latitude
        patient.last_longitude = longitude
        patient.last_location_update = db.func.now()
        db.session.commit()
        
        # Check for wandering
        is_wandering = wandering_prevention.check_wandering(patient, models.SafeZone.query.all())
        if is_wandering:
            # Create alert for caregivers
            alert = models.Alert(
                patient_id=patient.id,
                alert_type='wandering',
                latitude=latitude,
                longitude=longitude,
                message=f"{patient.name} may be wandering outside safe zones"
            )
            db.session.add(alert)
            db.session.commit()
            
            # Notify caregivers (in a real app, this would use MQTT or push notifications)
            caregiver_service.notify_caregivers(alert)
    
    return jsonify({'success': True, 'message': 'Location updated'})

@app.route('/alerts')
def alerts():
    if 'user_id' not in session or session.get('user_type') != 'caregiver':
        flash('Please log in as a caregiver to view alerts', 'error')
        return redirect(url_for('index'))
    
    alerts = models.Alert.query.order_by(models.Alert.timestamp.desc()).limit(50).all()
    safe_zones = models.SafeZone.query.all()
    
    # Prepare JSON data for the map
    safe_zones_json = []
    for zone in safe_zones:
        safe_zones_json.append({
            'id': zone.id,
            'name': zone.name,
            'latitude': zone.latitude,
            'longitude': zone.longitude,
            'radius': zone.radius
        })
    
    alerts_json = []
    for alert in alerts:
        if alert.latitude and alert.longitude:
            alerts_json.append({
                'id': alert.id,
                'patient_id': alert.patient_id,
                'message': alert.message,
                'alert_type': alert.alert_type,
                'latitude': alert.latitude,
                'longitude': alert.longitude,
                'is_resolved': alert.is_resolved,
                'timestamp': alert.timestamp.isoformat() if alert.timestamp else None
            })
    
    return render_template(
        'alerts.html', 
        alerts=alerts, 
        safe_zones_json=json.dumps(safe_zones_json),
        alerts_json=json.dumps(alerts_json)
    )

@app.route('/alerts/resolve', methods=['POST'])
def resolve_alert():
    if 'user_id' not in session or session.get('user_type') != 'caregiver':
        flash('Please log in as a caregiver to resolve alerts', 'error')
        return redirect(url_for('alerts'))
    
    alert_id = int(request.form.get('alert_id'))
    
    # Use the caregiver service to resolve the alert
    result = caregiver_service.resolve_alert(alert_id)
    
    if result:
        flash('Alert marked as resolved', 'success')
    else:
        flash('Error resolving alert', 'error')
    
    return redirect(url_for('alerts'))

@app.route('/api/gesture', methods=['POST'])
def process_gesture():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    gesture_data = data.get('gesture_data')
    
    if not gesture_data:
        return jsonify({'success': False, 'message': 'No gesture data provided'}), 400
    
    # Process gesture using gesture service
    gesture_type = gesture_service.process_gesture(gesture_data)
    
    if gesture_type:
        return jsonify({'success': True, 'gesture': gesture_type})
    else:
        return jsonify({'success': False, 'message': 'Gesture not recognized'})

@app.route('/api/exercise/result', methods=['POST'])
def save_exercise_result():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    exercise_id = data.get('exercise_id')
    score = data.get('score')
    completion_time = data.get('completion_time')
    
    if not all([exercise_id, score is not None]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    result = models.ExerciseResult(
        patient_id=session['user_id'],
        exercise_id=exercise_id,
        score=score,
        completion_time=completion_time
    )
    
    db.session.add(result)
    db.session.commit()
    
    # Update patient's cognitive profile based on results
    cognitive_service.update_cognitive_profile(result)
    
    return jsonify({'success': True, 'message': 'Result saved successfully'})

@app.route('/user/profile')
def user_profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile', 'error')
        return redirect(url_for('index'))
    
    if session.get('user_type') == 'patient':
        user = models.Patient.query.get(session['user_id'])
        exercise_results = models.ExerciseResult.query.filter_by(patient_id=user.id).order_by(models.ExerciseResult.timestamp.desc()).limit(10).all()
        cognitive_profile = models.CognitiveProfile.query.filter_by(patient_id=user.id).first()
        return render_template('user_profile.html', user=user, results=exercise_results, cognitive_profile=cognitive_profile)
    else:
        user = models.Caregiver.query.get(session['user_id'])
        return render_template('user_profile.html', user=user)

@app.route('/cognitive_features')
def cognitive_features():
    if 'user_id' not in session:
        flash('Please log in to access cognitive features', 'error')
        return redirect(url_for('index'))
    
    if session.get('user_type') == 'patient':
        patient = models.Patient.query.get(session['user_id'])
    else:
        # For caregivers, get the first patient (in a real app, this would be a selected patient)
        patient = models.Patient.query.first()
        if not patient:
            flash('No patients found in the system', 'error')
            return redirect(url_for('caregiver_dashboard'))
    
    # Initialize cognitive model for the patient if needed
    cognitive_enhancement.initialize_patient_model(patient.id, {
        'demographics': {
            'gender': patient.gender if hasattr(patient, 'gender') else None,
            'age': patient.age if hasattr(patient, 'age') else None
        }
    })
    
    return render_template('cognitive_features.html', patient=patient)

@app.route('/api/chart/cognitive/progress/<int:patient_id>')
def cognitive_progress_chart(patient_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get last 30 results for chart
    results = models.ExerciseResult.query.filter_by(patient_id=patient_id).order_by(models.ExerciseResult.timestamp.asc()).limit(30).all()
    
    chart_data = {
        'labels': [result.timestamp.strftime('%Y-%m-%d') for result in results],
        'scores': [result.score for result in results],
        'types': [models.CognitiveExercise.query.get(result.exercise_id).type for result in results]
    }
    
    return jsonify(chart_data)

# New AlphaVox Cognitive Enhancement Routes

@app.route('/api/cognitive/initialize/<int:patient_id>', methods=['POST'])
def cognitive_initialize(patient_id):
    """Initialize or update cognitive services for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get patient data from request body
    patient_data = request.json or {}
    
    # Initialize the cognitive model for the patient
    result = cognitive_enhancement.initialize_patient_model(patient_id, patient_data)
    
    if result:
        return jsonify({
            'success': True,
            'message': 'Cognitive services initialized',
            'model': result
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to initialize cognitive services'
        }), 500

@app.route('/api/cognitive/status/<int:patient_id>', methods=['GET'])
def cognitive_status(patient_id):
    """Get cognitive status and learning progress for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get the patient's cognitive status
    result = cognitive_enhancement.get_patient_cognitive_status(patient_id)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/cognitive/interact/<int:patient_id>', methods=['POST'])
def cognitive_interact(patient_id):
    """Process a patient interaction and update models."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get interaction data from request body
    interaction_data = request.json or {}
    
    # Process the interaction
    result = cognitive_enhancement.process_interaction(patient_id, interaction_data)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/cognitive/generate/<int:patient_id>/<content_type>', methods=['POST'])
def cognitive_generate(patient_id, content_type):
    """Generate personalized content for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get generation parameters from request body
    parameters = request.json or {}
    
    # Generate personalized content
    result = cognitive_enhancement.generate_personalized_content(patient_id, content_type, parameters)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/cognitive/preferences/<int:patient_id>', methods=['PUT'])
def cognitive_update_preferences(patient_id):
    """Update preferences for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get preference updates from request body
    preferences = request.json or {}
    
    # Update preferences
    result = cognitive_enhancement.update_patient_preferences(patient_id, preferences)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/cognitive/component/<int:patient_id>/<component_name>', methods=['PUT'])
def cognitive_toggle_component(patient_id, component_name):
    """Enable or disable a cognitive component for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get active state from request body
    data = request.json or {}
    active = data.get('active', True)
    
    # Toggle component
    result = cognitive_enhancement.toggle_component(patient_id, component_name, active)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/symbols/<int:patient_id>', methods=['GET'])
def get_symbol_board(patient_id):
    """Get a patient's symbol communication board."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get the patient's symbol board
    board = symbol_communication.get_user_board(patient_id)
    
    if board:
        return jsonify({
            'success': True,
            'board': board
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Symbol board not found'
        }), 404

@app.route('/api/symbols/<int:patient_id>', methods=['POST'])
def create_symbol_board(patient_id):
    """Create a new symbol board for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get board data from request body
    data = request.json or {}
    
    # Create a new symbol board
    board = symbol_communication.create_symbol_board(
        patient_id,
        data.get('name', 'My Symbol Board'),
        data.get('categories')
    )
    
    if board:
        return jsonify({
            'success': True,
            'board': board
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to create symbol board'
        }), 500

@app.route('/api/symbols/<int:patient_id>/symbol', methods=['POST'])
def add_custom_symbol(patient_id):
    """Add a custom symbol to a patient's board."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get symbol data from request body
    data = request.json or {}
    
    # Add custom symbol
    symbol = symbol_communication.add_custom_symbol(
        patient_id,
        data.get('category'),
        data.get('name'),
        data.get('description'),
        data.get('image_data')
    )
    
    if symbol:
        return jsonify({
            'success': True,
            'symbol': symbol
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to add custom symbol'
        }), 500

@app.route('/api/symbols/<int:patient_id>/suggestions', methods=['GET'])
def get_symbol_suggestions(patient_id):
    """Get contextual symbol suggestions for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get context parameters from query string
    time_of_day = request.args.get('time_of_day')
    location = request.args.get('location')
    
    # Get contextual suggestions
    suggestions = symbol_communication.get_contextual_suggestions(
        patient_id,
        time_of_day,
        location
    )
    
    return jsonify({
        'success': True,
        'suggestions': suggestions
    })

@app.route('/api/voice/<int:patient_id>/generate', methods=['POST'])
def generate_voice(patient_id):
    """Generate speech that mimics the patient's voice."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get text to convert to speech
    data = request.json or {}
    text = data.get('text', '')
    
    if not text:
        return jsonify({
            'success': False,
            'message': 'No text provided'
        }), 400
    
    # Generate speech
    result = voice_mimicry.generate_mimicked_speech(
        patient_id,
        text,
        data.get('context')
    )
    
    if result.get('success'):
        return jsonify({
            'success': True,
            'speech': result
        })
    else:
        return jsonify({
            'success': False,
            'message': result.get('error', 'Failed to generate speech'),
            'text': text
        }), 500

@app.route('/api/voice/<int:patient_id>/sample', methods=['POST'])
def add_voice_sample(patient_id):
    """Add a voice sample to train the voice mimicry system."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get voice sample data
    data = request.json or {}
    
    # Add voice sample
    result = voice_mimicry.add_voice_sample(
        patient_id,
        data.get('audio_data'),
        None,  # audio_path
        data.get('transcript')
    )
    
    if result:
        return jsonify({
            'success': True,
            'message': 'Voice sample added successfully'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to add voice sample'
        }), 500

@app.route('/api/navigation/<int:patient_id>/layouts', methods=['GET'])
def get_navigation_layouts(patient_id):
    """Get all AR navigation layouts for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get patient layouts
    layouts = ar_navigation.get_patient_layouts(patient_id)
    
    return jsonify({
        'success': True,
        'layouts': layouts
    })

@app.route('/api/navigation/<int:patient_id>/layout', methods=['POST'])
def add_navigation_layout(patient_id):
    """Add a new AR navigation layout for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get layout data
    data = request.json or {}
    
    # Add layout
    layout = ar_navigation.add_location_layout(
        patient_id,
        data.get('name', 'New Layout'),
        data,
        data.get('floor_plan_image')
    )
    
    if layout:
        return jsonify({
            'success': True,
            'layout': layout
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to add layout'
        }), 500

@app.route('/api/navigation/<int:patient_id>/instructions', methods=['POST'])
def get_navigation_instructions(patient_id):
    """Generate navigation instructions for a patient."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Get navigation parameters
    data = request.json or {}
    
    # Generate instructions
    instructions = ar_navigation.generate_navigation_instructions(
        patient_id,
        data.get('layout_id'),
        data.get('start_name'),
        data.get('end_name'),
        data.get('complexity', 'simple')
    )
    
    if instructions:
        return jsonify({
            'success': True,
            'instructions': instructions
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to generate navigation instructions'
        }), 500

# New pages for AlphaWolf platform
@app.route('/learning-corner')
def learning_corner():
    """Learning resources about dementia and Alzheimer's."""
    from services.research_service import ResearchService
    
    # Initialize research service
    research_service = ResearchService()
    
    # Get research articles
    research_articles = research_service.get_research_articles(limit=6)
    
    # Get daily tip
    daily_tip = research_service.get_daily_tip()
    
    # Get expert insights
    expert_insights = research_service.get_expert_insights(limit=3)
    
    # Get resources
    resources = research_service.get_resources()
    
    return render_template('learning_corner.html', 
                          research_articles=research_articles,
                          daily_tip=daily_tip,
                          expert_insights=expert_insights, 
                          resources=resources)

@app.route('/caregivers')
def caregivers_page():
    """Support and tools for caregivers."""
    # In a production version, we would load actual data for the caregiver
    if 'user_id' in session and session.get('user_type') == 'caregiver':
        caregiver = models.Caregiver.query.get(session['user_id'])
        # Fetch associated patients
        patients = models.Patient.query.all()  # In a real app, filter by caregiver-patient relationship
        return render_template('caregivers_page.html', caregiver=caregiver, patients=patients)
    
    return render_template('caregivers_page.html')

@app.route('/caregivers/videos')
def caregiver_videos():
    """Training videos for caregivers."""
    # Define video categories and their content
    videos = [
        {
            'id': 1,
            'title': 'Safe Transferring Techniques',
            'description': 'Learn how to safely assist a person with dementia when moving between bed, chair, or bathroom.',
            'thumbnail': 'https://source.unsplash.com/300x200/?healthcare',
            'duration': '5:32',
            'categories': ['Daily Care', 'Safety']
        },
        {
            'id': 2,
            'title': 'Bathing and Hygiene Tips',
            'description': 'Strategies to make bathing and personal hygiene more comfortable for both patient and caregiver.',
            'thumbnail': 'https://source.unsplash.com/300x200/?wellness',
            'duration': '7:15',
            'categories': ['Daily Care', 'Comfort']
        },
        {
            'id': 3,
            'title': 'Redirection Strategies',
            'description': 'How to handle challenging behaviors through effective communication and redirection.',
            'thumbnail': 'https://source.unsplash.com/300x200/?communication',
            'duration': '8:45',
            'categories': ['Behavior', 'Communication']
        },
        {
            'id': 4,
            'title': 'Emotion-Focused Care',
            'description': 'Understanding the emotional needs of dementia patients and responding with empathy.',
            'thumbnail': 'https://source.unsplash.com/300x200/?empathy',
            'duration': '6:20',
            'categories': ['Emotional Support', 'Communication']
        }
    ]
    
    return render_template('caregiver_videos.html', videos=videos)

@app.route('/caregivers/video/<int:video_id>')
def caregiver_video_detail(video_id):
    """Display a specific training video."""
    # In a real app, we'd fetch video details from a database
    videos = {
        1: {
            'id': 1,
            'title': 'Safe Transferring Techniques',
            'description': 'Learn how to safely assist a person with dementia when moving between bed, chair, or bathroom.',
            'embed_code': '<iframe width="100%" height="450" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
            'transcript': 'In this video, we cover the basics of safe transferring techniques for individuals with dementia. Always remember to protect your own body mechanics while ensuring the safety and dignity of the person in your care.',
            'tips': [
                'Always communicate clearly before beginning a transfer',
                'Ensure proper body mechanics to prevent caregiver injury',
                'Use assistive devices when appropriate',
                'Promote as much independence as possible'
            ]
        },
        2: {
            'id': 2,
            'title': 'Bathing and Hygiene Tips',
            'description': 'Strategies to make bathing and personal hygiene more comfortable for both patient and caregiver.',
            'embed_code': '<iframe width="100%" height="450" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
            'transcript': 'This video covers strategies for making bathing and hygiene routines more comfortable for individuals with dementia. We discuss creating a calm environment and addressing common challenges.',
            'tips': [
                'Maintain a consistent routine',
                'Create a warm, comfortable environment',
                'Use distraction and positive reinforcement',
                'Consider alternative bathing methods when needed'
            ]
        },
        3: {
            'id': 3,
            'title': 'Redirection Strategies',
            'description': 'How to handle challenging behaviors through effective communication and redirection.',
            'embed_code': '<iframe width="100%" height="450" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
            'transcript': 'In this video, we explore effective redirection strategies for caregivers of people with dementia. Learn how to de-escalate situations and redirect attention in a positive way.',
            'tips': [
                'Validate feelings before redirecting',
                'Use clear, simple language',
                'Offer meaningful alternatives',
                'Stay calm and patient throughout the process'
            ]
        },
        4: {
            'id': 4,
            'title': 'Emotion-Focused Care',
            'description': 'Understanding the emotional needs of dementia patients and responding with empathy.',
            'embed_code': '<iframe width="100%" height="450" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
            'transcript': 'This video focuses on the emotional aspects of dementia care. Learn techniques for recognizing emotional cues and responding with empathy and understanding.',
            'tips': [
                'Focus on the feeling, not just the behavior',
                'Use validation rather than correction',
                'Maintain meaningful connections through activities',
                'Practice self-awareness of your own emotions'
            ]
        }
    }
    
    video = videos.get(video_id)
    if not video:
        flash('Video not found', 'error')
        return redirect(url_for('caregiver_videos'))
    
    return render_template('caregiver_video_detail.html', video=video)

@app.route('/caregivers/assessment')
def caregiver_assessment():
    """Caregiver stress assessment tool."""
    assessment_questions = [
        {
            'id': 1,
            'text': 'How often do you feel overwhelmed by your caregiving responsibilities?',
            'options': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
        },
        {
            'id': 2,
            'text': 'How often do you feel you don\'t have enough time for yourself because of caregiving?',
            'options': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
        },
        {
            'id': 3,
            'text': 'How often do you experience stress-related physical symptoms (headaches, fatigue, etc.)?',
            'options': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
        },
        {
            'id': 4,
            'text': 'How often do you feel emotionally drained because of your caregiving role?',
            'options': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
        },
        {
            'id': 5,
            'text': 'How often do you feel socially isolated or like you\'ve lost connection with friends?',
            'options': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
        },
        {
            'id': 6,
            'text': 'How often do you feel you\'re not doing enough for the person you\'re caring for?',
            'options': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
        },
        {
            'id': 7,
            'text': 'How difficult is it for you to find time for relaxation or hobbies?',
            'options': ['Not difficult', 'Slightly difficult', 'Moderately difficult', 'Very difficult', 'Extremely difficult']
        },
        {
            'id': 8,
            'text': 'How would you rate your overall stress level as a caregiver?',
            'options': ['Very low', 'Low', 'Moderate', 'High', 'Very high']
        },
        {
            'id': 9,
            'text': 'How often do you feel uncertain about what to do about the person you\'re caring for?',
            'options': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
        },
        {
            'id': 10,
            'text': 'How well are you taking care of your own health and well-being?',
            'options': ['Very well', 'Well', 'Moderately well', 'Not very well', 'Not at all']
        }
    ]
    
    return render_template('caregiver_assessment.html', questions=assessment_questions)

@app.route('/caregivers/assessment/results', methods=['POST'])
def caregiver_assessment_results():
    """Process and display results of the caregiver stress assessment."""
    # Process form submission
    responses = {}
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            responses[question_id] = int(value)
    
    # Calculate stress score (0-40)
    # Questions 1-6, 9: Never=0, Rarely=1, Sometimes=2, Often=3, Always=4
    # Question 7: Not difficult=0 to Extremely difficult=4
    # Question 8: Very low=0 to Very high=4
    # Question 10: Very well=0 to Not at all=4 (reversed scale)
    
    stress_score = sum(responses.values())
    
    # Determine stress level and recommendations
    if stress_score <= 10:
        stress_level = "Low"
        color_class = "success"
        recommendations = [
            "Continue your current self-care practices",
            "Maintain your support network",
            "Consider joining a caregiver support group to share experiences",
            "Keep a journal to track changes in your stress levels"
        ]
    elif stress_score <= 20:
        stress_level = "Moderate"
        color_class = "warning"
        recommendations = [
            "Schedule regular breaks throughout your caregiving day",
            "Practice relaxation techniques like deep breathing or meditation",
            "Connect with other caregivers for emotional support",
            "Consider respite care options to give yourself time off",
            "Talk to your doctor about your stress levels"
        ]
    else:
        stress_level = "High"
        color_class = "danger"
        recommendations = [
            "Speak with a healthcare professional about your stress levels",
            "Look into regular respite care options",
            "Join a support group for caregivers",
            "Consider counseling or therapy for stress management",
            "Delegate responsibilities when possible",
            "Explore community resources for additional support",
            "Make your own health a priority—schedule medical check-ups"
        ]
    
    # Resources for all stress levels
    resources = [
        {
            'name': 'Alzheimer\'s Association Caregiver Support',
            'url': 'https://www.alz.org/help-support/caregiving',
            'description': 'Support groups, education, and resources for caregivers.'
        },
        {
            'name': 'Caregiver Action Network',
            'url': 'https://caregiveraction.org/',
            'description': 'Education, peer support, and resources for family caregivers.'
        },
        {
            'name': 'National Alliance for Caregiving',
            'url': 'https://www.caregiving.org/',
            'description': 'Research, advocacy, and innovation for family caregivers.'
        },
        {
            'name': 'Family Caregiver Alliance',
            'url': 'https://www.caregiver.org/',
            'description': 'Information, education, and services for family caregivers.'
        }
    ]
    
    # Get current datetime for the results page
    now = datetime.now()
    
    return render_template('caregiver_assessment_results.html', 
                          stress_score=stress_score,
                          stress_level=stress_level,
                          color_class=color_class,
                          recommendations=recommendations,
                          resources=resources,
                          now=now)

@app.route('/memory-lane')
def memory_lane():
    """Memory preservation and reminiscence tools."""
    return render_template('memory_lane.html')

@app.route('/voice-control-help')
def voice_control_help():
    """Documentation and help for voice control features."""
    return render_template('voice_control_help.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
