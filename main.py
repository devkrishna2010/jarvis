"""
J.A.R.V.I.S. — Main Application Entry Point
Phase 7 Autonomous Multi-Mode Assistant
"""

import os
import sys
import argparse
import datetime

import config
from core.brain import JarvisBrain
from core.responses import get_response
from core.voice_output import speak
from core.voice_input import listen_phrase
from core.hands_free_listener import HandsFreeListener
from core.hud_terminal import render_dashboard
from core.hud_server import get_hud_server
from skills.scheduler import handle_briefing
from skills.system_diagnostics import handle_diagnostics


def get_greeting() -> str:
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return get_response("greeting_morning")
    elif 12 <= hour < 17:
        return get_response("greeting_afternoon")
    else:
        return get_response("startup")


def run_interactive_mode(brain: JarvisBrain):
    render_dashboard(status="STANDBY", mode=config.DEFAULT_VOICE_STYLE.upper(), emotion="COMPOSED")
    print("  Commands:")
    print("    • Type 'handsfree' or 'wake' to start continuous voice listening")
    print("    • Type 'voice' to speak a single command")
    print("    • Type 'briefing' for intelligence brief with live weather")
    print("    • Type 'diagnostics' for full system hardware telemetry")
    print("    • Type 'flaws' to run self-diagnostic flaw audit & improvement targets")
    print("    • Type 'backup' to dispatch full project archive to Telegram")
    print("    • Type 'hud' to launch holographic browser HUD")
    print("    • Type 'quit' to exit")
    print("=" * 71)
    print()

    # Background Saturday Backup Check & Passcode 2681 Listener
    try:
        import threading
        from skills.telegram_backup import check_and_run_saturday_backup, start_passcode_listener
        start_passcode_listener()
        threading.Thread(target=check_and_run_saturday_backup, daemon=True).start()
    except Exception:
        pass

    # Startup Greeting
    greeting = get_greeting()
    print(f"[{config.JARVIS_NAME}]: {greeting}")
    speak(greeting, style=config.DEFAULT_VOICE_STYLE, block=True)

    while True:
        try:
            user_input = input(f"\n[{config.USER_TITLE}]: ").strip()
            if not user_input:
                continue

            low = user_input.lower()
            if low in ["quit", "exit", "shutdown", "power down"]:
                bye = get_response("shutdown")
                print(f"[{config.JARVIS_NAME}]: {bye}")
                speak(bye, style=config.DEFAULT_VOICE_STYLE, block=True)
                break

            # Launch browser HUD
            if low in ["hud", "web hud", "visualizer", "open hud"]:
                server = get_hud_server()
                if not server.running:
                    success, url = server.start(in_background=True)
                    print(f"[{config.JARVIS_NAME}]: Holographic tactical HUD launched at {url}")
                import webbrowser
                webbrowser.open(f"http://127.0.0.1:{server.port}")
                continue

            # Switch to continuous hands-free mode
            if low in ["handsfree", "wake", "hands-free", "autonomous"]:
                listener = HandsFreeListener(brain=brain)
                listener.start()
                continue

            # Handle single spoken command
            if low in ["voice", "listen", "mic"]:
                print(f"[{config.JARVIS_NAME}]: Listening, sir...")
                heard = listen_phrase(timeout_sec=7.0)
                if heard:
                    print(f"[{config.USER_TITLE} (Spoken)]: {heard}")
                    user_input = heard
                else:
                    msg = "I did not quite catch that, sir."
                    print(f"[{config.JARVIS_NAME}]: {msg}")
                    speak(msg, block=True)
                    continue

            # Process through Cognitive Brain
            reply, style = brain.process_query(user_input)
            print(f"[{config.JARVIS_NAME}]: {reply}")
            speak(reply, style=style, block=True)

        except (KeyboardInterrupt, EOFError):
            print(f"\nShutting down safely, {config.USER_TITLE}.")
            break

    # Automatic end-of-session flaw and improvement logging
    try:
        from core.self_improvement import get_flaw_detector
        get_flaw_detector().save_daily_report()
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Mark VII Personal Assistant")
    parser.add_argument("--wake", action="store_true", help="Launch directly into hands-free wake word listener")
    parser.add_argument("--status", action="store_true", help="Execute immediate diagnostic telemetry check")
    parser.add_argument("--brief", action="store_true", help="Deliver daily intelligence briefing with live weather")
    parser.add_argument("--flaws", action="store_true", help="Run autonomous self-diagnostic flaw audit and save report")
    parser.add_argument("--hud", action="store_true", help="Launch holographic Arc Reactor HUD in browser")
    args = parser.parse_args()

    brain = JarvisBrain()

    # Passcode 2681 Telegram Listener active across all modes
    try:
        from skills.telegram_backup import start_passcode_listener
        start_passcode_listener()
    except Exception:
        pass

    if args.hud:
        server = get_hud_server()
        success, url = server.start(in_background=True)
        print(f"[{config.JARVIS_NAME}]: Holographic tactical HUD launched at {url}")
        import webbrowser
        webbrowser.open(url)
        run_interactive_mode(brain)
    elif args.wake:
        listener = HandsFreeListener(brain=brain)
        listener.start()
    elif args.status:
        res = brain.process_query("diagnostic telemetry check")
        print(f"[{config.JARVIS_NAME}]: {res[0]}")
        speak(res[0], style=res[1], block=True)
    elif args.brief:
        res = brain.process_query("give me the morning briefing")
        print(f"[{config.JARVIS_NAME}]: {res[0]}")
        speak(res[0], style=res[1], block=True)
    elif args.flaws:
        res = brain.process_query("run self diagnostic flaw audit")
        print(f"[{config.JARVIS_NAME}]: {res[0]}")
        speak(res[0], style=res[1], block=True)
    else:
        run_interactive_mode(brain)


if __name__ == "__main__":
    main()
