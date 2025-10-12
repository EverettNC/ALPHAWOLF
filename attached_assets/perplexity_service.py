import logging
import os
from typing import Any, Dict, Optional
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class PerplexityService:
    def __init__(self, 
                 model: Optional[str] = None, 
                 temperature: Optional[float] = None,
                 top_p: Optional[float] = None, 
                 max_tokens: Optional[int] = None):
        self.api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            logger.error("PERPLEXITY_API_KEY environment variable is not set")
            raise RuntimeError("PERPLEXITY_API_KEY environment variable is required")
        
        self.base_url = "https://api.perplexity.ai/chat/completions"
        allowed_models = {
            "sonar", "sonar-pro", "sonar-reasoning", "sonar-deep-research", "r1-1776",
            "llama-3.1-sonar-small-128k-online", "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-small-128k-chat", "llama-3.1-sonar-large-128k-chat",
            "llama-3.1-70b-instruct", "llama-3.1-8b-instruct"
        }
        self.model = model or os.environ.get("PERPLEXITY_MODEL", "sonar-pro")
        if self.model not in allowed_models:
            raise ValueError(f"Unsupported Perplexity model: {self.model}")
        self.temperature = float(temperature if temperature is not None else os.environ.get("PERPLEXITY_TEMPERATURE", "0.2"))
        self.top_p = float(top_p if top_p is not None else os.environ.get("PERPLEXITY_TOP_P", "0.9"))
        self.max_tokens = int(max_tokens if max_tokens is not None else os.environ.get("PERPLEXITY_MAX_TOKENS", "500"))

        logger.info("PerplexityService initialized with model: %s", self.model)
    # -----------------------------------------------------------
    # Core API Call
    # -----------------------------------------------------------
    def _call_api(self, messages: list, **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", self.top_p),
        }

        # --- ADD THIS LINE ---
        logger.error(f"API request payload:\n{json.dumps(data, indent=2)}")

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError:
            logger.error(f"API returned {response.status_code}: {response.text}")
            raise


    # -----------------------------------------------------------
    # Main Content Generation
    # -----------------------------------------------------------
    def generate_content(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        # ✅ Perplexity no longer needs a system message. Only user content.
        messages = [{"role": "user", "content": prompt}]

        try:
            result = self._call_api(
                messages,
                max_tokens=max_tokens,
                temperature=temperature,
                # Remove or conditionally include extras:
                # search_enabled=search_enabled,
                # return_citations=return_citations,
            )

            choices = result.get("choices", [])
            if not choices:
                logger.error(f"API returned no choices. Raw response: {result}")
                raise ValueError("No choices returned from API")

            first_choice = choices[0]
            if not isinstance(first_choice, dict) or "message" not in first_choice:
                logger.error(f"API returned invalid choice format. Raw choices: {choices}")
                raise ValueError("Invalid choice format in API response")

            message = first_choice["message"]
            if not isinstance(message, dict) or "content" not in message:
                logger.error(f"API returned invalid message format. Raw message: {message}")
                raise ValueError("Invalid message format in API response")

            response_data = {"content": message["content"]}
            # Note: return_citations is not defined in the function signature
            # if return_citations and "citations" in result:
            #     response_data["citations"] = result["citations"]

            return response_data

        except requests.RequestException as e:
            logger.error("Network error calling Perplexity API: %s", str(e))
            return {"error": f"Network error: {str(e)}"}
        except ValueError as e:
            logger.error("API response format error: %s", str(e))
            return {"error": f"Response format error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    # -----------------------------------------------------------
    # Helper Methods for Derek / Your System
    # -----------------------------------------------------------
    def get_educational_content(self, topic: str) -> Dict[str, Any]:
        prompt = (
            f"What are the latest findings and best practices regarding {topic} "
            f"in relation to autism and nonverbal communication?"
        )
        return self.generate_content(
            prompt=prompt,
            max_tokens=500,
            temperature=0.2,
        )

    def get_communication_suggestions(
        self, voice_analysis: Dict[str, float]
    ) -> Dict[str, Any]:
        emotions_description = ", ".join(
            [f"{emotion}: {score:.2%}" for emotion, score in voice_analysis.items()]
        )
        prompt = (
            f"Based on this voice analysis ({emotions_description}), "
            f"what communication strategies would be most effective for autism support?"
        )
        return self.generate_content(
            prompt=prompt,
            max_tokens=300,
            temperature=0.2,
        )

    def translate_text(self, text: str, target_language: str) -> Dict[str, Any]:
        prompt = f"Translate this text into {target_language}:\n\n{text}"
        return self.generate_content(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.1,
        )

    def summarize_text(self, text: str, length: str = "medium") -> Dict[str, Any]:
        length_map = {
            "short": "a very concise summary in 1-2 sentences",
            "medium": "a paragraph-length summary capturing the main points",
            "long": "a detailed summary preserving essential information",
        }
        prompt = f"Please provide {length_map.get(length, length_map['medium'])} of the following:\n\n{text}"
        return self.generate_content(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.2,
        )

    def generate_communication_aids(
        self, situation: str, user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        preferences = (
            "User preferences: "
            + ", ".join(f"{k}: {v}" for k, v in user_preferences.items())
            if user_preferences
            else ""
        )
        prompt = f"""
        Create communication aids for the following situation:
        {situation}
        {preferences}

        Include:
        1. Short scripts for common exchanges
        2. Visual cue suggestions
        3. Alternative communication strategies
        4. Sensory considerations
        5. Exit strategies
        """
        return self.generate_content(
            prompt=prompt,
            max_tokens=800,
            temperature=0.3,
        )

    def simplify_language(self, text: str, level: str = "medium") -> Dict[str, Any]:
        level_map = {
            "high": "very basic language for young children or those with processing difficulties",
            "medium": "plain language, short sentences, no jargon",
            "low": "preserve content but clarify complex terms and long sentences",
        }
        prompt = f"Please simplify this text using {level_map.get(level, level_map['medium'])}:\n\n{text}"
        return self.generate_content(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.2,
        )

