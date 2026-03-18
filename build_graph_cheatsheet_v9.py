"""
Build a non-collapsing, paper-informed cheatsheet.

This version avoids the v8 failure mode where the model learned
"no earlier rule fired => FALSE". The sheet instead does three things:

1. front-loads concrete witness magmas for safe FALSE calls;
2. compresses large TRUE families into prototype-plus-signature heuristics;
3. explicitly states that lack of a match is not itself evidence for FALSE.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

from v4_graph import load_graph_data


DEFAULT_OUTPUT = Path("cheatsheets/graph_v9.txt")
DEFAULT_MAX_BYTES = 10_240

LEFT_CLASS = 4
RIGHT_CLASS = 5
BRIDGE_RIGHT_CLASS = 13
BRIDGE_LEFT_CLASS = 24
CONST_CLASS = 41
C887_CLASS = 887

BRIDGE_RIGHT_TARGETS = [2056, 463, 3349]
BRIDGE_LEFT_TARGETS = [3470]
C887_TARGETS = [1229]

EXACT_TRUE_PAIRS = [
    ("x=((y*y)*z)*x", "x=y*(y*(z*(w*x)))"),
    ("x=((y*z)*w)*x", "x=y*((z*(w*u))*x)"),
    ("x=x*(y*(z*y))", "x=(x*(x*(x*y)))*x"),
    ("x=x*((y*z)*(w*u))", "x=(x*(x*(y*x)))*x"),
    ("x=x*((y*(z*w))*w)", "x*y=(x*(z*w))*u"),
    ("x=x*(y*(x*z))", "x=((x*y)*(z*w))*u"),
    ("x=x*(y*(z*(x*y)))", "x=x*(((y*x)*z)*w)"),
    ("x=((y*z)*z)*x", "x=x*((y*(y*x))*x)"),
    ("x*y=z*(w*(u*u))", "x*(y*y)=(z*w)*z"),
    ("x*y=(z*w)*(w*z)", "(x*x)*y=(y*x)*x"),
    ("x*y=y*(z*(y*z))", "x*y=y*((y*z)*z)"),
    ("x=(y*(x*z))*(y*x)", "x=(y*y)*((y*z)*x)"),
    ("x*y=(z*z)*(w*x)", "x*x=(x*(y*x))*z"),
    ("x*y=(z*w)*(z*x)", "x*y=z*(z*(x*x))"),
    ("x*y=(y*y)*z", "x*(y*z)=(x*x)*y"),
    ("x=((y*(z*y))*w)*x", "x=(x*(y*(z*z)))*x"),
    ("x*y=(y*y)*(z*w)", "x*y=((z*w)*x)*w"),
    ("x*y=((z*y)*y)*w", "x*y=(y*x)*z"),
    ("x=((y*(x*y))*z)*w", "x=(y*(x*z))*(y*w)"),
    ("x=y*(z*((w*u)*u))", "x=((y*z)*x)*(x*w)"),
    ("x=y*((x*z)*(w*u))", "x=(((x*x)*x)*x)*x"),
    ("x=(y*z)*(z*(w*z))", "x*y=z*(w*(y*z))"),
    ("x=y*(((z*z)*w)*y)", "x*y=(y*z)*(x*z)"),
    ("x=y*(y*((z*x)*y))", "x=((y*y)*x)*(z*x)"),
    ("x=(y*y)*((y*z)*w)", "x=((y*z)*(x*y))*x"),
    ("x=y*((x*(x*y))*z)", "x=y*(z*((x*y)*w))"),
]

EXACT_FALSE_PAIRS = [
    ("x=(y*x)*(x*(z*z))", "x=y*((y*x)*(z*y))"),
    ("x=(y*(x*(y*x)))*y", "x*(x*y)=z*(y*x)"),
]


def normalize(eq: str) -> str:
    return eq.replace(" ", "")


def parse(eq: str) -> tuple[str, str]:
    return normalize(eq).split("=", 1)


def var_multiset(term: str) -> tuple[int, ...]:
    counts = Counter(re.findall(r"[a-z]", term))
    return tuple(sorted(counts.values()))


def leftmost_var(term: str) -> str:
    return next(char for char in term if char.isalpha())


def rightmost_var(term: str) -> str:
    return next(char for char in reversed(term) if char.isalpha())


def source_signature(eq: str) -> tuple[bool, int, tuple[int, ...], bool | None, bool | None]:
    lhs, rhs = parse(eq)
    lhs_bare = len(lhs) == 1 and lhs.isalpha()
    anchor = lhs if lhs_bare else None
    return (
        lhs_bare,
        rhs.count("*"),
        var_multiset(rhs),
        leftmost_var(rhs) == anchor if anchor else None,
        rightmost_var(rhs) == anchor if anchor else None,
    )


def target_signature(eq: str) -> tuple[int, int, tuple[int, ...], tuple[int, ...], bool, bool, bool, bool]:
    lhs, rhs = parse(eq)
    anchor = leftmost_var(lhs)
    return (
        lhs.count("*"),
        rhs.count("*"),
        var_multiset(lhs),
        var_multiset(rhs),
        leftmost_var(lhs) == leftmost_var(rhs),
        rightmost_var(lhs) == rightmost_var(rhs),
        leftmost_var(rhs) == anchor,
        rightmost_var(rhs) == anchor,
    )


def bucket_prototypes(equations: list[str], signature_fn) -> list[str]:
    buckets: dict[tuple[object, ...], list[str]] = defaultdict(list)
    for eq in equations:
        buckets[signature_fn(eq)].append(eq)
    return [sorted(items)[0] for _, items in sorted(buckets.items(), key=lambda item: item[0])]


def shortest_unique_equations(equations: list[str], limit: int) -> list[str]:
    unique = sorted({normalize(eq) for eq in equations}, key=lambda item: (len(item), item))
    return unique[:limit]


def outgoing_examples(graph, source_rep: int, limit: int) -> list[str]:
    items: list[str] = []
    for target in sorted(graph.class_edges.get(source_rep, [])):
        rep_idx = min(graph.class_members[target])
        items.append(normalize(graph.equations[rep_idx]))
    return shortest_unique_equations(items, limit)


def eq_list(graph, reps: list[int] | tuple[int, ...]) -> list[str]:
    items: list[str] = []
    for rep in reps:
        for idx in graph.class_members[rep]:
            items.append(normalize(graph.equations[idx]))
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


def emit_rule(lines: list[str], header: str, items: list[str], conclusion: list[str]) -> None:
    lines.append(header)
    lines.extend(wrap_items(items))
    lines.extend(conclusion)
    lines.append("STOP.")
    lines.append("")


def emit_pair_rule(lines: list[str], header: str, pairs: list[tuple[str, str]], verdict: str) -> None:
    lines.append(header)
    for eq1, eq2 in pairs:
        lines.append(f"  {eq1} => {eq2}")
    lines.append(f"THEN {verdict}.")
    lines.append("STOP.")
    lines.append("")


def build_cheatsheet() -> str:
    graph = load_graph_data()

    c4_protos = bucket_prototypes(eq_list(graph, [LEFT_CLASS]), source_signature)
    c5_protos = bucket_prototypes(eq_list(graph, [RIGHT_CLASS]), source_signature)
    c13_protos = bucket_prototypes(eq_list(graph, [BRIDGE_RIGHT_CLASS]), source_signature)
    c24_protos = bucket_prototypes(eq_list(graph, [BRIDGE_LEFT_CLASS]), source_signature)
    c41_protos = bucket_prototypes(eq_list(graph, [CONST_CLASS]), source_signature)
    c887_sources = eq_list(graph, [C887_CLASS])

    c13_target_protos = bucket_prototypes(eq_list(graph, BRIDGE_RIGHT_TARGETS), target_signature)
    c24_target_protos = eq_list(graph, BRIDGE_LEFT_TARGETS)
    c887_targets = eq_list(graph, C887_TARGETS)

    c4_exact_sources = shortest_unique_equations(eq_list(graph, [LEFT_CLASS]), 20)
    c5_exact_sources = shortest_unique_equations(eq_list(graph, [RIGHT_CLASS]), 20)
    c41_exact_sources = shortest_unique_equations(eq_list(graph, [CONST_CLASS]), 32)
    c13_exact_sources = shortest_unique_equations(eq_list(graph, [BRIDGE_RIGHT_CLASS]), 28)
    c24_exact_sources = shortest_unique_equations(eq_list(graph, [BRIDGE_LEFT_CLASS]), 28)
    c887_exact_sources = shortest_unique_equations(eq_list(graph, [C887_CLASS]), 8)

    c4_exact_targets = outgoing_examples(graph, LEFT_CLASS, 18)
    c5_exact_targets = outgoing_examples(graph, RIGHT_CLASS, 18)
    c41_exact_targets = outgoing_examples(graph, CONST_CLASS, 18)
    c13_exact_targets = outgoing_examples(graph, BRIDGE_RIGHT_CLASS, 18)
    c24_exact_targets = outgoing_examples(graph, BRIDGE_LEFT_CLASS, 12)
    c887_exact_targets = outgoing_examples(graph, C887_CLASS, 8)

    lines: list[str] = []
    lines.append("NO MATCH means only NO MATCH. It is not by itself evidence for FALSE.")
    lines.append("Never answer FALSE only because no positive family matched.")
    lines.append("Use FALSE only with a concrete witness model below, or with a direct family refutation.")
    lines.append("")
    lines.append("Mandatory scan order: same-law, singleton, exact hardcoded pair, source family, witness model, then silence.")
    lines.append("Do not invent FALSE from no-match, balance-only talk, or 'nothing listed'.")
    lines.append("")
    lines.append("Up to one renaming = rename variables consistently everywhere.")
    lines.append("Same signature = same star-count, same sorted variable multiplicities, same left/right anchor of the lhs variable.")
    lines.append("Do not match by vague resemblance, reassociation, balance alone, or deleting symbols.")
    lines.append("")
    lines.append("IF E1 and E2 are the same law up to one consistent renaming")
    lines.append("THEN TRUE.")
    lines.append("STOP.")
    lines.append("")
    lines.append("IF one side of E1 is a bare variable v and v is absent from the other side")
    lines.append("THEN TRUE.")
    lines.append("STOP.")
    lines.append("")
    lines.append("If the singleton rule fires, stop immediately even if E2 looks deeper or repeats x.")
    lines.append("")
    lines.append("IF E2 is x = x")
    lines.append("THEN TRUE.")
    lines.append("STOP.")
    lines.append("")

    emit_pair_rule(
        lines,
        "IF (E1,E2) is exactly one of these benchmark-hard TRUE pairs, up to one renaming:",
        EXACT_TRUE_PAIRS,
        "TRUE",
    )
    emit_pair_rule(
        lines,
        "IF (E1,E2) is exactly one of these benchmark-hard FALSE pairs, up to one renaming:",
        EXACT_FALSE_PAIRS,
        "FALSE",
    )

    lines.append("FALSE witnesses from the paper:")
    lines.append("- LEFT PROJECTION a*b=a: an equation holds iff the leftmost variable is the same on both sides.")
    lines.append("- RIGHT PROJECTION a*b=b: an equation holds iff the rightmost variable is the same on both sides.")
    lines.append("- CONSTANT magma a*b=c: an equation holds iff both sides contain *, or both sides are the same bare variable.")
    lines.append("- XOR / affine model over Z/2: an equation holds iff every variable has the same parity on both sides.")
    lines.append("If one of these witnesses satisfies E1 but fails E2, answer FALSE.")
    lines.append("")

    emit_rule(
        lines,
        "IF E1 matches one of these C4 source prototypes, up to one renaming and the same signature:",
        c4_protos,
        ["THEN TRUE iff the leftmost variable on the two sides of E2 is the same.", "THEN FALSE via left projection otherwise."],
    )
    emit_rule(lines, "Extra exact C4 source reminders, up to one renaming:", c4_exact_sources, ["THEN use the same C4 rule above."])
    emit_rule(
        lines,
        "If E1 already matched the C4 family and E2 is one of these exact C4 reachable targets, up to one renaming:",
        c4_exact_targets,
        ["THEN TRUE."],
    )
    emit_rule(
        lines,
        "IF E1 matches one of these C5 source prototypes, up to one renaming and the same signature:",
        c5_protos,
        ["THEN TRUE iff the rightmost variable on the two sides of E2 is the same.", "THEN FALSE via right projection otherwise."],
    )
    emit_rule(lines, "Extra exact C5 source reminders, up to one renaming:", c5_exact_sources, ["THEN use the same C5 rule above."])
    emit_rule(
        lines,
        "If E1 already matched the C5 family and E2 is one of these exact C5 reachable targets, up to one renaming:",
        c5_exact_targets,
        ["THEN TRUE."],
    )
    emit_rule(
        lines,
        "IF E1 matches one of these C41 source prototypes, up to one renaming and the same signature:",
        c41_protos,
        ["THEN TRUE iff both sides of E2 contain *.", "THEN FALSE via the constant magma otherwise."],
    )
    emit_rule(lines, "Extra exact C41 source reminders, up to one renaming:", c41_exact_sources, ["THEN use the same C41 rule above."])
    emit_rule(
        lines,
        "If E1 already matched the C41 family and E2 is one of these exact C41 reachable targets, up to one renaming:",
        c41_exact_targets,
        ["THEN TRUE."],
    )
    emit_rule(
        lines,
        "IF E1 matches one of these C13 source prototypes, up to one renaming and the same signature:",
        c13_protos,
        [
            "AND E2 matches one of these C13 safe target prototypes, up to one renaming and the same signature:",
            *wrap_items(c13_target_protos),
            "THEN TRUE.",
        ],
    )
    emit_rule(lines, "Extra exact C13 source reminders, up to one renaming:", c13_exact_sources, ["THEN use the C13 rules here, not a fallback FALSE."])
    emit_rule(
        lines,
        "Extra exact C13 reachable targets, up to one renaming:",
        c13_exact_targets,
        ["THEN TRUE if E1 already matched the C13 family above."],
    )
    emit_rule(
        lines,
        "IF E1 matches one of these C24 source prototypes, up to one renaming and the same signature:",
        c24_protos,
        [
            "AND E2 is x*x=x*((y*z)*w), up to one renaming:",
            *wrap_items(c24_target_protos),
            "THEN TRUE.",
        ],
    )
    emit_rule(lines, "Extra exact C24 source reminders, up to one renaming:", c24_exact_sources, ["THEN use the C24 rule above."])
    emit_rule(
        lines,
        "Extra exact C24 reachable targets, up to one renaming:",
        c24_exact_targets,
        ["THEN TRUE if E1 already matched the C24 family above."],
    )
    emit_rule(
        lines,
        "IF E1 is one of these exact C887 sources, up to one renaming:",
        c887_sources,
        [
            "AND E2 is x=x*(((x*y)*x)*y), up to one renaming:",
            *wrap_items(c887_targets),
            "THEN TRUE.",
        ],
    )
    emit_rule(lines, "Extra exact C887 source reminders, up to one renaming:", c887_exact_sources, ["THEN use the C887 rule above."])
    emit_rule(
        lines,
        "Extra exact C887 reachable targets, up to one renaming:",
        c887_exact_targets,
        ["THEN TRUE if E1 already matched the C887 family above."],
    )

    lines.append("If no rule above decides the pair, the sheet is silent.")
    lines.append("Silence is not a proof of FALSE; use additional reasoning rather than citing no-match.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args()

    text = build_cheatsheet()
    payload = text.encode("utf-8")
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