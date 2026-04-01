#!/usr/bin/env python3
"""
v22_coverage_analysis.py — Phase 1 analysis for v22 cheatsheet.

Computes:
  1. 8-test structural coverage on ALL normal benchmark FALSE pairs
  2. Gap analysis: which FALSE pairs escape all structural tests
  3. Comparison: graph.json matrix vs CSV matrix for benchmark pairs
  4. Equivalence class analysis
  5. Equation fingerprint uniqueness check

Run:
    python v22_coverage_analysis.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from v21_data_infrastructure import (
    ROOT,
    WITNESSES,
    WITNESS_NAMES,
    load_equations,
    build_equation_map,
    normalize_eq,
    check_equation,
    compute_witness_masks,
    load_implications_csv,
    load_all_benchmarks,
    map_benchmark_to_ids,
    witness_separates,
    mask_to_str,
    implication_answer,
)
from v21_verify_structural_rules import (
    STRUCTURAL_RULES,
    leftmost_leaf,
    rightmost_leaf,
    has_star,
    var_counts,
    var_set,
    count_stars,
)
from fetch_teorth_data import decode_graph_json


# ---------------------------------------------------------------------------
# Structural test coverage for a single equation pair
# ---------------------------------------------------------------------------
def structural_separates(eq1_norm: str, eq2_norm: str) -> list[str]:
    """
    Return list of structural test names where E1=HOLD and E2=FAIL
    (i.e., the test separates E1 → E2 as FALSE).
    """
    parts1 = eq1_norm.split(' = ', 1)
    parts2 = eq2_norm.split(' = ', 1)
    if len(parts1) != 2 or len(parts2) != 2:
        return []

    lhs1, rhs1 = parts1[0].strip(), parts1[1].strip()
    lhs2, rhs2 = parts2[0].strip(), parts2[1].strip()

    separations = []
    for name, rule_fn in STRUCTURAL_RULES.items():
        e1_holds = rule_fn(lhs1, rhs1)
        e2_holds = rule_fn(lhs2, rhs2)
        if e1_holds and not e2_holds:
            separations.append(name)
    return separations


def compute_structural_fingerprint(eq_norm: str) -> tuple:
    """
    Compute 8-bit structural fingerprint for an equation.
    Returns tuple of (LP, RP, C0, XOR, XNOR, AND, OR, Z3A) booleans.
    """
    parts = eq_norm.split(' = ', 1)
    if len(parts) != 2:
        return (False,) * 8
    lhs, rhs = parts[0].strip(), parts[1].strip()
    return tuple(rule_fn(lhs, rhs) for rule_fn in STRUCTURAL_RULES.values())


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------
def main():
    print("=" * 72)
    print("v22 Coverage Analysis — Phase 1")
    print("=" * 72)

    # Load equations and build map
    print("\n[1] Loading equations ...")
    equations = load_equations()
    eq_map = build_equation_map(equations)
    print(f"  {len(equations)} equations loaded")

    # Load graph.json matrix
    print("\n[2] Decoding graph.json ...")
    try:
        graph_data = decode_graph_json()
        graph_matrix = graph_data["matrix"]
        equiv_classes = graph_data["equivalence_classes"]
        print(f"  Matrix: {len(graph_matrix)}×{len(graph_matrix[0])}")
        print(f"  Equivalence classes: {len(equiv_classes)}")
    except FileNotFoundError:
        print("  graph.json not found — run: python fetch_teorth_data.py")
        graph_matrix = None
        equiv_classes = []

    # Load CSV matrix for comparison
    print("\n[3] Loading CSV matrix ...")
    csv_matrix = load_implications_csv()
    print(f"  CSV matrix: {len(csv_matrix)}×{len(csv_matrix[0]) if csv_matrix else 0}")

    # Compare graph.json vs CSV on a sample
    if graph_matrix:
        print("\n[4] Comparing graph.json vs CSV ...")
        agree = disagree = both_unknown = 0
        graph_resolved = csv_resolved = 0
        for i in range(0, len(graph_matrix), 10):  # sample every 10th row
            for j in range(0, len(graph_matrix[0]), 10):
                gv = graph_matrix[i][j]
                cv = csv_matrix[i][j]
                g_bool = gv > 0 if gv != 0 else None
                c_bool = cv > 0 if cv != 0 else None
                if g_bool is None and c_bool is None:
                    both_unknown += 1
                elif g_bool is None:
                    csv_resolved += 1
                elif c_bool is None:
                    graph_resolved += 1
                elif g_bool == c_bool:
                    agree += 1
                else:
                    disagree += 1
        print(f"  Sample (every 10th): agree={agree}, disagree={disagree}, "
              f"graph_only={graph_resolved}, csv_only={csv_resolved}, both_unknown={both_unknown}")
        if disagree > 0:
            print("  WARNING: Matrix disagreements found!")

    # Load benchmarks and map
    print("\n[5] Loading and mapping benchmarks ...")
    all_problems = load_all_benchmarks()
    mapped, unmapped = map_benchmark_to_ids(all_problems, eq_map)
    print(f"  Total: {len(all_problems)}, Mapped: {len(mapped)}, Unmapped: {len(unmapped)}")

    # Filter normal only
    normal_problems = [p for p in mapped if p.get("difficulty") == "normal"]
    print(f"  Normal problems: {len(normal_problems)}")

    normal_false = [p for p in normal_problems if p["answer"] is False]
    normal_true = [p for p in normal_problems if p["answer"] is True]
    print(f"  Normal FALSE: {len(normal_false)}, Normal TRUE: {len(normal_true)}")

    # Unique equations in normal benchmarks
    normal_eq_ids = set()
    for p in normal_problems:
        normal_eq_ids.add(p["eq1_id"])
        normal_eq_ids.add(p["eq2_id"])
    print(f"  Unique equations in normal benchmarks: {len(normal_eq_ids)}")

    # -----------------------------------------------------------------------
    # 8-test structural coverage on normal FALSE pairs
    # -----------------------------------------------------------------------
    print("\n[6] Structural test coverage on normal FALSE pairs ...")

    # Deduplicate FALSE pairs (same eq pair can appear in multiple benchmark files)
    false_pair_map: dict[tuple[int, int], dict] = {}
    for p in normal_false:
        key = (p["eq1_id"], p["eq2_id"])
        if key not in false_pair_map:
            false_pair_map[key] = p

    unique_false = list(false_pair_map.values())
    print(f"  Unique FALSE pairs: {len(unique_false)}")

    # Test each with all 8 structural rules
    test_coverage = Counter()  # test_name → count of pairs it catches
    pair_coverage = {}  # pair_key → list of catching tests
    uncovered = []

    for p in unique_false:
        seps = structural_separates(p["eq1_norm"], p["eq2_norm"])
        key = (p["eq1_id"], p["eq2_id"])
        pair_coverage[key] = seps
        for s in seps:
            test_coverage[s] += 1
        if not seps:
            uncovered.append(p)

    covered = len(unique_false) - len(uncovered)
    pct = 100 * covered / len(unique_false) if unique_false else 0
    print(f"  Covered by ≥1 structural test: {covered}/{len(unique_false)} ({pct:.1f}%)")
    print(f"  UNCOVERED (no structural test): {len(uncovered)}")
    print(f"  Per-test coverage:")
    for name in STRUCTURAL_RULES:
        cnt = test_coverage.get(name, 0)
        print(f"    {name}: {cnt} pairs ({100*cnt/len(unique_false):.1f}%)")

    # v21f only uses LP, RP, C0, VARS(=AND/OR)
    v21f_tests = {"LP", "RP", "C0", "AND"}  # AND == VARS in v21f logic
    v21f_covered = sum(
        1 for seps in pair_coverage.values()
        if any(s in v21f_tests for s in seps)
    )
    print(f"\n  v21f-only coverage (LP/RP/C0/VARS): {v21f_covered}/{len(unique_false)} "
          f"({100*v21f_covered/len(unique_false):.1f}%)")
    new_tests_only = sum(
        1 for seps in pair_coverage.values()
        if seps and not any(s in v21f_tests for s in seps)
    )
    print(f"  Pairs caught ONLY by new tests (XOR/Z3A/XNOR/OR): {new_tests_only}")

    # -----------------------------------------------------------------------
    # 11-witness coverage (brute-force) for comparison
    # -----------------------------------------------------------------------
    print("\n[7] 11-witness brute-force coverage ...")
    print("  Computing witness masks (this may take a few minutes) ...")
    masks = compute_witness_masks(equations)

    witness_covered = 0
    witness_uncovered = []
    witness_only_covered = []  # covered by witness but not by structural
    for p in unique_false:
        wseps = witness_separates(masks, p["eq1_id"], p["eq2_id"])
        if wseps:
            witness_covered += 1
            # Check if structural also covers
            key = (p["eq1_id"], p["eq2_id"])
            if not pair_coverage[key]:
                witness_only_covered.append((p, wseps))
        else:
            witness_uncovered.append(p)

    print(f"  Witness coverage: {witness_covered}/{len(unique_false)} "
          f"({100*witness_covered/len(unique_false):.1f}%)")
    print(f"  Witness-only (not structural): {len(witness_only_covered)}")
    if witness_only_covered:
        for p, wseps in witness_only_covered[:10]:
            print(f"    Eq{p['eq1_id']}→Eq{p['eq2_id']}: separated by {wseps}")
            print(f"      E1: {p['eq1_norm']}")
            print(f"      E2: {p['eq2_norm']}")

    # -----------------------------------------------------------------------
    # Gap analysis: pairs uncovered by BOTH structural and witnesses
    # -----------------------------------------------------------------------
    print("\n[8] Gap analysis — pairs uncovered by structural AND witnesses ...")
    deep_gap = [p for p in uncovered
                if not witness_separates(masks, p["eq1_id"], p["eq2_id"])]
    print(f"  Deep gap (no structural, no witness): {len(deep_gap)}")
    for p in deep_gap[:10]:
        print(f"    {p['id']}: Eq{p['eq1_id']}→Eq{p['eq2_id']}")
        print(f"      E1: {p['eq1_norm']}")
        print(f"      E2: {p['eq2_norm']}")

    # -----------------------------------------------------------------------
    # Equivalence class analysis
    # -----------------------------------------------------------------------
    print("\n[9] Equivalence class analysis ...")
    if equiv_classes:
        # Build eq_id → class_id map
        eq_to_class: dict[int, int] = {}
        for cls_idx, cls in enumerate(equiv_classes):
            for eq_id in cls:
                eq_to_class[eq_id] = cls_idx

        # How many classes appear in normal benchmarks?
        normal_classes = set()
        unmapped_to_class = 0
        for eid in normal_eq_ids:
            if eid in eq_to_class:
                normal_classes.add(eq_to_class[eid])
            else:
                unmapped_to_class += 1
        print(f"  Classes in normal benchmarks: {len(normal_classes)} (of {len(equiv_classes)} total)")
        if unmapped_to_class:
            print(f"  WARNING: {unmapped_to_class} equations not in any class")

        # Class size distribution for benchmark classes
        class_sizes = [len(equiv_classes[c]) for c in normal_classes]
        print(f"  Benchmark class sizes: min={min(class_sizes)}, max={max(class_sizes)}, "
              f"median={sorted(class_sizes)[len(class_sizes)//2]}")
    else:
        eq_to_class = {}
        print("  No equivalence class data available")

    # -----------------------------------------------------------------------
    # Fingerprint uniqueness
    # -----------------------------------------------------------------------
    print("\n[10] Fingerprint uniqueness check ...")
    fingerprints: dict[tuple, list[int]] = defaultdict(list)
    for eid in normal_eq_ids:
        if eid < len(equations):
            fp = compute_structural_fingerprint(equations[eid])
            fingerprints[fp].append(eid)

    unique_fps = len(fingerprints)
    collision_groups = {fp: ids for fp, ids in fingerprints.items() if len(ids) > 1}
    print(f"  Unique fingerprints: {unique_fps} (for {len(normal_eq_ids)} equations)")
    print(f"  Collision groups: {len(collision_groups)}")
    if collision_groups:
        # Show top 5 largest collision groups
        sorted_groups = sorted(collision_groups.items(), key=lambda x: -len(x[1]))
        for fp, ids in sorted_groups[:5]:
            labels = ["LP","RP","C0","XOR","XNOR","AND","OR","Z3A"]
            fp_str = "".join(l if v else "." for l, v in zip(labels, fp))
            print(f"    fp={fp_str}: {len(ids)} equations (IDs: {ids[:10]}{'...' if len(ids)>10 else ''})")

    # -----------------------------------------------------------------------
    # Summary: per-benchmark-file coverage
    # -----------------------------------------------------------------------
    print("\n[11] Per-benchmark structural coverage (8 tests) ...")
    by_file: dict[str, dict] = defaultdict(
        lambda: {"total": 0, "false": 0, "struct_covered": 0, "true": 0}
    )
    for p in normal_problems:
        bf = p["_benchmark_file"]
        by_file[bf]["total"] += 1
        if p["answer"] is True:
            by_file[bf]["true"] += 1
        else:
            by_file[bf]["false"] += 1
            seps = structural_separates(p["eq1_norm"], p["eq2_norm"])
            if seps:
                by_file[bf]["struct_covered"] += 1

    for bf in sorted(by_file):
        d = by_file[bf]
        false_cov = 100 * d["struct_covered"] / d["false"] if d["false"] > 0 else 100.0
        # Predicted accuracy: TRUE always correct (default TRUE), FALSE = struct_covered
        predicted_correct = d["true"] + d["struct_covered"]
        predicted_acc = 100 * predicted_correct / d["total"] if d["total"] > 0 else 0
        print(f"  {bf}: total={d['total']} T={d['true']} F={d['false']} "
              f"struct_cov={d['struct_covered']} ({false_cov:.0f}%) "
              f"predicted_acc={predicted_acc:.0f}%")

    # -----------------------------------------------------------------------
    # Save analysis
    # -----------------------------------------------------------------------
    output = {
        "unique_normal_equations": len(normal_eq_ids),
        "unique_false_pairs": len(unique_false),
        "structural_covered": covered,
        "structural_coverage_pct": round(pct, 2),
        "structural_uncovered": len(uncovered),
        "v21f_covered": v21f_covered,
        "new_tests_only": new_tests_only,
        "witness_covered": witness_covered,
        "witness_only": len(witness_only_covered),
        "deep_gap": len(deep_gap),
        "unique_fingerprints": unique_fps,
        "fingerprint_collisions": len(collision_groups),
        "equiv_classes_in_benchmark": len(normal_classes) if equiv_classes else 0,
        "uncovered_pairs": [
            {
                "id": p["id"],
                "eq1_id": p["eq1_id"],
                "eq2_id": p["eq2_id"],
                "eq1": p["eq1_norm"],
                "eq2": p["eq2_norm"],
                "witness_seps": witness_separates(masks, p["eq1_id"], p["eq2_id"]),
            }
            for p in uncovered
        ],
        "deep_gap_pairs": [
            {
                "id": p["id"],
                "eq1_id": p["eq1_id"],
                "eq2_id": p["eq2_id"],
                "eq1": p["eq1_norm"],
                "eq2": p["eq2_norm"],
            }
            for p in deep_gap
        ],
    }
    out_path = ROOT / "data" / "exports" / "v22_coverage_analysis.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\n  Analysis saved to {out_path}")

    print("\n" + "=" * 72)
    print("v22 Coverage Analysis complete.")
    print("=" * 72)


if __name__ == "__main__":
    main()
