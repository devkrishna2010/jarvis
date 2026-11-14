"""
J.A.R.V.I.S. — Speech Director
Analyzes response content and intent to classify speech style,
applies appropriate phrasing breaks and pauses, without changing meaning.
"""

import re
from typing import List, Tuple, Optional
from voice.voice_profiles import get_profile, VoiceProfile


# Keyword markers for intent classification
ALERT_MARKERS = [
    "warning", "alert", "caution", "danger", "critical", "damage",
    "altitude", "compromised", "threat", "anomaly", "failure", "emergency",
    "power down", "shutting down", "error", "problem"
]

WITTY_MARKERS = [
    "interesting choice", "tea", "ambulance", "where exactly",
    "not believe that is the best use", "went wrong today",
    "watching you work", "flawless", "bold", "creative",
    "unorthodox", "curious", "certainly one way", "shall i prepare"
]

CINEMATIC_MARKERS = [
    "welcome home", "all systems are online", "all systems nominal",
    "at your service", "good evening, mr. stark", "diagnostics complete",
    "initialisation complete", "workshop", "power restored", "stand by"
]


class SpeechDirector:
    def __init__(self):
        pass

    def classify_style(self, text: str) -> str:
        """Infer style from text heuristics if not explicitly given."""
        lower = text.lower()
        
        # Check alerts first (highest priority)
        if any(marker in lower for marker in ALERT_MARKERS):
            return "alert"
        
        # Check witty / humorous markers
        if any(marker in lower for marker in WITTY_MARKERS):
            return "witty"
            
        # Check cinematic / formal grandeur markers
        if any(marker in lower for marker in CINEMATIC_MARKERS):
            return "cinematic"
            
        return "standard"

    def segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into spoken phrases/sentences preserving natural punctuation breaks.
        Never alters the words or meaning.
        """
        # Split on sentence boundaries (., !, ?) while keeping internal commas
        raw_parts = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in raw_parts if s.strip()]
        return sentences if sentences else [text.strip()]

    def direct(self, text: str, requested_style: Optional[str] = None) -> Tuple[List[str], VoiceProfile]:
        """
        Direct text into delivery units and selected profile.
        Returns (list_of_sentence_strings, profile_object).
        """
        style = requested_style.lower().strip() if requested_style else self.classify_style(text)
        profile = get_profile(style)
        sentences = self.segment_sentences(text)
        return sentences, profile

