#!/usr/bin/env python3
"""
witness_safety_check.py — Verify mined witnesses don't false-flag TRUE pairs.

Tests top-5 mined witnesses (from Phase 0 audit) + existing 11 against ALL
TRUE pairs across every normal and hard benchmark.  A "false flag" means
witness separates E1 from E2 when the pair is actually TRUE (implication holds).

Also reports how many normal FALSE pairs each new witness catches (bonus coverage).
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from distill import check_equation, first_failing_assignment

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "data" / "benchmark"

# Top 6 mined witnesses (greedy set-cover order from Phase 0)
MINED_WITNESSES = [
    {"name": "M1", "table": [[0, 0, 0], [2, 1, 1], [1, 2, 2]], "desc": "catches 8 hard pairs"},
    {"name": "M2", "table": [[0, 0, 0], [1, 1, 0], [2, 0, 2]], "desc": "catches 3 hard pairs"},
    {"name": "M3", "table": [[0, 1, 2], [0, 1, 2], [1, 0, 2]], "desc": "catches 5 hard pairs"},
    {"name": "M4", "table": [[1, 1, 1], [2, 2, 2], [0, 0, 0]], "desc": "LSUCC: a*b=(a+1)%3"},
    {"name": "M5", "table": [[1, 2, 0], [1, 2, 0], [1, 2, 0]], "desc": "RSUCC: a*b=(b+1)%3"},
    {"name": "M6", "table": [[0, 0, 0], [0, 0, 2], [2, 2, 2]], "desc": "catches 4 hard pairs"},
]

# Existing 11 library (for reference)
EXISTING = [
    {"name": "LP",   "table": [[0, 0], [1, 1]]},
    {"name": "RP",   "table": [[0, 1], [0, 1]]},
    {"name": "C0",   "table": [[0, 0], [0, 0]]},
    {"name": "XOR",  "table": [[0, 1], [1, 0]]},
    {"name": "Z3A",  "table": [[0, 1, 2], [1, 2, 0], [2, 0, 1]]},
    {"name": "AND",  "table": [[0, 0], [0, 1]]},
    {"name": "OR",   "table": [[0, 1], [1, 1]]},
    {"name": "XNOR", "table": [[1, 0], [0, 1]]},
    {"name": "A2",   "table": [[0, 0], [1, 0]]},
    {"name": "T3L",  "table": [[0, 0, 0], [0, 0, 0], [0, 1, 0]]},
    {"name": "T3R",  "table": [[0, 0, 0], [0, 0, 0], [0, 0, 1]]},
]

ALL_WITNESSES = EXISTING + MINED_WITNESSES


def load_benchmark(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def find_separation(eq1: str, eq2: str, witnesses: list[dict]) -> list[str]:
    """Return names of witnesses that separate E1 from E2."""
    hits = []
    for w in witnesses:
        if check_equation(eq1, w["table"]):
            if first_failing_assignment(eq2, w["table"]) is not None:
                hits.append(w["name"])
    return hits


def main():
    all_benchmarks = sorted(BENCHMARK_DIR.glob("*.jsonl"))
    
    true_flags = defaultdict(list)  # witness_name -> list of (benchmark, pair_id)
    normal_false_catches = defaultdict(int)  # witness_name -> count
    
    for bf in all_benchmarks:
        rows = load_benchmark(bf)
        is_normal = "normal" in bf.name
        
        for row in rows:
            eq1, eq2, answer = row["equation1"], row["equation2"], row.get("answer")
            pid = row["id"]
            
            if answer is True:
                # Safety check: no witness should separate TRUE pairs
                hits = find_separation(eq1, eq2, ALL_WITNESSES)
                for wname in hits:
                    true_flags[wname].append((bf.name, pid))
            
            elif answer is False and is_normal:
                # Bonus: check normal FALSE catch rate for new witnesses
                hits = find_separation(eq1, eq2, MINED_WITNESSES)
                for wname in hits:
                    normal_false_catches[wname] += 1

    # Report
    print("=" * 60)
    print("SAFETY CHECK: Witnesses that false-flag TRUE pairs")
    print("=" * 60)
    if true_flags:
        for wname in sorted(true_flags):
            pairs = true_flags[wname]
            print(f"  DANGER: {wname} false-flags {len(pairs)} TRUE pairs:")
            for bench, pid in pairs[:5]:
                print(f"    {bench}: {pid}")
            if len(pairs) > 5:
                print(f"    ...and {len(pairs) - 5} more")
    else:
        print("  ALL CLEAR: No witness false-flags any TRUE pair!")

    print()
    print("=" * 60)
    print("BONUS: Normal FALSE pairs caught by new mined witnesses")
    print("=" * 60)
    total_normal_false = 0
    for bf in all_benchmarks:
        if "normal" in bf.name:
            rows = load_benchmark(bf)
            total_normal_false += sum(1 for r in rows if r.get("answer") is False)
    
    for wname in ["M1", "M2", "M3", "M4", "M5", "M6"]:
        c = normal_false_catches.get(wname, 0)
        print(f"  {wname}: catches {c} normal FALSE pairs")
    
    print(f"\n  Total normal FALSE pairs across all benchmarks: {total_normal_false}")


if __name__ == "__main__":
    main()
