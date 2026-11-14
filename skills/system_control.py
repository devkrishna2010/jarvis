"""
J.A.R.V.I.S. — System Control Skill
Provides native Windows controls:
- Application launching (Notepad, Calculator, Chrome, VS Code, Task Manager, Explorer)
- Volume adjustments (Up, Down, Mute)
- Workstation locking
- Screenshot capture
"""

import os
import sys
import subprocess
import datetime
import ctypes
from typing import Dict, Optional, Tuple

from core.responses import get_response
import config

# Common Windows application mapping
KNOWN_APPS: Dict[str, str] = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "browser": "msedge.exe",
    "vs code": "code.cmd",
    "vscode": "code.cmd",
    "code": "code.cmd",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
}


def launch_application(app_name: str) -> Tuple[bool, str]:
    """
    Launches an application on Windows.
    Never pretends an app is open if the launch command failed.
    """
    clean_name = app_name.strip().lower()
    exe = KNOWN_APPS.get(clean_name, clean_name)

    try:
        # Use os.startfile on Windows for safe, non-blocking native launching
        os.startfile(exe)
        return True, get_response("opening_app")
    except Exception as e:
        # Try direct process start via shell
        try:
            subprocess.Popen(exe, shell=True)
            return True, get_response("opening_app")
        except Exception as e2:
            return False, f"I was unable to locate or launch '{app_name}', sir. Error: {e2}"


def adjust_volume(action: str) -> Tuple[bool, str]:
    """
    Controls Windows volume via virtual key codes (VK_VOLUME_UP, VK_VOLUME_DOWN, VK_VOLUME_MUTE).
    """
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP   = 0xAF

    user32 = ctypes.windll.user32

    if action == "volume_up":
        # Press 5 times for a noticeable step
        for _ in range(5):
            user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
        return True, get_response("volume_up")

    elif action == "volume_down":
        for _ in range(5):
            user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
        return True, get_response("volume_down")

    elif action == "mute":
        user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
        return True, get_response("volume_mute")

    return False, "Unknown volume command, sir."


def lock_system() -> Tuple[bool, str]:
    """Locks the Windows workstation instantly."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return True, get_response("lock")
    except Exception as e:
        return False, f"Unable to engage workstation lock, sir: {e}"


def capture_screenshot() -> Tuple[bool, str]:
    """
    Captures primary screen using .NET Graphics without heavy external Python imaging libraries.
    Saves output into logs/screenshots/.
    """
    shot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "screenshots")
    os.makedirs(shot_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    target_path = os.path.join(shot_dir, f"screenshot_{timestamp}.png")

    ps_script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        "$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
        "$bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height; "
        "$gfx = [System.Drawing.Graphics]::FromImage($bmp); "
        "$gfx.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size); "
        f"$bmp.Save('{target_path}', [System.Drawing.Imaging.ImageFormat]::Png); "
        "$gfx.Dispose(); "
        "$bmp.Dispose()"
    )

    try:
        res = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
        if os.path.isfile(target_path):
            return True, f"{get_response('screenshot')} Stored as screenshot_{timestamp}.png."
        return False, f"Screenshot capture failed: {res.stderr}"
    except Exception as e:
        return False, f"Screenshot command encountered an error: {e}"


# Intent handler bridges
def handle_app_launch(intent_res) -> str:
    app_name = intent_res.parameters.get("app", "")
    if not app_name:
        return "Which application shall I open, sir?"
    success, msg = launch_application(app_name)
    return msg


def handle_system_action(intent_res) -> str:
    action = intent_res.parameters.get("action", "")
    if action in ["volume_up", "volume_down", "mute"]:
        _, msg = adjust_volume(action)
        return msg
    elif action == "lock":
        _, msg = lock_system()
        return msg
    elif action == "screenshot":
        _, msg = capture_screenshot()
        return msg
    return "System action could not be identified, sir."
