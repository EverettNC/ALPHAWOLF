import logging
from typing import Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class VoiceAnalysisService:
    def __init__(self):
        self.gesture_responses = {
            "wave_left": {
                "default": "I see you waving left",
                "confident": "Great left wave!",
                "uncertain": "Try moving your left hand more clearly",
            },
            "wave_right": {
                "default": "I see you waving right",
                "confident": "Excellent right wave!",
                "uncertain": "Try moving your right hand more smoothly",
            },
            "hand_up": {
                "default": "Hand raised",
                "confident": "Perfect hand raise!",
                "uncertain": "Try raising your hand a bit higher",
            },
            "hand_down": {
                "default": "Hand lowered",
                "confident": "Smooth downward motion!",
                "uncertain": "Try lowering your hand more steadily",
            },
            "circular": {
                "default": "Circular motion detected",
                "confident": "Beautiful circular movement!",
                "uncertain": "Try making a more complete circle",
            },
            "two_hands": {
                "default": "Two hands detected",
                "confident": "Perfect two-handed gesture!",
                "uncertain": "Try keeping both hands visible",
            },
        }

    def gesture_to_speech(self, gesture: str, confidence: float = 0.0) -> str:
        """Convert a gesture to speech feedback based on confidence level.

        Args:
            gesture: The type of gesture detected
            confidence: Confidence level of the gesture detection (0.0 to 1.0)

        Returns:
            Appropriate speech response based on gesture and confidence
        """
        try:
            responses = self.gesture_responses.get(
                gesture,
                {
                    "default": "Movement detected",
                    "confident": "Good movement!",
                    "uncertain": "Try that movement again",
                },
            )

            if confidence > 0.8:
                return responses["confident"]
            elif confidence < 0.4:
                return responses["uncertain"]
            else:
                return responses["default"]

        except Exception as e:
            logger.error(f"Error generating speech for gesture {gesture}: {str(e)}")
            return "I noticed your gesture"

    def analyze_tone(
        self, audio_data: bytes
    ) -> Tuple[Dict[str, float], Dict[str, float], float]:
        """Enhanced analyzer for both verbal and non-verbal communication
        patterns.

        Specifically tuned for neurodivergent communication patterns including:
        - Emotional states
        - Sound patterns
        - Rhythm variations
        - Communication styles

        Returns: (emotions dict, communication_patterns dict, confidence score)
        """
        try:
            if not audio_data:
                logger.error("Empty audio data received")
                return self._get_default_response()

            # Convert audio data to numpy array with error handling
            try:
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
                audio_array = np.clip(audio_array, -1.0, 1.0)

                if len(audio_array) == 0:
                    logger.error("Invalid audio data format")
                    return self._get_default_response()
            except ValueError as e:
                logger.error(f"Error converting audio data: {str(e)}")
                return self._get_default_response()

            # Extract enhanced audio features
            amplitude = np.abs(audio_array)
            mean_amplitude = float(np.mean(amplitude)) if len(amplitude) > 0 else 0.0
            variance = float(np.nanvar(amplitude)) if len(amplitude) > 0 else 0.0

            # Advanced pattern analysis
            frame_size = min(1024, len(audio_array))
            hop_length = min(512, frame_size // 2)

            if frame_size <= 0 or hop_length <= 0:
                logger.error("Invalid frame parameters")
                return self._get_default_response()

            frames = [
                audio_array[i : i + frame_size]
                for i in range(0, len(audio_array) - frame_size, hop_length)
            ]

            if not frames:
                logger.warning("Audio data too short for analysis")
                return self._get_default_response()

            # Analyze rhythmic patterns
            frame_energies = []
            for frame in frames:
                energy = float(np.sum(np.abs(frame)))
                if not np.isnan(energy) and not np.isinf(energy):
                    frame_energies.append(energy)

            if not frame_energies:
                logger.error("No valid frame energies computed")
                return self._get_default_response()

            # Enhanced pattern detection
            rhythm_regularity = float(np.std(frame_energies)) if frame_energies else 0.0
            pattern_strength = self._detect_repetitive_patterns(frame_energies)

            # Analyze sound variations
            max_frame_values = [float(np.max(np.abs(frame))) for frame in frames]
            intensity_variations = (
                float(np.std(max_frame_values)) if max_frame_values else 0.0
            )

            # Enhanced emotional state analysis
            emotions = {
                "calm": max(
                    min(
                        (1 - min(variance, 1.0)) * 0.6
                        + (1 - min(intensity_variations, 1.0)) * 0.4,
                        1.0,
                    ),
                    0.0,
                ),
                "engaged": max(
                    min(mean_amplitude * 0.4 + pattern_strength * 0.6, 1.0), 0.0
                ),
                "uncertain": max(
                    min(intensity_variations * 0.5 + rhythm_regularity * 0.5, 1.0), 0.0
                ),
                "focused": max(
                    min((1 - rhythm_regularity) * 0.7 + pattern_strength * 0.3, 1.0),
                    0.0,
                ),
                "overwhelmed": max(
                    min(variance * 0.6 + intensity_variations * 0.4, 1.0), 0.0
                ),
            }

            # Enhanced communication pattern analysis
            communication_patterns = {
                "rhythm_consistency": max(min(1 - rhythm_regularity, 1.0), 0.0),
                "sound_complexity": max(min(variance * 1.5, 1.0), 0.0),
                "pattern_repetition": max(min(pattern_strength, 1.0), 0.0),
                "intensity_control": max(min(1 - intensity_variations, 1.0), 0.0),
                "engagement_level": max(
                    min(mean_amplitude + pattern_strength * 0.5, 1.0), 0.0
                ),
            }

            # Normalize emotions
            total = sum(emotions.values())
            if total > 0:
                emotions = {k: float(v / total) for k, v in emotions.items()}

            # Calculate enhanced confidence score
            confidence = max(
                min(
                    mean_amplitude * 0.3
                    + pattern_strength * 0.3
                    + (1 - min(rhythm_regularity, 1.0)) * 0.4,
                    1.0,
                ),
                0.0,
            )

            logger.debug(
                f"Enhanced analysis complete: emotions={emotions}, "
                f"patterns={communication_patterns}, confidence={confidence}"
            )
            return emotions, communication_patterns, confidence

        except Exception as e:
            logger.error(f"Error analyzing audio patterns: {str(e)}", exc_info=True)
            return self._get_default_response()

    def _detect_repetitive_patterns(self, frame_energies: list) -> float:
        """Enhanced detection of repetitive patterns that might indicate self-
        stimulating behavior or communication attempts."""
        if len(frame_energies) < 2:
            return 0.0

        try:
            # Calculate frame differences
            diffs = np.diff(frame_energies)

            if len(diffs) == 0:
                return 0.0

            # Enhanced pattern detection
            mean_abs_diff = np.mean(np.abs(diffs))
            if mean_abs_diff == 0:
                return 0.0

            # Calculate pattern strength with stability check
            pattern_strength = 1.0 - (np.std(diffs) / (mean_abs_diff + 1e-6))

            return float(max(min(pattern_strength, 1.0), 0.0))

        except Exception as e:
            logger.error(f"Error detecting repetitive patterns: {str(e)}")
            return 0.0

    def _get_default_response(self) -> Tuple[Dict[str, float], Dict[str, float], float]:
        """Returns balanced default values when analysis fails."""
        return (
            {
                "calm": 0.2,
                "engaged": 0.2,
                "uncertain": 0.2,
                "focused": 0.2,
                "overwhelmed": 0.2,
            },
            {
                "rhythm_consistency": 0.0,
                "sound_complexity": 0.0,
                "pattern_repetition": 0.0,
                "intensity_control": 0.0,
                "engagement_level": 0.0,
            },
            0.5,
        )
