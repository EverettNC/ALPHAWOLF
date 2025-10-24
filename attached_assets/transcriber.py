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
# /speech/transcriber.py
# Hybrid VOSK + AlphaVox Speech Recognition + AlphaWolf Brain Integration
# Adds "Hey AlphaWolf" wake word mode and Voice Activity Detection (VAD)
# Auto-detects model folder safely

import os
import sys
import json
import queue
import sounddevice as sd
import vosk
import webrtcvad
import time

# -------------------------------------------------------------
# Add project root to Python path BEFORE local imports
# -------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------------------------------------
# Now import AlphaWolf’s brain and TTS safely
# -------------------------------------------------------------
from tts_bridge import speak_response
from brain import alphawolf

# -------------------------------------------------------------
# Configuration (clean version — no extra validation)
# -------------------------------------------------------------
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEECH_DIR = os.path.join(PROJECT_ROOT, "speech")

# Direct path to your actual model folder
MODEL_PATH = os.path.join(SPEECH_DIR, "vosk-model-small-en-us-0.15")

# Tell Python to just use this path — no error checking
print(f"🎯 Loading Vosk model directly from: {MODEL_PATH}")

# Initialize the model directly (no if-checks, no fallback)
model = vosk.Model(MODEL_PATH)

# -------------------------------------------------------------
# Load custom AlphaVox vocabulary (optional)
# -------------------------------------------------------------
CUSTOM_VOCAB_PATH = os.path.join(PROJECT_ROOT, "speech", "vocab-alpha.json")
custom_vocab = {"terms": []}
if os.path.exists(CUSTOM_VOCAB_PATH):
    try:
        with open(CUSTOM_VOCAB_PATH, "r") as f:
            custom_vocab = json.load(f)
        print(f"📘 Loaded custom vocabulary ({len(custom_vocab.get('terms', []))} terms)")
    except Exception as e:
        print(f"⚠️ Failed to load custom vocab: {e}")
else:
    print("⚠️ No custom vocabulary found (optional).")

# -------------------------------------------------------------
# Audio + VAD setup
# -------------------------------------------------------------
SAMPLE_RATE = 16000
FRAME_DURATION = 30  # ms
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000) * 2

q = queue.Queue()
vad = webrtcvad.Vad(2)


def callback(indata, frames, time_info, status):
    if status:
        print(f"[Audio Warning] {status}", flush=True)
    q.put(bytes(indata))


# -------------------------------------------------------------
# Wake Word Detection
# -------------------------------------------------------------
WAKE_WORDS = ["hey derek", "okay derek", "hi derek"]


def detect_wake_word(text: str) -> bool:
    text = text.lower().strip()
    return any(ww in text for ww in WAKE_WORDS)


# -------------------------------------------------------------
# Passive Listening
# -------------------------------------------------------------
def passive_listen():
    """Idle mode — listens for 'Hey Derek' without responding to everything."""
    print("👂 Passive listening... (Say 'Hey Derek' to wake me)")
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    buffer = b""

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=FRAME_SIZE,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        while True:
            frame = q.get()
            buffer += frame

            if len(buffer) >= FRAME_SIZE:
                chunk = buffer[:FRAME_SIZE]
                buffer = buffer[FRAME_SIZE:]

                if vad.is_speech(chunk, SAMPLE_RATE):
                    rec.AcceptWaveform(chunk)
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        sys.stdout.write(f"\r🗣️ Heard: {text}     ")
                        sys.stdout.flush()

                        if detect_wake_word(text):
                            print("\n🚀 Wake word detected! Derek is listening...")
                            speak_response("Yes?")
                            active_listen()
                            print("👂 Back to passive listening...\n")
                            rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)


# -------------------------------------------------------------
# Active Listening
# -------------------------------------------------------------
def active_listen():
    """Active mode — listens for full sentences until silence is detected."""
    print("🎤 Active listening mode. Speak your command...")

    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    silence_counter = 0
    speaking = False
    buffer = b""

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=FRAME_SIZE,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        while True:
            frame = q.get()
            buffer += frame

            if len(buffer) >= FRAME_SIZE:
                chunk = buffer[:FRAME_SIZE]
                buffer = buffer[FRAME_SIZE:]
                speech_detected = vad.is_speech(chunk, SAMPLE_RATE)

                if speech_detected:
                    speaking = True
                    silence_counter = 0
                    rec.AcceptWaveform(chunk)
                else:
                    if speaking:
                        silence_counter += 1
                        # about 0.8s silence ends capture
                        if silence_counter > int(800 / FRAME_DURATION):
                            speaking = False
                            process_audio(rec)
                            return  # Go back to passive listening


# -------------------------------------------------------------
# Process Audio with Derek
# -------------------------------------------------------------
def process_audio(rec):
    """Send recognized speech to Derek’s brain and speak back."""
    result = json.loads(rec.FinalResult())
    text = result.get("text", "").strip()
    if not text:
        print("⚠️ No speech detected.")
        return

    corrected = postprocess(text)
    print(f"\n🧠 You said: {corrected}")

    try:
        print("🧩 Sending to Derek.think()...")
        response = derek.think(corrected)
        print(f"🧩 Derek.think() returned: {response}")

        reply = response.get("response", "I'm here.")
        print(f"🤖 Derek: {reply}\n")

        print("🔊 Sending to speak_response()...")
        speak_response(reply)
        print("✅ Finished TTS playback.")

    except Exception as e:
        print(f"⚠️ Derek response error: {e}")


# -------------------------------------------------------------
# Post-processing (fix misheard words)
# -------------------------------------------------------------
def postprocess(text):
    corrections = {
        "ice cream": "I scream",
        "help me now": "emergency help",
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    for term in custom_vocab.get("terms", []):
        alias = term.get("alias")
        canonical = term.get("canonical")
        if alias and canonical and alias in text:
            text = text.replace(alias, canonical)
    return text


# -------------------------------------------------------------
# Main Entry
# -------------------------------------------------------------
if __name__ == "__main__":
    try:
        passive_listen()
    except KeyboardInterrupt:
        print("\n🛑 Exiting voice system.")

