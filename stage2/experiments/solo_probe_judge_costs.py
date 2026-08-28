"""Diagnosis-only: measure the real Lean-judge wall cost of the two Solo
"free" fallbacks -- the insurance reflexive `exact h` certificate and the
speculative grind certificate -- against a control that must be accepted.

Read-only w.r.t. the solver. One judge process; run on an otherwise quiet box.
    PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe stage2/experiments/solo_probe_judge_costs.py
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "experiments"))
import judge_rows as JR  # noqa: E402  (sets judge env + sys.path)
import solver as S  # noqa: E402


def run(problem, verdict, code, label):
    from judge.verify import verify_answer
    t0 = time.monotonic()
    try:
        res = verify_answer(JR.to_judge_problem(problem),
                            json.dumps({"verdict": verdict, "code": code}))
        status, err = res.get("status"), res.get("error_code")
    except Exception as exc:  # noqa: BLE001
        status, err = "infra_error", f"{type(exc).__name__}: {exc}"
    print(json.dumps({"label": label, "id": problem.get("id"),
                      "status": status, "error_code": err,
                      "bytes": len(code.encode()),
                      "seconds": round(time.monotonic() - t0, 1)}), flush=True)


def main():
    cat = JR.all_problems()
    ids = sys.argv[1:] or ["normal_0001"]
    for rid in ids:
        p = cat[rid]
        S.set_effort("fast"); S.clear_term_caches()
        rec = S.solve_problem(p)
        if rec is not None:
            run(p, rec["answer"]["verdict"], rec["answer"]["code"],
                f"control:{rec['route']}")
        run(p, "true", S.reflexive_true_certificate(), "insurance_reflexive")
        gvars = S.parse_equation(str(p["equation2"]))["variables"]
        run(p, "true", S.grind_true_certificate(gvars), "speculative_grind")


main()
