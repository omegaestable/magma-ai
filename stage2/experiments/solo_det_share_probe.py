"""Diagnosis-only: does the Solo deterministic pass USE its 1980 s?

`run_solo` gives the deterministic ladder SOLO_DETERMINISTIC_SHARE (0.55) of
3600 s and hands the rest to the LLM lane (measured 0 accepts / 433 real
calls). Raising the share is only worth anything if the `deep` pass is
actually clock-bound. Every engine budget is a fixed constant scaled by the
tier, so the pass may well self-terminate far below the deadline -- in which
case the share is irrelevant and the lever is engine budgets, not the split.

Measures: wall seconds until solve_problem returns, at `deep`, with a hard
deadline of CAP seconds, on rows the sweeps recorded as misses.

    PYTHONIOENCODING=utf-8 ./.venv311/Scripts/python.exe \
        stage2/experiments/solo_det_share_probe.py <cap_seconds> <n_order5> <n_order4>
"""
from __future__ import annotations
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOLVER = REPO / "stage2" / "solver"


def one(args):
    cap, problem = args
    sys.path.insert(0, str(SOLVER))
    import solver as S
    S.set_effort("deep")
    S.clear_term_caches()
    S.set_hard_deadline(time.monotonic() + cap)
    t0 = time.monotonic()
    try:
        rec = S.solve_problem(problem)
        route = rec["route"] if rec else None
    except Exception as exc:  # noqa: BLE001
        route = f"crash:{type(exc).__name__}"
    return {"id": problem.get("id"), "route": route,
            "seconds": round(time.monotonic() - t0, 1), "cap": cap}


def main():
    cap = float(sys.argv[1]) if len(sys.argv) > 1 else 900.0
    n5 = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    n4 = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    rows = []
    for path, n in ((REPO/"stage2/results/order5-misses-first40.jsonl", n5),
                    (REPO/"stage2/results/merged-order4-misses-218.jsonl", n4)):
        picked = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or picked >= n:
                continue
            rows.append(json.loads(line))
            picked += 1
    with ProcessPoolExecutor(max_workers=4) as ex:
        for r in ex.map(one, [(cap, r) for r in rows]):
            print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main()
