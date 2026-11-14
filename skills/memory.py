"""
J.A.R.V.I.S. — Persistent Memory Skill
Stores user facts, preferences, and custom notes in JSON format.
Persists across sessions in memory/jarvis_memory.json.
"""

import os
import json
import datetime
from typing import Dict, Any, Optional, List

import config

MEMORY_PATH = os.path.abspath(config.MEMORY_FILE)


class JarvisMemory:
    def __init__(self, memory_file: str = MEMORY_PATH):
        self.memory_file = memory_file
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.isfile(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"facts": {}, "notes": []}
        return {"facts": {}, "notes": []}

    def _save(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def store_fact(self, key: str, value: str) -> str:
        k = key.strip().lower()
        self.data.setdefault("facts", {})[k] = {
            "value": value.strip(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        self._save()
        return value

    def store_raw(self, text: str) -> str:
        """Stores arbitrary note with timestamp."""
        entry = {
            "text": text.strip(),
            "created_at": datetime.datetime.now().isoformat()
        }
        self.data.setdefault("notes", []).append(entry)
        self._save()
        return text

    def recall(self, query: str) -> Optional[str]:
        q = query.strip().lower()
        facts = self.data.get("facts", {})

        # Direct key match
        if q in facts:
            return facts[q]["value"]

        # Partial key match
        for k, v in facts.items():
            if k in q or q in k:
                return v["value"]

        # Search notes
        notes = self.data.get("notes", [])
        for note in reversed(notes):
            if q in note["text"].lower():
                return note["text"]

        return None

    def list_all(self) -> Dict[str, Any]:
        return self.data

    def get_last_event_and_congratulate(self) -> Optional[str]:
        """
        Retrieves the most recent stored milestone or event about Dev,
        and generates an authentic personal congratulation.
        """
        facts = self.data.get("facts", {})
        notes = self.data.get("notes", [])

        # Search notes for achievements or milestones
        for note in reversed(notes):
            txt = note.get("text", "")
            if any(w in txt.lower() for w in ["completed", "built", "finished", "won", "passed", "phase", "project", "success", "milestone"]):
                return f"Allow me to congratulate you once more on {txt}, Dev. A remarkable accomplishment, sir."

        if facts:
            recent_key = list(facts.keys())[-1]
            val = facts[recent_key].get("value", "")
            return f"Regarding your record of {recent_key} as {val}, Dev: allow me to congratulate you on the progress, sir."

        return "Allow me to congratulate you on completing all 11 foundational architectures, Dev. A stellar achievement, sir."


# Global instance
_memory_instance: Optional[JarvisMemory] = None


def get_memory() -> JarvisMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = JarvisMemory()
    return _memory_instance


def handle_store(intent_res) -> str:
    raw_data = intent_res.parameters.get("data", "")
    if not raw_data:
        return "I am afraid I did not receive any information to store, sir."

    mem = get_memory()
    # Check if "is" or ":" separates key and value (e.g. "my birthday is May 2")
    if " is " in raw_data:
        parts = raw_data.split(" is ", 1)
        mem.store_fact(parts[0], parts[1])
    else:
        mem.store_raw(raw_data)

    from core.responses import get_response
    return get_response("saving_memory")


def handle_recall(intent_res) -> str:
    query = intent_res.parameters.get("query", "")
    if not query:
        return "What would you like me to recall, sir?"

    mem = get_memory()
    result = mem.recall(query)
    from core.responses import get_response
    if result:
        return f"{get_response('recall_memory')} {result}"
    return f"I have no record regarding '{query}' in my memory banks, sir."

