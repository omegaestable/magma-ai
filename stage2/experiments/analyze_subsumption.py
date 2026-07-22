"""De-bloat decision tool (WS1).

Reads a corpus audit report and answers, per route:
  - how many rows it uniquely wins,
  - how many of those a general engine (equational / derived-CP closure)
    also proves,
  - roughly how many source bytes the route costs.

A route whose rows are *fully* subsumed is a safe deletion candidate: the
general engine already proves every row it wins, so removing it cannot lose
coverage (the golden gate then proves this empirically).

Usage:
    python stage2/experiments/analyze_subsumption.py --audit stage2/results/audit-2026-07-21.json
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOLVER_PATH = REPO_ROOT / "stage2" / "solver" / "solver.py"

GENERAL_ENGINES = {"equational_closure", "derived_cp_closure"}
# Routes that ARE the general engines, plus cheap primitives worth keeping
# regardless of subsumption (they are tiny and run first).
ALWAYS_KEEP = {
    "true:reflexive", "true:singleton",
    "true:equational_closure", "true:derived_cp_closure",
    "true:deep_absorption_closure", "true:absorption_closure",
}


def function_spans(source: str) -> dict[str, int]:
    """Map top-level function name -> source byte cost."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line.encode("utf-8")))
    spans: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = min(node.end_lineno, len(lines))
            spans[node.name] = offsets[end] - offsets[start]
    return spans


def route_stem(route: str) -> str:
    """'true:tail_square_singleton' -> 'tail_square_singleton'."""
    stem = route.split(":", 1)[1] if ":" in route else route
    return stem.split(":", 1)[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    report = json.loads(args.audit.read_text(encoding="utf-8"))
    source = SOLVER_PATH.read_text(encoding="utf-8")
    spans = function_spans(source)

    rows_by_route: dict[str, list[dict]] = defaultdict(list)
    for payload in report["sets"].values():
        for row in payload["rows"]:
            if row.get("status") == "solved":
                rows_by_route[row["route"]].append(row)

    analysis = []
    for route, rows in sorted(rows_by_route.items()):
        true_rows = [r for r in rows if r.get("verdict") == "true"]
        subsumed = [r for r in true_rows
                    if set(r.get("subsumed_by", [])) & GENERAL_ENGINES]
        stem = route_stem(route)
        # Attribute every top-level function whose name starts with the stem.
        cost = sum(size for name, size in spans.items() if name.startswith(stem))
        matched = sorted(n for n in spans if n.startswith(stem))
        analysis.append({
            "route": route,
            "rows": len(rows),
            "true_rows": len(true_rows),
            "subsumed": len(subsumed),
            "fully_subsumed": bool(true_rows) and len(subsumed) == len(true_rows),
            "source_bytes": cost,
            "functions": matched,
        })

    candidates = [
        a for a in analysis
        if a["fully_subsumed"] and a["route"] not in ALWAYS_KEEP and a["source_bytes"] > 0
    ]
    candidates.sort(key=lambda a: -a["source_bytes"])
    risky = [
        a for a in analysis
        if a["true_rows"] and not a["fully_subsumed"] and a["route"] not in ALWAYS_KEEP
    ]
    risky.sort(key=lambda a: -a["source_bytes"])

    print("=== SAFE DELETION CANDIDATES (every won row also proved by a general engine) ===")
    total = 0
    for a in candidates:
        total += a["source_bytes"]
        print(f"  {a['route']:52s} rows={a['rows']:4d} "
              f"subsumed={a['subsumed']}/{a['true_rows']:<4d} "
              f"bytes={a['source_bytes']:6d}")
    print(f"  -> reclaimable: {total} bytes ({total/1024:.1f} KB)")

    print("\n=== NOT FULLY SUBSUMED (keep, or must be replaced before deleting) ===")
    for a in risky[:30]:
        print(f"  {a['route']:52s} rows={a['rows']:4d} "
              f"subsumed={a['subsumed']}/{a['true_rows']:<4d} "
              f"bytes={a['source_bytes']:6d}")

    unused = sorted(
        name for name in spans
        if re.search(r"_(route|source|block)$", name)
        and not any(route_stem(r).startswith(name.rsplit("_", 1)[0][:12])
                    for r in rows_by_route)
    )
    print(f"\n=== ROUTE-LIKE FUNCTIONS THAT NEVER FIRED ON THIS CORPUS ({len(unused)}) ===")
    dead_bytes = sum(spans[n] for n in unused)
    for name in unused[:40]:
        print(f"  {name:56s} bytes={spans[name]:6d}")
    print(f"  -> never-fired total: {dead_bytes} bytes ({dead_bytes/1024:.1f} KB)")

    if args.out:
        args.out.write_text(json.dumps({
            "candidates": candidates, "risky": risky,
            "never_fired": [{"name": n, "bytes": spans[n]} for n in unused],
        }, indent=2), encoding="utf-8")
        print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
