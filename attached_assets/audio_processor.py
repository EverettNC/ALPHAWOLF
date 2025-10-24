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
"""Audio processor module for AlphaVox.

This module provides functionality for audio processing, including:
- Speech recognition from audio data
- Audio device discovery
- Audio format conversion
"""

import base64
import json
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional

# Audio processing libraries
import numpy as np

try:
    # Import the speech recognition engine
    from real_speech_recognition import (
        RealSpeechRecognition,
        get_speech_recognition_engine,
    )

    real_speech_available = True
except ImportError:
    real_speech_available = False
    logging.warning("Real speech recognition not available")


class AudioProcessor:
    """Processes audio data for speech recognition and other audio tasks."""

    def __init__(self):
        """Initialize the audio processor."""
        self.recognition_engine = None
        self._init_recognition_engine()
        logging.info(
            f"Audio processor initialized with real speech: {real_speech_available}"
        )

    def _init_recognition_engine(self):
        """Initialize the speech recognition engine."""
        if real_speech_available:
            try:
                self.recognition_engine = get_speech_recognition_engine()
                logging.info("Real speech recognition engine initialized")
            except Exception as e:
                logging.error(f"Error initializing speech recognition engine: {str(e)}")
                self.recognition_engine = None
        else:
            logging.warning("Using simulated speech recognition")
            self.recognition_engine = None

    def get_available_devices(self) -> List[Dict[str, Any]]:
        """Get available audio input devices.

        Returns:
            list: List of available audio devices with details
        """
        devices = []

        # Get real audio devices if available
        if real_speech_available and self.recognition_engine:
            try:
                real_devices = self.recognition_engine.get_audio_devices()
                devices.extend(real_devices)
                logging.info(f"Found {len(real_devices)} real audio devices")
            except Exception as e:
                logging.error(f"Error getting real audio devices: {str(e)}")

        # Add a simulated device if no real devices found
        if not devices:
            devices.append(
                {
                    "id": "sim-1",
                    "name": "Simulated Microphone",
                    "channels": 1,
                    "default": True,
                }
            )

        return devices

    def process_audio(self, audio_data: str) -> Dict[str, Any]:
        """Process audio data for speech recognition.

        Args:
            audio_data: Base64-encoded audio data

        Returns:
            dict: Recognition results with text and confidence
        """
        # Check if real speech recognition is available
        if not real_speech_available or not self.recognition_engine:
            # Simulated recognition
            logging.info("Using simulated speech recognition")
            return {"text": "Speech recognition simulated", "confidence": 0.8}

        try:
            # Decode the base64 audio data
            audio_bytes = base64.b64decode(audio_data)

            # Save to a temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_bytes)

            # Process the audio file
            result = self.recognition_engine.recognize_from_file(temp_path)

            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

            return {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
            }

        except Exception as e:
            logging.error(f"Error processing audio: {str(e)}")
            return {"error": str(e)}


# Create a singleton instance
_audio_processor = None


def get_audio_processor() -> AudioProcessor:
    """Get the singleton audio processor instance."""
    global _audio_processor
    if _audio_processor is None:
        _audio_processor = AudioProcessor()
    return _audio_processor


# Flask route registration
def register_audio_routes(app):
    """Register audio processing routes with the Flask app.

    Args:
        app: Flask application instance
    """
    from flask import jsonify, request

    # Get the audio processor instance
    audio_processor = get_audio_processor()

    @app.route("/api/audio/devices", methods=["GET"])
    def get_audio_devices():
        """API endpoint to get available audio devices."""
        try:
            devices = audio_processor.get_available_devices()
            return jsonify(devices)
        except Exception as e:
            logging.error(f"Error getting audio devices: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/audio/process", methods=["POST"])
    def process_audio():
        """API endpoint to process audio data for speech recognition."""
        try:
            data = request.get_json()
            if not data or "audio_data" not in data:
                return jsonify({"error": "No audio data provided"}), 400

            audio_data = data["audio_data"]
            result = audio_processor.process_audio(audio_data)

            return jsonify(result)
        except Exception as e:
            logging.error(f"Error processing audio: {str(e)}")
            return jsonify({"error": str(e)}), 500

    logging.info("Audio routes registered")
