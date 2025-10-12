import json
import logging
import os

from flask import jsonify, request, session

from conversation_bridge import ConversationBridge
from interpreter import analyze_frame

# Configure logger
logger = logging.getLogger(__name__)

# Global conversation bridge instance
# Default to "default" persona, but can be changed through settings
conversation_bridge = ConversationBridge(persona="default")


def register_eye_tracking_api(app, csrf):
    """Register the enhanced eye tracking API endpoints."""

    @app.route("/analyze-eye-tracking-v2", methods=["POST"])
    @csrf.exempt
    def analyze_eye_tracking_v2():
        """Enhanced eye tracking endpoint with direct prediction and response
        generation.

        This is a streamlined implementation compared to the multi-modal
        processor.
        """
        try:
            data = request.get_json()
            frame_data = data.get("frame")
            if not frame_data:
                return jsonify({"error": "Missing frame data"}), 400

            # Get user preferences from session if available
            user_id = session.get("user_id", "anonymous")
            persona = session.get("persona", "default")

            # Set persona if different from current
            global conversation_bridge
            conversation_bridge.set_persona(persona)

            # Analyze frame data
            analysis = analyze_frame(frame_data)
            prediction = predict_outcome(analysis["analysis"])

            # Generate AI response using conversation bridge
            ai_response = generate_ai_response(analysis["analysis"], user_id)

            response = {
                "analysis": analysis["analysis"],
                "response": ai_response,
                "prediction": prediction,
            }

            # Log the analysis and response for debugging
            logger.debug(f"Eye tracking analysis: {json.dumps(analysis['analysis'])}")
            logger.debug(f"Generated response: {ai_response}")

            return jsonify(response)

        except Exception as e:
            logger.error(f"Error in eye tracking analysis: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/change-persona", methods=["POST"])
    @csrf.exempt  # Consider changing this in production
    def change_persona():
        """Change the conversation persona for response generation."""
        try:
            data = request.get_json()
            new_persona = data.get("persona")

            if not new_persona:
                return jsonify({"error": "Missing persona parameter"}), 400

            # Change persona
            global conversation_bridge
            success = conversation_bridge.set_persona(new_persona)

            if success:
                # Store in session if successful
                session["persona"] = new_persona
                return jsonify(
                    {"success": True, "message": f"Persona changed to {new_persona}"}
                )
            else:
                return jsonify({"error": f"Invalid persona: {new_persona}"}), 400

        except Exception as e:
            logger.error(f"Error changing persona: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/academic-response", methods=["POST"])
    @csrf.exempt  # Consider changing this in production
    def get_academic_response():
        """Generate a PhD-level academic response on a given topic."""
        try:
            data = request.get_json()
            topic = data.get("topic")
            depth = data.get("depth", "advanced")

            if not topic:
                return jsonify({"error": "Missing topic parameter"}), 400

            # Generate academic response
            global conversation_bridge
            response = conversation_bridge.generate_academic_response(topic, depth)

            return jsonify({"response": response, "topic": topic, "depth": depth})

        except Exception as e:
            logger.error(f"Error generating academic response: {str(e)}")
            return jsonify({"error": str(e)}), 500


def generate_ai_response(analysis, user_id="anonymous"):
    """Generate an AI response based on the analysis of eye tracking and other
    physical indicators. Uses the ConversationBridge to generate human-quality
    responses.

    Args:
        analysis (dict): The analysis result from the eye tracking system
        user_id (str): Optional user ID for personalized responses

    Returns:
        str: A natural language response appropriate to the detected state
    """
    global conversation_bridge

    # Process the analysis through conversation bridge
    response = conversation_bridge.process_analysis(analysis)

    # Log the generated response for the user
    logger.info(f"Generated response for user {user_id}: {response}")

    return response


def predict_outcome(analysis):
    """Predict a potential outcome or state based on the analysis.

    Args:
        analysis (dict): The analysis result from the eye tracking system

    Returns:
        str: A predictive assessment of the user's state or needs
    """
    # Enhanced predictive logic with more nuanced outcomes
    perspiration = analysis.get("perspiration")
    emotion = analysis.get("emotion")
    gaze = analysis.get("gaze_direction")
    blink = analysis.get("blink_detected")

    # Calculate combined emotional intensity
    emotion_confidence = analysis.get("emotion_confidence", 0.5)
    perspiration_level = 0.7 if perspiration else 0.0  # Simplification

    emotional_intensity = max(emotion_confidence, perspiration_level)

    # Distress detection
    if perspiration and emotion in ["angry", "fear", "sad"]:
        if emotional_intensity > 0.7:
            return "The user appears highly distressed. Consider recommending professional support."
        return "The user may be experiencing moderate distress. Recommend calming interaction."

    # Positive engagement
    elif emotion == "happy":
        if emotional_intensity > 0.7:
            return "Strong positive engagement detected. User appears enthusiastic."
        return "Positive engagement detected. Continue current interaction approach."

    # Communication attempt detection
    elif blink and gaze == "center":
        if emotion in ["neutral", "happy"]:
            return "User likely attempting intentional communication."
        else:
            return "User may be attempting communication, but emotional state suggests caution."

    # Directional interest
    elif gaze == "left" or gaze == "right":
        return f"User's attention directed {gaze}ward. Consider relevant context in that direction."

    # Default monitoring
    else:
        return "Monitoring ongoing. No specific action recommended."
