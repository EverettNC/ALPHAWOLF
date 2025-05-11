###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# MODELS MODULE
# Database models and relationships for the AlphaWolf platform
###############################################################################

from app import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

class Patient(UserMixin, db.Model):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    date_of_birth = Column(DateTime)
    diagnosis = Column(String(200))
    emergency_contact = Column(String(200))
    last_latitude = Column(Float)
    last_longitude = Column(Float)
    last_location_update = Column(DateTime)
    points = Column(Integer, default=0)  # Total points earned from exercises
    level = Column(Integer, default=1)  # Current level in the gamification system
    streak_days = Column(Integer, default=0)  # Consecutive days with exercises
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reminders = relationship("Reminder", backref="patient", lazy=True)
    cognitive_profile = relationship("CognitiveProfile", backref="patient", uselist=False, lazy=True)
    exercise_results = relationship("ExerciseResult", backref="patient", lazy=True)
    alerts = relationship("Alert", backref="patient", lazy=True)
    point_transactions = relationship("PointTransaction", backref="patient", lazy=True)
    achievements_earned = relationship("PatientAchievement", backref="patient", lazy=True)
    rewards_redeemed = relationship("PatientReward", backref="patient", lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.name}>'

class Caregiver(UserMixin, db.Model):
    __tablename__ = 'caregivers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    phone = Column(String(20))
    relationship_to_patient = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Caregiver {self.name}>'

class CognitiveExercise(db.Model):
    __tablename__ = 'cognitive_exercises'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty = Column(String(20), default='medium')  # easy, medium, hard
    type = Column(String(50))  # memory, pattern, language, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    results = relationship("ExerciseResult", backref="exercise", lazy=True)
    
    def __repr__(self):
        return f'<CognitiveExercise {self.name}>'

class ExerciseResult(db.Model):
    __tablename__ = 'exercise_results'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('cognitive_exercises.id'), nullable=False)
    score = Column(Float, nullable=False)
    completion_time = Column(Float)  # in seconds
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExerciseResult {self.patient_id} {self.exercise_id} {self.score}>'

class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    time = Column(String(50), nullable=False)  # Time in format HH:MM or cron format
    recurring = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reminder {self.title}>'

class SafeZone(db.Model):
    __tablename__ = 'safe_zones'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)  # in meters
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SafeZone {self.name}>'

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    alert_type = Column(String(50), nullable=False)  # wandering, fall, etc.
    message = Column(Text, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    is_resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert {self.alert_type} for {self.patient_id}>'

class CognitiveProfile(db.Model):
    __tablename__ = 'cognitive_profiles'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, unique=True)
    memory_score = Column(Float, default=0.0)
    attention_score = Column(Float, default=0.0)
    language_score = Column(Float, default=0.0)
    pattern_recognition_score = Column(Float, default=0.0)
    problem_solving_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CognitiveProfile {self.patient_id}>'

class GestureLog(db.Model):
    __tablename__ = 'gesture_logs'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    gesture_type = Column(String(50), nullable=False)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GestureLog {self.gesture_type}>'

class Achievement(db.Model):
    """Achievements that patients can earn through various activities"""
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(100))  # Path or class name for the icon
    category = Column(String(50))  # Exercise completion, streak, level, etc.
    requirement = Column(Integer, nullable=False)  # Numeric requirement to earn it
    points_reward = Column(Integer, default=0)  # Points awarded when earned
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_achievements = relationship("PatientAchievement", backref="achievement", lazy=True)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'

class PatientAchievement(db.Model):
    """Record of achievements earned by patients"""
    __tablename__ = 'patient_achievements'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PatientAchievement {self.patient_id} {self.achievement_id}>'

class Reward(db.Model):
    """Rewards that can be redeemed with points"""
    __tablename__ = 'rewards'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(100))
    points_cost = Column(Integer, nullable=False)
    is_virtual = Column(Boolean, default=True)  # Virtual vs physical reward
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_rewards = relationship("PatientReward", backref="reward", lazy=True)
    
    def __repr__(self):
        return f'<Reward {self.name}>'

class PatientReward(db.Model):
    """Record of rewards redeemed by patients"""
    __tablename__ = 'patient_rewards'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    reward_id = Column(Integer, ForeignKey('rewards.id'), nullable=False)
    redeemed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PatientReward {self.patient_id} {self.reward_id}>'

class PointTransaction(db.Model):
    """Record of point transactions for patients"""
    __tablename__ = 'point_transactions'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    points = Column(Integer, nullable=False)  # Positive for earned, negative for spent
    transaction_type = Column(String(50), nullable=False)  # exercise_completion, achievement, reward_redemption
    reference_id = Column(Integer)  # ID of the related entity (exercise result, achievement, etc.)
    description = Column(String(200))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PointTransaction {self.patient_id} {self.points} {self.transaction_type}>'

class ExerciseStreak(db.Model):
    """Tracks consecutive days of exercise activity"""
    __tablename__ = 'exercise_streaks'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_exercise_date = Column(DateTime)
    
    # Relationships
    patient = relationship("Patient", backref="exercise_streak", uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<ExerciseStreak {self.patient_id} {self.current_streak}>'
