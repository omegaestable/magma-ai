#!/usr/bin/env python3
"""
v21_coverage_detail.py — Detailed analysis of structural-only witness coverage
vs full 11-witness coverage for benchmark FALSE pairs.
Also analyzes TRUE pair characteristics for heuristic design.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from v21_data_infrastructure import (
    load_equations, build_equation_map, compute_witness_masks,
    load_implications_csv, load_all_benchmarks, map_benchmark_to_ids,
    witness_separates, mask_to_str, WITNESSES, WITNESS_NAMES,
    normalize_eq
)
from v21_verify_structural_rules import (
    STRUCTURAL_RULES, leftmost_leaf, rightmost_leaf, has_star,
    var_counts, var_set, count_stars
)


STRUCTURAL_WITNESS_INDICES = [i for i, w in enumerate(WITNESSES) if w["name"] in STRUCTURAL_RULES]
ARITHMETIC_WITNESS_INDICES = [i for i, w in enumerate(WITNESSES) if w["name"] not in STRUCTURAL_RULES]


def structural_separates(masks, eq1_id, eq2_id):
    """Return list of STRUCTURAL witness names that separate E1 from E2."""
    m1, m2 = masks[eq1_id], masks[eq2_id]
    seps = []
    for i in STRUCTURAL_WITNESS_INDICES:
        if (m1 & (1 << i)) and not (m2 & (1 << i)):
            seps.append(WITNESS_NAMES[i])
    return seps


def arithmetic_only_separates(masks, eq1_id, eq2_id):
    """Return list of witnesses that ONLY arithmetic witnesses can separate."""
    m1, m2 = masks[eq1_id], masks[eq2_id]
    seps = []
    for i in ARITHMETIC_WITNESS_INDICES:
        if (m1 & (1 << i)) and not (m2 & (1 << i)):
            seps.append(WITNESS_NAMES[i])
    return seps


def analyze_true_pair(eq1, eq2):
    """Extract structural features of a TRUE pair."""
    parts1 = eq1.split(' = ', 1)
    parts2 = eq2.split(' = ', 1)
    lhs1, rhs1 = parts1[0].strip(), parts1[1].strip() if len(parts1) == 2 else ("", "")
    lhs2, rhs2 = parts2[0].strip(), parts2[1].strip() if len(parts2) == 2 else ("", "")
    
    # Is E2 a singleton (x = y)?
    e2_singleton = lhs2 in ['x', 'y'] and rhs2 in ['x', 'y'] and lhs2 != rhs2
    
    # Variable sets
    vs1 = var_set(eq1)
    vs2 = var_set(eq2)
    
    # E2 introduces fresh variables?
    fresh_in_e2 = vs2 - vs1
    
    return {
        "e2_singleton": e2_singleton,
        "e1_vars": vs1,
        "e2_vars": vs2,
        "fresh_in_e2": fresh_in_e2,
        "e1_stars": count_stars(eq1),
        "e2_stars": count_stars(eq2),
    }


def main():
    equations = load_equations()
    eq_map = build_equation_map(equations)
    masks = compute_witness_masks(equations)
    all_problems = load_all_benchmarks()
    mapped, _ = map_benchmark_to_ids(all_problems, eq_map)
    
    false_pairs = [p for p in mapped if p["answer"] is False]
    true_pairs = [p for p in mapped if p["answer"] is True]
    
    print("=" * 72)
    print("Witness Coverage Detail")
    print("=" * 72)
    
    # Structural-only coverage
    struct_covered = 0
    arith_only_covered = 0
    neither_covered = 0
    for p in false_pairs:
        s = structural_separates(masks, p["eq1_id"], p["eq2_id"])
        a = arithmetic_only_separates(masks, p["eq1_id"], p["eq2_id"])
        if s:
            struct_covered += 1
        elif a:
            arith_only_covered += 1
        else:
            neither_covered += 1
    
    total_false = len(false_pairs)
    print(f"\nFALSE pairs: {total_false}")
    print(f"  Structural witnesses cover: {struct_covered} ({100*struct_covered/total_false:.1f}%)")
    print(f"  Arithmetic-only witnesses add: {arith_only_covered} ({100*arith_only_covered/total_false:.1f}%)")
    print(f"  No witness covers: {neither_covered} ({100*neither_covered/total_false:.1f}%)")
    print(f"  Total witness coverage: {struct_covered + arith_only_covered} ({100*(struct_covered+arith_only_covered)/total_false:.1f}%)")
    
    # Per-benchmark structural coverage
    print("\n--- Per-benchmark structural-only coverage ---")
    by_file = defaultdict(lambda: {"false": 0, "struct": 0, "arith_only": 0, "neither": 0})
    for p in false_pairs:
        bf = p["_benchmark_file"]
        by_file[bf]["false"] += 1
        s = structural_separates(masks, p["eq1_id"], p["eq2_id"])
        a = arithmetic_only_separates(masks, p["eq1_id"], p["eq2_id"])
        if s:
            by_file[bf]["struct"] += 1
        elif a:
            by_file[bf]["arith_only"] += 1
        else:
            by_file[bf]["neither"] += 1
    for bf in sorted(by_file):
        d = by_file[bf]
        s_pct = 100 * d["struct"] / d["false"] if d["false"] else 0
        print(f"  {bf}: FALSE={d['false']}, structural={d['struct']}({s_pct:.0f}%), arith_only={d['arith_only']}, uncovered={d['neither']}")
    
    # TRUE pair analysis
    print("\n--- TRUE pair feature analysis ---")
    features = []
    for p in true_pairs:
        f = analyze_true_pair(p["eq1_norm"], p["eq2_norm"])
        f["id"] = p["id"]
        features.append(f)
    
    singleton_count = sum(1 for f in features if f["e2_singleton"])
    fresh_var_count = sum(1 for f in features if f["fresh_in_e2"])
    print(f"  Total TRUE pairs: {len(true_pairs)}")
    print(f"  E2 is singleton (x=y): {singleton_count}")
    print(f"  E2 introduces fresh variables: {fresh_var_count}")
    
    # For FALSE pairs: how many have fresh variables in E2?
    false_fresh = 0
    for p in false_pairs:
        parts1 = p["eq1_norm"].split(' = ', 1)
        parts2 = p["eq2_norm"].split(' = ', 1)
        vs1 = var_set(p["eq1_norm"])
        vs2 = var_set(p["eq2_norm"])
        if vs2 - vs1:
            false_fresh += 1
    print(f"\n  FALSE pairs with fresh vars in E2: {false_fresh}/{total_false}")
    print(f"  (Fresh vars in E2 is NOT a reliable TRUE signal)")
    
    # What's the accuracy of "default TRUE when no witness separates" strategy?
    print("\n--- Strategy: 'TRUE unless structural witness separates' ---")
    correct = 0
    wrong = 0
    for p in mapped:
        is_true = p["answer"]
        s = structural_separates(masks, p["eq1_id"], p["eq2_id"])
        if s:
            predicted = False  # witness separates → FALSE
        else:
            predicted = True   # no separation → default TRUE
        if predicted == is_true:
            correct += 1
        else:
            wrong += 1
    print(f"  Accuracy: {correct}/{len(mapped)} ({100*correct/len(mapped):.1f}%)")
    
    # What about "TRUE unless ANY witness (including arithmetic) separates"?
    print("\n--- Strategy: 'TRUE unless any witness separates' ---")
    correct2 = 0
    for p in mapped:
        is_true = p["answer"]
        all_seps = witness_separates(masks, p["eq1_id"], p["eq2_id"])
        predicted = not bool(all_seps)
        if predicted == is_true:
            correct2 += 1
    print(f"  Accuracy: {correct2}/{len(mapped)} ({100*correct2/len(mapped):.1f}%)")

    # Unique equations in uncovered FALSE pairs
    print("\n--- Uncovered FALSE pairs: equation diversity ---")
    uncovered_eqs = set()
    uncovered_pairs_unique = set()
    for p in false_pairs:
        if not witness_separates(masks, p["eq1_id"], p["eq2_id"]):
            uncovered_eqs.add(p["eq1_id"])
            uncovered_eqs.add(p["eq2_id"])
            uncovered_pairs_unique.add((p["eq1_id"], p["eq2_id"]))
    print(f"  Unique equation IDs in uncovered FALSE: {len(uncovered_eqs)}")
    print(f"  Unique (E1,E2) pairs: {len(uncovered_pairs_unique)}")
    print(f"  (Many benchmark files reuse the same pairs)")


if __name__ == "__main__":
    main()
