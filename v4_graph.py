from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def normalize(eq: str) -> str:
    return eq.replace(' ', '').replace('◇', '*')


@dataclass(frozen=True)
class GraphData:
    equations: tuple[str, ...]
    equation_index: dict[str, int]
    equation_to_class: dict[int, int]
    class_members: dict[int, tuple[int, ...]]
    class_edges: dict[int, set[int]]


@lru_cache(maxsize=1)
def load_graph_data() -> GraphData:
    equations_path = Path('data/exports/equations.txt')
    matrix_path = Path('data/exports/export_raw_implications_14_3_2026.csv')

    equations = ['']
    for line in equations_path.read_text(encoding='utf-8').splitlines():
        equations.append(line.strip().replace('◇', '*'))

    n = len(equations) - 1
    true_edges: set[tuple[int, int]] = set()
    with matrix_path.open(encoding='utf-8') as handle:
        for row, line in enumerate(handle, 1):
            if row > n:
                break
            for col, value in enumerate(line.strip().rstrip(',').split(','), 1):
                if value.strip() in ('3', '4'):
                    true_edges.add((row, col))

    parent = list(range(n + 1))

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for src, dst in true_edges:
        if src != dst and (dst, src) in true_edges:
            union(src, dst)

    raw_classes: dict[int, list[int]] = defaultdict(list)
    for idx in range(1, n + 1):
        raw_classes[find(idx)].append(idx)

    class_members = {
        min(members): tuple(sorted(members))
        for members in raw_classes.values()
    }
    equation_to_class = {
        member: rep
        for rep, members in class_members.items()
        for member in members
    }

    class_edges: dict[int, set[int]] = defaultdict(set)
    for src, dst in true_edges:
        src_class = equation_to_class[src]
        dst_class = equation_to_class[dst]
        if src_class != dst_class:
            class_edges[src_class].add(dst_class)

    equation_index = {
        normalize(eq): idx
        for idx, eq in enumerate(equations)
        if idx
    }

    return GraphData(
        equations=tuple(equations),
        equation_index=equation_index,
        equation_to_class=equation_to_class,
        class_members=class_members,
        class_edges=dict(class_edges),
    )


def equation_class(eq: str) -> int | None:
    graph = load_graph_data()
    eq_idx = graph.equation_index.get(normalize(eq))
    if eq_idx is None:
        return None
    return graph.equation_to_class[eq_idx]