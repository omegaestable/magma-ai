#!/usr/bin/env python3
"""Extract every teorth FinitePoly magma from the cached entries as a table.

The 2026-08-26 witness hunt found that 13 of 28 unseen FALSE misses were
refuted by tables already sitting in `data/teorth_cache/full_entries.json`
— while every search engine (constraint search to order 9, z3 to order 10,
~1M quadratic polynomials) found none. The facts lists in the cache are
sparse (10 of the 13 pairs were not mentioned in any entry's facts), but the
tables themselves are complete, so this dumps all of them for selection.

Two entry shapes: a literal `FinitePoly [[...], ...]` table, or a polynomial
`FinitePoly <expr> % m` over Z_m with `x`, `y`, `²`, `³`, `*`, `+`.

Output: jsonl of {"name", "order", "table"} — deduplicated by table.

Usage:
    python stage2/experiments/teorth_finitepoly_library.py \
        --out stage2/results/teorth-finitepoly-library.jsonl
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

POLY_RE = re.compile(r"FinitePoly\s+(.*?)\s*%\s*(\d+)")
TABLE_RE = re.compile(r"FinitePoly\s+(\[\[.*\]\])")


def _clean(name: str) -> str:
    # The cache carries mojibake around the display name; keep the ASCII
    # core plus the superscripts we need.
    return (name.replace("²", "^2").replace("³", "^3")
                .replace("Â²", "^2").replace("Â³", "^3"))


def parse_entry(name: str) -> tuple[int, list[list[int]]] | None:
    text = _clean(name)
    m = TABLE_RE.search(text)
    if m:
        table = ast.literal_eval(m.group(1))
        n = len(table)
        if all(len(row) == n for row in table) and all(
                isinstance(v, int) and 0 <= v < n for row in table for v in row):
            return n, [list(row) for row in table]
        return None
    m = POLY_RE.search(text)
    if not m:
        return None
    expr, modulus = m.group(1), int(m.group(2))
    expr = expr.replace("^", "**")
    if not re.fullmatch(r"[0-9xy\s\+\*\(\)\-]*", expr):
        return None
    try:
        code = compile(expr, "<poly>", "eval")
    except SyntaxError:
        return None
    n = modulus
    table = [[int(eval(code, {"__builtins__": {}}, {"x": x, "y": y})) % n
              for y in range(n)] for x in range(n)]
    return n, table


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    entries = json.load(open(REPO / "data" / "teorth_cache" / "full_entries.json",
                             encoding="utf-8"))
    seen: dict[tuple, str] = {}
    skipped = 0
    for entry in entries:
        name = entry.get("name") or ""
        if "FinitePoly" not in name:
            continue
        parsed = parse_entry(name)
        if parsed is None:
            skipped += 1
            continue
        n, table = parsed
        key = tuple(tuple(row) for row in table)
        seen.setdefault(key, _clean(name))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for key, name in seen.items():
            handle.write(json.dumps({"name": name, "order": len(key),
                                     "table": [list(r) for r in key]}) + "\n")
    orders: dict[int, int] = {}
    for key in seen:
        orders[len(key)] = orders.get(len(key), 0) + 1
    print(f"{len(seen)} distinct tables ({skipped} unparsed) -> {args.out}")
    print("orders:", dict(sorted(orders.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
