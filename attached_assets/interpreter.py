"""AlphaVox Integrated Interpreter.

This module serves as the central coordinator for the AlphaVox system,
integrating input analysis, behavioral interpretation, conversation
processing, and multimodal fusion to create a comprehensive
understanding of user needs.

The Interpreter coordinates data flow between specialized engines and
performs high-level integration of multimodal inputs to determine the
most appropriate system response.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Interpreter:
    """Central interpreter that coordinates between various specialized engines
    and modules to create a unified understanding of user inputs across
    multiple modalities."""

    def __init__(self):
        """Initialize the interpreter and its component engines."""
        # Import component engines
        try:
            from conversation_engine import get_conversation_engine

            # Import nonverbal engine with error handling to avoid circular imports
            try:
                from nonverbal_engine import get_nonverbal_engine

                nonverbal_engine_import_success = True
            except ImportError:
                logger.warning(
                    "Could not import nonverbal_engine directly, will try alternate approach"
                )
                nonverbal_engine_import_success = False

            from behavioral_interpreter import get_behavioral_interpreter
            from input_analyzer import get_input_analyzer

            # Initialize component engines
            if nonverbal_engine_import_success:
                self.nonverbal_engine = get_nonverbal_engine()
            else:
                # Alternative approach: import the class and create instance directly
                from app import nonverbal_engine

                if nonverbal_engine is None:
                    from nonverbal_engine import NonverbalEngine

                    self.nonverbal_engine = NonverbalEngine()
                else:
                    self.nonverbal_engine = nonverbal_engine

            self.conversation_engine = get_conversation_engine(self.nonverbal_engine)
            self.input_analyzer = get_input_analyzer()
            self.behavioral_interpreter = get_behavioral_interpreter()

            # Set up coordination flags
            self.engines_initialized = True
        except ImportError as e:
            logger.error(f"Failed to import required engines: {str(e)}")
            self.engines_initialized = False
        except Exception as e:
            logger.error(f"Error initializing interpreter: {str(e)}")
            self.engines_initialized = False

        # Configure interpreter settings
        self.confidence_threshold = (
            0.6  # Minimum confidence to accept an interpretation
        )
        self.context_window_size = (
            5  # Number of recent interactions to consider for context
        )
        self.multimodal_fusion_strategy = (
            "weighted"  # How to combine multiple modalities
        )

        # Track recent interactions
        self.interaction_history = []
        self.max_history_size = 20

        # Context tracking
        self.current_context = {
            "time_of_day": None,
            "location": None,
            "activity": None,
            "previous_intents": [],
            "conversation_state": "beginning",
            "emotional_state": None,
        }

        # Performance metrics
        self.performance_metrics = {
            "successful_interpretations": 0,
            "failed_interpretations": 0,
            "average_confidence": 0.0,
            "processing_times": [],
        }

        logger.info("Interpreter initialized")

    def process_multimodal_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process multimodal input combining text, gestures, eye tracking,
        etc.

        Args:
            input_data: Input data containing one or more modalities
                {
                    'text': Optional text input,
                    'gesture': Optional gesture name,
                    'eye_data': Optional eye tracking data,
                    'voice_data': Optional voice input data,
                    'context': Optional context information
                }

        Returns:
            dict: Comprehensive interpretation result
        """
        if not self.engines_initialized:
            return {
                "status": "error",
                "message": "Interpreter engines not properly initialized",
                "confidence": 0.0,
            }

        start_time = time.time()

        # Extract input components
        text = input_data.get("text")
        gesture = input_data.get("gesture")
        symbol = input_data.get("symbol")  # Added symbol support
        eye_data = input_data.get("eye_data")
        voice_data = input_data.get("voice_data")
        user_id = input_data.get("user_id")

        # Update context if provided
        if "context" in input_data:
            self.update_context(input_data["context"])

        # Update time context
        current_time = datetime.now()
        hour = current_time.hour

        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

        self.current_context["time_of_day"] = time_of_day
        self.current_context["timestamp"] = current_time.isoformat()

        # Convert symbol to gesture if symbol is provided but gesture is not
        if symbol and not gesture:
            logger.debug(f"Converting symbol '{symbol}' to gesture")
            gesture = symbol

        # Processing flags
        has_verbal_input = text is not None and text.strip() != ""
        has_nonverbal_input = (
            gesture is not None or eye_data is not None or voice_data is not None
        )

        # Results from different processing pathways
        results = {}

        # 1. Process text input if available
        if has_verbal_input:
            results["text"] = self.conversation_engine.process_text(
                text, user_id, self.current_context
            )

        # 2. Process nonverbal input if available
        if has_nonverbal_input:
            # 2.1 Process through nonverbal engine
            if gesture:
                results["gesture"] = self.nonverbal_engine.classify_gesture(gesture)

            if eye_data:
                results["eye"] = self.nonverbal_engine.process_eye_movement(eye_data)

            if voice_data:
                results["voice"] = self.nonverbal_engine.process_sound(voice_data)

            # 2.2 Process through advanced input analyzer
            nonverbal_analysis = self.input_analyzer.analyze_multimodal(
                gesture=gesture, eye_data=eye_data, audio_data=voice_data
            )
            results["nonverbal_analysis"] = nonverbal_analysis

        # 3. Integrate results based on fusion strategy
        integrated_result = self._fuse_results(results)

        # 4. Update behavioral interpreter
        behavior_data = {
            "type": self._determine_behavior_type(input_data),
            "intensity": integrated_result.get("confidence", 0.5),
            "timestamp": datetime.now().isoformat(),
            "context": self.current_context.copy(),
            "result": integrated_result,
            "emotional_indicators": integrated_result.get("emotional_indicators", {}),
        }

        self.behavioral_interpreter.record_behavior(behavior_data)

        # 5. Add behavioral analysis
        behavioral_analysis = self.behavioral_interpreter.analyze_recent_behavior()
        integrated_result["behavioral_analysis"] = behavioral_analysis

        # 6. Update emotional state context
        self.current_context["emotional_state"] = behavioral_analysis.get(
            "emotional_state"
        )

        # 7. Add to interaction history
        self.interaction_history.append(
            {
                "input": input_data,
                "result": integrated_result,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Trim history if needed
        if len(self.interaction_history) > self.max_history_size:
            self.interaction_history = self.interaction_history[
                -self.max_history_size :
            ]

        # Record performance metrics
        processing_time = time.time() - start_time
        self.performance_metrics["processing_times"].append(processing_time)

        if integrated_result.get("confidence", 0.0) >= self.confidence_threshold:
            self.performance_metrics["successful_interpretations"] += 1
        else:
            self.performance_metrics["failed_interpretations"] += 1

        # Update average confidence
        total_interpretations = (
            self.performance_metrics["successful_interpretations"]
            + self.performance_metrics["failed_interpretations"]
        )

        self.performance_metrics["average_confidence"] = (
            self.performance_metrics["average_confidence"] * (total_interpretations - 1)
            + integrated_result.get("confidence", 0.0)
        ) / total_interpretations

        # Add processing metadata
        integrated_result["processing_time"] = processing_time
        integrated_result["timestamp"] = current_time.isoformat()

        logger.info(
            f"Processed multimodal input in {processing_time:.3f}s "
            f"with confidence {integrated_result.get('confidence', 0.0):.2f}"
        )

        return integrated_result

    def _determine_behavior_type(self, input_data: Dict[str, Any]) -> str:
        """Determine the behavior type from input data."""
        if "text" in input_data and input_data["text"]:
            return f"text:input"
        elif "symbol" in input_data and input_data["symbol"]:
            return f"symbol:{input_data['symbol']}"
        elif "gesture" in input_data and input_data["gesture"]:
            return f"gesture:{input_data['gesture']}"
        elif "eye_data" in input_data and input_data["eye_data"]:
            region = input_data["eye_data"].get("region", "unknown")
            return f"eye:{region}"
        elif "voice_data" in input_data and input_data["voice_data"]:
            pattern = input_data["voice_data"].get("pattern", "unknown")
            return f"voice:{pattern}"
        else:
            return "unknown"

    def _fuse_results(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Fuse results from different processing pathways.

        Args:
            results: Results from different processing components

        Returns:
            dict: Integrated result
        """
        if not results:
            return {
                "status": "error",
                "message": "No input to process",
                "confidence": 0.0,
            }

        # Determine if we have a dominant modality with high confidence
        dominant_modality = None
        dominant_confidence = 0.0

        for modality, result in results.items():
            confidence = result.get("confidence", 0.0)
            if confidence > dominant_confidence and confidence >= 0.8:
                dominant_confidence = confidence
                dominant_modality = modality

        # If we have a clearly dominant modality, use its result as base
        if dominant_modality and dominant_confidence >= 0.8:
            base_result = results[dominant_modality].copy()
            base_result["dominant_modality"] = dominant_modality
        else:
            # Otherwise, use weighted fusion
            if self.multimodal_fusion_strategy == "weighted":
                base_result = self._weighted_fusion(results)
            else:
                # Default to highest confidence
                base_result = self._highest_confidence_fusion(results)

        # Add emotional indicators
        emotional_indicators = self._extract_emotional_indicators(results)
        base_result["emotional_indicators"] = emotional_indicators

        # Update overall confidence
        if "nonverbal_analysis" in results:
            # Factor in advanced analysis
            analysis_confidence = (
                results["nonverbal_analysis"]
                .get("combined_analysis", {})
                .get("confidence", 0.5)
            )
            base_result["confidence"] = (
                base_result.get("confidence", 0.5) * 0.7 + analysis_confidence * 0.3
            )

        # Ensure required fields are present
        if "message" not in base_result:
            # Generate message based on intent
            intent = base_result.get("intent", "unknown")
            expression = base_result.get("expression", "neutral")

            # Simple intent to message mapping
            intent_messages = {
                "affirm": "I understand you're confirming.",
                "deny": "I understand you're declining.",
                "help": "I understand you need assistance.",
                "greet": "Hello there!",
                "like": "I see you like this.",
                "dislike": "I understand you don't like this.",
                "stop": "I'll stop now.",
                "unknown": "I'm processing your input.",
            }

            base_result["message"] = intent_messages.get(
                intent, "I'm interpreting your communication."
            )

        # Add input modalities for reference
        base_result["input_modalities"] = list(results.keys())

        return base_result

    def _weighted_fusion(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Perform weighted fusion of results.

        Args:
            results: Results from different processing components

        Returns:
            dict: Fused result
        """
        # Define modality weights
        modality_weights = {
            "text": 1.0,  # Text is generally most explicit
            "gesture": 0.8,  # Gestures often clear but may be ambiguous
            "eye": 0.6,  # Eye tracking is more subtle
            "voice": 0.7,  # Voice patterns may be distinctive
            "nonverbal_analysis": 0.5,  # Secondary analysis, already included in other modalities
        }

        # Collect intent votes with weights
        intent_votes = {}
        expression_votes = {}
        emotion_tier_votes = {"mild": 0, "moderate": 0, "strong": 0, "urgent": 0}
        message_options = []

        total_weight = 0.0
        total_confidence = 0.0

        for modality, result in results.items():
            # Skip nonverbal_analysis as it's a meta-analysis
            if modality == "nonverbal_analysis":
                continue

            weight = modality_weights.get(modality, 0.5)
            confidence = result.get("confidence", 0.5)

            # Apply confidence-adjusted weight
            effective_weight = weight * confidence
            total_weight += effective_weight
            total_confidence += confidence

            # Vote for intent
            intent = result.get("intent", "unknown")
            if intent not in intent_votes:
                intent_votes[intent] = 0.0
            intent_votes[intent] += effective_weight

            # Vote for expression
            expression = result.get("expression", "neutral")
            if expression not in expression_votes:
                expression_votes[expression] = 0.0
            expression_votes[expression] += effective_weight

            # Vote for emotion tier
            emotion_tier = result.get("emotion_tier", "mild")
            emotion_tier_votes[emotion_tier] += effective_weight

            # Collect message
            if "message" in result:
                message_options.append(
                    {"message": result["message"], "weight": effective_weight}
                )

        # Determine best intent, expression, and emotion tier
        best_intent = (
            max(intent_votes.items(), key=lambda x: x[1])[0]
            if intent_votes
            else "unknown"
        )
        best_expression = (
            max(expression_votes.items(), key=lambda x: x[1])[0]
            if expression_votes
            else "neutral"
        )
        best_emotion_tier = max(emotion_tier_votes.items(), key=lambda x: x[1])[0]

        # Choose message
        message_options.sort(key=lambda x: x["weight"], reverse=True)
        best_message = (
            message_options[0]["message"]
            if message_options
            else "I'm processing your input."
        )

        # Calculate overall confidence as weighted average
        avg_confidence = total_confidence / len(results) if results else 0.5

        return {
            "status": "success",
            "intent": best_intent,
            "expression": best_expression,
            "emotion_tier": best_emotion_tier,
            "message": best_message,
            "confidence": avg_confidence,
            "fusion_method": "weighted",
        }

    def _highest_confidence_fusion(
        self, results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fuse results by selecting the one with highest confidence.

        Args:
            results: Results from different processing components

        Returns:
            dict: Best result
        """
        best_result = None
        best_confidence = 0.0

        for modality, result in results.items():
            # Skip nonverbal_analysis as it's a meta-analysis
            if modality == "nonverbal_analysis":
                continue

            confidence = result.get("confidence", 0.0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_result = result.copy()

        if best_result:
            best_result["fusion_method"] = "highest_confidence"
            return best_result
        else:
            return {
                "status": "error",
                "message": "No valid results to fuse",
                "confidence": 0.0,
                "fusion_method": "highest_confidence",
            }

    def _extract_emotional_indicators(
        self, results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract emotional indicators from results.

        Args:
            results: Results from different processing components

        Returns:
            dict: Emotional indicators
        """
        emotional_indicators = {}

        # Extract from nonverbal analysis if available
        if "nonverbal_analysis" in results:
            analysis = results["nonverbal_analysis"]
            combined = analysis.get("combined_analysis", {})
            indicators = combined.get("intent_indicators", {})

            for emotion, value in indicators.items():
                emotional_indicators[emotion] = value

        # Extract from gesture-specific emotional indicators
        if "gesture" in results:
            gesture_result = results["gesture"]
            gesture_emotions = gesture_result.get("emotional_indicators", {})

            for emotion, value in gesture_emotions.items():
                if emotion not in emotional_indicators:
                    emotional_indicators[emotion] = 0.0
                emotional_indicators[emotion] = max(
                    emotional_indicators[emotion], value
                )

        # Map standard expressions to emotional indicators
        expression_map = {
            "positive": {"happiness": 0.7, "satisfaction": 0.6},
            "negative": {"dissatisfaction": 0.7, "frustration": 0.6},
            "urgent": {"urgency": 0.8, "stress": 0.6},
            "inquisitive": {"curiosity": 0.7, "interest": 0.6},
            "neutral": {"neutral": 0.7},
        }

        # Add indicators from expression if not already present
        for result in results.values():
            expression = result.get("expression", "neutral")
            if expression in expression_map:
                for emotion, value in expression_map[expression].items():
                    if emotion not in emotional_indicators:
                        emotional_indicators[emotion] = value

        return emotional_indicators

    def update_context(self, context: Dict[str, Any]):
        """Update the current context.

        Args:
            context: Context information to update
        """
        for key, value in context.items():
            self.current_context[key] = value

        logger.debug(f"Updated context: {context.keys()}")

    def get_context(self) -> Dict[str, Any]:
        """Get the current context.

        Returns:
            dict: Current context
        """
        return self.current_context

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get interpreter performance metrics.

        Returns:
            dict: Performance metrics
        """
        # Calculate average processing time
        avg_processing_time = (
            sum(self.performance_metrics["processing_times"])
            / len(self.performance_metrics["processing_times"])
            if self.performance_metrics["processing_times"]
            else 0.0
        )

        metrics = self.performance_metrics.copy()
        metrics["average_processing_time"] = avg_processing_time

        return metrics

    def predict_next_interaction(self) -> Dict[str, Any]:
        """Predict the next likely user interaction based on history and
        context.

        Returns:
            dict: Prediction with confidence
        """
        if not self.interaction_history:
            return {"prediction": "insufficient_data", "confidence": 0.0}

        # Get behavior prediction
        behavior_prediction = self.behavioral_interpreter.predict_behavior(
            self.current_context
        )

        # Extract predicted behaviors
        likely_behaviors = behavior_prediction.get("likely_behaviors", [])

        # Maps predicted behaviors to predicted interactions
        predicted_interactions = []

        for behavior in likely_behaviors:
            behavior_type = behavior.get("behavior_type", "")
            probability = behavior.get("probability", 0.0)

            # Map behavior types to interaction types
            if behavior_type.startswith("gesture:"):
                gesture = behavior_type.split(":")[1] if ":" in behavior_type else ""
                predicted_interactions.append(
                    {"type": "gesture", "value": gesture, "probability": probability}
                )
            elif behavior_type.startswith("text:"):
                predicted_interactions.append(
                    {"type": "text", "probability": probability}
                )
            elif behavior_type.startswith("eye:"):
                region = behavior_type.split(":")[1] if ":" in behavior_type else ""
                predicted_interactions.append(
                    {
                        "type": "eye_movement",
                        "value": region,
                        "probability": probability,
                    }
                )

        return {
            "prediction": "context_based",
            "predicted_interactions": predicted_interactions,
            "confidence": behavior_prediction.get("confidence", 0.0),
            "context": self.current_context,
        }

    def reset(self):
        """Reset the interpreter state."""
        self.interaction_history = []
        self.current_context = {
            "time_of_day": None,
            "location": None,
            "activity": None,
            "previous_intents": [],
            "conversation_state": "beginning",
            "emotional_state": None,
        }

        # Reset component engines
        if hasattr(self, "behavioral_interpreter"):
            self.behavioral_interpreter.reset_history()

        logger.info("Interpreter state reset")


# Singleton instance
_interpreter = None


def get_interpreter():
    """Get or create the interpreter singleton."""
    global _interpreter
    if _interpreter is None:
        _interpreter = Interpreter()
    return _interpreter
