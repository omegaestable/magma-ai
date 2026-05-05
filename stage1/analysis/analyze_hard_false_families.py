#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import distill
from fetch_teorth_data import load_full_entries
from proof_atlas import FAMILY_TEMPLATES, classify_entry

ROOT = Path(__file__).resolve().parent

FALSE_FAMILY_ORDER = [
    "projection_family_counterexamples",
    "small_finite_magma",
    "all4x4_table_counterexamples",
    "central_groupoid_counterexamples",
    "modified_lifted_magma",
    "linear_translation",
    "canonizer_confluence",
    "exceptional_hard",
    "hard_case",
]
FALSE_FAMILY_SET = set(FALSE_FAMILY_ORDER)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def infer_benchmark_path(result_path: Path) -> Path:
    name = result_path.name
    marker = "_v23_"
    prefix = "sim_meta-llama_llama-3.3-70b-instruct_"
    if prefix in name and marker in name:
        bench_name = name.split(prefix, 1)[1].split(marker, 1)[0]
        return ROOT / "data" / "benchmark" / f"{bench_name}.jsonl"
    raise ValueError(f"Cannot infer benchmark path from {result_path.name}")


def build_fact_family_index(entries: list[dict]) -> dict[int, Counter[str]]:
    index: dict[int, Counter[str]] = defaultdict(Counter)
    for entry in entries:
        variant = entry.get("variant") or {}
        facts = variant.get("facts") or {}
        family = classify_entry(entry)
        if family not in FALSE_FAMILY_SET:
            continue
        for bucket in ("satisfied", "refuted"):
            for label in facts.get(bucket, []) or []:
                if not label.startswith("Equation"):
                    continue
                eq_id = int(label.replace("Equation", ""))
                index[eq_id][family] += 1
    return index


def ranked_counter(counter: Counter[str]) -> list[dict]:
    return [
        {"family": family, "score": score}
        for family, score in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def choose_primary_family(scores: Counter[str]) -> str:
    if not scores:
        return "hard_case"
    return sorted(
        scores.items(),
        key=lambda item: (
            -item[1],
            FALSE_FAMILY_ORDER.index(item[0]) if item[0] in FALSE_FAMILY_SET else len(FALSE_FAMILY_ORDER),
            item[0],
        ),
    )[0][0]


def rank_false_pair(row: dict, benchmark_row: dict, family_index: dict[int, Counter[str]]) -> dict:
    eq1_id = int(benchmark_row["eq1_id"])
    eq2_id = int(benchmark_row["eq2_id"])
    eq1_counts = family_index.get(eq1_id, Counter())
    eq2_counts = family_index.get(eq2_id, Counter())
    features = distill.extract_pair_features(row["equation1"], row["equation2"])
    witnesses = distill.find_verified_witnesses(row["equation1"], row["equation2"])

    scores: Counter[str] = Counter()
    reasons: list[str] = []

    for family in FALSE_FAMILY_SET:
        eq1_vote = min(eq1_counts.get(family, 0), 3)
        eq2_vote = min(eq2_counts.get(family, 0), 3)
        if eq1_vote and eq2_vote:
            scores[family] += 4 + eq1_vote + eq2_vote
            reasons.append(f"shared_eq_support:{family}:{eq1_vote}+{eq2_vote}")
        elif eq1_vote or eq2_vote:
            scores[family] += eq1_vote + eq2_vote

    if features["new_vars_in_e2"] or features["lp_obstruction"] or features["rp_obstruction"]:
        scores["projection_family_counterexamples"] += 5
        reasons.append("structural_projection_trigger")

    if witnesses:
        scores["small_finite_magma"] += 5
        reasons.append("verified_canned_witness")
        if eq1_counts.get("all4x4_table_counterexamples") or eq2_counts.get("all4x4_table_counterexamples"):
            scores["all4x4_table_counterexamples"] += 2
            reasons.append("all4x4_eq_support")
        if eq1_counts.get("central_groupoid_counterexamples") or eq2_counts.get("central_groupoid_counterexamples"):
            scores["central_groupoid_counterexamples"] += 2
            reasons.append("central_groupoid_eq_support")
    elif not scores:
        scores["canonizer_confluence"] += 2
        reasons.append("no_small_witness_fallback")

    primary_family = choose_primary_family(scores)
    template = FAMILY_TEMPLATES.get(primary_family, FAMILY_TEMPLATES["hard_case"])
    return {
        "id": row["id"],
        "eq1_id": eq1_id,
        "eq2_id": eq2_id,
        "equation1": row["equation1"],
        "equation2": row["equation2"],
        "primary_family": primary_family,
        "family_group": template["family_group"],
        "family_scores": ranked_counter(scores),
        "eq1_family_votes": ranked_counter(eq1_counts),
        "eq2_family_votes": ranked_counter(eq2_counts),
        "feature_flags": {
            "new_vars_in_e2": features["new_vars_in_e2"],
            "lp_obstruction": features["lp_obstruction"],
            "rp_obstruction": features["rp_obstruction"],
        },
        "verified_witnesses": witnesses,
        "ranking_reasons": reasons,
    }


def analyze_result_file(result_path: Path, family_index: dict[int, Counter[str]]) -> dict:
    payload = load_json(result_path)
    benchmark_path = infer_benchmark_path(result_path)
    benchmark_rows = {row["id"]: row for row in load_jsonl(benchmark_path)}
    false_positives = [row for row in payload["results"] if row["ground_truth"] is False and row["predicted"] is True]
    ranked_rows = [rank_false_pair(row, benchmark_rows[row["id"]], family_index) for row in false_positives]
    family_summary = Counter(item["primary_family"] for item in ranked_rows)
    return {
        "result_file": result_path.as_posix(),
        "benchmark_file": benchmark_path.as_posix(),
        "false_positive_count": len(ranked_rows),
        "primary_family_counts": dict(sorted(family_summary.items(), key=lambda item: (-item[1], item[0]))),
        "rows": ranked_rows,
    }


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, reports: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Hard False Family Report", ""]
    for report in reports:
        lines.append(f"## {Path(report['result_file']).name}")
        lines.append(f"- false_positive_count={report['false_positive_count']}")
        if report["primary_family_counts"]:
            summary = ", ".join(f"{family}:{count}" for family, count in report["primary_family_counts"].items())
            lines.append(f"- primary_family_counts={summary}")
        lines.append("")
        for row in report["rows"][:10]:
            top_scores = ", ".join(f"{item['family']}:{item['score']}" for item in row["family_scores"][:3])
            lines.append(f"### {row['id']}")
            lines.append(f"- pair={row['eq1_id']},{row['eq2_id']}")
            lines.append(f"- primary_family={row['primary_family']}")
            lines.append(f"- top_scores={top_scores if top_scores else 'none'}")
            lines.append(f"- feature_flags={row['feature_flags']}")
            if row["verified_witnesses"]:
                witness_names = ", ".join(item["name"] for item in row["verified_witnesses"])
                lines.append(f"- verified_witnesses={witness_names}")
            lines.append(f"- eq1={row['equation1']}")
            lines.append(f"- eq2={row['equation2']}")
            lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank likely hard-false witness families for evaluation false positives")
    parser.add_argument("--result-files", required=True, help="Comma-separated results JSON paths")
    parser.add_argument("--out-prefix", default="results/proof_lab/hard_false_family_report")
    args = parser.parse_args()

    result_files = [Path(part.strip()) for part in args.result_files.split(",") if part.strip()]
    family_index = build_fact_family_index(load_full_entries())
    reports = [analyze_result_file(path, family_index) for path in result_files]

    out_prefix = Path(args.out_prefix)
    json_path = out_prefix.with_suffix(".json")
    md_path = out_prefix.with_suffix(".md")
    write_json(json_path, reports)
    write_markdown(md_path, reports)

    print("=" * 80)
    print(f"WROTE {json_path.as_posix()}")
    print(f"WROTE {md_path.as_posix()}")
    print("=" * 80)


if __name__ == "__main__":
    main()