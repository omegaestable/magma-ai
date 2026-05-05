"""Marathon harness fixture: probes whether scratch dir is empty at start.

Writes a marker line to the output JSONL describing what it found in
scratch. The harness asserts the marker reports an empty scratch even
when the harness pre-populates a sentinel file before the run.

Tests the runner's anti-persist guarantee: scratch is wiped each run.
"""
import json
import os
from pathlib import Path

scratch = Path(os.environ["JUDGE_MARATHON_SCRATCH_DIR"])
# Filter out current-run files the runner places. ``manifest.jsonl`` is
# the manifest copy the runner writes for the solver to read.
# (Pre-2026-04-30 the proxy also wrote tokens_used.txt here; that file
# now lives in a runner-private state dir, but the names are kept in the
# filter as defense-in-depth in case the contract regresses.)
_RUNNER_OWNED = {"manifest.jsonl", "tokens_used.txt", "tokens_used.tmp"}
entries = sorted(
    p.name for p in scratch.iterdir() if p.name not in _RUNNER_OWNED
)
marker = {
    "id": "anti_persist_probe",
    "verdict": "true",
    "code": "(harness probe)",
    "scratch_entries": entries,
}
with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(marker) + "\n")
