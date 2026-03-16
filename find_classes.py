"""Find class IDs for benchmark problems."""
import json

with open('cheatsheets/graph_v2.txt') as f:
    lines = f.readlines()

map_start = next(i for i,l in enumerate(lines) if l.strip() == 'MAP')
edges_start = next(i for i,l in enumerate(lines) if l.strip() == 'EDGES')

eq_to_class = {}
for line in lines[map_start+1:edges_start]:
    line = line.strip()
    if not line: continue
    cid, eqs = line.split(':', 1)
    for eq in eqs.split('|'):
        eq_to_class[eq.strip()] = int(cid)

with open('data/benchmark/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

true_problems = [p for p in problems if p['answer']]
false_problems = [p for p in problems if not p['answer']]

print("=== TRUE problems (first 20) ===")
for p in true_problems[:20]:
    e1 = p['equation1'].replace(' ', '')
    e2 = p['equation2'].replace(' ', '')
    c1 = eq_to_class.get(e1, 'X')
    c2 = eq_to_class.get(e2, 'X')
    print(f"  {p['id']}: [{c1}]->[{c2}] {e1} -> {e2}")

print("\n=== FALSE problems (first 20) ===")
for p in false_problems[:20]:
    e1 = p['equation1'].replace(' ', '')
    e2 = p['equation2'].replace(' ', '')
    c1 = eq_to_class.get(e1, 'X')
    c2 = eq_to_class.get(e2, 'X')
    print(f"  {p['id']}: [{c1}]->[{c2}] {e1} -> {e2}")
