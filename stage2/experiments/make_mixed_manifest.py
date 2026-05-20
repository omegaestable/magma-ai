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
    per_source: int,
    shuffle: bool,
    sources: dict[str, Path] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], Path]:
    selected: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {
        "seed": seed,
        "per_source": per_source,
        "sources": {},
    }
    rng = random.Random(seed)
    for name, path in (sources or DEFAULT_SOURCES).items():
        rows = load_rows(path)
        if len(rows) < per_source:
            raise ValueError(f"{name} has only {len(rows)} rows, need {per_source}")
        sample = rng.sample(rows, per_source)
        selected.extend(dict(row) for row in sample)
        metadata["sources"][name] = {
            "path": str(path.relative_to(REPO_ROOT)),
            "available": len(rows),
            "selected": per_source,
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
    args = parser.parse_args()

    selected, metadata, meta_path = build_mixed_manifest(
        out=args.out,
        seed=args.seed,
        per_source=args.per_source,
        shuffle=args.shuffle,
    )
    print(f"wrote {args.out} ({metadata['total']} rows)")
    print(f"wrote {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
