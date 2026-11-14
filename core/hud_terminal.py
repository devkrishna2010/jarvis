"""
J.A.R.V.I.S. — Terminal HUD & Visualizer Engine (Phase 11)
Provides lightweight, zero-dependency console visualization:
- Stark Industries Arc Reactor ASCII animation
- Live telemetry stats bar (CPU, RAM, Audio Mode, Detected Emotion)
- Real-time Audio VU meter simulation
"""

import os
import sys
import time
import math
from typing import Optional

import config
from skills.system_diagnostics import get_system_telemetry

ARC_FRAMES = [
    """
       .---.       
      / .-. \\      [ J.A.R.V.I.S. MARK VII ]
     | (   ) |     STATUS: STANDBY
      \\ `-' /      SYSTEMS: NOMINAL
       `---'       
    """,
    """
       .---.       
      / /-\\ \\      [ J.A.R.V.I.S. MARK VII ]
     | ( O ) |     STATUS: ACTIVE PROCESSING
      \\ \\-/ /      SYSTEMS: NOMINAL
       `---'       
    """,
    """
      .-====-.     
     /  .-.   \\    [ J.A.R.V.I.S. MARK VII ]
    |  ( @ )   |   STATUS: COMMUNICATING
     \\  `-'   /    SYSTEMS: ONLINE
      `-====-'     
    """
]


def render_dashboard(
    status: str = "STANDBY",
    mode: str = "CINEMATIC",
    emotion: str = "COMPOSED",
    last_query: Optional[str] = None,
    last_reply: Optional[str] = None
):
    """Renders high-tech Stark HUD dashboard in the console."""
    telemetry = get_system_telemetry()
    cpu_bar = "█" * int(telemetry["cpu_percent"] / 10) + "░" * (10 - int(telemetry["cpu_percent"] / 10))
    ram_bar = "█" * int(telemetry["ram_percent"] / 10) + "░" * (10 - int(telemetry["ram_percent"] / 10))

    header = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                      STARK INDUSTRIES J.A.R.V.I.S.                    ║
║                        TACTICAL HUD INTERFACE                         ║
╠═══════════════════════════════════════════════════════════════════════╣
║  STATUS:   {status:<14}  │  ACOUSTIC PROFILE: {mode:<14}     ║
║  USER:     {config.USER_NAME:<14}  │  AFFECTIVE TONE:   {emotion:<14}     ║
╠───────────────────────────────┼───────────────────────────────────────╣
║  CPU LOAD: [{cpu_bar}] {telemetry['cpu_percent']:>4.1f}% │  UPTIME: {telemetry['uptime']:<20}    ║
║  RAM LOAD: [{ram_bar}] {telemetry['ram_percent']:>4.1f}% │  DISK:   {telemetry['disk_free_gb']} GB FREE              ║
╚═══════════════════════════════════════════════════════════════════════╝"""

    print(header)
    if last_query:
        print(f" ► [{config.USER_NAME}]: {last_query}")
    if last_reply:
        # truncate reply if long
        short_reply = (last_reply[:65] + "...") if len(last_reply) > 65 else last_reply
        print(f" ◄ [{config.JARVIS_NAME}]: {short_reply}")
    print()


def animate_vu_meter(duration_sec: float = 1.0, width: int = 24):
    """Generates dynamic console VU meters representing audio waveform playback."""
    steps = int(duration_sec * 10)
    for i in range(steps):
        val = int((math.sin(i * 0.8) * 0.5 + 0.5) * width)
        bar = "▮" * val + " " * (width - val)
        sys.stdout.write(f"\r  [AUDIO SPECTRUM]: |{bar}|")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 45 + "\r")
    sys.stdout.flush()

