#!/usr/bin/env python3
"""Keep only the pairs a small-model search cannot refute — the "hard region".

Motivation, measured 2026-08-25. A random pair of high-order laws is almost
never an implication, and almost always refutable by a tiny magma. Two order-6
(≤2 variable) pilots of 200 rows each came back **200/200 FALSE with a p50 of
8 ms**: the named-witness portfolio disposed of essentially every row before any
search started. Sweeping 20,000 such rows would burn hours to learn nothing.

The cause is not the order — it is the variable cap, and the labelled order-4
matrix proves it: over all 22,028,942 order-≤4 pairs the base TRUE rate is
**37.10%**, but restricted to pairs with ≤2 variables on both sides it is
**4.17%**, and for a 4-operation ≤2-variable hypothesis against any ≤2-variable
goal it is **2.87%**. Fewer variables means a more constraining law, which means
two unrelated laws almost never imply one another.

So a uniform draw is the wrong instrument for a low-variable track. This filter
builds a **stratified** one: it discards any pair for which an independent
small-model search finds a magma satisfying eq1 and refuting eq2. What survives
is every TRUE pair plus the FALSE pairs whose witness is not small — exactly the
population that exercises the solver. Measured survival on order-6 ≤2 vars:
**14.1%** of pairs, at 13.5 ms each.

Report any batch built this way as **stratified, not random**. Its solve rate is
not comparable to a uniform sweep's, and its FALSE rows are biased hard.

The filter deliberately uses `stage2/tests/oracles.py`, which by contract shares
no code with `solver.py`, rather than the solver's own witness portfolio — so
"survivor" is not defined by the thing being measured.

Usage:
    python stage2/experiments/filter_hard_region.py \
        --in stage2/results/order6-sweep-20k-2026-08-25.jsonl \
        --out stage2/results/order6-hard-20k-2026-08-25.jsonl \
        --target 20000 --workers 12
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))

import oracles  # noqa: E402
import solver as S  # noqa: E402


def survives(problem: dict, fin3_samples: int) -> dict | None:
    """None if a small model of eq1 refutes eq2 (certainly FALSE, and cheaply
    so); otherwise the problem, annotated with why it survived."""
    try:
        eq1 = S.parse_equation(str(problem["equation1"]))
        eq2 = S.parse_equation(str(problem["equation2"]))
    except (KeyError, ValueError):
        return None
    battery = oracles.model_battery(eq1, [], fin3_samples=fin3_samples, seed=17)
    nontrivial = oracles.nontrivial_model_count(battery)
    row = dict(problem)
    row["filter_nontrivial_models"] = nontrivial
    if nontrivial == 0:
        # Only the trivial magma satisfies eq1 in this battery. That is a
        # *candidate* collapse hypothesis, not a proof of one (the battery is a
        # finite sample) — but a collapse hypothesis implies every goal, so this
        # stratum is where order-6 TRUE rows concentrate.
        row["filter_reason"] = "collapse_candidate"
        return row
    try:
        oracles.model_check_true(eq2, battery)
    except oracles.OracleError:
        return None
    row["filter_reason"] = "no_small_countermodel"
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--target", type=int, default=0,
                    help="stop once this many survivors are found (0 = filter "
                         "the whole input)")
    ap.add_argument("--fin3-samples", type=int, default=200)
    ap.add_argument("--workers", type=int,
                    default=max(1, min(12, (os.cpu_count() or 2) - 2)))
    args = ap.parse_args()

    problems = [json.loads(line) for line
                in args.src.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    started = time.monotonic()
    kept: list[dict] = []
    worker = partial(survives, fin3_samples=args.fin3_samples)
    checked = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(worker, problems, chunksize=16):
            checked += 1
            if row is not None:
                kept.append(row)
            if checked % 2000 == 0:
                print(f"  {checked}/{len(problems)} checked, {len(kept)} kept "
                      f"({time.monotonic() - started:.0f}s)", flush=True)
            if args.target and len(kept) >= args.target:
                break

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for row in kept:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    reasons: dict[str, int] = {}
    for row in kept:
        reasons[row["filter_reason"]] = reasons.get(row["filter_reason"], 0) + 1
    rate = 100.0 * len(kept) / max(1, checked)
    print(f"kept {len(kept)}/{checked} = {rate:.2f}% in "
          f"{time.monotonic() - started:.0f}s -> {args.out}")
    print(f"  survival reasons: {reasons}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
