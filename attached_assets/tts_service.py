"""
AlphaVox - Advanced TTS Service
-----------------------------
This module provides enhanced text-to-speech capabilities with simulated gender differentiation.
It uses gTTS with various TLD parameters to create different voice characteristics.

While this implementation doesn't provide true gender/voice-specific TTS like Coqui TTS would,
it offers a reasonable approximation by using different accent parameters and regional settings.

Key TLD parameters for gTTS that create different voice characteristics:
- 'us' - US English accent
- 'co.uk' - UK English accent
- 'ca' - Canadian English accent
- 'co.in' - Indian English accent
- 'com.au' - Australian English accent
- 'co.za' - South African English accent
- 'ie' - Irish English accent
"""

import logging
import os
import tempfile
import uuid
from typing import Any, Dict, Optional

from gtts import gTTS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def text_to_speech(
    text: str,
    voice_id: str = "calming",
    output_path: Optional[str] = None,
    lang: str = "en",
    slow: bool = False,
    rate: float = 1.0,
) -> str:
    """Generate speech from text using the appropriate TLD parameter for voice
    variation.

    Args:
        text: Text to convert to speech
        voice_id: Voice ID from the voice selector
        output_path: Optional path to save the audio file
        lang: Language code (defaults to 'en')
        slow: Speaking rate boolean flag (defaults to False)
        rate: Fine-grained speaking rate multiplier (defaults to 1.0)

    Returns:
        Path to the generated audio file
    """
    # Import the voice profiles from the application
    # We're doing this here to avoid circular imports
    from simple_app import AVAILABLE_VOICES

    # Find the selected voice or default to first one
    selected_voice = None
    for voice in AVAILABLE_VOICES:
        if voice["id"] == voice_id:
            selected_voice = voice
            break

    # Default to first voice if not found
    if not selected_voice and AVAILABLE_VOICES:
        selected_voice = AVAILABLE_VOICES[0]
        logger.warning(
            f"Voice {voice_id} not found, using default: {selected_voice['label']}"
        )

    # If we somehow still don't have a voice, use fallback settings
    if not selected_voice:
        selected_voice = {
            "id": "default",
            "label": "Default Voice",
            "tld": "com",
            "gender": "female",
        }

    # Log the selected voice
    logger.info(
        f"Using voice: {selected_voice['label']} (TLD: {selected_voice.get('tld', 'com')})"
    )

    # Apply voice-specific speed adjustments to enhance differentiation
    # Each voice can have slightly different speeds to enhance the perception of different voices
    voice_speed_adjustments = {
        "us_male": 0.95,  # Slightly slower for US male
        "uk_female": 1.0,  # Normal for UK female
        "calming": 0.9,  # Slower for calming voice
        "casual": 1.05,  # Slightly faster for casual
        "formal": 0.98,  # Slightly slower for formal
        "friendly_male": 1.0,  # Normal for friendly male
        "za_voice": 1.02,  # Slightly faster for South African
        "au_female": 1.05,  # Slightly faster for Australian
    }

    # Apply voice-specific speed adjustment to enhance the perception of different voices
    # This modifies the 'slow' parameter based on voice identity
    voice_id_for_speed = selected_voice.get("id", "default")
    voice_speed_factor = voice_speed_adjustments.get(voice_id_for_speed, 1.0)

    # For male voices, we slightly modify text to potentially change pitch perception
    # (this is subtle and relies on gTTS pronunciation quirks)
    if selected_voice.get("gender") == "male" and len(text) > 5:
        # Small text modifications that don't change meaning but might affect output
        if not text.endswith(".") and not text.endswith("?") and not text.endswith("!"):
            text = text + "."

    # Generate a unique filename if not provided
    if not output_path:
        filename = f"speech_{uuid.uuid4()}.mp3"
        output_path = os.path.join(tempfile.gettempdir(), filename)

    # Apply voice speed adjustment to the slow parameter
    # If the speed factor is below 0.92, use slow=True
    effective_slow = slow or (voice_speed_factor < 0.92)

    # Use the voice profile to generate speech
    tts = gTTS(
        text=text,
        lang=lang,
        slow=effective_slow,
        tld=selected_voice.get("tld", "com"),  # Use TLD for voice variation
    )

    # Save the audio file
    tts.save(output_path)
    logger.info(
        f"Generated speech with TLD {selected_voice.get('tld', 'com')}, speed factor {voice_speed_factor}: {output_path}"
    )

    return output_path


def get_voice_preview(
    voice_id: str, text: str = "Hello, this is a sample of my voice."
) -> str:
    """Generate a voice preview for the voice selector.

    Args:
        voice_id: Voice ID to preview
        text: Text to use for the preview

    Returns:
        Path to the generated audio file
    """
    # Generate a unique filename in the static voices directory
    filename = f"preview_{voice_id}_{uuid.uuid4()}.mp3"
    preview_dir = os.path.join(os.path.dirname(__file__), "static", "voices")

    # Create directory if it doesn't exist
    os.makedirs(preview_dir, exist_ok=True)

    output_path = os.path.join(preview_dir, filename)

    # Generate the preview
    return text_to_speech(text, voice_id, output_path)


def get_voice_description(voice_id: str) -> Dict[str, Any]:
    """Get description and properties for a specific voice.

    Args:
        voice_id: Voice ID to get information about

    Returns:
        Dictionary with voice properties
    """
    # Import the voice profiles from the application
    from simple_app import AVAILABLE_VOICES

    # Find the selected voice
    for voice in AVAILABLE_VOICES:
        if voice["id"] == voice_id:
            return voice

    # Return default if not found
    return {
        "id": voice_id,
        "label": f"Voice {voice_id}",
        "description": "Default voice",
        "gender": "neutral",
        "tld": "com",
    }
