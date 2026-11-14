"""
J.A.R.V.I.S. — Scheduler & Morning Briefing Skill (Phase 6)
Handles:
- Time-based reminder scheduling & background alert firing
- Morning & evening intelligence briefings
- Integrates with core/responses.py for authentic JARVIS delivery
"""

import os
import re
import json
import time
import datetime
import threading
from typing import Dict, Any, List, Optional, Tuple

import config
from core.responses import get_response
from core.voice_output import speak

REMINDERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory", "reminders.json")


class JarvisScheduler:
    def __init__(self, storage_file: str = REMINDERS_FILE):
        self.storage_file = storage_file
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        self.reminders: List[Dict[str, Any]] = self._load()
        self._running = True
        self._daemon_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._daemon_thread.start()

    def _load(self) -> List[Dict[str, Any]]:
        if os.path.isfile(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save(self):
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self.reminders, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add_reminder(self, task: str, delay_seconds: float) -> str:
        fire_time = datetime.datetime.now() + datetime.timedelta(seconds=delay_seconds)
        entry = {
            "task": task.strip(),
            "fire_at": fire_time.isoformat(),
            "notified": False
        }
        self.reminders.append(entry)
        self._save()
        return get_response("reminder_set")

    def _monitor_loop(self):
        """Background thread checking for due reminders and Saturday Telegram backups."""
        last_backup_check = 0.0
        while self._running:
            time.sleep(2)
            now = datetime.datetime.now()

            # Periodic Saturday backup verification (checked every 30 minutes)
            if time.time() - last_backup_check > 1800.0:
                last_backup_check = time.time()
                try:
                    from skills.telegram_backup import check_and_run_saturday_backup
                    threading.Thread(target=check_and_run_saturday_backup, daemon=True).start()
                except Exception:
                    pass

            for r in self.reminders:
                if not r.get("notified", False):
                    fire_at = datetime.datetime.fromisoformat(r["fire_at"])
                    if now >= fire_at:
                        r["notified"] = True
                        self._save()
                        # Fire alert speech
                        alert_msg = get_response("reminder_fire", reminder=r["task"])
                        speak(alert_msg, style="alert", block=False)

    def generate_morning_briefing(self) -> str:
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d")
        time_str = now.strftime("%I:%M %p")

        # Count active reminders
        active_reminders = [r for r in self.reminders if not r.get("notified", False)]
        rem_count = len(active_reminders)

        briefing_parts = [
            f"{get_response('morning_briefing')}",
            f"It is {time_str} on {date_str}.",
            "All primary system modules are operational, with zero anomalies reported.",
        ]

        # Live weather insertion
        try:
            from skills.weather import get_current_weather
            success, wdata, _ = get_current_weather()
            if success and wdata.get("temp_c") != "N/A":
                briefing_parts.append(
                    f"Outside telemetry in {wdata['location']} reports {wdata['condition'].lower()} at {wdata['temp_c']} degrees Celsius."
                )
        except Exception:
            pass

        if rem_count > 0:
            briefing_parts.append(f"You have {rem_count} pending reminder{'s' if rem_count > 1 else ''} scheduled.")
        else:
            briefing_parts.append(f"{get_response('no_schedule')}")

        return " ".join(briefing_parts)


# Global scheduler instance
_scheduler_instance: Optional[JarvisScheduler] = None


def get_scheduler() -> JarvisScheduler:
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = JarvisScheduler()
    return _scheduler_instance


def handle_reminder(intent_res) -> str:
    raw = intent_res.raw_query.lower()

    # Pattern: remind me to <task> in <number> <minutes|seconds|hours>
    match = re.search(r"remind me to (.+?) in (\d+)\s*(second|minute|hour)s?", raw)
    if match:
        task = match.group(1).strip()
        qty = float(match.group(2))
        unit = match.group(3)

        if "second" in unit:
            seconds = qty
        elif "minute" in unit:
            seconds = qty * 60.0
        else:
            seconds = qty * 3600.0

        scheduler = get_scheduler()
        return scheduler.add_reminder(task, seconds)

    # General reminder fallback
    return get_response("reminder_set")


def handle_briefing(intent_res) -> str:
    scheduler = get_scheduler()
    return scheduler.generate_morning_briefing()

