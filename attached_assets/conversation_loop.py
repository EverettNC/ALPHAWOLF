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
"""
Conversation Loop for Derek
The Christman AI Project - Speech-to-Action Core
------------------------------------------------
Listens for speech, processes it via Derek’s brain, and replies with speech.
"""

import os
import sys
import time
import logging

# -------------------------------------------------------------
# Ensure project root is in path for imports
# -------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------------------------------------
# Imports from the alphawolf system
# -------------------------------------------------------------
from brain import derek
from tts_bridge import speak_response as speak
from executor import execute_task
from memory_engine import MemoryEngine
from speech_recognition_engine import SpeechRecognitionEngine

# -------------------------------------------------------------
# Initialize components
# -------------------------------------------------------------
logger = logging.getLogger("conversation_loop")
memory = MemoryEngine()
engine = SpeechRecognitionEngine()  # main speech engine

# -------------------------------------------------------------
# Handle recognized speech
# -------------------------------------------------------------
def handle_recognition(text, confidence, meta=None):
    """Callback executed when speech is recognized."""
    if not text or confidence < 0.2:
        print("❌ No clear speech recognized.")
        speak("I didn’t catch that clearly. Could you please repeat it?")
        return

    print(f"\n👤 You: {text}  (confidence: {confidence:.2f})")

    try:
        # Load Derek's context memory
        memory.load()
        context = memory.get_context()

        # Get Derek’s thought process
        response = derek.think(text)
        intent = response.get("intent", "general")

        # Execute the intent / generate reply
        reply = execute_task(text, intent, context)

        print(f"🤖 Derek: {reply}")
        speak(reply)

    except Exception as e:
        logger.error(f"Error in handle_recognition: {e}", exc_info=True)
        speak("I encountered an internal issue while processing that.")

# -------------------------------------------------------------
# Main conversation loop
# -------------------------------------------------------------
def run_conversation():
    """Continuously listen for speech and process commands."""
    print("🎙️ AlphaWolf is now live and listening...")
    try:
        # Start listening via the engine
        engine.start_listening(callback=handle_recognition)

        # Keep alive until interrupted
        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n🛑 Conversation manually stopped.")
        engine.stop_listening()
        speak("Conversation ended. Goodbye.")

    except Exception as e:
        logger.error(f"Conversation loop crashed: {e}", exc_info=True)
        speak("There was an error in the conversation system.")

# -------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------
if __name__ == "__main__":
    run_conversation()

