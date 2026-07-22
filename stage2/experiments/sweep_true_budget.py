"""Measure how many TRUE misses fall to a bigger deterministic budget.

The solver caps its closure/critical-pair engines with constants tuned as if
wall-clock were scarce (CP = 8 s), while Marathon actually affords ~1800 s per
problem. This sweep asks the decisive question: are the remaining TRUE misses
*unreachable*, or merely *under-resourced*?

Also separates the two possible bottlenecks:
  - time        (deadline hit first)  -> raise budgets
  - search caps (frontier/fills/depth exhausted) -> raise limits
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))

CONFIGS = [
    {"name": "baseline_8s", "time_budget": 8.0},
    {"name": "time_60s", "time_budget": 60.0},
    {"name": "time_60s_wide", "time_budget": 60.0, "frontier_limit": 12000,
     "max_fills": 4000, "pool_limit": 22},
    {"name": "time_180s_wide", "time_budget": 180.0, "frontier_limit": 30000,
     "max_fills": 8000, "pool_limit": 26},
    {"name": "time_180s_deep", "time_budget": 180.0, "frontier_limit": 30000,
     "max_fills": 8000, "pool_limit": 26, "chain_max_depth": 5,
     "max_rules": 96},
]


def _load_true_misses(audit_name: str) -> list[dict]:
    audit = json.loads(
        (REPO_ROOT / "stage2" / "results" / audit_name).read_text(encoding="utf-8"))
    problems: dict[str, dict] = {}
    for name in ("normal", "hard1", "hard2", "hard3"):
        path = REPO_ROOT / "data" / "stage2_official_problems" / f"{name}.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                problems[d["id"]] = d
    seen, out = set(), []
    for payload in audit["sets"].values():
        for row in payload["rows"]:
            if row.get("status") == "solved":
                continue
            p = problems.get(row["id"])
            if p is not None and p.get("answer") is True and p["id"] not in seen:
                seen.add(p["id"])
                out.append(p)
    return out


def _attempt(job):
    problem, config = job
    import oracles
    import solver as S

    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    kwargs = {k: v for k, v in config.items() if k != "name"}
    started = time.monotonic()
    try:
        expr = S.derived_cp_closure_proof_expr(eq1, eq2, **kwargs)
    except Exception as exc:  # noqa: BLE001
        return config["name"], problem["id"], "crash", 0.0, str(exc)
    elapsed = time.monotonic() - started
    if expr is None:
        # Distinguish "ran out of clock" from "exhausted its search space".
        reason = "timeout" if elapsed >= kwargs.get("time_budget", 8.0) * 0.95 else "exhausted"
        return config["name"], problem["id"], reason, elapsed, None

    code = S.substitution_true_certificate(eq2["variables"], expr)
    try:
        oracles.check_true_exact_certificate(code, eq1, eq2)
    except oracles.OracleError as exc:
        return config["name"], problem["id"], "UNSOUND", elapsed, str(exc)
    return config["name"], problem["id"], "solved", elapsed, None


def main() -> int:
    audit = sys.argv[1] if len(sys.argv) > 1 else "audit-ws3.json"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    misses = _load_true_misses(audit)
    if limit:
        misses = misses[:limit]
    print(f"{len(misses)} labelled-TRUE misses\n", flush=True)

    workers = max(1, min(16, (os.cpu_count() or 2) - 2))
    results: dict = {}
    for config in CONFIGS:
        jobs = [(p, config) for p in misses]
        started = time.monotonic()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(_attempt, jobs, chunksize=1))
        results[config["name"]] = rows
        solved = [r for r in rows if r[2] == "solved"]
        unsound = [r for r in rows if r[2] == "UNSOUND"]
        timeout = sum(1 for r in rows if r[2] == "timeout")
        exhausted = sum(1 for r in rows if r[2] == "exhausted")
        print(f"{config['name']:18s} solved={len(solved):3d}/{len(misses)} "
              f"timeout={timeout:3d} exhausted={exhausted:3d} "
              f"unsound={len(unsound)} wall={time.monotonic()-started:6.0f}s",
              flush=True)
        for r in unsound:
            print(f"   !! UNSOUND {r[1]}: {r[4]}")

    out = REPO_ROOT / "stage2" / "results" / "true-budget-sweep.json"
    out.write_text(json.dumps(
        {k: [list(r) for r in v] for k, v in results.items()}, indent=2),
        encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
