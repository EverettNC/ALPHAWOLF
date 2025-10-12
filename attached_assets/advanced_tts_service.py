import hashlib
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from flask import Flask, jsonify, send_file
from gtts import gTTS

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

AVAILABLE_VOICES = [
    {
        "id": "us_female",
        "label": "US Female",
        "description": "Standard US English female voice",
        "gender": "female",
        "tld": "us",
        "emotion_adaptability": 0.9,
        "age_category": "adult",
    },
    {
        "id": "us_male",
        "label": "US Male",
        "description": "Standard US English male voice (simulated)",
        "gender": "male",
        "tld": "us",
        "emotion_adaptability": 0.85,
        "age_category": "adult",
    },
    {
        "id": "uk_female",
        "label": "UK Female",
        "description": "British English female voice",
        "gender": "female",
        "tld": "co.uk",
        "emotion_adaptability": 0.9,
        "age_category": "adult",
    },
    {
        "id": "uk_male",
        "label": "UK Male",
        "description": "British English male voice (simulated)",
        "gender": "male",
        "tld": "co.uk",
        "emotion_adaptability": 0.85,
        "age_category": "adult",
    },
    {
        "id": "calming",
        "label": "Calming Voice",
        "description": "Slower, gentle voice good for anxiety reduction",
        "gender": "female",
        "tld": "ca",
        "emotion_adaptability": 0.95,
        "age_category": "adult",
    },
    {
        "id": "casual",
        "label": "Casual Voice",
        "description": "Relaxed, slightly faster conversational tone",
        "gender": "female",
        "tld": "com.au",
        "emotion_adaptability": 0.9,
        "age_category": "young_adult",
    },
    {
        "id": "formal",
        "label": "Formal Voice",
        "description": "Precise, professional tone",
        "gender": "female",
        "tld": "co.in",
        "emotion_adaptability": 0.8,
        "age_category": "adult",
    },
    {
        "id": "friendly_male",
        "label": "Friendly Male",
        "description": "Warm, approachable male voice (simulated)",
        "gender": "male",
        "tld": "ie",
        "emotion_adaptability": 0.9,
        "age_category": "adult",
    },
    {
        "id": "za_voice",
        "label": "South African",
        "description": "South African accent (gender-neutral)",
        "gender": "neutral",
        "tld": "co.za",
        "emotion_adaptability": 0.85,
        "age_category": "adult",
    },
    {
        "id": "au_female",
        "label": "Australian Female",
        "description": "Australian English female voice",
        "gender": "female",
        "tld": "com.au",
        "emotion_adaptability": 0.9,
        "age_category": "adult",
    },
]


def text_to_speech(
    text: str,
    voice_id: str = "calming",
    output_path: Optional[str] = None,
    lang: str = "en",
    slow: bool = False,
    rate: float = 1.0,
) -> str:
    selected_voice = None
    for voice in AVAILABLE_VOICES:
        if voice["id"] == voice_id:
            selected_voice = voice
            break

    if not selected_voice and AVAILABLE_VOICES:
        selected_voice = AVAILABLE_VOICES[0]
        logger.warning(
            f"Voice {voice_id} not found, using default: {selected_voice['label']}"
        )

    if not selected_voice:
        selected_voice = {
            "id": "default",
            "label": "Default Voice",
            "tld": "com",
            "gender": "female",
        }

    voice_speed_adjustments = {
        "us_male": 0.95,
        "uk_female": 1.0,
        "calming": 0.9,
        "casual": 1.05,
        "formal": 0.98,
        "friendly_male": 1.0,
        "za_voice": 1.02,
        "au_female": 1.05,
    }

    voice_id_for_speed = selected_voice.get("id", "default")
    voice_speed_factor = voice_speed_adjustments.get(voice_id_for_speed, 1.0)
    effective_speed_factor = voice_speed_factor * rate

    if selected_voice.get("gender") == "male" and len(text) > 5:
        if not text.endswith(".") and not text.endswith("?") and not text.endswith("!"):
            text = text + "."

    if not output_path:
        audio_dir = os.path.join(os.getcwd(), "static", "audio")
        os.makedirs(audio_dir, exist_ok=True)
        content_hash = hashlib.md5(
            f"{text}|{voice_id}|{lang}|{slow}|{rate}".encode()
        ).hexdigest()
        filename = f"{content_hash}.mp3"
        output_path = os.path.join(audio_dir, filename)

        if os.path.exists(output_path):
            return output_path

    effective_slow = slow or (effective_speed_factor < 0.92)

    tts = gTTS(
        text=text, lang=lang, slow=effective_slow, tld=selected_voice.get("tld", "com")
    )

    tts.save(output_path)
    return output_path


def text_to_speech_with_emotion(
    text: str,
    emotion: Optional[str] = None,
    emotion_tier: Optional[str] = None,
    voice_id: str = "calming",
    output_path: Optional[str] = None,
    lang: str = "en",
) -> str:
    rate = 1.0
    slow = False

    if emotion and emotion_tier:
        emotion_rates = {
            "positive": {"mild": 1.05, "moderate": 1.1, "strong": 1.15, "urgent": 1.2},
            "negative": {"mild": 0.95, "moderate": 0.9, "strong": 0.85, "urgent": 0.8},
            "neutral": {"mild": 1.0, "moderate": 1.0, "strong": 1.0, "urgent": 1.1},
            "questioning": {
                "mild": 1.0,
                "moderate": 0.95,
                "strong": 0.9,
                "urgent": 0.85,
            },
        }
        if emotion in emotion_rates and emotion_tier in emotion_rates[emotion]:
            rate = emotion_rates[emotion][emotion_tier]

    return text_to_speech(text, voice_id, output_path, lang, slow, rate)


def get_voice_preview(
    voice_id: str, text: str = "Hello, this is a sample of my voice."
) -> str:
    preview_dir = os.path.join(os.getcwd(), "static", "voices")
    os.makedirs(preview_dir, exist_ok=True)
    content_hash = hashlib.md5(f"preview_{voice_id}_{text}".encode()).hexdigest()
    filename = f"preview_{voice_id}_{content_hash}.mp3"
    output_path = os.path.join(preview_dir, filename)

    if not os.path.exists(output_path):
        return text_to_speech(text, voice_id, output_path)
    return output_path


def get_voice_description(voice_id: str) -> Dict[str, Any]:
    for voice in AVAILABLE_VOICES:
        if voice["id"] == voice_id:
            return voice
    return {
        "id": voice_id,
        "label": f"Voice {voice_id}",
        "description": "Default voice",
        "gender": "neutral",
        "tld": "com",
    }


def get_all_voices() -> list:
    return AVAILABLE_VOICES


def get_voice_for_emotion(
    emotion: str, gender_preference: Optional[str] = None
) -> Dict[str, Any]:
    emotion_voice_map = {
        "positive": ["casual", "friendly_male", "au_female"],
        "negative": ["formal", "uk_male"],
        "neutral": ["us_female", "uk_female"],
        "calming": ["calming", "uk_female"],
        "urgent": ["us_male", "formal"],
        "questioning": ["uk_female", "us_female"],
    }
    voice_options = emotion_voice_map.get(emotion, emotion_voice_map["neutral"])

    if gender_preference:
        gender_match_voices = []
        for voice_id in voice_options:
            voice = get_voice_description(voice_id)
            if voice["gender"] == gender_preference:
                gender_match_voices.append(voice_id)
        if gender_match_voices:
            voice_options = gender_match_voices

    selected_voice_id = voice_options[0]
    return get_voice_description(selected_voice_id)


app = Flask(__name__)


@app.route("/")
def index():
    return send_file("static/index.html")


@app.route("/generate_greeting", methods=["GET"])
def generate_greeting():
    text = "Hello, welcome to the app!"
    voice_id = "calming"
    audio_path = text_to_speech(text, voice_id)
    return jsonify({"audio_url": f"/audio/{os.path.basename(audio_path)}"})


@app.route("/audio/<filename>")
def serve_audio(filename):
    audio_path = os.path.join("static", "audio", filename)
    return send_file(audio_path, mimetype="audio/mpeg")


@app.route("/voices", methods=["GET"])
def list_voices():
    """List all available voices."""
    return jsonify(get_all_voices())


@app.route("/voice/<voice_id>/description", methods=["GET"])
def voice_description(voice_id):
    """Get metadata for a specific voice."""
    return jsonify(get_voice_description(voice_id))


@app.route("/voice/<voice_id>/preview", methods=["GET"])
def voice_preview(voice_id):
    """Generate or retrieve a preview audio file for a voice."""
    filename = os.path.basename(get_voice_preview(voice_id))
    return jsonify({"audio_url": f"/voices/audio/{filename}"})


@app.route("/voices/audio/<filename>", methods=["GET"])
def serve_voice_audio(filename):
    """Serve voice preview audio files."""
    path = os.path.join("static", "voices", filename)
    return send_file(path, mimetype="audio/mpeg")


@app.route("/status", methods=["GET"])
def status():
    """Health check: TTS service availability"""
    return jsonify(
        {
            "voices_loaded": len(AVAILABLE_VOICES),
            "last_update": datetime.now().isoformat(),
        }
    )


if __name__ == "__main__":
    print("Available voices:")
    for v in get_all_voices():
        print(f" - {v['id']}: {v['label']}")
    app.run(debug=True)
