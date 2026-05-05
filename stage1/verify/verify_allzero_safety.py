#!/usr/bin/env python3
"""
verify_allzero_safety.py — Check if the "all-zeros" SUCC3 check produces false positives.

The Phase 2 test checks: E1 HOLDS on SUCC3(all=0) and E2 FAILS on SUCC3(all=0).
This is an approximation of: E1 holds UNIVERSALLY on SUCC3 and E2 fails somewhere.

Risk: E1 holds on all=0 but NOT universally → false positive (says FALSE on TRUE pair).

This script checks all TRUE pairs in the benchmarks for this risk.
"""
import json
import itertools
from pathlib import Path
from distill import check_equation, parse_equation_tree, eval_tree, _collect_tree_vars

ROOT = Path(__file__).resolve().parent
SUCC3 = [[1, 2, 0], [1, 2, 0], [1, 2, 0]]


def eval_equation_on_assignment(eq: str, table, assignment: dict) -> bool:
    """Check if equation holds for a specific assignment."""
    lhs, rhs = parse_equation_tree(eq)
    return eval_tree(lhs, assignment, table) == eval_tree(rhs, assignment, table)


def check_allzero(eq: str, table) -> bool:
    """Check if equation holds when ALL variables = 0."""
    lhs, rhs = parse_equation_tree(eq)
    variables = set()
    _collect_tree_vars(lhs, variables)
    _collect_tree_vars(rhs, variables)
    assignment = {v: 0 for v in variables}
    return eval_tree(lhs, assignment, table) == eval_tree(rhs, assignment, table)


def main():
    hard3_file = sorted((ROOT / "data" / "benchmark").glob("hard3_balanced40_*rotation0002*.jsonl"))[-1]
    normal_file = sorted((ROOT / "data" / "benchmark").glob("normal_balanced60_*rotation0002*.jsonl"))[-1]

    print("=" * 70)
    print("FALSE POSITIVE CHECK: all-zeros SUCC3 on TRUE pairs")
    print("=" * 70)

    false_positives = []
    total_true = 0

    for f in [hard3_file, normal_file]:
        print(f"\n--- {f.name} ---")
        for line in open(f):
            row = json.loads(line.strip())
            if row["answer"] is not True:
                continue
            total_true += 1
            eq1, eq2 = row["equation1"], row["equation2"]

            e1_allzero = check_allzero(eq1, SUCC3)
            e2_allzero = check_allzero(eq2, SUCC3)
            e1_universal = check_equation(eq1, SUCC3)

            # False positive = E1 holds on all=0 AND E2 fails on all=0
            if e1_allzero and not e2_allzero:
                false_positives.append({
                    "id": row["id"],
                    "eq1": eq1,
                    "eq2": eq2,
                    "e1_universal": e1_universal,
                })
                print(f"  FALSE POSITIVE: {row['id']}")
                print(f"    E1: {eq1}")
                print(f"    E2: {eq2}")
                print(f"    E1 all=0: HOLDS, E2 all=0: FAILS")
                print(f"    E1 universal: {e1_universal}")

    print(f"\n{'='*70}")
    print(f"RESULT: {len(false_positives)} false positives out of {total_true} TRUE pairs")
    if not false_positives:
        print("  ALL-ZEROS CHECK IS SAFE on these benchmarks!")
    else:
        print("  WARNING: all-zeros check would produce false flags!")
        for fp in false_positives:
            print(f"    {fp['id']}: E1 universal={fp['e1_universal']}")

    # Also check: on FALSE pairs, does all=0 check catch the same pairs as full check?
    print(f"\n{'='*70}")
    print("COVERAGE CHECK: all-zeros vs full check on FALSE pairs")
    print("=" * 70)

    for f in [hard3_file, normal_file]:
        print(f"\n--- {f.name} ---")
        for line in open(f):
            row = json.loads(line.strip())
            if row["answer"] is not False:
                continue
            eq1, eq2 = row["equation1"], row["equation2"]

            e1_allzero = check_allzero(eq1, SUCC3)
            e2_allzero = check_allzero(eq2, SUCC3)
            e1_universal = check_equation(eq1, SUCC3)
            e2_universal = check_equation(eq2, SUCC3)

            full_sep = e1_universal and not e2_universal
            zero_sep = e1_allzero and not e2_allzero

            if full_sep or zero_sep:
                match = "MATCH" if full_sep == zero_sep else "MISMATCH"
                print(f"  {match}: {row['id']} full={full_sep} zero={zero_sep}")
                if full_sep != zero_sep:
                    print(f"    E1: {eq1}")
                    print(f"    E2: {eq2}")


if __name__ == "__main__":
    main()
