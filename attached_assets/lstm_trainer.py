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
"""
AlphaVox - LSTM Model Trainer
----------------------------
Author: Everett Christman & Python (AI)
Project: The Christman AI Project - AlphaVox
Mission: Legends are our only option

This script trains LSTM models to recognize temporal patterns in:
1. Gestures and body movements (including ticks)
2. Eye movements (including blinking patterns)
3. Emotional state transitions

LSTM (Long Short-Term Memory) networks are particularly suited for temporal data,
as they can learn patterns across sequences of observations, unlike our previous
RandomForest classifiers which treated each data point independently.
"""

import os
import numpy as np
import pickle
import logging
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create directories for models
MODEL_DIR = 'lstm_models'
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

def simulate_gesture_sequence_data(n_samples=200, time_steps=10, n_features=4):
    """
    Generate simulated gesture sequence data.
    
    Args:
        n_samples: Number of samples to generate
        time_steps: Number of time steps per sequence
        n_features: Number of features per time step
        
    Returns:
        Tuple of (X, y) where X is the sequence data and y is the labels
    """
    logger.info(f"Generating {n_samples} simulated gesture sequences")
    
    # Create empty arrays for data and labels
    X = np.zeros((n_samples, time_steps, n_features))
    y = np.zeros(n_samples, dtype=int)
    
    # Generate data for 4 gesture types (roughly 25% each)
    gesture_types = 4
    samples_per_type = n_samples // gesture_types
    
    for gesture_type in range(gesture_types):
        start_idx = gesture_type * samples_per_type
        end_idx = start_idx + samples_per_type if gesture_type < gesture_types - 1 else n_samples
        
        # For each sample of this gesture type
        for i in range(start_idx, end_idx):
            # Set the label
            y[i] = gesture_type
            
            # Create a base pattern for this gesture type
            base_pattern = np.random.normal(loc=gesture_type, scale=0.1, size=n_features)
            
            # Fill in the sequence with variations of the base pattern
            for t in range(time_steps):
                # Add some temporal variation to the pattern
                temporal_factor = np.sin(t / time_steps * np.pi) * 0.5 + 0.5
                variation = np.random.normal(loc=0, scale=0.05, size=n_features)
                X[i, t] = base_pattern * temporal_factor + variation
    
    return X, y

def simulate_eye_movement_data(n_samples=150, time_steps=10, n_features=3):
    """
    Generate simulated eye movement sequence data.
    
    Args:
        n_samples: Number of samples to generate
        time_steps: Number of time steps per sequence
        n_features: Number of features per time step
        
    Returns:
        Tuple of (X, y) where X is the sequence data and y is the labels
    """
    logger.info(f"Generating {n_samples} simulated eye movement sequences")
    
    # Create empty arrays for data and labels
    X = np.zeros((n_samples, time_steps, n_features))
    y = np.zeros(n_samples, dtype=int)
    
    # Generate data for 2 eye movement types
    movement_types = 2
    samples_per_type = n_samples // movement_types
    
    for movement_type in range(movement_types):
        start_idx = movement_type * samples_per_type
        end_idx = start_idx + samples_per_type if movement_type < movement_types - 1 else n_samples
        
        # For each sample of this movement type
        for i in range(start_idx, end_idx):
            # Set the label
            y[i] = movement_type
            
            # Create specific patterns for each eye movement type
            if movement_type == 0:  # Looking Up
                # Gaze starts at middle, moves up, then may wander slightly
                for t in range(time_steps):
                    gaze_x = 0.5 + np.random.normal(0, 0.05)  # Centered X with slight variation
                    gaze_y = max(0.2, 0.5 - 0.3 * (t / (time_steps-1)))  # Moving up (Y decreases)
                    blink_rate = 3 + np.random.normal(0, 0.5)  # Normal blink rate
                    X[i, t] = [gaze_x, gaze_y, blink_rate]
            
            else:  # Rapid Blinking (movement_type == 1)
                # Gaze is generally central but blink rate increases
                for t in range(time_steps):
                    gaze_x = 0.5 + np.random.normal(0, 0.05)
                    gaze_y = 0.5 + np.random.normal(0, 0.05)
                    # Blink rate increases over time
                    blink_rate = 3 + 9 * (t / (time_steps-1)) + np.random.normal(0, 1)
                    X[i, t] = [gaze_x, gaze_y, blink_rate]
    
    return X, y

def simulate_emotion_sequence_data(n_samples=180, time_steps=10, n_features=5):
    """
    Generate simulated emotional state sequence data.
    
    Args:
        n_samples: Number of samples to generate
        time_steps: Number of time steps per sequence
        n_features: Number of features per time step
        
    Returns:
        Tuple of (X, y) where X is the sequence data and y is the labels
    """
    logger.info(f"Generating {n_samples} simulated emotional state sequences")
    
    # Create empty arrays for data and labels
    X = np.zeros((n_samples, time_steps, n_features))
    y = np.zeros(n_samples, dtype=int)
    
    # Generate data for 6 emotion types
    emotion_types = 6  # neutral, happy, sad, angry, fear, surprise
    samples_per_type = n_samples // emotion_types
    
    for emotion_type in range(emotion_types):
        start_idx = emotion_type * samples_per_type
        end_idx = start_idx + samples_per_type if emotion_type < emotion_types - 1 else n_samples
        
        # For each sample of this emotion type
        for i in range(start_idx, end_idx):
            # Set the label
            y[i] = emotion_type
            
            # Create a base pattern for this emotion type
            # Features: [facial_tension, mouth_curve, eye_openness, eyebrow_position, perspiration]
            if emotion_type == 0:  # Neutral
                base_pattern = np.array([0.5, 0.5, 0.5, 0.5, 0.3])
            elif emotion_type == 1:  # Happy
                base_pattern = np.array([0.3, 0.8, 0.6, 0.6, 0.4])
            elif emotion_type == 2:  # Sad
                base_pattern = np.array([0.6, 0.2, 0.4, 0.3, 0.5])
            elif emotion_type == 3:  # Angry
                base_pattern = np.array([0.8, 0.3, 0.7, 0.8, 0.7])
            elif emotion_type == 4:  # Fear
                base_pattern = np.array([0.7, 0.4, 0.8, 0.7, 0.9])
            else:  # Surprise (emotion_type == 5)
                base_pattern = np.array([0.4, 0.6, 0.9, 0.9, 0.6])
            
            # Fill in the sequence with variations and temporal progression
            for t in range(time_steps):
                # Emotion intensifies over time
                intensity_factor = 0.7 + 0.3 * (t / (time_steps-1))
                variation = np.random.normal(loc=0, scale=0.05, size=n_features)
                
                # Calculate feature values with intensity and variation
                features = base_pattern * intensity_factor + variation
                
                # Ensure values are in valid range [0, 1]
                features = np.clip(features, 0, 1)
                
                X[i, t] = features
    
    return X, y

def train_gesture_lstm_model():
    """Train LSTM model for gesture sequences"""
    logger.info("Training gesture LSTM model...")
    
    # Generate or load data
    X, y = simulate_gesture_sequence_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Get model parameters
    n_samples, time_steps, n_features = X.shape
    n_classes = len(np.unique(y))
    
    # Build LSTM model
    model = Sequential([
        LSTM(64, input_shape=(time_steps, n_features), return_sequences=True),
        Dropout(0.3),
        LSTM(32, return_sequences=False),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dense(n_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Define early stopping
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    # Train model
    logger.info("Fitting gesture LSTM model...")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=1
    )
    
    # Evaluate model
    logger.info("Evaluating gesture LSTM model...")
    loss, accuracy = model.evaluate(X_test, y_test)
    logger.info(f"Gesture LSTM model accuracy: {accuracy:.4f}")
    
    # Get predictions
    y_pred = np.argmax(model.predict(X_test), axis=1)
    
    # Print classification report
    gesture_labels = ['Hand Up', 'Wave Left', 'Wave Right', 'Head Jerk']
    logger.info("Gesture LSTM classification report:")
    logger.info(classification_report(y_test, y_pred, target_names=gesture_labels))
    
    # Save model
    model_path = os.path.join(MODEL_DIR, 'gesture_lstm_model')
    model.save(model_path)
    logger.info(f"Gesture LSTM model saved to {model_path}")
    
    # Save labels
    labels_path = os.path.join(MODEL_DIR, 'gesture_labels.pkl')
    with open(labels_path, 'wb') as f:
        pickle.dump(gesture_labels, f)
    logger.info(f"Gesture labels saved to {labels_path}")
    
    return model

def train_eye_movement_lstm_model():
    """Train LSTM model for eye movement sequences"""
    logger.info("Training eye movement LSTM model...")
    
    # Generate or load data
    X, y = simulate_eye_movement_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Get model parameters
    n_samples, time_steps, n_features = X.shape
    n_classes = len(np.unique(y))
    
    # Build LSTM model
    model = Sequential([
        LSTM(48, input_shape=(time_steps, n_features), return_sequences=True),
        Dropout(0.3),
        LSTM(24, return_sequences=False),
        Dropout(0.3),
        Dense(16, activation='relu'),
        Dense(n_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Define early stopping
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    # Train model
    logger.info("Fitting eye movement LSTM model...")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=16,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=1
    )
    
    # Evaluate model
    logger.info("Evaluating eye movement LSTM model...")
    loss, accuracy = model.evaluate(X_test, y_test)
    logger.info(f"Eye movement LSTM model accuracy: {accuracy:.4f}")
    
    # Get predictions
    y_pred = np.argmax(model.predict(X_test), axis=1)
    
    # Print classification report
    eye_labels = ['Looking Up', 'Rapid Blinking']
    logger.info("Eye movement LSTM classification report:")
    logger.info(classification_report(y_test, y_pred, target_names=eye_labels))
    
    # Save model
    model_path = os.path.join(MODEL_DIR, 'eye_movement_lstm_model')
    model.save(model_path)
    logger.info(f"Eye movement LSTM model saved to {model_path}")
    
    # Save labels
    labels_path = os.path.join(MODEL_DIR, 'eye_movement_labels.pkl')
    with open(labels_path, 'wb') as f:
        pickle.dump(eye_labels, f)
    logger.info(f"Eye movement labels saved to {labels_path}")
    
    return model

def train_emotion_lstm_model():
    """Train LSTM model for emotional state sequences"""
    logger.info("Training emotion LSTM model...")
    
    # Generate or load data
    X, y = simulate_emotion_sequence_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Get model parameters
    n_samples, time_steps, n_features = X.shape
    n_classes = len(np.unique(y))
    
    # Build LSTM model
    model = Sequential([
        LSTM(96, input_shape=(time_steps, n_features), return_sequences=True),
        Dropout(0.4),
        LSTM(48, return_sequences=False),
        Dropout(0.4),
        Dense(32, activation='relu'),
        Dense(n_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Define early stopping
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    # Train model
    logger.info("Fitting emotion LSTM model...")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=1
    )
    
    # Evaluate model
    logger.info("Evaluating emotion LSTM model...")
    loss, accuracy = model.evaluate(X_test, y_test)
    logger.info(f"Emotion LSTM model accuracy: {accuracy:.4f}")
    
    # Get predictions
    y_pred = np.argmax(model.predict(X_test), axis=1)
    
    # Print classification report
    emotion_labels = ['Neutral', 'Happy', 'Sad', 'Angry', 'Fear', 'Surprise']
    logger.info("Emotion LSTM classification report:")
    logger.info(classification_report(y_test, y_pred, target_names=emotion_labels))
    
    # Save model
    model_path = os.path.join(MODEL_DIR, 'emotion_lstm_model')
    model.save(model_path)
    logger.info(f"Emotion LSTM model saved to {model_path}")
    
    # Save labels
    labels_path = os.path.join(MODEL_DIR, 'emotion_labels.pkl')
    with open(labels_path, 'wb') as f:
        pickle.dump(emotion_labels, f)
    logger.info(f"Emotion labels saved to {labels_path}")
    
    return model

def main():
    """Train all LSTM models"""
    logger.info("Starting AlphaVox LSTM model training...")
    
    try:
        # Set memory growth to avoid OOM errors
        physical_devices = tf.config.list_physical_devices('GPU')
        if physical_devices:
            for device in physical_devices:
                tf.config.experimental.set_memory_growth(device, True)
            logger.info(f"Found {len(physical_devices)} GPU(s), enabled memory growth")
        else:
            logger.info("No GPU found, using CPU for training")
    except Exception as e:
        logger.warning(f"Failed to configure GPU memory growth, using default configuration: {e}")
    
    # Train models
    gesture_model = train_gesture_lstm_model()
    eye_movement_model = train_eye_movement_lstm_model()
    emotion_model = train_emotion_lstm_model()
    
    logger.info("All LSTM models trained and saved successfully!")
    
    return {
        'gesture_model': gesture_model,
        'eye_movement_model': eye_movement_model,
        'emotion_model': emotion_model
    }

if __name__ == '__main__':
    main()