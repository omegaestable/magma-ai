import json

import glob
files = sorted(glob.glob('results/sim_*v24d*.json'))
path = files[-1] if files else 'NOT_FOUND'
print(f"Reading: {path}\n")
with open(path) as f:
    data = json.load(f)

print("=== SUMMARY ===")
s = data['summary']
print(f"Accuracy: {s['accuracy']:.1%}  ({s['correct']}/{s['total']})")
print(f"TRUE acc: {s['true_accuracy']:.1%}  (TP={s['tp']} FN={s['fn']})")
print(f"FALSE acc: {s['false_accuracy']:.1%}  (TN={s['tn']} FP={s['fp']})")
print(f"Parse: {s['parse_success_rate']:.1%}  unparsed={s['unparsed']}")
print()

misses = [r for r in data['results'] if not r['correct'] or not r['parsed_ok']]
for m in misses:
    gt = 'T' if m['ground_truth'] else 'F'
    pred = m['predicted']
    tag = 'UNPARSED' if not m['parsed_ok'] else ('FN' if m['ground_truth'] and not pred else 'FP')
    print(f"=== {m['id']} | gt={gt} pred={pred} → {tag} ===")
    print(f"E1: {m['equation1']}")
    print(f"E2: {m['equation2']}")
    print(f"--- MODEL RESPONSE ---")
    print(m['raw_response'][:1500])
    print("---\n")
