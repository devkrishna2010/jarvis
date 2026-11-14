"""
J.A.R.V.I.S. — System Diagnostics & Telemetry Skill (Phase 7)
Provides real-time hardware telemetry:
- CPU utilization & core counts
- RAM usage & available memory headroom
- Disk storage capacity & free space
- Battery & AC power status
- System boot uptime & running task load
Delivered with authentic Tony Stark HUD status reporting.
"""

import os
import sys
import datetime
import psutil
from typing import Dict, Any, Tuple

from core.responses import get_response
import config


def get_system_telemetry() -> Dict[str, Any]:
    """Gathers real-time machine hardware metrics."""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count(logical=True)

    # RAM
    vmem = psutil.virtual_memory()
    ram_total_gb = round(vmem.total / (1024 ** 3), 1)
    ram_used_gb = round(vmem.used / (1024 ** 3), 1)
    ram_percent = vmem.percent

    # Disk (primary drive)
    disk = psutil.disk_usage("C:\\")
    disk_total_gb = round(disk.total / (1024 ** 3), 1)
    disk_free_gb = round(disk.free / (1024 ** 3), 1)
    disk_percent = disk.percent

    # Battery
    battery = psutil.sensors_battery()
    bat_info = None
    if battery is not None:
        bat_info = {
            "percent": round(battery.percent),
            "power_plugged": battery.power_plugged
        }

    # Uptime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime_duration = datetime.datetime.now() - boot_time
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)

    # Active process count
    p_count = len(psutil.pids())

    return {
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "ram_total_gb": ram_total_gb,
        "ram_used_gb": ram_used_gb,
        "ram_percent": ram_percent,
        "disk_total_gb": disk_total_gb,
        "disk_free_gb": disk_free_gb,
        "disk_percent": disk_percent,
        "battery": bat_info,
        "uptime": f"{hours} hours, {minutes} minutes",
        "process_count": p_count
    }


def format_diagnostic_report(telemetry: Dict[str, Any]) -> str:
    """Formats telemetry dictionary into authentic J.A.R.V.I.S. speech dialogue."""
    cpu_p = telemetry["cpu_percent"]
    ram_p = telemetry["ram_percent"]
    ram_used = telemetry["ram_used_gb"]
    ram_tot = telemetry["ram_total_gb"]
    disk_free = telemetry["disk_free_gb"]
    bat = telemetry.get("battery")
    uptime = telemetry["uptime"]

    parts = [
        "Diagnostic telemetry scan complete, sir.",
        f"Central processor is operating at {cpu_p} percent capacity across {telemetry['cpu_count']} cores.",
        f"Memory utilization is at {ram_p} percent, consuming {ram_used} of {ram_tot} gigabytes.",
        f"Storage reserves indicate {disk_free} gigabytes available on primary volumes.",
    ]

    if bat is not None:
        plugged_str = "connected to AC power" if bat["power_plugged"] else "discharging on internal cells"
        parts.append(f"Power cells stand at {bat['percent']} percent, currently {plugged_str}.")
    else:
        parts.append("Power distribution is drawing continuously from standard AC mains.")

    parts.append(f"System uptime stands at {uptime} with {telemetry['process_count']} active tasks running within nominal parameters.")

    return " ".join(parts)


def handle_diagnostics(intent_res) -> str:
    telemetry = get_system_telemetry()
    return format_diagnostic_report(telemetry)

