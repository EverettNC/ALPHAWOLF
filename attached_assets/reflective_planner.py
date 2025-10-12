"""Foundation for Derek's autonomous reflection and planning."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ReflectivePlanner:
    """Lightweight reflective loop seed.

    Records interactions with cues and can surface simple follow-up tasks.
    """

    def __init__(
        self, memory_engine, log_path: str = "logs/autonomy_reflections.jsonl"
    ) -> None:
        self.memory_engine = memory_engine
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record_interaction(
        self,
        user_input: str,
        response: str,
        intent: str,
        cues: List[str],
    ) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_input": user_input,
            "response": response,
            "intent": intent,
            "empathy_cues": cues,
            "tone_profile": self.memory_engine.get_tone_profile(),
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def suggest_follow_ups(self) -> List[str]:
        """Return lightweight next-step prompts Derek could pursue."""

        suggestions: List[str] = []
        profile = self.memory_engine.get_tone_profile()

        if profile.get("structure") == "guided":
            suggestions.append(
                "Prepare a concise, step-by-step explanation template for the current topic."
            )
        if profile.get("speech_rate", 180) < 150:
            suggestions.append(
                "Evaluate pacing adjustments after the next few interactions to confirm clarity."
            )
        if not suggestions:
            suggestions.append(
                "Review recent learnings and identify one improvement opportunity for speech tone."
            )

        return suggestions
