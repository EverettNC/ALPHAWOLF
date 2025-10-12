"""
AlphaVox - NLP Integration Module
-------------------------------
This module integrates the advanced NLP processor with the AICore and provides utilities
for enhancing AlphaVox's conversational capabilities to PhD level.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from nlp_module import AdvancedNLPProcessor

# Configure logger
logger = logging.getLogger(__name__)


class NLPIntegrationService:
    """Service for integrating NLP capabilities with AlphaVox's core AI."""

    def __init__(self, nlp_model=None, ai_core=None):
        self.nlp_processor = AdvancedNLPProcessor(nlp_model)
        self.ai_core = ai_core

        self.domain_expertise = {
            "science": 0.90,
            "philosophy": 0.95,
            "mathematics": 0.90,
            "medicine": 0.85,
            "linguistics": 0.95,
            "psychology": 0.90,
            "history": 0.85,
            "economics": 0.80,
        }

        self.emotional_intelligence = {
            "empathy": 0.95,
            "self_awareness": 0.90,
            "adaptability": 0.90,
            "neurodivergent_sensitivity": 0.95,
        }

        logger.info("NLP Integration Service initialized successfully")

    def enhance_response(
        self,
        intent: str,
        confidence: float,
        user_input: Optional[str] = None,
        emotion: Optional[str] = None,
        gaze: Optional[str] = None,
        blink: Optional[bool] = None,
        perspiration: Optional[str] = None,
    ) -> Tuple[str, float]:
        nlp_result = self.nlp_processor.process_input(
            text=user_input,
            emotion=emotion,
            gaze=gaze,
            blink=blink,
            perspiration=perspiration,
        )

        domain = nlp_result.get("domain")
        domain_expertise_level = (
            self.domain_expertise.get(domain, 0.75) if domain else 0.75
        )

        if domain and confidence > 0.5:
            enhanced_confidence = (confidence + domain_expertise_level) / 2
        else:
            enhanced_confidence = confidence

        enhanced_response = nlp_result.get("response")

        if not enhanced_response or enhanced_confidence < 0.6:
            if user_input:
                enhanced_response = self.nlp_processor.generate_phd_level_response(
                    user_input
                )
            else:
                enhanced_response = self._generate_intent_based_response(
                    intent, emotion, gaze, blink
                )

        return enhanced_response, enhanced_confidence

    def _generate_intent_based_response(
        self,
        intent: str,
        emotion: Optional[str] = None,
        gaze: Optional[str] = None,
        blink: Optional[bool] = None,
    ) -> str:
        if emotion and gaze and blink is not None:
            key = (emotion, gaze, blink)
            if key in INTENT_NLP_RESPONSES:
                return INTENT_NLP_RESPONSES[key]

        intent_responses = {
            "greet": [
                "Hello. How may I assist you today?",
                "Greetings. I'm here to provide support for your communication needs.",
            ],
            "help": [
                "I can assist with a range of communication needs. Would you like information on specific capabilities?",
                "My purpose is to facilitate communication through multi-modal inputs. How can I best support you?",
            ],
            "track": [
                "I'm actively monitoring your eye movements and expressions to understand your needs better.",
                "My tracking systems are engaged. I'll respond to your nonverbal cues as precisely as possible.",
            ],
            "gesture": [
                "I've detected your gesture. Please continue using these movements to communicate your needs.",
                "Your gestural communication is being processed. This modality provides an effective channel for expression.",
            ],
            "question": [
                "That's an insightful inquiry. Let me provide a comprehensive response.",
                "Your question touches on important aspects. I'll address it thoroughly.",
            ],
            "academic": [
                "That's a fascinating academic topic. The literature in this field suggests several theoretical frameworks worth exploring.",
                "From a scholarly perspective, this subject intersects with multiple disciplines, each offering valuable insights.",
            ],
            "unknown": [
                "I notice you're trying to communicate. Let me know how I can better understand your needs.",
                "I'm attentive to your signals. Please continue, and I'll work to comprehend your intended meaning.",
            ],
        }

        responses = intent_responses.get(intent, intent_responses["unknown"])
        return responses[0]

    def analyze_text_for_academic_content(self, text: str) -> Dict:
        if not text:
            return {"academic_level": "undetermined", "confidence": 0.0}

        doc = self.nlp_processor.nlp(text)
        domain, confidence = self.nlp_processor._detect_academic_domain(doc)
        complexity_score = self._analyze_vocabulary_complexity(text)

        if domain and confidence > 0.7 and complexity_score > 0.6:
            academic_level = "advanced"
        elif domain and confidence > 0.5 and complexity_score > 0.4:
            academic_level = "intermediate"
        elif domain and confidence > 0.3:
            academic_level = "basic"
        else:
            academic_level = "general"

        return {
            "academic_level": academic_level,
            "domain": domain,
            "confidence": confidence,
            "complexity_score": complexity_score,
        }

    def _analyze_vocabulary_complexity(self, text: str) -> float:
        if not text or not self.nlp_processor.nlp:
            return 0.0

        doc = self.nlp_processor.nlp(text)

        word_count = len(
            [token for token in doc if not token.is_punct and not token.is_space]
        )
        if word_count == 0:
            return 0.0

        complex_words = [
            token.text for token in doc if len(token.text) > 8 and token.is_alpha
        ]
        complex_ratio = len(complex_words) / word_count if word_count > 0 else 0

        academic_terms = []
        for domain, terms in self.nlp_processor.academic_domains.items():
            for term in terms:
                if term in text.lower():
                    academic_terms.append(term)

        academic_term_ratio = len(academic_terms) / word_count if word_count > 0 else 0

        sentences = list(doc.sents)
        avg_sentence_length = (
            sum(
                len(
                    [
                        token
                        for token in sent
                        if not token.is_punct and not token.is_space
                    ]
                )
                for sent in sentences
            )
            / len(sentences)
            if sentences
            else 0
        )

        sentence_length_factor = min(avg_sentence_length / 40, 1.0)

        complexity_score = (
            (complex_ratio * 0.4)
            + (academic_term_ratio * 0.4)
            + (sentence_length_factor * 0.2)
        )

        return complexity_score

    def get_phd_level_explanation(self, topic: str, simplify: bool = False) -> str:
        domain, _ = self.nlp_processor._detect_academic_domain(
            self.nlp_processor.nlp(topic)
        )

        if simplify:
            return (
                self.nlp_processor.generate_phd_level_response(topic)
                + "\n\nTo put it more simply: "
                + self._generate_simplified_explanation(topic, domain)
            )
        else:
            return self.nlp_processor.generate_phd_level_response(topic)

    def _generate_simplified_explanation(
        self, topic: str, domain: Optional[str]
    ) -> str:
        simplified_explanations = {
            "science": "This is about how we observe, test, and understand the natural world through careful experiments and data analysis.",
            "philosophy": "This explores fundamental questions about knowledge, reality, existence, and ethics through logical reasoning.",
            "mathematics": "This involves the study of numbers, quantities, shapes, and patterns using precise rules and abstract thinking.",
            "medicine": "This concerns understanding how the human body works, what happens when it doesn't work properly, and how to fix those problems.",
            "linguistics": "This is about how language works - the sounds, structures, meanings, and social uses of human communication.",
            "psychology": "This examines how people think, feel, and behave, and why they do what they do.",
            "history": "This involves studying the past to understand how events, societies, and people have shaped our world today.",
            "economics": "This looks at how resources are produced, distributed, and consumed, and how people make decisions about these processes.",
        }

        if domain and domain in simplified_explanations:
            return simplified_explanations[domain]
        else:
            return "This topic involves examining specific questions using careful, evidence-based thinking and specialized knowledge."
