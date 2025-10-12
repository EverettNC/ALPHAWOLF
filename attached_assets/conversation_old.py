def generate_response(user_input):
    if "teach" in user_input.lower():
        return "Sure! Let's begin your lesson now."
    if "yes" in user_input.lower():
        return "Okay, confirming that."
    return "I'm still learning. Can you rephrase?"
