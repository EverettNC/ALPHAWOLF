def analyze_emotion(user_data: dict) -> str:
    """
    Infer user emotion based on gesture repetition and error frequency.

    Args:
        user_data (dict): Contains 'gesture_score' (dict[str, int]) and 'recent_errors' (int)

    Returns:
        str: Inferred emotion state: 'confident', 'frustrated', or 'neutral'
    """
    score = 0
    gestures: dict = user_data.get("gesture_score", {})
    errors: int = user_data.get("recent_errors", 0)

    if not gestures:
        return "neutral"

    # Detect strong repetitive signals
    high_repeats = [g for g, count in gestures.items() if count >= 5]
    if len(high_repeats) >= 3:
        score += 1  # mastering gesture control

    # Detect error-driven struggle
    if errors >= 3:
        score -= 2  # frustration due to system or gesture failures

    # Infer emotional state
    if score <= -1:
        return "frustrated"
    elif score >= 2:
        return "confident"
    return "neutral"
