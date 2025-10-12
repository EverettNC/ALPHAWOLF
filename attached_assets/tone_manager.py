"""Tone and empathy management helpers for Derek."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


def _ensure_profile_defaults(profile: Dict[str, any]) -> Dict[str, any]:
    profile.setdefault("speech_rate", 180)
    profile.setdefault("volume", 1.0)
    profile.setdefault("warmth", "balanced")
    profile.setdefault("structure", "concise")
    profile.setdefault("mirroring", True)
    return profile


def analyse_user_text(
    text: str, profile: Dict[str, any]
) -> Tuple[Dict[str, any], List[str]]:
    """Derive tone adjustments and empathy cues from user input."""

    profile = _ensure_profile_defaults(profile)
    text_lower = text.lower()
    updates: Dict[str, any] = {}
    cues: List[str] = []

    if any(
        phrase in text_lower
        for phrase in ["can't hear", "cannot hear", "hard to hear", "slow down"]
    ):
        new_rate = max(120, int(profile.get("speech_rate", 180) * 0.85))
        updates["speech_rate"] = new_rate
        cues.append("hearing_support")

    if any(
        word in text_lower
        for word in ["confused", "don't understand", "lost", "not sure"]
    ):
        updates["structure"] = "guided"
        updates["warmth"] = "reassuring"
        cues.append("confusion")

    if any(word in text_lower for word in ["good", "great", "awesome", "excited"]):
        updates.setdefault("warmth", "uplifting")
        cues.append("positive_affect")

    return updates, cues


def format_response(base_text: str, cues: List[str], profile: Dict[str, any]) -> str:
    """Apply empathy wrappers and structure adjustments to Derek's reply."""

    profile = _ensure_profile_defaults(profile)
    intro_parts: List[str] = []

    if "hearing_support" in cues:
        intro_parts.append(
            "Thanks for letting me know—I'll keep things clear and steady."
        )
    if "confusion" in cues:
        intro_parts.append("Let me break that down so it feels simpler.")
    if "positive_affect" in cues and profile.get("warmth") == "uplifting":
        intro_parts.append("I love the energy you're bringing!")

    body = base_text
    if profile.get("structure") == "guided":
        body = _structure_response(body)

    if intro_parts:
        return " ".join(intro_parts) + "\n\n" + body
    return body


def _structure_response(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s for s in sentences if s]
    if len(sentences) <= 2:
        return text
    return "\n".join(f"• {s}" for s in sentences)


def extract_speech_controls(profile: Dict[str, any]) -> Dict[str, any]:
    profile = _ensure_profile_defaults(profile)
    return {
        "speech_rate": profile.get("speech_rate", 180),
        "volume": profile.get("volume", 1.0),
    }
