"""Find dense-graph class IDs for benchmark problems."""
import json

from v4_graph import equation_class, normalize


with open('data/benchmark/hard.jsonl', encoding='utf-8') as handle:
    problems = [json.loads(line) for line in handle]

true_problems = [p for p in problems if p['answer']]
false_problems = [p for p in problems if not p['answer']]

print("=== TRUE problems (first 20) ===")
for p in true_problems[:20]:
    e1 = normalize(p['equation1'])
    e2 = normalize(p['equation2'])
    c1 = equation_class(e1)
    c2 = equation_class(e2)
    print(f"  {p['id']}: [{c1}]->[{c2}] {e1} -> {e2}")

print("\n=== FALSE problems (first 20) ===")
for p in false_problems[:20]:
    e1 = normalize(p['equation1'])
    e2 = normalize(p['equation2'])
    c1 = equation_class(e1)
    c2 = equation_class(e2)
    print(f"  {p['id']}: [{c1}]->[{c2}] {e1} -> {e2}")
