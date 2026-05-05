"""Marathon harness fixture: writes two lines for the same id.

The score path must take the LAST line. Tests:
* duplicate ids do not crash the score path
* last-write-wins is honoured in summary

The first write is intentionally malformed (missing 'code'). The
second write is a brute-forceable counterexample for ``normal_0003``,
so when Lean is available the case lands as ``accepted``; without
Lean it lands as ``incorrect`` (and the harness still asserts the
*last* line's content was used, regardless of Lean availability).
"""
import json
import os

OUT = os.environ["JUDGE_MARATHON_OUTPUT"]
PID = "normal_0003"


def write(entry):
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


# First write: malformed (no 'code').
write({"id": PID, "verdict": "true"})

# Second write: a real false certificate the brute-forcer would also produce.
table = [[0, 1], [0, 1]]
table_str = json.dumps(table)
code = (
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
)
write({"id": PID, "verdict": "false", "code": code})
