#!/usr/bin/env python3
"""Probe whether the solver's bounded closure can derive canonical basis laws."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import time
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOLVER = REPO_ROOT / "stage2" / "solver" / "solver.py"

CASES = (
    ("E1686", "x = (y * x) * ((x * y) * z)", "E2", "a = b"),
    ("E871", "x = y * ((x * x) * (x * z))", "E2", "a = b"),
    ("E4208", "x * y = ((z * y) * x) * x", "E41", "a * a = b * c"),
    ("E2329", "x = (y * (y * (x * x))) * z", "E46", "a * b = c * d"),
)


def load_solver(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("derived_basis_probe_solver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import solver from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solver", type=Path, default=DEFAULT_SOLVER)
    parser.add_argument("--depth", type=int, default=7)
    parser.add_argument("--pool-limit", type=int, default=28)
    parser.add_argument("--frontier-limit", type=int, default=6000)
    parser.add_argument("--max-fills", type=int, default=1200)
    parser.add_argument("--term-slack", type=int, default=14)
    parser.add_argument("--depth-slack", type=int, default=4)
    parser.add_argument("--time-budget", type=float, default=5.0)
    args = parser.parse_args()

    solver = load_solver(args.solver.resolve())
    hits = 0
    for source_id, source_text, basis_id, basis_text in CASES:
        started = time.perf_counter()
        result = solver._closure_proof_expr_impl(
            solver.parse_equation(source_text),
            solver.parse_equation(basis_text),
            route_name="probe:derived_basis",
            chain_max_depth=args.depth,
            pool_limit=args.pool_limit,
            frontier_limit=args.frontier_limit,
            max_fills=args.max_fills,
            term_slack=args.term_slack,
            depth_slack=args.depth_slack,
            time_budget=args.time_budget,
        )
        elapsed = time.perf_counter() - started
        if result is None:
            print(f"{source_id}->{basis_id} miss elapsed={elapsed:.3f}s")
            continue
        hits += 1
        print(f"{source_id}->{basis_id} hit elapsed={elapsed:.3f}s proof_chars={len(result[1])}")
    print(f"hits={hits}/{len(CASES)}")
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
