#!/usr/bin/env python3
"""Shared catalog for imported SAIR problem sets.

Policy:
- ``data/hf_cache`` is the canonical local mirror of Hugging Face problem
  subsets for theory analysis and offline inspection.
- ``evaluation_*`` subsets are analysis-only for now. They are imported and
  validated, but they are not part of the default Stage 2 benchmark/eval
  workflows.
- ``data/stage2_official_problems`` mirrors the vendored official Stage 2
  public fixtures and remains the source of truth for runner-facing evals.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
HF_CACHE_DIR = REPO_ROOT / "data" / "hf_cache"
HF_METADATA_DIR = HF_CACHE_DIR / "metadata"
OFFICIAL_STAGE2_PROBLEMS_DIR = REPO_ROOT / "data" / "stage2_official_problems"

CORE_HF_SUBSETS = ("normal", "hard", "hard1", "hard2", "hard3")
ANALYSIS_ONLY_HF_SUBSETS = (
    "evaluation_normal",
    "evaluation_hard",
    "evaluation_extra_hard",
    "evaluation_order5",
)
ALL_HF_SUBSETS = CORE_HF_SUBSETS + ANALYSIS_ONLY_HF_SUBSETS

OFFICIAL_STAGE2_PUBLIC_FILES = (
    "normal.jsonl",
    "hard1.jsonl",
    "hard2.jsonl",
    "hard3.jsonl",
    "sample_20.json",
    "sample_200.json",
    "marathon/normal_100.jsonl",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_problem_file(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON array in {path}")
        return payload
    if path.suffix == ".jsonl":
        return load_jsonl(path)
    raise ValueError(f"Unsupported problem file format: {path}")


def load_hf_problem_set(name: str) -> list[dict[str, Any]]:
    if name not in ALL_HF_SUBSETS:
        raise ValueError(f"Unknown HF subset {name!r}. Expected one of: {ALL_HF_SUBSETS}")
    return load_problem_file(HF_CACHE_DIR / f"{name}.jsonl")


def load_hf_problem_corpus(*, include_analysis_only: bool = False) -> list[dict[str, Any]]:
    subset_names = list(CORE_HF_SUBSETS)
    if include_analysis_only:
        subset_names.extend(ANALYSIS_ONLY_HF_SUBSETS)

    rows: list[dict[str, Any]] = []
    for subset in subset_names:
        role = "analysis_only" if subset in ANALYSIS_ONLY_HF_SUBSETS else "benchmark"
        for row in load_hf_problem_set(subset):
            rows.append(
                {
                    **row,
                    "_subset_name": subset,
                    "_subset_role": role,
                    "_benchmark_file": f"{subset}.jsonl",
                }
            )
    return rows


def load_hf_metadata(name: str) -> dict[str, Any]:
    if name not in ALL_HF_SUBSETS:
        raise ValueError(f"Unknown HF subset {name!r}. Expected one of: {ALL_HF_SUBSETS}")
    return json.loads((HF_METADATA_DIR / f"{name}.json").read_text(encoding="utf-8"))
