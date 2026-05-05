#!/usr/bin/env python3
"""
spine_classify — Spine Isolation Theorem implementation for magma equations.

Classifies equations by spine type and applies the Spine Isolation Theorem
(McKenna 2026) to determine non-implications.

Spine type is the path from the parse-tree root to the leftmost occurrence
of the LHS variable in the RHS:
  - pure left-spine of depth n: always go left to reach x
  - pure right-spine: x is NOT the leftmost leaf
  - mixed spine: path to x has both left and right steps
  - product-LHS: left side of equation contains * (not bare variable)
  - trivial: x = x (depth 0)

Separation rules (all Lean 4-verified, zero exceptions across 22M pairs):
  (a) left-spine depth n ⊬ left-spine depth m when n ∤ m
      (counterexample: Z/nZ with a◇b = a+1 mod n)
  (b) left-spine ⊬ right-spine
      (counterexample: left-zero magma, a◇b = a)
  (c) left-spine ⊬ mixed-spine
      (counterexample: left-zero magma, a◇b = a)

References:
  - McKenna, A. (2026). A Spine Isolation Theorem for Magma Implications.
    Zenodo. https://doi.org/10.5281/zenodo.19380600
  - Lean 4: https://github.com/mysticflounder/equational-magma-theorems
  - ETP Corollary 10.4 (first-letter invariant)

Usage:
    python spine_classify.py "x = (x * y) * (y * x)"
    python spine_classify.py --file data/exports/equations.txt
    python spine_classify.py --check "x = x * (y * z)" "x = (y * x) * z"
"""

import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SpineType(Enum):
    TRIVIAL = "trivial"           # x = x
    LEFT_SPINE = "left-spine"     # x = (...((x ◇ T₁) ◇ T₂) ... ◇ Tₙ)
    RIGHT_SPINE = "right-spine"   # x appears only on right branches
    MIXED = "mixed"               # path to x has both L and R steps
    PRODUCT_LHS = "product-lhs"   # LHS contains * (not bare variable)
    NO_VAR_MATCH = "no-var-match" # LHS var not found in RHS


@dataclass
class SpineInfo:
    spine_type: SpineType
    depth: Optional[int]  # Only meaningful for LEFT_SPINE
    lhs_var: str          # The bare variable on the LHS (if applicable)
    equation: str         # Original equation string


class ParseNode:
    """Binary tree node for a magma term."""
    def __init__(self, var: Optional[str] = None,
                 left: Optional["ParseNode"] = None,
                 right: Optional["ParseNode"] = None):
        self.var = var      # leaf variable name, or None for internal node
        self.left = left    # left child (a in a*b)
        self.right = right  # right child (b in a*b)

    @property
    def is_leaf(self) -> bool:
        return self.var is not None

    def __repr__(self):
        if self.is_leaf:
            return self.var
        return f"({self.left} * {self.right})"


def _tokenize(expr: str) -> list[str]:
    """Tokenize a magma expression into variables, *, (, )."""
    tokens = []
    i = 0
    s = expr.strip()
    while i < len(s):
        if s[i].isspace():
            i += 1
        elif s[i] in "(*)" or s[i] == '\u25c7':  # ◇
            if s[i] in "*\u25c7":
                tokens.append("*")
            else:
                tokens.append(s[i])
            i += 1
        elif s[i].isalpha() or s[i] == '_':
            j = i
            while j < len(s) and (s[j].isalnum() or s[j] == '_'):
                j += 1
            tokens.append(s[i:j])
            i = j
        else:
            i += 1  # skip unexpected chars
    return tokens


def parse_term(expr: str) -> ParseNode:
    """Parse a magma expression string into a tree.

    Grammar: term = atom | term * atom
             atom = variable | ( term )
    Left-associative: a * b * c = (a * b) * c
    """
    tokens = _tokenize(expr)
    pos = [0]

    def _atom() -> ParseNode:
        if pos[0] >= len(tokens):
            raise ValueError(f"Unexpected end of expression: {expr}")
        tok = tokens[pos[0]]
        if tok == "(":
            pos[0] += 1
            node = _expr()
            if pos[0] < len(tokens) and tokens[pos[0]] == ")":
                pos[0] += 1
            return node
        elif tok not in ("*", ")"):
            pos[0] += 1
            return ParseNode(var=tok)
        else:
            raise ValueError(f"Unexpected token '{tok}' at pos {pos[0]} in: {expr}")

    def _expr() -> ParseNode:
        node = _atom()
        while pos[0] < len(tokens) and tokens[pos[0]] == "*":
            pos[0] += 1  # consume *
            right = _atom()
            node = ParseNode(left=node, right=right)
        return node

    result = _expr()
    return result


def classify_spine(equation: str) -> SpineInfo:
    """Classify an equation by its spine type.

    Args:
        equation: String of form "LHS = RHS" using * for the magma op.
    """
    # Normalize: replace ◇ with *
    eq = equation.replace("\u25c7", "*").strip()

    parts = eq.split("=", 1)
    if len(parts) != 2:
        raise ValueError(f"No '=' found in equation: {equation}")

    lhs_str = parts[0].strip()
    rhs_str = parts[1].strip()

    # Parse LHS
    lhs_tree = parse_term(lhs_str)

    # Check if LHS is a bare variable
    if not lhs_tree.is_leaf:
        return SpineInfo(SpineType.PRODUCT_LHS, None, "", equation)

    lhs_var = lhs_tree.var

    # Parse RHS
    rhs_tree = parse_term(rhs_str)

    # Trivial case: x = x
    if rhs_tree.is_leaf and rhs_tree.var == lhs_var:
        return SpineInfo(SpineType.TRIVIAL, 0, lhs_var, equation)

    # Walk the tree to find the path to the first (leftmost) occurrence of lhs_var
    path = _find_leftmost_path(rhs_tree, lhs_var)

    if path is None:
        return SpineInfo(SpineType.NO_VAR_MATCH, None, lhs_var, equation)

    if len(path) == 0:
        # RHS is just the variable itself (trivial, handled above)
        return SpineInfo(SpineType.TRIVIAL, 0, lhs_var, equation)

    # Classify based on path directions
    all_left = all(d == "L" for d in path)
    all_right = all(d == "R" for d in path)

    if all_left:
        return SpineInfo(SpineType.LEFT_SPINE, len(path), lhs_var, equation)
    elif all_right:
        return SpineInfo(SpineType.RIGHT_SPINE, len(path), lhs_var, equation)
    else:
        return SpineInfo(SpineType.MIXED, len(path), lhs_var, equation)


def _find_leftmost_path(node: ParseNode, target: str) -> Optional[list[str]]:
    """Find path from root to the leftmost occurrence of target variable.

    Returns list of 'L'/'R' directions, or None if target not found.
    """
    if node.is_leaf:
        if node.var == target:
            return []
        return None

    # Try left subtree first (leftmost occurrence)
    left_path = _find_leftmost_path(node.left, target)
    if left_path is not None:
        return ["L"] + left_path

    # Then right subtree
    right_path = _find_leftmost_path(node.right, target)
    if right_path is not None:
        return ["R"] + right_path

    return None


def spine_separates(eq1_info: SpineInfo, eq2_info: SpineInfo) -> Optional[str]:
    """Check if the Spine Isolation Theorem proves eq1 ⊬ eq2.

    Returns a reason string if separation is proven, None otherwise.
    """
    # Only applies when E1 is left-spine
    if eq1_info.spine_type != SpineType.LEFT_SPINE:
        return None

    n = eq1_info.depth

    # (b) left-spine ⊬ right-spine
    if eq2_info.spine_type == SpineType.RIGHT_SPINE:
        return f"left-spine (depth {n}) cannot imply right-spine (left-zero magma)"

    # (c) left-spine ⊬ mixed-spine
    if eq2_info.spine_type == SpineType.MIXED:
        return f"left-spine (depth {n}) cannot imply mixed-spine (left-zero magma)"

    # (a) left-spine depth n ⊬ left-spine depth m when n ∤ m
    if eq2_info.spine_type == SpineType.LEFT_SPINE:
        m = eq2_info.depth
        if m is not None and n is not None and n > 0 and m % n != 0:
            return (
                f"left-spine depth {n} cannot imply left-spine depth {m} "
                f"({n} does not divide {m}; cyclic successor magma Z/{n}Z)"
            )

    return None


def check_implication(eq1: str, eq2: str) -> dict:
    """Check whether the Spine Isolation Theorem separates eq1 from eq2."""
    info1 = classify_spine(eq1)
    info2 = classify_spine(eq2)
    reason = spine_separates(info1, info2)
    return {
        "eq1": eq1,
        "eq2": eq2,
        "eq1_spine": info1.spine_type.value,
        "eq1_depth": info1.depth,
        "eq2_spine": info2.spine_type.value,
        "eq2_depth": info2.depth,
        "separated": reason is not None,
        "reason": reason,
    }


# ── CLI ────────────────────────────────────────────────────────────────

def _main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Classify magma equations by spine type and check separations."
    )
    ap.add_argument("equation", nargs="?", help="Single equation to classify")
    ap.add_argument("--file", help="File with one equation per line")
    ap.add_argument(
        "--check", nargs=2, metavar=("EQ1", "EQ2"),
        help="Check if Spine Isolation Theorem separates EQ1 from EQ2",
    )
    ap.add_argument("--stats", action="store_true", help="Print spine type stats")
    ap.add_argument("--benchmark", help="JSONL benchmark file to analyze")

    args = ap.parse_args()

    if args.check:
        result = check_implication(args.check[0], args.check[1])
        print(f"E1: {result['eq1']}")
        print(f"  spine: {result['eq1_spine']}, depth: {result['eq1_depth']}")
        print(f"E2: {result['eq2']}")
        print(f"  spine: {result['eq2_spine']}, depth: {result['eq2_depth']}")
        if result["separated"]:
            print(f"\nSEPARATED: {result['reason']}")
        else:
            print("\nNo spine separation (does not mean implication holds)")
        return

    if args.benchmark:
        import json
        with open(args.benchmark, encoding="utf-8") as f:
            problems = [json.loads(line) for line in f if line.strip()]

        separated_correct = 0
        separated_wrong = 0
        not_separated = 0
        for p in problems:
            eq1 = p["equation1"].replace("\u25c7", "*")
            eq2 = p["equation2"].replace("\u25c7", "*")
            answer = bool(p["answer"])
            result = check_implication(eq1, eq2)
            if result["separated"]:
                if not answer:  # ground truth is FALSE, spine says FALSE
                    separated_correct += 1
                else:
                    separated_wrong += 1
                    print(f"SPINE ERROR: {p['id']} — spine says FALSE but answer is TRUE")
                    print(f"  E1: {eq1} ({result['eq1_spine']} d={result['eq1_depth']})")
                    print(f"  E2: {eq2} ({result['eq2_spine']} d={result['eq2_depth']})")
                    print(f"  Reason: {result['reason']}")
            else:
                not_separated += 1

        total_false = sum(1 for p in problems if not p["answer"])
        print(f"\n  Spine Isolation Theorem on {args.benchmark}")
        print(f"  Total problems:        {len(problems)}")
        print(f"  Total FALSE problems:  {total_false}")
        print(f"  Spine separated:       {separated_correct + separated_wrong}")
        print(f"    Correct (TRUE neg):  {separated_correct}")
        print(f"    Wrong (FALSE pos):   {separated_wrong}")
        print(f"  Not separated:         {not_separated}")
        if total_false > 0:
            print(f"  FALSE coverage:        {separated_correct}/{total_false} "
                  f"({100*separated_correct/total_false:.1f}%)")
        return

    equations = []
    if args.equation:
        equations.append(args.equation)
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            equations = [line.strip() for line in f if line.strip() and "=" in line]
    else:
        ap.print_help()
        return

    counts = {}
    for eq in equations:
        try:
            info = classify_spine(eq)
            key = info.spine_type.value
            depth_str = f" (depth {info.depth})" if info.depth is not None else ""
            if not args.stats:
                print(f"{key}{depth_str}: {eq}")
            counts[key] = counts.get(key, 0) + 1
        except Exception as e:
            print(f"ERROR: {eq}: {e}", file=sys.stderr)
            counts["error"] = counts.get("error", 0) + 1

    if args.stats or len(equations) > 10:
        print(f"\n  Spine type distribution ({len(equations)} equations):")
        for k, v in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    {k:20s}: {v:5d} ({100*v/len(equations):.1f}%)")


if __name__ == "__main__":
    _main()
