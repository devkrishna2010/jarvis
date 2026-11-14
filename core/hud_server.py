"""
J.A.R.V.I.S. — Micro Tactical HUD Web Server (Phase 11)
Lightweight HTTP server serving the holographic Stark Arc Reactor interface
and live telemetry feed using standard library http.server (0 external dependencies).
"""

import os
import sys
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config
from skills.system_diagnostics import get_system_telemetry

HUD_DIR = os.path.join(ROOT, "assets", "hud")

# Shared state
_hud_state = {
    "status": "online",
    "mode": config.DEFAULT_VOICE_STYLE,
    "emotion": "composed",
    "last_query": "",
    "last_reply": ""
}


def update_hud_state(key: str, val: str):
    _hud_state[key] = val


class JarvisHUDHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HUD_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/telemetry":
            telemetry = get_system_telemetry()
            data = {
                "status": _hud_state["status"],
                "mode": _hud_state["mode"],
                "emotion": _hud_state["emotion"],
                "last_query": _hud_state["last_query"],
                "last_reply": _hud_state["last_reply"],
                "cpu_percent": telemetry["cpu_percent"],
                "ram_percent": telemetry["ram_percent"],
                "uptime": telemetry["uptime"],
                "disk_free_gb": telemetry["disk_free_gb"]
            }
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        # Silence standard HTTP access logging to keep console clean
        pass


class JarvisHUDServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self.running = False

    def start(self, in_background: bool = True):
        try:
            self.server = HTTPServer((self.host, self.port), JarvisHUDHandler)
            self.running = True
            if in_background:
                self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self._thread.start()
            else:
                self.server.serve_forever()
            return True, f"http://{self.host}:{self.port}"
        except Exception as e:
            return False, f"HUD server error: {e}"

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.running = False


# Global server instance
_hud_server_instance: Optional[JarvisHUDServer] = None


def get_hud_server() -> JarvisHUDServer:
    global _hud_server_instance
    if _hud_server_instance is None:
        _hud_server_instance = JarvisHUDServer()
    return _hud_server_instance

