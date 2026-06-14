"""Inspect explicit Teorth implication edges near Stage 2 problem rows."""

from __future__ import annotations

import argparse
from collections import deque
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ENTRIES_PATH = ROOT / "data" / "teorth_cache" / "full_entries.json"
EQUATIONS_PATH = ROOT / "data" / "exports" / "equations.txt"
EQUATION_RE = re.compile(r"^Equation(\d+)$")


def equation_number(raw: str) -> int:
    text = raw.strip()
    if text.isdigit():
        return int(text)
    match = EQUATION_RE.match(text)
    if match is None:
        raise argparse.ArgumentTypeError(f"expected EquationN or N, got {raw!r}")
    return int(match.group(1))


def load_equations() -> dict[int, str]:
    lines = EQUATIONS_PATH.read_text(encoding="utf-8").splitlines()
    return {idx + 1: line.strip() for idx, line in enumerate(lines) if line.strip()}


def implication_edges() -> list[dict[str, Any]]:
    entries = json.loads(ENTRIES_PATH.read_text(encoding="utf-8"))
    edges: list[dict[str, Any]] = []
    for entry in entries:
        implication = (entry.get("variant") or {}).get("implication")
        if not implication:
            continue
        lhs_raw = str(implication.get("lhs", ""))
        rhs_raw = str(implication.get("rhs", ""))
        lhs_match = EQUATION_RE.match(lhs_raw)
        rhs_match = EQUATION_RE.match(rhs_raw)
        if lhs_match is None or rhs_match is None:
            continue
        edges.append(
            {
                "lhs": int(lhs_match.group(1)),
                "rhs": int(rhs_match.group(1)),
                "name": entry.get("name"),
                "filename": entry.get("filename"),
                "line": entry.get("line"),
                "finite": bool(implication.get("finite", False)),
                "proven": bool(entry.get("proven")),
            }
        )
    return edges


def bfs_path(edges: list[dict[str, Any]], start: int, goal: int, max_depth: int) -> list[int] | None:
    adjacency: dict[int, list[int]] = {}
    for edge in edges:
        adjacency.setdefault(int(edge["lhs"]), []).append(int(edge["rhs"]))
    queue: deque[tuple[int, list[int]]] = deque([(start, [start])])
    seen = {start}
    while queue:
        node, path = queue.popleft()
        if len(path) - 1 >= max_depth:
            continue
        for nxt in adjacency.get(node, []):
            if nxt in seen:
                continue
            next_path = [*path, nxt]
            if nxt == goal:
                return next_path
            seen.add(nxt)
            queue.append((nxt, next_path))
    return None


def edge_lookup(edges: list[dict[str, Any]]) -> dict[tuple[int, int], list[dict[str, Any]]]:
    lookup: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for edge in edges:
        lookup.setdefault((int(edge["lhs"]), int(edge["rhs"])), []).append(edge)
    return lookup


def compact_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": edge.get("name"),
        "filename": edge.get("filename"),
        "line": edge.get("line"),
        "finite": edge.get("finite"),
        "proven": edge.get("proven"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lhs", type=equation_number, required=True)
    parser.add_argument("--rhs", type=equation_number, required=True)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--nearby-limit", type=int, default=12)
    args = parser.parse_args()

    equations = load_equations()
    edges = implication_edges()
    lookup = edge_lookup(edges)
    path = bfs_path(edges, args.lhs, args.rhs, args.max_depth)

    outgoing = [edge for edge in edges if int(edge["lhs"]) == args.lhs][: args.nearby_limit]
    incoming = [edge for edge in edges if int(edge["rhs"]) == args.rhs][: args.nearby_limit]
    result: dict[str, Any] = {
        "lhs": args.lhs,
        "rhs": args.rhs,
        "lhs_text": equations.get(args.lhs, ""),
        "rhs_text": equations.get(args.rhs, ""),
        "explicit_path": path,
        "explicit_path_edges": [],
        "outgoing_head": [compact_edge(edge) for edge in outgoing],
        "incoming_head": [compact_edge(edge) for edge in incoming],
        "edge_count": len(edges),
    }
    if path is not None:
        for src, dst in zip(path, path[1:]):
            result["explicit_path_edges"].append(
                {
                    "from": src,
                    "to": dst,
                    "from_text": equations.get(src, ""),
                    "to_text": equations.get(dst, ""),
                    "entries": [compact_edge(edge) for edge in lookup.get((src, dst), [])[:3]],
                }
            )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
