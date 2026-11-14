"""
J.A.R.V.I.S. — Phase 9 Verification Suite
Tests:
1. Emotion detection across dimensions (happy, angry, sad, freaky, neutral).
2. Registration of emotion-specific voice profiles (soothing, composed, triage).
3. Brain intent parsing for emotion inquiries.
4. Dynamic vocal style shift and empathetic framing based on user emotion.
"""

import os
import sys
import unittest
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.brain import JarvisBrain
from core.emotion_detector import EmotionDetector, get_emotion_detector
from voice.voice_profiles import PROFILES


class TestPhase9(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = JarvisBrain()
        cls.detector = get_emotion_detector()

    def test_emotion_profiles_registered(self):
        """Verifies emotion-specific voice profiles exist in the profile catalog."""
        self.assertIn("soothing", PROFILES)
        self.assertIn("composed", PROFILES)
        self.assertIn("triage", PROFILES)

    def test_happy_emotion_detection(self):
        """Verifies happy / excited inputs are detected accurately."""
        res = self.detector.detect_emotion("I am so thrilled and happy with this amazing progress!")
        self.assertEqual(res.primary_emotion, "happy")
        self.assertGreater(res.valence, 0.0)

    def test_angry_emotion_detection(self):
        """Verifies angry / frustrated inputs are detected accurately."""
        res = self.detector.detect_emotion("I am furious and angry! This stupid failure is annoying!")
        self.assertEqual(res.primary_emotion, "angry")
        self.assertLess(res.valence, 0.0)
        self.assertEqual(res.suggested_voice_style, "composed")

    def test_sad_emotion_detection(self):
        """Verifies sad / exhausted inputs are detected accurately."""
        res = self.detector.detect_emotion("I feel so sad and exhausted today, completely drained and down.")
        self.assertEqual(res.primary_emotion, "sad")
        self.assertLess(res.valence, 0.0)
        self.assertEqual(res.suggested_voice_style, "soothing")

    def test_freaky_emotion_detection(self):
        """Verifies freaky / panicked inputs are detected accurately."""
        res = self.detector.detect_emotion("I am freaking out! Quick, we have an emergency panic situation!")
        self.assertEqual(res.primary_emotion, "freaky")
        self.assertGreater(res.arousal, 0.6)
        self.assertEqual(res.suggested_voice_style, "triage")

    def test_neutral_emotion_detection(self):
        """Verifies plain conversational queries remain neutral."""
        res = self.detector.detect_emotion("What is the current time?")
        self.assertEqual(res.primary_emotion, "neutral")

    def test_brain_emotion_check_intent(self):
        """Verifies Brain routes emotion check questions."""
        queries = [
            "How do I sound?",
            "What is my mood?",
            "Detect my emotion",
            "Check my tone"
        ]
        for q in queries:
            intent_res = self.brain.parse_intent(q)
            self.assertEqual(intent_res.intent, "emotion_check", f"Failed for query: '{q}'")

        # Execution check
        reply, style = self.brain.process_query("How do I sound today?")
        self.assertIn("analysis", reply.lower())
        self.assertIn("Dev", reply)

    def test_adaptive_vocal_style_shift(self):
        """Verifies cognitive brain shifts voice style in response to emotional prompts."""
        # Sad input -> soothing style
        _, sad_style = self.brain.process_query("I feel really sad and tired today")
        self.assertEqual(sad_style, "soothing")

        # Angry input -> composed style
        _, angry_style = self.brain.process_query("I am so angry and furious right now!")
        self.assertEqual(angry_style, "composed")

        # Freaky input -> triage style
        _, freaky_style = self.brain.process_query("I am freaking out about an emergency!")
        self.assertEqual(freaky_style, "triage")


if __name__ == "__main__":
    unittest.main()

