"""Shared benchmark helpers for submission-support and research evaluation.

This module keeps label loading, balanced sampling, bucket assignment, and
benchmark metadata in one place so evaluation code can state clearly when a
run is submission-valid and when it is only research support.
"""

from __future__ import annotations

import csv
import json
import random
from collections import defaultdict
from typing import Iterable

from analyze_equations import (
    can_prove_by_rewriting,
    count_ops,
    find_counterexample,
    get_depth,
    get_vars,
    is_specialization,
    parse_equation,
)


LANDMARK_EQUATIONS = {
    1, 2, 3, 4, 5, 6, 7, 23, 38, 39, 40, 41, 42, 43, 44, 45, 46, 4512, 4513
}


def load_equations(filepath: str = "equations.txt") -> list[str]:
    with open(filepath, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def load_labeled_pairs_from_jsonl(filepath: str) -> list[dict]:
    records = []
    with open(filepath, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            eq1_idx = payload.get("equation1_index", payload.get("eq1"))
            eq2_idx = payload.get("equation2_index", payload.get("eq2"))
            label = payload.get("implies", payload.get("label"))
            if eq1_idx and eq2_idx and label is not None:
                records.append(
                    {
                        "eq1_idx": int(eq1_idx),
                        "eq2_idx": int(eq2_idx),
                        "label": bool(label),
                    }
                )
    return records


def sample_balanced_pairs_from_matrix(
    filepath: str = "export_raw_implications_14_3_2026.csv",
    n: int = 100,
    seed: int = 42,
) -> list[dict]:
    rng = random.Random(seed)
    half = max(1, n // 2)
    true_pairs: list[dict] = []
    false_pairs: list[dict] = []
    true_seen = 0
    false_seen = 0

    with open(filepath, "r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for eq1_idx, row in enumerate(reader, start=1):
            for eq2_idx, value_str in enumerate(row, start=1):
                if eq1_idx == eq2_idx:
                    continue
                try:
                    value = int(value_str)
                except ValueError:
                    continue
                if value == 0:
                    continue

                record = {
                    "eq1_idx": eq1_idx,
                    "eq2_idx": eq2_idx,
                    "label": value > 0,
                }
                if value > 0:
                    true_seen += 1
                    _reservoir_append(true_pairs, record, half, true_seen, rng)
                else:
                    false_seen += 1
                    _reservoir_append(false_pairs, record, half, false_seen, rng)

    sampled = true_pairs + false_pairs
    rng.shuffle(sampled)
    return sampled


def _reservoir_append(bucket: list[dict], record: dict, limit: int, seen: int, rng: random.Random) -> None:
    if len(bucket) < limit:
        bucket.append(record)
        return
    replacement_index = rng.randint(0, seen - 1)
    if replacement_index < limit:
        bucket[replacement_index] = record


def annotate_records(records: Iterable[dict], equations: list[str]) -> list[dict]:
    annotated = []
    for record in records:
        enriched = dict(record)
        eq1_str = equations[record["eq1_idx"] - 1]
        eq2_str = equations[record["eq2_idx"] - 1]
        enriched["eq1"] = eq1_str
        enriched["eq2"] = eq2_str
        enriched["bucket"] = classify_pair(
            eq1_str,
            eq2_str,
            record["label"],
            eq1_idx=record["eq1_idx"],
            eq2_idx=record["eq2_idx"],
        )
        annotated.append(enriched)
    return annotated


def classify_pair(
    eq1_str: str,
    eq2_str: str,
    label: bool,
    eq1_idx: int = 0,
    eq2_idx: int = 0,
) -> str:
    try:
        eq1 = parse_equation(eq1_str)
        eq2 = parse_equation(eq2_str)
    except Exception:
        return "parse_error"

    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2

    if (
        eq1_str.strip() == eq2_str.strip()
        or lhs1 == rhs1
        or lhs2 == rhs2
        or _forces_singleton(eq1)
        or _forces_singleton(eq2)
    ):
        return "trivial"

    if label and is_specialization(eq1, eq2):
        return "specialization_positive"

    if not label:
        try:
            if find_counterexample(eq1, eq2, magma_sizes=(2, 3)) is not None:
                return "counterexample_easy_negative"
        except Exception:
            pass

    if eq1_idx in LANDMARK_EQUATIONS or eq2_idx in LANDMARK_EQUATIONS:
        return "landmark_pair"

    try:
        rewrite_proved = can_prove_by_rewriting(eq1, eq2, max_steps=100)
    except Exception:
        rewrite_proved = False

    vars1 = get_vars(lhs1) | get_vars(rhs1)
    vars2 = get_vars(lhs2) | get_vars(rhs2)
    ops1 = count_ops(lhs1) + count_ops(rhs1)
    ops2 = count_ops(lhs2) + count_ops(rhs2)
    depth1 = max(get_depth(lhs1), get_depth(rhs1))
    depth2 = max(get_depth(lhs2), get_depth(rhs2))

    ambiguous = (
        len(vars1) == len(vars2)
        and abs(ops1 - ops2) <= 1
        and abs(depth1 - depth2) <= 1
        and vars1 == vars2
    )
    if ambiguous and not rewrite_proved:
        return "structurally_ambiguous"

    return "hard_or_disagreement"


def summarize_bucket_accuracy(records: Iterable[dict]) -> dict:
    summary: dict[str, dict] = defaultdict(lambda: {"count": 0, "correct": 0})
    for record in records:
        bucket = record.get("bucket", "unknown")
        summary[bucket]["count"] += 1
        if record.get("correct"):
            summary[bucket]["correct"] += 1

    finalized = {}
    for bucket, values in sorted(summary.items()):
        count = values["count"]
        correct = values["correct"]
        finalized[bucket] = {
            "count": count,
            "accuracy": (correct / count) if count else None,
        }
    return finalized


def summarize_bucket_counts(records: Iterable[dict]) -> dict:
    summary: dict[str, int] = defaultdict(int)
    for record in records:
        summary[record.get("bucket", "unknown")] += 1
    return dict(sorted(summary.items()))


def benchmark_metadata(
    *,
    artifact_kind: str,
    label_source: str,
    inference_mode: str,
    uses_matrix_at_inference: bool,
    format_examples_source: str = "none",
    uses_eval_labels_in_prompt: bool = False,
) -> dict:
    submission_valid = (
        artifact_kind == "cheatsheet_only"
        and inference_mode == "llm_prompt"
        and not uses_matrix_at_inference
        and not uses_eval_labels_in_prompt
        and format_examples_source in {"none", "separate_jsonl"}
    )

    if submission_valid:
        reason = "Cheatsheet-only prompting with separate labels and no matrix/graph access at inference."
    elif uses_eval_labels_in_prompt:
        reason = "Invalid: evaluation labels appear in the prompt context."
    elif uses_matrix_at_inference:
        reason = "Research-only: inference path can access answer-like matrix information."
    elif artifact_kind != "cheatsheet_only":
        reason = "Research-only: the evaluated artifact is not the submission artifact."
    else:
        reason = "Submission validity not established."

    return {
        "artifact_kind": artifact_kind,
        "label_source": label_source,
        "inference_mode": inference_mode,
        "format_examples_source": format_examples_source,
        "uses_matrix_at_inference": uses_matrix_at_inference,
        "uses_eval_labels_in_prompt": uses_eval_labels_in_prompt,
        "submission_valid": submission_valid,
        "validity_reason": reason,
    }


def _forces_singleton(eq: tuple) -> bool:
    lhs, rhs = eq
    variables = get_vars(lhs) | get_vars(rhs)
    return isinstance(lhs, str) and isinstance(rhs, str) and len(variables) == 2 and lhs != rhs