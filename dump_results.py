import json, sys

data = json.load(open('results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced10_true5_false5_seed0_v21c_structural_20260330_220404.json'))
for i, r in enumerate(data['results']):
    mark = 'CORRECT' if r['ground_truth'] == r['predicted'] else 'WRONG'
    gt = r['ground_truth']
    pred = r['predicted']
    eid = r['id']
    e1 = r['equation1']
    e2 = r['equation2']
    resp = r['raw_response']
    print(f"=== [{i+1}] {eid} | GT={gt} Pred={pred} {mark} ===")
    print(f"E1: {e1}")
    print(f"E2: {e2}")
    print(resp)
    print("---END---")
    print()
