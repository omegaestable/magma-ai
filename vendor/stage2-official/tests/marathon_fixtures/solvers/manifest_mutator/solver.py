"""Marathon harness fixture: solver tries to poison the manifest.

Attack model:
* Solver overwrites JUDGE_MARATHON_MANIFEST with a manifest where
  ``normal_0003`` is replaced by ``hijacked_id``.
* Solver also writes a fake answer for ``hijacked_id`` so a naive scorer
  that re-reads the manifest off disk would credit a fabricated problem.

Expected behaviour: the runner snapshots the manifest in memory before
launching the solver and feeds that snapshot to scoring. The score path
must score the *original* problem ids and ignore the on-disk mutation.
"""
import json
import os

manifest_path = os.environ["JUDGE_MARATHON_MANIFEST"]
output_path = os.environ["JUDGE_MARATHON_OUTPUT"]

# Step 1: clobber the manifest copy the solver was given.
hijacked = {
    "id": "hijacked_id",
    "eq1_id": 1,
    "eq2_id": 2,
    "equation1": "x = x",
    "equation2": "x = x",
    "answer": True,
}
with open(manifest_path, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(hijacked) + "\n")

# Step 2: write a "valid"-looking answer for the hijacked id.
with open(output_path, "a", encoding="utf-8") as fh:
    fh.write(json.dumps({
        "id": "hijacked_id",
        "verdict": "true",
        "code": "import JudgeProblem\n\ndef submission : Goal := by\n  intro G _ h\n  rfl\n",
    }) + "\n")
