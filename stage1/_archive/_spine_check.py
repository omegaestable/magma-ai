#!/usr/bin/env python3
"""One-shot: identify which benchmark pairs spine separates."""
import json
from spine_classify import check_implication

benchmarks = [
    "data/benchmark/normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl",
    "data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl",
]

for bench in benchmarks:
    short = bench.split("/")[-1]
    print(f"\n=== {short} ===")
    with open(bench, encoding="utf-8") as f:
        problems = [json.loads(line) for line in f if line.strip()]
    for p in problems:
        eq1 = p["equation1"].replace("\u25c7", "*")
        eq2 = p["equation2"].replace("\u25c7", "*")
        r = check_implication(eq1, eq2)
        if r["separated"]:
            gt = "TRUE" if p["answer"] else "FALSE"
            pid = p["id"]
            print(f"  {pid}  gt={gt}  E1:{r['eq1_spine']} d={r['eq1_depth']}  E2:{r['eq2_spine']} d={r['eq2_depth']}")
            print(f"    Reason: {r['reason']}")
            print(f"    E1: {eq1}")
            print(f"    E2: {eq2}")
