# speech/speech_response.py

import pyttsx3
import logging

logger = logging.getLogger(__name__)

try:
    engine = pyttsx3.init(driverName="nsss")  # macOS driver
    engine.setProperty("rate", 180)
    engine.setProperty("volume", 1.0)
except Exception as e:
    engine = None
    logger.warning(f"Speech engine init failed: {e}")


def speak(text, tone_profile=None):
    print(f"🗣️ Speaking response: {text}")
    if not engine:
        print("❌ Speech engine not available.")
        return

    original_rate = engine.getProperty("rate")
    original_volume = engine.getProperty("volume")

    try:
        if tone_profile:
            rate = tone_profile.get("speech_rate")
            if rate:
                engine.setProperty("rate", rate)
            volume = tone_profile.get("volume")
            if volume is not None:
                engine.setProperty("volume", volume)

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"❌ Failed to speak: {e}")
    finally:
        if tone_profile:
            engine.setProperty("rate", original_rate)
            engine.setProperty("volume", original_volume)
