"""
J.A.R.V.I.S. — Phase 10 Verification Suite
Tests:
1. ProtocolEngine loading and defaults.
2. Multi-step protocol execution (workshop, cinema, lockdown, night_owl).
3. Brain intent routing for Stark workshop protocols.
4. Error resilience for unregistered protocols.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config
from core.brain import JarvisBrain
from skills.protocols import ProtocolEngine, get_protocol_engine


class TestPhase10(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = JarvisBrain()
        cls.engine = get_protocol_engine()

    def test_default_protocols_exist(self):
        """Verifies default MCU protocols are registered."""
        self.assertIn("workshop", self.engine.protocols)
        self.assertIn("cinema", self.engine.protocols)
        self.assertIn("lockdown", self.engine.protocols)
        self.assertIn("night_owl", self.engine.protocols)

    def test_execute_workshop_protocol(self):
        """Verifies workshop protocol executes and returns speech."""
        success, speech, style = self.engine.execute_protocol("workshop")
        self.assertTrue(success)
        self.assertIn("protocol", speech.lower())
        self.assertEqual(style, "cinematic")

    def test_execute_unknown_protocol(self):
        """Verifies unregistered protocol is handled gracefully."""
        success, speech, _ = self.engine.execute_protocol("quantum_realm_warp")
        self.assertFalse(success)
        self.assertIn("not registered", speech.lower())

    def test_brain_protocol_routing(self):
        """Verifies Brain routes protocol commands to protocol intent."""
        queries = [
            ("Initiate workshop protocol", "workshop"),
            ("Engage cinema protocol", "cinema"),
            ("Activate lockdown protocol", "lockdown"),
            ("Night owl protocol", "night_owl"),
            ("Coding mode", "workshop")
        ]
        for q, expected_proto in queries:
            intent_res = self.brain.parse_intent(q)
            self.assertEqual(intent_res.intent, "protocol", f"Failed intent for: '{q}'")
            self.assertIn(expected_proto, intent_res.parameters.get("protocol", ""), f"Failed target for: '{q}'")

        # Execution check
        reply, style = self.brain.process_query("Initiate workshop protocol")
        self.assertIn("protocol", reply.lower())
        self.assertIn("Dev", reply)


if __name__ == "__main__":
    unittest.main()

