#!/usr/bin/env python3
"""
build_magma_eval_benchmark.py — Create a small benchmark to test whether the
70B model can evaluate equations on the SUCC3 magma [[1,2,0],[1,2,0],[1,2,0]].

Generates 10 pairs where:
- 5 where SUCC3 HOLDS for both E1 and E2 (expected: no separation → TRUE)
- 5 where SUCC3 HOLDS for E1 but FAILS for E2 (expected: separation → FALSE)

Uses real equations from the hard3 and normal benchmarks for realism.
"""
from __future__ import annotations

import json
from pathlib import Path

from distill import check_equation, first_failing_assignment

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "data" / "benchmark"

SUCC3_TABLE = [[1, 2, 0], [1, 2, 0], [1, 2, 0]]


def load_benchmark(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    # Load real pairs
    hard3_files = sorted(BENCHMARK_DIR.glob("hard3_balanced40_*rotation0002*.jsonl"))
    normal_files = sorted(BENCHMARK_DIR.glob("normal_balanced60_*rotation0002*.jsonl"))

    all_pairs = []
    for f in hard3_files + normal_files:
        all_pairs.extend(load_benchmark(f))

    # Find pairs where SUCC3 separates (E1 holds, E2 doesn't) — these are ground-truth FALSE
    succ3_separates = []
    # Find pairs where SUCC3 does NOT separate — ground truth could be TRUE or FALSE
    succ3_no_sep = []

    for p in all_pairs:
        eq1, eq2 = p["equation1"], p["equation2"]
        e1_holds = check_equation(eq1, SUCC3_TABLE)
        e2_holds = check_equation(eq2, SUCC3_TABLE)

        if e1_holds and not e2_holds:
            succ3_separates.append(p)
        elif e1_holds and e2_holds:
            succ3_no_sep.append(p)

    print(f"SUCC3 separates: {len(succ3_separates)} pairs")
    print(f"SUCC3 no-sep (both hold): {len(succ3_no_sep)} pairs")

    # Build the test set
    # Pick 5 FALSE (separation) pairs — prioritize hard3
    false_pool = sorted(succ3_separates, key=lambda p: (0 if 'hard3' in p['id'] else 1))
    false_picks = false_pool[:5]

    # Pick 5 TRUE-ish (no separation) pairs
    true_picks = succ3_no_sep[:5]

    # Build benchmark
    test_pairs = []
    for i, p in enumerate(false_picks):
        eq1, eq2 = p["equation1"], p["equation2"]
        failure = first_failing_assignment(eq2, SUCC3_TABLE)
        test_pairs.append({
            "id": f"magma_eval_{i:03d}",
            "equation1": eq1,
            "equation2": eq2,
            "answer": False,
            "source_id": p["id"],
            "succ3_e1_holds": True,
            "succ3_e2_holds": False,
            "succ3_e2_failure": {
                "assignment": failure["assignment"],
                "lhs": failure["lhs_value"],
                "rhs": failure["rhs_value"],
            } if failure else None,
        })
        print(f"\nFALSE #{i}: {p['id']}")
        print(f"  E1: {eq1}")
        print(f"  E2: {eq2}")
        if failure:
            print(f"  E2 fails at: {failure['assignment']} → LHS={failure['lhs_value']}, RHS={failure['rhs_value']}")

    for i, p in enumerate(true_picks):
        test_pairs.append({
            "id": f"magma_eval_{len(false_picks)+i:03d}",
            "equation1": p["equation1"],
            "equation2": p["equation2"],
            "answer": True,
            "source_id": p["id"],
            "succ3_e1_holds": True,
            "succ3_e2_holds": True,
        })
        print(f"\nTRUE #{i}: {p['id']}")
        print(f"  E1: {p['equation1']}")
        print(f"  E2: {p['equation2']}")

    # Write benchmark
    out_path = BENCHMARK_DIR / "magma_eval_test_10.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for tp in test_pairs:
            f.write(json.dumps(tp) + "\n")
    print(f"\nWrote {len(test_pairs)} pairs to {out_path}")


if __name__ == "__main__":
    main()
