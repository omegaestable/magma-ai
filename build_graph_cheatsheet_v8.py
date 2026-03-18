"""
Build a compact graph-backed cheatsheet tuned for cross-model transfer.

Design goals:
- start with short imperative rules rather than prose;
- keep only graph-backed exact source lanes for the highest-yield classes;
- avoid the full class map that made smaller models drift off prompt;
- stay well under a 30 KB budget.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from v4_graph import load_graph_data


DEFAULT_OUTPUT = Path("cheatsheets/graph_v8.txt")
DEFAULT_MAX_BYTES = 30 * 1024

LEFT_CLASS = 4
RIGHT_CLASS = 5
BRIDGE_RIGHT_CLASS = 13
BRIDGE_LEFT_CLASS = 24
CONST_CLASS = 41
C887_CLASS = 887

BRIDGE_RIGHT_TARGETS = [2056, 463, 3349]
BRIDGE_LEFT_TARGETS = [3470]
C887_TARGETS = [1229]


def eq_list(graph, reps: list[int] | tuple[int, ...] | set[int]) -> list[str]:
    items: list[str] = []
    for rep in reps:
        for idx in graph.class_members[rep]:
            items.append(graph.equations[idx].replace(" ", ""))
    return items


def wrap_items(items: list[str], *, prefix: str = "  ", width: int = 100) -> list[str]:
    lines: list[str] = []
    current = prefix
    for item in items:
        piece = item if current == prefix else "|" + item
        if len(current) + len(piece) > width and current != prefix:
            lines.append(current)
            current = prefix + item
        else:
            current += piece
    if current != prefix:
        lines.append(current)
    return lines


def emit_exact_source_rule(
    lines: list[str],
    *,
    label: str,
    sources: list[str],
    target_rule: str,
    false_rule: str | None = None,
) -> None:
    lines.append(f"IF E1 is one of these exact {label} sources, up to one consistent renaming:")
    lines.extend(wrap_items(sources))
    lines.append(f"THEN {target_rule}")
    if false_rule:
        lines.append(f"THEN {false_rule}")
    lines.append("STOP.")
    lines.append("")


def emit_exact_bridge_rule(
    lines: list[str],
    *,
    label: str,
    sources: list[str],
    targets: list[str],
) -> None:
    lines.append(f"IF E1 is one of these exact {label} sources, up to one consistent renaming:")
    lines.extend(wrap_items(sources))
    lines.append(f"AND E2 is one of these exact {label} safe targets, up to one consistent renaming:")
    lines.extend(wrap_items(targets))
    lines.append("THEN TRUE.")
    lines.append("STOP.")
    lines.append("")


def build_cheatsheet() -> str:
    graph = load_graph_data()

    c4_sources = eq_list(graph, [LEFT_CLASS])
    c5_sources = eq_list(graph, [RIGHT_CLASS])
    c13_sources = eq_list(graph, [BRIDGE_RIGHT_CLASS])
    c13_targets = eq_list(graph, BRIDGE_RIGHT_TARGETS)
    c24_sources = eq_list(graph, [BRIDGE_LEFT_CLASS])
    c24_targets = eq_list(graph, BRIDGE_LEFT_TARGETS)
    c41_sources = eq_list(graph, [CONST_CLASS])
    c887_sources = eq_list(graph, [C887_CLASS])
    c887_targets = eq_list(graph, C887_TARGETS)

    lines: list[str] = []
    lines.append("IF a listed equation matches only by vague similarity, star count, reassociation, or deleting symbols")
    lines.append("THEN treat it as NO MATCH.")
    lines.append("STOP.")
    lines.append("")
    lines.append("IF your only reason is balanced vs unbalanced, ignore that reason and continue")
    lines.append("THEN NO MATCH.")
    lines.append("STOP.")
    lines.append("")
    lines.append("IF E1 and E2 are the same law up to one consistent renaming")
    lines.append("THEN TRUE.")
    lines.append("STOP.")
    lines.append("")
    lines.append("IF one side of E1 is a bare variable v and v is absent from the other side")
    lines.append("THEN TRUE.")
    lines.append("STOP.")
    lines.append("")
    lines.append("IF E2 is x = x")
    lines.append("THEN TRUE.")
    lines.append("STOP.")
    lines.append("")

    emit_exact_source_rule(
        lines,
        label="C41",
        sources=c41_sources,
        target_rule="TRUE iff both sides of E2 contain *.",
        false_rule="FALSE otherwise.",
    )
    emit_exact_source_rule(
        lines,
        label="C4",
        sources=c4_sources,
        target_rule="TRUE iff the leftmost variable on the two sides of E2 is the same.",
        false_rule="FALSE otherwise.",
    )
    emit_exact_source_rule(
        lines,
        label="C5",
        sources=c5_sources,
        target_rule="TRUE iff the rightmost variable on the two sides of E2 is the same.",
        false_rule="FALSE otherwise.",
    )
    emit_exact_bridge_rule(
        lines,
        label="C13",
        sources=c13_sources,
        targets=c13_targets,
    )
    emit_exact_bridge_rule(
        lines,
        label="C24",
        sources=c24_sources,
        targets=c24_targets,
    )
    emit_exact_bridge_rule(
        lines,
        label="C887",
        sources=c887_sources,
        targets=c887_targets,
    )

    lines.append("IF no earlier rule fired")
    lines.append("THEN FALSE.")
    lines.append("STOP.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args()

    payload = build_cheatsheet().encode("utf-8")
    output = Path(args.output)
    output.write_bytes(payload)
    size = len(payload)

    print(f"wrote {output} ({size:,} bytes)")
    if size > args.max_bytes:
        print(f"WARNING: exceeds budget by {size - args.max_bytes:,} bytes")
    else:
        print(f"within budget: {args.max_bytes - size:,} bytes spare")


if __name__ == "__main__":
    main()
