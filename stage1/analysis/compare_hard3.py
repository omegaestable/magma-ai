import json

with open('results/sim_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v26a_gpt-oss-120b_20260411_185517.json', encoding='utf-8') as f:
    v26a = json.load(f)
with open('results/sim_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_gpt-oss-120b_20260411_190415.json', encoding='utf-8') as f:
    v24j = json.load(f)

flips_for = []
flips_against = []

print(f"{'Pos':>3} {'ID':12} {'GT':>2}  v24j v26a  Delta")
print("-" * 48)
for i, (a, b) in enumerate(zip(v24j['results'], v26a['results'])):
    assert a['id'] == b['id']
    gt = 'T' if a['ground_truth'] else 'F'
    c24 = 'Y' if a['correct'] else 'N'
    c26 = 'Y' if b['correct'] else 'N'
    delta = ''
    if a['correct'] != b['correct']:
        if b['correct']:
            delta = '+v26a'
            flips_for.append(a['id'])
        else:
            delta = '-v26a'
            flips_against.append(a['id'])
    print(f"{i+1:3d} {a['id']:12s} {gt:>2}   {c24}    {c26}   {delta}")

print()
print(f"v24j: {v24j['summary']['correct']}/{v24j['summary']['total']} = {v24j['summary']['accuracy']:.1%}")
print(f"v26a: {v26a['summary']['correct']}/{v26a['summary']['total']} = {v26a['summary']['accuracy']:.1%}")
print(f"\nFlips FOR v26a ({len(flips_for)}): {flips_for}")
print(f"Flips AGAINST v26a ({len(flips_against)}): {flips_against}")
print(f"Net delta: {len(flips_for) - len(flips_against):+d} problems ({(len(flips_for) - len(flips_against)) * 2.5:+.1f}pp)")
