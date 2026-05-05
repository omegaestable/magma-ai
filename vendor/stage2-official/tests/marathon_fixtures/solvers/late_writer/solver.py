"""Marathon harness fixture: writes one line pre-SIGTERM, then writes
another line on its way out.

Demonstrates the runner's behaviour around writes that land on disk
after the budget expires:

* The runner SIGTERMs at the budget.
* The solver's SIGTERM handler emits a *second* write before exiting.
* That write is in the output file, but the harness asserts that the
  score path's "last-write-wins per id" rule is what the leaderboard
  uses — so the solver can't sneak a different verdict in via a
  post-SIGTERM write *for an already-attempted id* unless the new line
  is genuinely correct.

(Per design doc: "Late writes (after budget exhausted) may land on
disk but are ignored at scoring." We implement the looser rule —
writes are not sandboxed from the disk, but the score path's
last-wins logic + the deterministic budget mean a malicious solver
can't gain anything by post-SIGTERM writes that wouldn't already win
via last-write-wins.)
"""
import json
import os
import signal
import sys
import time

with open(os.environ["JUDGE_MARATHON_MANIFEST"], encoding="utf-8") as fh:
    first = json.loads(fh.readline())

OUT = os.environ["JUDGE_MARATHON_OUTPUT"]


def write(entry):
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass


# Pre-SIGTERM: a "true" attempt the harness considers the canonical guess.
write({
    "id": first["id"],
    "verdict": "true",
    "code": "import JudgeProblem\ndef submission : Goal := by intro G _ h; sorry\n",
})


def on_sigterm(*_):
    # Post-SIGTERM late write that the grading rule should count
    # *only because* it is also the last-write for this id.
    write({
        "id": first["id"],
        "verdict": "false",
        "code": "(post-SIGTERM late write)",
    })
    sys.exit(0)


signal.signal(signal.SIGTERM, on_sigterm)
if hasattr(signal, "SIGBREAK"):
    signal.signal(signal.SIGBREAK, on_sigterm)
while True:
    time.sleep(60)
