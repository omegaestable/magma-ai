"""Analyze how many benchmark problems each v4 rule solves."""
import argparse
import json
from collections import Counter

from rule_profiles import normalize, predict_implication


parser = argparse.ArgumentParser()
parser.add_argument('--profile', default='graph_v4', help='Named cheatsheet profile to analyze')
args = parser.parse_args()

for fname, label in [('data/benchmark/hard.jsonl', 'HARD'), ('data/benchmark/normal.jsonl', 'NORMAL')]:
    stats = Counter()

    with open(fname) as f:
        for line in f:
            d = json.loads(line)
            e1 = normalize(d['equation1'])
            e2 = normalize(d['equation2'])
            answer = d['answer']
            stats['total'] += 1
            
            prediction, rule = predict_implication(e1, e2, profile_name=args.profile)
            if prediction is None:
                stats['unsolved'] += 1
                if answer:
                    stats['unsolved_true'] += 1
                else:
                    stats['unsolved_false'] += 1
                continue

            stats[f'{rule}_{"true" if prediction else "false"}'] += 1

    print(f"\n{label} benchmark rule coverage:")
    solved = stats['total'] - stats['unsolved']
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"  solved: {solved}")
    print(f"  solved%: {solved / stats['total'] * 100:.1f}%")
