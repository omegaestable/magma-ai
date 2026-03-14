"""Research-only analyses for Workstreams E4 and E5.

This script mines:
- direct-proof patterns from matrix value 4 pairs;
- hard-false counterexample method coverage from matrix value -4 pairs.

Outputs JSON and Markdown summaries under results/.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
from collections import Counter, defaultdict
from pathlib import Path

from analyze_equations import (
    PATTERNS,
    can_prove_by_rewriting,
    count_ops,
    get_dual,
    get_vars,
    load_equations,
    matches_pattern,
    parse_equation,
)
from benchmark_utils import annotate_records, is_singleton_equivalent_equation
from config import RAW_IMPL_CSV, RESULTS_DIR
from magma_search import find_counterexample
from proof_search import check_specialization

logger = logging.getLogger(__name__)


def iter_matrix_pairs(filepath: str, target_values: set[int]) -> list[tuple[int, int, int]]:
    pairs: list[tuple[int, int, int]] = []
    with open(filepath, "r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for eq1_idx, row in enumerate(reader, start=1):
            for eq2_idx, raw_value in enumerate(row, start=1):
                if eq1_idx == eq2_idx:
                    continue
                try:
                    value = int(raw_value)
                except ValueError:
                    continue
                if value in target_values:
                    pairs.append((eq1_idx, eq2_idx, value))
    return pairs


def reservoir_sample_pairs(
    filepath: str,
    target_value: int,
    sample_size: int,
    seed: int,
) -> list[tuple[int, int, int]]:
    rng = random.Random(seed)
    sample: list[tuple[int, int, int]] = []
    seen = 0
    with open(filepath, "r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for eq1_idx, row in enumerate(reader, start=1):
            for eq2_idx, raw_value in enumerate(row, start=1):
                if eq1_idx == eq2_idx:
                    continue
                try:
                    value = int(raw_value)
                except ValueError:
                    continue
                if value != target_value:
                    continue
                seen += 1
                record = (eq1_idx, eq2_idx, value)
                if len(sample) < sample_size:
                    sample.append(record)
                    continue
                replacement = rng.randint(0, seen - 1)
                if replacement < sample_size:
                    sample[replacement] = record
    return sample


def primary_pattern(eq_str: str) -> str:
    if is_singleton_equivalent_equation(eq_str):
        return "singleton_equiv"
    try:
        eq = parse_equation(eq_str)
    except Exception:
        return "parse_error"
    for name in PATTERNS:
        if matches_pattern(eq, name):
            return name
    return "unclassified"


def pair_signature(eq1_str: str, eq2_str: str) -> dict:
    eq1 = parse_equation(eq1_str)
    eq2 = parse_equation(eq2_str)
    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    vars1 = get_vars(lhs1) | get_vars(rhs1)
    vars2 = get_vars(lhs2) | get_vars(rhs2)
    ops1 = count_ops(lhs1) + count_ops(rhs1)
    ops2 = count_ops(lhs2) + count_ops(rhs2)
    if ops1 > ops2:
        ops_relation = "eq1_stronger"
    elif ops1 < ops2:
        ops_relation = "eq2_stronger"
    else:
        ops_relation = "same_ops"
    return {
        "eq1_family": primary_pattern(eq1_str),
        "eq2_family": primary_pattern(eq2_str),
        "extra_vars_in_eq2": bool(vars2 - vars1),
        "ops_relation": ops_relation,
    }


def proof_rule_text(method: str, signature: dict) -> str:
    if method == "specialization":
        return "If Eq2 is a direct substitution instance of Eq1, answer TRUE immediately."
    if method == "duality_then_specialization":
        return "If dual(Eq2) is a substitution instance of Eq1, use duality first and then specialize."
    if method == "rewrite":
        return "When both laws stay in the same variable support, try a short rewrite chain before guessing."
    if signature["eq1_family"] in {"left_projection", "right_projection"}:
        return "Projection laws often prove nested targets by repeatedly collapsing inner terms."
    return "If Eq1 is structurally stronger than Eq2 with no extra variables in Eq2, try simplification patterns before searching for counterexamples."


def classify_proof_pattern(eq1_str: str, eq2_str: str, rewrite_steps: int) -> dict:
    signature = pair_signature(eq1_str, eq2_str)
    eq1 = parse_equation(eq1_str)
    eq2 = parse_equation(eq2_str)
    method = "unresolved_direct_proof"

    sigma = check_specialization(eq1, eq2)
    if sigma is not None:
        method = "specialization"
    else:
        lhs2, rhs2 = eq2
        dual_eq2 = (get_dual(lhs2), get_dual(rhs2))
        sigma = check_specialization(eq1, dual_eq2)
        if sigma is not None:
            method = "duality_then_specialization"
        elif can_prove_by_rewriting(eq1, eq2, max_steps=rewrite_steps):
            method = "rewrite"
        elif not signature["extra_vars_in_eq2"] and signature["ops_relation"] != "eq2_stronger":
            method = "structural_simplification"

    signature_text = (
        f"{method}|{signature['eq1_family']}->{signature['eq2_family']}|"
        f"extra_vars={int(signature['extra_vars_in_eq2'])}|{signature['ops_relation']}"
    )
    return {
        "method": method,
        "signature": signature_text,
        "rule_text": proof_rule_text(method, signature),
        **signature,
    }


def counterexample_method_family(method: str) -> str:
    if method.startswith("known:"):
        return "known_small_magma"
    if method == "exhaustive_size2":
        return "exhaustive_size2"
    if method.startswith("linear_Fp"):
        return "linear_magma"
    if method.startswith("translation_invariant"):
        return "translation_invariant"
    if method.startswith("twist:"):
        return "twisted_magma"
    if method.startswith("greedy_construction"):
        return "greedy_construction"
    if method == "backtrack_size3":
        return "backtrack_size3"
    if method == "random_search":
        return "random_search"
    return method


def counterexample_rule_text(method_family: str, signature: dict) -> str:
    if method_family in {"known_small_magma", "exhaustive_size2"}:
        return "Try the tiny stock magmas first; many hard negatives still collapse under size-2 or other canned small tables."
    if method_family == "linear_magma":
        return "If small finite tables miss, try linear magmas x◇y=ax+by over small prime fields."
    if method_family == "translation_invariant":
        return "Medium-hard negatives often separate via translation-invariant tables x◇y=x+f(y-x) on Z/nZ."
    if method_family == "twisted_magma":
        return "For symmetry-heavy failures, twisted product constructions are a strong next counterexample family."
    if method_family == "greedy_construction":
        return "If finite-style searches stall, escalate to greedy partial constructions for inherently harder negatives."
    return "Escalate counterexample search by structure: stock magmas, then linear, then richer constructed families."


def classify_counterexample_pattern(eq1_str: str, eq2_str: str, timeout: float) -> dict:
    signature = pair_signature(eq1_str, eq2_str)
    result = find_counterexample(eq1_str, eq2_str, timeout=timeout)
    method = result["method"] if result is not None else "unresolved"
    family = counterexample_method_family(method)
    signature_text = (
        f"{family}|{signature['eq1_family']}->{signature['eq2_family']}|"
        f"extra_vars={int(signature['extra_vars_in_eq2'])}|{signature['ops_relation']}"
    )
    return {
        "method": method,
        "method_family": family,
        "signature": signature_text,
        "rule_text": counterexample_rule_text(family, signature),
        **signature,
    }


def aggregate_patterns(rows: list[dict], pair_records: list[dict], label_key: str) -> dict:
    by_signature: dict[str, dict] = {}
    by_method = Counter()
    rule_counts = Counter()
    for row, pair in zip(rows, pair_records):
        by_method[row[label_key]] += 1
        rule_counts[row["rule_text"]] += 1
        bucket = by_signature.setdefault(
            row["signature"],
            {
                "count": 0,
                label_key: row[label_key],
                "eq1_family": row["eq1_family"],
                "eq2_family": row["eq2_family"],
                "extra_vars_in_eq2": row["extra_vars_in_eq2"],
                "ops_relation": row["ops_relation"],
                "rule_text": row["rule_text"],
                "samples": [],
            },
        )
        bucket["count"] += 1
        if len(bucket["samples"]) < 3:
            bucket["samples"].append({
                "eq1_idx": pair["eq1_idx"],
                "eq2_idx": pair["eq2_idx"],
                "eq1": pair["eq1"],
                "eq2": pair["eq2"],
            })
    top_signatures = sorted(by_signature.values(), key=lambda item: item["count"], reverse=True)
    return {
        "method_counts": dict(by_method.most_common()),
        "top_signatures": top_signatures[:25],
        "cheatsheet_candidates": [
            {"rule_text": rule, "count": count}
            for rule, count in rule_counts.most_common(10)
        ],
    }


def write_summary_files(name: str, payload: dict) -> tuple[Path, Path]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / f"{name}.json"
    md_path = RESULTS_DIR / f"{name}.md"
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    lines = [f"# {name}", ""]
    for section_name in ("method_counts", "cheatsheet_candidates", "top_signatures"):
        if section_name not in payload:
            continue
        lines.append(f"## {section_name.replace('_', ' ').title()}")
        if section_name == "method_counts":
            for method, count in payload[section_name].items():
                lines.append(f"- {method}: {count}")
        elif section_name == "cheatsheet_candidates":
            for item in payload[section_name]:
                lines.append(f"- {item['rule_text']} ({item['count']})")
        else:
            for item in payload[section_name][:10]:
                lines.append(
                    f"- {item['count']}x {item['eq1_family']} -> {item['eq2_family']} | "
                    f"{item['rule_text']}"
                )
        lines.append("")

    with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines).rstrip() + "\n")
    return json_path, md_path


def mine_proof_patterns(matrix_path: str, equations: list[str], limit: int, rewrite_steps: int) -> dict:
    pairs = iter_matrix_pairs(matrix_path, {4})
    if limit > 0:
        pairs = pairs[:limit]
    logger.info(f"Mining proof patterns from {len(pairs)} value-4 pairs")

    pair_records = annotate_records(
        [
            {"eq1_idx": eq1_idx, "eq2_idx": eq2_idx, "label": True}
            for eq1_idx, eq2_idx, _ in pairs
        ],
        equations,
    )
    rows = [classify_proof_pattern(record["eq1"], record["eq2"], rewrite_steps) for record in pair_records]
    summary = aggregate_patterns(rows, pair_records, "method")
    summary.update({
        "n_pairs": len(pair_records),
        "rewrite_steps": rewrite_steps,
    })
    return summary


def mine_counterexample_patterns(
    matrix_path: str,
    equations: list[str],
    sample_size: int,
    seed: int,
    timeout: float,
) -> dict:
    pairs = reservoir_sample_pairs(matrix_path, -4, sample_size=sample_size, seed=seed)
    logger.info(f"Mining counterexample patterns from {len(pairs)} sampled value--4 pairs")

    pair_records = annotate_records(
        [
            {"eq1_idx": eq1_idx, "eq2_idx": eq2_idx, "label": False}
            for eq1_idx, eq2_idx, _ in pairs
        ],
        equations,
    )
    rows = [classify_counterexample_pattern(record["eq1"], record["eq2"], timeout) for record in pair_records]
    summary = aggregate_patterns(rows, pair_records, "method_family")
    unresolved = sum(1 for row in rows if row["method_family"] == "unresolved")
    summary.update({
        "n_pairs": len(pair_records),
        "sample_size": sample_size,
        "timeout_per_pair": timeout,
        "unresolved": unresolved,
    })
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine Workstream E proof/counterexample patterns")
    parser.add_argument("--mode", choices=["proof-patterns", "counterexample-patterns"], required=True)
    parser.add_argument("--matrix", default=str(RAW_IMPL_CSV), help="Path to the dense implication matrix")
    parser.add_argument("--limit", type=int, default=0,
                        help="Optional cap for proof-pattern mining (0 = all value-4 pairs)")
    parser.add_argument("--sample-size", type=int, default=400,
                        help="Reservoir sample size for value--4 counterexample mining")
    parser.add_argument("--rewrite-steps", type=int, default=150,
                        help="Rewrite step budget used when classifying proof pairs")
    parser.add_argument("--timeout", type=float, default=2.5,
                        help="Per-pair timeout for hard-false counterexample mining")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--name", default="workstream")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    equations = load_equations()
    if args.mode == "proof-patterns":
        payload = mine_proof_patterns(args.matrix, equations, limit=args.limit, rewrite_steps=args.rewrite_steps)
        output_name = f"proof_patterns_{args.name}"
    else:
        payload = mine_counterexample_patterns(
            args.matrix,
            equations,
            sample_size=args.sample_size,
            seed=args.seed,
            timeout=args.timeout,
        )
        output_name = f"counterexample_patterns_{args.name}"

    json_path, md_path = write_summary_files(output_name, payload)
    logger.info(f"Wrote {json_path}")
    logger.info(f"Wrote {md_path}")


if __name__ == "__main__":
    main()