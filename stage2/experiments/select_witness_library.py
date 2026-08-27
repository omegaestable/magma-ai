#!/usr/bin/env python3
"""Greedy set-cover: which teorth FinitePoly tables are worth shipping?

Population = FALSE rows the cheap named-witness stage does NOT refute (rows
prior sweeps solved only by constraint/local-model search, plus known misses,
plus hard-region survivors). For each candidate table we record which rows it
refutes (`witness_check`, exhaustive), then greedily pick tables by rows
covered per byte until nothing new is covered. The output is the ranked list
with cumulative bytes, so the byte budget decides the cut, not a guess.

Usage:
    python stage2/experiments/select_witness_library.py \
        --library stage2/results/teorth-finitepoly-library.jsonl \
        --rows a.jsonl b.jsonl --max-order 12 --workers 6 \
        --out stage2/results/witness-library-selection.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))

import solver as S  # noqa: E402

_LIB: list[dict] = []


def _init(library_path: str, max_order: int) -> None:
    global _LIB
    _LIB = [json.loads(line) for line in open(library_path, encoding="utf-8")]
    _LIB = [t for t in _LIB if t["order"] <= max_order]


def _table_bytes(table: list[list[int]]) -> int:
    # Cost as written in WITNESS_TABLES: `("NAME", [[...], ...]),` roughly.
    return len(json.dumps(table, separators=(",", ":"))) + 14


def cover_row(problem: dict) -> tuple[str, bool, list[int]]:
    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    # Already covered by the shipped named tables? Then it is not a target.
    for _name, table in S.WITNESS_TABLES:
        if S.witness_check(eq1, eq2, table):
            return str(problem["id"]), True, []
    hits = [index for index, entry in enumerate(_LIB)
            if S.witness_check(eq1, eq2, entry["table"])]
    return str(problem["id"]), False, hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", type=Path, required=True)
    ap.add_argument("--rows", type=Path, nargs="+", required=True)
    ap.add_argument("--max-order", type=int, default=12)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    problems: dict[str, dict] = {}
    for path in args.rows:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                problems[str(row["id"])] = row
    rows = list(problems.values())
    _init(str(args.library), args.max_order)
    library = list(_LIB)
    print(f"{len(rows)} rows x {len(library)} tables (order <= {args.max_order})",
          flush=True)
    t0 = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init,
                             initargs=(str(args.library), args.max_order)) as pool:
        results = list(pool.map(cover_row, rows, chunksize=4))
    print(f"scan {time.monotonic() - t0:.0f}s", flush=True)

    already = sum(1 for _id, covered, _h in results if covered)
    targets = [(rid, set(hits)) for rid, covered, hits in results if not covered]
    coverable = sum(1 for _rid, hits in targets if hits)
    print(f"already covered by WITNESS_TABLES: {already}; targets: {len(targets)}; "
          f"coverable by the library: {coverable}")

    remaining = {rid: hits for rid, hits in targets if hits}
    chosen: list[dict] = []
    cumulative = 0
    while remaining:
        best, best_score, best_cover = None, 0.0, set()
        for index, entry in enumerate(library):
            cover = {rid for rid, hits in remaining.items() if index in hits}
            if not cover:
                continue
            score = len(cover) / _table_bytes(entry["table"])
            if score > best_score:
                best, best_score, best_cover = index, score, cover
        if best is None:
            break
        entry = library[best]
        cumulative += _table_bytes(entry["table"])
        chosen.append({"index": best, "name": entry["name"], "order": entry["order"],
                       "table": entry["table"], "covers": sorted(best_cover),
                       "new_rows": len(best_cover), "bytes": _table_bytes(entry["table"]),
                       "cumulative_bytes": cumulative})
        for rid in best_cover:
            remaining.pop(rid, None)
    covered_total = sum(c["new_rows"] for c in chosen)
    print(f"greedy: {len(chosen)} tables cover {covered_total} rows, "
          f"{cumulative} bytes total")
    for c in chosen[:25]:
        print(f"  +{c['new_rows']:>3} rows  order {c['order']:>2}  {c['bytes']:>4} B  "
              f"cum {c['cumulative_bytes']:>6} B")
    args.out.write_text(json.dumps({
        "rows": len(rows), "already_covered": already, "targets": len(targets),
        "coverable": coverable, "chosen": chosen,
        "uncoverable": sorted(rid for rid, hits in targets if not hits),
    }, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
