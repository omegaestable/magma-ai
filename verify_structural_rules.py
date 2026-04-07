#!/usr/bin/env python3
"""
verify_structural_rules.py — Verify that LSUCC/RSUCC text-inspectable rules
match algebraic witness evaluation exactly.

LSUCC (M4 = [[1,1,1],[2,2,2],[0,0,0]], a*b=(a+1)%3):
  left_depth(expr) = (opening parens before first letter) + 1 if has *, else 0
  Equation holds iff first_letters match AND left_depths equal mod 3

RSUCC (M5 = [[1,2,0],[1,2,0],[1,2,0]], a*b=(b+1)%3):
  right_depth(expr) = (closing parens after last letter) + 1 if has *, else 0
  Equation holds iff last_letters match AND right_depths equal mod 3
"""
from __future__ import annotations
import json, re
from pathlib import Path
from distill import check_equation

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "data" / "benchmark"

M4 = [[1, 1, 1], [2, 2, 2], [0, 0, 0]]  # LSUCC
M5 = [[1, 2, 0], [1, 2, 0], [1, 2, 0]]  # RSUCC


def left_depth(expr: str) -> int:
    """Count opening parens before first letter, +1 if has *."""
    expr = expr.strip()
    if "*" not in expr:
        return 0
    count = 0
    for ch in expr:
        if ch == "(":
            count += 1
        elif ch.isalpha():
            break
    return count + 1


def right_depth(expr: str) -> int:
    """Count closing parens after last letter, +1 if has *."""
    expr = expr.strip()
    if "*" not in expr:
        return 0
    count = 0
    for ch in reversed(expr):
        if ch == ")":
            count += 1
        elif ch.isalpha():
            break
    return count + 1


def first_letter(expr: str) -> str:
    for ch in expr:
        if ch.isalpha():
            return ch
    return ""


def last_letter(expr: str) -> str:
    for ch in reversed(expr):
        if ch.isalpha():
            return ch
    return ""


def structural_lsucc(eq: str) -> bool:
    """Does equation hold on LSUCC by structural rule?"""
    lhs, rhs = eq.split("=", 1)
    lhs, rhs = lhs.strip(), rhs.strip()
    fl = first_letter(lhs)
    fr = first_letter(rhs)
    dl = left_depth(lhs)
    dr = left_depth(rhs)
    return fl == fr and (dl % 3) == (dr % 3)


def structural_rsucc(eq: str) -> bool:
    """Does equation hold on RSUCC by structural rule?"""
    lhs, rhs = eq.split("=", 1)
    lhs, rhs = lhs.strip(), rhs.strip()
    ll = last_letter(lhs)
    lr = last_letter(rhs)
    dl = right_depth(lhs)
    dr = right_depth(rhs)
    return ll == lr and (dl % 3) == (dr % 3)


def main():
    benchmarks = sorted(BENCHMARK_DIR.glob("*.jsonl"))
    
    lsucc_mismatches = 0
    rsucc_mismatches = 0
    total = 0
    
    for bf in benchmarks:
        with open(bf, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                for eq_key in ["equation1", "equation2"]:
                    eq = row[eq_key]
                    total += 1
                    
                    # Algebraic truth
                    alg_lsucc = check_equation(eq, M4)
                    alg_rsucc = check_equation(eq, M5)
                    
                    # Structural prediction
                    str_lsucc = structural_lsucc(eq)
                    str_rsucc = structural_rsucc(eq)
                    
                    if alg_lsucc != str_lsucc:
                        lsucc_mismatches += 1
                        print(f"LSUCC MISMATCH: {eq}")
                        lhs, rhs = eq.split("=", 1)
                        print(f"  LHS: first={first_letter(lhs)}, depth={left_depth(lhs.strip())}")
                        print(f"  RHS: first={first_letter(rhs)}, depth={left_depth(rhs.strip())}")
                        print(f"  Structural={str_lsucc}, Algebraic={alg_lsucc}")
                    
                    if alg_rsucc != str_rsucc:
                        rsucc_mismatches += 1
                        print(f"RSUCC MISMATCH: {eq}")
                        lhs, rhs = eq.split("=", 1)
                        print(f"  LHS: last={last_letter(lhs)}, depth={right_depth(lhs.strip())}")
                        print(f"  RHS: last={last_letter(rhs)}, depth={right_depth(rhs.strip())}")
                        print(f"  Structural={str_rsucc}, Algebraic={alg_rsucc}")
    
    print(f"\nTotal equations checked: {total}")
    print(f"LSUCC mismatches: {lsucc_mismatches}")
    print(f"RSUCC mismatches: {rsucc_mismatches}")
    if lsucc_mismatches == 0 and rsucc_mismatches == 0:
        print("ALL CLEAR: Structural rules match algebraic evaluation perfectly!")


if __name__ == "__main__":
    main()
