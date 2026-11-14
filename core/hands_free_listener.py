"""
J.A.R.V.I.S. — Hands-Free Autonomous Voice Listener (Phase 7)
Enables continuous hands-free operation:
1. Low-power Wake-Word standby loop ("Jarvis" / "Hey Jarvis").
2. Chime / Spoken acknowledgment ("Yes, sir?", "At your service, sir.").
3. Speech command recognition using Vosk.
4. Cognitive brain processing and skill dispatch.
5. High-fidelity 3-layer audio response playback.
6. Seamless, non-blocking return to standby.
"""

import os
import sys
import time
import random
from typing import Optional, Callable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config
from core.wake_word import WakeWordDetector
from core.voice_input import listen_phrase
from core.voice_output import speak
from core.brain import JarvisBrain

WAKE_ACKS = [
    "Yes, sir?",
    "At your service, sir.",
    "Online and listening, sir.",
    "Awaiting your instruction, sir.",
    "Right here, sir."
]


class HandsFreeListener:
    def __init__(self, brain: Optional[JarvisBrain] = None, on_query_callback: Optional[Callable[[str, str], None]] = None):
        self.brain = brain or JarvisBrain()
        self.detector = WakeWordDetector(target_word="jarvis")
        self.on_query_callback = on_query_callback
        self.running = False

    def start(self):
        """Runs the continuous hands-free loop until stopped."""
        self.running = True
        print()
        print("=" * 65)
        print("  J.A.R.V.I.S. — Hands-Free Autonomous Mode Active")
        print("  Listening for wake word: 'JARVIS' or 'HEY JARVIS'")
        print("  Press Ctrl+C to exit hands-free mode.")
        print("=" * 65)
        print()

        while self.running:
            try:
                # 1. Listen for Wake Word with low-power detector
                detected = self.detector.listen_for_wake(timeout_sec=2.0)
                if not detected:
                    continue

                # 2. Wake Word Detected -> Acknowledge
                ack = random.choice(WAKE_ACKS)
                print(f"\n[WAKE DETECTED] [{config.JARVIS_NAME}]: {ack}")
                speak(ack, style="cinematic", block=True)

                # 3. Capture Command
                print(f"[{config.JARVIS_NAME}]: Awaiting command...")
                query = listen_phrase(timeout_sec=7.0)

                if not query:
                    msg = "I am on standby whenever you need me, sir."
                    print(f"[{config.JARVIS_NAME}]: {msg}")
                    speak(msg, style="normal", block=True)
                    continue

                print(f"[{config.USER_TITLE} (Spoken)]: {query}")

                # Check if exit command
                if query.lower() in ["shutdown", "go to sleep", "exit", "quit", "power down"]:
                    bye = "Entering low-power standby mode. Have a pleasant day, sir."
                    print(f"[{config.JARVIS_NAME}]: {bye}")
                    speak(bye, style="cinematic", block=True)
                    self.running = False
                    break

                # 4. Process Through Cognitive Brain
                reply, style = self.brain.process_query(query)
                print(f"[{config.JARVIS_NAME}]: {reply}")

                if self.on_query_callback:
                    self.on_query_callback(query, reply)

                # 5. Speak Result
                speak(reply, style=style, block=True)

                # Short debounce before resuming wake loop
                time.sleep(0.5)

            except (KeyboardInterrupt, EOFError):
                print("\nHands-free mode deactivated, sir.")
                self.running = False
                break
            except Exception as e:
                print(f"[HandsFree error]: {e}")
                time.sleep(1.0)

    def stop(self):
        self.running = False

