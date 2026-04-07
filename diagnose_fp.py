#!/usr/bin/env python3
"""Quick diagnostic for a specific pair."""
from verify_structural_rules import structural_lsucc, structural_rsucc, left_depth, right_depth, first_letter, last_letter

eq1 = "x = (y * x) * ((z * w) * z)"
eq2 = "x * y = (x * x) * x"

for eq_label, eq in [("E1", eq1), ("E2", eq2)]:
    lhs, rhs = eq.split("=", 1)
    lhs, rhs = lhs.strip(), rhs.strip()
    fl, fr = first_letter(lhs), first_letter(rhs)
    ll, lr = last_letter(lhs), last_letter(rhs)
    ld_l, ld_r = left_depth(lhs), left_depth(rhs)
    rd_l, rd_r = right_depth(lhs), right_depth(rhs)
    has_star_l = "*" in lhs
    has_star_r = "*" in rhs
    lp = "HOLD" if fl == fr else "FAIL"
    rp = "HOLD" if ll == lr else "FAIL"
    c0_hold = (has_star_l and has_star_r) or (not has_star_l and not has_star_r and lhs == rhs)
    c0 = "HOLD" if c0_hold else "FAIL"
    lsucc = "HOLD" if structural_lsucc(eq) else "FAIL"
    rsucc = "HOLD" if structural_rsucc(eq) else "FAIL"
    print(f"{eq_label}: {eq}")
    print(f"  L='{lhs}'  R='{rhs}'")
    print(f"  LP:    first(L)={fl} first(R)={fr} -> {lp}")
    print(f"  RP:    last(L)={ll} last(R)={lr} -> {rp}")
    print(f"  C0:    L has *={has_star_l}, R has *={has_star_r} -> {c0}")
    print(f"  LSUCC: L depth={ld_l}, R depth={ld_r}, mod3=({ld_l%3},{ld_r%3}), first match={fl==fr} -> {lsucc}")
    print(f"  RSUCC: L depth={rd_l}, R depth={rd_r}, mod3=({rd_l%3},{rd_r%3}), last match={ll==lr} -> {rsucc}")
    print()
