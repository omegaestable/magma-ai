#!/usr/bin/env python3
"""
witness_coverage_audit.py — Phase 0: audit which canned witnesses catch hard FALSE pairs.

Tests ALL 11 witnesses from v21_data_infrastructure against every FALSE pair
in hard2 and hard3 benchmarks. Reports:
  1. Per-pair: which witnesses separate E1 from E2
  2. Per-witness: how many hard-FALSE pairs it catches
  3. Coverage gaps: FALSE pairs with NO witness in the current library
  4. Additional magma candidates: brute-force 2-elem and 3-elem tables for uncaught pairs

Usage:
    python witness_coverage_audit.py
    python witness_coverage_audit.py --include-normal   # also audit normal benchmarks
    python witness_coverage_audit.py --mine-extras      # search for new witnesses
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

# Reuse distill.py's equation evaluator
from distill import check_equation, first_failing_assignment, parse_equation_tree

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "data" / "benchmark"

# Full 11-witness library (from v21_data_infrastructure.py)
WITNESSES = [
    {"name": "LP",   "rule": "x*y = x",              "table": [[0, 0], [1, 1]]},
    {"name": "RP",   "rule": "x*y = y",              "table": [[0, 1], [0, 1]]},
    {"name": "C0",   "rule": "x*y = 0",              "table": [[0, 0], [0, 0]]},
    {"name": "XOR",  "rule": "x*y = (x+y) mod 2",    "table": [[0, 1], [1, 0]]},
    {"name": "Z3A",  "rule": "x*y = (x+y) mod 3",    "table": [[0, 1, 2], [1, 2, 0], [2, 0, 1]]},
    {"name": "AND",  "rule": "x*y = min(x,y)",        "table": [[0, 0], [0, 1]]},
    {"name": "OR",   "rule": "x*y = max(x,y)",        "table": [[0, 1], [1, 1]]},
    {"name": "XNOR", "rule": "x*y = 1 iff x=y",      "table": [[1, 0], [0, 1]]},
    {"name": "A2",   "rule": "x*y = x AND NOT y",     "table": [[0, 0], [1, 0]]},
    {"name": "T3L",  "rule": "3-elem sparse L",       "table": [[0, 0, 0], [0, 0, 0], [0, 1, 0]]},
    {"name": "T3R",  "rule": "3-elem sparse R",       "table": [[0, 0, 0], [0, 0, 0], [0, 0, 1]]},
]


def load_benchmark(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def find_witnesses(eq1: str, eq2: str, witness_lib: list[dict]) -> list[dict]:
    """Find all witnesses that satisfy E1 but have a failing assignment for E2."""
    results = []
    for w in witness_lib:
        table = w["table"]
        if not check_equation(eq1, table):
            continue
        failure = first_failing_assignment(eq2, table)
        if failure is None:
            continue
        results.append({
            "name": w["name"],
            "rule": w.get("rule", ""),
            "assignment": failure["assignment"],
            "lhs_value": failure["lhs_value"],
            "rhs_value": failure["rhs_value"],
        })
    return results


def generate_all_2elem_magmas():
    """Generate all 16 possible 2-element magma tables."""
    for a00 in range(2):
        for a01 in range(2):
            for a10 in range(2):
                for a11 in range(2):
                    yield [[a00, a01], [a10, a11]]


def generate_all_3elem_magmas():
    """Generate all 3^9 = 19683 possible 3-element magma tables."""
    for vals in itertools.product(range(3), repeat=9):
        yield [
            [vals[0], vals[1], vals[2]],
            [vals[3], vals[4], vals[5]],
            [vals[6], vals[7], vals[8]],
        ]


def mine_extra_witnesses(uncaught_pairs: list[dict], max_size: int = 3) -> list[dict]:
    """Brute-force search for magmas that catch uncaught FALSE pairs."""
    print(f"\n{'='*60}")
    print(f"Mining extra witnesses for {len(uncaught_pairs)} uncaught pairs...")
    print(f"{'='*60}")

    # Track best new witnesses
    new_witnesses: dict[str, dict] = {}  # table_key -> {table, caught_pairs, caught_count}

    # Try all 2-element magmas first (fast: only 16)
    print("\nSearching 2-element magmas (16 total)...")
    for table in generate_all_2elem_magmas():
        key = str(table)
        # Skip if it's already in our library
        if any(str(w["table"]) == key for w in WITNESSES):
            continue
        caught = []
        for pair in uncaught_pairs:
            if check_equation(pair["equation1"], table):
                failure = first_failing_assignment(pair["equation2"], table)
                if failure is not None:
                    caught.append(pair["id"])
        if caught:
            new_witnesses[key] = {"table": table, "caught_pairs": caught, "caught_count": len(caught)}

    if max_size >= 3:
        print("Searching 3-element magmas (19,683 total)...")
        count = 0
        for table in generate_all_3elem_magmas():
            count += 1
            if count % 5000 == 0:
                print(f"  ...checked {count}/19683")
            key = str(table)
            if any(str(w["table"]) == key for w in WITNESSES):
                continue
            caught = []
            for pair in uncaught_pairs:
                if check_equation(pair["equation1"], table):
                    failure = first_failing_assignment(pair["equation2"], table)
                    if failure is not None:
                        caught.append(pair["id"])
            if caught:
                existing = new_witnesses.get(key)
                if existing is None or len(caught) > existing["caught_count"]:
                    new_witnesses[key] = {"table": table, "caught_pairs": caught, "caught_count": len(caught)}

    # Rank by catch count
    ranked = sorted(new_witnesses.values(), key=lambda x: -x["caught_count"])

    # Greedy set-cover: pick witnesses that maximize marginal coverage
    covered = set()
    selected = []
    for w in ranked:
        new_catch = set(w["caught_pairs"]) - covered
        if new_catch:
            covered |= new_catch
            selected.append({
                "table": w["table"],
                "caught_count": len(new_catch),
                "marginal_pairs": sorted(new_catch),
                "total_pairs": sorted(w["caught_pairs"]),
            })

    return selected


def audit_benchmarks(benchmark_files: list[Path], do_mine: bool = False, mine_size: int = 3):
    all_false_pairs = []
    pair_results = []

    for bf in benchmark_files:
        if not bf.exists():
            print(f"SKIP (not found): {bf.name}")
            continue
        rows = load_benchmark(bf)
        false_rows = [r for r in rows if r.get("answer") is False]
        true_rows = [r for r in rows if r.get("answer") is True]
        print(f"\n{'='*60}")
        print(f"Benchmark: {bf.name}")
        print(f"  Total: {len(rows)}, TRUE: {len(true_rows)}, FALSE: {len(false_rows)}")
        print(f"{'='*60}")

        for row in false_rows:
            eq1 = row["equation1"]
            eq2 = row["equation2"]
            pid = row["id"]
            witnesses = find_witnesses(eq1, eq2, WITNESSES)
            witness_names = [w["name"] for w in witnesses]
            pair_results.append({
                "benchmark": bf.name,
                "id": pid,
                "equation1": eq1,
                "equation2": eq2,
                "witnesses": witness_names,
                "witness_details": witnesses,
                "caught": len(witnesses) > 0,
            })
            all_false_pairs.append(row)

            status = "CAUGHT" if witnesses else "UNCAUGHT"
            wlist = ", ".join(witness_names) if witness_names else "---"
            print(f"  [{status}] {pid}: {wlist}")
            if witnesses:
                # Show first witness detail
                w = witnesses[0]
                print(f"           via {w['name']}: assign {w['assignment']} → LHS={w['lhs_value']}, RHS={w['rhs_value']}")

    # Summary
    caught_count = sum(1 for p in pair_results if p["caught"])
    uncaught_count = len(pair_results) - caught_count
    print(f"\n{'='*60}")
    print(f"SUMMARY: {caught_count}/{len(pair_results)} FALSE pairs caught ({100*caught_count/max(len(pair_results),1):.1f}%)")
    print(f"         {uncaught_count} pairs have NO witness in current 11-library")
    print(f"{'='*60}")

    # Per-witness breakdown
    witness_counts = defaultdict(int)
    for p in pair_results:
        for wn in p["witnesses"]:
            witness_counts[wn] += 1
    print("\nPer-witness catch counts:")
    for name in sorted(witness_counts, key=lambda k: -witness_counts[k]):
        print(f"  {name:6s}: catches {witness_counts[name]} pairs")

    # Uncaught pairs
    uncaught_pairs = [p for p in pair_results if not p["caught"]]
    if uncaught_pairs:
        print(f"\nUncaught FALSE pairs ({len(uncaught_pairs)}):")
        for p in uncaught_pairs:
            print(f"  {p['id']}: {p['equation1']}  →  {p['equation2']}")

    # Mine extras if requested
    if do_mine and uncaught_pairs:
        uncaught_for_mining = []
        for p in uncaught_pairs:
            uncaught_for_mining.append({
                "id": p["id"],
                "equation1": p["equation1"],
                "equation2": p["equation2"],
            })
        extras = mine_extra_witnesses(uncaught_for_mining, max_size=mine_size)
        if extras:
            print(f"\nTop new witnesses found ({len(extras)} selected by greedy set-cover):")
            total_new_caught = 0
            for i, w in enumerate(extras):
                total_new_caught += w["caught_count"]
                print(f"  #{i+1}: table={w['table']}")
                print(f"       catches {w['caught_count']} NEW pairs: {w['marginal_pairs']}")
            remaining = uncaught_count - total_new_caught
            print(f"\n  After adding these: {caught_count + total_new_caught}/{len(pair_results)} caught, {remaining} still uncaught")
        else:
            print(f"\nNo new size-≤{mine_size} witnesses found for uncaught pairs.")
            if mine_size < 4:
                print("  Try --mine-size 4 for 4-element magma search (slow: 4^16 = 4B tables)")

    # Also check: do any witnesses cause FALSE on TRUE pairs? (safety check)
    print(f"\n{'='*60}")
    print("SAFETY CHECK: Do any witnesses false-flag TRUE pairs?")
    print(f"{'='*60}")
    for bf in benchmark_files:
        if not bf.exists():
            continue
        rows = load_benchmark(bf)
        true_rows = [r for r in rows if r.get("answer") is True]
        for row in true_rows:
            eq1 = row["equation1"]
            eq2 = row["equation2"]
            pid = row["id"]
            witnesses = find_witnesses(eq1, eq2, WITNESSES)
            if witnesses:
                wnames = ", ".join(w["name"] for w in witnesses)
                print(f"  WARNING: {pid} (TRUE) flagged by witnesses: {wnames}")
    print("  (No warnings = witnesses are safe on TRUE pairs)")

    return pair_results


def main():
    parser = argparse.ArgumentParser(description="Witness coverage audit for hard benchmarks")
    parser.add_argument("--include-normal", action="store_true", help="Also audit normal benchmarks")
    parser.add_argument("--mine-extras", action="store_true", help="Search for new witnesses for uncaught pairs")
    parser.add_argument("--mine-size", type=int, default=3, help="Max magma size to search (default: 3)")
    args = parser.parse_args()

    benchmarks = [
        BENCHMARK_DIR / "hard1_balanced6_true3_false3_seed0.jsonl",
        BENCHMARK_DIR / "hard1_balanced14_true7_false7_seed0.jsonl",
        BENCHMARK_DIR / "hard2_balanced14_true7_false7_seed0.jsonl",
        BENCHMARK_DIR / "hard3_balanced26_true13_false13_seed0.jsonl",
        BENCHMARK_DIR / "hard3_balanced20_true10_false10_rotation0001_20260403_163406.jsonl",
        BENCHMARK_DIR / "hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl",
        BENCHMARK_DIR / "hard_balanced40_true20_false20_rotation0001_20260403_163406.jsonl",
    ]
    if args.include_normal:
        benchmarks += sorted(BENCHMARK_DIR.glob("normal_*.jsonl"))

    audit_benchmarks(benchmarks, do_mine=args.mine_extras, mine_size=args.mine_size)


if __name__ == "__main__":
    main()
