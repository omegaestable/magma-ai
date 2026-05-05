"""Marathon harness fixture: writes one valid line, then sleeps forever.

The runner's wall-clock watchdog should SIGTERM us at the budget. Used
by the ``budget_kill`` case to confirm:
* SIGTERM fires
* the pre-kill write is preserved
* score reflects only writes that landed before SIGTERM
"""
import json
import os
import signal
import sys
import time

with open(os.environ["JUDGE_MARATHON_MANIFEST"], encoding="utf-8") as fh:
    first = json.loads(fh.readline())

with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps({
        "id": first["id"],
        "verdict": "true",
        "code": "import JudgeProblem\ndef submission : Goal := by intro G _ h; sorry\n",
    }) + "\n")
    fh.flush()
    os.fsync(fh.fileno())

# Honour SIGTERM cleanly so the test sees a deterministic exit code.
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

while True:
    time.sleep(60)
