#!/usr/bin/env python3
"""Build a stratified competition-simulation Marathon manifest.

The generated manifest is for local research runs only. It deliberately mixes
official public development files with Hugging Face mirror and analysis-only
files, while preserving source metadata and namespacing ids so Marathon
last-write-wins scoring cannot collapse duplicate ids from mirrored corpora.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR_PROBLEMS = REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems"
HF_CACHE = REPO_ROOT / "data" / "hf_cache"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tmp_stage2_smoke" / f"{datetime.now():%Y-%m-%d}-competition-sim"
DEFAULT_OUTPUT = DEFAULT_OUTPUT_ROOT / "competition_sim_10each_7true_3false.jsonl"
ID_SEPARATOR = "__"


@dataclass(frozen=True)
class SourceSpec:
    name: str
    scope: str
    role: str
    path: Path


def default_sources() -> list[SourceSpec]:
    return [
        SourceSpec("official_normal", "official", "public", VENDOR_PROBLEMS / "normal.jsonl"),
        SourceSpec("official_hard1", "official", "public", VENDOR_PROBLEMS / "hard1.jsonl"),
        SourceSpec("official_hard2", "official", "public", VENDOR_PROBLEMS / "hard2.jsonl"),
        SourceSpec("official_hard3", "official", "public", VENDOR_PROBLEMS / "hard3.jsonl"),
        SourceSpec("hf_normal", "hf_core", "public_duplicate", HF_CACHE / "normal.jsonl"),
        SourceSpec("hf_hard", "hf_core", "benchmark", HF_CACHE / "hard.jsonl"),
        SourceSpec("hf_hard1", "hf_core", "public_duplicate", HF_CACHE / "hard1.jsonl"),
        SourceSpec("hf_hard2", "hf_core", "public_duplicate", HF_CACHE / "hard2.jsonl"),
        SourceSpec("hf_hard3", "hf_core", "public_duplicate", HF_CACHE / "hard3.jsonl"),
        SourceSpec("evaluation_normal", "hf_analysis", "analysis_only", HF_CACHE / "evaluation_normal.jsonl"),
        SourceSpec("evaluation_hard", "hf_analysis", "analysis_only", HF_CACHE / "evaluation_hard.jsonl"),
        SourceSpec("evaluation_extra_hard", "hf_analysis", "analysis_only", HF_CACHE / "evaluation_extra_hard.jsonl"),
        SourceSpec("evaluation_order5", "hf_analysis", "analysis_only", HF_CACHE / "evaluation_order5.jsonl"),
    ]


def repo_display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def slug(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", text.strip())
    return cleaned.strip("_") or "source"


def load_rows(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        return []
    if stripped[0] == "[":
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON array in {path}")
        return [row for row in payload if isinstance(row, dict)]

    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def require_bool_labels(rows: list[dict[str, Any]], source: SourceSpec) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    true_rows = [row for row in rows if row.get("answer") is True]
    false_rows = [row for row in rows if row.get("answer") is False]
    unlabeled = len(rows) - len(true_rows) - len(false_rows)
    if unlabeled:
        raise ValueError(f"{source.name} has {unlabeled} rows without boolean answer labels")
    return true_rows, false_rows


def namespaced_row(source: SourceSpec, row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    original_id = str(row.get("id", ""))
    if not original_id:
        raise ValueError(f"{source.name} contains a row without id")
    out["id"] = f"{slug(source.name)}{ID_SEPARATOR}{original_id}"
    out["source_bucket"] = source.name
    out["source_scope"] = source.scope
    out["source_role"] = source.role
    out["original_id"] = original_id
    return out


def pair_key(row: dict[str, Any]) -> str:
    eq1 = row.get("eq1_id")
    eq2 = row.get("eq2_id")
    if eq1 is None or eq2 is None:
        return f"text:{row.get('equation1')}=>{row.get('equation2')}"
    return f"{eq1}->{eq2}"


def duplicate_pair_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_pair.setdefault(pair_key(row), []).append(row)
    duplicates: list[dict[str, Any]] = []
    for key, group in sorted(by_pair.items()):
        if len(group) <= 1:
            continue
        duplicates.append(
            {
                "pair": key,
                "count": len(group),
                "ids": [row.get("id") for row in group],
                "original_ids": [row.get("original_id") for row in group],
                "sources": [row.get("source_bucket") for row in group],
            }
        )
    return duplicates


def build_manifest(
    *,
    out: Path,
    seed: int,
    true_per_source: int,
    false_per_source: int,
    shuffle: bool,
    sources: list[SourceSpec] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], Path]:
    if true_per_source < 0 or false_per_source < 0:
        raise ValueError("true_per_source and false_per_source must be nonnegative")
    if true_per_source + false_per_source <= 0:
        raise ValueError("at least one row per source is required")

    resolved_sources = sources or default_sources()
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {
        "label": "competition_sim_10each_7true_3false",
        "seed": seed,
        "true_per_source": true_per_source,
        "false_per_source": false_per_source,
        "id_namespace_separator": ID_SEPARATOR,
        "sources": {},
    }

    for source in resolved_sources:
        if not source.path.exists():
            raise FileNotFoundError(f"Missing source {source.name}: {source.path}")
        rows = load_rows(source.path)
        true_rows, false_rows = require_bool_labels(rows, source)
        if len(true_rows) < true_per_source or len(false_rows) < false_per_source:
            raise ValueError(
                f"{source.name} cannot satisfy requested split: "
                f"need {true_per_source} TRUE/{false_per_source} FALSE, "
                f"have {len(true_rows)} TRUE/{len(false_rows)} FALSE"
            )
        true_sample = rng.sample(true_rows, true_per_source)
        false_sample = rng.sample(false_rows, false_per_source)
        source_rows = [namespaced_row(source, row) for row in true_sample + false_sample]
        selected.extend(source_rows)
        metadata["sources"][source.name] = {
            "path": repo_display_path(source.path),
            "scope": source.scope,
            "role": source.role,
            "available": len(rows),
            "available_true": len(true_rows),
            "available_false": len(false_rows),
            "selected": len(source_rows),
            "selected_true": len(true_sample),
            "selected_false": len(false_sample),
            "ids": [row["id"] for row in source_rows],
            "original_ids": [row["original_id"] for row in source_rows],
            "eq_pairs": [pair_key(row) for row in source_rows],
        }

    if shuffle:
        rng.shuffle(selected)

    id_counts = Counter(str(row.get("id")) for row in selected)
    duplicate_ids = sorted(identifier for identifier, count in id_counts.items() if count > 1)
    if duplicate_ids:
        raise ValueError(f"Namespaced ids are not unique: {duplicate_ids[:5]}")

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for row in selected:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")

    metadata["output"] = repo_display_path(out)
    metadata["total"] = len(selected)
    metadata["expected_true"] = sum(1 for row in selected if row.get("answer") is True)
    metadata["expected_false"] = sum(1 for row in selected if row.get("answer") is False)
    metadata["duplicate_pairs"] = duplicate_pair_summary(selected)
    metadata["full_reference_budget"] = {
        "compression_ratio": 1.0,
        "seconds_per_problem": 3600,
        "tokens_per_problem": 65536,
        "budget_seconds": len(selected) * 3600,
        "budget_tokens": len(selected) * 65536,
    }
    meta_path = out.with_suffix(out.suffix + ".meta.json")
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return selected, metadata, meta_path


def print_source_counts(sources: list[SourceSpec], *, true_per_source: int, false_per_source: int) -> None:
    print("| Source | Scope | Rows | TRUE | FALSE | Can sample | Path |")
    print("| --- | --- | ---: | ---: | ---: | --- | --- |")
    for source in sources:
        rows = load_rows(source.path)
        true_rows, false_rows = require_bool_labels(rows, source)
        ok = len(true_rows) >= true_per_source and len(false_rows) >= false_per_source
        print(
            f"| {source.name} | {source.scope} | {len(rows)} | {len(true_rows)} | {len(false_rows)} | "
            f"{'yes' if ok else 'no'} | {repo_display_path(source.path)} |"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=20260601)
    parser.add_argument("--true-per-source", type=int, default=7)
    parser.add_argument("--false-per-source", type=int, default=3)
    parser.add_argument("--no-shuffle", dest="shuffle", action="store_false")
    parser.add_argument("--list", action="store_true", help="Print source label counts and exit.")
    args = parser.parse_args()

    sources = default_sources()
    if args.list:
        print_source_counts(
            sources,
            true_per_source=args.true_per_source,
            false_per_source=args.false_per_source,
        )
        return 0

    selected, metadata, meta_path = build_manifest(
        out=args.out.resolve(),
        seed=args.seed,
        true_per_source=args.true_per_source,
        false_per_source=args.false_per_source,
        shuffle=args.shuffle,
        sources=sources,
    )
    budget = metadata["full_reference_budget"]
    print(f"wrote {args.out} ({len(selected)} rows)")
    print(f"wrote {meta_path}")
    print(f"expected_true={metadata['expected_true']} expected_false={metadata['expected_false']}")
    print(f"budget_seconds={budget['budget_seconds']} budget_tokens={budget['budget_tokens']}")
    print(f"duplicate_pairs={len(metadata['duplicate_pairs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
