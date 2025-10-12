"""Basic intent detection module."""


def detect_intent(text: str) -> str:
    """Detect intent from input text."""
    text_lower = text.lower()

    if any(word in text_lower for word in ["hello", "hi", "hey"]):
        return "greeting"
    elif any(word in text_lower for word in ["bye", "goodbye", "see you"]):
        return "farewell"
    elif any(word in text_lower for word in ["help", "assist", "support"]):
        return "help"
    elif any(word in text_lower for word in ["what", "how", "when", "where", "why"]):
        return "question"
    else:
        return "general"
