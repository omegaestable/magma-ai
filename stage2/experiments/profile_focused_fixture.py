"""Profile deterministic solver routes for a JSONL problem fixture."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = ROOT / "stage2" / "fixtures" / "focused_failure_rows_2026-06-14.jsonl"
SOLVER_PATH = ROOT / "stage2" / "solver" / "solver.py"


def load_solver():
    spec = importlib.util.spec_from_file_location("stage2_solver", SOLVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load solver from {SOLVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--false-time-budget", type=float, default=0.05)
    args = parser.parse_args()

    solver = load_solver()
    rows = load_rows(args.fixture)
    route_counts: Counter[str] = Counter()
    verdict_counts: Counter[str] = Counter()
    unresolved: list[str] = []

    for row in rows:
        solved = solver.solve_problem(row, false_time_budget=args.false_time_budget)
        if solved is None:
            route = "unresolved"
            verdict = "none"
            unresolved.append(str(row.get("id", "")))
        else:
            answer = solved["answer"]
            route = str(solved["route"])
            verdict = str(answer.get("verdict", ""))
        route_counts[route] += 1
        verdict_counts[verdict] += 1
        print(
            json.dumps(
                {
                    "id": row.get("id"),
                    "expected": row.get("answer"),
                    "verdict": verdict,
                    "route": route,
                },
                separators=(",", ":"),
            )
        )

    print(
        json.dumps(
            {
                "rows": len(rows),
                "routes": dict(sorted(route_counts.items())),
                "verdicts": dict(sorted(verdict_counts.items())),
                "unresolved": unresolved,
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
