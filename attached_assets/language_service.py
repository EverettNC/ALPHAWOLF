import logging
import os
from typing import Dict, Optional

import requests
from flask import current_app

logger = logging.getLogger(__name__)


class LanguageService:
    """Service for handling language processing operations."""

    def __init__(self):
        self.api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            logger.warning("PERPLEXITY_API_KEY not found in environment variables")

    def _call_perplexity_api(self, messages: list, max_tokens: int = 150) -> Dict:
        """Make a call to the Perplexity API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.2,
                "top_p": 0.9,
                "stream": False,
            }

            response = requests.post(
                "https://api.perplexity.ai/chat/completions", headers=headers, json=data
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error calling Perplexity API: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def translate_text(self, text: str, target_language: str) -> Dict:
        """Translate text to target language."""
        try:
            messages = [
                {"role": "system", "content": "You are a precise translator."},
                {
                    "role": "user",
                    "content": f"Translate this to {target_language}: {text}",
                },
            ]

            result = self._call_perplexity_api(messages)
            if "error" in result:
                return {"error": result["error"]}

            translated_text = result["choices"][0]["message"]["content"]
            return {
                "original": text,
                "translated": translated_text,
                "target_language": target_language,
            }

        except Exception as e:
            logger.error(f"Translation error: {str(e)}", exc_info=True)
            return {"error": "Translation failed", "details": str(e)}

    def summarize_text(self, text: str, length: str = "medium") -> Dict:
        """Summarize text to specified length."""
        try:
            messages = [
                {"role": "system", "content": f"Provide a {length} length summary."},
                {"role": "user", "content": text},
            ]

            result = self._call_perplexity_api(messages)
            if "error" in result:
                return {"error": result["error"]}

            summary = result["choices"][0]["message"]["content"]
            return {"original": text, "summary": summary, "length": length}

        except Exception as e:
            logger.error(f"Summarization error: {str(e)}", exc_info=True)
            return {"error": "Summarization failed", "details": str(e)}

    def simplify_language(self, text: str, level: str = "medium") -> Dict:
        """Simplify text for better accessibility."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"Simplify this text to {level} complexity level.",
                },
                {"role": "user", "content": text},
            ]

            result = self._call_perplexity_api(messages)
            if "error" in result:
                return {"error": result["error"]}

            simplified = result["choices"][0]["message"]["content"]
            return {"original": text, "simplified": simplified, "level": level}

        except Exception as e:
            logger.error(f"Simplification error: {str(e)}", exc_info=True)
            return {"error": "Simplification failed", "details": str(e)}
