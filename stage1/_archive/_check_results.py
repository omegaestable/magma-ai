import json
d = json.loads(open('results/v26h_normal_60.json', encoding='utf-8').read())
s = d.get('summary', d)
total = len(d['results'])
correct = sum(1 for r in d['results'] if r['correct'])
print(f"Correct: {correct}/{total} = {correct/total:.1%}")
for r in d['results']:
    if not r['correct']:
        print(f"  MISS: {r['id']} pred={r['predicted']} gt={r['ground_truth']}")
