"""Does the raised Solo deterministic share + the overtime slot buy rows?

The diagnosis (`Solo.md`, SOLO-1) measured `solo_det_share_probe.py 900 6 2`:
7 of 8 known-miss rows consumed 100% of a 900 s `deep` deadline and 2 closed
(`order5_46513_41697` at 3.5 s, `etp_2923_156` by `completion:join` at 235.5 s).
That says the pass is CLOCK-bound, so `SOLO_DETERMINISTIC_SHARE = 0.55` was a
real cap. This probe measures the two things the pacing change actually adds,
separately, so a null result is attributable:

  --mode det       one `solve_problem` at `deep` under the NEW deterministic
                   deadline (0.85 x 3600 = 3060 s) -- the pass itself.
  --mode overtime  one `completion_prove(..., escalate=True)` at the overtime
                   slot's budget on a row the pass already failed -- exactly
                   what `solo_overtime_completion` does, and the only lever
                   that reaches past `COMPLETION_ROUTE_MAX_SECONDS = 300`.

Rail 22: cap the pool at 3 workers and record the machine's load next to any
wall clock this prints.

    PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe \
        stage2/experiments/solo_pacing_probe.py --mode overtime --cap 900 \
        --workers 3 --ids order5_...,etp_481_3050
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOLVER = REPO / "stage2" / "solver"
# The miss ledgers are gitignored, so a worktree checkout does not carry them.
# `--sources` points at whichever tree does; these are the defaults.
DEFAULT_SOURCES = (
    "stage2/results/order5-misses-first40.jsonl",
    "stage2/results/merged-order4-misses-218.jsonl",
)


def _one(args):
    mode, cap, problem = args
    sys.path.insert(0, str(SOLVER))
    import solver as S

    S.set_effort("deep")
    S.clear_term_caches()
    S.arm_memory_guard()
    S.reset_memory_reclaims()
    S.set_hard_deadline(time.monotonic() + cap)
    started = time.monotonic()
    try:
        if mode == "det":
            record = S.solve_problem(problem)
            route = record["route"] if record else None
        else:
            record = S.solo_overtime_completion(problem, cap)
            route = record["route"] if record else None
    except Exception as exc:  # noqa: BLE001
        route = f"crash:{type(exc).__name__}: {exc}"
    return {
        "id": problem.get("id"),
        "mode": mode,
        "route": route,
        "seconds": round(time.monotonic() - started, 1),
        "cap": cap,
        "label": problem.get("label"),
    }


def _load(sources: list[Path], ids: set[str] | None, limit: int) -> list[dict]:
    rows: list[dict] = []
    for path in sources:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if ids is not None:
                if row.get("id") in ids:
                    rows.append(row)
            elif len(rows) < limit:
                rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("det", "overtime"), default="overtime")
    parser.add_argument("--cap", type=float, default=900.0)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--ids", default="")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--root", default=str(REPO),
                        help="tree holding stage2/results/*.jsonl")
    args = parser.parse_args()

    root = Path(args.root)
    sources = [root / name for name in DEFAULT_SOURCES]
    ids = {i for i in args.ids.split(",") if i} or None
    rows = _load(sources, ids, args.limit)
    if not rows:
        print("no rows selected", file=sys.stderr)
        return 2
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for result in pool.map(_one, [(args.mode, args.cap, row) for row in rows]):
            print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
