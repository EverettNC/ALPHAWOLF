"""Utility helpers for Derek's autonomous learning."""

from __future__ import annotations

import logging
import re
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"
)


def _summarize_text(text: str, max_sentences: int = 3) -> str:
    """Very lightweight summariser by taking the first few sentences."""

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    summary = " ".join(sentences[:max_sentences]).strip()
    return summary or text[:300].strip()


def fetch_and_summarize(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Fetch a web page and extract a short summary and topic."""

    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
    except Exception as exc:  # pragma: no cover - network defensive block
        logger.error("Failed to retrieve %s: %s", url, exc)
        return None, None

    soup = BeautifulSoup(resp.text, "html.parser")
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    content = " ".join(paragraphs[:20])

    if not content:
        logger.warning("No textual content found at %s", url)
        return None, None

    summary = _summarize_text(content)
    topic = soup.title.string.strip() if soup.title and soup.title.string else "General"
    return summary, topic
