"""Marathon harness fixture: writes a mix of valid and malformed lines.

Layout (against the 5-problem manifest):
* normal_0001: malformed (missing 'code' field)
* normal_0002: malformed (verdict='maybe')
* normal_0003: valid 'false' brute-force certificate (Lean-acceptable)
* normal_0004: NOT WRITTEN — should land as ``not_attempted``
* normal_0005: malformed (code is not a string)

Tests the score path's status mapping:
* malformed lines → 'malformed'
* unwritten ids   → 'not_attempted'
* valid 'false'   → 'accepted' (when Lean available) or 'incorrect' (otherwise)
"""
import json
import os

OUT = os.environ["JUDGE_MARATHON_OUTPUT"]


def write(entry):
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


write({"id": "normal_0001", "verdict": "true"})
write({"id": "normal_0002", "verdict": "maybe", "code": "x"})

table_str = json.dumps([[0, 1], [0, 1]])
write({
    "id": "normal_0003",
    "verdict": "false",
    "code": (
        "import JudgeProblem\n"
        "import JudgeDecide.DecideBang\n"
        "import JudgeFinOp.MemoFinOp\n"
        "open MemoFinOp\n\n"
        "def submission : Goal := by\n"
        "  let m : Magma (Fin 2) := {\n"
        f"    op := finOpTable \"{table_str}\"\n"
        "  }\n"
        "  refine \u27e8Fin 2, m, ?_\u27e9\n"
        "  decideFin!\n"
    ),
})

write({"id": "normal_0005", "verdict": "true", "code": 12345})
