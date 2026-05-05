#!/usr/bin/env python3
"""
hard3_magma_mining.py — Phase 2: Find the best small magma(s) for hard3 FALSE separation.

Enumerates all 2-element (16) and 3-element (19,683) magmas, tests each against
all hard3 FALSE pairs, ranks by coverage, then safety-checks winners against
ALL TRUE pairs (normal + hard3).

Usage:
    python hard3_magma_mining.py                      # mine 2-elem + 3-elem
    python hard3_magma_mining.py --max-size 2         # 2-elem only (fast)
    python hard3_magma_mining.py --safety-check       # also check TRUE pairs
    python hard3_magma_mining.py --also-normal        # include normal FALSE pairs in coverage
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

from distill import check_equation, first_failing_assignment

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "data" / "benchmark"


def load_benchmark(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def find_hard3_file() -> Path:
    """Find the canonical hard3 benchmark file."""
    candidates = sorted(BENCHMARK_DIR.glob("hard3_balanced40_*rotation0002*.jsonl"))
    if not candidates:
        sys.exit("ERROR: No hard3 rotation0002 benchmark found in data/benchmark/")
    return candidates[-1]


def find_normal_file() -> Path:
    """Find the canonical normal-60 benchmark file."""
    candidates = sorted(BENCHMARK_DIR.glob("normal_balanced60_*rotation0002*.jsonl"))
    if not candidates:
        sys.exit("ERROR: No normal rotation0002 benchmark found in data/benchmark/")
    return candidates[-1]


def generate_all_magmas(size: int):
    """Generate all possible magma tables of given size."""
    cells = size * size
    for vals in itertools.product(range(size), repeat=cells):
        yield [list(vals[i * size:(i + 1) * size]) for i in range(size)]


def test_magma_separation(table: list[list[int]], eq1: str, eq2: str) -> bool:
    """Returns True if table satisfies eq1 but NOT eq2 (separation)."""
    if not check_equation(eq1, table):
        return False
    return not check_equation(eq2, table)


def mine_magmas(false_pairs: list[dict], max_size: int = 3, verbose: bool = True) -> dict:
    """
    Enumerate all magmas up to max_size and test against false_pairs.
    Returns {table_key: {"table": ..., "caught_ids": set, "size": int}}
    """
    results = {}

    for size in range(2, max_size + 1):
        total = size ** (size * size)
        if verbose:
            print(f"\nSearching {size}-element magmas ({total:,} total)...")

        count = 0
        report_interval = max(1, total // 20)
        for table in generate_all_magmas(size):
            count += 1
            if verbose and count % report_interval == 0:
                print(f"  ...checked {count:,}/{total:,} ({100*count//total}%)")

            caught_ids = set()
            for pair in false_pairs:
                if test_magma_separation(table, pair["equation1"], pair["equation2"]):
                    caught_ids.add(pair["id"])

            if caught_ids:
                key = str(table)
                # Keep if new or better than existing with same key
                if key not in results or len(caught_ids) > len(results[key]["caught_ids"]):
                    results[key] = {
                        "table": table,
                        "caught_ids": caught_ids,
                        "size": size,
                    }

        if verbose:
            this_size = [r for r in results.values() if r["size"] == size]
            if this_size:
                best = max(this_size, key=lambda r: len(r["caught_ids"]))
                print(f"  Best {size}-elem magma catches {len(best['caught_ids'])}/{len(false_pairs)} pairs")
            else:
                print(f"  No {size}-element magma separates any pair")

    return results


def greedy_set_cover(results: dict, n_pairs: int, verbose: bool = True) -> list[dict]:
    """Greedy set-cover: pick magmas that maximize marginal coverage."""
    covered = set()
    selected = []

    # Rank all by catch count
    ranked = sorted(results.values(), key=lambda r: -len(r["caught_ids"]))

    while ranked:
        best = None
        best_marginal = 0
        for r in ranked:
            marginal = len(r["caught_ids"] - covered)
            if marginal > best_marginal:
                best = r
                best_marginal = marginal
        if best is None or best_marginal == 0:
            break

        covered |= best["caught_ids"]
        selected.append({
            "table": best["table"],
            "size": best["size"],
            "marginal_catch": best_marginal,
            "total_catch": len(best["caught_ids"]),
            "caught_ids": sorted(best["caught_ids"]),
            "cumulative_coverage": len(covered),
        })

        if verbose:
            print(f"  Pick #{len(selected)}: {best['table']} (size={best['size']}) "
                  f"catches {best_marginal} new → {len(covered)}/{n_pairs} total")

        # Remove from ranked
        ranked = [r for r in ranked if r is not best]

    return selected


def safety_check(magmas: list[dict], true_pairs: list[dict], verbose: bool = True) -> list[dict]:
    """
    For each magma, count how many TRUE pairs it would FALSE-FLAG.
    A false-flag: magma satisfies E1 but not E2, causing an incorrect FALSE prediction.
    """
    results = []
    for m in magmas:
        table = m["table"]
        false_flags = []
        for pair in true_pairs:
            if test_magma_separation(table, pair["equation1"], pair["equation2"]):
                false_flags.append(pair["id"])
        m_result = {
            **m,
            "false_flag_count": len(false_flags),
            "false_flag_ids": false_flags,
        }
        results.append(m_result)
        if verbose:
            status = "SAFE" if not false_flags else f"UNSAFE ({len(false_flags)} flags)"
            print(f"  {m['table']} → {status}")
            if false_flags:
                for fid in false_flags[:5]:
                    print(f"    false-flags: {fid}")
    return results


def vars_marginal_importance(false_pairs_all: list[dict]) -> dict:
    """
    For each FALSE pair, determine which of the 4 structural tests (LP, RP, C0, VARS)
    provides separation. Returns per-test counts and pairs where ONLY VARS separates.
    """
    # The 4 structural test magmas:
    LP_TABLE = [[0, 0], [1, 1]]   # x*y = x
    RP_TABLE = [[0, 1], [0, 1]]   # x*y = y
    C0_TABLE = [[0, 0], [0, 0]]   # x*y = 0

    results = {"LP": [], "RP": [], "C0": [], "VARS_only": [], "none": []}
    for pair in false_pairs_all:
        eq1, eq2 = pair["equation1"], pair["equation2"]
        pid = pair["id"]
        separators = []
        if test_magma_separation(LP_TABLE, eq1, eq2):
            separators.append("LP")
        if test_magma_separation(RP_TABLE, eq1, eq2):
            separators.append("RP")
        if test_magma_separation(C0_TABLE, eq1, eq2):
            separators.append("C0")

        # VARS test is structural (not a magma) — it checks variable-set mismatch
        # We approximate VARS separation: E1 passes LP/RP/C0 but E2 fails them differently
        # Actually, VARS = set of distinct variables on left vs right
        # A pair is "VARS-separated" if E1 has matching var-sets and E2 doesn't (or vice versa)
        # For now, skip VARS approximation — we'll check manually

        if separators:
            for s in separators:
                results[s].append(pid)
        else:
            results["none"].append(pid)

    return results


def main():
    parser = argparse.ArgumentParser(description="Mine best small magmas for hard3 FALSE separation")
    parser.add_argument("--max-size", type=int, default=3, help="Max magma size to search (2 or 3)")
    parser.add_argument("--safety-check", action="store_true", help="Also check TRUE pairs for false-flags")
    parser.add_argument("--also-normal", action="store_true", help="Include normal FALSE pairs in coverage")
    parser.add_argument("--top-n", type=int, default=10, help="Show top N individual magmas")
    parser.add_argument("--greedy-n", type=int, default=5, help="Select up to N magmas via set cover")
    args = parser.parse_args()

    # Load hard3 benchmark
    hard3_file = find_hard3_file()
    hard3_rows = load_benchmark(hard3_file)
    hard3_false = [r for r in hard3_rows if r.get("answer") is False]
    hard3_true = [r for r in hard3_rows if r.get("answer") is True]
    print(f"Hard3 benchmark: {hard3_file.name}")
    print(f"  FALSE pairs: {len(hard3_false)}, TRUE pairs: {len(hard3_true)}")

    # Optionally load normal benchmark
    normal_false = []
    normal_true = []
    if args.also_normal or args.safety_check:
        normal_file = find_normal_file()
        normal_rows = load_benchmark(normal_file)
        normal_false = [r for r in normal_rows if r.get("answer") is False]
        normal_true = [r for r in normal_rows if r.get("answer") is True]
        print(f"Normal benchmark: {normal_file.name}")
        print(f"  FALSE pairs: {len(normal_false)}, TRUE pairs: {len(normal_true)}")

    # Combine target FALSE pairs
    target_false = hard3_false[:]
    if args.also_normal:
        target_false.extend(normal_false)
    print(f"\nTarget FALSE pairs for mining: {len(target_false)}")

    # === PHASE 2.1-2.3: Mine and rank magmas ===
    print("\n" + "=" * 60)
    print("PHASE 2: UNIVERSAL MAGMA MINING")
    print("=" * 60)

    all_results = mine_magmas(target_false, max_size=args.max_size)

    if not all_results:
        print("\nNo magma found that separates any FALSE pair!")
        sys.exit(1)

    # Top N individual magmas
    ranked = sorted(all_results.values(), key=lambda r: (-len(r["caught_ids"]), r["size"]))
    print(f"\n{'='*60}")
    print(f"TOP {min(args.top_n, len(ranked))} INDIVIDUAL MAGMAS")
    print(f"{'='*60}")
    for i, r in enumerate(ranked[:args.top_n]):
        print(f"  #{i+1}: {r['table']} (size={r['size']}) catches {len(r['caught_ids'])}/{len(target_false)}")
        print(f"       pairs: {sorted(r['caught_ids'])}")

    # Greedy set cover
    print(f"\n{'='*60}")
    print(f"GREEDY SET COVER (up to {args.greedy_n} magmas)")
    print(f"{'='*60}")
    selected = greedy_set_cover(all_results, len(target_false))
    selected = selected[:args.greedy_n]

    total_covered = sum(s["marginal_catch"] for s in selected)
    print(f"\nSet cover result: {total_covered}/{len(target_false)} pairs covered by {len(selected)} magmas")

    # === PHASE 2.4: Safety check ===
    if args.safety_check:
        print(f"\n{'='*60}")
        print("SAFETY CHECK: Testing selected magmas against TRUE pairs")
        print(f"{'='*60}")

        all_true = hard3_true[:]
        if normal_true:
            all_true.extend(normal_true)
        print(f"  Checking against {len(all_true)} TRUE pairs ({len(hard3_true)} hard3 + {len(normal_true)} normal)")

        checked = safety_check(selected, all_true)

        safe_count = sum(1 for c in checked if c["false_flag_count"] == 0)
        print(f"\n  SAFE magmas: {safe_count}/{len(checked)}")
        for i, c in enumerate(checked):
            if c["false_flag_count"] > 0:
                print(f"  WARNING: Magma #{i+1} {c['table']} false-flags {c['false_flag_count']} TRUE pairs")

    # === SUMMARY ===
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Magmas searched: 2-elem(16)" +
          (f" + 3-elem(19,683)" if args.max_size >= 3 else ""))
    print(f"  Target FALSE pairs: {len(target_false)}")
    print(f"  Best single magma: {ranked[0]['table']} → catches {len(ranked[0]['caught_ids'])}")
    print(f"  Set cover ({len(selected)} magmas): {total_covered}/{len(target_false)} covered")
    uncovered = set()
    for pair in target_false:
        uncovered.add(pair["id"])
    for s in selected:
        for pid in s["caught_ids"]:
            uncovered.discard(pid)
    if uncovered:
        print(f"  Uncovered pairs ({len(uncovered)}): {sorted(uncovered)}")
    else:
        print(f"  ALL pairs covered!")

    # Save results
    output = {
        "top_magmas": [
            {"table": r["table"], "size": r["size"], "catch_count": len(r["caught_ids"]),
             "caught_ids": sorted(r["caught_ids"])}
            for r in ranked[:20]
        ],
        "set_cover": [
            {"table": s["table"], "size": s["size"], "marginal_catch": s["marginal_catch"],
             "cumulative_coverage": s["cumulative_coverage"], "caught_ids": s["caught_ids"]}
            for s in selected
        ],
        "uncovered_ids": sorted(uncovered),
        "total_false_pairs": len(target_false),
    }
    out_path = ROOT / "results" / "hard3_magma_mining.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
