"""Marathon harness fixture: stderr without newlines must not OOM the runner.

Pre-fix the runner's drain loop used ``stream.readline()``, which
buffers everything up to the next ``\\n``. A solver that writes
hundreds of megabytes of stderr *without* a newline could OOM the
runner before the per-line truncation step ran.

The drain loop now reads in fixed-size chunks and emits a truncated
partial line whenever the buffer crosses ``_MAX_DRAIN_LINE_BYTES``,
so a newline-less stream is bounded the same way a chatty one is.

This fixture writes ~16 MB of stderr in 1 MB chunks, none containing
a newline, and is sized so the solver finishes well under the wall
budget. The harness assertion is the run completes cleanly and the
captured stderr_tail is bounded.
"""
import json
import os
import sys

# 1 MB chunk, no newline anywhere.
chunk = "X" * (1024 * 1024)

# Write 16 MB of newline-less stderr. Pre-fix this ~doubles runner RSS;
# post-fix it should be bounded by the per-line cap (~1 KB) plus the
# 4 KB chunk size, regardless of total bytes streamed.
for _ in range(16):
    sys.stderr.write(chunk)
sys.stderr.flush()

# Drop a trivially-malformed answer so the run produces a row that
# scoring can attribute. The harness assertion focuses on lifecycle,
# not score, but having a row makes the assertion site uniform with
# the other I/O regressions.
with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps({
        "id": "stderr_no_newline_probe",
        "verdict": "true",
        "code": "(stderr_no_newline probe)",
    }) + "\n")
