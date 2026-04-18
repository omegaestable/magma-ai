"""Read FN raw responses to diagnose model failure patterns."""
import json

with open('results/v28c_hard3_r22.json', encoding='utf-8') as f:
    data = json.load(f)

fns = [r for r in data['results'] if r['ground_truth'] and not r['predicted']]
print(f'Total FNs: {len(fns)}')

for r in fns:
    print(f'\n{"="*70}')
    print(f'{r["id"]}  gt=TRUE  pred=FALSE  time={r.get("elapsed_s","?"):.1f}s')
    print(f'E1: {r["equation1"]}')
    print(f'E2: {r["equation2"]}')
    print(f'--- Raw response (last 1500 chars) ---')
    resp = r['raw_response']
    # Show last part where the verdict and reasoning happen
    print(resp[-1500:].encode('ascii', 'replace').decode())
    print('---')
