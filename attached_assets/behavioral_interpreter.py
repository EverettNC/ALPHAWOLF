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
"""Behavioral Interpreter for AlphaVox.

This module provides advanced behavioral pattern recognition and
interpretation for AlphaVox, including contextual behavior analysis,
emotional state tracking, and prediction of user needs based on
behavioral patterns.
"""

import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BehavioralInterpreter:
    """Analyzes behavior patterns over time to detect trends, emotional states,
    and predictive indicators of user needs."""

    def __init__(self):
        """Initialize the behavioral interpreter."""
        self.behavior_history = []
        self.max_history_size = 100
        self.emotional_state = self._initialize_emotional_state()
        self.behavior_patterns = self._load_behavior_patterns()
        self.emotional_indicators = self._load_emotional_indicators()
        self.need_indicators = self._load_need_indicators()

        # Time windows for analysis (in minutes)
        self.time_windows = {
            "immediate": 5,
            "short_term": 60,
            "medium_term": 24 * 60,  # 1 day
            "long_term": 7 * 24 * 60,  # 1 week
        }

        # Initialize pattern detection engines
        self.pattern_detector = BehavioralPatternDetector()
        self.emotional_analyzer = EmotionalStateAnalyzer()
        self.need_predictor = NeedPredictor()

        logger.info("Behavioral interpreter initialized")

    def _initialize_emotional_state(self) -> Dict[str, float]:
        """Initialize the default emotional state tracking."""
        return {
            "valence": 0.0,  # Negative to positive (-1.0 to 1.0)
            "arousal": 0.5,  # Calm to excited (0.0 to 1.0)
            "dominance": 0.5,  # Submissive to dominant (0.0 to 1.0)
            "frustration": 0.0,  # Level of frustration (0.0 to 1.0)
            "satisfaction": 0.0,  # Level of satisfaction (0.0 to 1.0)
            "uncertainty": 0.5,  # Level of uncertainty (0.0 to 1.0)
            "attention": 0.5,  # Level of attention/focus (0.0 to 1.0)
        }

    def _load_behavior_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load behavior pattern definitions."""
        try:
            with open("data/behavior_patterns.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Default patterns
            return {
                "repetitive_requests": {
                    "description": "Repeated requests for the same information or action",
                    "indicators": ["same_intent", "frequent_requests"],
                    "interpretation": "Confusion or dissatisfaction with previous responses",
                    "confidence": 0.8,
                },
                "hesitation": {
                    "description": "Starting and stopping communication attempts",
                    "indicators": ["incomplete_inputs", "varied_intents"],
                    "interpretation": "Uncertainty or difficulty expressing needs",
                    "confidence": 0.7,
                },
                "escalation": {
                    "description": "Increasing intensity or urgency in communication",
                    "indicators": ["increasing_intensity", "urgent_gestures"],
                    "interpretation": "Growing frustration or critical need",
                    "confidence": 0.85,
                },
                "disengagement": {
                    "description": "Decreasing engagement and responsiveness",
                    "indicators": ["decreasing_interaction", "short_responses"],
                    "interpretation": "Losing interest or energy",
                    "confidence": 0.75,
                },
                "cyclical_needs": {
                    "description": "Regular pattern of specific needs",
                    "indicators": ["timed_requests", "predictable_needs"],
                    "interpretation": "Routine-based needs",
                    "confidence": 0.8,
                },
            }

    def _load_emotional_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Load emotional indicator definitions."""
        try:
            with open("data/emotional_indicators.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Default indicators
            return {
                "frustration": {
                    "behavioral_signs": ["repetitive_gestures", "increasing_intensity"],
                    "communication_signs": ["short_responses", "negative_tone"],
                    "threshold": 0.7,
                },
                "satisfaction": {
                    "behavioral_signs": ["positive_gestures", "sustained_engagement"],
                    "communication_signs": ["positive_tone", "elaborated_responses"],
                    "threshold": 0.7,
                },
                "anxiety": {
                    "behavioral_signs": [
                        "rapid_movements",
                        "stimming",
                        "rapid_blinking",
                    ],
                    "communication_signs": ["short_responses", "urgent_tone"],
                    "threshold": 0.7,
                },
                "calmness": {
                    "behavioral_signs": ["measured_movements", "steady_gaze"],
                    "communication_signs": ["measured_tone", "complete_responses"],
                    "threshold": 0.7,
                },
                "confusion": {
                    "behavioral_signs": ["head_tilting", "uncertain_gestures"],
                    "communication_signs": ["question_tone", "repeating_queries"],
                    "threshold": 0.7,
                },
            }

    def _load_need_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Load need indicator definitions."""
        try:
            with open("data/need_indicators.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Default indicators
            return {
                "physical_needs": {
                    "indicators": [
                        "requests_for_water",
                        "requests_for_food",
                        "requests_for_bathroom",
                        "requests_for_rest",
                    ],
                    "timing_patterns": ["regular_intervals", "morning_requests"],
                    "context_factors": ["activity_level", "time_since_last_meal"],
                    "urgency_indicators": ["increasing_intensity", "repetition"],
                },
                "emotional_needs": {
                    "indicators": [
                        "requests_for_comfort",
                        "expressions_of_distress",
                        "seeking_reassurance",
                        "seeking_connection",
                    ],
                    "timing_patterns": ["after_challenges", "before_transitions"],
                    "context_factors": ["social_environment", "recent_events"],
                    "urgency_indicators": ["emotional_displays", "withdrawal"],
                },
                "cognitive_needs": {
                    "indicators": [
                        "requests_for_information",
                        "seeking_stimulation",
                        "seeking_clarification",
                        "problem_solving_attempts",
                    ],
                    "timing_patterns": ["during_activities", "learning_periods"],
                    "context_factors": ["complexity_of_task", "familiarity"],
                    "urgency_indicators": ["repeated_questions", "signs_of_confusion"],
                },
                "social_needs": {
                    "indicators": [
                        "seeking_interaction",
                        "seeking_validation",
                        "sharing_experiences",
                        "turn_taking_behavior",
                    ],
                    "timing_patterns": ["during_group_activities", "after_isolation"],
                    "context_factors": ["social_setting", "relationship_quality"],
                    "urgency_indicators": [
                        "initiating_contact",
                        "prolonged_engagement",
                    ],
                },
                "sensory_needs": {
                    "indicators": [
                        "seeking_stimulation",
                        "avoiding_stimulation",
                        "regulating_behaviors",
                        "environment_adjustments",
                    ],
                    "timing_patterns": [
                        "during_overwhelming_situations",
                        "transitions",
                    ],
                    "context_factors": ["sensory_environment", "stress_level"],
                    "urgency_indicators": [
                        "self-regulation_behaviors",
                        "distress_signs",
                    ],
                },
            }

    def record_behavior(self, behavior_data: Dict[str, Any]):
        """Record a behavioral observation.

        Args:
            behavior_data: Observed behavior data
        """
        # Add timestamp if not present
        if "timestamp" not in behavior_data:
            behavior_data["timestamp"] = datetime.now().isoformat()

        # Add the behavior to history
        self.behavior_history.append(behavior_data)

        # Trim history if needed
        if len(self.behavior_history) > self.max_history_size:
            self.behavior_history = self.behavior_history[-self.max_history_size :]

        # Update emotional state based on behavior
        self._update_emotional_state(behavior_data)

        logger.debug(f"Recorded behavior: {behavior_data}")

    def _update_emotional_state(self, behavior_data: Dict[str, Any]):
        """Update emotional state based on observed behavior.

        Args:
            behavior_data: Observed behavior data
        """
        # Extract relevant data
        behavior_type = behavior_data.get("type", "unknown")
        intensity = behavior_data.get("intensity", 0.5)
        emotional_indicators = behavior_data.get("emotional_indicators", {})

        # Update valence (positive/negative)
        if "valence" in emotional_indicators:
            # Direct update if provided
            # Dampened impact
            valence_impact = emotional_indicators["valence"] * 0.2
            self.emotional_state["valence"] = max(
                -1.0, min(1.0, self.emotional_state["valence"] + valence_impact)
            )
        else:
            # Infer from behavior type
            valence_map = {
                "gesture:thumbs_up": 0.3,
                "gesture:thumbs_down": -0.3,
                "gesture:wave": 0.2,
                "gesture:nod": 0.1,
                "gesture:shake": -0.1,
                "gesture:stimming": -0.2,
                "gesture:rapid_blink": -0.2,
                "symbol:happy": 0.3,
                "symbol:sad": -0.3,
                "symbol:pain": -0.4,
                "symbol:tired": -0.2,
                "intent:greeting": 0.2,
                "intent:farewell": 0.1,
                "intent:affirmation": 0.2,
                "intent:denial": -0.1,
                "intent:complaint": -0.3,
                "intent:gratitude": 0.4,
            }

            valence_impact = valence_map.get(behavior_type, 0.0) * intensity * 0.2
            self.emotional_state["valence"] = max(
                -1.0, min(1.0, self.emotional_state["valence"] + valence_impact)
            )

        # Update arousal (calm/excited)
        if "arousal" in emotional_indicators:
            # Direct update if provided
            arousal_impact = (
                emotional_indicators["arousal"] - self.emotional_state["arousal"]
            ) * 0.2
            self.emotional_state["arousal"] = max(
                0.0, min(1.0, self.emotional_state["arousal"] + arousal_impact)
            )
        else:
            # Infer from behavior type and intensity
            arousal_map = {
                "gesture:thumbs_up": 0.2,
                "gesture:thumbs_down": 0.2,
                "gesture:wave": 0.2,
                "gesture:nod": 0.1,
                "gesture:shake": 0.1,
                "gesture:stimming": 0.4,
                "gesture:rapid_blink": 0.3,
                "symbol:happy": 0.2,
                "symbol:sad": 0.1,
                "symbol:pain": 0.4,
                "symbol:tired": -0.2,
                "intent:greeting": 0.2,
                "intent:farewell": 0.1,
                "intent:urgent_request": 0.5,
                "intent:complaint": 0.3,
                "intent:confusion": 0.2,
            }

            # Higher intensity behaviors increase arousal more
            base_arousal = arousal_map.get(behavior_type, 0.0)
            arousal_impact = base_arousal * intensity * 0.2

            # Apply decay over time - arousal naturally reduces
            time_decay = 0.01  # Small constant decay

            self.emotional_state["arousal"] = max(
                0.0,
                min(1.0, self.emotional_state["arousal"] + arousal_impact - time_decay),
            )

        # Update other emotional dimensions
        # Frustration
        if behavior_type in [
            "gesture:shake",
            "gesture:stimming",
            "symbol:pain",
            "intent:complaint",
        ]:
            self.emotional_state["frustration"] = min(
                1.0, self.emotional_state["frustration"] + 0.1 * intensity
            )
        else:
            # Frustration decreases slowly over time
            self.emotional_state["frustration"] = max(
                0.0, self.emotional_state["frustration"] - 0.02
            )

        # Satisfaction
        if behavior_type in ["gesture:thumbs_up", "symbol:happy", "intent:gratitude"]:
            self.emotional_state["satisfaction"] = min(
                1.0, self.emotional_state["satisfaction"] + 0.1 * intensity
            )
        else:
            # Satisfaction decreases slowly over time
            self.emotional_state["satisfaction"] = max(
                0.0, self.emotional_state["satisfaction"] - 0.01
            )

        # Uncertainty
        if behavior_type in [
            "gesture:tilt_head",
            "intent:confusion",
            "intent:request_clarification",
        ]:
            self.emotional_state["uncertainty"] = min(
                1.0, self.emotional_state["uncertainty"] + 0.1 * intensity
            )
        elif behavior_type in [
            "gesture:nod",
            "intent:affirmation",
            "intent:understanding",
        ]:
            self.emotional_state["uncertainty"] = max(
                0.0, self.emotional_state["uncertainty"] - 0.1 * intensity
            )

        # Attention
        if behavior_type in ["intent:focus", "eye_tracking:sustained_gaze"]:
            self.emotional_state["attention"] = min(
                1.0, self.emotional_state["attention"] + 0.1 * intensity
            )
        elif behavior_type in ["gesture:stimming", "eye_tracking:rapid_shifts"]:
            self.emotional_state["attention"] = max(
                0.0, self.emotional_state["attention"] - 0.1 * intensity
            )
        else:
            # Attention naturally wanes over time
            self.emotional_state["attention"] = max(
                0.3, self.emotional_state["attention"] - 0.01
            )

    def analyze_recent_behavior(self, time_window: str = "immediate") -> Dict[str, Any]:
        """Analyze behavior within a specified time window.

        Args:
            time_window: Time window for analysis ('immediate', 'short_term', 'medium_term', 'long_term')

        Returns:
            dict: Analysis results
        """
        # Determine time cutoff
        minutes = self.time_windows.get(time_window, 5)  # Default to immediate
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        # Filter behavior history by time
        recent_behaviors = []
        for behavior in self.behavior_history:
            try:
                behavior_time = datetime.fromisoformat(
                    behavior.get("timestamp", "2000-01-01T00:00:00")
                )
                if behavior_time >= cutoff_time:
                    recent_behaviors.append(behavior)
            except ValueError:
                # Skip entries with invalid timestamps
                continue

        if not recent_behaviors:
            return {
                "time_window": time_window,
                "pattern": "insufficient_data",
                "emotional_state": self.emotional_state,
                "confidence": 0.0,
            }

        # Detect behavioral patterns
        patterns = self.pattern_detector.detect_patterns(recent_behaviors)

        # Analyze emotional state
        emotional_analysis = self.emotional_analyzer.analyze(
            recent_behaviors, self.emotional_state
        )

        # Predict needs
        needs_prediction = self.need_predictor.predict(
            recent_behaviors, emotional_analysis
        )

        # Combine results
        analysis = {
            "time_window": time_window,
            "behavior_count": len(recent_behaviors),
            "patterns": patterns,
            "emotional_analysis": emotional_analysis,
            "needs_prediction": needs_prediction,
            "emotional_state": self.emotional_state,
            "confidence": min(
                0.95, 0.5 + len(recent_behaviors) / 20
            ),  # More data = higher confidence
        }

        logger.debug(
            f"Behavior analysis for {time_window} window: {len(recent_behaviors)} behaviors"
        )
        return analysis

    def get_behavior_trend(
        self, behavior_type: str, time_window: str = "medium_term"
    ) -> Dict[str, Any]:
        """Analyze the trend of a specific behavior over time.

        Args:
            behavior_type: Type of behavior to analyze
            time_window: Time window for analysis

        Returns:
            dict: Trend analysis
        """
        # Determine time cutoff
        minutes = self.time_windows.get(time_window, 60)  # Default to short-term
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        # Filter behavior history by type and time
        matching_behaviors = []
        for behavior in self.behavior_history:
            try:
                behavior_time = datetime.fromisoformat(
                    behavior.get("timestamp", "2000-01-01T00:00:00")
                )
                if (
                    behavior_time >= cutoff_time
                    and behavior.get("type", "") == behavior_type
                ):
                    matching_behaviors.append(behavior)
            except ValueError:
                # Skip entries with invalid timestamps
                continue

        if not matching_behaviors:
            return {
                "behavior_type": behavior_type,
                "time_window": time_window,
                "trend": "insufficient_data",
                "confidence": 0.0,
            }

        # Sort by timestamp
        matching_behaviors.sort(key=lambda x: x.get("timestamp", ""))

        # Divide into time segments for trend analysis
        segments = min(5, len(matching_behaviors))
        segment_size = max(1, len(matching_behaviors) // segments)
        intensity_segments = []

        for i in range(segments):
            start_idx = i * segment_size
            end_idx = min(len(matching_behaviors), (i + 1) * segment_size)
            segment_behaviors = matching_behaviors[start_idx:end_idx]

            # Calculate average intensity for this segment
            intensities = [b.get("intensity", 0.5) for b in segment_behaviors]
            avg_intensity = sum(intensities) / len(intensities) if intensities else 0.5

            segment_time = (
                segment_behaviors[-1].get("timestamp", "") if segment_behaviors else ""
            )
            intensity_segments.append(
                {
                    "segment": i,
                    "avg_intensity": avg_intensity,
                    "count": len(segment_behaviors),
                    "timestamp": segment_time,
                }
            )

        # Determine trend direction
        if len(intensity_segments) >= 2:
            first_intensity = intensity_segments[0]["avg_intensity"]
            last_intensity = intensity_segments[-1]["avg_intensity"]

            if last_intensity > first_intensity * 1.2:
                trend = "increasing"
            elif last_intensity < first_intensity * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        # Calculate trend metrics
        if len(intensity_segments) >= 2:
            intensities = [segment["avg_intensity"] for segment in intensity_segments]
            avg_intensity = sum(intensities) / len(intensities)
            min_intensity = min(intensities)
            max_intensity = max(intensities)
            range_intensity = max_intensity - min_intensity

            # Measure variability
            variance = sum((i - avg_intensity) ** 2 for i in intensities) / len(
                intensities
            )
            variability = variance**0.5  # Standard deviation
        else:
            avg_intensity = (
                intensity_segments[0]["avg_intensity"] if intensity_segments else 0.5
            )
            min_intensity = avg_intensity
            max_intensity = avg_intensity
            range_intensity = 0.0
            variability = 0.0

        return {
            "behavior_type": behavior_type,
            "time_window": time_window,
            "trend": trend,
            "segments": intensity_segments,
            "metrics": {
                "count": len(matching_behaviors),
                "avg_intensity": avg_intensity,
                "min_intensity": min_intensity,
                "max_intensity": max_intensity,
                "range": range_intensity,
                "variability": variability,
            },
            "confidence": min(0.9, 0.4 + len(matching_behaviors) / 10),
        }

    def predict_behavior(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict likely behaviors based on context and history.

        Args:
            context: Current context information

        Returns:
            dict: Behavior predictions
        """
        # Extract context features
        time_of_day = context.get("time_of_day")
        day_of_week = context.get("day_of_week")
        location = context.get("location")
        activity = context.get("activity")

        # Find similar contexts in history
        similar_contexts = []
        context_match_scores = []

        for behavior in self.behavior_history:
            behavior_context = behavior.get("context", {})
            match_score = 0.0

            # Compare context features if available
            if time_of_day and behavior_context.get("time_of_day") == time_of_day:
                match_score += 0.3

            if day_of_week and behavior_context.get("day_of_week") == day_of_week:
                match_score += 0.2

            if location and behavior_context.get("location") == location:
                match_score += 0.3

            if activity and behavior_context.get("activity") == activity:
                match_score += 0.2

            if match_score > 0.3:  # Threshold for considering it similar
                similar_contexts.append(behavior)
                context_match_scores.append(match_score)

        if not similar_contexts:
            return {
                "prediction": "insufficient_context_data",
                "confidence": 0.0,
                "context": context,
            }

        # Weight behaviors by context similarity
        behavior_counts = {}
        total_weight = sum(context_match_scores)

        for behavior, weight in zip(similar_contexts, context_match_scores):
            behavior_type = behavior.get("type", "unknown")
            normalized_weight = weight / total_weight

            if behavior_type not in behavior_counts:
                behavior_counts[behavior_type] = 0.0

            behavior_counts[behavior_type] += normalized_weight

        # Sort behaviors by weighted frequency
        sorted_behaviors = sorted(
            behavior_counts.items(), key=lambda x: x[1], reverse=True
        )

        # Prepare prediction
        likely_behaviors = []
        # Top 3 behaviors
        for behavior_type, probability in sorted_behaviors[:3]:
            # Gather typical intensities for this behavior
            intensities = [
                b.get("intensity", 0.5)
                for b in similar_contexts
                if b.get("type", "") == behavior_type
            ]
            avg_intensity = sum(intensities) / len(intensities) if intensities else 0.5

            likely_behaviors.append(
                {
                    "behavior_type": behavior_type,
                    "probability": min(
                        0.95, probability * 1.5
                    ),  # Scale up but cap at 0.95
                    "expected_intensity": avg_intensity,
                }
            )

        return {
            "prediction": "context_based",
            "likely_behaviors": likely_behaviors,
            "context": context,
            "confidence": min(0.9, 0.3 + len(similar_contexts) / 20),
            "similar_context_count": len(similar_contexts),
        }

    def get_emotional_state(self) -> Dict[str, float]:
        """Get the current emotional state.

        Returns:
            dict: Emotional state components
        """
        return self.emotional_state

    def reset_history(self):
        """Reset behavior history."""
        self.behavior_history = []
        self.emotional_state = self._initialize_emotional_state()
        logger.info("Behavior history and emotional state reset")


class BehavioralPatternDetector:
    """Detects patterns in behavioral data."""

    def detect_patterns(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect patterns in a list of behaviors.

        Args:
            behaviors: List of behavior observations

        Returns:
            list: Detected patterns with confidence
        """
        if len(behaviors) < 2:
            return []

        detected_patterns = []

        # Check for repetitive behaviors
        repetitive_patterns = self._detect_repetitive_behaviors(behaviors)
        if repetitive_patterns:
            detected_patterns.extend(repetitive_patterns)

        # Check for escalation/de-escalation
        intensity_patterns = self._detect_intensity_patterns(behaviors)
        if intensity_patterns:
            detected_patterns.extend(intensity_patterns)

        # Check for switching patterns
        switching_patterns = self._detect_switching_patterns(behaviors)
        if switching_patterns:
            detected_patterns.extend(switching_patterns)

        # Sort by confidence
        detected_patterns.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)

        return detected_patterns

    def _detect_repetitive_behaviors(
        self, behaviors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect repetitive behavior patterns."""
        behavior_types = [b.get("type", "unknown") for b in behaviors]

        # Count occurrences of each behavior type
        type_counts = {}
        for behavior_type in behavior_types:
            if behavior_type not in type_counts:
                type_counts[behavior_type] = 0
            type_counts[behavior_type] += 1

        # Identify repetitive behaviors
        repetitive_patterns = []
        for behavior_type, count in type_counts.items():
            repetition_ratio = count / len(behaviors)

            if repetition_ratio >= 0.7 and count >= 3:  # At least 70% and 3 occurrences
                # Calculate average intensity
                intensities = [
                    b.get("intensity", 0.5)
                    for b in behaviors
                    if b.get("type", "") == behavior_type
                ]
                avg_intensity = sum(intensities) / len(intensities)

                repetitive_patterns.append(
                    {
                        "pattern": "repetitive_behavior",
                        "behavior_type": behavior_type,
                        "count": count,
                        "ratio": repetition_ratio,
                        "avg_intensity": avg_intensity,
                        "confidence": min(0.95, 0.6 + repetition_ratio * 0.3),
                    }
                )

        return repetitive_patterns

    def _detect_intensity_patterns(
        self, behaviors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect patterns in behavior intensity."""
        if len(behaviors) < 3:
            return []

        # Sort behaviors by timestamp
        try:
            sorted_behaviors = sorted(behaviors, key=lambda x: x.get("timestamp", ""))
        except:
            # Fall back to original order if timestamps are not valid
            sorted_behaviors = behaviors

        # Extract intensities
        intensities = [b.get("intensity", 0.5) for b in sorted_behaviors]

        # Calculate trend using linear regression approach
        n = len(intensities)
        indices = list(range(n))
        sum_x = sum(indices)
        sum_y = sum(intensities)
        sum_xy = sum(i * y for i, y in zip(indices, intensities))
        sum_xx = sum(i * i for i in indices)

        # Calculate slope
        slope = (
            (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            if (n * sum_xx - sum_x * sum_x) != 0
            else 0
        )

        # Determine pattern based on slope
        intensity_patterns = []

        if slope > 0.05:  # Significant increase
            intensity_patterns.append(
                {
                    "pattern": "escalating_intensity",
                    "slope": slope,
                    "start_intensity": intensities[0],
                    "end_intensity": intensities[-1],
                    "confidence": min(0.9, 0.6 + abs(slope) * 3),
                }
            )
        elif slope < -0.05:  # Significant decrease
            intensity_patterns.append(
                {
                    "pattern": "decreasing_intensity",
                    "slope": slope,
                    "start_intensity": intensities[0],
                    "end_intensity": intensities[-1],
                    "confidence": min(0.9, 0.6 + abs(slope) * 3),
                }
            )

        return intensity_patterns

    def _detect_switching_patterns(
        self, behaviors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect patterns of switching between different behaviors."""
        if len(behaviors) < 4:
            return []

        # Sort behaviors by timestamp
        try:
            sorted_behaviors = sorted(behaviors, key=lambda x: x.get("timestamp", ""))
        except:
            # Fall back to original order if timestamps are not valid
            sorted_behaviors = behaviors

        # Extract behavior types
        behavior_types = [b.get("type", "unknown") for b in sorted_behaviors]

        # Count transitions between different types
        transitions = {}
        for i in range(len(behavior_types) - 1):
            current_type = behavior_types[i]
            next_type = behavior_types[i + 1]

            if current_type != next_type:
                transition = (current_type, next_type)
                if transition not in transitions:
                    transitions[transition] = 0
                transitions[transition] += 1

        # Check for rapid switching
        unique_types = set(behavior_types)
        switch_ratio = (
            len(transitions) / (len(behavior_types) - 1)
            if len(behavior_types) > 1
            else 0
        )

        switching_patterns = []

        if switch_ratio > 0.7 and len(unique_types) >= 3:
            # High rate of switching between different behaviors
            switching_patterns.append(
                {
                    "pattern": "rapid_behavioral_switching",
                    "unique_behaviors": len(unique_types),
                    "switch_ratio": switch_ratio,
                    "confidence": min(0.85, 0.5 + switch_ratio * 0.4),
                }
            )

        # Check for alternating pattern between two types
        if len(unique_types) == 2 and switch_ratio > 0.7:
            switching_patterns.append(
                {
                    "pattern": "alternating_behaviors",
                    "behaviors": list(unique_types),
                    "switch_ratio": switch_ratio,
                    "confidence": min(0.9, 0.6 + switch_ratio * 0.3),
                }
            )

        return switching_patterns


class EmotionalStateAnalyzer:
    """Analyzes emotional state based on behavioral patterns."""

    def analyze(
        self, behaviors: List[Dict[str, Any]], current_state: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze emotional state from behaviors.

        Args:
            behaviors: List of behavior observations
            current_state: Current emotional state

        Returns:
            dict: Emotional analysis results
        """
        if not behaviors:
            return {
                "primary_emotion": "neutral",
                "confidence": 0.0,
                "emotional_indicators": {},
            }

        # Extract emotional indicators from behaviors
        emotion_indicators = {}

        for behavior in behaviors:
            # Get direct emotional indicators if available
            behavior_indicators = behavior.get("emotional_indicators", {})
            for emotion, value in behavior_indicators.items():
                if emotion not in emotion_indicators:
                    emotion_indicators[emotion] = []
                emotion_indicators[emotion].append(value)

            # Infer from behavior type
            behavior_type = behavior.get("type", "unknown")
            intensity = behavior.get("intensity", 0.5)

            emotion_map = {
                "gesture:thumbs_up": {"happiness": 0.7, "satisfaction": 0.8},
                "gesture:thumbs_down": {"dissatisfaction": 0.7, "frustration": 0.6},
                "gesture:wave": {"friendliness": 0.7},
                "gesture:nod": {"agreement": 0.8, "understanding": 0.7},
                "gesture:shake": {"disagreement": 0.8, "frustration": 0.5},
                "gesture:stimming": {"anxiety": 0.7, "overwhelm": 0.6},
                "gesture:rapid_blink": {"anxiety": 0.8, "stress": 0.7},
                "symbol:happy": {"happiness": 0.9},
                "symbol:sad": {"sadness": 0.9},
                "symbol:pain": {"discomfort": 0.9, "distress": 0.8},
                "symbol:tired": {"fatigue": 0.8},
                "intent:greeting": {"friendliness": 0.7},
                "intent:farewell": {"closure": 0.7},
                "intent:affirmation": {"agreement": 0.8},
                "intent:denial": {"disagreement": 0.8},
                "intent:complaint": {"frustration": 0.8, "dissatisfaction": 0.7},
                "intent:gratitude": {"appreciation": 0.9, "happiness": 0.7},
            }

            if behavior_type in emotion_map:
                for emotion, base_value in emotion_map[behavior_type].items():
                    value = base_value * intensity  # Scale by intensity
                    if emotion not in emotion_indicators:
                        emotion_indicators[emotion] = []
                    emotion_indicators[emotion].append(value)

        # Calculate average value for each emotion
        avg_indicators = {}
        for emotion, values in emotion_indicators.items():
            avg_indicators[emotion] = sum(values) / len(values)

        # Find primary emotion
        primary_emotion = "neutral"
        primary_value = 0.0

        for emotion, value in avg_indicators.items():
            if value > primary_value:
                primary_value = value
                primary_emotion = emotion

        # Map to valence-arousal space
        emotion_va_map = {
            "happiness": (0.8, 0.6),
            "satisfaction": (0.7, 0.3),
            "dissatisfaction": (-0.6, 0.4),
            "frustration": (-0.7, 0.8),
            "friendliness": (0.6, 0.5),
            "agreement": (0.5, 0.3),
            "understanding": (0.4, 0.2),
            "disagreement": (-0.5, 0.4),
            "anxiety": (-0.6, 0.9),
            "overwhelm": (-0.7, 0.9),
            "stress": (-0.6, 0.8),
            "sadness": (-0.7, 0.3),
            "discomfort": (-0.6, 0.6),
            "distress": (-0.8, 0.8),
            "fatigue": (-0.3, 0.1),
            "closure": (0.1, 0.2),
            "appreciation": (0.8, 0.5),
            "neutral": (0.0, 0.3),
        }

        # Get VA coordinates for primary emotion
        valence, arousal = emotion_va_map.get(primary_emotion, (0.0, 0.3))

        # Calculate confidence based on emotion strength and behavior count
        confidence = primary_value * min(1.0, len(behaviors) / 5)

        return {
            "primary_emotion": primary_emotion,
            "valence": valence,
            "arousal": arousal,
            "confidence": confidence,
            "emotional_indicators": avg_indicators,
        }


class NeedPredictor:
    """Predicts user needs based on behavioral patterns and emotional state."""

    def predict(
        self, behaviors: List[Dict[str, Any]], emotional_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict user needs based on behaviors and emotional state.

        Args:
            behaviors: List of behavior observations
            emotional_analysis: Emotional state analysis

        Returns:
            dict: Need prediction results
        """
        if not behaviors:
            return {"primary_need": "unknown", "confidence": 0.0, "need_indicators": {}}

        # Extract behavior types
        behavior_types = [b.get("type", "unknown") for b in behaviors]

        # Map behaviors to need indicators
        need_indicators = {
            "physical": 0.0,
            "emotional": 0.0,
            "cognitive": 0.0,
            "social": 0.0,
            "sensory": 0.0,
        }

        # Behavior to need mapping
        need_map = {
            "symbol:food": {"physical": 0.9},
            "symbol:drink": {"physical": 0.9},
            "symbol:bathroom": {"physical": 0.9},
            "symbol:tired": {"physical": 0.8},
            "symbol:pain": {"physical": 0.8},
            "symbol:happy": {"emotional": 0.7},
            "symbol:sad": {"emotional": 0.8},
            "gesture:stimming": {"sensory": 0.8, "emotional": 0.6},
            "gesture:rapid_blink": {"sensory": 0.7, "emotional": 0.7},
            "intent:request_info": {"cognitive": 0.8},
            "intent:confusion": {"cognitive": 0.8},
            "intent:greeting": {"social": 0.7},
            "intent:farewell": {"social": 0.5},
            "intent:gratitude": {"social": 0.6, "emotional": 0.5},
            "intent:complaint": {"emotional": 0.7},
        }

        # Count need indicators from behaviors
        for behavior_type in behavior_types:
            if behavior_type in need_map:
                for need, value in need_map[behavior_type].items():
                    need_indicators[need] += value

        # Factor in emotional state
        primary_emotion = emotional_analysis.get("primary_emotion", "neutral")
        emotion_confidence = emotional_analysis.get("confidence", 0.0)

        # Emotion to need mapping
        emotion_need_map = {
            "happiness": {"emotional": 0.2, "social": 0.3},
            "satisfaction": {"emotional": 0.3},
            "dissatisfaction": {"emotional": 0.4},
            "frustration": {"emotional": 0.5, "cognitive": 0.3},
            "anxiety": {"emotional": 0.6, "sensory": 0.4},
            "overwhelm": {"sensory": 0.7, "emotional": 0.5},
            "stress": {"emotional": 0.6, "physical": 0.3},
            "sadness": {"emotional": 0.7, "social": 0.4},
            "discomfort": {"physical": 0.5, "sensory": 0.4},
            "distress": {"emotional": 0.6, "physical": 0.4},
            "fatigue": {"physical": 0.8},
        }

        # Add emotional state influence
        if primary_emotion in emotion_need_map:
            for need, value in emotion_need_map[primary_emotion].items():
                need_indicators[need] += value * emotion_confidence

        # Normalize need indicators
        behavior_count = len(behaviors)
        for need in need_indicators:
            need_indicators[need] = min(
                1.0, need_indicators[need] / (behavior_count * 0.5)
            )

        # Find primary need
        primary_need = max(need_indicators.items(), key=lambda x: x[1])

        # Calculate confidence
        confidence = primary_need[1] * min(1.0, behavior_count / 5)

        # Sort need indicators by strength
        sorted_needs = sorted(need_indicators.items(), key=lambda x: x[1], reverse=True)

        return {
            "primary_need": primary_need[0],
            "confidence": confidence,
            "need_indicators": dict(sorted_needs),
        }


# Singleton instance
_behavioral_interpreter = None


def get_behavioral_interpreter():
    """Get or create the behavioral interpreter singleton."""
    global _behavioral_interpreter
    if _behavioral_interpreter is None:
        _behavioral_interpreter = BehavioralInterpreter()
    return _behavioral_interpreter
