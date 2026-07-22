"""Benchmark the WS3 model finder against the solver's known FALSE misses.

Only rows whose ground-truth label is FALSE and which the current solver
skips. Any row cracked here is a row the packaged solver would gain, and the
witness is self-verifying (the judge re-checks the table), so these wins carry
no soundness risk.
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
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))


def _load_misses() -> list[dict]:
    import solver as S  # noqa: F401  (import cost paid in workers too)

    audit = json.loads(
        (REPO_ROOT / "stage2" / "results" / "audit-2026-07-21.json")
        .read_text(encoding="utf-8"))
    problems: dict[str, dict] = {}
    for name in ("normal", "hard1", "hard2", "hard3"):
        path = REPO_ROOT / "data" / "stage2_official_problems" / f"{name}.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                problems[d["id"]] = d

    misses = []
    for payload in audit["sets"].values():
        for row in payload["rows"]:
            if row.get("status") == "solved":
                continue
            p = problems.get(row["id"])
            if p is not None and p.get("answer") is False:
                misses.append(p)
    # de-duplicate (sample sets overlap normal)
    seen, out = set(), []
    for p in misses:
        if p["id"] not in seen:
            seen.add(p["id"])
            out.append(p)
    return out


def _attempt(problem: dict) -> dict:
    import modelfinder as MF
    import solver as S

    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    started = time.monotonic()
    found = MF.find_counterexample(eq1, eq2, sizes=(4, 5, 6), time_budget=25.0)
    elapsed = round(time.monotonic() - started, 2)
    if found is None:
        return {"id": problem["id"], "found": False, "seconds": elapsed}
    n, table, route = found
    # Re-verify with the solver's own independent checker.
    assert S.table_is_counterexample(eq1, eq2, table), "unsound witness!"
    return {"id": problem["id"], "found": True, "n": n, "route": route,
            "table": table, "seconds": elapsed}


def main() -> int:
    misses = _load_misses()
    print(f"{len(misses)} labelled-FALSE rows the solver currently skips")
    workers = max(1, min(16, (os.cpu_count() or 2) - 2))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_attempt, misses))

    won = [r for r in results if r["found"]]
    print(f"\ncracked {len(won)}/{len(results)}")
    for r in sorted(won, key=lambda r: r["seconds"]):
        print(f"  {r['id']:16s} Fin{r['n']} {r['route']:16s} {r['seconds']:6.2f}s")
    out = REPO_ROOT / "stage2" / "results" / "modelfinder-false-misses.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
