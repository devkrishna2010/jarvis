"""
J.A.R.V.I.S. — Stark Workshop Protocols Engine (Phase 10)
Automates multi-step routine sequences:
- Workshop / Coding Protocol (launches IDE/terminal, sets concentration volume)
- Cinema / Entertainment Protocol (maximizes media, applies cinematic bass profile)
- Lockdown / Clean Slate Protocol (instant mute, security screenshot, workstation lock)
- Night Owl Protocol (lowers volume, night voice mode, generates evening recap)
- Custom protocol definitions stored in memory/protocols.json
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Tuple, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config
from core.responses import get_response
from skills.system_control import launch_application, adjust_volume, lock_system, capture_screenshot

PROTOCOLS_FILE = os.path.join(ROOT, "memory", "protocols.json")

DEFAULT_PROTOCOLS = {
    "workshop": {
        "description": "Engages development workspace and focus audio",
        "actions": [
            {"type": "app", "target": "terminal"},
            {"type": "volume", "action": "volume_down"},
            {"type": "voice_style", "style": "cinematic"}
        ],
        "speech": "Workshop protocol engaged, Dev. Development suite active and acoustic profile calibrated."
    },
    "cinema": {
        "description": "Optimizes system for cinematic media playback",
        "actions": [
            {"type": "volume", "action": "volume_up"},
            {"type": "voice_style", "style": "cinematic"}
        ],
        "speech": "Cinema protocol initiated, Dev. Audio dynamics boosted with full harmonic bass presence."
    },
    "lockdown": {
        "description": "Emergency security lockdown and workstation secure",
        "actions": [
            {"type": "volume", "action": "mute"},
            {"type": "screenshot"},
            {"type": "lock"}
        ],
        "speech": "Lockdown protocol engaged, Dev. Workstation secured."
    },
    "night_owl": {
        "description": "Late-night quiet workspace optimization",
        "actions": [
            {"type": "volume", "action": "volume_down"},
            {"type": "voice_style", "style": "night"}
        ],
        "speech": "Night owl protocol active, Dev. Audio shifted to subdued acoustic profile. The workshop is at rest, sir."
    }
}


class ProtocolEngine:
    def __init__(self, storage_file: str = PROTOCOLS_FILE):
        self.storage_file = storage_file
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        self.protocols = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.isfile(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge with defaults
                    merged = dict(DEFAULT_PROTOCOLS)
                    merged.update(data)
                    return merged
            except Exception:
                return dict(DEFAULT_PROTOCOLS)
        # Write initial defaults
        self._save(DEFAULT_PROTOCOLS)
        return dict(DEFAULT_PROTOCOLS)

    def _save(self, data: Dict[str, Any]):
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def execute_protocol(self, protocol_name: str) -> Tuple[bool, str, str]:
        """
        Executes sequence of protocol actions.
        Returns (success_bool, speech_announcement, applied_voice_style).
        """
        name = protocol_name.lower().strip()
        proto = self.protocols.get(name)

        if not proto:
            # Fallback search
            for k, v in self.protocols.items():
                if k in name or name in k:
                    proto = v
                    name = k
                    break

        if not proto:
            return False, f"Protocol '{protocol_name}' is not registered in the Stark database, Dev.", "normal"

        applied_style = "cinematic"

        for action in proto.get("actions", []):
            atype = action.get("type")
            if atype == "app":
                target = action.get("target", "")
                if target:
                    launch_application(target)
            elif atype == "volume":
                act = action.get("action", "")
                if act:
                    adjust_volume(act)
            elif atype == "screenshot":
                capture_screenshot()
            elif atype == "lock":
                lock_system()
            elif atype == "voice_style":
                applied_style = action.get("style", "cinematic")

        speech = proto.get("speech", f"{name.capitalize()} protocol executed, Dev.")
        return True, speech, applied_style


# Global instance
_protocol_engine: Optional[ProtocolEngine] = None


def get_protocol_engine() -> ProtocolEngine:
    global _protocol_engine
    if _protocol_engine is None:
        _protocol_engine = ProtocolEngine()
    return _protocol_engine


def handle_protocol(intent_res) -> str:
    engine = get_protocol_engine()
    target_proto = intent_res.parameters.get("protocol", "workshop")
    _, speech, _ = engine.execute_protocol(target_proto)
    return speech

