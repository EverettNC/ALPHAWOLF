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
import logging
import os
import queue
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import sounddevice as sd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

AUDIO_SAMPLE_RATE = 16000
MIN_SPEECH_DURATION = 0.5
SILENCE_THRESHOLD = 0.1
AUDIO_CACHE_DIR = "audio_cache"

if not os.path.exists(AUDIO_CACHE_DIR):
    os.makedirs(AUDIO_CACHE_DIR)


class RealSpeechRecognitionEngine:
    def __init__(self, language: str = "en-US"):
        self.language = language
        self.is_listening = False
        self.callbacks = []
        self.audio_buffer = []
        self.last_speech_time = 0
        self.silence_threshold = SILENCE_THRESHOLD
        self.min_speech_duration = MIN_SPEECH_DURATION
        self.audio_queue = queue.Queue()

        self.devices = sd.query_devices()
        logger.info(f"Available audio devices: {len(self.devices)}")
        for i, device in enumerate(self.devices):
            logger.info(f"Device {i}: {device['name']}")

        self.input_device = next(
            (i for i, d in enumerate(self.devices) if d["max_input_channels"] > 0), None
        )
        if self.input_device is None:
            logger.warning("No suitable input device found, using default")
            self.input_device = sd.default.device[0]

        logger.info(
            f"Real Speech Recognition Engine initialized with language: {language}"
        )

    def start_listening(self, callback: Optional[Callable] = None) -> bool:
        if self.is_listening:
            logger.warning("Speech recognition is already active")
            return False

        if callback:
            self.callbacks.append(callback)

        self.is_listening = True
        self._start_audio_processing_thread()

        try:
            self.stream = sd.InputStream(
                samplerate=AUDIO_SAMPLE_RATE,
                channels=1,
                callback=self._audio_callback,
                device=self.input_device,
            )
            self.stream.start()
            logger.info("Started audio stream from microphone")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            self.is_listening = False
            return False

        logger.info("Real speech recognition started")
        return True

    def stop_listening(self) -> bool:
        if not self.is_listening:
            logger.warning("Speech recognition is not active")
            return False

        self.is_listening = False
        if hasattr(self, "stream"):
            self.stream.stop()
            self.stream.close()

        logger.info("Real speech recognition stopped")
        return True

    def _audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())

    def _start_audio_processing_thread(self):
        thread = threading.Thread(target=self._audio_processing_loop)
        thread.daemon = True
        thread.start()

    def _audio_processing_loop(self):
        try:
            while self.is_listening:
                try:
                    audio_chunk = self.audio_queue.get(timeout=1.0)
                    self._process_audio_chunk(audio_chunk)
                except queue.Empty:
                    continue
        except Exception as e:
            logger.error(f"Error in audio processing loop: {e}")
            self.is_listening = False

    def _process_audio_chunk(self, audio_chunk: np.ndarray):
        self.audio_buffer.append(audio_chunk.flatten())

        max_buffer_size = int(AUDIO_SAMPLE_RATE * 5)
        total_samples = sum(len(chunk) for chunk in self.audio_buffer)
        while total_samples > max_buffer_size and self.audio_buffer:
            removed = self.audio_buffer.pop(0)
            total_samples -= len(removed)

        if self._detect_speech(audio_chunk):
            self.last_speech_time = time.time()
            if self._check_speech_duration():
                combined_audio = np.concatenate(self.audio_buffer)
                text, confidence, metadata = self._process_speech(combined_audio)
                if text:
                    for callback in self.callbacks:
                        callback(text, confidence, metadata)
                    self.audio_buffer = []

    def _detect_speech(self, audio_chunk: np.ndarray) -> bool:
        energy = np.mean(np.abs(audio_chunk))
        return energy > self.silence_threshold

    def _check_speech_duration(self) -> bool:
        if not self.audio_buffer:
            return False
        return (time.time() - self.last_speech_time) > self.min_speech_duration

    def _process_speech(
        self, audio_data: np.ndarray
    ) -> Tuple[str, float, Dict[str, Any]]:
        frame_size = int(AUDIO_SAMPLE_RATE * 0.02)
        frames = [
            audio_data[i : i + frame_size]
            for i in range(0, len(audio_data), frame_size)
        ]
        energies = [
            np.mean(np.abs(frame)) for frame in frames if len(frame) == frame_size
        ]

        if not energies:
            return "", 0.0, {"error": "No audio data"}

        avg_energy = np.mean(energies)
        energy_variance = np.var(energies)
        zero_crossings = sum(
            1
            for i in range(1, len(audio_data))
            if audio_data[i - 1] * audio_data[i] < 0
        )
        zero_crossing_rate = zero_crossings / len(audio_data)

        if avg_energy > self.silence_threshold * 2 and energy_variance > 0.001:
            text = (
                "I detected speech but need a speech recognition API to understand it."
            )
            confidence = min(max(avg_energy / (self.silence_threshold * 4), 0.1), 0.9)
            logger.info(
                f"Speech detected: Energy={avg_energy:.4f}, Confidence={confidence:.2f}"
            )
            return (
                text,
                confidence,
                {
                    "language": self.language,
                    "duration": len(audio_data) / AUDIO_SAMPLE_RATE,
                    "timestamp": time.time(),
                    "audio_features": {
                        "energy": float(avg_energy),
                        "variance": float(energy_variance),
                        "zero_crossing_rate": float(zero_crossing_rate),
                    },
                },
            )
        return "", 0.0, {"error": "No clear speech detected"}

    def set_language(self, language: str) -> bool:
        self.language = language
        logger.info(f"Recognition language set to: {language}")
        return True

    def adjust_sensitivity(
        self, silence_threshold: float, min_speech_duration: float
    ) -> bool:
        if silence_threshold <= 0 or min_speech_duration <= 0:
            logger.error("Invalid sensitivity parameters")
            return False

        self.silence_threshold = silence_threshold
        self.min_speech_duration = min_speech_duration
        logger.info(
            f"Sensitivity adjusted: threshold={silence_threshold}, duration={min_speech_duration}"
        )
        return True

    def get_audio_devices(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": i,
                "name": device["name"],
                "channels": device["max_input_channels"],
                "default": i == sd.default.device[0],
            }
            for i, device in enumerate(self.devices)
            if device["max_input_channels"] > 0
        ]

    def set_input_device(self, device_id: int) -> bool:
        if device_id < 0 or device_id >= len(self.devices):
            logger.error(f"Invalid device ID: {device_id}")
            return False
        if self.devices[device_id]["max_input_channels"] <= 0:
            logger.error(f"Device {device_id} has no input channels")
            return False

        was_listening = self.is_listening
        if was_listening:
            self.stop_listening()

        self.input_device = device_id
        logger.info(
            f"Input device set to {device_id}: {self.devices[device_id]['name']}"
        )

        if was_listening:
            self.start_listening()
        return True


_real_speech_recognition_engine = None


def get_real_speech_recognition_engine() -> RealSpeechRecognitionEngine:
    global _real_speech_recognition_engine
    if _real_speech_recognition_engine is None:
        _real_speech_recognition_engine = RealSpeechRecognitionEngine()
    return _real_speech_recognition_engine
