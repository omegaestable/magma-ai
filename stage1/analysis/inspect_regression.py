import json

with open('results/sim_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v26a_gpt-oss-120b_20260411_185517.json', encoding='utf-8') as f:
    v26a = json.load(f)
with open('results/sim_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_gpt-oss-120b_20260411_190415.json', encoding='utf-8') as f:
    v24j = json.load(f)

for r in v26a['results']:
    if r['id'] == 'hard3_0017':
        print('=== v26a response for hard3_0017 ===')
        print('E1:', r['equation1'])
        print('E2:', r['equation2'])
        print('GT:', r['ground_truth'], '  Pred:', r['predicted'])
        print()
        print(r['raw_response'])
        break

print()
print('=' * 60)
print()

for r in v24j['results']:
    if r['id'] == 'hard3_0017':
        print('=== v24j response for hard3_0017 ===')
        print('GT:', r['ground_truth'], '  Pred:', r['predicted'])
        print()
        print(r['raw_response'])
        break
