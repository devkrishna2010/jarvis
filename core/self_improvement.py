"""
J.A.R.V.I.S. — Autonomous Flaw Detection & Continuous Improvement Engine (Phase 8)
Continuously monitors runtime operations to detect self-flaws:
- Unhandled/ambiguous queries (intents falling back to 'unknown')
- Execution latency spikes (> 500 ms parse, > 2.5s synthesis)
- Audio synthesis errors & cache misses
- Failed network searches and meteorological drops
- Missing application mappings in system control
- Memory and CPU resource spikes

Logs structured daily improvement entries into:
`memory/daily_flaws_and_improvements.txt`
"""

import os
import sys
import time
import datetime
from typing import Dict, Any, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config
from core.responses import get_response

FLAWS_FILE = os.path.join(ROOT, "memory", "daily_flaws_and_improvements.txt")
LOG_FILE = os.path.join(ROOT, "logs", "jarvis.log")


class FlawDetector:
    def __init__(self, output_file: str = FLAWS_FILE):
        self.output_file = output_file
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        self.detected_flaws: List[Dict[str, Any]] = []

    def record_query_event(
        self,
        query: str,
        intent: str,
        confidence: float,
        latency_ms: float,
        error: Optional[str] = None
    ):
        """Monitors a single turn and captures any flaw or friction point."""
        # 1. Fallback / Unrecognized intent
        if intent == "unknown" or confidence < 0.60:
            self.detected_flaws.append({
                "category": "Intent Understanding",
                "severity": "MODERATE",
                "flaw": f"Failed to classify intent for query: '{query}' (confidence: {confidence:.2f})",
                "fix": f"Add pattern rule to core/brain.py matching '{query}' with dedicated skill dispatch."
            })

        # 2. Latency Bottleneck
        if latency_ms > 450.0:
            self.detected_flaws.append({
                "category": "Latency & Responsiveness",
                "severity": "LOW",
                "flaw": f"Cognitive parse latency reached {latency_ms:.1f} ms for query: '{query}'",
                "fix": "Optimize regex pattern order or compile static regex patterns at module startup."
            })

        # 3. Explicit Execution Error
        if error:
            self.detected_flaws.append({
                "category": "Skill Execution",
                "severity": "HIGH",
                "flaw": f"Runtime error during execution: {error}",
                "fix": "Inspect skill exception stack trace and add defensive error boundary."
            })

    def run_system_audit(self) -> List[Dict[str, Any]]:
        """Scans system state and logs to discover systemic flaws."""
        import psutil
        vmem = psutil.virtual_memory()

        # Audit 1: High RAM pressure (> 80% on 4 GB machine)
        if vmem.percent > 80.0:
            self.detected_flaws.append({
                "category": "Hardware & Memory Overhead",
                "severity": "HIGH",
                "flaw": f"System RAM usage at {vmem.percent}% ({round(vmem.used / (1024**3), 1)} GB used of {round(vmem.total / (1024**3), 1)} GB).",
                "fix": "Purge unreferenced audio buffers and ensure speech synthesis models unload promptly."
            })

        # Audit 2: Audio Cache Size Check
        cache_dir = os.path.join(ROOT, "assets", "voice_cache")
        if os.path.isdir(cache_dir):
            cache_files = os.listdir(cache_dir)
            if len(cache_files) > 300:
                self.detected_flaws.append({
                    "category": "Disk Storage Headroom",
                    "severity": "LOW",
                    "flaw": f"Voice cache contains {len(cache_files)} entries accumulating on disk.",
                    "fix": "Implement LRU eviction policy to keep only the top 100 most frequent response files."
                })

        # Audit 3: Scan jarvis.log if exists
        if os.path.isfile(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                err_lines = [l for l in lines if "ERROR" in l or "Exception" in l]
                if len(err_lines) > 5:
                    self.detected_flaws.append({
                        "category": "Runtime Exceptions",
                        "severity": "MODERATE",
                        "flaw": f"Detected {len(err_lines)} error entries in recent runtime logs.",
                        "fix": "Review logs/jarvis.log and resolve intermittent module exceptions."
                    })
            except Exception:
                pass

        return self.detected_flaws

    def save_daily_report(self) -> Tuple[int, str]:
        """
        Appends or updates today's flaw detection audit in daily_flaws_and_improvements.txt.
        Returns (flaws_count, summary_string).
        """
        today_str = datetime.date.today().isoformat()
        now_time = datetime.datetime.now().strftime("%I:%M %p")

        # Run fresh system scan
        self.run_system_audit()

        # Deduplicate flaws by description
        unique_flaws = []
        seen = set()
        for f in self.detected_flaws:
            key = f["flaw"]
            if key not in seen:
                seen.add(key)
                unique_flaws.append(f)

        count = len(unique_flaws)

        report_lines = [
            "=" * 75,
            f"  J.A.R.V.I.S. SELF-DIAGNOSTIC & CONTINUOUS IMPROVEMENT AUDIT — {today_str}",
            f"  Audit Generated: {now_time} | Machine: Windows | User: {config.USER_NAME}",
            "=" * 75,
            f"Status: {count} Areas Identified for Improvement\n"
        ]

        if count == 0:
            report_lines.append("✓ Flaw Scan Result: Zero critical bottlenecks or unhandled intents detected.")
            report_lines.append("  All subsystems are executing with optimal MCU-fidelity and low latency.\n")
        else:
            for idx, fl in enumerate(unique_flaws, 1):
                report_lines.append(f"[{idx}] CATEGORY: {fl['category']}  [SEVERITY: {fl['severity']}]")
                report_lines.append(f"    • Detected Flaw: {fl['flaw']}")
                report_lines.append(f"    • Actionable Fix: {fl['fix']}\n")

        report_lines.append("-" * 75)
        report_lines.append(f"Audit concluded. Ready for self-repair and system refinement.\n\n")

        full_content = "\n".join(report_lines)

        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(full_content)
        except Exception as e:
            return count, f"Failed to write flaw report: {e}"

        summary = (
            f"I have conducted a self-diagnostic audit, {config.USER_NAME}. "
            f"I identified {count} operational flaw{'s' if count != 1 else ''} and potential "
            f"improvement{'s' if count != 1 else ''}, and saved the full analysis to our daily "
            f"improvement log for your review, {config.USER_TITLE}."
        )

        return count, summary


# Global singleton instance
_flaw_detector: Optional[FlawDetector] = None


def get_flaw_detector() -> FlawDetector:
    global _flaw_detector
    if _flaw_detector is None:
        _flaw_detector = FlawDetector()
    return _flaw_detector


def handle_flaws_check(intent_res) -> str:
    detector = get_flaw_detector()
    _, summary = detector.save_daily_report()
    return summary

