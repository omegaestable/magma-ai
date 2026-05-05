#!/usr/bin/env python3
"""
v21_verify_structural_rules.py — Validate that structural witness rules
match actual Cayley-table evaluation for all 4694 equations.

For each witness with a structural shortcut rule, compare its prediction
to the brute-force check_equation() result across all equations.
"""
from __future__ import annotations

import re
import itertools
from collections import Counter
from v21_data_infrastructure import (
    load_equations, WITNESSES, WITNESS_NAMES, check_equation,
    normalize_eq, _parse_expr, _collect_vars
)


def leftmost_leaf(eq_side: str) -> str:
    """Extract leftmost variable from an expression."""
    vars_found = re.findall(r'\b([a-z])\b', eq_side)
    return vars_found[0] if vars_found else ""


def rightmost_leaf(eq_side: str) -> str:
    """Extract rightmost variable from an expression."""
    vars_found = re.findall(r'\b([a-z])\b', eq_side)
    return vars_found[-1] if vars_found else ""


def has_star(expr: str) -> bool:
    """Does expr contain ◇ or *?"""
    return '*' in expr


def var_counts(expr: str) -> dict[str, int]:
    """Count variable occurrences."""
    c = Counter()
    for v in re.findall(r'\b([a-z])\b', expr):
        c[v] += 1
    return dict(c)


def var_set(expr: str) -> set[str]:
    """Set of variables."""
    return set(re.findall(r'\b([a-z])\b', expr))


def count_stars(expr: str) -> int:
    """Count * operators."""
    return expr.count('*')


# Structural rules return True if equation holds on the witness
def rule_LP(lhs: str, rhs: str) -> bool:
    """LP (x*y=x): equation holds iff leftmost leaf(LHS) == leftmost leaf(RHS)"""
    return leftmost_leaf(lhs) == leftmost_leaf(rhs)


def rule_RP(lhs: str, rhs: str) -> bool:
    """RP (x*y=y): equation holds iff rightmost leaf(LHS) == rightmost leaf(RHS)"""
    return rightmost_leaf(lhs) == rightmost_leaf(rhs)


def rule_C0(lhs: str, rhs: str) -> bool:
    """C0 (x*y=0): holds iff both sides have * ops, or both are same bare variable."""
    l_has = has_star(lhs)
    r_has = has_star(rhs)
    if l_has and r_has:
        return True
    if not l_has and not r_has:
        return lhs.strip() == rhs.strip()
    return False


def rule_XOR(lhs: str, rhs: str) -> bool:
    """XOR (x+y mod 2): holds iff for every variable, count_LHS ≡ count_RHS (mod 2)."""
    cl = var_counts(lhs)
    cr = var_counts(rhs)
    all_vars = set(cl.keys()) | set(cr.keys())
    return all(cl.get(v, 0) % 2 == cr.get(v, 0) % 2 for v in all_vars)


def rule_XNOR(lhs: str, rhs: str) -> bool:
    """XNOR: XOR rule AND star_count_LHS ≡ star_count_RHS (mod 2)."""
    if not rule_XOR(lhs, rhs):
        return False
    return count_stars(lhs) % 2 == count_stars(rhs) % 2


def rule_AND(lhs: str, rhs: str) -> bool:
    """AND (min): holds iff variable sets match, with bare-var handling."""
    l_has = has_star(lhs)
    r_has = has_star(rhs)
    if l_has and r_has:
        return var_set(lhs) == var_set(rhs)
    if not l_has and not r_has:
        return lhs.strip() == rhs.strip()
    # One side bare var, other has *
    bare = lhs.strip() if not l_has else rhs.strip()
    other = rhs if not l_has else lhs
    return var_set(other) == {bare}


def rule_OR(lhs: str, rhs: str) -> bool:
    """OR (max): same structure as AND."""
    return rule_AND(lhs, rhs)


def rule_Z3A(lhs: str, rhs: str) -> bool:
    """Z3A (x+y mod 3): holds iff for every variable, count_LHS ≡ count_RHS (mod 3)."""
    cl = var_counts(lhs)
    cr = var_counts(rhs)
    all_vars = set(cl.keys()) | set(cr.keys())
    return all(cl.get(v, 0) % 3 == cr.get(v, 0) % 3 for v in all_vars)


STRUCTURAL_RULES = {
    "LP": rule_LP,
    "RP": rule_RP,
    "C0": rule_C0,
    "XOR": rule_XOR,
    "XNOR": rule_XNOR,
    "AND": rule_AND,
    "OR": rule_OR,
    "Z3A": rule_Z3A,
}


def main():
    equations = load_equations()
    print(f"Loaded {len(equations)} equations")
    
    for wname, rule_fn in STRUCTURAL_RULES.items():
        # Find corresponding witness
        w = next(w for w in WITNESSES if w["name"] == wname)
        table = w["table"]
        
        agree = 0
        disagree = 0
        errors = []
        for idx, eq in enumerate(equations):
            norm = normalize_eq(eq)
            parts = norm.split(' = ', 1)
            if len(parts) != 2:
                continue
            lhs, rhs = parts[0].strip(), parts[1].strip()
            
            structural = rule_fn(lhs, rhs)
            brute = check_equation(eq, table)
            
            if structural == brute:
                agree += 1
            else:
                disagree += 1
                if len(errors) < 5:
                    errors.append((idx, eq, structural, brute))
        
        status = "✓" if disagree == 0 else "✗"
        print(f"  {status} {wname}: {agree} agree, {disagree} disagree")
        for idx, eq, s, b in errors:
            print(f"    Eq{idx}: '{eq}' structural={s} brute={b}")


if __name__ == "__main__":
    main()
