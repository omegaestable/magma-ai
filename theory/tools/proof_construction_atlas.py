#!/usr/bin/env python3
"""
proof_construction_atlas.py

Normalize cached proof-page crawl artifacts into a machine-readable construction atlas.

This is the second pass after `proof_scraping_lab.py`:
1. Crawl and cache proof pages.
2. Join each crawled pair with `full_entries.json` provenance.
3. Classify recurring counterexample/proof construction families.
4. Emit pair-level annotations and family summaries for downstream distillation.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from fetch_teorth_data import load_full_entries
from proof_atlas import FAMILY_TEMPLATES, classify_entry

ROOT = Path(__file__).resolve().parent

TEXT_FAMILY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("linear_translation", re.compile(r"linear|translation|shift operator|affine|finite field|z/pz|mod \d+", re.IGNORECASE)),
    ("all4x4_table_counterexamples", re.compile(r"4x4|cayley table|truth table|table counterexample", re.IGNORECASE)),
    ("small_finite_magma", re.compile(r"small magma|finite magma|xor|xnor|and|or|nand|finite witness|counterexample family", re.IGNORECASE)),
    ("central_groupoid_counterexamples", re.compile(r"central groupoid|threec2|weak central groupoid", re.IGNORECASE)),
    ("projection_family_counterexamples", re.compile(r"left projection|right projection|projection family|absorption", re.IGNORECASE)),
    ("modified_lifted_magma", re.compile(r"lifting magma family|lifted magma|modified magma|extended magma", re.IGNORECASE)),
    ("canonizer_confluence", re.compile(r"canon|confluence|normal form|unique factori", re.IGNORECASE)),
    ("exceptional_hard", re.compile(r"greedy|partial magma|infinite|tree|immune|hard case|asterix|austin|obelix", re.IGNORECASE)),
]


def load_crawl_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_packed_pairs(path: Path) -> list[dict]:
    """Load rows from a packed JSONL index (skipping the _meta header line)."""
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if obj.get("_meta"):
                continue
            rows.append(obj)
    return rows


def build_entry_index(entries: list[dict]) -> dict[tuple[int, int], list[dict]]:
    index: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for entry in entries:
        variant = entry.get("variant") or {}
        implication = variant.get("implication") or {}
        lhs = implication.get("lhs", "")
        rhs = implication.get("rhs", "")
        if not (lhs.startswith("Equation") and rhs.startswith("Equation")):
            continue
        try:
            left = int(lhs.replace("Equation", ""))
            right = int(rhs.replace("Equation", ""))
        except ValueError:
            continue
        index[(left, right)].append(entry)
    return index


def page_text_blob(row: dict) -> str:
    parts: list[str] = []
    parts.append(row.get("title", ""))
    for block_name in ["code_blocks", "pre_blocks", "table_blocks"]:
        parts.extend(row.get(block_name, []))
    for link_name in ["theorem_links", "fact_links", "all_links"]:
        for item in row.get(link_name, []):
            parts.append(item.get("name") or item.get("text") or "")
    return "\n".join(part for part in parts if part)


def infer_page_families(row: dict) -> list[str]:
    blob = page_text_blob(row)
    families: list[str] = []
    for family, pattern in TEXT_FAMILY_PATTERNS:
        if pattern.search(blob):
            families.append(family)
    return families


def choose_primary_family(entry_families: list[str], page_families: list[str]) -> str:
    if entry_families:
        counts = Counter(entry_families)
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    if page_families:
        counts = Counter(page_families)
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return "hard_case"


def pair_key_from_row(row: dict) -> tuple[int, int]:
    pair = row.get("pair") or []
    if len(pair) != 2:
        raise ValueError(f"Bad pair row: {row}")
    return int(pair[0]), int(pair[1])


def annotate_row(row: dict, entry_index: dict[tuple[int, int], list[dict]]) -> dict:
    pair = pair_key_from_row(row)
    entries = entry_index.get(pair, [])
    entry_families = [classify_entry(entry) for entry in entries]
    page_families = infer_page_families(row)
    primary_family = choose_primary_family(entry_families, page_families)
    template = FAMILY_TEMPLATES.get(primary_family, FAMILY_TEMPLATES["hard_case"])
    return {
        "pair": list(pair),
        "ok": bool(row.get("ok")),
        "url": row.get("url", ""),
        "title": row.get("title", ""),
        "primary_family": primary_family,
        "family_group": template["family_group"],
        "entry_family_votes": Counter(entry_families),
        "page_family_votes": Counter(page_families),
        "page_signals": {
            "code_blocks": row.get("code_blocks", [])[:3],
            "pre_blocks": row.get("pre_blocks", [])[:3],
            "table_blocks": row.get("table_blocks", [])[:3],
            "pair_link_count": len(row.get("pair_links", [])),
            "theorem_link_count": len(row.get("theorem_links", [])),
            "fact_link_count": len(row.get("fact_links", [])),
        },
        "supporting_entries": [
            {
                "name": entry.get("name"),
                "filename": entry.get("filename"),
                "line": entry.get("line"),
                "classified_family": classify_entry(entry),
            }
            for entry in entries[:8]
        ],
        "known_blockers": list(template["known_blockers"]),
        "paper_refs": list(template["paper_refs"]),
    }


def build_family_summary(annotated_rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in annotated_rows:
        grouped[row["primary_family"]].append(row)

    summary: list[dict] = []
    for family, rows in grouped.items():
        template = FAMILY_TEMPLATES.get(family, FAMILY_TEMPLATES["hard_case"])
        summary.append(
            {
                "family": family,
                "title": template["title"],
                "family_group": template["family_group"],
                "description": template["description"],
                "pair_count": len(rows),
                "ok_count": sum(1 for row in rows if row.get("ok")),
                "paper_refs": list(template["paper_refs"]),
                "known_blockers": list(template["known_blockers"]),
                "sample_pairs": [row["pair"] for row in rows[:10]],
                "sample_titles": [row.get("title", "") for row in rows[:5]],
                "supporting_files": sorted(
                    {
                        item["filename"]
                        for row in rows
                        for item in row.get("supporting_entries", [])
                        if item.get("filename")
                    }
                )[:20],
            }
        )

    summary.sort(key=lambda item: (-item["pair_count"], item["family"]))
    return summary


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, family_summary: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Proof Construction Atlas",
        "",
        "| Family | Group | Pairs | Sample Pairs |",
        "|---|---|---:|---|",
    ]
    for item in family_summary:
        sample_pairs = ", ".join(f"{a},{b}" for a, b in item["sample_pairs"][:4])
        lines.append(f"| {item['family']} | {item['family_group']} | {item['pair_count']} | {sample_pairs} |")
    lines.append("")
    for item in family_summary:
        lines.append(f"## {item['family']}")
        lines.append(f"- title={item['title']}")
        lines.append(f"- pair_count={item['pair_count']}")
        lines.append(f"- family_group={item['family_group']}")
        if item["supporting_files"]:
            lines.append(f"- supporting_file_head={item['supporting_files'][0]}")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_atlas(crawl_jsonl: Path, out_prefix: Path, packed_pairs: Path | None = None) -> dict:
    if packed_pairs is not None:
        crawl_rows = load_packed_pairs(packed_pairs)
    else:
        crawl_rows = load_crawl_rows(crawl_jsonl)
    entry_index = build_entry_index(load_full_entries())
    annotated_rows = [annotate_row(row, entry_index) for row in crawl_rows]
    family_summary = build_family_summary(annotated_rows)

    pair_jsonl = out_prefix.with_suffix(".jsonl")
    family_json = out_prefix.with_name(out_prefix.name + "_families").with_suffix(".json")
    summary_md = out_prefix.with_suffix(".md")

    write_jsonl(pair_jsonl, annotated_rows)
    write_json(family_json, family_summary)
    write_markdown(summary_md, family_summary)
    return {
        "pair_jsonl": pair_jsonl,
        "family_json": family_json,
        "summary_md": summary_md,
        "pair_count": len(annotated_rows),
        "family_count": len(family_summary),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a machine-readable construction atlas from cached proof crawl artifacts")
    parser.add_argument("--crawl-jsonl", default="", help="JSONL output from proof_scraping_lab.py")
    parser.add_argument("--packed-pairs", default="", help="Packed JSONL index from proof_scraping_lab.py --pack-cache")
    parser.add_argument("--out-prefix", default="results/proof_lab/construction_atlas")
    args = parser.parse_args()

    packed = Path(args.packed_pairs) if args.packed_pairs else None
    crawl = Path(args.crawl_jsonl) if args.crawl_jsonl else None
    if not packed and not crawl:
        parser.error("Provide --crawl-jsonl or --packed-pairs")

    result = build_atlas(crawl or Path(""), Path(args.out_prefix), packed_pairs=packed)
    print("=" * 80)
    print(f"WROTE {result['pair_jsonl'].as_posix()} rows={result['pair_count']}")
    print(f"WROTE {result['family_json'].as_posix()} families={result['family_count']}")
    print(f"WROTE {result['summary_md'].as_posix()}")
    print("=" * 80)


if __name__ == "__main__":
    main()