"""Text-to-Speech bridge module."""

import logging
import tempfile
import os
import shlex
import threading

logger = logging.getLogger(__name__)


def text_to_speech(text: str) -> str:
    """Convert text to speech and return audio file path.

    Args:
        text: Text to convert to speech

    Returns:
        str: Path to generated audio file, or None if failed
    """
    try:
        # macOS "say" command support
        if os.system("which say > /dev/null 2>&1") == 0:
            temp_file = tempfile.mktemp(suffix=".aiff")
            # Escape the text safely using shlex.quote
            safe_text = shlex.quote(text)
            command = f"say {safe_text} -o {shlex.quote(temp_file)}"
            result = os.system(command)

            if result == 0 and os.path.exists(temp_file):
                return temp_file

        # Fallback: log the text if no audio engine available
        logger.info(f"TTS: {text}")
        return None

    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None


def speak_response(text: str):
    """Convert text to speech and play it out loud."""
    audio_file = text_to_speech(text)
    if audio_file:
        try:
            # macOS playback with "afplay"
            if os.system("which afplay > /dev/null 2>&1") == 0:
                os.system(f"afplay {shlex.quote(audio_file)}")

                # Clean up temp file after playback
                def cleanup():
                    import time

                    time.sleep(2)
                    try:
                        os.remove(audio_file)
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file: {e}")

                threading.Thread(target=cleanup, daemon=True).start()
            else:
                logger.warning("afplay not available, cannot play audio")

        except Exception as e:
            logger.error(f"Error playing audio: {e}")

    else:
        # Always give a visible fallback in console
        print(f"[SPEECH]: {text}")


# ✅ Added alias so other modules can import consistently
def speak(text: str):
    """Alias for speak_response, for cleaner imports."""
    speak_response(text)
