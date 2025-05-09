import os
import logging
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
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
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
            return redirect(url_for('index'))
        
        # Create new user
        password_hash = generate_password_hash(password)
        
        if user_type == 'patient':
            new_user = models.Patient(name=name, email=email, password_hash=password_hash)
        else:
            new_user = models.Caregiver(name=name, email=email, password_hash=password_hash)
            
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('index'))
        
    return render_template('index.html')

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
    
    return render_template('cognitive_exercises.html', patient=patient, exercises=exercises, reminders=reminders)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
