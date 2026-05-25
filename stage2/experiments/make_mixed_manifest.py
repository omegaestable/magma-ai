#!/usr/bin/env python3
"""Create a reproducible mixed JSONL manifest from official problem files."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBLEM_ROOT = REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems"
DEFAULT_SOURCES = {
    "normal": PROBLEM_ROOT / "normal.jsonl",
    "hard1": PROBLEM_ROOT / "hard1.jsonl",
    "hard2": PROBLEM_ROOT / "hard2.jsonl",
    "hard3": PROBLEM_ROOT / "hard3.jsonl",
}


def repo_display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def parse_source_entries(entries: list[str]) -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Expected NAME=PATH, got: {entry}")
        name, raw_path = entry.split("=", 1)
        name = name.strip()
        raw_path = raw_path.strip()
        if not name or not raw_path:
            raise ValueError(f"Expected NAME=PATH, got: {entry}")
        path = Path(raw_path)
        if not path.is_absolute():
            path = path.resolve()
        sources[name] = path
    return sources


def parse_source_count_entries(entries: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Expected NAME=COUNT, got: {entry}")
        name, raw_count = entry.split("=", 1)
        name = name.strip()
        raw_count = raw_count.strip()
        if not name or not raw_count:
            raise ValueError(f"Expected NAME=COUNT, got: {entry}")
        try:
            count = int(raw_count)
        except ValueError as exc:
            raise ValueError(f"Invalid count for {name}: {raw_count}") from exc
        if count <= 0:
            raise ValueError(f"Count for {name} must be positive, got {count}")
        counts[name] = count
    return counts


def resolve_source_config(
    *,
    per_source: int | None,
    sources: dict[str, Path] | None,
    source_counts: dict[str, int] | None,
) -> tuple[dict[str, Path], dict[str, int]]:
    resolved_sources = dict(sources or DEFAULT_SOURCES)
    resolved_counts = dict(source_counts or {})

    unknown_sources = sorted(name for name in resolved_counts if name not in resolved_sources)
    if unknown_sources:
        joined = ", ".join(unknown_sources)
        raise ValueError(f"Counts supplied for unknown sources: {joined}")

    if per_source is not None and per_source <= 0:
        raise ValueError(f"per_source must be positive, got {per_source}")

    if per_source is None and not resolved_counts:
        raise ValueError("Provide --per-source or at least one --source-count")

    counts_by_source: dict[str, int] = {}
    for name in resolved_sources:
        count = resolved_counts.get(name, per_source)
        if count is None:
            raise ValueError(f"No count configured for source: {name}")
        counts_by_source[name] = count
    return resolved_sources, counts_by_source


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
        if line:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
    return rows


def build_mixed_manifest(
    *,
    out: Path,
    seed: int,
    per_source: int | None,
    shuffle: bool,
    sources: dict[str, Path] | None = None,
    source_counts: dict[str, int] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], Path]:
    resolved_sources, counts_by_source = resolve_source_config(
        per_source=per_source,
        sources=sources,
        source_counts=source_counts,
    )
    selected: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {
        "seed": seed,
        "per_source": per_source,
        "source_counts": counts_by_source,
        "sources": {},
    }
    rng = random.Random(seed)
    for name, path in resolved_sources.items():
        count = counts_by_source[name]
        rows = load_rows(path)
        if len(rows) < count:
            raise ValueError(f"{name} has only {len(rows)} rows, need {count}")
        sample = rng.sample(rows, count)
        selected.extend(dict(row) for row in sample)
        metadata["sources"][name] = {
            "path": repo_display_path(path),
            "available": len(rows),
            "selected": count,
            "ids": [row.get("id") for row in sample],
            "expected_true": sum(1 for row in sample if row.get("answer") is True),
            "expected_false": sum(1 for row in sample if row.get("answer") is False),
        }

    if shuffle:
        rng.shuffle(selected)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for row in selected:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")

    metadata["total"] = len(selected)
    metadata["expected_true"] = sum(1 for row in selected if row.get("answer") is True)
    metadata["expected_false"] = sum(1 for row in selected if row.get("answer") is False)
    meta_path = out.with_suffix(out.suffix + ".meta.json")
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return selected, metadata, meta_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--per-source", type=int, default=50)
    parser.add_argument("--shuffle", action="store_true")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Optional explicit source manifest. Repeatable.",
    )
    parser.add_argument(
        "--source-count",
        action="append",
        default=[],
        metavar="NAME=COUNT",
        help="Optional per-source override. Repeatable.",
    )
    args = parser.parse_args()

    sources = parse_source_entries(args.source) if args.source else None
    source_counts = parse_source_count_entries(args.source_count) if args.source_count else None

    selected, metadata, meta_path = build_mixed_manifest(
        out=args.out,
        seed=args.seed,
        per_source=args.per_source,
        shuffle=args.shuffle,
        sources=sources,
        source_counts=source_counts,
    )
    print(f"wrote {args.out} ({metadata['total']} rows)")
    print(f"wrote {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
