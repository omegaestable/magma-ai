"""Analyze which FULL entries would solve the most TRUE problems."""
import json
from collections import Counter

with open('cheatsheets/graph_v2.txt') as f:
    lines = f.readlines()

map_start = next(i for i,l in enumerate(lines) if l.strip() == 'MAP')
edges_start = next(i for i,l in enumerate(lines) if l.strip() == 'EDGES')
full_start = next(i for i,l in enumerate(lines) if l.strip() == 'FULL')

eq_to_class = {}
for line in lines[map_start+1:edges_start]:
    line = line.strip()
    if not line: continue
    cid, eqs = line.split(':', 1)
    for eq in eqs.split('|'):
        eq_to_class[eq.strip()] = int(cid)

# Parse FULL
full_closures = {}
for line in lines[full_start+1:]:
    line = line.strip()
    if not line or '>' not in line: continue
    parts = line.split('>', 1)
    try:
        src = int(parts[0])
    except ValueError:
        continue
    targets = set()
    for seg in parts[1].split(','):
        seg = seg.strip()
        if '-' in seg:
            a, b = seg.split('-')
            for x in range(int(a), int(b)+1):
                targets.add(x)
        else:
            try: targets.add(int(seg))
            except: pass
    full_closures[src] = targets

# Parse EDGES
edges = {}
for line in lines[edges_start+1:full_start]:
    line = line.strip()
    if not line or '>' not in line: continue
    parts = line.split('>', 1)
    try:
        src = int(parts[0])
    except ValueError:
        continue
    targets = set()
    for seg in parts[1].split(','):
        seg = seg.strip()
        try: targets.add(int(seg))
        except: pass
    edges[src] = targets

# Load hard benchmark TRUE problems
with open('data/benchmark/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

true_problems = [p for p in problems if p['answer']]

# For each TRUE problem, find source class and target class
source_counts = Counter()
true_pairs = []
for p in true_problems:
    e1 = p['equation1'].replace(' ', '')
    e2 = p['equation2'].replace(' ', '')
    c1 = eq_to_class.get(e1)
    c2 = eq_to_class.get(e2)
    true_pairs.append((c1, c2, p['id']))
    if c1: source_counts[c1] += 1

print("Most common source classes for TRUE hard problems:")
for cls, cnt in source_counts.most_common(20):
    in_full = cls in full_closures
    print(f"  Class {cls}: {cnt} TRUE problems (FULL available: {in_full})")

# For each FULL entry, count how many TRUE problems it solves
print("\nFULL entry coverage of TRUE hard problems:")
for src in sorted(full_closures.keys()):
    solved = 0
    for c1, c2, pid in true_pairs:
        if c1 == src and c2 is not None and c2 in full_closures[src]:
            solved += 1
    if solved > 0:
        entry_size = len(lines[full_start + 1 + list(full_closures.keys()).index(src)]) if src in full_closures else 0
        print(f"  FULL({src}): solves {solved} TRUE problems")

# Check how many TRUE problems can be solved by EDGES alone (direct edge check)
direct_solved = 0
for c1, c2, pid in true_pairs:
    if c1 and c2 and c1 in edges and c2 in edges[c1]:
        direct_solved += 1

print(f"\nDirect edges solve: {direct_solved}/{len(true_pairs)} TRUE problems")

# Check same-class
same_class = sum(1 for c1, c2, _ in true_pairs if c1 is not None and c1 == c2)
print(f"Same class: {same_class}/{len(true_pairs)} TRUE problems")

# Check FULL coverage
full_solved = 0
for c1, c2, _ in true_pairs:
    if c1 and c2 and c1 in full_closures and c2 in full_closures[c1]:
        full_solved += 1

print(f"FULL section solves: {full_solved}/{len(true_pairs)} TRUE problems")

# Check: c1 unmatched
unmatched = sum(1 for c1, c2, _ in true_pairs if c1 is None)
print(f"Source unmatched (singleton?): {unmatched}/{len(true_pairs)}")
