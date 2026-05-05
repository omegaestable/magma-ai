from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from distill import check_equation, eval_tree, parse_equation_tree


@dataclass
class RunSummary:
    path: Path
    candidate: str
    model: str
    subset: str
    repeats: int
    benchmark_signature: str
    benchmark_size: int
    accuracy: float
    parse_rate: float
    fp_ids: list[str]
    fn_ids: list[str]
    unparsed_ids: list[str]
    result_rows: list[dict]


def load_result_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_name(payload: dict) -> str:
    cheatsheet = str(payload.get("cheatsheet", ""))
    if cheatsheet and cheatsheet != "(none)":
        return Path(cheatsheet).stem
    return "unknown"


def benchmark_signature(rows: Iterable[dict]) -> str:
    normalized = sorted(
        (str(row.get("id", "")), bool(row.get("ground_truth")))
        for row in rows
    )
    digest = hashlib.sha1(
        json.dumps(normalized, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return digest[:16]


def _ids_for(rows: Iterable[dict], predicate) -> list[str]:
    return sorted(str(row["id"]) for row in rows if predicate(row))


def summarize_result_file(path: Path) -> RunSummary:
    payload = load_result_payload(path)
    rows = payload.get("results", [])
    summary = payload.get("summary", {})
    return RunSummary(
        path=path,
        candidate=candidate_name(payload),
        model=str(payload.get("model", "unknown")),
        subset=str(payload.get("subset", "unknown")),
        repeats=int(payload.get("repeats", 1)),
        benchmark_signature=benchmark_signature(rows),
        benchmark_size=len(rows),
        accuracy=float(summary.get("accuracy", 0.0)),
        parse_rate=float(summary.get("parse_rate", 0.0)),
        fp_ids=_ids_for(
            rows,
            lambda row: bool(row.get("ground_truth")) is False
            and row.get("predicted") is True,
        ),
        fn_ids=_ids_for(
            rows,
            lambda row: bool(row.get("ground_truth")) is True
            and row.get("predicted") is False,
        ),
        unparsed_ids=_ids_for(rows, lambda row: not bool(row.get("parsed_ok", False))),
        result_rows=rows,
    )


def _group_key(run: RunSummary) -> tuple[str, str, int]:
    return run.benchmark_signature, run.model, run.repeats


def _pairwise_delta(base: RunSummary, challenger: RunSummary) -> dict:
    base_rows = {str(row["id"]): row for row in base.result_rows}
    challenger_rows = {str(row["id"]): row for row in challenger.result_rows}
    shared_ids = sorted(set(base_rows) & set(challenger_rows))
    prediction_flips = [
        row_id
        for row_id in shared_ids
        if base_rows[row_id].get("predicted") != challenger_rows[row_id].get("predicted")
    ]
    return {
        "base_candidate": base.candidate,
        "challenger_candidate": challenger.candidate,
        "base_path": str(base.path),
        "challenger_path": str(challenger.path),
        "accuracy_delta": round(challenger.accuracy - base.accuracy, 4),
        "parse_rate_delta": round(challenger.parse_rate - base.parse_rate, 4),
        "fp_fixed": sorted(set(base.fp_ids) - set(challenger.fp_ids)),
        "fp_introduced": sorted(set(challenger.fp_ids) - set(base.fp_ids)),
        "fn_fixed": sorted(set(base.fn_ids) - set(challenger.fn_ids)),
        "fn_introduced": sorted(set(challenger.fn_ids) - set(base.fn_ids)),
        "unparsed_fixed": sorted(set(base.unparsed_ids) - set(challenger.unparsed_ids)),
        "unparsed_introduced": sorted(set(challenger.unparsed_ids) - set(base.unparsed_ids)),
        "prediction_flips": prediction_flips,
    }


def compare_runs(result_paths: Iterable[Path]) -> dict:
    runs = [summarize_result_file(Path(path)) for path in result_paths]
    grouped: dict[tuple[str, str, int], list[RunSummary]] = {}
    for run in runs:
        grouped.setdefault(_group_key(run), []).append(run)

    comparable_groups = []
    incomparable_runs = []
    for key, group_runs in sorted(grouped.items(), key=lambda item: item[0]):
        signature, model, repeats = key
        ordered = sorted(group_runs, key=lambda run: (run.candidate, str(run.path)))
        if len(ordered) < 2:
            only = ordered[0]
            incomparable_runs.append(
                {
                    "path": str(only.path),
                    "candidate": only.candidate,
                    "model": only.model,
                    "subset": only.subset,
                    "benchmark_signature": only.benchmark_signature,
                    "reason": "no exact-match run on the same benchmark/model/repeats",
                }
            )
            continue

        comparable_groups.append(
            {
                "benchmark_signature": signature,
                "model": model,
                "repeats": repeats,
                "benchmark_size": ordered[0].benchmark_size,
                "subsets": sorted({run.subset for run in ordered}),
                "runs": [
                    {
                        "path": str(run.path),
                        "candidate": run.candidate,
                        "subset": run.subset,
                        "accuracy": run.accuracy,
                        "parse_rate": run.parse_rate,
                        "fp_ids": run.fp_ids,
                        "fn_ids": run.fn_ids,
                        "unparsed_ids": run.unparsed_ids,
                    }
                    for run in ordered
                ],
                "pairwise_deltas": [
                    _pairwise_delta(base, challenger)
                    for index, base in enumerate(ordered)
                    for challenger in ordered[index + 1 :]
                ],
            }
        )

    return {
        "run_count": len(runs),
        "comparable_group_count": len(comparable_groups),
        "incomparable_run_count": len(incomparable_runs),
        "comparable_groups": comparable_groups,
        "incomparable_runs": incomparable_runs,
    }


def write_compare_markdown(report: dict, path: Path) -> None:
    lines = [
        "# V26 Recovery Comparison",
        "",
        f"- runs={report['run_count']}",
        f"- comparable_groups={report['comparable_group_count']}",
        f"- incomparable_runs={report['incomparable_run_count']}",
        "",
    ]
    for group in report["comparable_groups"]:
        lines.append(
            f"## {group['model']} | sig={group['benchmark_signature']} | n={group['benchmark_size']}"
        )
        lines.append("")
        for run in group["runs"]:
            lines.append(
                f"- {run['candidate']} acc={run['accuracy']:.1%} parse={run['parse_rate']:.1%} "
                f"fp={len(run['fp_ids'])} fn={len(run['fn_ids'])} unparsed={len(run['unparsed_ids'])}"
            )
        lines.append("")
        for delta in group["pairwise_deltas"]:
            lines.append(
                f"- {delta['base_candidate']} -> {delta['challenger_candidate']}: "
                f"acc_delta={delta['accuracy_delta']:+.1%} parse_delta={delta['parse_rate_delta']:+.1%} "
                f"fp_fixed={len(delta['fp_fixed'])} fp_introduced={len(delta['fp_introduced'])}"
            )
        lines.append("")

    if report["incomparable_runs"]:
        lines.append("## Incomparable Runs")
        lines.append("")
        for run in report["incomparable_runs"]:
            lines.append(
                f"- {run['candidate']} [{run['model']}] sig={run['benchmark_signature']} {run['reason']}"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_all_magmas(size: int):
    cells = size * size
    for values in itertools.product(range(size), repeat=cells):
        yield [list(values[index * size : (index + 1) * size]) for index in range(size)]


def ordered_vars_first_appearance(eq1: str, eq2: str) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for char in f"{eq1} {eq2}":
        if char.isalpha() and char not in seen:
            seen.add(char)
            ordered.append(char)
    return ordered


def cycling_assignment(variables: list[str], size: int) -> dict[str, int]:
    return {var: index % size for index, var in enumerate(variables)}


def evaluate_equation_with_assignment(
    eq: str,
    assignment: dict[str, int],
    table: list[list[int]],
) -> tuple[int, int]:
    lhs, rhs = parse_equation_tree(eq)
    return eval_tree(lhs, assignment, table), eval_tree(rhs, assignment, table)


def separates_universally(table: list[list[int]], eq1: str, eq2: str) -> bool:
    return check_equation(eq1, table) and not check_equation(eq2, table)


def separates_with_cycling_assignment(table: list[list[int]], eq1: str, eq2: str) -> bool:
    assignment = cycling_assignment(ordered_vars_first_appearance(eq1, eq2), len(table))
    lhs1, rhs1 = evaluate_equation_with_assignment(eq1, assignment, table)
    if lhs1 != rhs1:
        return False
    lhs2, rhs2 = evaluate_equation_with_assignment(eq2, assignment, table)
    return lhs2 != rhs2


def _dedupe_problem_rows(result_paths: Iterable[Path]) -> tuple[list[dict], list[dict]]:
    false_positives: dict[str, dict] = {}
    true_pairs: dict[str, dict] = {}
    for path in result_paths:
        payload = load_result_payload(Path(path))
        for row in payload.get("results", []):
            row_id = str(row.get("id", ""))
            if bool(row.get("ground_truth")) is False and row.get("predicted") is True:
                false_positives.setdefault(row_id, row)
            elif bool(row.get("ground_truth")) is True:
                true_pairs.setdefault(row_id, row)
    return list(false_positives.values()), list(true_pairs.values())


def classify_magma_candidate(candidate: dict) -> str:
    if candidate["universal_true_flags"]:
        return "family_unsafe"
    if candidate["universal_caught_ids"]:
        return "admissible"
    if candidate["cycling_true_flags"]:
        return "assignment_unsafe"
    if candidate["cycling_caught_ids"]:
        return "assignment_only"
    return "no_signal"


def magma_description(table: list[list[int]]) -> str:
    size = len(table)
    flat = [table[row][col] for row in range(size) for col in range(size)]
    if len(set(flat)) == 1:
        return f"a*b = {flat[0]}"
    if all(table[row][col] == row for row in range(size) for col in range(size)):
        return "a*b = a"
    if all(table[row][col] == col for row in range(size) for col in range(size)):
        return "a*b = b"
    if all(table[row][col] == (row + col) % size for row in range(size) for col in range(size)):
        return f"a*b = (a+b) mod {size}"
    if all(table[row][col] == (row + 1) % size for row in range(size) for col in range(size)):
        return f"a*b = (a+1) mod {size}"
    if all(table[row][col] == (col + 1) % size for row in range(size) for col in range(size)):
        return f"a*b = (b+1) mod {size}"
    return str(table)


def _candidate_sort_key(candidate: dict) -> tuple[int, int, int, str]:
    return (
        -len(candidate["universal_caught_ids"]),
        -len(candidate["cycling_caught_ids"]),
        len(candidate["cycling_true_flags"]),
        candidate["description"],
    )


def greedy_cover(candidates: list[dict]) -> tuple[list[dict], list[str]]:
    admissible = [
        candidate
        for candidate in candidates
        if candidate["classification"] == "admissible"
        and candidate["universal_caught_ids"]
    ]
    covered: set[str] = set()
    selected: list[dict] = []
    remaining = list(admissible)
    while remaining:
        best = max(
            remaining,
            key=lambda candidate: len(set(candidate["universal_caught_ids"]) - covered),
        )
        marginal_ids = sorted(set(best["universal_caught_ids"]) - covered)
        if not marginal_ids:
            break
        covered.update(marginal_ids)
        selected.append(
            {
                "description": best["description"],
                "table": best["table"],
                "size": best["size"],
                "marginal": len(marginal_ids),
                "marginal_ids": marginal_ids,
                "cumulative": len(covered),
            }
        )
        remaining.remove(best)
    return selected, sorted(covered)


def audit_magmas(result_paths: Iterable[Path], max_size: int = 3) -> dict:
    false_positives, true_pairs = _dedupe_problem_rows(result_paths)
    candidates: list[dict] = []
    for size in range(2, max_size + 1):
        for table in generate_all_magmas(size):
            universal_caught_ids = []
            cycling_caught_ids = []
            universal_true_flags = []
            cycling_true_flags = []

            for row in false_positives:
                eq1 = row["equation1"]
                eq2 = row["equation2"]
                if separates_universally(table, eq1, eq2):
                    universal_caught_ids.append(str(row["id"]))
                if separates_with_cycling_assignment(table, eq1, eq2):
                    cycling_caught_ids.append(str(row["id"]))

            for row in true_pairs:
                eq1 = row["equation1"]
                eq2 = row["equation2"]
                if separates_universally(table, eq1, eq2):
                    universal_true_flags.append(str(row["id"]))
                if separates_with_cycling_assignment(table, eq1, eq2):
                    cycling_true_flags.append(str(row["id"]))

            if not any(
                [
                    universal_caught_ids,
                    cycling_caught_ids,
                    universal_true_flags,
                    cycling_true_flags,
                ]
            ):
                continue

            candidate = {
                "table": table,
                "size": size,
                "description": magma_description(table),
                "universal_caught_ids": sorted(universal_caught_ids),
                "cycling_caught_ids": sorted(cycling_caught_ids),
                "universal_true_flags": sorted(universal_true_flags),
                "cycling_true_flags": sorted(cycling_true_flags),
            }
            candidate["classification"] = classify_magma_candidate(candidate)
            candidates.append(candidate)

    candidates.sort(key=_candidate_sort_key)
    greedy_selected, universally_covered = greedy_cover(candidates)

    assignment_only_extra = sorted(
        {
            row_id
            for candidate in candidates
            if candidate["classification"] == "assignment_only"
            for row_id in candidate["cycling_caught_ids"]
        }
        - set(universally_covered)
    )

    counts_by_classification: dict[str, int] = {}
    for candidate in candidates:
        counts_by_classification[candidate["classification"]] = (
            counts_by_classification.get(candidate["classification"], 0) + 1
        )

    return {
        "false_positive_count": len(false_positives),
        "true_pair_count": len(true_pairs),
        "max_size": max_size,
        "counts_by_classification": counts_by_classification,
        "admissible_covered_ids": universally_covered,
        "admissible_uncovered_ids": sorted(
            str(row["id"]) for row in false_positives if str(row["id"]) not in set(universally_covered)
        ),
        "assignment_only_extra_ids": assignment_only_extra,
        "greedy_cover": greedy_selected,
        "candidates": candidates,
    }


def write_audit_markdown(report: dict, path: Path) -> None:
    lines = [
        "# V26 Witness Admissibility Audit",
        "",
        f"- false_positives={report['false_positive_count']}",
        f"- true_pairs={report['true_pair_count']}",
        f"- admissible_covered={len(report['admissible_covered_ids'])}",
        f"- admissible_uncovered={len(report['admissible_uncovered_ids'])}",
        f"- assignment_only_extra={len(report['assignment_only_extra_ids'])}",
        "",
        "## Counts By Classification",
        "",
    ]
    for classification, count in sorted(report["counts_by_classification"].items()):
        lines.append(f"- {classification}={count}")
    lines.extend(["", "## Greedy Admissible Cover", ""])
    for item in report["greedy_cover"]:
        lines.append(
            f"- {item['description']} size={item['size']} +{item['marginal']} -> {item['cumulative']}"
        )
    lines.extend(["", "## Top Candidates", ""])
    for candidate in report["candidates"][:10]:
        lines.append(
            f"- {candidate['classification']} | {candidate['description']} | "
            f"universal={len(candidate['universal_caught_ids'])} | "
            f"cycling={len(candidate['cycling_caught_ids'])} | "
            f"u_flags={len(candidate['universal_true_flags'])} | "
            f"c_flags={len(candidate['cycling_true_flags'])}"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _parse_result_paths(raw_items: list[str]) -> list[Path]:
    paths: list[Path] = []
    for item in raw_items:
        for token in item.split(","):
            token = token.strip()
            if token:
                paths.append(Path(token))
    if not paths:
        raise ValueError("No result files provided")
    return paths


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="V26 recovery comparison and witness audit utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare = subparsers.add_parser("compare-runs", help="Compare result files only when benchmark/model match exactly")
    compare.add_argument("--result-files", nargs="+", required=True)
    compare.add_argument("--output-prefix", default="results/v26_recovery/compare")

    audit = subparsers.add_parser("audit-magmas", help="Audit universal vs assignment-only magma coverage")
    audit.add_argument("--result-files", nargs="+", required=True)
    audit.add_argument("--max-size", type=int, default=3)
    audit.add_argument("--output-prefix", default="results/v26_recovery/magma_audit")

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    result_paths = _parse_result_paths(args.result_files)

    if args.command == "compare-runs":
        report = compare_runs(result_paths)
        prefix = Path(args.output_prefix)
        _write_json(prefix.with_suffix(".json"), report)
        write_compare_markdown(report, prefix.with_suffix(".md"))
        print(
            f"WROTE {prefix.with_suffix('.json').as_posix()} and {prefix.with_suffix('.md').as_posix()}"
        )
        return

    if args.command == "audit-magmas":
        report = audit_magmas(result_paths, max_size=args.max_size)
        prefix = Path(args.output_prefix)
        _write_json(prefix.with_suffix(".json"), report)
        write_audit_markdown(report, prefix.with_suffix(".md"))
        print(
            f"WROTE {prefix.with_suffix('.json').as_posix()} and {prefix.with_suffix('.md').as_posix()}"
        )
        return

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()