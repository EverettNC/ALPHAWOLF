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
# tts_bridge.py

import boto3
import os
import tempfile
import playsound  # pip install playsound==1.2.2

# Create Polly client
polly = boto3.client("polly")


def synthesize_speech(text):
    try:
        # Request speech synthesis
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Matthew",  # you can try "Joanna", "Amy", "Brian", etc.
        )

        # Write to a temporary file
        if "AudioStream" in response:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(response["AudioStream"].read())
                temp_filename = f.name

            # Play the audio
            playsound.playsound(temp_filename)

            # Cleanup
            os.remove(temp_filename)

        else:
            print("[TTS ERROR] No audio stream returned by Polly.")

    except Exception as e:
        print(f"[TTS ERROR] {str(e)}")
