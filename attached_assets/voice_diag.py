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
# /speech/voice_diag.py

import os
import sys
import sounddevice as sd

print("\n🧪 AlphaWolf Voice Diagnostic Starting\n")

# Check VOSK model path


def check_model_path():
    model_path = os.environ.get("VOSK_MODEL_PATH")
    if not model_path:
        print("❌ VOSK_MODEL_PATH not set.")
        return False
    if not os.path.exists(model_path):
        print(f"❌ Path does not exist: {model_path}")
        return False
    print(f"✅ VOSK_MODEL_PATH set and found: {model_path}")
    return True


# Check imports


def check_imports():
    try:
        import vosk

        print("✅ vosk import successful")
    except ImportError:
        print("❌ vosk not installed")

    try:
        import webrtcvad

        print("✅ webrtcvad import successful")
    except ImportError:
        print("❌ webrtcvad not installed")

    try:
        import pyttsx3

        engine = pyttsx3.init(driverName="nsss")
        engine.say("macOS voice engine confirmed working.")
        engine.runAndWait()
        print("✅ pyttsx3 (nsss) working on macOS")
    except ImportError:
        print("❌ pyttsx3 not installed")
    except Exception as e:
        print(f"❌ pyttsx3 error: {e}")


# Check mic access


def check_mic():
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d["max_input_channels"] > 0]
        if input_devices:
            print("✅ Microphone(s) found:")
            for idx, dev in enumerate(input_devices):
                print(f"   [{idx}] {dev['name']}")
        else:
            print("❌ No input devices found")
    except Exception as e:
        print(f"❌ Error accessing mic: {e}")


if __name__ == "__main__":
    check_model_path()
    check_imports()
    check_mic()
    print("\n✅ Diagnostic complete — review above results.")
