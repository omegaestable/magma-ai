#!/usr/bin/env python3
"""Find good TRUE example pairs for the cheatsheet where Phase 2 also says TRUE."""
import json
from pathlib import Path
from distill import check_equation

ROOT = Path(__file__).resolve().parent
SUCC3 = [[1, 2, 0], [1, 2, 0], [1, 2, 0]]

# Check current Example C
eq1 = "x = (y * x) * (z * (w * y))"
eq2 = "x = ((y * x) * x) * x"
print(f"Current Example C:")
print(f"  E1 on SUCC3: {check_equation(eq1, SUCC3)}")
print(f"  E2 on SUCC3: {check_equation(eq2, SUCC3)}")

# Check hard3 TRUE pairs
hard3_file = sorted((ROOT / "data" / "benchmark").glob("hard3_balanced40_*rotation0002*.jsonl"))[-1]
normal_file = sorted((ROOT / "data" / "benchmark").glob("normal_balanced60_*rotation0002*.jsonl"))[-1]

for f in [hard3_file, normal_file]:
    print(f"\n=== {f.name} TRUE pairs ===")
    for line in open(f):
        row = json.loads(line.strip())
        if row["answer"] is not True:
            continue
        eq1, eq2 = row["equation1"], row["equation2"]
        e1_succ3 = check_equation(eq1, SUCC3)
        e2_succ3 = check_equation(eq2, SUCC3)

        # We want: structural tests don't separate, and E1 FAILS on SUCC3
        # (simplest TRUE demo for Phase 2)
        left1, right1 = eq1.split("=", 1)
        left2, right2 = eq2.split("=", 1)

        # LP check
        def first_letter(s):
            for c in s.strip():
                if c.isalpha():
                    return c
            return None
        def last_letter(s):
            for c in reversed(s.strip()):
                if c.isalpha():
                    return c
            return None

        lp1 = first_letter(left1) == first_letter(right1)
        lp2 = first_letter(left2) == first_letter(right2)
        rp1 = last_letter(left1) == last_letter(right1)
        rp2 = last_letter(left2) == last_letter(right2)
        c0_1 = ("*" in left1) == ("*" in right1)
        c0_2 = ("*" in left2) == ("*" in right2)

        # Check for structural separation
        lp_sep = lp1 and not lp2
        rp_sep = rp1 and not rp2
        c0_sep = c0_1 and not c0_2

        if not (lp_sep or rp_sep or c0_sep):
            # No structural separation — good candidate
            nvars = len(set(c for c in eq1 + eq2 if c.isalpha()))
            status = "E1_FAILS" if not e1_succ3 else ("BOTH_HOLD" if e2_succ3 else "SEP")
            if nvars <= 4 and status == "E1_FAILS":
                print(f"  {row['id']}: {eq1} | {eq2}")
                print(f"    vars={nvars} LP=({'H' if lp1 else 'F'},{'H' if lp2 else 'F'}) "
                      f"RP=({'H' if rp1 else 'F'},{'H' if rp2 else 'F'}) "
                      f"C0=({'H' if c0_1 else 'F'},{'H' if c0_2 else 'F'}) "
                      f"SUCC3={status}")
