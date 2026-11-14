"""
J.A.R.V.I.S. — Real-Time Vocal & Semantic Emotion Detection Engine (Phase 9)
Analyzes user input across 5 affective dimensions:
- happy / excited
- angry / frustrated
- sad / exhausted
- freaky / panicked / anxious
- neutral / composed

Adjusts acoustic parameters and conversational framing in real-time.
"""

import re
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

import config
from voice.voice_profiles import VoiceProfile, PROFILES


@dataclass
class EmotionResult:
    primary_emotion: str
    confidence: float
    valence: float          # -1.0 (very negative) to +1.0 (very positive)
    arousal: float          # 0.0 (calm/low energy) to 1.0 (high excitement/intensity)
    suggested_voice_style: str
    empathetic_note: str


# Semantic Lexicons
HAPPY_KEYWORDS = [
    "happy", "great", "awesome", "fantastic", "amazing", "wonderful", "love it",
    "brilliant", "yay", "celebrate", "excellent", "perfect", "good job", "super",
    "thrilled", "excited", "hurray", "winning", "success", "delighted"
]

ANGRY_KEYWORDS = [
    "angry", "mad", "furious", "hate", "damn", "annoyed", "pissed", "stupid",
    "ridiculous", "shut up", "broken", "terrible", "worst", "screwed", "crap",
    "frustrated", "irritated", "fail", "useless", "garbage"
]

SAD_KEYWORDS = [
    "sad", "depressed", "unhappy", "tired", "exhausted", "down", "lonely",
    "miserable", "hurt", "hopeless", "gloomy", "crying", "sorrow", "giving up",
    "weary", "drained", "bad day", "rough day", "heavy"
]

FREAKY_KEYWORDS = [
    "freaking out", "freak", "freaky", "panic", "panicking", "scared", "terrified",
    "emergency", "hurry", "quick", "danger", "omg", "urgent", "help me", "nervous",
    "anxious", "stressing", "stressed", "nightmare", "crisis"
]


class EmotionDetector:
    def __init__(self):
        # Register emotion-specific voice profiles if not already present
        self._register_emotion_profiles()

    def _register_emotion_profiles(self):
        """Adds custom emotional acoustic profiles to PROFILES catalog."""
        # 1. Empathetic Soothing (for sad/tired)
        PROFILES["soothing"] = VoiceProfile(
            name="soothing",
            length_scale=1.15,
            noise_scale=0.30,
            noise_w=0.46,
            sentence_silence=0.28,
            eq_80_100_db=2.5,
            eq_120_160_db=3.5,
            eq_200_250_db=1.0,
            eq_300_400_db=-1.0,
            eq_2k_4k_db=-0.5,
            ambience_mix=0.06,
            stereo_spread=0.10,
            master_gain=0.90,
            limiter_ceiling=0.92,
            add_breath=True,
        )

        # 2. De-escalating Stoic (for angry/frustrated)
        PROFILES["composed"] = VoiceProfile(
            name="composed",
            length_scale=1.12,
            noise_scale=0.32,
            noise_w=0.48,
            sentence_silence=0.25,
            eq_80_100_db=3.0,
            eq_120_160_db=3.5,
            eq_200_250_db=1.5,
            eq_300_400_db=-1.5,
            eq_2k_4k_db=0.0,
            ambience_mix=0.08,
            stereo_spread=0.12,
            master_gain=0.94,
            limiter_ceiling=0.95,
            add_breath=True,
        )

        # 3. Urgent Triage Reassuring (for freaky/panicked)
        PROFILES["triage"] = VoiceProfile(
            name="triage",
            length_scale=0.98,
            noise_scale=0.28,
            noise_w=0.45,
            sentence_silence=0.14,
            eq_80_100_db=1.0,
            eq_120_160_db=2.0,
            eq_200_250_db=0.5,
            eq_300_400_db=-1.0,
            eq_2k_4k_db=1.8,
            ambience_mix=0.02,
            stereo_spread=0.04,
            master_gain=0.98,
            limiter_ceiling=0.96,
            add_breath=False,
        )

    def analyze_audio_prosody(self, audio_data: Optional[np.ndarray], sample_rate: int = 16000) -> Dict[str, float]:
        """Calculates RMS energy, pitch proxy (zero-crossings) from raw microphone frames."""
        if audio_data is None or len(audio_data) == 0:
            return {"rms": 0.05, "zcr": 0.05}

        samples = audio_data.astype(np.float32)
        rms = float(np.sqrt(np.mean(samples ** 2)))
        zero_crossings = float(np.mean(np.abs(np.diff(np.sign(samples)))) / 2.0)
        return {"rms": rms, "zcr": zero_crossings}

    def detect_emotion(
        self,
        text: str,
        audio_data: Optional[np.ndarray] = None,
        sample_rate: int = 16000
    ) -> EmotionResult:
        """
        Combines lexical sentiment and prosodic cues to determine user affect.
        """
        low = text.lower().strip()
        prosody = self.analyze_audio_prosody(audio_data, sample_rate)

        scores = {
            "happy": 0.0,
            "angry": 0.0,
            "sad": 0.0,
            "freaky": 0.0,
            "neutral": 0.15
        }

        # 1. Lexical Scoring
        for word in HAPPY_KEYWORDS:
            if re.search(rf"\b{re.escape(word)}\b", low):
                scores["happy"] += 0.45

        for word in ANGRY_KEYWORDS:
            if re.search(rf"\b{re.escape(word)}\b", low):
                scores["angry"] += 0.50

        for word in SAD_KEYWORDS:
            if re.search(rf"\b{re.escape(word)}\b", low):
                scores["sad"] += 0.45

        for word in FREAKY_KEYWORDS:
            if re.search(rf"\b{re.escape(word)}\b", low):
                scores["freaky"] += 0.55

        # Punctuation & casing signals
        if "!" in text:
            scores["happy"] += 0.2
            scores["angry"] += 0.2
            scores["freaky"] += 0.25
        if text.isupper() and len(text) > 4:
            scores["angry"] += 0.4
            scores["freaky"] += 0.35

        # Prosody influence
        if prosody["rms"] > 0.15:
            scores["angry"] += 0.25
            scores["freaky"] += 0.20
        elif prosody["rms"] < 0.02 and scores["sad"] > 0.0:
            scores["sad"] += 0.30

        # Determine dominant emotion
        dominant = max(scores, key=scores.get)
        confidence = min(0.98, max(0.40, scores[dominant]))

        # Mapping to voice profile & empathetic framing
        if dominant == "happy":
            return EmotionResult(
                primary_emotion="happy",
                confidence=confidence,
                valence=0.8,
                arousal=0.7,
                suggested_voice_style="witty",
                empathetic_note="A pleasure to hear you in high spirits, Dev."
            )
        elif dominant == "angry":
            return EmotionResult(
                primary_emotion="angry",
                confidence=confidence,
                valence=-0.7,
                arousal=0.8,
                suggested_voice_style="composed",
                empathetic_note="Allow me to take care of the details, Dev. Staying calm will serve us better, sir."
            )
        elif dominant == "sad":
            return EmotionResult(
                primary_emotion="sad",
                confidence=confidence,
                valence=-0.8,
                arousal=0.2,
                suggested_voice_style="soothing",
                empathetic_note="You sound weary, Dev. I have taken the liberty of streamlining everything on my end."
            )
        elif dominant == "freaky":
            return EmotionResult(
                primary_emotion="freaky",
                confidence=confidence,
                valence=-0.5,
                arousal=0.9,
                suggested_voice_style="triage",
                empathetic_note="Take a steady breath, Dev. All systems are stable and under control. We will resolve this immediately."
            )
        else:
            return EmotionResult(
                primary_emotion="neutral",
                confidence=confidence,
                valence=0.0,
                arousal=0.4,
                suggested_voice_style="cinematic",
                empathetic_note=""
            )


# Global instance
_emotion_detector: Optional[EmotionDetector] = None


def get_emotion_detector() -> EmotionDetector:
    global _emotion_detector
    if _emotion_detector is None:
        _emotion_detector = EmotionDetector()
    return _emotion_detector

