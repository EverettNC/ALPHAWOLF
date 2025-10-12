import logging
import os
import pickle

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Directory to save trained models (ensure existence)
MODEL_DIR = "lstm_models"
os.makedirs(MODEL_DIR, exist_ok=True)

# ----------------------------
# Simulation Data Generators
# ----------------------------


def simulate_gesture_sequence_data(n_samples=200, time_steps=10, n_features=4):
    logger.info(f"Generating {n_samples} simulated gesture sequences")
    X = np.zeros((n_samples, time_steps, n_features))
    y = np.zeros(n_samples, dtype=int)

    gesture_types = 4
    samples_per_type = n_samples // gesture_types

    for gesture_type in range(gesture_types):
        start_idx = gesture_type * samples_per_type
        end_idx = (
            (start_idx + samples_per_type)
            if gesture_type < gesture_types - 1
            else n_samples
        )

        for i in range(start_idx, end_idx):
            y[i] = gesture_type
            # Base pattern for this gesture
            base_pattern = np.random.normal(
                loc=gesture_type, scale=0.1, size=n_features
            )
            for t in range(time_steps):
                temporal_factor = np.sin(t / time_steps * np.pi) * 0.5 + 0.5
                variation = np.random.normal(loc=0, scale=0.05, size=n_features)
                X[i, t] = base_pattern * temporal_factor + variation

    return X, y


def simulate_eye_movement_data(n_samples=150, time_steps=10, n_features=3):
    logger.info(f"Generating {n_samples} simulated eye movement sequences")
    X = np.zeros((n_samples, time_steps, n_features))
    y = np.zeros(n_samples, dtype=int)

    movement_types = 2
    samples_per_type = n_samples // movement_types

    for movement_type in range(movement_types):
        start_idx = movement_type * samples_per_type
        end_idx = (
            (start_idx + samples_per_type)
            if movement_type < movement_types - 1
            else n_samples
        )

        for i in range(start_idx, end_idx):
            y[i] = movement_type
            if movement_type == 0:  # Looking Up
                for t in range(time_steps):
                    gaze_x = 0.5 + np.random.normal(0, 0.05)
                    gaze_y = max(0.2, 0.5 - 0.3 * (t / (time_steps - 1)))
                    blink_rate = 3 + np.random.normal(0, 0.5)
                    X[i, t] = [gaze_x, gaze_y, blink_rate]
            else:  # Rapid Blinking
                for t in range(time_steps):
                    gaze_x = 0.5 + np.random.normal(0, 0.05)
                    gaze_y = 0.5 + np.random.normal(0, 0.05)
                    blink_rate = 3 + 9 * (t / (time_steps - 1)) + np.random.normal(0, 1)
                    X[i, t] = [gaze_x, gaze_y, blink_rate]

    return X, y


def simulate_emotion_sequence_data(n_samples=180, time_steps=10, n_features=5):
    logger.info(f"Generating {n_samples} simulated emotional state sequences")
    X = np.zeros((n_samples, time_steps, n_features))
    y = np.zeros(n_samples, dtype=int)

    emotion_types = 6  # neutral, happy, sad, angry, fear, surprise
    samples_per_type = n_samples // emotion_types

    for emotion_type in range(emotion_types):
        start_idx = emotion_type * samples_per_type
        end_idx = (
            (start_idx + samples_per_type)
            if emotion_type < emotion_types - 1
            else n_samples
        )

        # Define base pattern for each emotion
        if emotion_type == 0:
            base_pattern = np.array([0.5, 0.5, 0.5, 0.5, 0.3])
        elif emotion_type == 1:
            base_pattern = np.array([0.3, 0.8, 0.6, 0.6, 0.4])
        elif emotion_type == 2:
            base_pattern = np.array([0.6, 0.2, 0.4, 0.3, 0.5])
        elif emotion_type == 3:
            base_pattern = np.array([0.8, 0.3, 0.7, 0.8, 0.7])
        elif emotion_type == 4:
            base_pattern = np.array([0.7, 0.4, 0.8, 0.7, 0.9])
        else:
            base_pattern = np.array([0.4, 0.6, 0.9, 0.9, 0.6])

        for i in range(start_idx, end_idx):
            y[i] = emotion_type
            for t in range(time_steps):
                intensity_factor = 0.7 + 0.3 * (t / (time_steps - 1))
                variation = np.random.normal(loc=0, scale=0.05, size=n_features)
                features = base_pattern * intensity_factor + variation
                features = np.clip(features, 0, 1)
                X[i, t] = features

    return X, y


# ----------------------------
# Training and Model Builders
# ----------------------------
def train_gesture_lstm_model():
    logger.info("Training gesture LSTM model...")
    X, y = simulate_gesture_sequence_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    n_samples, time_steps, n_features = X.shape
    n_classes = len(np.unique(y))

    model = Sequential(
        [
            LSTM(64, input_shape=(time_steps, n_features), return_sequences=True),
            Dropout(0.3),
            LSTM(32, return_sequences=False),
            Dropout(0.3),
            Dense(32, activation="relu"),
            Dense(n_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )

    early_stopping = EarlyStopping(
        monitor="val_loss", patience=10, restore_best_weights=True
    )

    history = model.fit(
        X_train,
        y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=1,
    )

    loss, accuracy = model.evaluate(X_test, y_test)
    logger.info(f"Gesture LSTM accuracy: {accuracy:.4f}")

    y_pred = np.argmax(model.predict(X_test), axis=1)
    gesture_labels = ["Hand Up", "Wave Left", "Wave Right", "Head Jerk"]
    logger.info(
        "Gesture classification report:\n"
        + classification_report(y_test, y_pred, target_names=gesture_labels)
    )

    model_path = "lstm_models/gesture_lstm_model.keras"
    model.save(model_path)
    logger.info(f"Saved gesture model to {model_path}")

    labels_path = os.path.join(MODEL_DIR, "gesture_labels.pkl")
    with open(labels_path, "wb") as f:
        pickle.dump(gesture_labels, f)
    logger.info(f"Saved gesture labels to {labels_path}")

    return model


def train_eye_movement_lstm_model():
    logger.info("Training eye movement LSTM model...")
    X, y = simulate_eye_movement_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    _, time_steps, n_features = X.shape
    n_classes = len(np.unique(y))

    model = Sequential(
        [
            LSTM(48, input_shape=(time_steps, n_features), return_sequences=True),
            Dropout(0.3),
            LSTM(24, return_sequences=False),
            Dropout(0.3),
            Dense(16, activation="relu"),
            Dense(n_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )
    early_stopping = EarlyStopping(
        monitor="val_loss", patience=10, restore_best_weights=True
    )

    history = model.fit(
        X_train,
        y_train,
        epochs=50,
        batch_size=16,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=1,
    )

    loss, accuracy = model.evaluate(X_test, y_test)
    logger.info(f"Eye movement LSTM accuracy: {accuracy:.4f}")

    y_pred = np.argmax(model.predict(X_test), axis=1)
    eye_labels = ["Looking Up", "Rapid Blinking"]
    logger.info(
        "Eye movement classification report:\n"
        + classification_report(y_test, y_pred, target_names=eye_labels)
    )

    model_path = os.path.join(MODEL_DIR, "eye_movement_lstm_model")
    model.save(model_path)
    logger.info(f"Saved eye movement model to {model_path}")

    labels_path = os.path.join(MODEL_DIR, "eye_movement_labels.pkl")
    with open(labels_path, "wb") as f:
        pickle.dump(eye_labels, f)
    logger.info(f"Saved eye movement labels to {labels_path}")

    return model


def train_emotion_lstm_model():
    logger.info("Training emotion LSTM model...")
    X, y = simulate_emotion_sequence_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    _, time_steps, n_features = X.shape
    n_classes = len(np.unique(y))

    model = Sequential(
        [
            LSTM(96, input_shape=(time_steps, n_features), return_sequences=True),
            Dropout(0.4),
            LSTM(48, return_sequences=False),
            Dropout(0.4),
            Dense(32, activation="relu"),
            Dense(n_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )
    early_stopping = EarlyStopping(
        monitor="val_loss", patience=10, restore_best_weights=True
    )

    history = model.fit(
        X_train,
        y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=1,
    )

    loss, accuracy = model.evaluate(X_test, y_test)
    logger.info(f"Emotion LSTM accuracy: {accuracy:.4f}")

    y_pred = np.argmax(model.predict(X_test), axis=1)
    emotion_labels = ["Neutral", "Happy", "Sad", "Angry", "Fear", "Surprise"]
    logger.info(
        "Emotion classification report:\n"
        + classification_report(y_test, y_pred, target_names=emotion_labels)
    )

    model_path = os.path.join(MODEL_DIR, "emotion_lstm_model")
    model.save(model_path)
    logger.info(f"Saved emotion model to {model_path}")

    labels_path = os.path.join(MODEL_DIR, "emotion_labels.pkl")
    with open(labels_path, "wb") as f:
        pickle.dump(emotion_labels, f)
    logger.info(f"Saved emotion labels to {labels_path}")

    return model


def main():
    logger.info("Starting training of all LSTM models...")

    try:
        physical_devices = tf.config.list_physical_devices("GPU")
        if physical_devices:
            for dev in physical_devices:
                tf.config.experimental.set_memory_growth(dev, True)
            logger.info(f"Found {len(physical_devices)} GPU(s); memory growth enabled")
        else:
            logger.info("No GPU available; using CPU")
    except Exception as e:
        logger.warning(f"Could not configure GPU memory growth: {e}")

    gesture_model = train_gesture_lstm_model()
    model_path = "lstm_models/eye_movement_lstm_model.keras"

    emotion_model = train_emotion_lstm_model()

    logger.info("All LSTM models trained.")
    return {
        "gesture_model": gesture_model,
        "eye_movement_model": eye_model,
        "emotion_model": emotion_model,
    }


if __name__ == "__main__":
    main()
