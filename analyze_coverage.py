"""Analyze TRUE benchmark coverage in the v4-only world."""
import argparse
import json
from collections import Counter

from v4_graph import equation_class
from rule_profiles import family_name, normalize


parser = argparse.ArgumentParser()
parser.add_argument('--profile', default='graph_v4', help='Named cheatsheet profile to analyze')
args = parser.parse_args()

for fname, label in [('data/benchmark/hard.jsonl', 'HARD'), ('data/benchmark/normal.jsonl', 'NORMAL')]:
    with open(fname) as f:
        problems = [json.loads(l) for l in f]
    
    true_problems = [p for p in problems if p['answer']]
    
    # Categorize TRUE problems by source identification method
    family_counts = Counter()
    other_class_solved = Counter()
    unidentified = 0
    
    for p in true_problems:
        e1 = normalize(p['equation1'])
        e2 = normalize(p['equation2'])
        
        family = family_name(e1, profile_name=args.profile)
        if family != 'other':
            family_counts[family] += 1
            continue

        c1 = equation_class(e1)
        if c1 is None:
            unidentified += 1
        else:
            other_class_solved[c1] += 1
    
    print(f"\n{label} TRUE problems by source:")
    print(f"  Total TRUE: {len(true_problems)}")
    for family in ('singleton', 'left_family', 'right_family', 'const_family', 'square_family'):
        print(f"  {family}: {family_counts[family]}")
    print(f"  Other classes: {sum(other_class_solved.values())}")
    if other_class_solved:
        print(f"    Top 10: {other_class_solved.most_common(10)}")
    print(f"  Unidentified: {unidentified}")
    total_easy = sum(family_counts.values())
    print(f"  Covered by rules: {total_easy}/{len(true_problems)} ({100*total_easy/len(true_problems):.1f}%)")
