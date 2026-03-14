"""Shared benchmark helpers for submission-support and research evaluation.

This module centralizes label loading, balanced sampling, holdout construction,
bucket assignment, and adversarial summaries so evaluation code can state
clearly when a run is submission-valid and when it is only research support.
"""

from __future__ import annotations

import csv
import heapq
import json
import random
from collections import defaultdict
from functools import lru_cache
from typing import Iterable, Sequence

from analyze_equations import (
    can_prove_by_rewriting,
    count_ops,
    find_counterexample,
    get_depth,
    get_dual,
    get_vars,
    is_specialization,
    load_equations,
    parse_equation,
    tree_to_str,
)
from config import RAW_IMPL_CSV


CORE_BUCKETS = (
    "trivial",
    "specialization",
    "counterexample_easy",
    "ambiguous",
    "landmark",
    "hard",
)

LANDMARK_EQUATIONS = {
    1, 2, 3, 4, 5, 6, 7, 23, 38, 39, 40, 41, 42, 43, 44, 45, 46, 4512, 4513
}


def load_labeled_pairs_from_jsonl(filepath: str) -> list[dict]:
    records = []
    with open(filepath, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            eq1_idx = payload.get("equation1_index", payload.get("eq1", payload.get("eq1_idx")))
            eq2_idx = payload.get("equation2_index", payload.get("eq2", payload.get("eq2_idx")))
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


def load_holdout_indices(filepath: str) -> list[int]:
    with open(filepath, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return sorted(int(value) for value in payload)
    if isinstance(payload, dict):
        indices = payload.get("heldout_equation_indices", payload.get("holdout_indices", []))
        return sorted(int(value) for value in indices)
    raise ValueError(f"Unsupported holdout index format in {filepath}")


def sample_holdout_equation_indices(
    n_equations: int,
    n_holdout: int,
    seed: int = 42,
    protected_indices: Iterable[int] | None = None,
) -> list[int]:
    if n_holdout <= 0:
        return []

    protected = {int(value) for value in (protected_indices or [])}
    candidates = [idx for idx in range(1, n_equations + 1) if idx not in protected]
    if n_holdout > len(candidates):
        raise ValueError(
            f"Requested {n_holdout} held-out equations, but only {len(candidates)} are available"
        )

    rng = random.Random(seed)
    return sorted(rng.sample(candidates, n_holdout))


def sample_balanced_pairs_from_matrix(
    filepath: str = str(RAW_IMPL_CSV),
    n: int = 100,
    seed: int = 42,
    *,
    allowed_eq_indices: Sequence[int] | set[int] | None = None,
    excluded_eq_indices: Sequence[int] | set[int] | None = None,
    require_both_allowed: bool = False,
    attach_matrix_value: bool = False,
) -> list[dict]:
    rng = random.Random(seed)
    half = max(1, n // 2)
    allowed = _normalize_index_set(allowed_eq_indices)
    excluded = _normalize_index_set(excluded_eq_indices)
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
                if not _pair_is_eligible(
                    eq1_idx,
                    eq2_idx,
                    allowed_eq_indices=allowed,
                    excluded_eq_indices=excluded,
                    require_both_allowed=require_both_allowed,
                ):
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
                if attach_matrix_value:
                    record["matrix_value"] = value

                if value > 0:
                    true_seen += 1
                    _reservoir_append(true_pairs, record, half, true_seen, rng)
                else:
                    false_seen += 1
                    _reservoir_append(false_pairs, record, half, false_seen, rng)

    sampled = true_pairs + false_pairs
    rng.shuffle(sampled)
    return sampled


def build_no_leak_benchmark(
    equations: Sequence[str],
    *,
    filepath: str = str(RAW_IMPL_CSV),
    n: int = 200,
    holdout_equation_count: int = 100,
    seed: int = 42,
    holdout_eq_indices: Sequence[int] | None = None,
    protected_indices: Iterable[int] | None = None,
) -> tuple[list[dict], list[int]]:
    holdout = list(holdout_eq_indices or [])
    if not holdout:
        holdout = sample_holdout_equation_indices(
            n_equations=len(equations),
            n_holdout=holdout_equation_count,
            seed=seed,
            protected_indices=protected_indices,
        )

    records = sample_balanced_pairs_from_matrix(
        filepath=filepath,
        n=n,
        seed=seed,
        allowed_eq_indices=holdout,
        require_both_allowed=True,
        attach_matrix_value=True,
    )
    return records, sorted(int(value) for value in holdout)


def build_hardest_benchmark_from_matrix(
    equations: Sequence[str],
    *,
    filepath: str = str(RAW_IMPL_CSV),
    n: int = 500,
    seed: int = 42,
    allowed_eq_indices: Sequence[int] | set[int] | None = None,
    excluded_eq_indices: Sequence[int] | set[int] | None = None,
    require_both_allowed: bool = False,
) -> list[dict]:
    rng = random.Random(seed)
    allowed = _normalize_index_set(allowed_eq_indices)
    excluded = _normalize_index_set(excluded_eq_indices)
    profiles = [_equation_profile(eq_str) for eq_str in equations]
    half = max(1, n // 2)
    heaps: dict[bool, list[tuple[float, int, float, dict]]] = {True: [], False: []}

    with open(filepath, "r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for eq1_idx, row in enumerate(reader, start=1):
            profile1 = profiles[eq1_idx - 1]
            for eq2_idx, value_str in enumerate(row, start=1):
                if eq1_idx == eq2_idx:
                    continue
                if not _pair_is_eligible(
                    eq1_idx,
                    eq2_idx,
                    allowed_eq_indices=allowed,
                    excluded_eq_indices=excluded,
                    require_both_allowed=require_both_allowed,
                ):
                    continue
                try:
                    value = int(value_str)
                except ValueError:
                    continue
                if value == 0:
                    continue

                profile2 = profiles[eq2_idx - 1]
                if _looks_trivial_from_profiles(profile1, profile2):
                    continue

                label = value > 0
                structural_prob = structural_heuristic_probability(profile1, profile2)
                structural_pred = structural_prob > 0.5
                if structural_pred == label:
                    continue

                misleading_score = structural_prob if not label else (1.0 - structural_prob)
                hard_flag = 1 if abs(value) == 4 else 0
                record = {
                    "eq1_idx": eq1_idx,
                    "eq2_idx": eq2_idx,
                    "label": label,
                    "matrix_value": value,
                    "structural_prob": structural_prob,
                    "structural_pred": structural_pred,
                    "misleading_score": misleading_score,
                    "matrix_hard_case": abs(value) == 4,
                }
                _bounded_heap_push(
                    heaps[label],
                    record,
                    limit=half,
                    score=misleading_score,
                    hard_flag=hard_flag,
                    tie_breaker=rng.random(),
                )

    selected = [entry[3] for label in (True, False) for entry in heaps[label]]
    selected.sort(
        key=lambda rec: (
            rec["misleading_score"],
            1 if rec.get("matrix_hard_case") else 0,
            rec["eq1_idx"],
            rec["eq2_idx"],
        ),
        reverse=True,
    )
    return selected[:n]


def annotate_records(records: Iterable[dict], equations: Sequence[str]) -> list[dict]:
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
        return "specialization"

    if not label:
        try:
            if find_counterexample(eq1, eq2, magma_sizes=(2, 3)) is not None:
                return "counterexample_easy"
        except Exception:
            pass

    if eq1_idx in LANDMARK_EQUATIONS or eq2_idx in LANDMARK_EQUATIONS:
        return "landmark"

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
        return "ambiguous"

    return "hard"


def structural_heuristic_probability(eq1_profile: dict, eq2_profile: dict) -> float:
    if not eq1_profile["parsed"] or not eq2_profile["parsed"]:
        return 0.5
    if eq1_profile["equation"] == eq2_profile["equation"]:
        return 0.99
    if eq1_profile["is_identity"]:
        return 0.01
    if eq2_profile["is_identity"]:
        return 0.99
    if eq1_profile["forces_singleton"]:
        return 0.995
    if eq2_profile["forces_singleton"] and not eq1_profile["forces_singleton"]:
        return 0.04

    vars1 = eq1_profile["vars"]
    vars2 = eq2_profile["vars"]
    extra_vars = len(vars2 - vars1)
    if extra_vars:
        return max(0.03, 0.18 - 0.04 * extra_vars)

    ops_delta = eq1_profile["ops_total"] - eq2_profile["ops_total"]
    depth_delta = eq1_profile["depth_max"] - eq2_profile["depth_max"]
    same_vars = vars1 == vars2

    if same_vars and abs(ops_delta) <= 1 and abs(depth_delta) <= 1:
        return 0.58
    if ops_delta >= 2 and depth_delta >= 0 and vars2 <= vars1:
        return 0.72
    if ops_delta <= -2 or depth_delta <= -2:
        return 0.12
    if ops_delta >= 0 and depth_delta >= -1:
        return 0.42
    return 0.22


def summarize_bucket_accuracy(records: Iterable[dict]) -> dict:
    summary: dict[str, dict] = defaultdict(lambda: {"count": 0, "correct": 0})
    total = 0
    for record in records:
        bucket = record.get("bucket", "unknown")
        summary[bucket]["count"] += 1
        if record.get("correct"):
            summary[bucket]["correct"] += 1
        total += 1

    finalized = {}
    for bucket, values in sorted(summary.items(), key=lambda item: _bucket_sort_key(item[0])):
        count = values["count"]
        correct = values["correct"]
        finalized[bucket] = {
            "count": count,
            "share": (count / total) if total else 0.0,
            "accuracy": (correct / count) if count else None,
        }
    return finalized


def summarize_bucket_counts(records: Iterable[dict]) -> dict:
    summary: dict[str, int] = defaultdict(int)
    for record in records:
        summary[record.get("bucket", "unknown")] += 1
    return {
        bucket: count
        for bucket, count in sorted(summary.items(), key=lambda item: _bucket_sort_key(item[0]))
    }


def summarize_accuracy(records: Iterable[dict]) -> dict:
    records_list = list(records)
    if not records_list:
        return {"count": 0, "accuracy": None}
    correct = sum(1 for record in records_list if record.get("correct"))
    return {
        "count": len(records_list),
        "accuracy": correct / len(records_list),
    }


def summarize_trivial_share(records: Iterable[dict]) -> dict:
    records_list = list(records)
    total = len(records_list)
    trivial_count = sum(1 for record in records_list if record.get("bucket") == "trivial")
    nontrivial_count = total - trivial_count
    return {
        "total": total,
        "trivial_count": trivial_count,
        "trivial_share": (trivial_count / total) if total else 0.0,
        "nontrivial_count": nontrivial_count,
        "nontrivial_share": (nontrivial_count / total) if total else 0.0,
    }


def is_singleton_equivalent_equation(eq_str: str) -> bool:
    try:
        lhs, rhs = parse_equation(eq_str)
    except Exception:
        return False
    vars_l = get_vars(lhs)
    vars_r = get_vars(rhs)
    if vars_l & vars_r:
        return False
    return not isinstance(lhs, str) or not isinstance(rhs, str)


def is_trivial_free_pair(record: dict, equations: Sequence[str]) -> bool:
    eq1_idx = int(record["eq1_idx"])
    eq2_idx = int(record["eq2_idx"])
    if eq1_idx in {1, 2} or eq2_idx in {1, 2}:
        return False
    singleton_indices = load_singleton_equivalent_indices()
    if singleton_indices:
        eq1_singleton = eq1_idx in singleton_indices
        eq2_singleton = eq2_idx in singleton_indices
    else:
        eq1_singleton = is_singleton_equivalent_equation(equations[eq1_idx - 1])
        eq2_singleton = is_singleton_equivalent_equation(equations[eq2_idx - 1])
    return not (eq1_singleton and eq2_singleton)


def summarize_trivial_free_accuracy(records: Iterable[dict], equations: Sequence[str] | None = None) -> dict:
    records_list = list(records)
    if equations is None:
        filtered = [record for record in records_list if record.get("bucket") != "trivial"]
    else:
        filtered = [record for record in records_list if is_trivial_free_pair(record, equations)]
    summary = summarize_accuracy(filtered)
    summary["excluded_count"] = len(records_list) - summary["count"]
    return summary


def summarize_landmark_accuracy(
    records: Iterable[dict],
    landmark_equations: set[int] | None = None,
) -> dict:
    landmark_equations = landmark_equations or LANDMARK_EQUATIONS
    filtered = [
        record for record in records
        if int(record.get("eq1_idx", 0)) in landmark_equations
        or int(record.get("eq2_idx", 0)) in landmark_equations
    ]
    summary = {
        "overall": summarize_accuracy(filtered),
        "per_landmark": {},
    }
    for landmark in sorted(landmark_equations):
        subset = [
            record for record in filtered
            if int(record.get("eq1_idx", 0)) == landmark or int(record.get("eq2_idx", 0)) == landmark
        ]
        if subset:
            summary["per_landmark"][str(landmark)] = summarize_accuracy(subset)
    return summary


def _canonical_equation_key(eq_str: str) -> tuple[str, str]:
    lhs, rhs = parse_equation(eq_str)
    return tuple(sorted((tree_to_str(lhs), tree_to_str(rhs))))


def build_dual_index(equations: Sequence[str]) -> dict[int, int]:
    key_to_idx: dict[tuple[str, str], int] = {}
    for idx, eq_str in enumerate(equations, start=1):
        try:
            key_to_idx[_canonical_equation_key(eq_str)] = idx
        except Exception:
            continue

    dual_map: dict[int, int] = {}
    for idx, eq_str in enumerate(equations, start=1):
        try:
            lhs, rhs = parse_equation(eq_str)
            dual_key = tuple(sorted((tree_to_str(get_dual(lhs)), tree_to_str(get_dual(rhs)))))
        except Exception:
            continue
        dual_idx = key_to_idx.get(dual_key)
        if dual_idx is not None:
            dual_map[idx] = dual_idx
    return dual_map


def build_dual_swap_records(records: Iterable[dict], equations: Sequence[str]) -> list[dict]:
    dual_map = build_dual_index(equations)
    swapped = []
    for record in records:
        eq1_idx = int(record["eq1_idx"])
        eq2_idx = int(record["eq2_idx"])
        dual_eq1 = dual_map.get(eq1_idx)
        dual_eq2 = dual_map.get(eq2_idx)
        if dual_eq1 is None or dual_eq2 is None:
            continue
        swapped.append(
            {
                "source_eq1_idx": eq1_idx,
                "source_eq2_idx": eq2_idx,
                "eq1_idx": dual_eq1,
                "eq2_idx": dual_eq2,
                "label": record.get("label"),
            }
        )
    return annotate_records(swapped, equations)


def summarize_dual_swap_consistency(records: Iterable[dict], dual_records: Iterable[dict]) -> dict:
    original = {
        (record.get("eq1_idx"), record.get("eq2_idx")): record
        for record in records
    }
    paired = 0
    consistent = 0
    label_preserved = 0
    mismatches = []
    for dual_record in dual_records:
        source_key = (
            dual_record.get("source_eq1_idx"),
            dual_record.get("source_eq2_idx"),
        )
        original_record = original.get(source_key)
        if not original_record:
            continue
        if "predicted" not in original_record or "predicted" not in dual_record:
            continue
        paired += 1
        if bool(original_record["predicted"]) == bool(dual_record["predicted"]):
            consistent += 1
        if original_record.get("label") == dual_record.get("label"):
            label_preserved += 1
        if bool(original_record["predicted"]) != bool(dual_record["predicted"]):
            mismatches.append(
                {
                    "eq1_idx": original_record.get("eq1_idx"),
                    "eq2_idx": original_record.get("eq2_idx"),
                    "predicted": original_record.get("predicted"),
                    "dual_predicted": dual_record.get("predicted"),
                    "label": original_record.get("label"),
                }
            )

    return {
        "paired_count": paired,
        "prediction_consistency": (consistent / paired) if paired else None,
        "label_preservation": (label_preserved / paired) if paired else None,
        "mismatch_examples": mismatches[:20],
    }


def benchmark_metadata(
    *,
    artifact_kind: str,
    label_source: str,
    inference_mode: str,
    uses_matrix_at_inference: bool,
    format_examples_source: str = "none",
    uses_eval_labels_in_prompt: bool = False,
    benchmark_name: str = "",
    holdout_equation_count: int = 0,
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
        "benchmark_name": benchmark_name,
        "holdout_equation_count": holdout_equation_count,
    }


@lru_cache(maxsize=1)
def load_singleton_equivalent_indices(filepath: str = str(RAW_IMPL_CSV)) -> frozenset[int]:
    """Load exact Eq2-equivalent membership from the dense matrix when available."""
    try:
        row2: list[int] | None = None
        col2: list[int] = []
        with open(filepath, "r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            for row_idx, row in enumerate(reader, start=1):
                if len(row) < 2:
                    return frozenset()
                if row_idx == 2:
                    row2 = [int(value) for value in row]
                col2.append(int(row[1]))
        if row2 is None:
            return frozenset()
        indices = set()
        for eq_idx, (from_eq2, to_eq2) in enumerate(zip(row2, col2), start=1):
            if eq_idx == 2 or (from_eq2 > 0 and to_eq2 > 0):
                indices.add(eq_idx)
        return frozenset(indices)
    except (OSError, ValueError):
        return frozenset()


def _normalize_index_set(values: Sequence[int] | set[int] | None) -> set[int] | None:
    if values is None:
        return None
    return {int(value) for value in values}


def _pair_is_eligible(
    eq1_idx: int,
    eq2_idx: int,
    *,
    allowed_eq_indices: set[int] | None,
    excluded_eq_indices: set[int] | None,
    require_both_allowed: bool,
) -> bool:
    if excluded_eq_indices and (eq1_idx in excluded_eq_indices or eq2_idx in excluded_eq_indices):
        return False
    if not allowed_eq_indices:
        return True
    if require_both_allowed:
        return eq1_idx in allowed_eq_indices and eq2_idx in allowed_eq_indices
    return eq1_idx in allowed_eq_indices or eq2_idx in allowed_eq_indices


def _reservoir_append(bucket: list[dict], record: dict, limit: int, seen: int, rng: random.Random) -> None:
    if len(bucket) < limit:
        bucket.append(record)
        return
    replacement_index = rng.randint(0, seen - 1)
    if replacement_index < limit:
        bucket[replacement_index] = record


def _bounded_heap_push(
    heap: list[tuple[float, int, float, dict]],
    record: dict,
    *,
    limit: int,
    score: float,
    hard_flag: int,
    tie_breaker: float,
) -> None:
    item = (score, hard_flag, tie_breaker, record)
    if len(heap) < limit:
        heapq.heappush(heap, item)
        return
    if item > heap[0]:
        heapq.heapreplace(heap, item)


def _equation_profile(eq_str: str) -> dict:
    try:
        lhs, rhs = parse_equation(eq_str)
    except Exception:
        return {
            "equation": eq_str,
            "parsed": False,
            "vars": set(),
            "ops_total": 0,
            "depth_max": 0,
            "is_identity": False,
            "forces_singleton": False,
        }

    vars_all = get_vars(lhs) | get_vars(rhs)
    return {
        "equation": eq_str,
        "parsed": True,
        "vars": vars_all,
        "ops_total": count_ops(lhs) + count_ops(rhs),
        "depth_max": max(get_depth(lhs), get_depth(rhs)),
        "is_identity": lhs == rhs,
        "forces_singleton": _forces_singleton((lhs, rhs)),
    }


def _looks_trivial_from_profiles(eq1_profile: dict, eq2_profile: dict) -> bool:
    return (
        eq1_profile["equation"] == eq2_profile["equation"]
        or eq1_profile["is_identity"]
        or eq2_profile["is_identity"]
        or eq1_profile["forces_singleton"]
        or eq2_profile["forces_singleton"]
    )


def _bucket_sort_key(bucket: str) -> tuple[int, str]:
    try:
        return (CORE_BUCKETS.index(bucket), bucket)
    except ValueError:
        return (len(CORE_BUCKETS), bucket)


def _forces_singleton(eq: tuple) -> bool:
    lhs, rhs = eq
    variables = get_vars(lhs) | get_vars(rhs)
    return isinstance(lhs, str) and isinstance(rhs, str) and len(variables) == 2 and lhs != rhs
