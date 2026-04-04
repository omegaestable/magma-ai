"""Show unparsed responses from the noisy rotation0002 normal run."""
import json
from pathlib import Path

f = Path("results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v23_20260403_150140.json")
data = json.loads(f.read_text(encoding="utf-8"))

unparsed = [r for r in data["results"] if r["predicted"] is None]
print(f"=== UNPARSED: {len(unparsed)} ===\n")
for r in unparsed:
    print(f"--- {r['id']} gt={r['ground_truth']} ---")
    resp = r["raw_response"]
    # Show last 600 chars (where verdict should be)
    print(f"  Length: {len(resp)} chars")
    print(f"  Last 600 chars:")
    print(resp[-600:])
    print()
