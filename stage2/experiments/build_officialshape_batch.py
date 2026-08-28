#!/usr/bin/env python3
"""Draw an ETP batch whose *shape* matches the official hard/extra-hard sets.

Every unseen sweep so far was a uniform catalog draw (91.3% of the order-4
catalog is a 4-operation law, so a uniform draw is 91.3% 4-op hypotheses).
The HF `evaluation_hard` / `evaluation_extra_hard` sets - the two that carry
the private evaluation's own category names - are not shaped like that at all:
they are 54% 3-operation hypotheses, a ~7x enrichment over the catalog.

This script builds a batch matched to the pooled hard+extra-hard joint
distribution over (eq1 operation count, eq1 variable count, TRUE/FALSE), by
*conditional* sampling from the full ETP matrix - which is exactly importance
sampling from a uniform draw, without needing to draw and discard millions of
rows.  Within a cell the pair is drawn uniformly (candidate eq1 ids are
weighted by how many eq2 ids carry the requested label, so the result is
uniform over the pairs in that cell, not merely over eq1).

The result is a STRATIFIED batch (rail 18): its solve rate is comparable to
another shape-matched batch, never to a uniform sweep's.

Usage:
    python stage2/experiments/build_officialshape_batch.py \
        --count 250 --seed 20260827 \
        --out stage2/results/etp-officialshape-250-2026-08-27.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))

from population_profile import HF, eq_shape, load  # noqa: E402
from spotcheck import ETPMatrix  # noqa: E402

TARGET_SETS = ("evaluation_hard", "evaluation_extra_hard")


def target_joint(count: int) -> dict[tuple[int, int, bool], int]:
    """(eq1_ops, eq1_vars, label) -> how many rows the batch should carry."""
    rows: list[dict] = []
    for name in TARGET_SETS:
        rows.extend(load(HF / f"{name}.jsonl"))
    counts = Counter()
    for row in rows:
        o1, v1, _ = eq_shape(row["equation1"])
        counts[(o1, v1, bool(row["answer"]))] += 1
    n = len(rows)
    # largest-remainder rounding onto `count`
    exact = {k: count * v / n for k, v in counts.items()}
    floors = {k: int(v) for k, v in exact.items()}
    short = count - sum(floors.values())
    for k in sorted(exact, key=lambda k: exact[k] - floors[k], reverse=True)[:short]:
        floors[k] += 1
    return {k: v for k, v in floors.items() if v}


def load_exclusions(paths: list[Path]) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rows = []
        if path.suffix == ".jsonl":
            for ln in text.splitlines():
                if not ln.strip():
                    continue
                try:
                    rows.append(json.loads(ln))
                except json.JSONDecodeError:
                    continue  # not every *.jsonl in results/ is pure jsonl
        else:
            try:
                rows = json.loads(text)
            except json.JSONDecodeError:
                continue
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict) and "eq1_id" in row and "eq2_id" in row:
                try:
                    out.add((int(row["eq1_id"]), int(row["eq2_id"])))
                except (TypeError, ValueError):
                    continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=250)
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    excl_paths = sorted((REPO_ROOT / "stage2" / "results").glob("*.jsonl"))
    excl_paths += sorted((REPO_ROOT / "stage2" / "experiments").glob("*.jsonl"))
    excl_paths += sorted((REPO_ROOT / "data" / "stage2_official_problems").glob("*.json*"))
    excl_paths += sorted((REPO_ROOT / "data" / "hf_cache").glob("*.jsonl"))
    excluded = load_exclusions(excl_paths)
    print(f"excluding {len(excluded)} (eq1,eq2) pairs from {len(excl_paths)} files")

    want = target_joint(args.count)
    print(f"target cells ({sum(want.values())} rows):")
    for k in sorted(want):
        print(f"   eq1 ops={k[0]} vars={k[1]} {'TRUE ' if k[2] else 'FALSE'}: {want[k]}")

    etp = ETPMatrix()
    rng = random.Random(args.seed)

    # catalog ids bucketed by (ops, vars)
    buckets: dict[tuple[int, int], list[int]] = {}
    for idx, text in enumerate(etp.equations, start=1):
        o, v, _ = eq_shape(text)
        buckets.setdefault((o, v), []).append(idx)

    rows: list[dict] = []
    drawn: set[tuple[int, int]] = set()
    shortfall: dict = {}
    for cell in sorted(want):
        ops, nvars, label = cell
        need = want[cell]
        cands = buckets.get((ops, nvars), [])
        # weight each candidate eq1 by how many eq2 carry the wanted label, so
        # the draw is uniform over *pairs* in the cell rather than over eq1.
        weights: list[int] = []
        for i in cands:
            row = etp.outcomes[i - 1]
            k = sum(1 for s in row if s.endswith("_true") == label)
            weights.append(k)
        if not cands or sum(weights) == 0:
            shortfall[str(cell)] = need
            continue
        got = 0
        attempts = 0
        while got < need and attempts < 20000:
            attempts += 1
            i = rng.choices(cands, weights=weights, k=1)[0]
            row = etp.outcomes[i - 1]
            js = [j for j in range(1, etp.n + 1)
                  if j != i and row[j - 1].endswith("_true") == label
                  and (i, j) not in excluded and (i, j) not in drawn]
            if not js:
                continue
            j = rng.choice(js)
            drawn.add((i, j))
            problem = etp.problem(i, j)
            problem["id"] = f"osh_{i}_{j}"
            rows.append(problem)
            got += 1
        if got < need:
            shortfall[str(cell)] = need - got

    rng.shuffle(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_true = sum(1 for r in rows if r["answer"])
    print(f"\nwrote {len(rows)} rows ({n_true} TRUE / {len(rows)-n_true} FALSE) to {args.out}")
    if shortfall:
        print("SHORTFALL:", shortfall)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
