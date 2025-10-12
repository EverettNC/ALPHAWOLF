"""
AlphaVox - Conversation Bridge Module
-------------------------------------
This module bridges between various analysis components (eye tracking, nonverbal, etc.)
and the conversation generation, enabling multi-modal communication.

The bridge processes analyzed inputs from various sensors and contexts,
then generates appropriate conversational responses using AI models.
"""

import logging
import random
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConversationBridge:
    """The ConversationBridge acts as an intermediary between various input
    analyses (eye tracking, nonverbal, etc.) and the generation of appropriate
    responses.

    It handles:
    - Interpretation of emotional states
    - Persona-based response generation
    - Contextual understanding of gaze and other inputs
    - Academic and domain-specific response generation
    """

    def __init__(self, persona: str = "default"):
        """Initialize the conversation bridge.

        Args:
            persona: The starting persona to use for generating responses
                     (default, academic, supportive, child-friendly)
        """
        self.persona = persona
        self.context_history = []
        self.session_data = {}

        # Load response templates
        self._load_response_templates()

        logger.info(f"Conversation Bridge initialized with persona: {persona}")

    def _load_response_templates(self):
        """Load response templates for different emotions and personas."""

        # Dictionary of emotional responses by persona
        self.response_templates = {
            "default": {
                "happy": [
                    "I see you're feeling positive!",
                    "You seem happy, that's great to see.",
                    "Your expression looks cheerful today.",
                ],
                "sad": [
                    "I notice you might be feeling down.",
                    "You seem a bit sad. Is everything okay?",
                    "Would you like to talk about what's bothering you?",
                ],
                "fear": [
                    "You appear to be concerned about something.",
                    "I sense some anxiety. Can I help with anything?",
                    "You seem worried. Would you like to discuss it?",
                ],
                "neutral": [
                    "How can I assist you today?",
                    "I'm here if you need anything.",
                    "Is there something specific you'd like to talk about?",
                ],
                "gaze_right": [
                    "I notice you're looking to the right.",
                    "Something interesting on your right?",
                ],
                "gaze_left": [
                    "You're looking to the left. Need something from there?",
                    "I see you looking leftward. Can I help with anything?",
                ],
                "perspiration": [
                    "You seem a bit stressed. Would you like to take a moment?",
                    "I notice you might be feeling anxious. Let's pause if needed.",
                ],
            },
            "academic": {
                "happy": [
                    "Your positive demeanor suggests an optimal state for learning.",
                    "I observe signs of positive affect, which correlates with enhanced cognitive performance.",
                ],
                "sad": [
                    "Research indicates emotional states can impact cognitive processing. Would you like to discuss?",
                    "I detect indicators of negative affect. Studies suggest brief mindfulness exercises may help.",
                ],
                "fear": [
                    "Anxiety can affect information processing. Perhaps we could examine this topic systematically.",
                    "Heightened arousal states can impact memory consolidation. Would a different approach help?",
                ],
                "neutral": [
                    "Would you prefer to explore a topic through inductive or deductive reasoning?",
                    "I can provide information across various academic domains. What interests you?",
                    "Several research paradigms might be applicable to your query. How shall we proceed?",
                ],
                "gaze_right": [
                    "Visual attention shifting rightward often correlates with accessing certain memory types in research paradigms.",
                ],
                "gaze_left": [
                    "Leftward gaze patterns have been studied in relation to certain cognitive processing tasks.",
                ],
                "perspiration": [
                    "Physiological indicators suggest elevated stress levels. Research indicates cognitive performance follows an inverted U-curve in relation to stress.",
                ],
            },
            "supportive": {
                "happy": [
                    "I'm glad to see you looking happy! Your smile brightens the day.",
                    "It's wonderful to see you in good spirits. What's bringing you joy?",
                ],
                "sad": [
                    "I'm here for you when you're feeling down. Sometimes just talking helps.",
                    "It's okay to feel sad sometimes. Would sharing what's on your mind help?",
                    "I care about how you're feeling. Would you like to talk about it?",
                ],
                "fear": [
                    "Whatever you're worried about, we can face it together.",
                    "It's okay to feel anxious. Let's take a deep breath together.",
                    "I'm right here with you. We'll take things one step at a time.",
                ],
                "neutral": [
                    "I'm here to support you however you need today.",
                    "How are you feeling right now? I'm here to listen.",
                    "Your wellbeing matters to me. How can I help?",
                ],
                "gaze_right": [
                    "Take your time to look around. I'm here whenever you're ready.",
                ],
                "gaze_left": [
                    "I notice you looking away. Sometimes that helps us think.",
                ],
                "perspiration": [
                    "You seem a bit stressed. Remember to breathe deeply. I'm here with you.",
                    "When things feel overwhelming, we can pause and reset together.",
                ],
            },
            "child-friendly": {
                "happy": [
                    "Your smile is super bright today! Like sunshine!",
                    "Wow, you look really happy! That makes me happy too!",
                ],
                "sad": [
                    "It's okay to feel a little blue sometimes. Want to talk about it?",
                    "Everyone feels sad sometimes. Would a story help cheer you up?",
                ],
                "fear": [
                    "Don't worry! We can be brave together!",
                    "Feeling scared is normal. What helps is naming what's scary.",
                ],
                "neutral": [
                    "What fun things should we talk about today?",
                    "I'm ready for an adventure! Are you?",
                    "What cool thing would you like to learn about?",
                ],
                "gaze_right": [
                    "I spy with my little eye... something over there?",
                ],
                "gaze_left": [
                    "Oh! Did you see something fun over there?",
                ],
                "perspiration": [
                    "Let's take a deep dragon breath together! In through the nose, out through the mouth!",
                ],
            },
        }

        # Academic domain responses
        self.academic_domains = {
            "science": {
                "basic": [
                    "Science is about discovering how our world works through observation and testing ideas.",
                    "The scientific method helps us ask questions and find reliable answers.",
                ],
                "intermediate": [
                    "Scientific inquiry involves forming hypotheses, designing experiments with controls, and analyzing data to draw conclusions.",
                    "Different scientific disciplines use specialized methodologies while adhering to core principles of empirical evidence.",
                ],
                "advanced": [
                    "Contemporary scientific epistemology acknowledges both the power and limitations of methodological naturalism while recognizing the role of paradigm shifts in scientific revolutions.",
                    "Meta-analyses and systematic reviews represent hierarchically superior evidence forms, though they remain vulnerable to publication bias and methodological heterogeneity.",
                ],
            },
            "mathematics": {
                "basic": [
                    "Mathematics helps us understand patterns and relationships using numbers and symbols.",
                    "Mathematical thinking involves logical reasoning and problem-solving strategies.",
                ],
                "intermediate": [
                    "Mathematics encompasses various branches including algebra, geometry, calculus, and statistics, each with distinct approaches to abstraction.",
                    "Mathematical proofs provide rigorous verification of theorems through deductive reasoning from axioms and previously established results.",
                ],
                "advanced": [
                    "Contemporary mathematical research explores the intersections of topology, abstract algebra, and category theory to illuminate structural invariants across seemingly disparate domains.",
                    "Non-Euclidean geometries and transfinite set theory challenged fundamental assumptions, demonstrating mathematics' capacity for self-reinvention through axiomatic reexamination.",
                ],
            },
            "history": {
                "basic": [
                    "History is the study of past events and how they shape our present world.",
                    "Historians use primary sources like letters and artifacts to understand what happened in the past.",
                ],
                "intermediate": [
                    "Historical analysis involves evaluating source credibility, recognizing bias, and contextualizing events within broader social, economic, and political frameworks.",
                    "Historiography examines how historical interpretation itself changes over time, reflecting contemporary concerns and methodological developments.",
                ],
                "advanced": [
                    "Postcolonial historiography challenges Eurocentric narratives through methodological innovations that center previously marginalized epistemologies and lived experiences.",
                    "The linguistic turn in historical analysis interrogates discursive formations as both reflections of and constitutive forces in power relations across temporal and spatial contexts.",
                ],
            },
        }

        logger.debug("Response templates loaded successfully")

    def set_persona(self, persona: str) -> None:
        """Change the current persona.

        Args:
            persona: The persona to switch to
                    (default, academic, supportive, child-friendly)
        """
        if persona in self.response_templates:
            self.persona = persona
            logger.info(f"Switched to {persona} persona")
        else:
            logger.warning(f"Unknown persona '{persona}'. Staying with {self.persona}")

    def process_analysis(self, analysis: Dict[str, Any]) -> str:
        """Process analysis results from various inputs and generate a
        response.

        Args:
            analysis: Dictionary containing analysis results, potentially including:
                     - emotion: Detected emotion (happy, sad, fear, neutral, etc.)
                     - emotion_confidence: Confidence score for emotion detection
                     - gaze_direction: Direction of gaze (center, left, right, etc.)
                     - blink_detected: Whether blinking was detected
                     - perspiration: Whether perspiration was detected
                     - domain: Optional academic domain being discussed

        Returns:
            A generated response string appropriate to the input analysis
        """
        # Store this analysis in context history (limit to last 10)
        self.context_history.append(analysis)
        if len(self.context_history) > 10:
            self.context_history.pop(0)

        # If we have an academic domain, use that for response generation
        if "domain" in analysis and self.persona == "academic":
            domain = analysis.get("domain", "science")
            depth = analysis.get("depth", "intermediate")
            return self.generate_academic_response(domain, depth)

        # Otherwise generate response based on emotion and other factors
        response = self._generate_response_from_analysis(analysis)

        logger.debug(f"Generated response: {response}")
        return response

    def _generate_response_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Generate a response based on the analysis.

        Args:
            analysis: Dictionary containing analysis results

        Returns:
            Generated response string
        """
        # Get the current persona's response templates
        persona_templates = self.response_templates.get(
            self.persona, self.response_templates["default"]
        )

        # Extract key factors from analysis
        emotion = analysis.get("emotion", "neutral")
        confidence = analysis.get("emotion_confidence", 0.5)
        gaze = analysis.get("gaze_direction", "center")
        perspiration = analysis.get("perspiration", False)

        # List of potential responses based on various factors
        potential_responses = []

        # Add emotion-based responses if confidence is high enough
        if confidence >= 0.6:
            if emotion in persona_templates:
                potential_responses.extend(persona_templates[emotion])
        else:
            # Lower confidence, use neutral responses
            potential_responses.extend(persona_templates["neutral"])

        # Add gaze-direction responses
        if gaze != "center":
            gaze_key = f"gaze_{gaze}"
            if gaze_key in persona_templates:
                potential_responses.extend(persona_templates[gaze_key])

        # Add perspiration response if detected
        if perspiration and "perspiration" in persona_templates:
            potential_responses.extend(persona_templates["perspiration"])

        # If we somehow have no responses, use a generic fallback
        if not potential_responses:
            return "I'm here to assist you. How can I help today?"

        # Select a response randomly from potential responses
        return random.choice(potential_responses)

    def generate_academic_response(
        self, topic: str, depth: str = "intermediate"
    ) -> str:
        """Generate an academic response on a given topic at the specified
        depth.

        Args:
            topic: The academic topic or domain
            depth: The depth of the response (basic, intermediate, advanced)

        Returns:
            An academic response string
        """
        # Map the topic to a domain if possible
        domain = None
        for domain_key in self.academic_domains:
            if topic.lower() in domain_key:
                domain = domain_key
                break

        # If no matching domain, use the first academic domain as fallback
        if not domain:
            if topic.lower() in ["physics", "chemistry", "biology", "astronomy"]:
                domain = "science"
            elif topic.lower() in ["algebra", "geometry", "calculus", "statistics"]:
                domain = "mathematics"
            elif topic.lower() in ["world war", "renaissance", "ancient", "medieval"]:
                domain = "history"
            else:
                # Default to science for unknown topics
                domain = "science"

        # Validate depth parameter
        if depth not in ["basic", "intermediate", "advanced"]:
            depth = "intermediate"  # Default to intermediate

        # Get responses for this domain and depth
        domain_responses = self.academic_domains.get(
            domain, self.academic_domains["science"]
        )
        depth_responses = domain_responses.get(depth, domain_responses["intermediate"])

        # Return a random response from the appropriate depth
        response = random.choice(depth_responses)

        # For custom topics not in our predefined domains, add a prefix
        if domain not in self.academic_domains and topic.lower() not in domain:
            topic_prefixes = [
                f"Regarding {topic}, ",
                f"On the subject of {topic}, ",
                f"When examining {topic}, ",
                f"In the field of {topic}, ",
            ]
            response = random.choice(topic_prefixes) + response

        return response
