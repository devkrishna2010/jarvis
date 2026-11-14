"""
J.A.R.V.I.S. — Voice System Audition & Multi-Mode Test
Generates and compares:
1. Cinematic mode — Fuller, warmer playback with custom EQ curve
2. Normal mode — Natural voice without extra bass
3. Night mode — Lower volume and controlled bass
Outputs saved in voice/tests/output/
"""

import os
import sys
import time
import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from voice.text_to_speech import JarvisTTS

TEST_OUTPUT_DIR = os.path.join(ROOT, "voice", "tests", "output")
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

TEST_LINE = "Good evening, Mr. Stark. Welcome home. All systems are online and fully operational."


def measure_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def run_test():
    print("=" * 65)
    print("  J.A.R.V.I.S. Multi-Mode Voice Test (Cinematic, Normal, Night)")
    print("=" * 65)

    start_mem = measure_memory_mb()
    tts = JarvisTTS(use_cache=False)

    modes = [
        ("cinematic", "1. Cinematic Mode  (Fuller, warmer + custom EQ curve)"),
        ("normal",    "2. Normal Mode     (Natural voice without extra bass)"),
        ("night",     "3. Night Mode      (Lower volume & controlled bass)"),
    ]

    generated = {}
    for mode_name, label in modes:
        out_path = os.path.join(TEST_OUTPUT_DIR, f"mode_{mode_name}.wav")
        print(f"\n► Generating: {label}")
        t0 = time.perf_counter()
        tts.synthesize(TEST_LINE, style=mode_name, output_file=out_path, apply_effects=True)
        dur = time.perf_counter() - t0
        sz_kb = os.path.getsize(out_path) / 1024.0
        print(f"    Saved: {os.path.basename(out_path)} ({sz_kb:.1f} KB in {dur:.2f}s)")
        generated[mode_name] = out_path

    # Also render an authentic dialogue sample in cinematic mode
    quote_path = os.path.join(TEST_OUTPUT_DIR, "cinematic_workshop.wav")
    quote_line = "Good evening, Mr. Stark. Welcome home. Shall I prepare the workshop for you?"
    tts.synthesize(quote_line, style="cinematic", output_file=quote_path, apply_effects=True)
    generated["cinematic_workshop"] = quote_path
    print(f"\n✓ Generated dialogue: {os.path.basename(quote_path)}")

    final_mem = measure_memory_mb()
    print("\n" + "=" * 65)
    print(f"  Memory Footprint: {final_mem:.2f} MB (Delta: {final_mem - start_mem:+.2f} MB)")
    print("  All outputs saved in: voice/tests/output/")
    print("=" * 65)

    # Play preview: Cinematic Mode
    cinematic_file = generated["cinematic_workshop"]
    print(f"\n>>> Playing Preview: Cinematic Mode (Fuller, Warmer)...")
    tts.play(cinematic_file)
    print(">>> Playback complete.")


if __name__ == "__main__":
    run_test()
