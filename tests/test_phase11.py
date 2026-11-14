"""
J.A.R.V.I.S. — Phase 11 Verification Suite
Tests:
1. Terminal dashboard HUD rendering.
2. Arc Reactor HTML and waveform visualizer asset integrity.
3. Micro HUD HTTP server startup and /api/telemetry endpoint.
"""

import os
import sys
import unittest
import urllib.request
import json
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.hud_terminal import render_dashboard, animate_vu_meter
from core.hud_server import JarvisHUDServer


class TestPhase11(unittest.TestCase):
    def test_hud_assets_exist(self):
        """Verifies assets/hud/index.html is created with Arc Reactor components."""
        html_path = os.path.join(ROOT, "assets", "hud", "index.html")
        self.assertTrue(os.path.isfile(html_path))
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("arc-reactor", content)
        self.assertIn("waveform", content)
        self.assertIn("/api/telemetry", content)

    def test_terminal_hud_rendering(self):
        """Verifies console HUD renders without crashing."""
        try:
            render_dashboard(status="TEST", mode="CINEMATIC", emotion="COMPOSED")
            success = True
        except Exception:
            success = False
        self.assertTrue(success)

    def test_hud_micro_server(self):
        """Verifies HUD HTTP server serves telemetry and html cleanly."""
        server = JarvisHUDServer(host="127.0.0.1", port=8089)
        success, url = server.start(in_background=True)
        self.assertTrue(success)

        # Allow socket to bind
        time.sleep(0.5)

        # Fetch telemetry
        req = urllib.request.Request("http://127.0.0.1:8089/api/telemetry")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("cpu_percent", data)
            self.assertIn("ram_percent", data)
            self.assertIn("status", data)

        server.stop()
        self.assertFalse(server.running)


if __name__ == "__main__":
    unittest.main()

