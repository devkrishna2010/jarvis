"""
J.A.R.V.I.S. — Voice Input
Offline Speech Recognition using Vosk and sounddevice.
Operates 100% locally with low CPU and memory footprint (< 100 MB).
"""

import os
import sys
import json
import queue
import time
from typing import Optional

import sounddevice as sd
from vosk import Model, KaldiRecognizer

import config

_model_instance: Optional[Model] = None
_audio_queue = queue.Queue()


def get_vosk_model() -> Model:
    """Singleton getter for Vosk model to prevent loading it multiple times."""
    global _model_instance
    if _model_instance is None:
        model_path = os.path.abspath(config.VOSK_MODEL_PATH)
        if not os.path.isdir(model_path):
            raise FileNotFoundError(f"Vosk model not found at: {model_path}")
        _model_instance = Model(model_path)
    return _model_instance


def _audio_callback(indata, frames, time_info, status):
    """Callback from sounddevice audio input stream."""
    if status and config.ENABLE_DEBUG_PRINTS:
        print(f"[VoiceInput Warning]: {status}", file=sys.stderr)
    _audio_queue.put(bytes(indata))


def listen_phrase(timeout_sec: float = 8.0, silence_threshold_sec: float = 1.5) -> str:
    """
    Listens to microphone until a complete phrase is recognized or timeout occurs.
    
    Returns:
    - Transcribed text string (lowercase), or empty string if nothing heard.
    """
    if not config.ENABLE_VOICE_INPUT:
        return input("Enter command: ").strip().lower()

    model = get_vosk_model()
    recognizer = KaldiRecognizer(model, config.VOSK_SAMPLE_RATE)
    recognizer.SetWords(False)

    # Clear old queue contents
    while not _audio_queue.empty():
        try:
            _audio_queue.get_nowait()
        except queue.Empty:
            break

    start_time = time.time()
    last_audio_activity = time.time()
    heard_partial = False

    try:
        with sd.RawInputStream(
            samplerate=config.VOSK_SAMPLE_RATE,
            blocksize=4000,
            dtype='int16',
            channels=1,
            callback=_audio_callback
        ):
            if config.ENABLE_DEBUG_PRINTS:
                print(f"[{config.JARVIS_NAME} Listening...]")

            while True:
                now = time.time()
                if timeout_sec and (now - start_time) > timeout_sec:
                    break

                try:
                    data = _audio_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(data):
                    res = json.loads(recognizer.Result())
                    text = res.get("text", "").strip()
                    if text:
                        return text.lower()
                else:
                    partial = json.loads(recognizer.PartialResult())
                    p_text = partial.get("partial", "").strip()
                    if p_text:
                        heard_partial = True
                        last_audio_activity = now

                # Silence timeout after speech began
                if heard_partial and (now - last_audio_activity) > silence_threshold_sec:
                    final_res = json.loads(recognizer.FinalResult())
                    return final_res.get("text", "").strip().lower()

    except Exception as e:
        if config.ENABLE_DEBUG_PRINTS:
            print(f"[VoiceInput Error]: {e}", file=sys.stderr)
        # Fallback to console input if mic is blocked or fails
        return input("Microphone unavailable. Type command: ").strip().lower()

    final_res = json.loads(recognizer.FinalResult())
    return final_res.get("text", "").strip().lower()


def listen_wake_word(wake_word: Optional[str] = None, timeout_sec: Optional[float] = None) -> bool:
    """
    Listens specifically for the wake word (e.g. 'jarvis').
    Returns True when wake word is detected.
    """
    target = (wake_word or config.WAKE_WORD).lower()
    phrase = listen_phrase(timeout_sec=timeout_sec or 10.0, silence_threshold_sec=1.0)
    return target in phrase


if __name__ == "__main__":
    print("Testing core/voice_input.py...")
    print("Say something into your microphone (e.g. 'Jarvis' or 'Hello')...")
    result = listen_phrase(timeout_sec=5.0)
    print(f"Heard: '{result}'")

