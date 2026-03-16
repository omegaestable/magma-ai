import json
with open('results/sim_qwen2.5_3b_graph_v4_20260315_231428.json') as f:
    data = json.load(f)
for r in data['results']:
    if r['id'] in ('hard_0004', 'hard_0006', 'hard_0010'):
        print(f"=== {r['id']} ===")
        print(f"E1: {r['equation1']}")
        print(f"E2: {r['equation2']}")
        print(f"Answer: {r['ground_truth']}, Predicted: {r['predicted']}")
        resp = r['raw_response'][:600]
        print(f"Response:\n{resp}")
        print()
