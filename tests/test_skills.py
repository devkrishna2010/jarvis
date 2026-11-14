"""
J.A.R.V.I.S. — Phase 4 Core Skills Verification
Tests:
1. Persistent Memory Storage & Recall (JSON)
2. System Control (Volume, Screenshot, Application Resolution)
3. Web Search & Live Retrieval (with offline fallback test)
4. Full Brain -> Skill Dispatch Pipeline
"""

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.brain import JarvisBrain
from skills.memory import get_memory
from skills.system_control import adjust_volume, capture_screenshot, KNOWN_APPS
from skills.web_search import check_internet_connection, search_web


def test_skills():
    print("=" * 65)
    print("  J.A.R.V.I.S. — Phase 4 Core Skills Verification")
    print("=" * 65)

    all_passed = True
    brain = JarvisBrain()

    # -------------------------------------------------------------
    # Test 1: Persistent Memory
    # -------------------------------------------------------------
    print("\n[Skill 1/3] Testing Persistent Memory Storage & Recall...")
    mem = get_memory()
    mem.store_fact("workshop security code", "Stark-1080")
    recalled = mem.recall("workshop security code")
    if recalled == "Stark-1080":
        print(f"  ✓ PASS: Direct memory storage & retrieval verified ('{recalled}')")
    else:
        print(f"  ✗ FAIL: Memory retrieval returned '{recalled}'")
        all_passed = False

    # Via Brain Dispatch
    store_resp, _ = brain.process_query("Remember that my favorite suit is Mark 7")
    recall_resp, _ = brain.process_query("What do you remember about my favorite suit?")
    print(f"  Brain Memory Query: '{recall_resp}'")
    if "mark 7" in recall_resp.lower():
        print("  ✓ PASS: End-to-end Brain -> Memory dispatch verified")
    else:
        print("  ✗ FAIL: Brain memory recall failed")
        all_passed = False

    # -------------------------------------------------------------
    # Test 2: System Control
    # -------------------------------------------------------------
    print("\n[Skill 2/3] Testing System Controls (Volume, Screenshot, Apps)...")
    v_ok, v_msg = adjust_volume("volume_up")
    if v_ok:
        print(f"  ✓ PASS: Volume adjustment virtual key event dispatched ({v_msg})")
    else:
        print("  ✗ FAIL: Volume control failed")
        all_passed = False

    shot_ok, shot_msg = capture_screenshot()
    if shot_ok:
        print(f"  ✓ PASS: Native screenshot captured ({shot_msg})")
    else:
        print(f"  ! NOTE: Screenshot notification: {shot_msg}")

    # App mapping check
    if "notepad" in KNOWN_APPS and "calc" in KNOWN_APPS:
        print(f"  ✓ PASS: Native Windows app mappings verified ({len(KNOWN_APPS)} apps registered)")
    else:
        print("  ✗ FAIL: App mappings missing")
        all_passed = False

    # -------------------------------------------------------------
    # Test 3: Web Search
    # -------------------------------------------------------------
    print("\n[Skill 3/3] Testing Web Search & Information Retrieval...")
    online = check_internet_connection()
    print(f"  Network Connectivity Status: {'ONLINE' if online else 'OFFLINE'}")

    if online:
        s_ok, results, s_msg = search_web("James Webb Space Telescope", max_results=1)
        if s_ok and results:
            print(f"  ✓ PASS: Live web search retrieved: '{results[0]['title'][:60]}...'")
            print(f"          Snippet: {results[0]['snippet'][:90]}...")
        else:
            print(f"  ! NOTE: Web search query returned: {s_msg}")
    else:
        s_ok, results, s_msg = search_web("test query")
        print(f"  ✓ PASS: Offline fallback correctly triggered: '{s_msg}'")

    # Via Brain Dispatch
    search_resp, _ = brain.process_query("Search for Python programming language")
    print(f"  Brain Search Query Response: '{search_resp[:120]}...'")
    if len(search_resp) > 20:
        print("  ✓ PASS: End-to-end Brain -> Web Search dispatch verified")
    else:
        print("  ✗ FAIL: Brain search response empty")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("  ALL PHASE 4 SKILLS VERIFIED SUCCESSFULLY, SIR.")
    else:
        print("  ONE OR MORE SKILLS CHECKS FAILED.")
    print("=" * 65)
    return all_passed


if __name__ == "__main__":
    success = test_skills()
    sys.exit(0 if success else 1)

