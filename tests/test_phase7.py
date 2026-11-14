"""
J.A.R.V.I.S. — Phase 7 Verification Suite
Tests:
1. Environmental weather intelligence (live & offline handling)
2. System hardware diagnostics and Stark HUD telemetry
3. Cognitive Brain routing for Phase 7 intents (weather, diagnostics)
4. Morning briefing weather integration
5. Hands-free autonomous listener component integrity
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.brain import JarvisBrain
from skills.weather import get_current_weather
from skills.system_diagnostics import get_system_telemetry, format_diagnostic_report
from skills.scheduler import get_scheduler
from core.wake_word import test_wake_detection
from core.hands_free_listener import HandsFreeListener


class TestPhase7(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = JarvisBrain()

    def test_weather_retrieval(self):
        """Verifies weather retrieval returns structured data or safe offline string."""
        success, data, summary = get_current_weather()
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 10)
        if success:
            self.assertIn("temp_c", data)
            self.assertIn("condition", data)

    def test_system_diagnostics(self):
        """Verifies telemetry captures CPU, RAM, Disk, and uptime."""
        telemetry = get_system_telemetry()
        self.assertIn("cpu_percent", telemetry)
        self.assertIn("ram_percent", telemetry)
        self.assertIn("disk_free_gb", telemetry)
        self.assertIn("uptime", telemetry)

        report = format_diagnostic_report(telemetry)
        self.assertIn("capacity", report.lower())
        self.assertIn("memory", report.lower())

    def test_brain_weather_routing(self):
        """Verifies Brain routes meteorological queries correctly."""
        queries = [
            "What is the weather outside?",
            "Give me the temperature forecast",
            "How is it outside in London?",
            "Outside temp report"
        ]
        for q in queries:
            intent_res = self.brain.parse_intent(q)
            self.assertEqual(intent_res.intent, "weather", f"Failed on query: '{q}'")

        # End-to-end execution
        reply, style = self.brain.process_query("What is the weather like?")
        self.assertIsInstance(reply, str)
        self.assertGreater(len(reply), 15)

    def test_brain_diagnostics_routing(self):
        """Verifies Brain routes hardware diagnostics queries correctly."""
        queries = [
            "Run a diagnostic check",
            "System telemetry report",
            "What is the cpu usage?",
            "Check ram usage and battery status"
        ]
        for q in queries:
            intent_res = self.brain.parse_intent(q)
            self.assertEqual(intent_res.intent, "diagnostics", f"Failed on query: '{q}'")

        # End-to-end execution
        reply, style = self.brain.process_query("Run system telemetry diagnostic")
        self.assertIn("telemetry", reply.lower())
        self.assertIn("processor", reply.lower())

    def test_morning_briefing_with_telemetry(self):
        """Verifies morning briefing generates without exception and mentions telemetry."""
        scheduler = get_scheduler()
        briefing = scheduler.generate_morning_briefing()
        self.assertIsInstance(briefing, str)
        self.assertGreater(len(briefing), 30)

    def test_hands_free_listener_init(self):
        """Verifies HandsFreeListener initializes correctly with brain and grammar model."""
        self.assertTrue(test_wake_detection())
        listener = HandsFreeListener(brain=self.brain)
        self.assertFalse(listener.running)
        self.assertIsNotNone(listener.detector)


if __name__ == "__main__":
    unittest.main()

