#!/usr/bin/env python3
"""
teorth_true_proof_agent.py

Phase 0 helper for Teorth implication certificates.

What it does:
- Reads Teorth graph/matrix metadata from data/teorth_cache/graph.json
- Reads proof metadata from data/teorth_cache/full_entries.json
- Certifies implication pairs with source tags (explicit/implicit proof/conjecture)
- Scrapes TRUE implications (optionally proof-only)

Notes:
- Benchmark JSON files do not carry explicit Lean proof objects.
- This tool attaches a reproducible source label and, when available,
  a full_entries source record (filename, line, theorem name).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from v21_data_infrastructure import build_equation_map, load_equations, normalize_eq

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "data" / "teorth_cache"
GRAPH_PATH = CACHE_DIR / "graph.json"
ENTRIES_PATH = CACHE_DIR / "full_entries.json"

N_EQ = 4694

RAW_TO_LABEL = {
    0: "explicit_conjecture_false",
    1: "explicit_conjecture_true",
    2: "explicit_proof_false",
    3: "explicit_proof_true",
    4: "implicit_conjecture_false",
    5: "implicit_conjecture_true",
    6: "implicit_proof_false",
    7: "implicit_proof_true",
    8: "unknown",
}

TRUE_LABELS = {"explicit_proof_true", "implicit_proof_true", "explicit_conjecture_true", "implicit_conjecture_true"}
PROOF_TRUE_LABELS = {"explicit_proof_true", "implicit_proof_true"}


def load_graph_raw() -> dict:
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


def build_entry_index(entries: list[dict]) -> dict[tuple[int, int], list[dict]]:
    index: dict[tuple[int, int], list[dict]] = {}
    for entry in entries:
        variant = entry.get("variant") or {}
        imp = variant.get("implication")
        if not imp:
            continue
        lhs = imp.get("lhs", "")
        rhs = imp.get("rhs", "")
        if not (lhs.startswith("Equation") and rhs.startswith("Equation")):
            continue
        try:
            lhs_id = int(lhs.replace("Equation", "")) - 1
            rhs_id = int(rhs.replace("Equation", "")) - 1
        except ValueError:
            continue
        key = (lhs_id, rhs_id)
        index.setdefault(key, []).append(
            {
                "name": entry.get("name"),
                "filename": entry.get("filename"),
                "line": entry.get("line"),
                "proven": bool(entry.get("proven")),
                "finite": bool((imp or {}).get("finite", False)),
            }
        )
    return index


def targets_from_benchmark(path: Path, eq_map: dict[str, int]) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            e1 = normalize_eq(obj["equation1"])
            e2 = normalize_eq(obj["equation2"])
            i = eq_map.get(e1)
            j = eq_map.get(e2)
            rows.append(
                {
                    "id": obj.get("id"),
                    "equation1": obj["equation1"],
                    "equation2": obj["equation2"],
                    "answer": bool(obj.get("answer")),
                    "eq1_id": i,
                    "eq2_id": j,
                }
            )
    return rows


def pair_indices(target_rows: Iterable[dict]) -> list[int]:
    return sorted({r["eq1_id"] * N_EQ + r["eq2_id"] for r in target_rows if r["eq1_id"] is not None and r["eq2_id"] is not None})


def decode_selected_cells(graph: dict, flat_indices: list[int]) -> dict[int, int]:
    """Decode only requested flat indices from RLE in one pass."""
    out: dict[int, int] = {}
    if not flat_indices:
        return out

    rle = graph["rle_encoded_array"]
    ptr = 0
    want_idx = 0

    for k in range(0, len(rle), 2):
        raw_value = int(rle[k])
        count = int(rle[k + 1])
        start = ptr
        end = ptr + count

        while want_idx < len(flat_indices) and start <= flat_indices[want_idx] < end:
            out[flat_indices[want_idx]] = raw_value
            want_idx += 1
        ptr = end
        if want_idx >= len(flat_indices):
            break

    return out


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def certify_benchmark(input_jsonl: Path, out_jsonl: Path) -> None:
    equations = load_equations()
    eq_map = build_equation_map(equations)

    targets = targets_from_benchmark(input_jsonl, eq_map)
    graph = load_graph_raw()
    entries = json.loads(ENTRIES_PATH.read_text(encoding="utf-8"))
    entry_index = build_entry_index(entries)

    flats = pair_indices(targets)
    cell_map = decode_selected_cells(graph, flats)

    out_rows = []
    for row in targets:
        i = row["eq1_id"]
        j = row["eq2_id"]
        if i is None or j is None:
            row_out = dict(row)
            row_out.update({"status": "unmapped", "is_true": None, "sources": []})
            out_rows.append(row_out)
            continue

        flat = i * N_EQ + j
        raw = cell_map.get(flat, 8)
        label = RAW_TO_LABEL.get(raw, "unknown")
        sources = entry_index.get((i, j), [])

        row_out = dict(row)
        row_out.update(
            {
                "status": label,
                "is_true": label in TRUE_LABELS,
                "source_type": "proof" if label in PROOF_TRUE_LABELS else ("conjecture" if label in TRUE_LABELS else "counterexample_or_unknown"),
                "sources": sources,
                "source_line": sources[0]["line"] if sources else None,
                "source_file": sources[0]["filename"] if sources else None,
                "source_name": sources[0]["name"] if sources else None,
            }
        )
        out_rows.append(row_out)

    write_jsonl(out_jsonl, out_rows)
    print(f"WROTE {out_jsonl.as_posix()} rows={len(out_rows)}")


def scrape_true_pairs(out_jsonl: Path, proof_only: bool, max_rows: int) -> None:
    graph = load_graph_raw()
    entries = json.loads(ENTRIES_PATH.read_text(encoding="utf-8"))
    entry_index = build_entry_index(entries)

    allow = PROOF_TRUE_LABELS if proof_only else TRUE_LABELS
    rle = graph["rle_encoded_array"]

    rows_written = 0
    flat_ptr = 0
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    with out_jsonl.open("w", encoding="utf-8") as out:
        for k in range(0, len(rle), 2):
            raw_value = int(rle[k])
            count = int(rle[k + 1])
            label = RAW_TO_LABEL.get(raw_value, "unknown")
            if label not in allow:
                flat_ptr += count
                continue

            for off in range(count):
                flat = flat_ptr + off
                i = flat // N_EQ
                j = flat % N_EQ
                sources = entry_index.get((i, j), [])
                obj = {
                    "eq1_id": i,
                    "eq2_id": j,
                    "status": label,
                    "source_type": "proof" if label in PROOF_TRUE_LABELS else "conjecture",
                    "sources": sources,
                }
                out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                rows_written += 1
                if max_rows > 0 and rows_written >= max_rows:
                    print(f"WROTE {out_jsonl.as_posix()} rows={rows_written} (capped)")
                    return

            flat_ptr += count

    print(f"WROTE {out_jsonl.as_posix()} rows={rows_written}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Teorth implication proof/certificate scraper.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_bench = sub.add_parser("certify-benchmark", help="Attach graph/full_entries source tags to a benchmark JSONL.")
    p_bench.add_argument("--input", required=True)
    p_bench.add_argument("--output", required=True)

    p_scrape = sub.add_parser("scrape-true", help="Scrape TRUE implications from graph.json.")
    p_scrape.add_argument("--output", required=True)
    p_scrape.add_argument("--proof-only", action="store_true", help="Only keep explicit/implicit proof-true cells.")
    p_scrape.add_argument("--max-rows", type=int, default=0, help="0 = no cap.")

    args = parser.parse_args()

    if args.cmd == "certify-benchmark":
        certify_benchmark(Path(args.input), Path(args.output))
    elif args.cmd == "scrape-true":
        scrape_true_pairs(Path(args.output), args.proof_only, args.max_rows)


if __name__ == "__main__":
    main()
