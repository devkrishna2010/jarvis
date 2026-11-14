"""
J.A.R.V.I.S. — Phase 8 Verification Suite
Tests:
1. FlawDetector event logging (unknown intents, latency bottlenecks, errors).
2. System resource & log audit.
3. Generation and persistence of memory/daily_flaws_and_improvements.txt.
4. Cognitive Brain routing for flaw detection and improvement queries.
5. Addressing user as Dev / sir.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config
from core.brain import JarvisBrain
from core.self_improvement import FlawDetector, get_flaw_detector

TEST_FLAWS_FILE = os.path.join(ROOT, "memory", "test_daily_flaws.txt")


class TestPhase8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = JarvisBrain()
        cls.detector = FlawDetector(output_file=TEST_FLAWS_FILE)

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(TEST_FLAWS_FILE):
            try:
                os.remove(TEST_FLAWS_FILE)
            except Exception:
                pass

    def test_record_flaw_events(self):
        """Verifies flaw detector records unhandled intents and latency spikes."""
        self.detector.detected_flaws.clear()

        # Record an unknown intent
        self.detector.record_query_event("hyperspace jump", "unknown", 0.30, 12.0)
        self.assertEqual(len(self.detector.detected_flaws), 1)
        self.assertEqual(self.detector.detected_flaws[0]["category"], "Intent Understanding")

        # Record a latency bottleneck
        self.detector.record_query_event("complex query", "calculation", 0.90, 520.0)
        self.assertEqual(len(self.detector.detected_flaws), 2)
        self.assertEqual(self.detector.detected_flaws[1]["category"], "Latency & Responsiveness")

    def test_save_daily_report(self):
        """Verifies report is generated with date headers and actionable fixes."""
        count, summary = self.detector.save_daily_report()
        self.assertTrue(os.path.isfile(TEST_FLAWS_FILE))
        with open(TEST_FLAWS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("J.A.R.V.I.S. SELF-DIAGNOSTIC", content)
        self.assertIn("Actionable Fix:", content)
        self.assertIn(config.USER_NAME, summary)

    def test_brain_flaw_routing(self):
        """Verifies Brain routes self-reflection queries to flaws_audit."""
        queries = [
            "Detect your flaws",
            "What should we improve?",
            "Run self diagnostic flaw audit",
            "Check system flaws"
        ]
        for q in queries:
            intent_res = self.brain.parse_intent(q)
            self.assertEqual(intent_res.intent, "flaws_audit", f"Failed for query: '{q}'")

        # End-to-end execution
        reply, style = self.brain.process_query("What should we improve?")
        self.assertIn("audit", reply.lower())
        self.assertIn(config.USER_NAME.lower(), reply.lower())

    def test_user_naming_configuration(self):
        """Verifies user name is set to Dev and title is sir."""
        self.assertEqual(config.USER_NAME, "Dev")
        self.assertEqual(config.USER_TITLE, "sir")


if __name__ == "__main__":
    unittest.main()

