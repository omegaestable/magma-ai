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
    load_equations,
    parse_equation,
    tree_to_str,
    get_dual,
)
from config import RAW_IMPL_CSV


LANDMARK_EQUATIONS = {
    1, 2, 3, 4, 5, 6, 7, 23, 38, 39, 40, 41, 42, 43, 44, 45, 46, 4512, 4513
}


def is_singleton_equivalent_equation(eq_str: str) -> bool:
    """Return True if the equation is equivalent to the singleton law x=y."""
    try:
        lhs, rhs = parse_equation(eq_str)
    except Exception:
        return False
    vars_l = get_vars(lhs)
    vars_r = get_vars(rhs)
    if vars_l & vars_r:
        return False
    return not isinstance(lhs, str) or not isinstance(rhs, str)


def is_trivial_free_pair(record: dict, equations: list[str]) -> bool:
    """F1 definition: drop Eq1/Eq2 incidents and pairs both singleton-equivalent."""
    eq1_idx = int(record["eq1_idx"])
    eq2_idx = int(record["eq2_idx"])
    if eq1_idx in {1, 2} or eq2_idx in {1, 2}:
        return False
    eq1_singleton = is_singleton_equivalent_equation(equations[eq1_idx - 1])
    eq2_singleton = is_singleton_equivalent_equation(equations[eq2_idx - 1])
    return not (eq1_singleton and eq2_singleton)


def summarize_accuracy(records: Iterable[dict]) -> dict:
    records = list(records)
    if not records:
        return {"count": 0, "accuracy": None}
    correct = sum(1 for record in records if record.get("correct"))
    return {
        "count": len(records),
        "accuracy": correct / len(records),
    }


def summarize_trivial_free_accuracy(records: Iterable[dict], equations: list[str]) -> dict:
    records = list(records)
    filtered = [record for record in records if is_trivial_free_pair(record, equations)]
    summary = summarize_accuracy(filtered)
    summary["excluded_count"] = max(0, len(records) - summary["count"])
    return summary


def _canonical_equation_key(eq_str: str) -> tuple[str, str]:
    lhs, rhs = parse_equation(eq_str)
    lhs_str = tree_to_str(lhs)
    rhs_str = tree_to_str(rhs)
    return tuple(sorted((lhs_str, rhs_str)))


def build_dual_index(equations: list[str]) -> dict[int, int]:
    """Map each equation index to the index of its dual, if present."""
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


def build_dual_swap_records(records: Iterable[dict], equations: list[str]) -> list[dict]:
    """Construct dual-swapped evaluation records for F2 consistency checks."""
    dual_map = build_dual_index(equations)
    swapped = []
    for record in records:
        eq1_idx = int(record["eq1_idx"])
        eq2_idx = int(record["eq2_idx"])
        dual_eq1 = dual_map.get(eq1_idx)
        dual_eq2 = dual_map.get(eq2_idx)
        if dual_eq1 is None or dual_eq2 is None:
            continue
        swapped.append({
            "source_eq1_idx": eq1_idx,
            "source_eq2_idx": eq2_idx,
            "eq1_idx": dual_eq1,
            "eq2_idx": dual_eq2,
            "eq1": equations[dual_eq1 - 1],
            "eq2": equations[dual_eq2 - 1],
            "label": record.get("label"),
        })
    return swapped


"""Shared benchmark helpers for submission-support and research evaluation.

This module keeps label loading, balanced sampling, holdout construction,
bucket assignment, and benchmark metadata in one place so evaluation code can
state clearly when a run is submission-valid and when it is only research
support.
"""

from __future__ import annotations

import csv
import heapq
import json
import random
from collections import defaultdict
from typing import Iterable, Sequence

from analyze_equations import (
    can_prove_by_rewriting,
    count_ops,
    find_counterexample,
    get_dual,
    get_depth,
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

    protected = set(int(value) for value in (protected_indices or []))
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


def summarize_trivial_free_accuracy(records: Iterable[dict], equations: Sequence[str] | None = None) -> dict:
    records_list = [record for record in records if record.get("bucket") != "trivial"]
    count = len(records_list)
    if count == 0:
        return {"count": 0, "accuracy": None}
    correct = sum(1 for record in records_list if record.get("correct"))
    return {"count": count, "accuracy": correct / count}


def summarize_landmark_accuracy(records: Iterable[dict]) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        eq1_idx = int(record.get("eq1_idx", 0))
        eq2_idx = int(record.get("eq2_idx", 0))
        touched = sorted({idx for idx in (eq1_idx, eq2_idx) if idx in LANDMARK_EQUATIONS})
        if touched:
            grouped["overall"].append(record)
            for idx in touched:
                grouped[f"Eq{idx}"] .append(record)

    summary = {}
    for key, bucket_records in grouped.items():
        count = len(bucket_records)
        summary[key] = {
            "count": count,
            "accuracy": (sum(1 for record in bucket_records if record.get("correct")) / count)
            if count else None,
        }
    if "overall" not in summary:
        summary["overall"] = {"count": 0, "accuracy": None}
    return summary


def build_dual_swap_records(records: Iterable[dict], equations: Sequence[str]) -> list[dict]:
    index_by_equation = {eq.strip(): idx for idx, eq in enumerate(equations, start=1)}
    swapped = []
    for record in records:
        eq1_str = equations[record["eq1_idx"] - 1]
        eq2_str = equations[record["eq2_idx"] - 1]
        try:
            lhs1, rhs1 = parse_equation(eq1_str)
            lhs2, rhs2 = parse_equation(eq2_str)
        except Exception:
            continue

        dual_eq1 = f"{tree_to_str(get_dual(lhs1))} = {tree_to_str(get_dual(rhs1))}"
        dual_eq2 = f"{tree_to_str(get_dual(lhs2))} = {tree_to_str(get_dual(rhs2))}"
        dual_eq1_idx = index_by_equation.get(dual_eq1)
        dual_eq2_idx = index_by_equation.get(dual_eq2)
        if not dual_eq1_idx or not dual_eq2_idx:
            continue

        swapped.append(
            {
                "eq1_idx": dual_eq1_idx,
                "eq2_idx": dual_eq2_idx,
                "label": record["label"],
                "source_eq1_idx": record["eq1_idx"],
                "source_eq2_idx": record["eq2_idx"],
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

    return {
        "paired_count": paired,
        "prediction_consistency": (consistent / paired) if paired else None,
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
        "primary_metric": PRIMARY_STAGE1_METRIC,
        "secondary_metrics": list(SECONDARY_LOCAL_METRICS),
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