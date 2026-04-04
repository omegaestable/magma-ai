"""Show raw model responses for all normal FP in the clean rotation0002 run."""
import json
from pathlib import Path

# Clean run (130838) — the one with 93.3% and 0 unparsed
f = Path("results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v23_20260403_130838.json")
data = json.loads(f.read_text(encoding="utf-8"))

fp_cases = [r for r in data["results"] if not r["correct"] and r["ground_truth"] is False and r["predicted"] is True]
fn_cases = [r for r in data["results"] if not r["correct"] and r["ground_truth"] is True and r["predicted"] is False]

print(f"=== FP (said TRUE, should be FALSE): {len(fp_cases)} ===\n")
for r in fp_cases:
    print(f"--- {r['id']} ---")
    print(f"E1: {r['equation1']}")
    print(f"E2: {r['equation2']}")
    print(f"Model response (first 1500 chars):")
    print(r["raw_response"][:1500])
    print("..." if len(r["raw_response"]) > 1500 else "")
    print()

print(f"=== FN (said FALSE, should be TRUE): {len(fn_cases)} ===\n")
for r in fn_cases:
    print(f"--- {r['id']} ---")
    print(f"E1: {r['equation1']}")
    print(f"E2: {r['equation2']}")
    print(f"Model response (first 1500 chars):")
    print(r["raw_response"][:1500])
    print()
