"""Marathon harness fixture: a chatty solver must not OOM the runner.

Pre-fix the runner appended every stderr line to an unbounded list. A
solver that streams gigabytes of stderr could exhaust the runner's
memory before the wall budget kicks in. The runner now keeps a rolling
deque (``maxlen=_MAX_DRAIN_LINES_PER_STREAM``) with per-line
truncation; this fixture pumps a few hundred thousand lines and
confirms the run still completes cleanly under a tight wall budget.

The fixture also writes one valid answer line so scoring has a reason
to attribute a status. Without that, the harness assertion below would
need to special-case zero-write runs.
"""
import json
import os
import sys

# Stream a lot of stderr. ~200_000 lines × ~30 bytes ≈ 6 MB of stderr
# spam. Without bounded I/O this would all live in the runner's RAM.
for i in range(200_000):
    print(f"chatty {i}", file=sys.stderr, flush=False)
sys.stderr.flush()

# Also fire a single oversized line to exercise the per-line truncation.
print("X" * 8192, file=sys.stderr, flush=True)

# Write one trivially-malformed answer so the run produces a row but
# scoring marks it ``malformed`` (we don't want this fixture to affect
# the score-with-lean assertions of unrelated cases — the harness
# assertion here only checks the runner's lifecycle, not the score).
with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps({
        "id": "stderr_flood_probe",
        "verdict": "true",
        "code": "(stderr_flood probe)",
    }) + "\n")
