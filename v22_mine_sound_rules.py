"""Mine sound implication-separation rules from equation features.

A rule is based on an invariant I(eq): boolean.
Separation condition: I(E1)=True and I(E2)=False => E1 does NOT imply E2.
We keep only rules that are globally sound against the full implications matrix.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from v21_data_infrastructure import (
    load_equations,
    load_implications_csv,
    implication_answer,
    normalize_eq,
    build_equation_map,
)


def split_eq(eq: str) -> Tuple[str, str]:
    lhs, rhs = eq.split(" = ", 1)
    return lhs.strip(), rhs.strip()


def letters(s: str) -> List[str]:
    return [c for c in s if "a" <= c <= "z"]


def var_counts(s: str) -> Dict[str, int]:
    out = {v: 0 for v in "xyzwu"}
    for c in s:
        if c in out:
            out[c] += 1
    return out


def star_count(s: str) -> int:
    return s.count("*")


def max_paren_depth(s: str) -> int:
    d = 0
    m = 0
    for c in s:
        if c == "(":
            d += 1
            if d > m:
                m = d
        elif c == ")":
            d -= 1
    return m


def shape_sig(s: str) -> str:
    # Replace vars with v to capture tree shape independent of variable names.
    t = []
    for c in s:
        if "a" <= c <= "z":
            t.append("v")
        elif c in "()*":
            t.append(c)
    return "".join(t)


def multiset_sig(s: str) -> Tuple[int, int, int, int, int]:
    c = var_counts(s)
    return (c["x"], c["y"], c["z"], c["w"], c["u"])


def multiset_mod2(s: str) -> Tuple[int, int, int, int, int]:
    c = var_counts(s)
    return (c["x"] % 2, c["y"] % 2, c["z"] % 2, c["w"] % 2, c["u"] % 2)


def multiset_mod3(s: str) -> Tuple[int, int, int, int, int]:
    c = var_counts(s)
    return (c["x"] % 3, c["y"] % 3, c["z"] % 3, c["w"] % 3, c["u"] % 3)


def lhs_rhs_invariant(eq: str, feat: Callable[[str], object]) -> bool:
    lhs, rhs = split_eq(eq)
    return feat(lhs) == feat(rhs)


def lhs_rhs_invariant_custom(eq: str, pred: Callable[[str, str], bool]) -> bool:
    lhs, rhs = split_eq(eq)
    return pred(lhs, rhs)


def evaluate_rule_soundness(inv: List[bool], matrix: List[List[int]]) -> Tuple[bool, int]:
    n = len(inv)
    sep = 0
    for i in range(n):
        if not inv[i]:
            continue
        for j in range(n):
            if inv[j]:
                continue
            sep += 1
            ans = implication_answer(matrix, i, j)
            if ans is not False:
                return False, sep
    return True, sep


def coverage_on_dataset(inv: List[bool], eq_map: Dict[str, int], path: Path) -> Tuple[int, int]:
    total_false = 0
    caught_false = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row["answer"] is True:
                continue
            total_false += 1
            i = eq_map.get(normalize_eq(row["equation1"]))
            j = eq_map.get(normalize_eq(row["equation2"]))
            if i is None or j is None:
                continue
            if inv[i] and not inv[j]:
                caught_false += 1
    return caught_false, total_false


def main() -> None:
    equations = load_equations()
    matrix = load_implications_csv()
    eq_map = build_equation_map(equations)

    feature_rules: Dict[str, Callable[[str], bool]] = {
        "LP": lambda e: lhs_rhs_invariant(e, lambda s: letters(s)[0]),
        "RP": lambda e: lhs_rhs_invariant(e, lambda s: letters(s)[-1]),
        "VARS": lambda e: lhs_rhs_invariant(e, lambda s: tuple(sorted(set(letters(s))))),
        "XOR": lambda e: lhs_rhs_invariant(e, multiset_mod2),
        "Z3A": lambda e: lhs_rhs_invariant(e, multiset_mod3),
        "STAR_PARITY": lambda e: lhs_rhs_invariant(e, lambda s: star_count(s) % 2),
        "STAR_MOD3": lambda e: lhs_rhs_invariant(e, lambda s: star_count(s) % 3),
        "STAR_EXACT": lambda e: lhs_rhs_invariant(e, star_count),
        "DEPTH_EXACT": lambda e: lhs_rhs_invariant(e, max_paren_depth),
        "SHAPE": lambda e: lhs_rhs_invariant(e, shape_sig),
        "COUNT_EXACT": lambda e: lhs_rhs_invariant(e, multiset_sig),
        "LEN_EXACT": lambda e: lhs_rhs_invariant(e, lambda s: len(s.replace(" ", ""))),
        "C0": lambda e: lhs_rhs_invariant_custom(
            e,
            lambda l, r: ("*" in l and "*" in r)
            or ("*" not in l and "*" not in r and l.strip() == r.strip()),
        ),
    }

    print("Evaluating candidate rules for global soundness...")
    survivors = []
    for name, fn in feature_rules.items():
        inv = [fn(eq) for eq in equations]
        ok, sep = evaluate_rule_soundness(inv, matrix)
        print(f"  {name:12s} sound={ok} separations={sep}")
        if ok:
            survivors.append((name, inv, sep))

    hard3 = Path("data/hf_cache/hard3.jsonl")
    normal_seed = Path("data/benchmark/normal_balanced20_true10_false10_seed0.jsonl")
    print("\nCoverage on datasets (FALSE pairs only):")
    for name, inv, _ in survivors:
        hc, ht = coverage_on_dataset(inv, eq_map, hard3)
        nc, nt = coverage_on_dataset(inv, eq_map, normal_seed)
        print(f"  {name:12s} hard3={hc}/{ht}  normal={nc}/{nt}")


if __name__ == "__main__":
    main()
