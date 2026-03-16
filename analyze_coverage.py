"""Analyze TRUE problem coverage by source class across both benchmarks."""
import json
from collections import Counter

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

import re

def normalize(eq):
    return eq.replace(' ', '')

def is_singleton_forcing(eq):
    parts = eq.split('=', 1)
    lhs, rhs = parts[0], parts[1]
    lv = set(re.findall(r'[a-z]', lhs))
    rv = set(re.findall(r'[a-z]', rhs))
    bl = len(lhs) == 1 and lhs.isalpha()
    br = len(rhs) == 1 and rhs.isalpha()
    if bl and lhs not in rv: return True
    if br and rhs not in lv: return True
    return False

for fname, label in [('data/benchmark/hard.jsonl', 'HARD'), ('data/benchmark/normal.jsonl', 'NORMAL')]:
    with open(fname) as f:
        problems = [json.loads(l) for l in f]
    
    true_problems = [p for p in problems if p['answer']]
    
    # Categorize TRUE problems by source identification method
    singleton_solved = 0
    class4_solved = 0
    class5_solved = 0
    class41_solved = 0
    other_class_solved = Counter()
    unidentified = 0
    
    for p in true_problems:
        e1 = normalize(p['equation1'])
        e2 = normalize(p['equation2'])
        
        # Check singleton
        if is_singleton_forcing(e1):
            singleton_solved += 1
            continue
        
        c1 = eq_to_class.get(e1)
        
        if c1 == 4:
            class4_solved += 1
        elif c1 == 5:
            class5_solved += 1
        elif c1 == 41:
            class41_solved += 1
        elif c1 is None:
            # Not in MAP - might be singleton-forcing (already checked) or unknown
            unidentified += 1
        else:
            other_class_solved[c1] += 1
    
    print(f"\n{label} TRUE problems by source:")
    print(f"  Total TRUE: {len(true_problems)}")
    print(f"  Singleton: {singleton_solved}")
    print(f"  Class 4: {class4_solved}")
    print(f"  Class 5: {class5_solved}")
    print(f"  Class 41: {class41_solved}")
    print(f"  Other classes: {sum(other_class_solved.values())}")
    if other_class_solved:
        print(f"    Top 10: {other_class_solved.most_common(10)}")
    print(f"  Unidentified: {unidentified}")
    total_easy = singleton_solved + class4_solved + class5_solved + class41_solved
    print(f"  Covered by rules: {total_easy}/{len(true_problems)} ({100*total_easy/len(true_problems):.1f}%)")
