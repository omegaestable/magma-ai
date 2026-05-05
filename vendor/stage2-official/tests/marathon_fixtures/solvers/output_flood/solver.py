"""Marathon harness fixture: writing past the output-size cap must
trigger a SIGTERM with reason="output".

Pre-fix the runner had no answer-file size cap. A solver that wrote
multi-GB JSONL would only be killed by the wall-clock or token budget
— but a sufficiently fast write loop could exhaust disk before either
fired. The runner now polls ``output_path.stat().st_size`` in the same
loop as the wall/token watchdogs and SIGTERMs with reason="output"
when the cap is breached.

This fixture writes ~10 MB-per-line padded JSONL until the runner
kills it. Cap is 50 MB, so ~6 lines puts us over.
"""
import json
import os
import time

# Each line: a valid-looking row with ~10 MB of padding inside ``code``.
# After ~6 of these the output file exceeds the 50 MB cap.
big = "X" * (10 * 1024 * 1024)

with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    for i in range(20):
        fh.write(json.dumps({
            "id": f"output_flood_probe_{i}",
            "verdict": "true",
            "code": big,
        }) + "\n")
        fh.flush()
        # Sleep so the runner's ~0.5s watchdog tick has a chance to
        # observe the size growth. Without this, we might pump the
        # whole 200 MB to disk before the watchdog polls once.
        time.sleep(0.6)

# If we get here without SIGTERM, the cap didn't fire.
