#!/usr/bin/env python3
"""Comprehensive smoke test for imported SAIR problem sets and active loaders."""

from __future__ import annotations

import sys

import atlas_public_dev
import proof_atlas
import proof_construction_atlas

from problem_set_catalog import (
    ALL_HF_SUBSETS,
    ANALYSIS_ONLY_HF_SUBSETS,
    CORE_HF_SUBSETS,
    HF_CACHE_DIR,
    OFFICIAL_STAGE2_PROBLEMS_DIR,
    load_hf_metadata,
    load_hf_problem_corpus,
    load_hf_problem_set,
    load_problem_file,
)
from proof_scraping_lab import pairs_from_jsonl
from v21_data_infrastructure import build_equation_map, load_all_benchmarks, load_equations


REQUIRED_KEYS = {"id", "eq1_id", "eq2_id", "equation1", "equation2"}
OVERLAP_STAGE2_FILES = ("normal", "hard1", "hard2", "hard3")
OFFICIAL_STAGE2_EXPECTED_COUNTS = {
    "normal.jsonl": 1000,
    "hard1.jsonl": 69,
    "hard2.jsonl": 200,
    "hard3.jsonl": 400,
    "sample_20.json": 20,
    "sample_200.json": 200,
    "marathon/normal_100.jsonl": 100,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def validate_problem_rows(rows: list[dict], label: str, require_answer: bool) -> dict:
    ids: set[str] = set()
    true_count = 0
    false_count = 0
    for idx, row in enumerate(rows, start=1):
        missing = REQUIRED_KEYS - row.keys()
        if missing:
            fail(f"{label}: row {idx} missing keys {sorted(missing)}")
        row_id = row["id"]
        if row_id in ids:
            fail(f"{label}: duplicate id {row_id}")
        ids.add(row_id)
        if require_answer:
            if "answer" not in row:
                fail(f"{label}: row {idx} missing answer")
            if bool(row["answer"]):
                true_count += 1
            else:
                false_count += 1
    return {"count": len(rows), "true_count": true_count, "false_count": false_count}


def normalize_eq_text(text: str) -> str:
    return " ".join(text.replace("◇", "*").split())


def smoke_hf_subsets() -> list[str]:
    lines = []
    for subset in ALL_HF_SUBSETS:
        rows = load_hf_problem_set(subset)
        stats = validate_problem_rows(rows, f"hf:{subset}", require_answer=True)
        metadata = load_hf_metadata(subset)
        if stats["count"] != int(metadata["problem_count"]):
            fail(f"hf:{subset}: count mismatch rows={stats['count']} metadata={metadata['problem_count']}")
        if stats["true_count"] != int(metadata["true_count"]):
            fail(f"hf:{subset}: true_count mismatch rows={stats['true_count']} metadata={metadata['true_count']}")
        if stats["false_count"] != int(metadata["false_count"]):
            fail(f"hf:{subset}: false_count mismatch rows={stats['false_count']} metadata={metadata['false_count']}")
        role = "analysis_only" if subset in ANALYSIS_ONLY_HF_SUBSETS else "benchmark"
        lines.append(f"HF {subset}: {stats['count']} rows ({stats['true_count']} true / {stats['false_count']} false) role={role}")
    return lines


def smoke_official_stage2_files() -> list[str]:
    lines = []
    for rel_path, expected_count in OFFICIAL_STAGE2_EXPECTED_COUNTS.items():
        path = OFFICIAL_STAGE2_PROBLEMS_DIR / rel_path
        rows = load_problem_file(path)
        require_answer = path.suffix == ".jsonl"
        stats = validate_problem_rows(rows, f"official:{rel_path}", require_answer=require_answer)
        if stats["count"] != expected_count:
            fail(f"official:{rel_path}: count mismatch rows={stats['count']} expected={expected_count}")
        lines.append(f"Official {rel_path}: {stats['count']} rows")
    return lines


def smoke_overlap_consistency() -> list[str]:
    lines = []
    for subset in OVERLAP_STAGE2_FILES:
        hf_rows = {row["id"]: row for row in load_hf_problem_set(subset)}
        official_rows = {
            row["id"]: row
            for row in load_problem_file(OFFICIAL_STAGE2_PROBLEMS_DIR / f"{subset}.jsonl")
        }
        if set(hf_rows) != set(official_rows):
            fail(f"overlap:{subset}: id set mismatch between hf_cache and stage2_official_problems")
        for row_id, hf_row in hf_rows.items():
            official_row = official_rows[row_id]
            for key in ("eq1_id", "eq2_id", "answer"):
                if hf_row.get(key) != official_row.get(key):
                    fail(f"overlap:{subset}: mismatch for {row_id} key={key}")
            if normalize_eq_text(hf_row["equation1"]) != normalize_eq_text(official_row["equation1"]):
                fail(f"overlap:{subset}: equation1 semantic mismatch for {row_id}")
            if normalize_eq_text(hf_row["equation2"]) != normalize_eq_text(official_row["equation2"]):
                fail(f"overlap:{subset}: equation2 semantic mismatch for {row_id}")
        lines.append(f"Overlap {subset}: HF and official mirror are ID- and equation-equivalent ({len(hf_rows)} rows)")
    return lines


def smoke_active_loaders() -> list[str]:
    lines = []
    benchmark_rows = load_all_benchmarks()
    expected_benchmark_count = sum(len(load_hf_problem_set(name)) for name in CORE_HF_SUBSETS)
    if len(benchmark_rows) != expected_benchmark_count:
        fail(f"v21_data_infrastructure.load_all_benchmarks(): expected {expected_benchmark_count}, found {len(benchmark_rows)}")
    lines.append(f"v21_data_infrastructure.load_all_benchmarks(): {len(benchmark_rows)} rows")

    full_corpus = load_hf_problem_corpus(include_analysis_only=True)
    expected_full_corpus = sum(len(load_hf_problem_set(name)) for name in ALL_HF_SUBSETS)
    if len(full_corpus) != expected_full_corpus:
        fail(f"problem_set_catalog.load_hf_problem_corpus(include_analysis_only=True): expected {expected_full_corpus}, found {len(full_corpus)}")
    lines.append(f"problem_set_catalog.load_hf_problem_corpus(include_analysis_only=True): {len(full_corpus)} rows")

    equations = load_equations()
    eq_map = build_equation_map(equations)
    pair_preview = pairs_from_jsonl(HF_CACHE_DIR / "hard3.jsonl", only_false=True)
    if not pair_preview:
        fail("proof_scraping_lab.pairs_from_jsonl(): no pairs produced for hard3 false rows")
    if any(pair[0] <= 0 or pair[1] <= 0 for pair in pair_preview[:20]):
        fail("proof_scraping_lab.pairs_from_jsonl(): invalid 1-based equation ids")
    if not eq_map:
        fail("build_equation_map(): produced empty equation map")
    lines.append(f"proof_scraping_lab.pairs_from_jsonl(hard3,false): {len(pair_preview)} pairs")
    lines.append(f"equation map size: {len(eq_map)}")
    return lines


def smoke_active_module_imports() -> list[str]:
    lines = [
        f"atlas_public_dev import: {atlas_public_dev.__name__}",
        f"proof_atlas import: {proof_atlas.__name__}",
        f"proof_construction_atlas import: {proof_construction_atlas.__name__}",
    ]
    return lines


def main() -> int:
    report_lines = [
        "Smoke test: imported Hugging Face subsets",
        *smoke_hf_subsets(),
        "",
        "Smoke test: mirrored official Stage 2 files",
        *smoke_official_stage2_files(),
        "",
        "Smoke test: overlap consistency",
        *smoke_overlap_consistency(),
        "",
        "Smoke test: active loader functions",
        *smoke_active_loaders(),
        "",
        "Smoke test: active module imports",
        *smoke_active_module_imports(),
    ]
    print("\n".join(report_lines))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"SMOKE FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
