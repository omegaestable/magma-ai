"""Simulate the current graph_v4.txt rule set on benchmarks."""
import argparse
import json

from rule_profiles import normalize, predict_implication

def simulate(fname, label, profile_name):
    with open(fname) as f:
        problems = [json.loads(l) for l in f]
    
    correct = 0
    incorrect = 0
    unsolved = 0
    true_correct = 0
    true_incorrect = 0
    false_correct = 0
    false_incorrect = 0
    true_unsolved = 0
    false_unsolved = 0
    errors_detail = []
    rule_correct = {}
    
    for p in problems:
        e1 = normalize(p['equation1'])
        e2 = normalize(p['equation2'])
        answer = p['answer']
        
        prediction, rule = predict_implication(e1, e2, profile_name=profile_name)
        
        if prediction is None:
            unsolved += 1
            rule = 'unsolved'
            if answer: true_unsolved += 1
            else: false_unsolved += 1
        elif prediction == answer:
            correct += 1
            if answer: true_correct += 1
            else: false_correct += 1
        else:
            incorrect += 1
            if answer: true_incorrect += 1
            else: false_incorrect += 1
            errors_detail.append((p['id'], e1, e2, answer, prediction, rule))
        
        key = f"{rule}_{'T' if answer else 'F'}"
        rule_correct[key] = rule_correct.get(key, 0) + 1
    
    total = len(problems)
    print(f"\n{'='*60}")
    print(f"{label} ({total} problems):")
    print(f"  Correct: {correct} ({100*correct/total:.1f}%)")
    print(f"  Incorrect: {incorrect} ({100*incorrect/total:.1f}%)")
    print(f"  Unsolved: {unsolved} ({100*unsolved/total:.1f}%)")
    print(f"  TRUE:  correct={true_correct}, incorrect={true_incorrect}, unsolved={true_unsolved}")
    print(f"  FALSE: correct={false_correct}, incorrect={false_incorrect}, unsolved={false_unsolved}")
    
    default_false = correct + false_unsolved
    print(f"\n  If unsolved→FALSE: {default_false}/{total} ({100*default_false/total:.1f}%)")
    true_recall = true_correct / (true_correct + true_incorrect + true_unsolved) if (true_correct + true_incorrect + true_unsolved) > 0 else 0
    false_recall = (false_correct + false_unsolved) / (false_correct + false_incorrect + false_unsolved) if (false_correct + false_incorrect + false_unsolved) > 0 else 0
    print(f"  TRUE recall: {true_recall:.1%}")
    print(f"  FALSE recall: {false_recall:.1%}")
    
    print(f"\n  Rule breakdown:")
    for key in sorted(rule_correct.keys()):
        print(f"    {key:25} {rule_correct[key]}")
    
    if errors_detail:
        print(f"\n  ERRORS ({len(errors_detail)}):")
        for pid, e1, e2, ans, pred, r in errors_detail:
            print(f"    {pid}: {r} | {e1} → {e2} | ans={ans} pred={pred}")


parser = argparse.ArgumentParser()
parser.add_argument('--profile', default='graph_v4', help='Named cheatsheet profile to simulate')
args = parser.parse_args()

simulate('data/benchmark/hard.jsonl', 'HARD', args.profile)
simulate('data/benchmark/normal.jsonl', 'NORMAL', args.profile)
