#!/usr/bin/env python3
"""Quick script to inspect results from the most recent sim_lab run."""
import json, sys, glob

# Find most recent result
files = sorted(glob.glob("results/sim_*v24c*.json"))
if not files:
    files = sorted(glob.glob("results/sim_*.json"))
if not files:
    sys.exit("No results found")

path = files[-1]
print(f"File: {path}")
with open(path) as f:
    data = json.load(f)

m = data["metadata"]
print(f"Accuracy: {m['accuracy']}")
print(f"Parse rate: {m['parse_rate']}")
print(f"TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']}")
print(f"TRUE acc: {m['true_accuracy']}, FALSE acc: {m['false_accuracy']}")
print(f"Unparsed: {m.get('unparsed', '?')}")

print("\n--- MISSES ---")
for r in data["results"]:
    if not r.get("correct"):
        print(f"\nID: {r['id']}  GT: {r['ground_truth']}  Pred: {r['predicted']}")
        print(f"  E1: {r.get('equation1','?')}")
        print(f"  E2: {r.get('equation2','?')}")
        resp = r.get("raw_response", "")
        # Show last 400 chars (verdict area)
        if len(resp) > 500:
            print(f"  ...{resp[-400:]}")
        else:
            print(f"  {resp}")
