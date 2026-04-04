"""Show model responses for the 3 FP in the warmup run."""
import json
from pathlib import Path

f = sorted(Path("results").glob("sim_*v23a_*.json"))[-1]
data = json.loads(f.read_text(encoding="utf-8"))

for r in data["results"]:
    if r["correct"]:
        continue
    print(f"=== {r['id']} gt={r['ground_truth']} pred={r['predicted']} ===")
    print(f"E1: {r['equation1']}")
    print(f"E2: {r['equation2']}")
    print(f"--- Response ---")
    print(r["raw_response"])
    print()
