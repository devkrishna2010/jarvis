"""
J.A.R.V.I.S — Voice Audition Script
=====================================
Generates and plays WAV samples using piper.exe.
Run from the Jarvis root:
    venv\\Scripts\\python voice_audition.py
"""

import os
import sys
import subprocess
import time

ROOT         = os.path.dirname(os.path.abspath(__file__))
PIPER_DIR    = os.path.join(ROOT, "assets", "piper", "piper")
PIPER_EXE    = os.path.join(PIPER_DIR, "piper.exe")
VOICE_DIR    = os.path.join(ROOT, "assets", "voice_model")
SAMPLES_DIR  = os.path.join(ROOT, "assets", "voice_samples")
CONFIG_PATH  = os.path.join(ROOT, "config.py")

os.makedirs(SAMPLES_DIR, exist_ok=True)

SAMPLE_TEXT = "Good morning, sir. All systems are online. Analysis complete. An interesting choice, sir."

VOICES = [
    {
        "id": "jarvis-high-smooth",
        "name": "1. JARVIS High (Smooth / Anti-crackle) [RECOMMENDED]",
        "folder": "jarvis-high",
        "onnx": "jarvis-high.onnx",
        "extra_args": ["--length_scale", "1.08", "--noise_scale", "0.4", "--noise_w", "0.6"]
    },
    {
        "id": "jarvis-high-standard",
        "name": "2. JARVIS High (Standard tuning)",
        "folder": "jarvis-high",
        "onnx": "jarvis-high.onnx",
        "extra_args": []
    },
    {
        "id": "jarvis-medium",
        "name": "3. JARVIS Medium (Original)",
        "folder": "jarvis-medium",
        "onnx": "jarvis-medium.onnx",
        "extra_args": []
    },
    {
        "id": "alan-medium",
        "name": "4. Alan Medium (Clean Studio British)",
        "folder": "alan-medium",
        "onnx": "en_GB-alan-medium.onnx",
        "extra_args": []
    },
    {
        "id": "southern-english-male-medium",
        "name": "5. Southern English Male (Formal RP)",
        "folder": "southern-english-male-medium",
        "onnx": "en_GB-southern_english_male-medium.onnx",
        "extra_args": []
    }
]


def play_wav(wav_path: str):
    if not wav_path or not os.path.isfile(wav_path):
        return
    ps_cmd = (
        f"$player = New-Object System.Media.SoundPlayer '{wav_path}'; "
        f"$player.PlaySync()"
    )
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)


def update_config(voice_dict: dict):
    onnx_full = os.path.join("assets", "voice_model", voice_dict["folder"], voice_dict["onnx"])
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    import re
    p1 = r'^PIPER_VOICE_MODEL\s*=.*$'
    n1 = f'PIPER_VOICE_MODEL = r"{onnx_full}"'
    if re.search(p1, content, re.MULTILINE):
        content = re.sub(p1, n1, content, flags=re.MULTILINE)
    else:
        content += f"\n{n1}\n"

    p2 = r'^PIPER_EXTRA_ARGS\s*=.*$'
    n2 = f'PIPER_EXTRA_ARGS = {voice_dict["extra_args"]}'
    if re.search(p2, content, re.MULTILINE):
        content = re.sub(p2, n2, content, flags=re.MULTILINE)
    else:
        content += f"{n2}\n"

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\\n  config.py updated with {voice_dict['name']}")


def main():
    print("=" * 60)
    print("  J.A.R.V.I.S — Voice Selector")
    print("=" * 60)
    for i, v in enumerate(VOICES, 1):
        wav = os.path.join(SAMPLES_DIR, f"{v['id']}.wav")
        status = "ready" if os.path.isfile(wav) else "missing"
        print(f"  [{i}] {v['name']} ({status})")

    while True:
        choice = input("\\nEnter number to select (or 'p 1' to play, 'q' to quit): ").strip().lower()
        if choice == "q":
            break
        if choice.startswith("p "):
            try:
                num = int(choice.split()[1]) - 1
                wav = os.path.join(SAMPLES_DIR, f"{VOICES[num]['id']}.wav")
                print(f"Playing {VOICES[num]['name']}...")
                play_wav(wav)
            except Exception as e:
                print("Invalid selection:", e)
            continue
        try:
            num = int(choice) - 1
            if 0 <= num < len(VOICES):
                update_config(VOICES[num])
                break
        except ValueError:
            pass


if __name__ == "__main__":
    main()
