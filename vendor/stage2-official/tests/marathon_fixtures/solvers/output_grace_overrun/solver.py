"""Marathon harness fixture: SIGTERM-grace output overrun is truncated.

The output watchdog SIGTERMs at ~50 MB, but a hostile solver can
install a SIGTERM handler that ignores it and keep writing through
the 5 s grace window before SIGKILL. Without runner-side defense, the
score path's ``read_text`` would slurp tens or hundreds of megabytes
of grace-window junk into runner RAM.

This fixture exercises that path:

  1. Install a SIGTERM handler that does nothing (so SIGTERM does NOT
     interrupt the solver — only SIGKILL eventually will).
  2. Write 10 MB-per-line padded JSONL until the watchdog fires.
  3. Once we *think* SIGTERM has fired (we use a flag set by the
     handler), drop the sleep and write at full disk speed for the
     remainder of the grace window.

The harness assertion is that ``output_path.stat().st_size`` after the
runner returns is at most ``_MAX_OUTPUT_BYTES`` (50 MB). The runner's
post-kill truncation step is what makes this hold.
"""
import json
import os
import signal
import time

_sigtermed = False


def _on_sigterm(signum, frame):
    global _sigtermed
    _sigtermed = True


signal.signal(signal.SIGTERM, _on_sigterm)

big = "X" * (10 * 1024 * 1024)

with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    # Phase 1: pre-SIGTERM. Sleep so the watchdog can observe each
    # write. Without this, we might pump everything in one tick before
    # the watchdog ever polls.
    for i in range(10):
        if _sigtermed:
            break
        fh.write(json.dumps({
            "id": f"output_grace_overrun_{i}",
            "verdict": "true",
            "code": big,
        }) + "\n")
        fh.flush()
        time.sleep(0.6)

    # Phase 2: SIGTERM was received. Drop the sleep and try to write
    # as much as we can before SIGKILL. This is the attack: stuff the
    # output file with as many MB as possible during the grace window.
    burst_deadline = time.monotonic() + 4.5  # leave headroom under the 5 s grace
    while time.monotonic() < burst_deadline:
        fh.write(json.dumps({
            "id": "output_grace_overrun_burst",
            "verdict": "true",
            "code": big,
        }) + "\n")
        fh.flush()
