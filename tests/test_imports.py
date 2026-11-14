"""
J.A.R.V.I.S - Phase 1 Import Verification
Run with: venv/Scripts/python tests/test_imports.py
"""

import sys
import importlib

REQUIRED_PACKAGES = [
    ("vosk",          "vosk"),
    ("sounddevice",   "sounddevice"),
    ("pyttsx3",       "pyttsx3"),
    ("requests",      "requests"),
    ("beautifulsoup4","bs4"),
]

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

def test_imports():
    print()
    print("=" * 55)
    print("  J.A.R.V.I.S — Phase 1 Dependency Verification")
    print("=" * 55)
    print(f"{INFO} Python {sys.version}")
    print("-" * 55)

    all_passed = True
    for display_name, import_name in REQUIRED_PACKAGES:
        try:
            mod = importlib.import_module(import_name)
            version = getattr(mod, "__version__", "version unknown")
            print(f"{PASS} {display_name:<18} — {version}")
        except ImportError as e:
            print(f"{FAIL} {display_name:<18} — IMPORT FAILED: {e}")
            all_passed = False

    print("-" * 55)

    # Test JARVIS response library
    try:
        sys.path.insert(0, ".")
        from core.responses import get_response, list_keys
        key_count  = len(list_keys())
        resp_count = sum(len(v) for v in __import__("core.responses", fromlist=["RESPONSES"]).RESPONSES.values())
        sample     = get_response("startup")
        print(f"{PASS} core.responses      — {key_count} keys / {resp_count} responses")
        print(f"  Sample: \"{sample}\"")
    except Exception as e:
        print(f"{FAIL} core.responses      — {e}")
        all_passed = False

    print("=" * 55)
    if all_passed:
        print("  All checks passed. Phase 1 is complete, sir.")
    else:
        print("  One or more checks FAILED. See above.")
    print("=" * 55)
    print()
    return all_passed


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
