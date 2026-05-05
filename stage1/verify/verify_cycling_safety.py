#!/usr/bin/env python3
"""
verify_cycling_safety.py — Check cycling assignment (x=0,y=1,z=2,...) on SUCC3.

SUCC3: x*y = NEXT(y) where NEXT(0)=1, NEXT(1)=2, NEXT(2)=0.
Since the op ignores the left argument, eval(term) = (rightmost_var + depth) mod 3.

For "E holds universally on SUCC3" iff same rightmost var AND same depth mod 3 on both sides.
Checking all=0 only verifies depth match, missing the variable-identity check.
Cycling assignment (x=0,y=1,z=2) checks BOTH depth AND variable identity in one shot.
"""
import json
from pathlib import Path
from distill import check_equation, parse_equation_tree, eval_tree, _collect_tree_vars

ROOT = Path(__file__).resolve().parent
SUCC3 = [[1, 2, 0], [1, 2, 0], [1, 2, 0]]


def make_cycling_assignment(variables: set) -> dict:
    """Assign 0,1,2,0,1,2,... to variables in alphabetical order."""
    ordered = sorted(variables)
    return {v: i % 3 for i, v in enumerate(ordered)}


def check_on_assignment(eq: str, table, assignment: dict) -> bool:
    lhs, rhs = parse_equation_tree(eq)
    return eval_tree(lhs, assignment, table) == eval_tree(rhs, assignment, table)


def get_variables(eq: str) -> set:
    lhs, rhs = parse_equation_tree(eq)
    variables = set()
    _collect_tree_vars(lhs, variables)
    _collect_tree_vars(rhs, variables)
    return variables


def main():
    hard3_file = sorted((ROOT / "data" / "benchmark").glob("hard3_balanced40_*rotation0002*.jsonl"))[-1]
    normal_file = sorted((ROOT / "data" / "benchmark").glob("normal_balanced60_*rotation0002*.jsonl"))[-1]

    print("=" * 70)
    print("CYCLING ASSIGNMENT CHECK on SUCC3")
    print("=" * 70)

    # Check against D3 / universal SUCC3 on all pairs
    all_pairs = []
    for f in [hard3_file, normal_file]:
        for line in open(f):
            all_pairs.append(json.loads(line.strip()))

    true_pairs = [p for p in all_pairs if p["answer"] is True]
    false_pairs = [p for p in all_pairs if p["answer"] is False]

    # FALSE POSITIVE CHECK on TRUE pairs
    print(f"\n--- FALSE POSITIVE CHECK on {len(true_pairs)} TRUE pairs ---")
    fp_count = 0
    for p in true_pairs:
        eq1, eq2 = p["equation1"], p["equation2"]
        vars1 = get_variables(eq1)
        vars2 = get_variables(eq2)
        all_vars = vars1 | vars2
        assign = make_cycling_assignment(all_vars)

        e1_cy = check_on_assignment(eq1, SUCC3, assign)
        e2_cy = check_on_assignment(eq2, SUCC3, assign)

        if e1_cy and not e2_cy:
            fp_count += 1
            e1_univ = check_equation(eq1, SUCC3)
            print(f"  FALSE POSITIVE: {p['id']} (E1 univ={e1_univ})")
            print(f"    assign={assign}")
            print(f"    E1: {eq1}")
            print(f"    E2: {eq2}")

    print(f"\n  Total false positives: {fp_count}/{len(true_pairs)}")

    # COVERAGE CHECK on FALSE pairs - compare cycling vs universal
    print(f"\n--- COVERAGE on {len(false_pairs)} FALSE pairs ---")
    cycling_catches = []
    universal_catches = []
    mismatches = []

    for p in false_pairs:
        eq1, eq2 = p["equation1"], p["equation2"]
        vars1 = get_variables(eq1)
        vars2 = get_variables(eq2)
        all_vars = vars1 | vars2
        assign = make_cycling_assignment(all_vars)

        e1_cy = check_on_assignment(eq1, SUCC3, assign)
        e2_cy = check_on_assignment(eq2, SUCC3, assign)
        cycling_sep = e1_cy and not e2_cy

        e1_univ = check_equation(eq1, SUCC3)
        e2_univ = check_equation(eq2, SUCC3)
        univ_sep = e1_univ and not e2_univ

        if cycling_sep:
            cycling_catches.append(p["id"])
        if univ_sep:
            universal_catches.append(p["id"])
        if cycling_sep != univ_sep:
            mismatches.append(p["id"])
            print(f"  MISMATCH: {p['id']} cycling={cycling_sep} univ={univ_sep}")

    print(f"\n  Cycling catches: {len(cycling_catches)} → {sorted(cycling_catches)}")
    print(f"  Universal catches: {len(universal_catches)} → {sorted(universal_catches)}")
    print(f"  Mismatches: {len(mismatches)}")

    # Also try x=0, y=1 (2-value cycling) for comparison
    print(f"\n--- ALTERNATIVE: x=0, y=1, z=0, w=1 (2-value cycling) ---")
    for label, make_assign in [
        ("x=0,y=1,z=2,w=0", lambda vs: {v: i % 3 for i, v in enumerate(sorted(vs))}),
        ("all=1", lambda vs: {v: 1 for v in vs}),
        ("x=0,y=1,z=0,w=1", lambda vs: {v: i % 2 for i, v in enumerate(sorted(vs))}),
    ]:
        fp = 0
        catches = 0
        for p in true_pairs:
            eq1, eq2 = p["equation1"], p["equation2"]
            all_vars = get_variables(eq1) | get_variables(eq2)
            assign = make_assign(all_vars)
            e1 = check_on_assignment(eq1, SUCC3, assign)
            e2 = check_on_assignment(eq2, SUCC3, assign)
            if e1 and not e2:
                fp += 1
        for p in false_pairs:
            eq1, eq2 = p["equation1"], p["equation2"]
            all_vars = get_variables(eq1) | get_variables(eq2)
            assign = make_assign(all_vars)
            e1 = check_on_assignment(eq1, SUCC3, assign)
            e2 = check_on_assignment(eq2, SUCC3, assign)
            if e1 and not e2:
                catches += 1
        print(f"  {label}: {fp} FP on TRUE, {catches} catches on FALSE")


if __name__ == "__main__":
    main()
