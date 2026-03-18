"""
Build a larger graph-backed cheatsheet that packs most of the implication graph
into a single prompt-friendly artifact.

The output is intentionally hybrid:
- a small front section with math / invariant guidance;
- a complete map from every non-singleton equation to its implication class;
- compressed reduced edges for all classes;
- direct full reachability for the most benchmark-relevant source classes.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path


EQUATIONS_PATH = Path("data/exports/equations.txt")
MATRIX_PATH = Path("data/exports/export_raw_implications_14_3_2026.csv")
DEFAULT_OUTPUT = Path("cheatsheets/graph_ultimate_100k.txt")
DEFAULT_MAX_BYTES = 102_400

# These are the source classes that mattered most in the repo's public mining.
FULL_CLASSES = [4, 5, 13, 24, 41, 887]


def normalize(eq: str) -> str:
    return eq.replace(" ", "").replace("\u25c7", "*")


def load_equations(path: Path) -> list[str]:
    equations = [""]
    for line in path.read_text(encoding="utf-8").splitlines():
        equations.append(normalize(line.strip()))
    return equations


def load_true_edges(path: Path, n: int) -> set[tuple[int, int]]:
    true_edges: set[tuple[int, int]] = set()
    with path.open(encoding="utf-8") as handle:
        for row, line in enumerate(handle, 1):
            if row > n:
                break
            for col, value in enumerate(line.strip().rstrip(",").split(","), 1):
                if value.strip() in ("3", "4"):
                    true_edges.add((row, col))
            if row % 1000 == 0:
                print(f"  row {row}/{n}", file=sys.stderr)
    return true_edges


def find_classes(true_edges: set[tuple[int, int]], n: int) -> dict[int, list[int]]:
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

    raw: dict[int, list[int]] = defaultdict(list)
    for idx in range(1, n + 1):
        raw[find(idx)].append(idx)
    return {min(members): sorted(members) for members in raw.values()}


def compress_ints(nums: set[int] | list[int]) -> str:
    if not nums:
        return ""
    seq = sorted(nums)
    ranges: list[str] = []
    start = end = seq[0]
    for num in seq[1:]:
        if num == end + 1:
            end = num
            continue
        ranges.append(render_range(start, end))
        start = end = num
    ranges.append(render_range(start, end))
    return ",".join(ranges)


def render_range(start: int, end: int) -> str:
    if start == end:
        return str(start)
    if end == start + 1:
        return f"{start},{end}"
    return f"{start}-{end}"


def transitive_reduction(adj: dict[int, set[int]], nodes: list[int]) -> dict[int, set[int]]:
    reduced: dict[int, set[int]] = defaultdict(set)
    for src in nodes:
        if src not in adj:
            continue
        neighbors = adj[src]
        for dst in neighbors:
            visited = {src}
            queue = [mid for mid in neighbors if mid != dst]
            visited.update(queue)
            found = False
            while queue and not found:
                cur = queue.pop(0)
                if cur == dst:
                    found = True
                    break
                for nxt in adj.get(cur, set()):
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
            if not found:
                reduced[src].add(dst)
    return dict(reduced)


def is_singleton_forcing(eq: str) -> bool:
    lhs, rhs = eq.split("=", 1)
    if len(lhs) == 1 and lhs.isalpha() and lhs not in rhs:
        return True
    if len(rhs) == 1 and rhs.isalpha() and rhs not in lhs:
        return True
    return False


def build_cheatsheet() -> str:
    equations = load_equations(EQUATIONS_PATH)
    n = len(equations) - 1
    print(f"loaded {n} equations", file=sys.stderr)

    print("loading implication matrix...", file=sys.stderr)
    true_edges = load_true_edges(MATRIX_PATH, n)
    print(f"true edges: {len(true_edges)}", file=sys.stderr)

    print("building equivalence classes...", file=sys.stderr)
    classes = find_classes(true_edges, n)
    reps = sorted(classes)
    eq_to_rep = {
        member: rep for rep, members in classes.items() for member in members
    }

    inter: dict[int, set[int]] = defaultdict(set)
    for src, dst in true_edges:
        src_rep = eq_to_rep[src]
        dst_rep = eq_to_rep[dst]
        if src_rep != dst_rep:
            inter[src_rep].add(dst_rep)

    trivial_class = eq_to_rep[1]
    singleton_class = eq_to_rep[2]

    simplified: dict[int, set[int]] = defaultdict(set)
    for src, targets in inter.items():
        if src == singleton_class:
            continue
        for dst in targets:
            if dst == trivial_class:
                continue
            simplified[src].add(dst)

    print("computing transitive reduction...", file=sys.stderr)
    reduced = transitive_reduction(simplified, reps)
    print(
        f"reduced edges: {sum(len(v) for v in reduced.values())}",
        file=sys.stderr,
    )

    lines: list[str] = []
    lines.append("ULTIMATE MAGMA GRAPH ORACLE")
    lines.append("Use exact graph lookup first; use invariants when lookup is hard.")
    lines.append("SAME-LAW up to consistent renaming or swapping sides => TRUE.")
    lines.append("TRIVIAL target x=x => TRUE.")
    lines.append("SINGLETON: bare variable absent from the other side => class 2 => TRUE.")
    lines.append("DUALITY: reverse every product on both equations; implication is preserved.")
    lines.append("MATCHING INVARIANTS from the paper:")
    lines.append("LP a*b=a preserves leftmost variable; RP a*b=b preserves rightmost variable.")
    lines.append("XOR preserves variable parity mod 2; CONSTANT a*b=0 preserves product-vs-bare pattern.")
    lines.append("Lookup protocol:")
    lines.append("1. Remove spaces.")
    lines.append("2. Find E1 and E2 in [M].")
    lines.append("3. If same class => TRUE.")
    lines.append("4. If E1 class is in [F], use direct full reachability there.")
    lines.append("5. Else follow [R] transitively.")
    lines.append("6. If no path, answer FALSE unless a quick invariant already refutes first.")
    lines.append("Special classes: 1 is trivial x=x; 2 is singleton x=y and implies everything.")
    lines.append("[M]")
    lines.append("Format: class=eq|eq|eq ; class 2 omitted because singleton is handled by rule.")

    for rep in reps:
        if rep == singleton_class:
            continue
        members = "|".join(equations[idx] for idx in classes[rep])
        lines.append(f"{rep}={members}")

    lines.append("[R]")
    lines.append("Reduced implication edges. Format: a>b,c,d or a>m-n.")
    lines.append("All classes imply 1. Class 2 implies all classes.")
    for src in sorted(reduced):
        targets = reduced[src]
        if targets:
            lines.append(f"{src}>{compress_ints(targets)}")

    lines.append("[F]")
    lines.append("Full reachability for the most important source classes.")
    for src in FULL_CLASSES:
        targets = simplified.get(src, set())
        if targets:
            lines.append(f"{src}>>{compress_ints(targets)}")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args()

    cheatsheet = build_cheatsheet()
    output = Path(args.output)
    payload = cheatsheet.encode("utf-8")
    output.write_bytes(payload)
    size = len(payload)

    print(f"wrote {output} ({size:,} bytes)", file=sys.stderr)
    if size > args.max_bytes:
        print(
            f"WARNING: exceeds budget by {size - args.max_bytes:,} bytes",
            file=sys.stderr,
        )
    else:
        print(
            f"within budget: {args.max_bytes - size:,} bytes spare",
            file=sys.stderr,
        )

    singleton_count = sum(
        1 for eq in load_equations(EQUATIONS_PATH)[1:] if is_singleton_forcing(eq)
    )
    print(f"singleton-forcing equations by syntax: {singleton_count}", file=sys.stderr)


if __name__ == "__main__":
    main()
