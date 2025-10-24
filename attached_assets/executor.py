# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
# executor.py

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI not available")
    OPENAI_AVAILABLE = False


def ask_openai(prompt: str, context=None):
    """
    Ask OpenAI with v1.x interface or fallback to older interface if available.
    """
    if not OPENAI_AVAILABLE:
        logger.warning("OpenAI not available, using fallback response")
        return "I'm processing your request without external AI assistance. How can I best support you?"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return "I'm sorry — I'm not configured to think right now. Please set the OPENAI_API_KEY environment variable."

    try:
        # Try the new OpenAI client style
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are Derek, an AI assistant. Respond only to what the user actually says. Never assume what they were about to ask or claim to know their intentions.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=256,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return "I'm having trouble connecting to my advanced thinking module, but I'm still here to help."


def execute_task(text: str, intent: str, memory_context):
    """Execute a task based on user input and context."""
    try:
        # Create a contextual prompt for the LLM
        context_info = ""
        if isinstance(memory_context, dict) and "context" in memory_context:
            context_info = f" Context from memory: {memory_context['context'][:100]}..."

        prompt = f"User input: '{text}' (Intent: {intent}){context_info}. Please provide a helpful response."

        # Ask the model
        full_response = ask_openai(prompt, memory_context)

        # Optionally shorten for speech output (speak only first sentence)
        spoken_response = (
            full_response.split(".")[0].strip() + "."
            if "." in full_response
            else full_response.strip()
        )

        logger.info(f"Task executed for intent '{intent}'")
        return spoken_response

    except Exception as e:
        logger.error(f"Error executing task: {e}")
        return "I'm having some technical difficulties, but I'm here with you."
