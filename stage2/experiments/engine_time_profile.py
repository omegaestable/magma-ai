#!/usr/bin/env python3
"""DIAGNOSIS ONLY (2026-08-27). Per-engine wall-clock profile of solve_problem.

Wraps every engine call site named in `solve_problem_pass` with a timer, runs
the rows, and reports cumulative seconds per engine split by the verdict the
row ended up with. Answers "where does the Marathon clock go" without guessing.

Usage:
  python stage2/experiments/engine_time_profile.py --rows rows.jsonl [--limit N]
      [--effort fast|standard|deep] [--row-budget S] [--workers 4] [--out out.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOLVER_DIR = os.environ.get("MAGMA_SOLVER_DIR") or str(REPO / "stage2" / "solver")

ENGINES = (
    "find_counterexample",
    "constraint_countermodel",
    "egg_probe_route",
    "completion_probe_route",
    "equational_closure_route",
    "deep_absorption_closure_route",
    "derived_cp_closure_route",
    "projection_bootstrap_route",
    "lemma_bootstrap_route",
    "lemma_chain_bootstrap_route",
    "egg_closure_route",
    "egg_collapse_route",
    "egg_priority_bootstrap_route",
    "egg_bootstrap_route",
    "egg_ladder_route",
    "completion_route",
    "narrow_grind_true_route",
    "local_model_counterexample",
    "constraint_countermodel_wide_domain",
)

_TIMES: dict[str, float] = {}
_CALLS: dict[str, int] = {}


def _instrument(S):
    def wrap(name):
        orig = getattr(S, name)

        def timed(*a, **kw):
            t0 = time.perf_counter()
            try:
                return orig(*a, **kw)
            finally:
                dt = time.perf_counter() - t0
                _TIMES[name] = _TIMES.get(name, 0.0) + dt
                _CALLS[name] = _CALLS.get(name, 0) + 1
        timed.__name__ = name
        return timed
    for n in ENGINES:
        if hasattr(S, n):
            setattr(S, n, wrap(n))


_S = None


def _init(effort: str):
    global _S
    if SOLVER_DIR not in sys.path:
        sys.path.insert(0, SOLVER_DIR)
    import solver as S
    _instrument(S)
    S.set_effort(effort)
    _S = S


def _run(args):
    row, effort, row_budget, false_budget = args
    S = _S
    _TIMES.clear()
    _CALLS.clear()
    S.set_effort(effort)
    S.clear_term_caches()
    S.set_hard_deadline(time.monotonic() + row_budget if row_budget else None)
    t0 = time.perf_counter()
    try:
        rec = S.solve_problem(row, false_time_budget=false_budget)
    except Exception as exc:  # noqa: BLE001
        rec = None
        err = f"{type(exc).__name__}: {exc}"
    else:
        err = None
    total = time.perf_counter() - t0
    S.set_hard_deadline(None)
    return {
        "id": row.get("id"),
        "seconds": round(total, 4),
        "route": (rec or {}).get("route"),
        "verdict": (rec or {}).get("answer", {}).get("verdict") if rec else None,
        "error": err,
        "engine_seconds": {k: round(v, 4) for k, v in _TIMES.items()},
        "engine_calls": dict(_CALLS),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--effort", default="fast")
    ap.add_argument("--row-budget", type=float, default=0.0)
    ap.add_argument("--false-budget", type=float, default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    rows = []
    for line in Path(a.rows).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    if a.limit:
        rows = rows[: a.limit]

    payload = [(r, a.effort, a.row_budget, a.false_budget) for r in rows]
    out = []
    with ProcessPoolExecutor(max_workers=a.workers, initializer=_init,
                             initargs=(a.effort,)) as ex:
        for res in ex.map(_run, payload, chunksize=1):
            out.append(res)

    tot = sum(r["seconds"] for r in out)
    agg = defaultdict(float)
    calls = defaultdict(int)
    agg_true = defaultdict(float)
    agg_false = defaultdict(float)
    agg_skip = defaultdict(float)
    for r in out:
        for k, v in r["engine_seconds"].items():
            agg[k] += v
            if r["verdict"] == "true":
                agg_true[k] += v
            elif r["verdict"] == "false":
                agg_false[k] += v
            else:
                agg_skip[k] += v
        for k, v in r["engine_calls"].items():
            calls[k] += v
    solved = sum(1 for r in out if r["route"])
    print(f"rows={len(out)} solved={solved} total={tot:.1f}s "
          f"(true={sum(r['seconds'] for r in out if r['verdict']=='true'):.1f}s "
          f"false={sum(r['seconds'] for r in out if r['verdict']=='false'):.1f}s "
          f"unsolved={sum(r['seconds'] for r in out if not r['route']):.1f}s)")
    print(f"{'engine':38s} {'calls':>6s} {'sum_s':>9s} {'%tot':>6s} "
          f"{'on_TRUE':>9s} {'on_FALSE':>9s} {'on_SKIP':>9s}")
    for k, v in sorted(agg.items(), key=lambda kv: -kv[1]):
        print(f"{k:38s} {calls[k]:6d} {v:9.2f} {100*v/max(tot,1e-9):5.1f}% "
              f"{agg_true[k]:9.2f} {agg_false[k]:9.2f} {agg_skip[k]:9.2f}")
    if a.out:
        Path(a.out).write_text(json.dumps(
            {"rows": out, "aggregate": dict(agg), "calls": dict(calls),
             "on_true": dict(agg_true), "on_false": dict(agg_false),
             "on_skip": dict(agg_skip), "total_seconds": tot},
            indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
