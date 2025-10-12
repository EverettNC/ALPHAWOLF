"""Dynamic AI-powered conversation difficulty adjustment module for AlphaVox.

This module provides functionality to dynamically adjust the complexity
and sophistication of AI-generated responses based on user proficiency,
conversation context, and adaptability preferences.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
USER_PROFILES_PATH = "data/user_complexity_profiles.json"
# Ensure the data folder exists before loading or saving profiles
# (this creates /Users/EverettN/LumaCognify-AlphaVox/data if missing)
os.makedirs(os.path.dirname(USER_PROFILES_PATH), exist_ok=True)

COMPLEXITY_LEVELS = {
    1: {"name": "Simplified", "description": "Basic vocabulary and simple sentences"},
    2: {"name": "Easy", "description": "Simple vocabulary with occasional complexity"},
    3: {
        "name": "Moderate",
        "description": "Balanced vocabulary and sentence structures",
    },
    4: {
        "name": "Advanced",
        "description": "Complex vocabulary and varied sentence structures",
    },
    5: {
        "name": "Expert",
        "description": "Sophisticated vocabulary and complex sentence structures",
    },
}

ADAPTATION_MODES = {
    "fixed": "Maintain a consistent complexity level",
    "responsive": "Adjust based on recent user inputs",
    "progressive": "Gradually increase complexity over time",
    "adaptive": "Fully dynamic adjustment based on all factors",
}

# Module-level singleton instance renamed for clarity
_engine_instance: Optional["ConversationComplexityEngine"] = None


class ConversationComplexityEngine:
    """Engine to dynamically adjust conversation complexity based on user
    interactions, preferences, and contextual factors."""

    def __init__(self):
        """Initialize the conversation complexity engine."""
        self.user_profiles = self._load_user_profiles()
        self.default_complexity = 3  # Moderate level by default
        self.default_adaptation_mode = "adaptive"

        logger.info("Conversation Complexity Engine initialized")

    def _load_user_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load user complexity profiles from the JSON file."""
        try:
            if os.path.exists(USER_PROFILES_PATH):
                with open(USER_PROFILES_PATH, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading user profiles: {e}")
            return {}

    def _save_user_profiles(self):
        """Save user complexity profiles to the JSON file."""
        try:
            with open(USER_PROFILES_PATH, "w") as f:
                json.dump(self.user_profiles, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user profiles: {e}")

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get a user's complexity profile, creating a new one if needed."""
        if user_id not in self.user_profiles:
            # Create a new user profile with default settings
            self.user_profiles[user_id] = {
                "complexity_level": self.default_complexity,
                "adaptation_mode": self.default_adaptation_mode,
                "interaction_history": [],
                "topic_complexities": {},
                "last_update": datetime.now().isoformat(),
                "progression_factor": 0.1,  # How quickly to increase complexity in progressive mode
                "complexity_variance": 0.5,  # How much to vary complexity in adaptive mode
            }
            self._save_user_profiles()

        return self.user_profiles[user_id]

    def update_user_profile(self, user_id: str, profile_updates: Dict[str, Any]):
        """Update a user's complexity profile."""
        if user_id not in self.user_profiles:
            self.get_user_profile(user_id)

        # Update specified fields
        for key, value in profile_updates.items():
            if key in self.user_profiles[user_id]:
                self.user_profiles[user_id][key] = value

        # Update last update timestamp
        self.user_profiles[user_id]["last_update"] = datetime.now().isoformat()

        # Save profiles
        self._save_user_profiles()

        return self.user_profiles[user_id]

    def log_interaction(
        self,
        user_id: str,
        user_input: str,
        response: str,
        topic: Optional[str] = None,
        comprehension_feedback: Optional[float] = None,
    ):
        """Log a user interaction to inform future complexity adjustments.

        Args:
            user_id: User identifier
            user_input: Text input from the user
            response: System's response text
            topic: Optional topic category for the interaction
            comprehension_feedback: Optional feedback score (0-1) indicating user comprehension
        """
        profile = self.get_user_profile(user_id)

        # Calculate complexity metrics for this interaction
        input_complexity = self._calculate_text_complexity(user_input)
        response_complexity = self._calculate_text_complexity(response)

        # Create interaction record
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "input_complexity": input_complexity,
            "response": response,
            "response_complexity": response_complexity,
            "topic": topic,
            "comprehension_feedback": comprehension_feedback,
        }

        # Add to user's interaction history
        profile["interaction_history"].append(interaction)

        # Limit history size to prevent excessive growth
        if len(profile["interaction_history"]) > 100:
            profile["interaction_history"] = profile["interaction_history"][-100:]

        # Update topic-specific complexity if topic is provided
        if topic:
            if topic not in profile["topic_complexities"]:
                profile["topic_complexities"][topic] = self.default_complexity

            # Adjust topic complexity based on this interaction
            current = profile["topic_complexities"][topic]
            adjustment = 0

            # If user's input is complex, potentially increase complexity
            if input_complexity > current:
                adjustment += 0.1

            # If feedback is provided, adjust based on comprehension
            if comprehension_feedback is not None:
                # High comprehension (>0.7) suggests we can increase complexity
                if comprehension_feedback > 0.7:
                    adjustment += 0.1
                # Low comprehension (<0.3) suggests we should decrease complexity
                elif comprehension_feedback < 0.3:
                    adjustment -= 0.2

            # Apply adjustment with limits
            profile["topic_complexities"][topic] = max(1, min(5, current + adjustment))

        # Save updated profile
        self._save_user_profiles()

    def determine_response_complexity(
        self, user_id: str, context: Dict[str, Any] = {}
    ) -> float:
        """Determine the appropriate complexity level for a response.

        Args:
            user_id: User identifier
            context: Optional context with additional factors that may influence complexity
                     (e.g., topic, urgency, emotional state)

        Returns:
            A complexity level (float between 1-5)
        """
        profile = self.get_user_profile(user_id)
        base_complexity = profile["complexity_level"]
        adaptation_mode = profile["adaptation_mode"]

        # Handle different adaptation modes
        if adaptation_mode == "fixed":
            # Simply return the user's set complexity level
            return base_complexity

        elif adaptation_mode == "responsive":
            # Adjust based on recent user inputs
            recent_inputs = self._get_recent_input_complexity(profile, n=5)
            if recent_inputs:
                # Adjust toward the average of recent inputs, but don't change too drastically
                avg_recent = sum(recent_inputs) / len(recent_inputs)
                return (base_complexity * 0.7) + (avg_recent * 0.3)
            return base_complexity

        elif adaptation_mode == "progressive":
            # Gradually increase complexity over time
            progression_factor = profile.get("progression_factor", 0.1)
            interaction_count = len(profile["interaction_history"])

            # Simple progression formula: base + (log of interaction count * factor)
            import math

            if interaction_count > 0:
                log_factor = math.log(min(interaction_count, 100)) * progression_factor
                return min(5, base_complexity + log_factor)
            return base_complexity

        elif adaptation_mode == "adaptive":
            # The most dynamic mode, considers multiple factors
            adjustments = []

            # 1. Recent input complexity
            recent_inputs = self._get_recent_input_complexity(profile, n=5)
            if recent_inputs:
                avg_recent = sum(recent_inputs) / len(recent_inputs)
                adjustments.append(avg_recent)

            # 2. Topic-specific complexity if topic is provided
            topic = context.get("topic")
            if topic and topic in profile["topic_complexities"]:
                adjustments.append(profile["topic_complexities"][topic])

            # 3. Emotional state adjustment
            emotion = context.get("emotion")
            if emotion:
                # Simplify language when emotional state indicates stress/urgency
                if emotion in ["stressed", "anxious", "urgent"]:
                    adjustments.append(max(1, base_complexity - 1))
                # Maintain or increase complexity for positive/calm emotions
                elif emotion in ["calm", "happy", "curious"]:
                    adjustments.append(min(5, base_complexity + 0.5))

            # 4. Time of day (simplified reasoning ability in evening/night)
            time_context = context.get("time_of_day")
            if time_context == "evening" or time_context == "night":
                adjustments.append(max(1, base_complexity - 0.5))

            # Combine adjustments with the base complexity
            if adjustments:
                # Weight base complexity more heavily (60%) than other factors
                weighted_complexity = (base_complexity * 0.6) + (
                    sum(adjustments) / len(adjustments) * 0.4
                )

                # Add some variability to prevent monotony, controlled by complexity_variance
                import random

                variance = profile.get("complexity_variance", 0.5)
                random_adjustment = random.uniform(-variance, variance)

                # Final complexity with limits
                return max(1, min(5, weighted_complexity + random_adjustment))

            return base_complexity

        # Default case
        return base_complexity

    def _get_recent_input_complexity(
        self, profile: Dict[str, Any], n: int = 5
    ) -> List[float]:
        """Get complexity levels of the n most recent user inputs."""
        history = profile["interaction_history"]
        # Sort by timestamp (most recent first) and take n most recent
        sorted_history = sorted(history, key=lambda x: x["timestamp"], reverse=True)[:n]
        return [entry["input_complexity"] for entry in sorted_history]

    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate the complexity level of a text.

        Returns a value between 1-5 representing complexity.
        """
        if not text:
            return 1.0

        # Metrics to consider:
        # 1. Vocabulary complexity (average word length)
        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return 1.0

        avg_word_length = sum(len(word) for word in words) / len(words)

        # 2. Sentence complexity (average sentence length)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 1.0

        avg_sentence_length = len(words) / len(sentences)

        # 3. Lexical diversity (ratio of unique words to total words)
        unique_words = set(words)
        lexical_diversity = len(unique_words) / len(words)

        # Convert metrics to complexity score (1-5 scale)

        # Word length: typically 4-8 characters
        word_complexity = min(5, max(1, (avg_word_length - 3) * 1.25))

        # Sentence length: typically 5-25 words
        sentence_complexity = min(5, max(1, (avg_sentence_length - 5) / 5))

        # Lexical diversity: typically 0.3-0.7
        diversity_complexity = min(5, max(1, lexical_diversity * 10 - 2))

        # Combine metrics with different weights
        complexity_score = (
            word_complexity * 0.3
            + sentence_complexity * 0.4
            + diversity_complexity * 0.3
        )

        return complexity_score

    def simplify_text(self, text: str, target_complexity: float) -> str:
        """Simplify a text to match the target complexity level.

        This is a basic implementation focused on sentence length and
        structure. A more sophisticated implementation might use NLP
        techniques for vocabulary simplification and syntactic
        restructuring.
        """
        # For very low complexity (levels 1-2), break into shorter sentences
        if target_complexity <= 2:
            # Split long sentences
            sentences = re.split(r"(?<=[.!?])\s+", text)
            simplified_sentences = []

            for sentence in sentences:
                # If sentence is long, break it up
                words = sentence.split()
                if len(words) > 10:
                    # Find conjunctions or commas to break at
                    breaks = [
                        i
                        for i, word in enumerate(words)
                        if word.lower() in ["and", "but", "or", "however", "therefore"]
                        or word.endswith(",")
                    ]

                    if breaks:
                        # Split sentence at appropriate points
                        current_segment = []
                        prev_break = 0

                        for break_point in breaks:
                            if break_point - prev_break >= 5:  # Avoid tiny fragments
                                segment = " ".join(words[prev_break : break_point + 1])
                                # Ensure proper capitalization and punctuation
                                if not segment.endswith((".", "!", "?")):
                                    segment += "."
                                simplified_sentences.append(segment)
                                prev_break = break_point + 1

                        # Add any remaining words
                        if prev_break < len(words):
                            segment = " ".join(words[prev_break:])
                            if not segment.endswith((".", "!", "?")):
                                segment += "."
                            simplified_sentences.append(segment)
                    else:
                        # No good break points, just include the original
                        simplified_sentences.append(sentence)
                else:
                    # Short enough to keep as is
                    simplified_sentences.append(sentence)

            simplified_text = " ".join(simplified_sentences)

            # For the simplest level, also replace uncommon words with simpler alternatives
            if target_complexity <= 1.5:
                # This is a very simplified approach - in a real system, you'd use
                # a more comprehensive dictionary of word simplifications
                simplifications = {
                    "utilize": "use",
                    "implement": "use",
                    "facilitate": "help",
                    "moreover": "also",
                    "nevertheless": "still",
                    "consequently": "so",
                    "therefore": "so",
                    "approximately": "about",
                    "initiate": "start",
                    "terminate": "end",
                    "comprehend": "understand",
                    "endeavor": "try",
                    "sufficient": "enough",
                    "commence": "begin",
                    "additional": "more",
                    "demonstrate": "show",
                    "require": "need",
                    "encounter": "meet",
                    "obtain": "get",
                    "perceive": "see",
                    "inquire": "ask",
                    "ascertain": "find out",
                    "construct": "build",
                }

                # Apply simplifications
                for complex_word, simple_word in simplifications.items():
                    simplified_text = re.sub(
                        r"\b" + complex_word + r"\b",
                        simple_word,
                        simplified_text,
                        flags=re.IGNORECASE,
                    )

            return simplified_text

        # For moderate complexity (3), the text is returned mostly as is
        elif target_complexity <= 3:
            return text

        # For higher complexity (4-5), we would enhance vocabulary and structure
        # This is a placeholder - in a real system, you would use more sophisticated NLP
        else:
            return text  # No enhancement in this simple implementation

    def get_complexity_level_info(self, level: int) -> Dict[str, str]:
        """Get information about a specific complexity level."""
        return COMPLEXITY_LEVELS.get(
            level, {"name": "Unknown", "description": "Unknown level"}
        )

    def get_adaptation_mode_info(self, mode: str) -> str:
        """Get description of an adaptation mode."""
        return ADAPTATION_MODES.get(mode, "Unknown adaptation mode")


def get_complexity_engine() -> ConversationComplexityEngine:
    """Get or create the conversation complexity engine singleton."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ConversationComplexityEngine()
    return _engine_instance
