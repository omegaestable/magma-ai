"""Sweep model-finder settings against the solver's remaining FALSE misses.

Uses the solver's own `local_model_counterexample`, so whatever wins here is
directly a constant change in solver.py. Every hit is re-verified by
`table_is_counterexample`.
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

CONFIGS = [
    {"name": "cur_4_5_b6", "sizes": (4, 5), "time_budget": 6.0, "max_flips": 4000},
    {"name": "b12_4_5", "sizes": (4, 5), "time_budget": 12.0, "max_flips": 4000},
    {"name": "b12_4_5_6", "sizes": (4, 5, 6), "time_budget": 12.0, "max_flips": 4000},
    {"name": "b20_4_5_6", "sizes": (4, 5, 6), "time_budget": 20.0, "max_flips": 8000},
    {"name": "b20_4_5_6_7", "sizes": (4, 5, 6, 7), "time_budget": 20.0, "max_flips": 8000},
    {"name": "b20_shortrestart", "sizes": (4, 5, 6), "time_budget": 20.0, "max_flips": 800},
    {"name": "b20_noise40", "sizes": (4, 5, 6), "time_budget": 20.0,
     "max_flips": 4000, "noise": 0.40},
    {"name": "b20_noise10", "sizes": (4, 5, 6), "time_budget": 20.0,
     "max_flips": 4000, "noise": 0.10},
]


def _load_misses(audit_name: str) -> list[dict]:
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
            if p is not None and p.get("answer") is False and p["id"] not in seen:
                seen.add(p["id"])
                out.append(p)
    return out


def _attempt(job):
    problem, config = job
    import solver as S

    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    kwargs = {k: v for k, v in config.items() if k != "name"}
    started = time.monotonic()
    found = S.local_model_counterexample(eq1, eq2, **kwargs)
    elapsed = time.monotonic() - started
    if found is None:
        return config["name"], problem["id"], False, elapsed
    n, table, _route = found
    assert S.table_is_counterexample(eq1, eq2, table), "unsound witness!"
    return config["name"], problem["id"], True, elapsed


def main() -> int:
    audit = sys.argv[1] if len(sys.argv) > 1 else "audit-ws3.json"
    misses = _load_misses(audit)
    print(f"{len(misses)} remaining labelled-FALSE misses\n")

    jobs = [(p, c) for c in CONFIGS for p in misses]
    workers = max(1, min(16, (os.cpu_count() or 2) - 2))
    results = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for name, pid, ok, secs in pool.map(_attempt, jobs, chunksize=1):
            results.setdefault(name, {})[pid] = (ok, secs)

    print(f"{'config':20s} {'cracked':>8s} {'total_s':>9s}  worst_s")
    for c in CONFIGS:
        r = results.get(c["name"], {})
        won = sum(1 for ok, _ in r.values() if ok)
        tot = sum(s for _, s in r.values())
        worst = max((s for _, s in r.values()), default=0)
        print(f"{c['name']:20s} {won:5d}/{len(misses):<3d} {tot:9.1f} {worst:8.1f}")

    best = max(CONFIGS, key=lambda c: sum(
        1 for ok, _ in results.get(c["name"], {}).values() if ok))
    print(f"\nbest: {best['name']}")
    ids = sorted(p for p, (ok, _) in results[best["name"]].items() if ok)
    print(f"cracked ids: {ids}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
