import json, glob

f = sorted(glob.glob('results/sim_*v24e*.json'))[-1]
data = json.load(open(f))
misses = [r for r in data['results'] if not r['correct'] or not r['parsed_ok']]
for m in misses:
    gt = 'T' if m['ground_truth'] else 'F'
    pred = m['predicted']
    tag = 'UNPARSED' if not m['parsed_ok'] else ('FN' if gt == 'T' else 'FP')
    pid = m['id']
    print(f"=== {pid} gt={gt} pred={pred} -> {tag} ===")
    print(f"E1: {m['equation1']}")
    print(f"E2: {m['equation2']}")
    print("--- RESPONSE ---")
    print(m['raw_response'][:1200])
    print("---\n")
