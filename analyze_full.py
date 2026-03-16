"""Analyze dense-graph class usage for TRUE hard problems."""
import json
from collections import Counter

from v4_graph import load_graph_data, normalize


graph = load_graph_data()

with open('data/benchmark/hard.jsonl', encoding='utf-8') as handle:
    problems = [json.loads(line) for line in handle]

true_problems = [problem for problem in problems if problem['answer']]

source_counts = Counter()
pair_counts = Counter()
for problem in true_problems:
    source_idx = graph.equation_index[normalize(problem['equation1'])]
    target_idx = graph.equation_index[normalize(problem['equation2'])]
    source_class = graph.equation_to_class[source_idx]
    target_class = graph.equation_to_class[target_idx]
    source_counts[source_class] += 1
    pair_counts[(source_class, target_class)] += 1

print('Most common TRUE hard source classes:')
for cls, cnt in source_counts.most_common(20):
    print(f'  C{cls}: {cnt} | {graph.equations[cls]}')

print('\nMost common TRUE hard source->target pairs:')
for (source_class, target_class), cnt in pair_counts.most_common(20):
    print(
        f'  C{source_class} -> C{target_class}: {cnt} '
        f'| {graph.equations[source_class]} => {graph.equations[target_class]}'
    )

direct_edge_hits = sum(
    1
    for source_class, target_class in pair_counts
    if target_class in graph.class_edges.get(source_class, set())
)
print(f'\nDistinct direct-edge source->target pairs present in hard TRUE set: {direct_edge_hits}')
