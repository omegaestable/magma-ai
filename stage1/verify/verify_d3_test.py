#!/usr/bin/env python3
"""
verify_d3_test.py — Verify the D3 (depth mod 3) test against SUCC3 magma truth.

For each side of an equation, D3 computes:
  - last letter
  - depth: bare variable → 0; has * → (closing parens after last letter) + 1
  - HOLD: same last letter on both sides AND same depth mod 3
  - FAIL: otherwise

D3 should be equivalent to checking whether the equation holds on the SUCC3 magma
where x◇y = (y+1) mod 3.

This script verifies this equivalence on all hard3 and normal benchmark pairs.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from distill import check_equation

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "data" / "benchmark"

SUCC3_TABLE = [[1, 2, 0], [1, 2, 0], [1, 2, 0]]  # x◇y = (y+1) mod 3


def d3_side(side: str) -> tuple[str, int]:
    """Compute last letter and depth for one side of an equation."""
    side = side.strip()
    has_star = '*' in side

    # Find last letter
    last_letter = None
    last_idx = -1
    for i, c in enumerate(side):
        if c.isalpha():
            last_letter = c
            last_idx = i

    if not has_star:
        return (last_letter, 0)

    # Count closing parens after last letter
    c_count = 0
    for i in range(last_idx + 1, len(side)):
        if side[i] == ')':
            c_count += 1

    return (last_letter, c_count + 1)


def d3_equation(eq: str) -> str:
    """Returns 'HOLD' or 'FAIL' for the D3 test on this equation."""
    parts = eq.split('=', 1)
    left = parts[0].strip()
    right = parts[1].strip()

    l_letter, l_depth = d3_side(left)
    r_letter, r_depth = d3_side(right)

    if l_letter == r_letter and l_depth % 3 == r_depth % 3:
        return "HOLD"
    return "FAIL"


def d3_separation(eq1: str, eq2: str) -> bool:
    """Returns True if D3 gives E1=HOLD, E2=FAIL (separation)."""
    return d3_equation(eq1) == "HOLD" and d3_equation(eq2) == "FAIL"


def succ3_separation(eq1: str, eq2: str) -> bool:
    """Returns True if SUCC3 magma separates: E1 holds but E2 doesn't."""
    return check_equation(eq1, SUCC3_TABLE) and not check_equation(eq2, SUCC3_TABLE)


def load_benchmark(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    # Test on hard3 FALSE pairs
    hard3_files = sorted(BENCHMARK_DIR.glob("hard3_balanced40_*rotation0002*.jsonl"))
    normal_files = sorted(BENCHMARK_DIR.glob("normal_balanced60_*rotation0002*.jsonl"))

    all_pairs = []
    for f in hard3_files + normal_files:
        all_pairs.extend(load_benchmark(f))

    false_pairs = [p for p in all_pairs if p.get("answer") is False]
    true_pairs = [p for p in all_pairs if p.get("answer") is True]

    # Check D3 vs SUCC3 equivalence on FALSE pairs
    print("=" * 70)
    print("D3 vs SUCC3 on FALSE pairs")
    print("=" * 70)

    d3_catches = []
    succ3_catches = []
    mismatches = []

    for p in false_pairs:
        eq1, eq2, pid = p["equation1"], p["equation2"], p["id"]
        d3_sep = d3_separation(eq1, eq2)
        succ3_sep = succ3_separation(eq1, eq2)

        if d3_sep:
            d3_catches.append(pid)
        if succ3_sep:
            succ3_catches.append(pid)
        if d3_sep != succ3_sep:
            mismatches.append(pid)

            # Show details
            l_letter1, l_depth1 = d3_side(eq1.split('=')[0].strip())
            r_letter1, r_depth1 = d3_side(eq1.split('=')[1].strip())
            l_letter2, l_depth2 = d3_side(eq2.split('=')[0].strip())
            r_letter2, r_depth2 = d3_side(eq2.split('=')[1].strip())

            e1_holds = check_equation(eq1, SUCC3_TABLE)
            e2_holds = check_equation(eq2, SUCC3_TABLE)

            print(f"\n  MISMATCH: {pid}")
            print(f"    E1: {eq1}")
            print(f"    E2: {eq2}")
            print(f"    D3: E1 L=({l_letter1},{l_depth1}) R=({r_letter1},{r_depth1}) → {d3_equation(eq1)}")
            print(f"    D3: E2 L=({l_letter2},{l_depth2}) R=({r_letter2},{r_depth2}) → {d3_equation(eq2)}")
            print(f"    SUCC3: E1 holds={e1_holds}, E2 holds={e2_holds}")
            print(f"    D3 says sep={d3_sep}, SUCC3 says sep={succ3_sep}")

    print(f"\nD3 catches: {len(d3_catches)} → {sorted(d3_catches)}")
    print(f"SUCC3 catches: {len(succ3_catches)} → {sorted(succ3_catches)}")
    print(f"Mismatches: {len(mismatches)} → {sorted(mismatches)}")

    # Safety check: D3 false-flags on TRUE pairs
    print(f"\n{'='*70}")
    print("D3 SAFETY CHECK on TRUE pairs")
    print("=" * 70)

    d3_false_flags = []
    succ3_false_flags = []

    for p in true_pairs:
        eq1, eq2, pid = p["equation1"], p["equation2"], p["id"]
        if d3_separation(eq1, eq2):
            d3_false_flags.append(pid)
            # Show details
            l_letter1, l_depth1 = d3_side(eq1.split('=')[0].strip())
            r_letter1, r_depth1 = d3_side(eq1.split('=')[1].strip())
            l_letter2, l_depth2 = d3_side(eq2.split('=')[0].strip())
            r_letter2, r_depth2 = d3_side(eq2.split('=')[1].strip())
            print(f"\n  FALSE FLAG: {pid}")
            print(f"    E1: {eq1}")
            print(f"    E2: {eq2}")
            print(f"    D3: E1 L=({l_letter1},{l_depth1}) R=({r_letter1},{r_depth1}) → {d3_equation(eq1)}")
            print(f"    D3: E2 L=({l_letter2},{l_depth2}) R=({r_letter2},{r_depth2}) → {d3_equation(eq2)}")
        if succ3_separation(eq1, eq2):
            succ3_false_flags.append(pid)

    print(f"\nD3 false-flags: {len(d3_false_flags)} → {sorted(d3_false_flags)}")
    print(f"SUCC3 false-flags: {len(succ3_false_flags)} → {sorted(succ3_false_flags)}")

    # Show D3 details for the 5 caught hard3 pairs
    print(f"\n{'='*70}")
    print("D3 DETAILS for caught hard3 pairs")
    print("=" * 70)
    for pid in sorted(d3_catches):
        if 'hard3' in pid:
            p = next(pp for pp in false_pairs if pp["id"] == pid)
            eq1, eq2 = p["equation1"], p["equation2"]
            l1, d1 = d3_side(eq1.split('=')[0].strip())
            r1, rd1 = d3_side(eq1.split('=')[1].strip())
            l2, d2 = d3_side(eq2.split('=')[0].strip())
            r2, rd2 = d3_side(eq2.split('=')[1].strip())
            print(f"\n  {pid}: {eq1}  ⇏  {eq2}")
            print(f"    E1: L last={l1} depth={d1}, R last={r1} depth={rd1} → {d3_equation(eq1)}")
            print(f"    E2: L last={l2} depth={d2}, R last={r2} depth={rd2} → {d3_equation(eq2)}")


if __name__ == "__main__":
    main()
