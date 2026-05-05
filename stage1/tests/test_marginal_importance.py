#!/usr/bin/env python3
"""
test_marginal_importance.py — Phase 3.1: Which structural test matters most?

For each FALSE pair in normal-60 and hard3-40, determine which of the 4 structural
tests (LP, RP, C0, VARS) provide separation. Reports:
  1. Per-test catch count on normal FALSE pairs
  2. Pairs where ONLY one test provides separation (marginal importance)
  3. Overlap analysis — which tests are redundant
  4. Coverage gap analysis — pairs where NO test fires

This answers: "If we replace VARS with a magma check, how many normal pairs break?"
"""
from __future__ import annotations

import json
import itertools
from pathlib import Path

from distill import check_equation, first_failing_assignment, parse_equation_tree

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "data" / "benchmark"

# The 4 structural tests as magma witnesses:
# LP: "first letter left = first letter right" — equivalent to x*y=x (Left Projection)
LP_TABLE = [[0, 0], [1, 1]]

# RP: "last letter left = last letter right" — equivalent to x*y=y (Right Projection)
RP_TABLE = [[0, 1], [0, 1]]

# C0: "left has * iff right has *" — equivalent to x*y=0 (Constant Zero)
C0_TABLE = [[0, 0], [0, 0]]


def load_benchmark(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def check_vars_separation(eq1: str, eq2: str) -> bool:
    """
    VARS test: Compare variable sets on left vs right for both equations.
    Separation = E1 holds (same var set or bare-var subsumes) and E2 fails.

    The actual VARS test logic:
    - If both sides have *: same set → HOLD, different set → FAIL
    - If one side is bare variable v, other has *: HOLD only if * side uses only v
    - If neither has * and same variable: HOLD. Different: FAIL.
    """
    def vars_test(eq: str) -> str:
        """Returns 'HOLD' or 'FAIL' for the VARS test on a single equation."""
        # Parse into left and right of =
        parts = eq.split('=', 1)
        left = parts[0].strip()
        right = parts[1].strip()

        left_has_star = '*' in left
        right_has_star = '*' in right

        def get_vars(s):
            return set(c for c in s if c.isalpha())

        left_vars = get_vars(left)
        right_vars = get_vars(right)

        if left_has_star and right_has_star:
            return "HOLD" if left_vars == right_vars else "FAIL"
        elif not left_has_star and not right_has_star:
            return "HOLD" if left_vars == right_vars else "FAIL"
        else:
            # One side bare variable, other has *
            bare_vars = left_vars if not left_has_star else right_vars
            star_vars = right_vars if not left_has_star else left_vars
            # HOLD only if star side uses only the bare variable
            return "HOLD" if star_vars <= bare_vars else "FAIL"

    e1_result = vars_test(eq1)
    e2_result = vars_test(eq2)

    # Separation = E1=HOLD and E2=FAIL
    return e1_result == "HOLD" and e2_result == "FAIL"


def check_magma_separation(table, eq1: str, eq2: str) -> bool:
    """Returns True if table satisfies eq1 but NOT eq2."""
    if not check_equation(eq1, table):
        return False
    return not check_equation(eq2, table)


def analyze_test_coverage(pairs: list[dict], label: str):
    """Analyze which tests separate which FALSE pairs."""
    print(f"\n{'='*70}")
    print(f"TEST COVERAGE ANALYSIS: {label}")
    print(f"{'='*70}")

    test_results = []
    for pair in pairs:
        eq1, eq2 = pair["equation1"], pair["equation2"]
        pid = pair["id"]

        separators = []
        if check_magma_separation(LP_TABLE, eq1, eq2):
            separators.append("LP")
        if check_magma_separation(RP_TABLE, eq1, eq2):
            separators.append("RP")
        if check_magma_separation(C0_TABLE, eq1, eq2):
            separators.append("C0")
        if check_vars_separation(eq1, eq2):
            separators.append("VARS")

        test_results.append({
            "id": pid,
            "separators": separators,
            "count": len(separators),
        })

    # Per-test counts
    test_counts = {"LP": 0, "RP": 0, "C0": 0, "VARS": 0}
    for r in test_results:
        for s in r["separators"]:
            test_counts[s] += 1

    print(f"\nPer-test catch counts (out of {len(pairs)} FALSE pairs):")
    for test, count in sorted(test_counts.items(), key=lambda x: -x[1]):
        print(f"  {test:6s}: {count:3d} pairs ({100*count/len(pairs):.1f}%)")

    # Solo separators (only one test fires)
    print(f"\nSolo separators (only ONE test fires):")
    for test in ["LP", "RP", "C0", "VARS"]:
        solo = [r for r in test_results if r["separators"] == [test]]
        if solo:
            print(f"  {test} ONLY: {len(solo)} pairs → {[r['id'] for r in solo]}")
        else:
            print(f"  {test} ONLY: 0 pairs")

    # Coverage gaps (no test fires)
    gaps = [r for r in test_results if not r["separators"]]
    print(f"\nCoverage gaps (NO test fires): {len(gaps)} pairs")
    for r in gaps:
        pair = next(p for p in pairs if p["id"] == r["id"])
        print(f"  {r['id']}: {pair['equation1']}  ⇏  {pair['equation2']}")

    # Multi-test overlap (2+ tests fire)
    multi = [r for r in test_results if len(r["separators"]) >= 2]
    print(f"\nMulti-test (2+ tests fire): {len(multi)} pairs")

    # VARS marginal importance: how many pairs break if we remove VARS?
    vars_needed = [r for r in test_results if "VARS" in r["separators"]
                   and not any(s in r["separators"] for s in ["LP", "RP", "C0"])]
    print(f"\nVARS MARGINAL IMPORTANCE: {len(vars_needed)} pairs rely SOLELY on VARS")
    for r in vars_needed:
        pair = next(p for p in pairs if p["id"] == r["id"])
        print(f"  {r['id']}: {pair['equation1']}  ⇏  {pair['equation2']}")

    # What if we replaced VARS? How many pairs would still be caught?
    caught_without_vars = sum(1 for r in test_results
                              if any(s in r["separators"] for s in ["LP", "RP", "C0"]))
    print(f"\nWithout VARS: {caught_without_vars}/{len(pairs)} still caught by LP/RP/C0")
    print(f"  Drop: {len(pairs) - len(gaps) - caught_without_vars} pairs would become gaps")

    return test_results


def main():
    # Find benchmarks
    normal_files = sorted(BENCHMARK_DIR.glob("normal_balanced60_*rotation0002*.jsonl"))
    hard3_files = sorted(BENCHMARK_DIR.glob("hard3_balanced40_*rotation0002*.jsonl"))

    if normal_files:
        rows = load_benchmark(normal_files[-1])
        false_pairs = [r for r in rows if r.get("answer") is False]
        print(f"Normal benchmark: {normal_files[-1].name} ({len(false_pairs)} FALSE pairs)")
        normal_results = analyze_test_coverage(false_pairs, "NORMAL-60 FALSE pairs")

    if hard3_files:
        rows = load_benchmark(hard3_files[-1])
        false_pairs = [r for r in rows if r.get("answer") is False]
        print(f"\nHard3 benchmark: {hard3_files[-1].name} ({len(false_pairs)} FALSE pairs)")
        hard3_results = analyze_test_coverage(false_pairs, "HARD3-40 FALSE pairs")

    # Combined summary
    if normal_files and hard3_files:
        print(f"\n{'='*70}")
        print("RECOMMENDATION")
        print(f"{'='*70}")

        # Count pairs needing only VARS in normal set
        normal_false = load_benchmark(normal_files[-1])
        normal_false = [r for r in normal_false if r.get("answer") is False]
        vars_only_normal = 0
        for pair in normal_false:
            eq1, eq2 = pair["equation1"], pair["equation2"]
            has_lp = check_magma_separation(LP_TABLE, eq1, eq2)
            has_rp = check_magma_separation(RP_TABLE, eq1, eq2)
            has_c0 = check_magma_separation(C0_TABLE, eq1, eq2)
            has_vars = check_vars_separation(eq1, eq2)
            if has_vars and not (has_lp or has_rp or has_c0):
                vars_only_normal += 1

        if vars_only_normal <= 2:
            print(f"  VARS is low-importance ({vars_only_normal} sole-separator pairs on normal).")
            print(f"  SAFE to consider replacing VARS with a magma evaluation test.")
        else:
            print(f"  VARS has {vars_only_normal} sole-separator pairs on normal.")
            print(f"  Replacing VARS would cost ~{vars_only_normal} correct answers on normal.")
            print(f"  ONLY replace VARS if the magma test compensates with ≥{vars_only_normal} hard3 catches.")


if __name__ == "__main__":
    main()
