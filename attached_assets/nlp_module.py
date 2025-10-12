# Rewriting the AdvancedNLPProcessor with integration for loading API keys and sentiment analysis (Azure + fallback).
import json
import logging
import os
import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_api_keys(config_path="config/keys.json") -> Dict[str, Any]:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Missing config file at {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)


class AdvancedNLPProcessor:
    def __init__(self):
        """Initialize the Advanced NLP Processor."""
        self.academic_domains = {
            "philosophy": [
                "ethics",
                "moral",
                "kant",
                "metaphysics",
                "existentialism",
                "philosophical",
                "epistemology",
                "ontology",
                "categorical imperative",
            ],
            "science": [
                "climate",
                "physics",
                "chemistry",
                "biology",
                "scientific",
                "empirical",
                "evidence",
                "hypothesis",
                "quantum",
                "crispr",
                "gene",
            ],
            "mathematics": [
                "theorem",
                "proof",
                "geometry",
                "algebra",
                "calculus",
                "mathematical",
                "equation",
                "fermat",
                "number theory",
            ],
            "psychology": [
                "cognitive",
                "behavioral",
                "therapy",
                "psychological",
                "disorders",
                "mental health",
                "counseling",
                "psychiatry",
            ],
            "linguistics": [
                "grammar",
                "syntax",
                "semantics",
                "language",
                "linguistic",
                "chomsky",
                "phonology",
                "morphology",
            ],
            "economics": [
                "macroeconomic",
                "microeconomic",
                "fiscal",
                "monetary",
                "inflation",
                "employment",
                "market",
                "economic",
            ],
            "history": [
                "historical",
                "revolution",
                "historiographical",
                "civilization",
                "ancient",
                "medieval",
                "modern history",
            ],
        }

        self.api_keys = _load_api_keys()
        self.azure_keys = self.api_keys.get("azure", {})
        self.openai_key = self.api_keys.get("openai", {}).get("api_key")

        self._load_response_templates()
        logger.info("Advanced NLP Processor initialized")

    def _load_response_templates(self):
        try:
            with open("data/nlp_responses.json", "r") as f:
                self.responses = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.responses = {
                "emotional": {
                    "happy": ["You seem happy!", "That’s wonderful!"],
                    "sad": ["I sense sadness.", "Want to talk about it?"],
                    "angry": ["You seem frustrated.", "It’s okay to feel that way."],
                    "fear": [
                        "You seem concerned.",
                        "Let’s work through this together.",
                    ],
                    "surprise": [
                        "You seem surprised!",
                        "That must’ve been unexpected.",
                    ],
                    "neutral": ["You seem neutral.", "Anything on your mind?"],
                },
                "gaze": {
                    "center": "You're focusing directly, which suggests engagement.",
                    "left": "Your gaze is directed to the left, possibly recalling.",
                    "right": "You're looking right, maybe imagining something.",
                },
                "blink": {
                    True: "Normal blinking detected.",
                    False: "Steady gaze detected.",
                },
                "perspiration": {"high": "High stress detected."},
                "phd_level": {
                    "philosophy": [
                        "Kant’s idealism suggests knowledge is a mental construct."
                    ],
                    "science": ["Scientific consensus shows emergent system behavior."],
                    "mathematics": ["This relates to Riemannian geometry."],
                    "psychology": ["Cognitive biases tie to dual-process theory."],
                    "linguistics": ["Chomsky’s grammar defines linguistic universals."],
                    "economics": ["Behavioral economics shows irrational choices."],
                    "history": ["Historians moved from Great Man to Annales school."],
                },
            }

    def analyze_sentiment_azure(self, text: str) -> Dict[str, Any]:
        try:
            from azure.ai.textanalytics import TextAnalyticsClient
            from azure.core.credentials import AzureKeyCredential

            endpoint = self.azure_keys.get("text_analytics_endpoint")
            key = self.azure_keys.get("text_analytics_key")

            if not endpoint or not key:
                raise ValueError("Azure endpoint or key missing")

            client = TextAnalyticsClient(
                endpoint=endpoint, credential=AzureKeyCredential(key)
            )
            documents = [text]
            response = client.analyze_sentiment(documents=documents)[0]

            return {
                "sentiment": response.sentiment,
                "confidence_scores": {
                    "positive": response.confidence_scores.positive,
                    "neutral": response.confidence_scores.neutral,
                    "negative": response.confidence_scores.negative,
                },
            }
        except Exception as e:
            logger.error(f"Azure sentiment analysis failed: {e}")
            return {"sentiment": "unknown", "confidence_scores": {}}

    def analyze_text(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        best_domain = None
        best_score = 0

        for domain, keywords in self.academic_domains.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if score > best_score:
                best_domain = domain
                best_score = score

        confidence = min(0.5 + (best_score * 0.1), 0.95) if best_score > 0 else 0.0

        return {"domain": best_domain, "confidence": confidence, "text": text}

    def process_input(self, **kwargs) -> Dict[str, Any]:
        logger.info(f"Processing input: {kwargs}")
        response = "I'm here to help you communicate."
        domain = None
        confidence = 0.0

        if "text" in kwargs and kwargs["text"]:
            text_analysis = self.analyze_text(kwargs["text"])
            domain = text_analysis["domain"]
            confidence = text_analysis["confidence"]

            if domain:
                response = self._generate_domain_response(domain, text_analysis["text"])
            else:
                sentiment = self.analyze_sentiment_azure(kwargs["text"])
                response = f"Azure detected a {sentiment['sentiment']} tone. Let’s go from there."
        else:
            parts = []
            if "emotion" in kwargs:
                parts.append(
                    random.choice(
                        self.responses["emotional"].get(kwargs["emotion"], [])
                    )
                )
            if "gaze" in kwargs:
                parts.append(self.responses["gaze"].get(kwargs["gaze"], ""))
            if "blink" in kwargs:
                parts.append(self.responses["blink"].get(kwargs["blink"], ""))
            if "perspiration" in kwargs:
                parts.append(
                    self.responses["perspiration"].get(kwargs["perspiration"], "")
                )

            response = " ".join(filter(None, parts))

        return {
            "response": response,
            "domain": domain,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }

    def _generate_domain_response(self, domain: str, text: str) -> str:
        if domain in self.responses["phd_level"]:
            return f"Regarding your inquiry in {domain}: {random.choice(self.responses['phd_level'][domain])}"
        return f"Your interest in {domain} is fascinating. Could you specify what aspect you want to explore?"

    def get_supported_domains(self) -> List[str]:
        return list(self.academic_domains.keys())

    def get_keywords_for_domain(self, domain: str) -> List[str]:
        return self.academic_domains.get(domain, [])


# Singleton instance
_nlp_processor = None


def get_nlp_processor():
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = AdvancedNLPProcessor()
    return _nlp_processor
