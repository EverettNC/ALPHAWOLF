import logging
from datetime import datetime

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class AudioPatternService:
    """Service for analyzing and interpreting non-verbal sounds."""

    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.pattern_threshold = 0.6
        self.sound_patterns = {
            "excited": {"freq_range": (300, 800), "duration": 0.5, "intensity": 0.7},
            "distressed": {
                "freq_range": (400, 1200),
                "duration": 0.3,
                "intensity": 0.8,
            },
            "content": {"freq_range": (200, 600), "duration": 0.4, "intensity": 0.5},
            "seeking_attention": {
                "freq_range": (500, 1000),
                "duration": 0.6,
                "intensity": 0.9,
            },
        }
        logger.info("AudioPatternService initialized with default patterns")

    def analyze_sound(self, audio_data):
        """Analyze incoming audio data for pattern matching."""
        try:
            # Convert audio data to numpy array for processing
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Calculate audio features
            intensity = np.mean(np.abs(audio_array))
            frequency = self._estimate_frequency(audio_array)
            duration = len(audio_array) / self.sample_rate

            # Match against known patterns
            matches = []
            for pattern_name, pattern in self.sound_patterns.items():
                match_score = self._calculate_pattern_match(
                    frequency, duration, intensity, pattern
                )
                if match_score > self.pattern_threshold:
                    matches.append(
                        {
                            "pattern": pattern_name,
                            "confidence": match_score,
                            "timestamp": datetime.utcnow(),
                        }
                    )

            return matches if matches else [{"pattern": "unknown", "confidence": 0.0}]

        except Exception as e:
            logger.error(f"Error analyzing audio pattern: {str(e)}", exc_info=True)
            return [{"pattern": "error", "confidence": 0.0}]

    def _estimate_frequency(self, audio_array):
        """Estimate the fundamental frequency of the audio signal."""
        try:
            # Simple zero-crossing rate for frequency estimation
            zero_crossings = np.where(np.diff(np.signbit(audio_array)))[0]
            if len(zero_crossings) > 1:
                return len(zero_crossings) * self.sample_rate / (2 * len(audio_array))
            return 0
        except Exception as e:
            logger.error(f"Error estimating frequency: {str(e)}")
            return 0

    def _calculate_pattern_match(self, freq, duration, intensity, pattern):
        """Calculate how well the current audio matches a known pattern."""
        try:
            freq_match = (
                1.0
                if pattern["freq_range"][0] <= freq <= pattern["freq_range"][1]
                else 0.0
            )
            duration_match = 1.0 if abs(duration - pattern["duration"]) < 0.2 else 0.0
            intensity_match = (
                1.0 if abs(intensity - pattern["intensity"]) < 0.2 else 0.0
            )

            # Weight the different components
            return freq_match * 0.4 + duration_match * 0.3 + intensity_match * 0.3
        except Exception as e:
            logger.error(f"Error calculating pattern match: {str(e)}")
            return 0.0

    def update_pattern(self, pattern_name, audio_data):
        """Update existing patterns based on new audio data."""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            frequency = self._estimate_frequency(audio_array)
            intensity = np.mean(np.abs(audio_array))
            duration = len(audio_array) / self.sample_rate

            # Update pattern if it exists
            if pattern_name in self.sound_patterns:
                current = self.sound_patterns[pattern_name]
                # Gradually adapt pattern based on new data
                current["freq_range"] = (
                    (current["freq_range"][0] * 0.9 + frequency * 0.1),
                    (current["freq_range"][1] * 0.9 + frequency * 1.1 * 0.1),
                )
                current["intensity"] = current["intensity"] * 0.9 + intensity * 0.1
                current["duration"] = current["duration"] * 0.9 + duration * 0.1
                logger.info(f"Updated pattern: {pattern_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating pattern: {str(e)}")
            return False
